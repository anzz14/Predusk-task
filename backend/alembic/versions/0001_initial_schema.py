"""Initial schema creation: users, documents, processing_jobs, extracted_results tables.

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
	# Create users table
	op.create_table(
		'users',
		sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.func.gen_random_uuid(), nullable=False),
		sa.Column('email', sa.String(length=255), nullable=False),
		sa.Column('hashed_password', sa.String(length=255), nullable=False),
		sa.Column('is_active', sa.Boolean(), server_default=sa.literal(True), nullable=False),
		sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
		sa.PrimaryKeyConstraint('id'),
		sa.UniqueConstraint('email'),
	)

	# Create documents table
	op.create_table(
		'documents',
		sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.func.gen_random_uuid(), nullable=False),
		sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
		sa.Column('original_filename', sa.String(length=255), nullable=False),
		sa.Column('file_path', sa.String(length=512), nullable=False),
		sa.Column('file_size', sa.BigInteger(), nullable=False),
		sa.Column('mime_type', sa.String(length=100), nullable=False),
		sa.Column('upload_timestamp', sa.DateTime(timezone=True), nullable=False),
		sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
		sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
		sa.PrimaryKeyConstraint('id'),
	)
	op.create_index('ix_documents_user_id', 'documents', ['user_id'], unique=False)

	# Create processing_jobs table
	op.create_table(
		'processing_jobs',
		sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.func.gen_random_uuid(), nullable=False),
		sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
		sa.Column('celery_task_id', sa.String(length=255), nullable=True),
		sa.Column('status', sa.String(length=50), server_default=sa.literal('queued'), nullable=False),
		sa.Column('progress_percentage', sa.Integer(), server_default=sa.literal(0), nullable=False),
		sa.Column('current_stage', sa.String(length=100), server_default=sa.literal('job_queued'), nullable=False),
		sa.Column('error_message', sa.Text(), nullable=True),
		sa.Column('retry_count', sa.Integer(), server_default=sa.literal(0), nullable=False),
		sa.Column('meta', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
		sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
		sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
		sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
		sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
		sa.PrimaryKeyConstraint('id'),
	)
	op.create_index('ix_processing_jobs_document_id', 'processing_jobs', ['document_id'], unique=False)
	op.create_index('ix_processing_jobs_status', 'processing_jobs', ['status'], unique=False)

	# Create extracted_results table
	op.create_table(
		'extracted_results',
		sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.func.gen_random_uuid(), nullable=False),
		sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
		sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=False),
		sa.Column('word_count', sa.Integer(), nullable=False),
		sa.Column('readability_score', sa.Float(), nullable=False),
		sa.Column('primary_keywords', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
		sa.Column('auto_summary', sa.Text(), nullable=False),
		sa.Column('user_edited_summary', sa.Text(), nullable=True),
		sa.Column('is_finalized', sa.Boolean(), server_default=sa.literal(False), nullable=False),
		sa.Column('finalized_at', sa.DateTime(timezone=True), nullable=True),
		sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
		sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
		sa.ForeignKeyConstraint(['job_id'], ['processing_jobs.id'], ),
		sa.PrimaryKeyConstraint('id'),
		sa.UniqueConstraint('document_id', name='uq_extracted_results_document_id'),
	)


def downgrade() -> None:
	# Drop tables in reverse order
	op.drop_table('extracted_results')
	op.drop_table('processing_jobs')
	op.drop_table('documents')
	op.drop_table('users')