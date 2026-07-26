import React, { useState, useEffect } from 'react';
import {
  FileText,
  Filter,
  Download,
  Play,
  Save,
  Printer,
  Calendar,
  Layers,
  Search,
  RefreshCw,
  CheckCircle2,
} from 'lucide-react';
import { analyticsService, ReportExecuteResponse } from '@/services/analyticsService';

export function CustomReportsPage() {
  const [domain, setDomain] = useState('FINANCE');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<ReportExecuteResponse | null>(null);
  const [saveTitle, setSaveTitle] = useState('');
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    runReport();
  }, [domain]);

  const runReport = async () => {
    setLoading(true);
    try {
      const res = await analyticsService.executeReport({
        domain,
        page: 1,
        page_size: 50,
      });
      setData(res);
    } catch (err) {
      console.error('Failed to execute report:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (fmt: 'CSV' | 'JSON' | 'PDF') => {
    if (!data) return;
    try {
      const exp = await analyticsService.exportReport({
        report_name: data.report_title,
        export_format: fmt,
        dataset: data.data,
        columns: data.columns,
      });

      // Trigger download
      const element = document.createElement('a');
      const file = new Blob([atob(exp.content_base64)], { type: 'text/plain' });
      element.href = URL.createObjectURL(file);
      element.download = exp.filename;
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
    } catch (err) {
      console.error('Export failed:', err);
    }
  };

  const handleSaveReport = async () => {
    if (!saveTitle) return;
    try {
      await analyticsService.createReport({
        name: saveTitle,
        report_category: domain,
        description: `Custom saved snapshot for ${domain}`,
      });
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
      setSaveTitle('');
    } catch (err) {
      console.error('Save failed:', err);
    }
  };

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100">Enterprise Custom Report Builder</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Build, execute, filter, and export cross-departmental tabular reports with real-time aggregation.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleExport('CSV')}
            className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800"
          >
            <Download className="h-3.5 w-3.5" /> Export CSV
          </button>
          <button
            onClick={() => handleExport('JSON')}
            className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800"
          >
            <FileText className="h-3.5 w-3.5" /> Export JSON
          </button>
          <button
            onClick={() => alert('Print preview placeholder rendered successfully.')}
            className="flex items-center gap-1.5 rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-blue-700 shadow-sm"
          >
            <Printer className="h-3.5 w-3.5" /> Print Preview
          </button>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">Domain:</span>
              <select
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-800 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200"
              >
                <option value="FINANCE">Finance & Accounting</option>
                <option value="HR">HR & Workforce</option>
                <option value="CRM">CRM & Sales</option>
                <option value="INVENTORY">Inventory & Warehouse</option>
                <option value="MANUFACTURING">Manufacturing & Plant</option>
              </select>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">Branch:</span>
              <select className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-800 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200">
                <option value="ALL">All Enterprise Branches</option>
                <option value="HQ">Headquarters (NYC)</option>
                <option value="WEST">West Coast Operation</option>
              </select>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <input
              type="text"
              placeholder="Saved Report Title..."
              value={saveTitle}
              onChange={(e) => setSaveTitle(e.target.value)}
              className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-800 placeholder-slate-400 focus:outline-none dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200"
            />
            <button
              onClick={handleSaveReport}
              disabled={!saveTitle}
              className="flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-50 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300"
            >
              <Save className="h-3.5 w-3.5" /> Save Preset
            </button>
            {savedSuccess && (
              <span className="flex items-center gap-1 text-xs font-medium text-emerald-600 dark:text-emerald-400">
                <CheckCircle2 className="h-3.5 w-3.5" /> Saved!
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Dataset Results Table */}
      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3 dark:border-slate-800">
          <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">{data?.report_title || 'Report Output'}</h3>
          <span className="text-xs text-slate-500 dark:text-slate-400">Total Records: {data?.total_records || 0}</span>
        </div>

        {loading ? (
          <div className="flex h-48 items-center justify-center">
            <RefreshCw className="h-6 w-6 animate-spin text-blue-600 dark:text-blue-400" />
          </div>
        ) : (
          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-slate-200 font-semibold text-slate-600 dark:border-slate-800 dark:text-slate-400 uppercase tracking-wider">
                <tr>
                  {data?.columns.map((col) => (
                    <th key={col} className="py-2.5 px-3">{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {data?.data.map((row, idx) => (
                  <tr key={idx} className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                    {data.columns.map((col) => (
                      <td key={col} className="py-3 px-3 text-slate-800 dark:text-slate-200 font-medium">
                        {row[col] !== undefined ? String(row[col]) : '-'}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
