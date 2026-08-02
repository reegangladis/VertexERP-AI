import { useState, useEffect } from 'react';
import {
  Users,
  TrendingUp,
  Briefcase,
  AlertCircle,
  Play,
  RefreshCw,
  Info,
  Activity
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { useNotification } from '@/hooks/useNotification';
import { apiClient } from '@/services/apiClient';

export function CRMDashboard() {
  const { addNotification } = useNotification();
  const [stats, setStats] = useState({
    customers: 0,
    leads: 0,
    deals: 0,
    tickets: 0,
    campaigns: 0,
  });
  const [loading, setLoading] = useState(false);

  const fetchStats = async () => {
    try {
      const [custRes, leadRes, dealRes, ticketRes, campRes] = await Promise.all([
        apiClient.get('/api/v1/crm/customers'),
        apiClient.get('/api/v1/crm/leads'),
        apiClient.get('/api/v1/crm/deals'),
        apiClient.get('/api/v1/crm/support-tickets'),
        apiClient.get('/api/v1/crm/campaigns')
      ]);

      setStats({
        customers: custRes.data.data?.length || 0,
        leads: leadRes.data.data?.length || 0,
        deals: dealRes.data.data?.length || 0,
        tickets: ticketRes.data.data?.length || 0,
        campaigns: campRes.data.data?.length || 0,
      });
    } catch (err) {
      console.error("Failed to load CRM dashboard telemetry", err);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const handleSeedData = async () => {
    setLoading(true);
    try {
      await apiClient.post('/api/v1/organizations/seed-enterprise-data');
      addNotification('CRM & Account structure successfully seeded!', 'success');
      await fetchStats();
    } catch (err: any) {
      addNotification(err.message || 'Failed to seed data', 'error');
    } finally {
      setLoading(false);
    }
  };

  const revenueData = [
    { month: 'May', Expected: 120000, Actual: 95000 },
    { month: 'Jun', Expected: 150000, Actual: 140000 },
    { month: 'Jul', Expected: 220000, Actual: 190000 },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">CRM Intelligence Cockpit</h1>
          <p className="text-sm text-muted-foreground">
            Monitor client accounts, sales deals progression, support logs, and marketing campaign performance indicators.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button onClick={fetchStats} variant="secondary" className="flex items-center gap-2">
            <RefreshCw className="h-4 w-4" />
            Reload Metrics
          </Button>
          <Button onClick={handleSeedData} disabled={loading} variant="primary" className="flex items-center gap-2">
            <Play className="h-4 w-4" />
            {loading ? 'Seeding...' : 'Seed CRM Structure'}
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {[
          { label: 'Total Customers', val: stats.customers, icon: <Users className="h-4 w-4" /> },
          { label: 'Active Leads', val: stats.leads, icon: <TrendingUp className="h-4 w-4" /> },
          { label: 'Pipeline Deals', val: stats.deals, icon: <Briefcase className="h-4 w-4" /> },
          { label: 'Support Tickets', val: stats.tickets, icon: <AlertCircle className="h-4 w-4" /> },
          { label: 'Marketing Campaigns', val: stats.campaigns, icon: <Activity className="h-4 w-4" /> },
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
            <CardTitle>AI Readiness: Sales Pipeline Revenue Forecast</CardTitle>
            <CardDescription>Deals valuation compared with historical probability scores</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[240px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={revenueData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" />
                  <XAxis dataKey="month" stroke="var(--muted)" fontSize={11} tickLine={false} />
                  <YAxis stroke="var(--muted)" fontSize={11} tickLine={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'var(--card)',
                      borderColor: 'var(--border)',
                      color: 'var(--foreground)',
                      fontSize: 12,
                    }}
                  />
                  <Bar dataKey="Expected" fill="var(--primary)" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="Actual" fill="var(--muted)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>AI Scoring & Churn Metrics</CardTitle>
            <CardDescription>Indicators tracking client behavior and deal health</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-2 p-3 bg-secondary/30 rounded border border-border">
              <Info className="h-5 w-5 text-primary shrink-0" />
              <p className="text-xs text-muted-foreground">
                CRM telemetry collects data points to run future churn predictions and automatically grade new leads by converting channels.
              </p>
            </div>
            <div className="text-xs space-y-2">
              <div className="flex justify-between border-b border-border pb-1">
                <span className="text-muted-foreground">Lead Scoring ML</span>
                <span className="font-semibold font-mono text-[10px] text-primary">Telemetry Enabled</span>
              </div>
              <div className="flex justify-between border-b border-border pb-1">
                <span className="text-muted-foreground">Sales Forecast Engines</span>
                <span className="font-semibold font-mono text-[10px] text-primary">Telemetry Enabled</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Churn Prediction</span>
                <span className="font-semibold font-mono text-[10px] text-primary">Telemetry Enabled</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
export default CRMDashboard;
