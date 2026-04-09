import tempfile
import os
from uuid import uuid4
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.select import select

from app.models import Document, ProcessingJob, ExtractedResult, User
from app.workers.tasks import analyze_document
from app.config import settings


class TestWorkerPipeline:
    """Test the complete worker pipeline with synchronous task execution."""

    @pytest.mark.asyncio
    async def test_successful_analysis_pipeline(self, test_db_session: AsyncSession):
        """Test successful document analysis through the entire pipeline."""
        # Create test user and document
        user = User(
            id=uuid4(),
            email="worker-test@example.com",
            hashed_password="hash",
            is_active=True,
        )
        test_db_session.add(user)
        await test_db_session.flush()

        # Create temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(
                "Python is a popular programming language. "
                "It is used for web development, data science, and machine learning. "
                "Python emphasizes code readability and simplicity. "
                "Many companies use Python in their technology stack. "
                "Python has a large and active community of developers."
            )
            file_path = f.name

        try:
            # Create document record
            document = Document(
                id=uuid4(),
                user_id=user.id,
                original_filename="test_document.txt",
                file_path=file_path,
                file_size=os.path.getsize(file_path),
                mime_type="text/plain",
            )
            test_db_session.add(document)
            await test_db_session.flush()

            # Create job record
            job = ProcessingJob(
                id=uuid4(),
                document_id=document.id,
                status="queued",
                progress_percentage=0,
                current_stage="job_queued",
            )
            test_db_session.add(job)
            await test_db_session.flush()
            await test_db_session.commit()

            # Run task synchronously (simulating worker execution)
            # Note: In real scenarios, .apply() runs the task synchronously in-process
            analyze_document.apply(args=[str(job.id), str(document.id), file_path])

            # Refresh job from database
            result = await test_db_session.execute(
                select(ProcessingJob).where(ProcessingJob.id == job.id)
            )
            updated_job = result.scalar_one_or_none()

            # Assertions on job status
            assert updated_job is not None
            assert updated_job.status == "completed"
            assert updated_job.progress_percentage == 100
            assert updated_job.completed_at is not None
            assert updated_job.current_stage == "job_completed"

            # Check for extracted result
            result = await test_db_session.execute(
                select(ExtractedResult).where(ExtractedResult.document_id == document.id)
            )
            extracted_result = result.scalar_one_or_none()

            # Assertions on result data
            assert extracted_result is not None
            assert extracted_result.word_count > 0
            assert 0 <= extracted_result.readability_score <= 100
            assert isinstance(extracted_result.primary_keywords, list)
            assert len(extracted_result.primary_keywords) > 0
            assert len(extracted_result.auto_summary) > 0

        finally:
            # Cleanup
            if os.path.exists(file_path):
                os.unlink(file_path)

    @pytest.mark.asyncio
    async def test_failure_path_missing_file(self, test_db_session: AsyncSession):
        """Test that job fails gracefully when file is missing."""
        # Create test user
        user = User(
            id=uuid4(),
            email="worker-fail-test@example.com",
            hashed_password="hash",
            is_active=True,
        )
        test_db_session.add(user)
        await test_db_session.flush()

        # Create document with non-existent file path
        document = Document(
            id=uuid4(),
            user_id=user.id,
            original_filename="missing_document.txt",
            file_path="/nonexistent/path/to/file.txt",
            file_size=0,
            mime_type="text/plain",
        )
        test_db_session.add(document)
        await test_db_session.flush()

        # Create job record
        job = ProcessingJob(
            id=uuid4(),
            document_id=document.id,
            status="queued",
            progress_percentage=0,
            current_stage="job_queued",
        )
        test_db_session.add(job)
        await test_db_session.flush()
        await test_db_session.commit()

        # Run task - should fail due to missing file
        # The task will retry max_retries times then call on_failure
        analyze_document.apply(args=[str(job.id), str(document.id), document.file_path])

        # Refresh job from database
        result = await test_db_session.execute(
            select(ProcessingJob).where(ProcessingJob.id == job.id)
        )
        updated_job = result.scalar_one_or_none()

        # Task should have failed after retries
        assert updated_job is not None
        assert updated_job.status == "failed"
        assert updated_job.error_message is not None
        # No result should be created on failure
        result = await test_db_session.execute(
            select(ExtractedResult).where(ExtractedResult.document_id == document.id)
        )
        assert result.scalar_one_or_none() is None