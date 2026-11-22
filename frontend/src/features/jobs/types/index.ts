/**
 * Background Processing & Asynchronous Jobs Domain Types
 * VertexERP AI V2
 */

export type JobStatus =
  | "PENDING"
  | "QUEUED"
  | "RUNNING"
  | "COMPLETED"
  | "FAILED"
  | "CANCELLED"
  | "DEAD_LETTER";

export type JobPriority = 0 | 1 | 2;

export type JobType =
  | "email"
  | "document_ingestion"
  | "embeddings"
  | "reports"
  | "notifications"
  | "scheduled_jobs"
  | "integrations";

export interface JobExecutionLog {
  id: string;
  job_id: string;
  tenant_id: string;
  attempt_number: number;
  status: string;
  started_at: string;
  completed_at?: string;
  duration_ms: number;
  error_message?: string;
  stack_trace?: string;
  worker_id?: string;
  created_at: string;
}

export interface BackgroundJob {
  id: string;
  tenant_id: string;
  organization_id: string;
  job_type: JobType | string;
  job_name: string;
  status: JobStatus;
  priority: number;
  idempotency_key?: string;
  correlation_id?: string;
  retry_count: number;
  max_retries: number;
  backoff_base_seconds: number;
  timeout_seconds: number;
  is_dead_letter: boolean;
  dead_letter_reason?: string;
  scheduled_at?: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface BackgroundJobDetail extends BackgroundJob {
  payload_json: Record<string, any>;
  result_json?: Record<string, any>;
  error_message?: string;
  stack_trace?: string;
  execution_logs: JobExecutionLog[];
}

export interface JobCreatePayload {
  job_type: JobType | string;
  job_name: string;
  priority?: number;
  payload?: Record<string, any>;
  idempotency_key?: string;
  correlation_id?: string;
  max_retries?: number;
  backoff_base_seconds?: number;
  timeout_seconds?: number;
  scheduled_at?: string;
}

export interface JobSchedule {
  id: string;
  tenant_id: string;
  organization_id: string;
  name: string;
  description?: string;
  job_type: string;
  cron_expression: string;
  payload_template: Record<string, any>;
  is_enabled: boolean;
  last_run_at?: string;
  next_run_at?: string;
  created_at: string;
  updated_at: string;
}

export interface JobScheduleCreatePayload {
  name: string;
  description?: string;
  job_type: string;
  cron_expression: string;
  payload_template?: Record<string, any>;
  is_enabled?: boolean;
}

export interface QueueMetrics {
  total_jobs: number;
  pending_jobs: number;
  queued_jobs: number;
  running_jobs: number;
  completed_jobs: number;
  failed_jobs: number;
  dead_letter_jobs: number;
  active_workers: number;
  queue_depth_by_type: Record<string, number>;
}
