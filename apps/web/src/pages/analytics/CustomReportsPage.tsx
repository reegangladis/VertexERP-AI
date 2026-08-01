import React, { useState, useEffect } from 'react';
import { FileText, Download, Play, Filter, Plus, CheckCircle2, X } from 'lucide-react';
import { analyticsService, ReportExecuteResponse } from '@/services/analyticsService';

export function CustomReportsPage() {
  const [domain, setDomain] = useState('FINANCE');
  const [reports, setReports] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [executedReport, setExecutedReport] = useState<ReportExecuteResponse | null>(null);

  // Export Modal
  const [showExportModal, setShowExportModal] = useState(false);
  const [exportFormat, setExportFormat] = useState('CSV');
  const [exporting, setExporting] = useState(false);

  const fetchReports = async () => {
    try {
      const data = await analyticsService.getReports(domain);
      setReports(data || []);
    } catch (err) {
      console.error('Error fetching reports', err);
    }
  };

  useEffect(() => {
    fetchReports();
  }, [domain]);

  const handleExecute = async () => {
    setLoading(true);
    try {
      const res = await analyticsService.executeReport({
        domain,
        columns: ['id', 'code', 'name', 'category', 'amount', 'status', 'date'],
        page: 1,
        page_size: 10,
      });
      setExecutedReport(res);
    } catch (err) {
      console.error('Error executing report', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    if (!executedReport) return;
    setExporting(true);
    try {
      const res = await analyticsService.exportReport({
        report_name: executedReport.report_title,
        export_format: exportFormat,
        dataset: executedReport.data,
        columns: executedReport.columns,
      });
      
      // Trigger download
      const element = document.createElement('a');
      element.setAttribute('href', `data:text/plain;base64,${res.content_base64}`);
      element.setAttribute('download', res.filename);
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);

      setShowExportModal(false);
    } catch (err) {
      console.error('Error exporting report data', err);
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <FileText className="h-6 w-6 text-primary" />
            Enterprise Custom Reports & Query Engine
          </h1>
          <p className="text-xs text-muted-foreground mt-1">
            Dynamic Dataset Querying, Column Customization & Multi-Format Data Exporting (CSV, Excel, PDF)
          </p>
        </div>

        <div className="flex items-center gap-2">
          <select
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
            className="text-xs bg-card border border-border px-3 py-2 rounded-xl font-semibold focus:outline-none"
          >
            <option value="FINANCE">Finance Domain</option>
            <option value="CRM">CRM & Sales</option>
            <option value="HR">HR & Workforce</option>
            <option value="INVENTORY">Inventory & Supply</option>
            <option value="MANUFACTURING">Manufacturing</option>
          </select>

          <button
            onClick={handleExecute}
            className="flex items-center gap-2 px-4 py-2 text-xs font-semibold bg-primary text-primary-foreground rounded-xl shadow hover:bg-primary/90 transition"
          >
            <Play className="h-4 w-4" />
            Run Report Query
          </button>
        </div>
      </div>

      {/* Executed Report Output */}
      {executedReport && (
        <div className="bg-card border border-border rounded-xl p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-border pb-3">
            <div>
              <h2 className="text-lg font-bold text-foreground">{executedReport.report_title}</h2>
              <p className="text-xs text-muted-foreground">
                Domain: {executedReport.domain} | Total Records: {executedReport.total_records}
              </p>
            </div>
            <button
              onClick={() => setShowExportModal(true)}
              className="flex items-center gap-2 px-3 py-1.5 text-xs font-semibold bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition"
            >
              <Download className="h-4 w-4" />
              Export Dataset
            </button>
          </div>

          <div className="border border-border rounded-lg overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-muted/50 border-b border-border text-muted-foreground font-medium uppercase text-[10px]">
                <tr>
                  {executedReport.columns.map((c, i) => (
                    <th key={i} className="px-4 py-3">{c}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border/60 text-foreground font-mono">
                {executedReport.data.map((row, idx) => (
                  <tr key={idx} className="hover:bg-muted/30">
                    {executedReport.columns.map((c, i) => (
                      <td key={i} className="px-4 py-3 font-sans">{String(row[c] || '')}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {!executedReport && (
        <div className="bg-card border border-border rounded-xl p-16 text-center text-xs text-muted-foreground">
          Select a domain and click "Run Report Query" to generate live dynamic report data.
        </div>
      )}

      {/* EXPORT MODAL */}
      {showExportModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-card border border-border rounded-xl max-w-md w-full p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
                <Download className="h-5 w-5 text-emerald-500" />
                Export Analytics Dataset
              </h3>
              <button onClick={() => setShowExportModal(false)} className="text-muted-foreground hover:text-foreground">
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block font-medium text-foreground mb-1">Select Export Format</label>
                <select
                  value={exportFormat}
                  onChange={(e) => setExportFormat(e.target.value)}
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none"
                >
                  <option value="CSV">Comma Separated Values (.CSV)</option>
                  <option value="JSON">Structured Data (.JSON / Excel Data)</option>
                  <option value="PDF">PDF Preview Print Stream</option>
                </select>
              </div>

              <div className="p-3 bg-muted/40 rounded-lg text-muted-foreground">
                Dataset contains {executedReport?.total_records} records across {executedReport?.columns.length} columns.
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-3 border-t border-border text-xs">
              <button
                onClick={() => setShowExportModal(false)}
                className="px-4 py-2 border border-border rounded-lg hover:bg-muted"
              >
                Cancel
              </button>
              <button
                onClick={handleExport}
                disabled={exporting}
                className="px-4 py-2 bg-emerald-600 text-white rounded-lg font-semibold shadow hover:bg-emerald-700 flex items-center gap-2"
              >
                <Download className="h-4 w-4" />
                {exporting ? 'Generating...' : 'Download File'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
