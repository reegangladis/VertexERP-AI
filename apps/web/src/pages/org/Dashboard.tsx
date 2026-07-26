import { useState, useEffect } from 'react';
import {
  Building2,
  GitBranch,
  Network,
  Users2,
  MapPin,
  Award,
  Play,
  RefreshCw,
  Info
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { useNotification } from '@/hooks/useNotification';
import { apiClient } from '@/services/apiClient';

export function OrgDashboard() {
  const { addNotification } = useNotification();
  const [stats, setStats] = useState({
    organizations: 1,
    branches: 0,
    departments: 0,
    teams: 0,
    locations: 0,
    designations: 0,
  });
  const [loading, setLoading] = useState(false);

  const fetchStats = async () => {
    try {
      const [branchesRes, deptsRes, teamsRes, locsRes, desigRes] = await Promise.all([
        apiClient.get('/api/v1/branches'),
        apiClient.get('/api/v1/departments'),
        apiClient.get('/api/v1/teams'),
        apiClient.get('/api/v1/locations'),
        apiClient.get('/api/v1/designations')
      ]);

      setStats({
        organizations: 1,
        branches: branchesRes.data.data?.length || 0,
        departments: deptsRes.data.data?.length || 0,
        teams: teamsRes.data.data?.length || 0,
        locations: locsRes.data.data?.length || 0,
        designations: desigRes.data.data?.length || 0,
      });
    } catch (err) {
      console.error("Failed to load dashboard metrics", err);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const handleSeedData = async () => {
    setLoading(true);
    try {
      await apiClient.post('/api/v1/organizations/seed-enterprise-data');
      addNotification('Enterprise organization structure successfully seeded!', 'success');
      await fetchStats();
    } catch (err: any) {
      addNotification(err.message || 'Failed to seed data', 'error');
    } finally {
      setLoading(false);
    }
  };

  const chartData = [
    { name: 'Jan', headcount: stats.branches * 5 + 10, departments: stats.departments },
    { name: 'Feb', headcount: stats.branches * 5 + 15, departments: stats.departments },
    { name: 'Mar', headcount: stats.branches * 6 + 18, departments: stats.departments },
    { name: 'Apr', headcount: stats.branches * 8 + 25, departments: stats.departments },
    { name: 'May', headcount: stats.branches * 10 + 35, departments: stats.departments },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Organization Console</h1>
          <p className="text-sm text-muted-foreground">
            Configure internal corporate registers, reporting structures, and branches.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button onClick={fetchStats} variant="secondary" className="flex items-center gap-2">
            <RefreshCw className="h-4 w-4" />
            Reload Metrics
          </Button>
          <Button onClick={handleSeedData} disabled={loading} variant="primary" className="flex items-center gap-2">
            <Play className="h-4 w-4" />
            {loading ? 'Seeding...' : 'Seed Enterprise Structure'}
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
        {[
          { label: 'Organizations', val: stats.organizations, icon: <Building2 className="h-4 w-4" /> },
          { label: 'Branches', val: stats.branches, icon: <GitBranch className="h-4 w-4" /> },
          { label: 'Departments', val: stats.departments, icon: <Network className="h-4 w-4" /> },
          { label: 'Teams', val: stats.teams, icon: <Users2 className="h-4 w-4" /> },
          { label: 'Locations', val: stats.locations, icon: <MapPin className="h-4 w-4" /> },
          { label: 'Designations', val: stats.designations, icon: <Award className="h-4 w-4" /> },
        ].map((item, idx) => (
          <div key={idx} className="border border-border p-4 rounded bg-card flex flex-col justify-between h-24">
            <div className="flex justify-between items-center text-muted-foreground">
              <span className="text-[10px] uppercase font-mono tracking-wider font-semibold">{item.label}</span>
              {item.icon}
            </div>
            <h3 className="text-2xl font-bold font-mono tracking-tight">{item.val}</h3>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Staff Count Telemetry</CardTitle>
            <CardDescription>Headcount and department scaling over time</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[240px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="headcountGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.2} />
                      <stop offset="95%" stopColor="var(--primary)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" />
                  <XAxis dataKey="name" stroke="var(--muted)" fontSize={11} tickLine={false} />
                  <YAxis stroke="var(--muted)" fontSize={11} tickLine={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'var(--card)',
                      borderColor: 'var(--border)',
                      color: 'var(--foreground)',
                      fontSize: 12,
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="headcount"
                    stroke="var(--foreground)"
                    fillOpacity={1}
                    fill="url(#headcountGrad)"
                    strokeWidth={1.5}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>System Information</CardTitle>
            <CardDescription>Status and configurations</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-2 p-3 bg-secondary/30 rounded border border-border">
              <Info className="h-5 w-5 text-primary shrink-0" />
              <p className="text-xs text-muted-foreground">
                Seeding injecting a pre-built executive and engineering tree including CEO, VPs, and software engineering teams.
              </p>
            </div>
            <div className="text-xs space-y-2">
              <div className="flex justify-between border-b border-border pb-1">
                <span className="text-muted-foreground">Database Engine</span>
                <span className="font-semibold font-mono text-[10px]">PostgreSQL 17</span>
              </div>
              <div className="flex justify-between border-b border-border pb-1">
                <span className="text-muted-foreground">Cache Middleware</span>
                <span className="font-semibold font-mono text-[10px]">Redis 7</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Identity Protocol</span>
                <span className="font-semibold font-mono text-[10px]">RBAC + MFA Ready</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
export default OrgDashboard;
