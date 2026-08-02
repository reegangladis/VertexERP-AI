import React, { useState, useEffect } from 'react';
import {
  Shield,
  ChevronRight,
  ChevronDown,
  Info,
} from 'lucide-react';
import { useNotification } from '@/hooks/useNotification';
import { copilotService, ToolRegistry as ToolItem } from '@/services/copilotService';
import PageHeader from '@/components/PageHeader';

export function ToolRegistry() {
  const { addNotification } = useNotification();
  const [tools, setTools] = useState<ToolItem[]>([]);
  const [expandedTool, setExpandedTool] = useState<string | null>(null);

  useEffect(() => {
    loadTools();
  }, []);

  const loadTools = async () => {
    try {
      const data = await copilotService.listTools();
      setTools(data);
    } catch (err) {
      addNotification('Failed to fetch registered tools list', 'error');
    }
  };

  const handleToggleStatus = async (tool: ToolItem) => {
    const nextStatus = !tool.is_active;
    try {
      const updated = await copilotService.updateToolStatus(tool.name, nextStatus);
      setTools((prev) => prev.map((t) => (t.name === tool.name ? updated : t)));
      addNotification(`Tool '${tool.name}' ${nextStatus ? 'enabled' : 'disabled'}`, 'success');
    } catch (err) {
      addNotification('Could not modify tool status', 'error');
    }
  };

  const toggleExpand = (tname: string) => {
    setExpandedTool(expandedTool === tname ? null : tname);
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <PageHeader
        title="Pluggable Tool Registry"
        description="Verify system-registered backend operations, configure RBAC execution contexts, and manage pluggable modules."
      />

      <div className="bg-card border border-border rounded-xl shadow-sm overflow-hidden">
        <div className="p-4 border-b border-border bg-card/60 flex items-center justify-between">
          <h3 className="text-xs font-bold text-foreground uppercase tracking-wider">Registered ERP Interfaces</h3>
          <span className="text-[10px] text-muted-foreground/85 bg-secondary/80 px-2 py-0.5 rounded border border-border">
            Total Modules: {tools.length}
          </span>
        </div>

        <div className="divide-y divide-border/60">
          {tools.length === 0 ? (
            <div className="p-12 text-center text-muted-foreground text-xs">
              No pluggable tools currently registered in the database. Run server sequence to hydrate the registry.
            </div>
          ) : (
            tools.map((tool) => {
              const isExpanded = expandedTool === tool.name;
              return (
                <div key={tool.id} className="p-4 space-y-3 transition-colors hover:bg-secondary/5">
                  <div className="flex items-center justify-between gap-4">
                    <div className="min-w-0 flex-1 space-y-1">
                      <div className="flex items-center gap-2.5">
                        <span
                          onClick={() => toggleExpand(tool.name)}
                          className="font-bold text-xs text-foreground hover:text-primary cursor-pointer flex items-center gap-1.5"
                        >
                          {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                          {tool.name}
                        </span>
                        
                        {tool.required_role && (
                          <span className="inline-flex items-center gap-1 text-[9px] bg-amber-500/10 text-amber-500 border border-amber-500/20 px-1.5 py-0.5 rounded font-medium font-mono uppercase">
                            <Shield className="h-2.5 w-2.5" />
                            {tool.required_role}
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-muted-foreground max-w-2xl">{tool.description}</p>
                    </div>

                    <div className="flex items-center gap-3">
                      <button
                        onClick={() => handleToggleStatus(tool)}
                        className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                          tool.is_active ? 'bg-primary' : 'bg-secondary'
                        }`}
                      >
                        <span
                          className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-background shadow ring-0 transition duration-200 ease-in-out ${
                            tool.is_active ? 'translate-x-4' : 'translate-x-0'
                          }`}
                        />
                      </button>
                    </div>
                  </div>

                  {isExpanded && (
                    <div className="pl-6 pt-2 border-t border-border/20 grid grid-cols-1 md:grid-cols-2 gap-4 text-[10px]">
                      {/* Parameters schema representation */}
                      <div className="space-y-1">
                        <span className="font-semibold text-muted-foreground uppercase tracking-wide flex items-center gap-1">
                          <Info className="h-3.5 w-3.5" /> Parameters Schema Schema
                        </span>
                        <pre className="bg-secondary/40 border border-border/80 rounded-lg p-3 font-mono leading-relaxed text-foreground max-h-48 overflow-y-auto">
                          {JSON.stringify(tool.parameters_schema, null, 2)}
                        </pre>
                      </div>

                      {/* Tool metadata details */}
                      <div className="space-y-2 bg-secondary/20 border border-border/40 rounded-lg p-3 h-fit space-y-2.5">
                        <div className="flex justify-between items-center pb-1.5 border-b border-border/20">
                          <span className="text-muted-foreground">Registration ID</span>
                          <span className="font-mono text-foreground">{tool.id}</span>
                        </div>
                        <div className="flex justify-between items-center pb-1.5 border-b border-border/20">
                          <span className="text-muted-foreground">Registry Sync Timestamp</span>
                          <span className="text-foreground">{new Date(tool.created_at).toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-muted-foreground">Security Mapping context</span>
                          <span className="text-foreground">{tool.required_role ? 'RBAC validation active' : 'Public System Access'}</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
export default ToolRegistry;
