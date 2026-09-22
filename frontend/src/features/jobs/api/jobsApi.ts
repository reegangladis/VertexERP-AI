/**
 * Background Jobs & Asynchronous Workers API Client
 * VertexERP AI V2
 */

import { apiClient } from "@/lib/api-client";
import {
  BackgroundJob,
  BackgroundJobDetail,
  JobCreatePayload,
  JobSchedule,
  JobScheduleCreatePayload,
  QueueMetrics,
} from "../types";

export const jobsApi = {
  /**
   * Enqueue a new background job. Returns HTTP 202 Accepted.
   */
  async enqueueJob(payload: JobCreatePayload, eager = false): Promise<BackgroundJob> {
    return apiClient<BackgroundJob>(`/jobs?eager=${eager}`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /**
   * List background jobs with filtering and pagination.
   */
  async listJobs(params?: {
    job_type?: string;
    status?: string;
    is_dead_letter?: boolean;
    skip?: number;
    limit?: number;
  }): Promise<{ items: BackgroundJob[]; total: number; skip: number; limit: number }> {
    const query = new URLSearchParams();
    if (params?.job_type) query.set("job_type", params.job_type);
    if (params?.status) query.set("status", params.status);
    if (params?.is_dead_letter !== undefined) query.set("is_dead_letter", String(params.is_dead_letter));
    if (params?.skip !== undefined) query.set("skip", String(params.skip));
    if (params?.limit !== undefined) query.set("limit", String(params.limit));

    const qs = query.toString();
    return apiClient<{ items: BackgroundJob[]; total: number; skip: number; limit: number }>(
      `/jobs${qs ? `?${qs}` : ""}`
    );
  },

  /**
   * Get detailed job information including execution attempt logs and payload.
   */
  async getJobDetails(jobId: string): Promise<BackgroundJobDetail> {
    return apiClient<BackgroundJobDetail>(`/jobs/${jobId}`);
  },

  /**
   * Manually retry a failed or dead-letter job.
   */
  async retryJob(jobId: string, forceReset = true, eager = false): Promise<BackgroundJob> {
    return apiClient<BackgroundJob>(`/jobs/${jobId}/retry?eager=${eager}`, {
      method: "POST",
      body: JSON.stringify({ force_reset: forceReset }),
    });
  },

  /**
   * Cancel a pending or running job.
   */
  async cancelJob(jobId: string, reason?: string): Promise<BackgroundJob> {
    return apiClient<BackgroundJob>(`/jobs/${jobId}/cancel`, {
      method: "POST",
      body: JSON.stringify({ reason }),
    });
  },

  /**
   * Retrieve real-time queue depths and status distribution.
   */
  async getMetrics(): Promise<QueueMetrics> {
    return apiClient<QueueMetrics>("/jobs/metrics");
  },

  /**
   * List all recurring cron schedules.
   */
  async listSchedules(): Promise<JobSchedule[]> {
    return apiClient<JobSchedule[]>("/jobs/schedules");
  },

  /**
   * Create a recurring cron job schedule.
   */
  async createSchedule(payload: JobScheduleCreatePayload): Promise<JobSchedule> {
    return apiClient<JobSchedule>("/jobs/schedules", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /**
   * Delete a recurring schedule.
   */
  async deleteSchedule(scheduleId: string): Promise<{ message: string }> {
    return apiClient<{ message: string }>(`/jobs/schedules/${scheduleId}`, {
      method: "DELETE",
    });
  },

  /**
   * Manually trigger an immediate run of a scheduled job.
   */
  async triggerSchedule(scheduleId: string, eager = false): Promise<BackgroundJob> {
    return apiClient<BackgroundJob>(`/jobs/schedules/${scheduleId}/trigger?eager=${eager}`, {
      method: "POST",
    });
  },
};
