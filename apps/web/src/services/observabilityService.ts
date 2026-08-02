import { apiClient } from './apiClient';

export interface SystemMetric {
  id: string;
  organization_id?: string;
  metric_name: string;
  metric_type: string;
  value: number;
  labels?: Record<string, any>;
  created_at: string;
}

export interface ApplicationLog {
  id: string;
  organization_id?: string;
  service_name: string;
  log_level: string;
  message: string;
  structured_data?: Record<string, any>;
  correlation_id?: string;
  request_id?: string;
  timestamp: string;
}

export interface TraceSpan {
  id: string;
  organization_id?: string;
  trace_id: string;
  span_id: string;
  parent_span_id?: string;
  name: string;
  service_name: string;
  start_time: string;
  end_time: string;
  duration_ms: number;
  status: string;
  attributes?: Record<string, any>;
}

export interface ServiceDependency {
  caller: string;
  callee: string;
  call_count: number;
  avg_duration_ms: number;
  error_rate: number;
}

export interface AlertHistory {
  id: string;
  alert_id: string;
  status_from: string;
  status_to: string;
  transition_reason?: string;
  changed_by?: string;
  timestamp: string;
}

export interface Alert {
  id: string;
  organization_id?: string;
  rule_name: string;
  metric_name: string;
  threshold: number;
  comparison_operator: string;
  current_value?: number;
  status: 'active' | 'acknowledged' | 'resolved';
  severity: 'critical' | 'warning' | 'info';
  description?: string;
  acknowledged_by?: string;
  acknowledged_at?: string;
  resolved_at?: string;
  created_at: string;
  history?: AlertHistory[];
}

export interface ServiceHealthItem {
  name: string;
  status: 'healthy' | 'unhealthy' | 'degraded';
  liveness: boolean;
  readiness: boolean;
  uptime_seconds: number;
  latency_ms: number;
  dependency_status?: Record<string, string>;
  last_checked: string;
}

export interface SystemHealthData {
  status: 'healthy' | 'unhealthy' | 'degraded';
  version: string;
  timestamp: string;
  uptime_ratio_percent: number;
  services: ServiceHealthItem[];
}

export interface DashboardConfig {
  id: string;
  organization_id?: string;
  name: string;
  dashboard_type: string;
  config: Record<string, any>;
  created_by: string;
  created_at: string;
}

export interface ObservabilityEvent {
  id: string;
  organization_id?: string;
  event_type: string;
  name: string;
  description?: string;
  severity: string;
  metadata?: Record<string, any>;
  timestamp: string;
}

export const observabilityService = {
  // Health
  getSystemHealth: async (): Promise<SystemHealthData> => {
    const res = await apiClient.get('/api/v1/observability/health');
    return res.data.data;
  },

  // Metrics
  recordMetric: async (metric: Partial<SystemMetric>): Promise<SystemMetric> => {
    const res = await apiClient.post('/api/v1/observability/metrics', metric);
    return res.data.data;
  },

  getMetrics: async (metricName?: string, durationMinutes = 60): Promise<SystemMetric[]> => {
    const res = await apiClient.get('/api/v1/observability/metrics', {
      params: { metric_name: metricName, duration_minutes: durationMinutes },
    });
    return res.data.data;
  },

  getBusinessMetrics: async (): Promise<any> => {
    const res = await apiClient.get('/api/v1/observability/business');
    return res.data.data;
  },

  getAiMetrics: async (): Promise<any> => {
    const res = await apiClient.get('/api/v1/observability/ai');
    return res.data.data;
  },

  // Logs
  submitLog: async (log: Partial<ApplicationLog>): Promise<ApplicationLog> => {
    const res = await apiClient.post('/api/v1/observability/logs', log);
    return res.data.data;
  },

  getLogs: async (params: {
    service_name?: string;
    log_level?: string;
    keyword?: string;
    correlation_id?: string;
    request_id?: string;
    page?: number;
    page_size?: number;
  }): Promise<{ logs: ApplicationLog[]; total_count: number; page: number; page_size: number }> => {
    const res = await apiClient.get('/api/v1/observability/logs', { params });
    return res.data.data;
  },

  // Traces
  submitTraceSpan: async (span: Partial<TraceSpan>): Promise<TraceSpan> => {
    const res = await apiClient.post('/api/v1/observability/traces', span);
    return res.data.data;
  },

  getTraces: async (params?: {
    trace_id?: string;
    service_name?: string;
    status?: string;
  }): Promise<TraceSpan[]> => {
    const res = await apiClient.get('/api/v1/observability/traces', { params });
    return res.data.data;
  },

  getDependencyMap: async (): Promise<ServiceDependency[]> => {
    const res = await apiClient.get('/api/v1/observability/traces/dependencies');
    return res.data.data;
  },

  // Alerts
  createAlertRule: async (alert: Partial<Alert>): Promise<Alert> => {
    const res = await apiClient.post('/api/v1/observability/alerts', alert);
    return res.data.data;
  },

  getAlerts: async (status?: string, severity?: string): Promise<Alert[]> => {
    const res = await apiClient.get('/api/v1/observability/alerts', {
      params: { status, severity },
    });
    return res.data.data;
  },

  updateAlertStatus: async (alertId: string, status: string, description?: string): Promise<Alert> => {
    const res = await apiClient.put(`/api/v1/observability/alerts/${alertId}`, {
      status,
      description,
    });
    return res.data.data;
  },

  // Dashboards layouts
  getDashboardConfig: async (dashboardType: string): Promise<DashboardConfig> => {
    const res = await apiClient.get(`/api/v1/observability/dashboards/${dashboardType}`);
    return res.data.data;
  },

  saveDashboardConfig: async (dashboardType: string, name: string, config: Record<string, any>): Promise<DashboardConfig> => {
    const res = await apiClient.post(`/api/v1/observability/dashboards/${dashboardType}`, {
      name,
      config,
    });
    return res.data.data;
  },

  // Events
  getEvents: async (): Promise<ObservabilityEvent[]> => {
    const res = await apiClient.get('/api/v1/observability/events');
    return res.data.data;
  },
};
