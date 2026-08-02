import React, { useEffect, useState } from 'react';
import {
  GitBranch,
  ArrowRight,
  Database,
  Layers,
  HardDrive,
  Cpu,
  Table as TableIcon,
} from 'lucide-react';
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';
import { dataEngineeringApi, LineageGraph } from '@/services/dataEngineeringApi';

export function LineageViewer() {
  const [lineage, setLineage] = useState<LineageGraph | null>(null);

  useEffect(() => {
    async function load() {
      const data = await dataEngineeringApi.getLineageGraph();
      setLineage(data);
    }
    load();
  }, []);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Interactive Data Lineage & Pipeline Graph"
        subtitle="End-to-end dependency graph mapping Source Systems -> Data Lake -> Warehouse Facts/Dims -> Feature Store -> Curated Datasets"
      />

      <Card className="p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-2 flex items-center">
          <GitBranch className="h-5 w-5 mr-2 text-indigo-600" />
          Pipeline DAG & Transformation Lineage Flow
        </h3>
        <p className="text-xs text-slate-500 mb-6">Visual representation of data lineage and transformation history</p>

        {/* Lineage Graph Visual Representation */}
        <div className="space-y-6 bg-slate-950 p-6 rounded-xl border border-slate-800 text-white overflow-x-auto">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 min-w-[900px] text-center text-xs">
            {/* Category 1: Source */}
            <div className="space-y-3">
              <div className="font-bold text-slate-400 uppercase tracking-wider text-[11px] pb-2 border-b border-slate-800">
                1. Source Systems
              </div>
              <div className="bg-slate-900 border border-slate-700 p-3 rounded-lg text-slate-200 space-y-1">
                <Database className="h-5 w-5 mx-auto text-blue-400 mb-1" />
                <div className="font-bold">PostgreSQL Sources</div>
                <div className="text-[10px] text-slate-400">CRM, HR, Inventory, Finance</div>
              </div>
            </div>

            {/* Category 2: Data Lake */}
            <div className="space-y-3">
              <div className="font-bold text-slate-400 uppercase tracking-wider text-[11px] pb-2 border-b border-slate-800">
                2. Data Lake Zones
              </div>
              <div className="bg-slate-900 border border-slate-700 p-3 rounded-lg text-slate-200 space-y-1">
                <HardDrive className="h-5 w-5 mx-auto text-amber-400 mb-1" />
                <div className="font-bold">Raw & Processed</div>
                <div className="text-[10px] text-slate-400">Parquet S3 Storage</div>
              </div>
            </div>

            {/* Category 3: Warehouse */}
            <div className="space-y-3">
              <div className="font-bold text-slate-400 uppercase tracking-wider text-[11px] pb-2 border-b border-slate-800">
                3. Data Warehouse
              </div>
              <div className="bg-slate-900 border border-slate-700 p-3 rounded-lg text-slate-200 space-y-1">
                <Layers className="h-5 w-5 mx-auto text-emerald-400 mb-1" />
                <div className="font-bold">Star / Snowflake</div>
                <div className="text-[10px] text-slate-400">SCD2 Dims & Fact Tables</div>
              </div>
            </div>

            {/* Category 4: Feature Store */}
            <div className="space-y-3">
              <div className="font-bold text-slate-400 uppercase tracking-wider text-[11px] pb-2 border-b border-slate-800">
                4. Feature Store
              </div>
              <div className="bg-slate-900 border border-slate-700 p-3 rounded-lg text-slate-200 space-y-1">
                <Cpu className="h-5 w-5 mx-auto text-indigo-400 mb-1" />
                <div className="font-bold">ML Feature Registry</div>
                <div className="text-[10px] text-slate-400">Offline & Online Cache</div>
              </div>
            </div>

            {/* Category 5: Curated Datasets */}
            <div className="space-y-3">
              <div className="font-bold text-slate-400 uppercase tracking-wider text-[11px] pb-2 border-b border-slate-800">
                5. Curated Datasets
              </div>
              <div className="bg-slate-900 border border-slate-700 p-3 rounded-lg text-slate-200 space-y-1">
                <TableIcon className="h-5 w-5 mx-auto text-purple-400 mb-1" />
                <div className="font-bold">Analytics Datasets</div>
                <div className="text-[10px] text-slate-400">7 Pre-built Datasets</div>
              </div>
            </div>
          </div>

          <div className="border-t border-slate-800 pt-4 mt-6">
            <h4 className="font-semibold text-xs text-slate-400 uppercase tracking-wider mb-3">Lineage DAG Edges Log</h4>
            <div className="space-y-2 text-xs">
              {lineage?.edges.map((edge, idx) => (
                <div key={idx} className="flex items-center justify-between bg-slate-900/60 p-2.5 rounded border border-slate-800">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-indigo-300 font-bold">{edge.source}</span>
                    <ArrowRight className="h-3.5 w-3.5 text-slate-500" />
                    <span className="font-mono text-emerald-300 font-bold">{edge.target}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-slate-400">{edge.label}</span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-300">
                      {edge.type}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
