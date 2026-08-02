import React, { useState, useEffect } from 'react';
import { Layout, Plus, X } from 'lucide-react';
import { analyticsService } from '@/services/analyticsService';

export function DashboardBuilderPage() {
  const [dashboards, setDashboards] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [title, setTitle] = useState('');
  const [scope, setScope] = useState('EXECUTIVE');
  const [description, setDescription] = useState('');

  const fetchDashboards = async () => {
    setLoading(true);
    try {
      const data = await analyticsService.getDashboards();
      setDashboards(data || []);
    } catch (err) {
      console.error('Error fetching dashboards', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboards();
  }, []);

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await analyticsService.createDashboard({
        title,
        scope,
        description,
        is_default: false,
        is_public: true,
      });
      setShowCreateModal(false);
      setTitle('');
      setDescription('');
      fetchDashboards();
    } catch (err) {
      console.error('Error creating dashboard', err);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Layout className="h-6 w-6 text-primary" />
            Custom Dashboard & Visual Widget Builder
          </h1>
          <p className="text-xs text-muted-foreground mt-1">
            Build Tailored Analytics Dashboards, Configure Chart Grid Positions & Data Sources
          </p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 text-xs font-semibold bg-primary text-primary-foreground rounded-xl shadow hover:bg-primary/90 transition"
        >
          <Plus className="h-4 w-4" />
          Create New Dashboard
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {dashboards.map((dash) => (
          <div key={dash.id} className="p-5 border border-border rounded-xl bg-card space-y-3 shadow-sm hover:border-primary/50 transition">
            <div className="flex items-start justify-between">
              <div>
                <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-primary/10 text-primary font-bold">
                  {dash.scope}
                </span>
                <h3 className="text-base font-bold text-foreground mt-1">{dash.title}</h3>
              </div>
            </div>
            <p className="text-xs text-muted-foreground line-clamp-2">{dash.description || 'Custom configured analytics dashboard workspace.'}</p>
            <div className="flex justify-between items-center text-[11px] text-muted-foreground border-t border-border/60 pt-3">
              <span>Widgets: <strong className="text-foreground">{dash.widgets?.length || 0}</strong></span>
              <span>{dash.is_public ? 'Public' : 'Private'}</span>
            </div>
          </div>
        ))}

        {dashboards.length === 0 && !loading && (
          <div className="col-span-full text-center py-16 text-muted-foreground text-xs">
            No custom analytics dashboards created yet.
          </div>
        )}
      </div>

      {/* CREATE DASHBOARD MODAL */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-card border border-border rounded-xl max-w-md w-full p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <h3 className="text-lg font-bold text-foreground">Create Custom Dashboard</h3>
              <button onClick={() => setShowCreateModal(false)} className="text-muted-foreground hover:text-foreground">
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleCreateSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block font-medium text-foreground mb-1">Dashboard Title</label>
                <input
                  type="text"
                  required
                  placeholder="Regional Sales Cockpit"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-medium text-foreground mb-1">Scope</label>
                <select
                  value={scope}
                  onChange={(e) => setScope(e.target.value)}
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none"
                >
                  <option value="EXECUTIVE">EXECUTIVE</option>
                  <option value="DEPARTMENT">DEPARTMENT</option>
                  <option value="BRANCH">BRANCH</option>
                  <option value="CUSTOM">CUSTOM</option>
                </select>
              </div>

              <div>
                <label className="block font-medium text-foreground mb-1">Description</label>
                <textarea
                  rows={3}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Overview of sales KPIs across western territories..."
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none"
                />
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-border">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 border border-border rounded-lg hover:bg-muted"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary text-primary-foreground rounded-lg font-semibold shadow hover:bg-primary/90"
                >
                  Save Dashboard
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
