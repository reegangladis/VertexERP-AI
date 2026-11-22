/**
 * Analytics Domain TypeScript Types & Data Contracts
 * VertexERP AI V2
 */

export type KPICategory = "FINANCE" | "SALES" | "INVENTORY" | "MANUFACTURING" | "HR" | "EXECUTIVE";

export type KPIUnit = "CURRENCY" | "PERCENTAGE" | "COUNT" | "DAYS" | "RATIO";

export type KPICalculationMethod = "SUM" | "COUNT" | "AVG" | "FORMULA" | "SNAPSHOT";

export type MetricHealthStatus = "ON_TRACK" | "WARNING" | "CRITICAL" | "NEUTRAL";

export type DateFilterPeriod =
  | "TODAY"
  | "THIS_WEEK"
  | "THIS_MONTH"
  | "THIS_QUARTER"
  | "THIS_YEAR"
  | "LAST_30_DAYS"
  | "LAST_90_DAYS"
  | "CUSTOM";

export type AggregationInterval = "DAILY" | "WEEKLY" | "MONTHLY" | "QUARTERLY" | "YEARLY";

export interface AnalyticsFilterParams {
  period?: DateFilterPeriod;
  start_date?: string;
  end_date?: string;
  branch_id?: string;
  cost_center_id?: string;
  interval?: AggregationInterval;
  compare_previous_period?: boolean;
}

export interface KPIDefinition {
  id: string;
  tenant_id: string;
  organization_id: string;
  code: string;
  name: string;
  description?: string | null;
  category: KPICategory;
  unit: KPIUnit;
  calculation_method: KPICalculationMethod;
  formula_expression?: string | null;
  target_value?: number | null;
  warning_threshold?: number | null;
  critical_threshold?: number | null;
  is_higher_better: boolean;
  required_permission?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface MetricCardData {
  code?: string;
  kpi_code?: string;
  name: string;
  category: KPICategory;
  unit: KPIUnit;
  current_value: number;
  previous_value?: number | null;
  delta_value?: number | null;
  delta_percentage?: number | null;
  target_value?: number | null;
  status: MetricHealthStatus;
  sparkline_points?: number[];
  formatted_value: string;
  period_label: string;
}

export interface DomainExecutiveSummary {
  domain?: string;
  period?: string;
  as_of?: string;
  period_label?: string;
  kpis: MetricCardData[];
}

export interface TimeSeriesPoint {
  timestamp: string;
  label: string;
  primary_value?: number;
  value?: number;
  secondary_value?: number | null;
  breakdown?: Record<string, number>;
}

export interface TimeSeriesData {
  title?: string;
  metric_name?: string;
  chart_type: "LINE" | "BAR" | "AREA" | "PIE" | "DONUT" | "GAUGE" | "FUNNEL" | "TABLE";
  interval?: AggregationInterval;
  series: TimeSeriesPoint[];
  breakdowns?: DimensionalBreakdownItem[];
  summary_metrics?: Record<string, any>;
}

export interface DimensionalBreakdownItem {
  dimension_key: string;
  dimension_label: string;
  total_amount: number;
  count: number;
  percentage_share?: number | null;
  percentage?: number | null;
  metadata?: Record<string, any>;
}

export interface DimensionalDistributionData {
  title?: string;
  dimension_name?: string;
  chart_type: "BAR" | "PIE" | "DONUT" | "LINE" | "AREA" | "FUNNEL" | "GAUGE" | "TABLE";
  series?: TimeSeriesPoint[];
  breakdowns: DimensionalBreakdownItem[];
  summary_metrics?: Record<string, any>;
}

export interface DashboardWidget {
  id: string;
  dashboard_id: string;
  title: string;
  widget_type: "METRIC_CARD" | "CHART_LINE" | "CHART_BAR" | "CHART_PIE" | "CHART_DONUT" | "TABLE" | "ALERT_FEED";
  kpi_code?: string | null;
  grid_x: number;
  grid_y: number;
  grid_w: number;
  grid_h: number;
  config: Record<string, any>;
  created_at?: string;
  updated_at?: string;
}

export interface Dashboard {
  id: string;
  tenant_id: string;
  organization_id: string;
  code: string;
  title: string;
  description?: string | null;
  category: string;
  is_system_default: boolean;
  is_favorite: boolean;
  refresh_interval_seconds: number;
  layout_config: Record<string, any>;
  widgets: DashboardWidget[];
  created_at: string;
  updated_at: string;
}

export interface AnalyticsReport {
  id: string;
  tenant_id: string;
  organization_id: string;
  code: string;
  title: string;
  description?: string | null;
  category: string;
  is_system: boolean;
  default_parameters: Record<string, any>;
  query_definition: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface ReportExecutionResult {
  id?: string;
  execution_id?: string;
  report_id?: string;
  report_code: string;
  report_title?: string;
  title?: string;
  status: "PENDING" | "RUNNING" | "COMPLETED" | "FAILED" | string;
  row_count?: number;
  result_summary?: { row_count?: number; [key: string]: any };
  execution_time_ms?: number;
  execution_duration_ms?: number;
  parameters?: Record<string, any>;
  headers?: string[];
  columns?: string[];
  rows: Record<string, any>[];
  csv_content?: string | null;
  error_message?: string | null;
  created_at?: string;
  executed_at?: string;
}
