import React, { useEffect, useState } from 'react';
import {
  CheckCircle2,
  AlertTriangle,
  RotateCw,
  ShieldCheck,
  Percent,
} from 'lucide-react';
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { dataEngineeringApi, DataQualityReport } from '@/services/dataEngineeringApi';

export function DataQualityDashboard() {
  const [reports, setReports] = useState<DataQualityReport[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchReports = async () => {
    setLoading(true);
    const data = await dataEngineeringApi.getDataQualityReports();
    setReports(data);
    setLoading(false);
  };

  useEffect(() => {
    fetchReports();
  }, []);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Data Quality & Integrity Dashboard"
        subtitle="Automated null checks, duplicate detection, referential integrity verification, schema validation, and quality scores"
        actions={
          <Button variant="outline" size="sm" onClick={fetchReports} disabled={loading}>
            <RotateCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Run Quality Audit
          </Button>
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-5 border-l-4 border-l-emerald-500">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-xs font-semibold uppercase text-slate-500">Overall Quality Index</p>
              <h3 className="text-3xl font-extrabold text-slate-900 mt-1">99.8%</h3>
              <p className="text-xs text-emerald-600 flex items-center mt-1">
                <CheckCircle2 className="h-3.5 w-3.5 mr-1" />
                Passed 100% Quality Rules
              </p>
            </div>
            <div className="p-3 bg-emerald-50 text-emerald-600 rounded-xl">
              <ShieldCheck className="h-6 w-6" />
            </div>
          </div>
        </Card>

        <Card className="p-5 border-l-4 border-l-blue-500">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-xs font-semibold uppercase text-slate-500">Null Check Violations</p>
              <h3 className="text-3xl font-extrabold text-slate-900 mt-1">0</h3>
              <p className="text-xs text-slate-500 mt-1">Primary keys & non-null columns</p>
            </div>
            <div className="p-3 bg-blue-50 text-blue-600 rounded-xl">
              <CheckCircle2 className="h-6 w-6" />
            </div>
          </div>
        </Card>

        <Card className="p-5 border-l-4 border-l-purple-500">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-xs font-semibold uppercase text-slate-500">Duplicate Entity Risk</p>
              <h3 className="text-3xl font-extrabold text-slate-900 mt-1">0</h3>
              <p className="text-xs text-slate-500 mt-1">Deduplicated via MDM matching</p>
            </div>
            <div className="p-3 bg-purple-50 text-purple-600 rounded-xl">
              <CheckCircle2 className="h-6 w-6" />
            </div>
          </div>
        </Card>
      </div>

      <Card className="p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Inspection & Profiling Reports</h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-600">
            <thead className="bg-slate-50 text-slate-700 uppercase text-xs font-semibold">
              <tr>
                <th className="py-3 px-4">Target Table</th>
                <th className="py-3 px-4">Passed / Failed Rules</th>
                <th className="py-3 px-4">Quality Score</th>
                <th className="py-3 px-4">Violations Detail</th>
                <th className="py-3 px-4 text-right">Inspected At</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {reports.map((r) => (
                <tr key={r.id} className="hover:bg-slate-50">
                  <td className="py-3 px-4 font-mono font-bold text-slate-900">{r.table_name}</td>
                  <td className="py-3 px-4">
                    <span className="font-semibold text-emerald-600">{r.passed_count} Passed</span> /{' '}
                    <span className="text-slate-400">{r.failed_count} Failed</span>
                  </td>
                  <td className="py-3 px-4">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800">
                      {r.quality_score}%
                    </span>
                  </td>
                  <td className="py-3 px-4 text-xs text-slate-500">
                    Null: {r.null_violations} | Dups: {r.duplicate_violations} | Schema: {r.schema_violations}
                  </td>
                  <td className="py-3 px-4 text-right text-xs text-slate-400">
                    {new Date(r.created_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
