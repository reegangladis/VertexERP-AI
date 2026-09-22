import React, { useEffect, useState } from "react";
import {
  Activity,
  AlertOctagon,
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Clock,
  Copy,
  Cpu,
  Database,
  FileCode,
  FileSpreadsheet,
  Mail,
  Play,
  Plus,
  RefreshCw,
  RotateCw,
  Send,
  Server,
  ShieldAlert,
  Sliders,
  Terminal,
  Trash2,
  X,
  XCircle,
  Zap,
} from "lucide-react";
import { jobsApi } from "../api/jobsApi";
import {
  BackgroundJob,
  BackgroundJobDetail,
  JobCreatePayload,
  JobPriority,
  JobSchedule,
  JobStatus,
  JobType,
  QueueMetrics,
} from "../types";

export const BackgroundJobsDashboardPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"jobs" | "schedules" | "workers">("jobs");
  const [metrics, setMetrics] = useState<QueueMetrics | null>(null);
  const [jobs, setJobs] = useState<BackgroundJob[]>([]);
  const [schedules, setSchedules] = useState<JobSchedule[]>([]);
  const [totalJobs, setTotalJobs] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Filters
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [typeFilter, setTypeFilter] = useState<string>("");
  const [dlqOnly, setDlqOnly] = useState(false);

  // Modals & Drawers
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);
  const [selectedJobDetail, setSelectedJobDetail] = useState<BackgroundJobDetail | null>(null);
  const [isDetailLoading, setIsDetailLoading] = useState(false);
  const [showEnqueueModal, setShowEnqueueModal] = useState(false);
  const [showScheduleModal, setShowScheduleModal] = useState(false);

  // Enqueue Form State
  const [newJobType, setNewJobType] = useState<JobType>("email");
  const [newJobName, setNewJobName] = useState("");
  const [newJobPriority, setNewJobPriority] = useState(0);
  const [newJobPayloadText, setNewJobPayloadText] = useState(
    JSON.stringify({ recipient: "operations@vertexerp.com", template: "invoice_ready" }, null, 2)
  );
  const [newJobMaxRetries, setNewJobMaxRetries] = useState(3);
  const [newJobTimeout, setNewJobTimeout] = useState(60);

  // Schedule Form State
  const [newSchedName, setNewSchedName] = useState("");
  const [newSchedType, setNewSchedType] = useState("reports");
  const [newSchedCron, setNewSchedCron] = useState("0 * * * *");
  const [newSchedPayload, setNewSchedPayload] = useState('{\n  "report_type": "balance_sheet"\n}');

  // Action status message
  const [bannerMessage, setBannerMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const fetchDashboardData = async () => {
    try {
      const [m, j, s] = await Promise.all([
        jobsApi.getMetrics().catch(() => null),
        jobsApi.listJobs({
          status: statusFilter || undefined,
          job_type: typeFilter || undefined,
          is_dead_letter: dlqOnly ? true : undefined,
          limit: 50,
        }),
        jobsApi.listSchedules().catch(() => []),
      ]);
      setMetrics(m);
      setJobs(j.items);
      setTotalJobs(j.total);
      setSchedules(s);
    } catch (err: any) {
      console.error("Failed to load dashboard data", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [statusFilter, typeFilter, dlqOnly]);

  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(fetchDashboardData, 4000);
    return () => clearInterval(interval);
  }, [autoRefresh, statusFilter, typeFilter, dlqOnly]);

  const loadJobDetail = async (jobId: string) => {
    setSelectedJobId(jobId);
    setIsDetailLoading(true);
    try {
      const detail = await jobsApi.getJobDetails(jobId);
      setSelectedJobDetail(detail);
    } catch (err: any) {
      console.error("Failed to load job details", err);
    } finally {
      setIsDetailLoading(false);
    }
  };

  const handleRetryJob = async (jobId: string) => {
    try {
      await jobsApi.retryJob(jobId, true, false);
      setBannerMessage({ type: "success", text: `Job ${jobId.slice(0, 8)} re-queued for processing.` });
      fetchDashboardData();
      if (selectedJobId === jobId) {
        loadJobDetail(jobId);
      }
    } catch (err: any) {
      setBannerMessage({ type: "error", text: `Failed to retry job: ${err.message}` });
    }
  };

  const handleCancelJob = async (jobId: string) => {
    try {
      await jobsApi.cancelJob(jobId, "Cancelled from Dashboard");
      setBannerMessage({ type: "success", text: `Job ${jobId.slice(0, 8)} successfully cancelled.` });
      fetchDashboardData();
      if (selectedJobId === jobId) {
        loadJobDetail(jobId);
      }
    } catch (err: any) {
      setBannerMessage({ type: "error", text: `Failed to cancel job: ${err.message}` });
    }
  };

  const handleTriggerSchedule = async (scheduleId: string) => {
    try {
      await jobsApi.triggerSchedule(scheduleId);
      setBannerMessage({ type: "success", text: "Scheduled job triggered immediately." });
      fetchDashboardData();
    } catch (err: any) {
      setBannerMessage({ type: "error", text: `Trigger failed: ${err.message}` });
    }
  };

  const handleDeleteSchedule = async (scheduleId: string) => {
    try {
      await jobsApi.deleteSchedule(scheduleId);
      setBannerMessage({ type: "success", text: "Recurring schedule deleted." });
      fetchDashboardData();
    } catch (err: any) {
      setBannerMessage({ type: "error", text: `Delete failed: ${err.message}` });
    }
  };

  const handleEnqueueSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      let parsedPayload = {};
      try {
        parsedPayload = JSON.parse(newJobPayloadText);
      } catch {
        throw new Error("Payload must be valid JSON format");
      }

      await jobsApi.enqueueJob({
        job_type: newJobType,
        job_name: newJobName || `${newJobType.toUpperCase()} Task`,
        priority: newJobPriority,
        payload: parsedPayload,
        max_retries: newJobMaxRetries,
        timeout_seconds: newJobTimeout,
      });

      setShowEnqueueModal(false);
      setBannerMessage({ type: "success", text: "New background job successfully enqueued (HTTP 202)." });
      fetchDashboardData();
    } catch (err: any) {
      setBannerMessage({ type: "error", text: err.message });
    }
  };

  const handleCreateScheduleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      let parsed = {};
      try {
        parsed = JSON.parse(newSchedPayload);
      } catch {
        throw new Error("Payload template must be valid JSON");
      }

      await jobsApi.createSchedule({
        name: newSchedName,
        job_type: newSchedType,
        cron_expression: newSchedCron,
        payload_template: parsed,
      });

      setShowScheduleModal(false);
      setBannerMessage({ type: "success", text: "Recurring cron schedule established." });
      fetchDashboardData();
    } catch (err: any) {
      setBannerMessage({ type: "error", text: err.message });
    }
  };

  const getStatusBadge = (status: JobStatus | string, isDeadLetter?: boolean) => {
    if (isDeadLetter || status === "DEAD_LETTER") {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30 animate-pulse">
          <AlertOctagon className="w-3 h-3 text-rose-400" />
          DEAD LETTER
        </span>
      );
    }
    switch (status) {
      case "COMPLETED":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
            <CheckCircle2 className="w-3 h-3 text-emerald-400" />
            COMPLETED
          </span>
        );
      case "RUNNING":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/30">
            <RotateCw className="w-3 h-3 text-amber-400 animate-spin" />
            RUNNING
          </span>
        );
      case "QUEUED":
      case "PENDING":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-blue-500/20 text-blue-300 border border-blue-500/30">
            <Clock className="w-3 h-3 text-blue-400" />
            {status}
          </span>
        );
      case "FAILED":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-red-500/20 text-red-300 border border-red-500/30">
            <AlertTriangle className="w-3 h-3 text-red-400" />
            FAILED
          </span>
        );
      case "CANCELLED":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-slate-500/20 text-slate-300 border border-slate-500/30">
            <XCircle className="w-3 h-3 text-slate-400" />
            CANCELLED
          </span>
        );
      default:
        return <span className="text-xs text-slate-400">{status}</span>;
    }
  };

  const getPriorityBadge = (priority: number) => {
    if (priority === 2) {
      return (
        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30">
          CRITICAL
        </span>
      );
    }
    if (priority === 1) {
      return (
        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
          HIGH
        </span>
      );
    }
    return (
      <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-800 text-slate-400 border border-slate-700">
        NORMAL
      </span>
    );
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "email":
        return <Mail className="w-4 h-4 text-sky-400" />;
      case "document_ingestion":
        return <FileCode className="w-4 h-4 text-emerald-400" />;
      case "embeddings":
        return <Cpu className="w-4 h-4 text-purple-400" />;
      case "reports":
        return <FileSpreadsheet className="w-4 h-4 text-amber-400" />;
      case "notifications":
        return <Zap className="w-4 h-4 text-indigo-400" />;
      case "scheduled_jobs":
        return <Clock className="w-4 h-4 text-teal-400" />;
      case "integrations":
        return <Server className="w-4 h-4 text-pink-400" />;
      default:
        return <Activity className="w-4 h-4 text-slate-400" />;
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header & Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-500 text-white shadow-lg shadow-brand-500/20">
              <Cpu className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
                Background Processing & Worker Subsystem
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-semibold">
                  ACTIVE ENGINE
                </span>
              </h1>
              <p className="text-xs text-slate-400 mt-0.5">
                Multi-tenant asynchronous task execution with idempotency, exponential backoff, timeouts, and DLQ.
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium border transition-colors ${
              autoRefresh
                ? "bg-emerald-500/10 text-emerald-300 border-emerald-500/30 hover:bg-emerald-500/20"
                : "bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700"
            }`}
          >
            <RefreshCw className={`w-3.5 h-3.5 ${autoRefresh ? "animate-spin" : ""}`} />
            {autoRefresh ? "Live Polling (4s)" : "Auto-Refresh Paused"}
          </button>

          <button
            onClick={() => setShowEnqueueModal(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold bg-brand-600 hover:bg-brand-500 text-white shadow-lg shadow-brand-600/30 transition-all"
          >
            <Plus className="w-4 h-4" />
            Enqueue Job
          </button>
        </div>
      </div>

      {/* Banner Alert */}
      {bannerMessage && (
        <div
          className={`p-3 rounded-lg flex items-center justify-between text-xs border ${
            bannerMessage.type === "success"
              ? "bg-emerald-950/40 text-emerald-300 border-emerald-800/60"
              : "bg-rose-950/40 text-rose-300 border-rose-800/60"
          }`}
        >
          <span>{bannerMessage.text}</span>
          <button onClick={() => setBannerMessage(null)} className="text-slate-400 hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Metrics Row */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Total Tasks</span>
            <Database className="w-4 h-4 text-slate-500" />
          </div>
          <div className="text-2xl font-bold text-white mt-2">{metrics?.total_jobs ?? totalJobs}</div>
          <div className="text-[10px] text-slate-500 mt-1">Tenant aggregate</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="flex items-center justify-between text-amber-400 text-xs font-medium">
            <span>Running Now</span>
            <RotateCw className="w-4 h-4 text-amber-400 animate-spin" />
          </div>
          <div className="text-2xl font-bold text-amber-300 mt-2">{metrics?.running_jobs ?? 0}</div>
          <div className="text-[10px] text-slate-500 mt-1">Active worker slots</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="flex items-center justify-between text-blue-400 text-xs">
            <span>Queued / Ready</span>
            <Clock className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-bold text-blue-300 mt-2">
            {(metrics?.pending_jobs ?? 0) + (metrics?.queued_jobs ?? 0)}
          </div>
          <div className="text-[10px] text-slate-500 mt-1">Priority queue depth</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="flex items-center justify-between text-emerald-400 text-xs">
            <span>Completed</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-300 mt-2">{metrics?.completed_jobs ?? 0}</div>
          <div className="text-[10px] text-slate-500 mt-1">Successful runs</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="flex items-center justify-between text-red-400 text-xs">
            <span>Failed Retrying</span>
            <AlertTriangle className="w-4 h-4 text-red-400" />
          </div>
          <div className="text-2xl font-bold text-red-300 mt-2">{metrics?.failed_jobs ?? 0}</div>
          <div className="text-[10px] text-slate-500 mt-1">In backoff schedule</div>
        </div>

        <div
          onClick={() => setDlqOnly(!dlqOnly)}
          className={`border p-4 rounded-xl cursor-pointer transition-all ${
            dlqOnly
              ? "bg-rose-950/40 border-rose-500 text-white ring-2 ring-rose-500/30"
              : "bg-slate-900 border-rose-900/50 hover:border-rose-700/80"
          }`}
        >
          <div className="flex items-center justify-between text-rose-400 text-xs font-semibold">
            <span>Dead-Letter (DLQ)</span>
            <ShieldAlert className="w-4 h-4 text-rose-400 animate-pulse" />
          </div>
          <div className="text-2xl font-bold text-rose-300 mt-2">{metrics?.dead_letter_jobs ?? 0}</div>
          <div className="text-[10px] text-rose-400/80 mt-1">{dlqOnly ? "Filtering DLQ active" : "Click to isolate DLQ"}</div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setActiveTab("jobs")}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition-colors ${
              activeTab === "jobs"
                ? "bg-brand-600 text-white shadow-md shadow-brand-600/30"
                : "text-slate-400 hover:text-white hover:bg-slate-800"
            }`}
          >
            Live Jobs Stream ({jobs.length})
          </button>
          <button
            onClick={() => setActiveTab("schedules")}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition-colors ${
              activeTab === "schedules"
                ? "bg-brand-600 text-white shadow-md shadow-brand-600/30"
                : "text-slate-400 hover:text-white hover:bg-slate-800"
            }`}
          >
            Recurring Cron Schedules ({schedules.length})
          </button>
          <button
            onClick={() => setActiveTab("workers")}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition-colors ${
              activeTab === "workers"
                ? "bg-brand-600 text-white shadow-md shadow-brand-600/30"
                : "text-slate-400 hover:text-white hover:bg-slate-800"
            }`}
          >
            Registered Workers (7)
          </button>
        </div>

        {activeTab === "jobs" && (
          <div className="flex items-center gap-2">
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="bg-slate-900 border border-slate-700 text-slate-300 text-xs rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-brand-500"
            >
              <option value="">All Worker Types</option>
              <option value="email">Email Worker</option>
              <option value="document_ingestion">Document Ingestion (RAG)</option>
              <option value="embeddings">Embeddings Worker</option>
              <option value="reports">Reports Worker</option>
              <option value="notifications">Notifications Worker</option>
              <option value="scheduled_jobs">Scheduled Jobs</option>
              <option value="integrations">Integrations Worker</option>
            </select>

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-slate-900 border border-slate-700 text-slate-300 text-xs rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-brand-500"
            >
              <option value="">All Statuses</option>
              <option value="RUNNING">RUNNING</option>
              <option value="QUEUED">QUEUED</option>
              <option value="COMPLETED">COMPLETED</option>
              <option value="FAILED">FAILED</option>
              <option value="DEAD_LETTER">DEAD_LETTER</option>
              <option value="CANCELLED">CANCELLED</option>
            </select>
          </div>
        )}

        {activeTab === "schedules" && (
          <button
            onClick={() => setShowScheduleModal(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-white border border-slate-700"
          >
            <Plus className="w-3.5 h-3.5" />
            New Schedule
          </button>
        )}
      </div>

      {/* Main Content Area */}
      {activeTab === "jobs" && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/60 text-slate-400 font-semibold border-b border-slate-800 uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="py-3 px-4">Job Name & ID</th>
                  <th className="py-3 px-4">Type</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Priority</th>
                  <th className="py-3 px-4">Attempts</th>
                  <th className="py-3 px-4">Created / Runtime</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {jobs.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-12 text-center text-slate-500">
                      No background jobs match the active filters.
                    </td>
                  </tr>
                ) : (
                  jobs.map((job) => (
                    <tr
                      key={job.id}
                      onClick={() => loadJobDetail(job.id)}
                      className="hover:bg-slate-800/40 cursor-pointer transition-colors"
                    >
                      <td className="py-3 px-4">
                        <div className="font-semibold text-slate-200">{job.job_name}</div>
                        <div className="text-[10px] text-slate-500 font-mono flex items-center gap-2 mt-0.5">
                          <span>{job.id.slice(0, 8)}...</span>
                          {job.correlation_id && (
                            <span className="px-1.5 py-0.2 rounded bg-slate-800 text-slate-400">
                              {job.correlation_id.slice(0, 14)}
                            </span>
                          )}
                        </div>
                      </td>

                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2 text-slate-300 font-medium">
                          {getTypeIcon(job.job_type)}
                          <span className="capitalize">{job.job_type.replace("_", " ")}</span>
                        </div>
                      </td>

                      <td className="py-3 px-4">{getStatusBadge(job.status, job.is_dead_letter)}</td>

                      <td className="py-3 px-4">{getPriorityBadge(job.priority)}</td>

                      <td className="py-3 px-4">
                        <div className="text-slate-300 font-medium">
                          {job.retry_count} / {job.max_retries}
                        </div>
                        {job.timeout_seconds && (
                          <div className="text-[10px] text-slate-500">Timeout: {job.timeout_seconds}s</div>
                        )}
                      </td>

                      <td className="py-3 px-4">
                        <div className="text-slate-300">
                          {new Date(job.created_at).toLocaleTimeString()}
                        </div>
                        <div className="text-[10px] text-slate-500">
                          {new Date(job.created_at).toLocaleDateString()}
                        </div>
                      </td>

                      <td className="py-3 px-4 text-right" onClick={(e) => e.stopPropagation()}>
                        <div className="flex items-center justify-end gap-2">
                          {(job.status === "FAILED" || job.status === "DEAD_LETTER" || job.is_dead_letter) && (
                            <button
                              onClick={() => handleRetryJob(job.id)}
                              title="Retry Job"
                              className="p-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 transition-colors"
                            >
                              <RotateCw className="w-3.5 h-3.5" />
                            </button>
                          )}
                          {(job.status === "PENDING" || job.status === "QUEUED" || job.status === "RUNNING") && (
                            <button
                              onClick={() => handleCancelJob(job.id)}
                              title="Cancel Job"
                              className="p-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 transition-colors"
                            >
                              <XCircle className="w-3.5 h-3.5" />
                            </button>
                          )}
                          <button
                            onClick={() => loadJobDetail(job.id)}
                            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
                          >
                            <ArrowRight className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Schedules Tab */}
      {activeTab === "schedules" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {schedules.map((s) => (
            <div key={s.id} className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="p-2 rounded-lg bg-teal-500/10 text-teal-400 border border-teal-500/20">
                    <Clock className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-white">{s.name}</h3>
                    <span className="text-[10px] text-slate-500 font-mono">{s.job_type}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-slate-800 text-slate-300 border border-slate-700">
                    {s.cron_expression}
                  </span>
                  <button
                    onClick={() => handleDeleteSchedule(s.id)}
                    className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              {s.description && <p className="text-xs text-slate-400">{s.description}</p>}

              <div className="bg-slate-950 p-2.5 rounded-lg text-[11px] font-mono text-slate-400 overflow-x-auto">
                <pre>{JSON.stringify(s.payload_template, null, 2)}</pre>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-slate-800/80 text-xs">
                <div className="text-slate-500 text-[10px]">
                  Next Run: {s.next_run_at ? new Date(s.next_run_at).toLocaleString() : "Pending evaluation"}
                </div>
                <button
                  onClick={() => handleTriggerSchedule(s.id)}
                  className="flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold bg-brand-600 hover:bg-brand-500 text-white shadow transition-all"
                >
                  <Play className="w-3 h-3" />
                  Trigger Now
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Registered Workers Tab */}
      {activeTab === "workers" && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { type: "email", name: "Transactional Email Worker", desc: "Templates (invoice, welcome, alerts), SMTP simulation, delivery telemetry." },
            { type: "document_ingestion", name: "RAG Document Ingestion Worker", desc: "Parses, cleans, chunks, embeds, and indexes knowledge documents asynchronously." },
            { type: "embeddings", name: "Batch Vector Embeddings Worker", desc: "High-throughput vector generation for catalog items, knowledge chunks, and CRM notes." },
            { type: "reports", name: "Heavy Analytical Reports Worker", desc: "Generates GL Balance Sheets, inventory valuations, sales summaries in JSON/CSV artifacts." },
            { type: "notifications", name: "Multi-Channel Notifications Worker", desc: "In-app alerts, mobile push, and real-time chat broadcasts." },
            { type: "scheduled_jobs", name: "Scheduled Cron Maintenance Worker", desc: "Periodic inventory reorder scans, daily closing balance checks, and session cleanup." },
            { type: "integrations", name: "Outbound Webhooks & Integrations", desc: "Cryptographic HMAC-SHA256 signing for partner synchronization (Shopify, QuickBooks, Salesforce)." },
          ].map((w) => (
            <div key={w.type} className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-slate-800 border border-slate-700">{getTypeIcon(w.type)}</div>
                <div>
                  <h3 className="text-sm font-semibold text-white">{w.name}</h3>
                  <span className="text-[10px] text-brand-400 font-mono">job_type: "{w.type}"</span>
                </div>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">{w.desc}</p>
              <div className="pt-2 border-t border-slate-800 text-[10px] text-emerald-400 font-semibold flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
                ONLINE &amp; REGISTERED
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Slide-over Job Details Drawer */}
      {selectedJobId && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex justify-end">
          <div className="w-full max-w-xl bg-slate-900 border-l border-slate-800 h-full overflow-y-auto p-6 space-y-5 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div>
                <h2 className="text-base font-bold text-white flex items-center gap-2">
                  Job Execution Detail
                  {selectedJobDetail && getStatusBadge(selectedJobDetail.status, selectedJobDetail.is_dead_letter)}
                </h2>
                <div className="text-xs text-slate-400 font-mono mt-0.5">{selectedJobId}</div>
              </div>
              <button
                onClick={() => setSelectedJobId(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {isDetailLoading || !selectedJobDetail ? (
              <div className="py-12 text-center text-slate-400 flex items-center justify-center gap-2">
                <RotateCw className="w-4 h-4 animate-spin text-brand-400" />
                Loading detailed telemetry...
              </div>
            ) : (
              <div className="space-y-5">
                {/* Status & Error Summary */}
                {selectedJobDetail.error_message && (
                  <div className="p-3.5 rounded-xl bg-rose-950/40 border border-rose-800/60 text-xs text-rose-300 space-y-1.5">
                    <div className="font-semibold flex items-center gap-2">
                      <AlertOctagon className="w-4 h-4 text-rose-400" />
                      {selectedJobDetail.is_dead_letter ? "Dead-Letter Reason" : "Execution Error"}
                    </div>
                    <div className="font-mono text-[11px] break-words">
                      {selectedJobDetail.dead_letter_reason || selectedJobDetail.error_message}
                    </div>
                  </div>
                )}

                {/* Configuration Specs */}
                <div className="grid grid-cols-2 gap-3 bg-slate-950/60 p-3.5 rounded-xl border border-slate-800 text-xs">
                  <div>
                    <span className="text-slate-500">Job Type:</span>
                    <div className="font-medium text-slate-200 mt-0.5">{selectedJobDetail.job_type}</div>
                  </div>
                  <div>
                    <span className="text-slate-500">Correlation ID:</span>
                    <div className="font-mono text-[11px] text-slate-300 mt-0.5 truncate">
                      {selectedJobDetail.correlation_id || "None"}
                    </div>
                  </div>
                  <div>
                    <span className="text-slate-500">Timeout:</span>
                    <div className="font-medium text-slate-200 mt-0.5">{selectedJobDetail.timeout_seconds}s</div>
                  </div>
                  <div>
                    <span className="text-slate-500">Retry Count:</span>
                    <div className="font-medium text-slate-200 mt-0.5">
                      {selectedJobDetail.retry_count} of {selectedJobDetail.max_retries}
                    </div>
                  </div>
                </div>

                {/* Execution Attempt Logs Timeline */}
                <div>
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2.5">
                    Execution Attempts ({selectedJobDetail.execution_logs.length})
                  </h3>
                  <div className="space-y-2">
                    {selectedJobDetail.execution_logs.map((log) => (
                      <div
                        key={log.id}
                        className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-xs space-y-1.5"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-slate-200">Attempt #{log.attempt_number}</span>
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              log.status === "COMPLETED"
                                ? "bg-emerald-500/20 text-emerald-300"
                                : log.status === "FAILED"
                                ? "bg-rose-500/20 text-rose-300"
                                : "bg-amber-500/20 text-amber-300"
                            }`}
                          >
                            {log.status} ({log.duration_ms.toFixed(1)}ms)
                          </span>
                        </div>
                        {log.worker_id && (
                          <div className="text-[10px] text-slate-500 font-mono">Worker: {log.worker_id}</div>
                        )}
                        {log.error_message && (
                          <div className="text-rose-400 font-mono text-[10px] mt-1 break-words">
                            {log.error_message}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Payload & Result JSON */}
                <div className="space-y-3">
                  <div>
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                      Input Payload
                    </h3>
                    <pre className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-[11px] font-mono text-slate-300 overflow-x-auto max-h-48">
                      {JSON.stringify(selectedJobDetail.payload_json, null, 2)}
                    </pre>
                  </div>

                  {selectedJobDetail.result_json && (
                    <div>
                      <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-400 mb-1.5">
                        Execution Result Artifacts
                      </h3>
                      <pre className="bg-slate-950 p-3 rounded-lg border border-emerald-900/40 text-[11px] font-mono text-emerald-300 overflow-x-auto max-h-56">
                        {JSON.stringify(selectedJobDetail.result_json, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>

                {/* Action Buttons */}
                <div className="flex items-center gap-3 pt-3 border-t border-slate-800">
                  <button
                    onClick={() => handleRetryJob(selectedJobDetail.id)}
                    className="flex-1 flex items-center justify-center gap-2 py-2 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white shadow transition-all"
                  >
                    <RotateCw className="w-3.5 h-3.5" />
                    Retry Job
                  </button>
                  {selectedJobDetail.status !== "COMPLETED" && (
                    <button
                      onClick={() => handleCancelJob(selectedJobDetail.id)}
                      className="flex-1 flex items-center justify-center gap-2 py-2 rounded-lg text-xs font-semibold bg-rose-600/80 hover:bg-rose-500 text-white transition-all"
                    >
                      <XCircle className="w-3.5 h-3.5" />
                      Cancel
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Enqueue Modal */}
      {showEnqueueModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <Plus className="w-5 h-5 text-brand-400" />
                Enqueue Background Job
              </h2>
              <button onClick={() => setShowEnqueueModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleEnqueueSubmit} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 font-medium mb-1">Worker Job Type</label>
                  <select
                    value={newJobType}
                    onChange={(e) => setNewJobType(e.target.value as JobType)}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200 focus:outline-none focus:border-brand-500"
                  >
                    <option value="email">email (Email Delivery)</option>
                    <option value="document_ingestion">document_ingestion (RAG Pipeline)</option>
                    <option value="embeddings">embeddings (Batch Embeddings)</option>
                    <option value="reports">reports (Heavy Reports)</option>
                    <option value="notifications">notifications (Push/In-App)</option>
                    <option value="scheduled_jobs">scheduled_jobs (Periodic Scan)</option>
                    <option value="integrations">integrations (Outbound HMAC Webhook)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-400 font-medium mb-1">Priority</label>
                  <select
                    value={newJobPriority}
                    onChange={(e) => setNewJobPriority(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200 focus:outline-none focus:border-brand-500"
                  >
                    <option value={0}>0 - NORMAL Priority</option>
                    <option value={1}>1 - HIGH Priority</option>
                    <option value={2}>2 - CRITICAL Priority</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-slate-400 font-medium mb-1">Job Name / Description</label>
                <input
                  type="text"
                  placeholder="e.g. Monthly Inventory Valuation Export"
                  value={newJobName}
                  onChange={(e) => setNewJobName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200 focus:outline-none focus:border-brand-500"
                />
              </div>

              <div>
                <label className="block text-slate-400 font-medium mb-1">Payload JSON</label>
                <textarea
                  rows={5}
                  value={newJobPayloadText}
                  onChange={(e) => setNewJobPayloadText(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 font-mono text-[11px] text-slate-300 focus:outline-none focus:border-brand-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 font-medium mb-1">Max Retries</label>
                  <input
                    type="number"
                    min={0}
                    max={10}
                    value={newJobMaxRetries}
                    onChange={(e) => setNewJobMaxRetries(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 font-medium mb-1">Timeout (seconds)</label>
                  <input
                    type="number"
                    min={1}
                    max={3600}
                    value={newJobTimeout}
                    onChange={(e) => setNewJobTimeout(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowEnqueueModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white font-semibold shadow-lg shadow-brand-600/30"
                >
                  Enqueue (202 Accepted)
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Schedule Modal */}
      {showScheduleModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <Clock className="w-5 h-5 text-teal-400" />
                Create Recurring Cron Schedule
              </h2>
              <button onClick={() => setShowScheduleModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateScheduleSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-400 font-medium mb-1">Schedule Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Hourly Ledger Reconciliation"
                  value={newSchedName}
                  onChange={(e) => setNewSchedName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200 focus:outline-none focus:border-brand-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 font-medium mb-1">Job Type</label>
                  <select
                    value={newSchedType}
                    onChange={(e) => setNewSchedType(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200"
                  >
                    <option value="reports">reports</option>
                    <option value="scheduled_jobs">scheduled_jobs</option>
                    <option value="email">email</option>
                    <option value="integrations">integrations</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-400 font-medium mb-1">Cron Expression</label>
                  <input
                    type="text"
                    required
                    placeholder="0 * * * * or @hourly"
                    value={newSchedCron}
                    onChange={(e) => setNewSchedCron(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200 font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-400 font-medium mb-1">Payload Template (JSON)</label>
                <textarea
                  rows={4}
                  value={newSchedPayload}
                  onChange={(e) => setNewSchedPayload(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 font-mono text-[11px] text-slate-300"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowScheduleModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-lg bg-teal-600 hover:bg-teal-500 text-white font-semibold shadow-lg"
                >
                  Create Schedule
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
