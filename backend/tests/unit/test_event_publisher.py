from unittest.mock import MagicMock, AsyncMock, patch
import json
import pytest
from app.services.event_publisher import publish_and_persist


class TestPublishAndPersist:
    """Test the publish_and_persist dual write helper function."""

    @pytest.mark.asyncio
    async def test_publish_and_persist_updates_db_and_redis(self):
        """Test that publish_and_persist updates both database and Redis."""
        # Create mocks
        mock_db = MagicMock()
        mock_redis = MagicMock()
        
        job_id = "test-job-id"
        stage = "job_started"
        progress = 5
        message = "Job has started"

        # Call function
        publish_and_persist(mock_db, mock_redis, job_id, stage, progress, message)

        # Verify database execute was called
        assert mock_db.execute.called
        
        # Verify Redis publish was called with correct channel and payload
        assert mock_redis.publish.called
        call_args = mock_redis.publish.call_args
        channel = call_args[0][0]
        payload = json.loads(call_args[0][1])
        
        assert channel == f"job_progress:{job_id}"
        assert payload["stage"] == stage
        assert payload["progress"] == progress
        assert payload["message"] == message

    @pytest.mark.asyncio
    async def test_publish_and_persist_db_update_fields(self):
        """Test that database update touches correct fields."""
        mock_db = MagicMock()
        mock_redis = MagicMock()

        publish_and_persist(mock_db, mock_redis, "job-123", "field_extraction_completed", 80, "Extracting keywords")

        # Verify execute was called
        assert mock_db.execute.called
        assert mock_db.commit.called

    @pytest.mark.asyncio
    async def test_publish_and_persist_redis_failure_isolation(self):
        """Test that Redis failure doesn't propagate - DB commit must still happen."""
        mock_db = MagicMock()
        mock_redis = MagicMock()
        
        # Simulate Redis connection failure
        mock_redis.publish.side_effect = ConnectionError("Redis unavailable")

        # This should NOT raise an exception
        try:
            publish_and_persist(mock_db, mock_redis, "job-456", "job_completed", 100, "Done")
        except ConnectionError:
            pytest.fail("Redis failure should not propagate")

        # But database operations should have completed
        assert mock_db.execute.called
        assert mock_db.commit.called

    @pytest.mark.asyncio
    async def test_publish_timestamp_included(self):
        """Test that published event includes timestamp."""
        mock_db = MagicMock()
        mock_redis = MagicMock()

        publish_and_persist(mock_db, mock_redis, "job-789", "processing", 50, "Still going")

        # Get the published payload
        call_args = mock_redis.publish.call_args
        payload = json.loads(call_args[0][1])
        
        assert "timestamp" in payload
        assert payload["job_id"] == "job-789"