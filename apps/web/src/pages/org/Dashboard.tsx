import { useState, useEffect } from 'react';
import {
  GitBranch,
  MapPin,
  ShieldCheck,
  Key,
  RefreshCw,
  FolderTree,
  Building,
  Users,
  DollarSign,
  UserCheck,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { useAuth } from '@/store/AuthContext';
import { apiClient } from '@/services/apiClient';

export function OrgDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    branches: 0,
    locations: 0,
    roles: 0,
    permissions: 0,
    departments: 0,
    businessUnits: 0,
    teams: 0,
    costCenters: 0,
    officeLocations: 0,
    employees: 0,
    activeEmployees: 0,
  });
  const [loading, setLoading] = useState(false);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const [
        branchesRes,
        locsRes,
        rolesRes,
        permsRes,
        deptsRes,
        buRes,
        teamsRes,
        ccRes,
        officesRes,
        empRes,
      ] = await Promise.all([
        apiClient.get('/api/v1/branches').catch(() => ({ data: [] })),
        apiClient.get('/api/v1/locations').catch(() => ({ data: [] })),
        apiClient.get('/api/v1/roles').catch(() => ({ data: [] })),
        apiClient.get('/api/v1/permissions').catch(() => ({ data: [] })),
        apiClient.get('/api/v1/departments').catch(() => ({ data: [] })),
        apiClient.get('/api/v1/business-units').catch(() => ({ data: [] })),
        apiClient.get('/api/v1/teams').catch(() => ({ data: [] })),
        apiClient.get('/api/v1/cost-centers').catch(() => ({ data: [] })),
        apiClient.get('/api/v1/office-locations').catch(() => ({ data: [] })),
        apiClient.get('/api/v1/employees').catch(() => ({ data: [] })),
      ]);

      const empList = empRes.data || [];
      setStats({
        branches: branchesRes.data?.length || 0,
        locations: locsRes.data?.length || 0,
        roles: rolesRes.data?.length || 0,
        permissions: permsRes.data?.length || 0,
        departments: deptsRes.data?.length || 0,
        businessUnits: buRes.data?.length || 0,
        teams: teamsRes.data?.length || 0,
        costCenters: ccRes.data?.length || 0,
        officeLocations: officesRes.data?.length || 0,
        employees: empList.length,
        activeEmployees: empList.filter((e: any) => e.employment_status === 'active').length,
      });
    } catch (err) {
      console.error("Failed to load dashboard telemetry", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const userRolesList = user?.roles?.map((r: any) => typeof r === 'string' ? r : r.name) || ['Admin'];

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight font-mono">Enterprise Operations Console</h1>
          <p className="text-sm text-muted-foreground">
            Phase 1, Phase 2, Phase 3 & Phase 4 Core HR Platform Console.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button onClick={fetchStats} disabled={loading} variant="secondary" className="flex items-center gap-2">
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh Telemetry
          </Button>
        </div>
      </div>

      {/* Authenticated User Banner */}
      {user && (
        <Card className="bg-gradient-to-r from-primary/10 via-background to-background border-primary/20">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-primary text-primary-foreground font-bold text-lg flex items-center justify-center shadow-md">
                  {user.first_name[0]}{user.last_name[0]}
                </div>
                <div>
                  <CardTitle className="text-xl font-bold">{user.first_name} {user.last_name}</CardTitle>
                  <CardDescription className="text-xs font-mono">{user.email} • {user.username}</CardDescription>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-1 text-xs font-semibold rounded bg-primary/20 text-primary border border-primary/30 uppercase font-mono">
                  {userRolesList[0]}
                </span>
                <span className="px-2.5 py-1 text-xs font-semibold rounded bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 uppercase font-mono">
                  {user.status}
                </span>
              </div>
            </div>
          </CardHeader>
        </Card>
      )}

      {/* Phase 4 Core HR Highlights */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="p-4 bg-primary/5 border-primary/20 flex items-center justify-between">
          <div>
            <span className="text-xs font-mono uppercase text-muted-foreground font-semibold">Total Employees</span>
            <h3 className="text-4xl font-bold font-mono tracking-tight text-primary mt-1">{stats.employees}</h3>
          </div>
          <UserCheck className="h-10 w-10 text-primary opacity-80" />
        </Card>
        <Card className="p-4 bg-emerald-500/5 border-emerald-500/20 flex items-center justify-between">
          <div>
            <span className="text-xs font-mono uppercase text-muted-foreground font-semibold">Active Workforce</span>
            <h3 className="text-4xl font-bold font-mono tracking-tight text-emerald-500 mt-1">{stats.activeEmployees}</h3>
          </div>
          <Users className="h-10 w-10 text-emerald-500 opacity-80" />
        </Card>
      </div>

      {/* Phase 3 Organization Structure Metrics Grid */}
      <h2 className="text-xs uppercase font-mono tracking-wider text-muted-foreground font-semibold">
        Organization Hierarchy & Structure Telemetry
      </h2>
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <Card className="p-4 flex flex-col justify-between h-28">
          <div className="flex justify-between items-center text-muted-foreground">
            <span className="text-xs uppercase font-mono font-semibold">Departments</span>
            <FolderTree className="h-5 w-5 text-primary" />
          </div>
          <h3 className="text-3xl font-bold font-mono tracking-tight">{stats.departments}</h3>
        </Card>

        <Card className="p-4 flex flex-col justify-between h-28">
          <div className="flex justify-between items-center text-muted-foreground">
            <span className="text-xs uppercase font-mono font-semibold">Business Units</span>
            <Building className="h-5 w-5 text-primary" />
          </div>
          <h3 className="text-3xl font-bold font-mono tracking-tight">{stats.businessUnits}</h3>
        </Card>

        <Card className="p-4 flex flex-col justify-between h-28">
          <div className="flex justify-between items-center text-muted-foreground">
            <span className="text-xs uppercase font-mono font-semibold">Teams</span>
            <Users className="h-5 w-5 text-primary" />
          </div>
          <h3 className="text-3xl font-bold font-mono tracking-tight">{stats.teams}</h3>
        </Card>

        <Card className="p-4 flex flex-col justify-between h-28">
          <div className="flex justify-between items-center text-muted-foreground">
            <span className="text-xs uppercase font-mono font-semibold">Cost Centers</span>
            <DollarSign className="h-5 w-5 text-emerald-500" />
          </div>
          <h3 className="text-3xl font-bold font-mono tracking-tight text-emerald-500">{stats.costCenters}</h3>
        </Card>

        <Card className="p-4 flex flex-col justify-between h-28">
          <div className="flex justify-between items-center text-muted-foreground">
            <span className="text-xs uppercase font-mono font-semibold">Office Locations</span>
            <MapPin className="h-5 w-5 text-primary" />
          </div>
          <h3 className="text-3xl font-bold font-mono tracking-tight">{stats.officeLocations}</h3>
        </Card>
      </div>

      {/* Phase 1 & 2 Core Telemetry Grid */}
      <h2 className="text-xs uppercase font-mono tracking-wider text-muted-foreground font-semibold">
        Core Infrastructure Telemetry
      </h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="p-4 flex flex-col justify-between h-24">
          <div className="flex justify-between items-center text-muted-foreground">
            <span className="text-xs uppercase font-mono font-semibold">Branches</span>
            <GitBranch className="h-4 w-4 text-primary" />
          </div>
          <h3 className="text-2xl font-bold font-mono">{stats.branches}</h3>
        </Card>

        <Card className="p-4 flex flex-col justify-between h-24">
          <div className="flex justify-between items-center text-muted-foreground">
            <span className="text-xs uppercase font-mono font-semibold">Locations</span>
            <MapPin className="h-4 w-4 text-primary" />
          </div>
          <h3 className="text-2xl font-bold font-mono">{stats.locations}</h3>
        </Card>

        <Card className="p-4 flex flex-col justify-between h-24">
          <div className="flex justify-between items-center text-muted-foreground">
            <span className="text-xs uppercase font-mono font-semibold">Roles</span>
            <ShieldCheck className="h-4 w-4 text-primary" />
          </div>
          <h3 className="text-2xl font-bold font-mono">{stats.roles}</h3>
        </Card>

        <Card className="p-4 flex flex-col justify-between h-24">
          <div className="flex justify-between items-center text-muted-foreground">
            <span className="text-xs uppercase font-mono font-semibold">Permissions</span>
            <Key className="h-4 w-4 text-primary" />
          </div>
          <h3 className="text-2xl font-bold font-mono">{stats.permissions}</h3>
        </Card>
      </div>
    </div>
  );
}

export default OrgDashboard;
