import React, { useState, useEffect } from 'react';
import {
  Building,
  GitMerge,
  Users,
  Award,
  DollarSign,
  Network,
  MapPin,
  Plus,
  RefreshCw,
  FolderTree,
  ChevronRight,
  ChevronDown,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { apiClient } from '@/services/apiClient';

// ─────────────────────────────────────────
// 1. Departments & Department Tree
// ─────────────────────────────────────────

interface DeptNode {
  id: string;
  name: string;
  code: string | null;
  description: string | null;
  children: DeptNode[];
}

function DeptTreeItem({ node }: { node: DeptNode }) {
  const [isOpen, setIsOpen] = useState(true);
  const hasChildren = node.children && node.children.length > 0;

  return (
    <div className="ml-4 my-1">
      <div className="flex items-center gap-2 p-2 rounded hover:bg-secondary/40 border border-border/50 bg-card">
        {hasChildren ? (
          <button onClick={() => setIsOpen(!isOpen)} className="p-1 text-muted-foreground hover:text-foreground">
            {isOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
          </button>
        ) : (
          <div className="w-4" />
        )}
        <FolderTree className="h-4 w-4 text-primary" />
        <span className="font-semibold text-sm">{node.name}</span>
        {node.code && (
          <span className="text-xs font-mono px-2 py-0.5 rounded bg-primary/10 text-primary border border-primary/20">
            {node.code}
          </span>
        )}
      </div>
      {hasChildren && isOpen && (
        <div className="pl-4 border-l-2 border-primary/20 space-y-1">
          {node.children.map((child) => (
            <DeptTreeItem key={child.id} node={child} />
          ))}
        </div>
      )}
    </div>
  );
}

export function DepartmentsPage() {
  const [departments, setDepartments] = useState<any[]>([]);
  const [tree, setTree] = useState<DeptNode[]>([]);
  const [loading, setLoading] = useState(false);

  const loadDepts = async () => {
    setLoading(true);
    try {
      const [listRes, treeRes] = await Promise.all([
        apiClient.get('/api/v1/departments').catch(() => ({ data: [] })),
        apiClient.get('/api/v1/departments/tree').catch(() => ({ data: [] })),
      ]);
      setDepartments(listRes.data || []);
      setTree(treeRes.data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDepts();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Departments & Hierarchy</h1>
          <p className="text-sm text-muted-foreground">Manage nested corporate department structures.</p>
        </div>
        <Button onClick={loadDepts} disabled={loading} variant="secondary" className="flex items-center gap-2">
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <FolderTree className="h-4 w-4 text-primary" />
              Department Hierarchy Tree
            </CardTitle>
            <CardDescription font-mono>Interactive tree visualization</CardDescription>
          </CardHeader>
          <CardContent>
            {tree.length === 0 ? (
              <p className="text-sm text-muted-foreground py-4">No department hierarchy created yet.</p>
            ) : (
              <div className="-ml-4">
                {tree.map((node) => (
                  <DeptTreeItem key={node.id} node={node} />
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">All Departments ({departments.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {departments.map((d: any) => (
                <div key={d.id} className="p-3 rounded border border-border flex justify-between items-center text-xs">
                  <div>
                    <p className="font-semibold text-sm">{d.name}</p>
                    <p className="text-muted-foreground">{d.description || 'No description'}</p>
                  </div>
                  <span className="font-mono px-2 py-1 bg-secondary text-foreground rounded">{d.code || 'N/A'}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────
// 2. Business Units Page
// ─────────────────────────────────────────

export function BusinessUnitsPage() {
  const [items, setItems] = useState<any[]>([]);

  useEffect(() => {
    apiClient.get('/api/v1/business-units').then((res) => setItems(res.data || [])).catch(console.error);
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Business Units</h1>
        <p className="text-sm text-muted-foreground">Strategic corporate divisions and business units.</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {items.map((bu: any) => (
          <Card key={bu.id}>
            <CardHeader className="pb-2">
              <div className="flex justify-between items-center">
                <CardTitle className="text-base">{bu.name}</CardTitle>
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-primary/10 text-primary">{bu.code}</span>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-muted-foreground">{bu.description || 'No description provided.'}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────
// 3. Teams Page
// ─────────────────────────────────────────

export function TeamsPage() {
  const [teams, setTeams] = useState<any[]>([]);

  useEffect(() => {
    apiClient.get('/api/v1/teams').then((res) => setTeams(res.data || [])).catch(console.error);
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Teams & Members</h1>
        <p className="text-sm text-muted-foreground">Functional project and operational teams.</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {teams.map((team: any) => (
          <Card key={team.id}>
            <CardHeader className="pb-2">
              <div className="flex justify-between items-center">
                <CardTitle className="text-base">{team.name}</CardTitle>
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-primary/10 text-primary">{team.code}</span>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-muted-foreground mb-3">{team.description || 'Operational team.'}</p>
              <div className="text-xs font-mono text-muted-foreground">
                Members: {team.members?.length || 0} user(s)
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────
// 4. Designations Page
// ─────────────────────────────────────────

export function DesignationsPage() {
  const [items, setItems] = useState<any[]>([]);

  useEffect(() => {
    apiClient.get('/api/v1/designations').then((res) => setItems(res.data || [])).catch(console.error);
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Job Designations</h1>
        <p className="text-sm text-muted-foreground">Job titles, grades, and reporting levels.</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {items.map((d: any) => (
          <Card key={d.id}>
            <CardHeader className="pb-2">
              <CardTitle className="text-base">{d.name}</CardTitle>
              <CardDescription className="text-xs">{d.title || d.name}</CardDescription>
            </CardHeader>
            <CardContent className="text-xs space-y-1 font-mono">
              <p>Code: <span className="text-primary">{d.code || 'N/A'}</span></p>
              <p>Level: {d.job_level || 'N/A'} | Grade: {d.grade || 'N/A'}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────
// 5. Cost Centers Page
// ─────────────────────────────────────────

export function CostCentersPage() {
  const [items, setItems] = useState<any[]>([]);

  useEffect(() => {
    apiClient.get('/api/v1/cost-centers').then((res) => setItems(res.data || [])).catch(console.error);
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Cost Centers</h1>
        <p className="text-sm text-muted-foreground">Financial accounting and cost center allocation units.</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {items.map((cc: any) => (
          <Card key={cc.id}>
            <CardHeader className="pb-2">
              <div className="flex justify-between items-center">
                <CardTitle className="text-base">{cc.name}</CardTitle>
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-500">{cc.code}</span>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-muted-foreground">{cc.description || 'Cost allocation center.'}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────
// 6. Reporting Structure & Org Chart Page
// ─────────────────────────────────────────

export function OrgChartPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Organization Chart</h1>
        <p className="text-sm text-muted-foreground">Interactive reporting structure and executive hierarchy chart.</p>
      </div>
      <Card className="p-8 flex flex-col items-center justify-center text-center space-y-4">
        <Network className="h-16 w-16 text-primary animate-pulse" />
        <h2 className="text-lg font-bold">Interactive Org Chart Engine</h2>
        <p className="text-xs text-muted-foreground max-w-md">
          Phase 3 Enterprise Reporting Structure platform active. Connect employee records to view live interactive manager-reporting node graphs.
        </p>
      </Card>
    </div>
  );
}

// ─────────────────────────────────────────
// 7. Office Locations Page
// ─────────────────────────────────────────

export function OfficeLocationsPage() {
  const [items, setItems] = useState<any[]>([]);

  useEffect(() => {
    apiClient.get('/api/v1/office-locations').then((res) => setItems(res.data || [])).catch(console.error);
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Office Locations</h1>
        <p className="text-sm text-muted-foreground">Physical office buildings, floors, and workplace capacities.</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {items.map((loc: any) => (
          <Card key={loc.id}>
            <CardHeader className="pb-2">
              <CardTitle className="text-base flex items-center gap-2">
                <MapPin className="h-4 w-4 text-primary" />
                {loc.name}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-xs space-y-1 font-mono text-muted-foreground">
              <p>Building: {loc.building || 'Main Tower'}</p>
              <p>Floor: {loc.floor || 'N/A'} | Capacity: {loc.capacity || 'Unlimited'}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
