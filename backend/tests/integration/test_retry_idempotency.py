import tempfile
import os
from uuid import uuid4
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.select import select

from app.models import Document, ProcessingJob, ExtractedResult, User
from app.workers.tasks import analyze_document


class TestRetryIdempotency:
    """Test that retrying analysis is idempotent via COALESCE upsert strategy."""

    @pytest.mark.asyncio
    async def test_double_run_single_result(self, test_db_session: AsyncSession):
        """Test that running task twice creates only one result row."""
        # Create test user
        user = User(
            id=uuid4(),
            email="idempotency-test@example.com",
            hashed_password="hash",
            is_active=True,
        )
        test_db_session.add(user)
        await test_db_session.flush()

        # Create temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(
                "Idempotency is important for reliability. "
                "Running tasks multiple times should produce consistent results. "
                "The database should enforce constraints to prevent duplicates. "
                "User edits should be preserved across retries."
            )
            file_path = f.name

        try:
            # Create document
            document = Document(
                id=uuid4(),
                user_id=user.id,
                original_filename="idempotency_test.txt",
                file_path=file_path,
                file_size=os.path.getsize(file_path),
                mime_type="text/plain",
            )
            test_db_session.add(document)
            await test_db_session.flush()

            # Run task first time
            job1 = ProcessingJob(
                id=uuid4(),
                document_id=document.id,
                status="queued",
                progress_percentage=0,
                current_stage="job_queued",
            )
            test_db_session.add(job1)
            await test_db_session.flush()
            await test_db_session.commit()

            analyze_document.apply(args=[str(job1.id), str(document.id), file_path])

            # Verify first result exists
            result = await test_db_session.execute(
                select(ExtractedResult).where(ExtractedResult.document_id == document.id)
            )
            first_result = result.scalar_one_or_none()
            assert first_result is not None
            original_auto_summary = first_result.auto_summary

            # Simulate user editing the summary
            first_result.user_edited_summary = "User's custom summary that should be preserved"
            await test_db_session.commit()

            # Run task second time (simulating retry)
            job2 = ProcessingJob(
                id=uuid4(),
                document_id=document.id,
                status="queued",
                progress_percentage=0,
                current_stage="job_queued",
            )
            test_db_session.add(job2)
            await test_db_session.flush()
            await test_db_session.commit()

            analyze_document.apply(args=[str(job2.id), str(document.id), file_path])

            # Verify only ONE result row exists
            result = await test_db_session.execute(
                select(ExtractedResult).where(ExtractedResult.document_id == document.id)
            )
            all_results = result.scalars().all()
            assert len(all_results) == 1, f"Expected 1 result, found {len(all_results)}"

            # Verify user edit was preserved (COALESCE in upsert)
            final_result = all_results[0]
            assert final_result.user_edited_summary == "User's custom summary that should be preserved"
            # Auto summary may have updated, but user edit should persist
            assert final_result.auto_summary == original_auto_summary or len(final_result.auto_summary) > 0

        finally:
            # Cleanup
            if os.path.exists(file_path):
                os.unlink(file_path)