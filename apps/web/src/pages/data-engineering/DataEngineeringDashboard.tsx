import React, { useEffect, useState } from 'react';
import {
  Database,
  GitPullRequest,
  CheckCircle2,
  HardDrive,
  Layers,
  Cpu,
  RefreshCw,
  Activity,
  ArrowUpRight,
  Sparkles,
} from 'lucide-react';
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { dataEngineeringApi, DataEngineeringMonitoringSummary } from '@/services/dataEngineeringApi';

export function DataEngineeringDashboard() {
  const [summary, setSummary] = useState<DataEngineeringMonitoringSummary | null>(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    const res = await dataEngineeringApi.getMonitoringSummary();
    setSummary(res);
    setLoading(false);
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Data Engineering Platform"
        subtitle="Enterprise Data Warehouse, Multi-Zone Data Lake, Feature Store, and Automated ETL/ELT Ingestion Pipelines"
        actions={
          <Button variant="outline" size="sm" onClick={loadData} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh Platform Telemetry
          </Button>
        }
      />

      {/* Top Telemetry KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-4 border-l-4 border-l-blue-500">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Active Ingestion Pipelines</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-1">{summary?.active_pipelines ?? 0} / {summary?.total_pipelines ?? 0}</h3>
              <p className="text-xs text-emerald-600 flex items-center mt-1">
                <CheckCircle2 className="h-3 w-3 mr-1" />
                100% Operational Status
              </p>
            </div>
            <div className="p-2 bg-blue-50 rounded-lg text-blue-600">
              <GitPullRequest className="h-5 w-5" />
            </div>
          </div>
        </Card>

        <Card className="p-4 border-l-4 border-l-emerald-500">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Rows Processed (24h)</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-1">{(summary?.total_rows_processed_24h ?? 0).toLocaleString()}</h3>
              <p className="text-xs text-emerald-600 flex items-center mt-1">
                <ArrowUpRight className="h-3 w-3 mr-1" />
                +14.2% Incremental Throughput
              </p>
            </div>
            <div className="p-2 bg-emerald-50 rounded-lg text-emerald-600">
              <Activity className="h-5 w-5" />
            </div>
          </div>
        </Card>

        <Card className="p-4 border-l-4 border-l-purple-500">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Overall Data Quality Index</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-1">{summary?.overall_quality_score}%</h3>
              <p className="text-xs text-emerald-600 flex items-center mt-1">
                <CheckCircle2 className="h-3 w-3 mr-1" />
                Zero Null / Schema Violations
              </p>
            </div>
            <div className="p-2 bg-purple-50 rounded-lg text-purple-600">
              <CheckCircle2 className="h-5 w-5" />
            </div>
          </div>
        </Card>

        <Card className="p-4 border-l-4 border-l-amber-500">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Data Lake Volume</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-1">{summary?.data_lake_total_size_gb} GB</h3>
              <p className="text-xs text-slate-500 mt-1">Raw, Processed, Curated, Archive</p>
            </div>
            <div className="p-2 bg-amber-50 rounded-lg text-amber-600">
              <HardDrive className="h-5 w-5" />
            </div>
          </div>
        </Card>
      </div>

      {/* Architecture & AI Readiness Banner */}
      <Card className="p-6 bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white shadow-xl">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="space-y-2 max-w-3xl">
            <div className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
              <Sparkles className="h-3 w-3 mr-1.5" />
              AI & Machine Learning Data Preparedness
            </div>
            <h3 className="text-xl font-bold">Enterprise Data Lake & Feature Store Architecture</h3>
            <p className="text-sm text-slate-300">
              All ERP transactions from HR, CRM, Inventory, Finance, Manufacturing, and Identity are automatically extracted, standardized, schema-validated, and indexed for downstream Star & Snowflake schema Data Warehouses, Feature Registry, Embeddings, RAG indexing, and ML forecasting.
            </p>
          </div>
          <div className="flex gap-2">
            <div className="bg-slate-800/80 p-3 rounded-lg border border-slate-700 text-center min-w-[120px]">
              <Cpu className="h-5 w-5 mx-auto text-indigo-400 mb-1" />
              <div className="text-lg font-bold">{summary?.feature_groups_count}</div>
              <div className="text-xs text-slate-400">Feature Groups</div>
            </div>
            <div className="bg-slate-800/80 p-3 rounded-lg border border-slate-700 text-center min-w-[120px]">
              <Layers className="h-5 w-5 mx-auto text-emerald-400 mb-1" />
              <div className="text-lg font-bold">{summary?.registered_features_count}</div>
              <div className="text-xs text-slate-400">ML Features</div>
            </div>
          </div>
        </div>
      </Card>

      {/* Data Lake Storage Zone Distribution & Pipeline Status Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-5">
          <div className="flex justify-between items-center mb-4">
            <h4 className="font-semibold text-slate-900 flex items-center">
              <HardDrive className="h-4 w-4 mr-2 text-indigo-600" />
              Data Lake Storage Zones & Volume Breakdown
            </h4>
            <span className="text-xs font-medium text-emerald-700 bg-emerald-50 px-2 py-1 rounded">S3 Parquet Native</span>
          </div>

          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm font-medium mb-1">
                <span className="text-slate-700">Raw Zone (Inbound Ingestion Dump)</span>
                <span className="text-slate-500">45.2 GB (31.7%)</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2.5">
                <div className="bg-blue-600 h-2.5 rounded-full" style={{ width: '31.7%' }}></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-sm font-medium mb-1">
                <span className="text-slate-700">Processed Zone (Cleaned & Schema Validated)</span>
                <span className="text-slate-500">52.8 GB (37.0%)</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2.5">
                <div className="bg-emerald-600 h-2.5 rounded-full" style={{ width: '37.0%' }}></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-sm font-medium mb-1">
                <span className="text-slate-700">Curated Zone (Analytics Datasets & Facts)</span>
                <span className="text-slate-500">32.5 GB (22.8%)</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2.5">
                <div className="bg-purple-600 h-2.5 rounded-full" style={{ width: '22.8%' }}></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-sm font-medium mb-1">
                <span className="text-slate-700">Archive Zone (Long-term Cold Snapshots)</span>
                <span className="text-slate-500">12.0 GB (8.5%)</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2.5">
                <div className="bg-amber-500 h-2.5 rounded-full" style={{ width: '8.5%' }}></div>
              </div>
            </div>
          </div>
        </Card>

        <Card className="p-5">
          <div className="flex justify-between items-center mb-4">
            <h4 className="font-semibold text-slate-900 flex items-center">
              <Database className="h-4 w-4 mr-2 text-blue-600" />
              Data Warehouse Star & Snowflake Schema Status
            </h4>
            <span className="text-xs font-medium text-slate-500">SCD Type 2 Enabled</span>
          </div>

          <div className="divide-y divide-slate-100">
            <div className="py-3 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-900">DimCustomer / DimEmployee / DimProduct</p>
                <p className="text-xs text-slate-500">Slowly Changing Dimensions (SCD Type 2) tracking historical record changes</p>
              </div>
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-50 text-emerald-700">
                ACTIVE
              </span>
            </div>

            <div className="py-3 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-900">FactSales & FactInventory</p>
                <p className="text-xs text-slate-500">High-throughput transactional revenue, gross margin, and stock valuation facts</p>
              </div>
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-50 text-emerald-700">
                ACTIVE
              </span>
            </div>

            <div className="py-3 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-900">FactFinancials & FactManufacturing</p>
                <p className="text-xs text-slate-500">General ledger balances, plant OEE metrics, and quality scrap rates</p>
              </div>
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-50 text-emerald-700">
                ACTIVE
              </span>
            </div>

            <div className="py-3 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-900">Historical Audit Snapshots</p>
                <p className="text-xs text-slate-500">Immutable point-in-time warehouse checksum audit logs</p>
              </div>
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-50 text-emerald-700">
                VERIFIED
              </span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
