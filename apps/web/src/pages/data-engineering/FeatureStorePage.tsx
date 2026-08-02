import React, { useEffect, useState } from 'react';
import {
  CheckCircle2,
  Zap,
} from 'lucide-react';
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';
import { dataEngineeringApi, FeatureGroup } from '@/services/dataEngineeringApi';

export function FeatureStorePage() {
  const [featureGroups, setFeatureGroups] = useState<FeatureGroup[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const data = await dataEngineeringApi.getFeatureGroups();
      setFeatureGroups(data);
      setLoading(false);
    }
    load();
  }, []);

  return (
    <div className="space-y-6">
      <PageHeader
        title="AI Feature Store & Feature Registry"
        subtitle="Manage offline/online feature groups, aggregation windows, feature metadata, and entity keys for ML models"
      />

      {/* Feature Store Info Banner */}
      <Card className="p-5 bg-indigo-900 text-white shadow-lg">
        <div className="flex justify-between items-center">
          <div className="space-y-1">
            <h3 className="text-lg font-bold flex items-center">
              <Zap className="h-5 w-5 mr-2 text-amber-400" />
              Low-Latency Online & Offline Feature Architecture
            </h3>
            <p className="text-xs text-indigo-200">
              Features are pre-computed in batch offline tables and cached in low-latency online key-value stores for instant sub-millisecond AI inference lookup.
            </p>
          </div>
          <div className="flex items-center gap-4 text-right">
            <div>
              <div className="text-2xl font-extrabold">{featureGroups.length}</div>
              <div className="text-[11px] text-indigo-300">Feature Groups</div>
            </div>
          </div>
        </div>
      </Card>

      {/* Feature Groups List */}
      <div className="space-y-6">
        {featureGroups.map((fg) => (
          <Card key={fg.id} className="p-6">
            <div className="flex justify-between items-start border-b border-slate-100 pb-4 mb-4">
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-lg font-bold text-slate-900">{fg.group_name}</h3>
                  <span className="text-xs font-semibold px-2 py-0.5 rounded bg-blue-50 text-blue-700">
                    Entity: {fg.entity_name} ({fg.entity_key})
                  </span>
                </div>
                <p className="text-sm text-slate-500 mt-1">{fg.description}</p>
              </div>

              <div className="flex items-center gap-2">
                <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700">
                  <CheckCircle2 className="h-3 w-3 mr-1" />
                  Online Store Enabled
                </span>
              </div>
            </div>

            {/* Registered Features Table */}
            <div>
              <h4 className="text-xs font-semibold uppercase text-slate-500 tracking-wider mb-3">
                Registered Features ({fg.features?.length || 0})
              </h4>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm text-slate-600">
                  <thead className="bg-slate-50 text-slate-700 uppercase text-xs font-semibold">
                    <tr>
                      <th className="py-2.5 px-4">Feature Name</th>
                      <th className="py-2.5 px-4">Data Type</th>
                      <th className="py-2.5 px-4">Aggregation Window</th>
                      <th className="py-2.5 px-4">ML Feature Type</th>
                      <th className="py-2.5 px-4">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 text-xs">
                    {fg.features?.map((f) => (
                      <tr key={f.id}>
                        <td className="py-2.5 px-4 font-mono font-semibold text-slate-900">{f.feature_name}</td>
                        <td className="py-2.5 px-4 font-mono text-indigo-600">{f.data_type}</td>
                        <td className="py-2.5 px-4">{f.aggregation_window || 'N/A'}</td>
                        <td className="py-2.5 px-4 font-semibold text-slate-700">{f.ml_feature_type}</td>
                        <td className="py-2.5 px-4">
                          <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 text-[10px] font-bold">
                            {f.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
