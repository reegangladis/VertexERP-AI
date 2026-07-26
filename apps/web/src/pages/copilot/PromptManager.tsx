import React, { useState, useEffect } from 'react';
import {
  FileText,
  Plus,
  Play,
  Save,
  Trash2,
  AlertCircle,
  Copy,
  CheckCircle,
} from 'lucide-react';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { Alert } from '@/components/Alert';
import { useNotification } from '@/hooks/useNotification';
import { copilotService, CopilotPrompt } from '@/services/copilotService';
import PageHeader from '@/components/PageHeader';

export function PromptManager() {
  const { addNotification } = useNotification();
  const [prompts, setPrompts] = useState<CopilotPrompt[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingPrompt, setEditingPrompt] = useState<Partial<CopilotPrompt> | null>(null);

  // Prompt Sandbox tester
  const [sandboxTemplate, setSandboxTemplate] = useState('');
  const [sandboxVars, setSandboxVars] = useState('{\n  "user_name": "John Doe",\n  "org_name": "Acme Industrial"\n}');
  const [sandboxResult, setSandboxResult] = useState('');
  const [isTesting, setIsTesting] = useState(false);

  useEffect(() => {
    loadPrompts();
  }, []);

  const loadPrompts = async () => {
    try {
      const data = await copilotService.listPrompts();
      setPrompts(data);
    } catch (err) {
      addNotification('Failed to fetch prompt templates catalog', 'error');
    }
  };

  const handleSavePrompt = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingPrompt) return;

    try {
      if (editingPrompt.id) {
        // Update
        const updated = await copilotService.updatePrompt(editingPrompt.id, editingPrompt);
        setPrompts((prev) => prev.map((p) => (p.id === editingPrompt.id ? updated : p)));
        addNotification('Prompt configuration updated successfully', 'success');
      } else {
        // Create
        const created = await copilotService.createPrompt(editingPrompt);
        setPrompts((prev) => [...prev, created]);
        addNotification('Prompt template created', 'success');
      }
      setIsModalOpen(false);
      setEditingPrompt(null);
    } catch (err: any) {
      addNotification(err.message || 'Error saving prompt', 'error');
    }
  };

  const handleDeletePrompt = async (pid: string) => {
    if (!confirm('Are you sure you want to delete this prompt template? Default system templates cannot be deleted.')) return;
    try {
      await copilotService.deletePrompt(pid);
      setPrompts((prev) => prev.filter((p) => p.id !== pid));
      addNotification('Prompt template deleted', 'success');
    } catch (err) {
      addNotification('Failed to delete prompt template. You might not have permission.', 'error');
    }
  };

  const handleTestRender = async () => {
    setIsTesting(true);
    setSandboxResult('');
    try {
      let parsedVars = {};
      try {
        parsedVars = JSON.parse(sandboxVars);
      } catch {
        throw new Error('Variables must be valid JSON format');
      }
      const rendered = await copilotService.testPrompt(sandboxTemplate, parsedVars);
      setSandboxResult(rendered);
      addNotification('Rendered successfully', 'success');
    } catch (err: any) {
      addNotification(err.message || 'Test render failed', 'error');
    } finally {
      setIsTesting(false);
    }
  };

  const openEditModal = (prompt?: CopilotPrompt) => {
    if (prompt) {
      setEditingPrompt(prompt);
    } else {
      setEditingPrompt({
        name: '',
        type: 'system',
        department: '',
        template: '',
        variables: ['user_name', 'org_name'],
        version: '1.0.0',
        is_active: true,
      });
    }
    setIsModalOpen(true);
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <PageHeader
        title="Prompt Engineering Manager"
        description="Configure instructions boundaries, customize department context templates, and test variables rendering."
        actions={
          <Button size="sm" onClick={() => openEditModal()} className="gap-2">
            <Plus className="h-4 w-4" /> Create Prompt
          </Button>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        {/* Templates list table */}
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-card border border-border rounded-xl shadow-sm overflow-hidden">
            <div className="p-4 border-b border-border bg-card/60">
              <h3 className="text-xs font-bold text-foreground uppercase tracking-wider">Active Prompts Repository</h3>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-border bg-secondary/20 text-muted-foreground/80 font-semibold">
                    <th className="p-3">Prompt Name</th>
                    <th className="p-3">Type</th>
                    <th className="p-3">Department</th>
                    <th className="p-3">Version</th>
                    <th className="p-3">Status</th>
                    <th className="p-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/60">
                  {prompts.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="p-6 text-center text-muted-foreground">
                        No custom prompt templates configured. Default system instructions will be utilized.
                      </td>
                    </tr>
                  ) : (
                    prompts.map((p) => (
                      <tr key={p.id} className="hover:bg-secondary/10">
                        <td className="p-3 font-semibold text-foreground">{p.name}</td>
                        <td className="p-3">
                          <span className="capitalize">{p.type}</span>
                        </td>
                        <td className="p-3">
                          <span className="uppercase text-[9px] bg-secondary px-1.5 py-0.5 rounded font-bold border border-border">
                            {p.department || 'global'}
                          </span>
                        </td>
                        <td className="p-3">{p.version}</td>
                        <td className="p-3">
                          <span className={`text-[9px] px-1.5 py-0.5 rounded-full font-semibold uppercase ${
                            p.is_active ? 'bg-emerald-500/10 text-emerald-500' : 'bg-secondary text-muted-foreground'
                          }`}>
                            {p.is_active ? 'active' : 'disabled'}
                          </span>
                        </td>
                        <td className="p-3 text-right space-x-1.5">
                          <button
                            onClick={() => {
                              setSandboxTemplate(p.template);
                              addNotification(`Template loaded to sandbox: ${p.name}`, 'info');
                            }}
                            className="text-primary hover:underline text-[11px]"
                          >
                            Load Sandbox
                          </button>
                          <button
                            onClick={() => openEditModal(p)}
                            className="text-foreground hover:underline text-[11px]"
                          >
                            Edit
                          </button>
                          {p.organization_id && (
                            <button
                              onClick={() => handleDeletePrompt(p.id)}
                              className="text-destructive hover:underline text-[11px]"
                            >
                              Delete
                            </button>
                          )}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Sandbox Tester */}
        <div className="lg:col-span-1 space-y-4">
          <div className="bg-card border border-border rounded-xl p-4 shadow-sm space-y-4">
            <div className="flex items-center gap-2 border-b border-border pb-3">
              <Play className="h-4.5 w-4.5 text-primary" />
              <h3 className="text-xs font-bold text-foreground uppercase tracking-wider">Prompt Sandbox Sandbox</h3>
            </div>

            <div className="space-y-3 text-xs">
              <div className="space-y-1">
                <label className="font-semibold text-muted-foreground">Template Template</label>
                <textarea
                  className="w-full h-32 bg-secondary/30 border border-border rounded-lg p-2.5 font-mono text-[11px] focus:outline-none focus:ring-1 focus:ring-primary"
                  placeholder="e.g. Hello {{ user_name }}, welcome back to VertexERP!"
                  value={sandboxTemplate}
                  onChange={(e) => setSandboxTemplate(e.target.value)}
                />
              </div>

              <div className="space-y-1">
                <label className="font-semibold text-muted-foreground">Mock Variables (JSON Format)</label>
                <textarea
                  className="w-full h-24 bg-secondary/30 border border-border rounded-lg p-2.5 font-mono text-[11px] focus:outline-none focus:ring-1 focus:ring-primary"
                  value={sandboxVars}
                  onChange={(e) => setSandboxVars(e.target.value)}
                />
              </div>

              <Button
                variant="primary"
                onClick={handleTestRender}
                isLoading={isTesting}
                className="w-full text-xs h-9"
              >
                Test Render
              </Button>

              {sandboxResult && (
                <div className="space-y-1.5 border-t border-border pt-3">
                  <label className="font-semibold text-foreground">Compiled Output Output</label>
                  <div className="p-3 bg-secondary/50 border border-border/80 rounded-lg text-[11px] whitespace-pre-wrap leading-relaxed">
                    {sandboxResult}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Editor Modal */}
      {isModalOpen && editingPrompt && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <form onSubmit={handleSavePrompt} className="bg-card border border-border rounded-xl shadow-lg max-w-xl w-full overflow-hidden">
            <div className="p-4 border-b border-border bg-secondary/10 flex justify-between items-center">
              <h3 className="text-xs font-bold text-foreground uppercase tracking-wider">
                {editingPrompt.id ? 'Modify Template Configuration' : 'Create Custom Prompt Template'}
              </h3>
              <button
                type="button"
                onClick={() => {
                  setIsModalOpen(false);
                  setEditingPrompt(null);
                }}
                className="text-muted-foreground hover:text-foreground text-sm font-semibold"
              >
                Close
              </button>
            </div>
            
            <div className="p-6 space-y-4 text-xs">
              <Input
                label="Prompt Name"
                value={editingPrompt.name || ''}
                onChange={(e) => setEditingPrompt((prev) => ({ ...prev, name: e.target.value }))}
                required
                className="text-xs"
              />

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block mb-1 font-semibold text-muted-foreground">Prompt Type</label>
                  <select
                    className="w-full text-xs bg-background border border-border rounded-lg p-2 text-foreground"
                    value={editingPrompt.type || 'system'}
                    onChange={(e) => setEditingPrompt((prev) => ({ ...prev, type: e.target.value }))}
                  >
                    <option value="system">System Boundary</option>
                    <option value="department">Department-Specific Context</option>
                    <option value="generic">Generic Task Instruction</option>
                  </select>
                </div>
                <div>
                  <label className="block mb-1 font-semibold text-muted-foreground">Department Context</label>
                  <select
                    className="w-full text-xs bg-background border border-border rounded-lg p-2 text-foreground"
                    value={editingPrompt.department || ''}
                    onChange={(e) => setEditingPrompt((prev) => ({ ...prev, department: e.target.value || undefined }))}
                  >
                    <option value="">Global (None)</option>
                    <option value="hr">HR Platform</option>
                    <option value="crm">CRM Leads</option>
                    <option value="finance">Finance Platform</option>
                    <option value="inventory">Inventory Hub</option>
                    <option value="manufacturing">Manufacturing Operations</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="Version"
                  value={editingPrompt.version || '1.0.0'}
                  onChange={(e) => setEditingPrompt((prev) => ({ ...prev, version: e.target.value }))}
                  required
                  className="text-xs"
                />
                <div className="flex items-center gap-2 mt-6">
                  <input
                    type="checkbox"
                    id="is_active"
                    checked={editingPrompt.is_active ?? true}
                    onChange={(e) => setEditingPrompt((prev) => ({ ...prev, is_active: e.target.checked }))}
                    className="rounded border-border text-primary focus:ring-primary"
                  />
                  <label htmlFor="is_active" className="font-semibold text-muted-foreground">
                    Enable Active Status
                  </label>
                </div>
              </div>

              <div className="space-y-1">
                <label className="font-semibold text-muted-foreground">Template Body (supports {"{{ variables }}"})</label>
                <textarea
                  className="w-full h-40 bg-secondary/30 border border-border rounded-lg p-2.5 font-mono text-[11px] focus:outline-none focus:ring-1 focus:ring-primary"
                  value={editingPrompt.template || ''}
                  onChange={(e) => setEditingPrompt((prev) => ({ ...prev, template: e.target.value }))}
                  required
                />
              </div>
            </div>

            <div className="p-4 border-t border-border bg-secondary/10 flex justify-end gap-2.5">
              <Button
                variant="outline"
                type="button"
                onClick={() => {
                  setIsModalOpen(false);
                  setEditingPrompt(null);
                }}
                className="text-xs"
              >
                Cancel
              </Button>
              <Button variant="primary" type="submit" className="text-xs">
                Save Prompt Configuration
              </Button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
export default PromptManager;
