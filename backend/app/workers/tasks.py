from __future__ import annotations

import logging
import traceback
from datetime import datetime
from uuid import UUID

import redis
from sqlalchemy import insert

from app.config import settings
from app.database import sync_sessionmaker
from app.models.document import Document
from app.models.extracted_result import ExtractedResult
from app.models.processing_job import ProcessingJob
from app.services.event_publisher import publish_and_persist
from services.analysis_engine import compute_all
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60, name="analyze_document")
def analyze_document(self, job_id: str, document_id: str, file_path: str):
	"""
	Main worker task: process a document through the full 8-stage pipeline.

	Args:
		self: Reference to task instance (for retries)
		job_id: UUID of the processing job
		document_id: UUID of the document
		file_path: Absolute path to the uploaded text file
	"""
	session = sync_sessionmaker()
	redis_client = redis.from_url(settings.REDIS_URL)

	try:
		# Convert string IDs to UUIDs
		job_id_uuid = UUID(job_id)
		document_id_uuid = UUID(document_id)

		# Fetch the job and document from DB
		job = session.query(ProcessingJob).filter(ProcessingJob.id == job_id_uuid).first()
		document = session.query(Document).filter(Document.id == document_id_uuid).first()

		if not job or not document:
			raise RuntimeError(f"Job {job_id} or Document {document_id} not found")

		# Stage 1: Mark job as processing
		job.status = "processing"
		job.started_at = datetime.utcnow()
		session.commit()
		publish_and_persist(session, redis_client, job_id, "job_started", 5, "Job started")

		# Stage 2: Read and parse file
		try:
			with open(file_path, 'r', encoding='utf-8') as f:
				text = f.read()
		except Exception as e:
			raise RuntimeError(f"Failed to read file {file_path}: {e}")

		publish_and_persist(session, redis_client, job_id, "document_parsing_started", 10, "Parsing document")

		# Stage 3: Extract structural metadata
		# (In a real system, this would do more complex parsing)
		text_length = len(text)
		publish_and_persist(session, redis_client, job_id, "document_parsing_completed", 30, f"Parsed {text_length} characters")

		# Stage 4: Start field extraction
		publish_and_persist(session, redis_client, job_id, "field_extraction_started", 35, "Extracting fields")

		# Stage 5: Compute all SEO metrics
		results = compute_all(text)

		# Stage 6: Complete field extraction
		publish_and_persist(session, redis_client, job_id, "field_extraction_completed", 80, "Fields extracted")

		# Stage 7: Upsert result with COALESCE protection
		stmt = insert(ExtractedResult).values(
			document_id=document_id_uuid,
			job_id=job_id_uuid,
			word_count=results['word_count'],
			readability_score=results['readability_score'],
			primary_keywords=results['primary_keywords'],
			auto_summary=results['auto_summary'],
			created_at=datetime.utcnow(),
			updated_at=datetime.utcnow(),
		).on_conflict_do_update(
			index_elements=['document_id'],
			set_={
				'job_id': job_id_uuid,
				'word_count': results['word_count'],
				'readability_score': results['readability_score'],
				'primary_keywords': results['primary_keywords'],
				'auto_summary': results['auto_summary'],
				'updated_at': datetime.utcnow(),
			}
		)
		session.execute(stmt)
		session.commit()

		publish_and_persist(session, redis_client, job_id, "final_result_stored", 90, "Result stored")

		# Stage 8: Mark job as completed
		job.status = "completed"
		job.completed_at = datetime.utcnow()
		session.commit()
		publish_and_persist(session, redis_client, job_id, "job_completed", 100, "Job completed")

	except Exception as exc:
		logger.exception(f"Error processing job {job_id}: {exc}")
		# Retry up to max_retries times with default_retry_delay
		raise self.retry(exc=exc)
	finally:
		session.close()
		redis_client.close()


@analyze_document.on_failure
def on_analyze_document_failure(self, exc, task_id, args, kwargs, einfo):
	"""
	Failure handler: mark the job as failed with error details.

	Args:
		self: Task instance
		exc: Exception instance
		task_id: Task ID
		args: Task positional arguments
		kwargs: Task keyword arguments
		einfo: Exception info object (includes full traceback)
	"""
	job_id = args[0]  # job_id is the first positional argument

	session = sync_sessionmaker()
	try:
		job = session.query(ProcessingJob).filter(ProcessingJob.id == UUID(job_id)).first()
		if job:
			job.status = "failed"
			job.error_message = str(einfo)  # Full traceback from ExceptionInfo
			session.commit()
			logger.info(f"Job {job_id} marked as failed")
	except Exception as e:
		logger.exception(f"Failed to update job {job_id} status to failed: {e}")
	finally:
		session.close()