import React, { useState } from 'react';
import {
  LayoutDashboard,
  Plus,
  BarChart3,
  LineChart,
  PieChart as PieIcon,
  Table as TableIcon,
  Sliders,
  CheckCircle2,
  Sparkles,
} from 'lucide-react';
import { analyticsService } from '@/services/analyticsService';

export function DashboardBuilderPage() {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [scope, setScope] = useState('EXECUTIVE');
  const [widgetTitle, setWidgetTitle] = useState('');
  const [widgetType, setWidgetType] = useState('BAR');
  const [dataSource, setDataSource] = useState('FINANCE');
  const [widgets, setWidgets] = useState<any[]>([]);
  const [savedSuccess, setSavedSuccess] = useState(false);

  const handleAddWidget = () => {
    if (!widgetTitle) return;
    const newWidget = {
      title: widgetTitle,
      widget_type: widgetType,
      data_source: dataSource,
      refresh_interval_seconds: 300,
      grid_position: { x: 0, y: widgets.length * 4, w: 6, h: 4 },
    };
    setWidgets([...widgets, newWidget]);
    setWidgetTitle('');
  };

  const handleSaveDashboard = async () => {
    if (!title) return;
    try {
      await analyticsService.createDashboard({
        title,
        description,
        scope,
        is_default: false,
        is_public: true,
        ai_forecast_enabled: true,
        widgets,
      });
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
      setTitle('');
      setDescription('');
      setWidgets([]);
    } catch (err) {
      console.error('Failed to create dashboard:', err);
    }
  };

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100">Custom BI Dashboard Builder</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Design drag-and-drop enterprise analytics dashboards comparable to Power BI, Tableau, and Looker.
          </p>
        </div>
        <button
          onClick={handleSaveDashboard}
          disabled={!title || widgets.length === 0}
          className="flex items-center gap-1.5 rounded-lg bg-blue-600 px-4 py-2 text-xs font-semibold text-white shadow-sm hover:bg-blue-700 disabled:opacity-50"
        >
          <Sparkles className="h-4 w-4" /> Save BI Dashboard
        </button>
      </div>

      {savedSuccess && (
        <div className="flex items-center gap-2 rounded-lg bg-emerald-50 p-4 text-xs font-semibold text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
          <CheckCircle2 className="h-4 w-4" /> Custom Dashboard created successfully!
        </div>
      )}

      {/* Builder Configuration Canvas */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Left Form: Dashboard & Widget Settings */}
        <div className="space-y-6 rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 border-b border-slate-100 pb-3 dark:border-slate-800">
            1. Dashboard Settings
          </h3>

          <div className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300">Dashboard Title</label>
              <input
                type="text"
                placeholder="e.g. Executive Board Summary Q3"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs text-slate-800 focus:outline-none dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300">Description</label>
              <textarea
                rows={2}
                placeholder="Enter dashboard scope and purpose..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs text-slate-800 focus:outline-none dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300">Scope Level</label>
              <select
                value={scope}
                onChange={(e) => setScope(e.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs text-slate-800 focus:outline-none dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200"
              >
                <option value="EXECUTIVE">Executive Scope</option>
                <option value="DEPARTMENT">Departmental Scope</option>
                <option value="BRANCH">Branch Scope</option>
                <option value="GLOBAL">Global Enterprise Scope</option>
              </select>
            </div>
          </div>

          <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 border-b border-slate-100 pb-3 pt-4 dark:border-slate-800">
            2. Add Visual Widget
          </h3>

          <div className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300">Widget Title</label>
              <input
                type="text"
                placeholder="e.g. Monthly Revenue Trajectory"
                value={widgetTitle}
                onChange={(e) => setWidgetTitle(e.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs text-slate-800 focus:outline-none dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300">Visualization Type</label>
              <select
                value={widgetType}
                onChange={(e) => setWidgetType(e.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs text-slate-800 focus:outline-none dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200"
              >
                <option value="BAR">Bar Chart</option>
                <option value="LINE">Line Chart</option>
                <option value="PIE">Pie Chart</option>
                <option value="AREA">Area Chart</option>
                <option value="KPI_CARD">KPI Card</option>
                <option value="TABLE">Data Table</option>
                <option value="HEATMAP">Heatmap Placeholder</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300">Data Source</label>
              <select
                value={dataSource}
                onChange={(e) => setDataSource(e.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs text-slate-800 focus:outline-none dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200"
              >
                <option value="FINANCE">Finance & Accounting</option>
                <option value="HR">HR & Workforce</option>
                <option value="CRM">CRM & Sales</option>
                <option value="INVENTORY">Inventory & Warehouse</option>
                <option value="MANUFACTURING">Manufacturing & Operations</option>
              </select>
            </div>

            <button
              type="button"
              onClick={handleAddWidget}
              disabled={!widgetTitle}
              className="flex w-full items-center justify-center gap-1.5 rounded-lg border border-blue-600 bg-blue-50 py-2 text-xs font-semibold text-blue-700 hover:bg-blue-100 disabled:opacity-50 dark:bg-blue-950/40 dark:text-blue-300"
            >
              <Plus className="h-4 w-4" /> Add Widget to Canvas
            </button>
          </div>
        </div>

        {/* Right Canvas: Live Layout Preview */}
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900 lg:col-span-2">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3 dark:border-slate-800">
            <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">Live Dashboard Grid Preview</h3>
            <span className="text-xs text-slate-500 dark:text-slate-400">{widgets.length} Widgets Placed</span>
          </div>

          {widgets.length === 0 ? (
            <div className="flex h-72 flex-col items-center justify-center text-slate-400">
              <LayoutDashboard className="h-10 w-10 mb-2 opacity-50" />
              <p className="text-sm font-medium">Your canvas is empty.</p>
              <p className="text-xs">Add visual widgets from the left configuration panel.</p>
            </div>
          ) : (
            <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
              {widgets.map((w, idx) => (
                <div key={idx} className="rounded-lg border border-slate-200 p-4 dark:border-slate-800 dark:bg-slate-900/50">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-800 dark:text-slate-200">{w.title}</span>
                    <span className="rounded bg-blue-50 px-2 py-0.5 text-[10px] font-bold text-blue-600 dark:bg-blue-950/50 dark:text-blue-400">
                      {w.widget_type}
                    </span>
                  </div>
                  <div className="mt-2 text-[11px] text-slate-500 dark:text-slate-400">Source: {w.data_source}</div>
                  <div className="mt-4 flex h-24 items-center justify-center rounded border border-dashed border-slate-200 bg-slate-50 text-xs font-medium text-slate-400 dark:border-slate-800 dark:bg-slate-800/40">
                    [{w.widget_type} Visualization Placeholder]
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
