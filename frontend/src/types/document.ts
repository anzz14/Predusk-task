export interface ExtractedResult {
  id: string;
  document_id: string;
  job_id: string;
  word_count: number;
  readability_score: number;
  primary_keywords: KeywordData[];
  auto_summary: string;
  user_edited_summary: string | null;
  is_finalized: boolean;
  finalized_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface KeywordData {
  keyword: string;
  count: number;
  density_percentage: number;
}

export interface ProcessingJob {
  id: string;
  document_id: string;
  celery_task_id: string | null;
  status: 'queued' | 'processing' | 'completed' | 'failed' | 'finalized';
  progress_percentage: number;
  current_stage: string;
  error_message: string | null;
  retry_count: number;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
}

export interface Document {
  id: string;
  user_id: string;
  original_filename: string;
  file_path: string;
  file_size: number;
  mime_type: string;
  upload_timestamp: string;
  created_at: string;
}

export interface DocumentResponse {
  id: string;
  user_id: string;
  original_filename: string;
  file_path: string;
  file_size: number;
  mime_type: string;
  upload_timestamp: string;
  created_at: string;
  processing_jobs: ProcessingJob[];
  extracted_result: ExtractedResult | null;
}

export interface DocumentListResponse {
  items: DocumentResponse[];
  total: number;
  page: number;
  page_size: number;
}

export interface PatchResultRequest {
  user_edited_summary: string;
}

export interface ExportRow {
  filename: string;
  word_count: number;
  readability_score: number;
  primary_keywords: string;
  auto_summary: string;
  user_edited_summary: string | null;
  finalized_at: string;
}

export interface UploadResponse {
  document_id: string;
  job_id: string;
}