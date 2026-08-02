import { useState, useEffect } from 'react';
import {
  Users,
  Clock,
  Calendar,
  Briefcase,
  Award,
  TrendingUp,
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

export function HRDashboard() {
  const { addNotification } = useNotification();
  const [stats, setStats] = useState({
    employees: 0,
    attendance: 0,
    leaves: 0,
    recruitment: 0,
    performance: 0,
    training: 0,
  });
  const [loading, setLoading] = useState(false);

  const fetchStats = async () => {
    try {
      const [empRes, attRes, leaveRes, jobRes, reviewRes, courseRes] = await Promise.all([
        apiClient.get('/api/v1/employees'),
        apiClient.get('/api/v1/attendance'),
        apiClient.get('/api/v1/leaves/requests'),
        apiClient.get('/api/v1/recruitment/jobs'),
        apiClient.get('/api/v1/performance/reviews'),
        apiClient.get('/api/v1/training/courses')
      ]);

      setStats({
        employees: empRes.data.data?.length || 0,
        attendance: attRes.data.data?.length || 0,
        leaves: leaveRes.data.data?.length || 0,
        recruitment: jobRes.data.data?.length || 0,
        performance: reviewRes.data.data?.length || 0,
        training: courseRes.data.data?.length || 0,
      });
    } catch (err) {
      console.error("Failed to load HR dashboard telemetry", err);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const handleSeedData = async () => {
    setLoading(true);
    try {
      await apiClient.post('/api/v1/organizations/seed-enterprise-data');
      addNotification('Enterprise & HR structure successfully seeded!', 'success');
      await fetchStats();
    } catch (err: any) {
      addNotification(err.message || 'Failed to seed data', 'error');
    } finally {
      setLoading(false);
    }
  };

  const attritionData = [
    { name: 'Jan', attritionRate: 4.5, promotionRate: 1.2 },
    { name: 'Feb', attritionRate: 4.2, promotionRate: 1.5 },
    { name: 'Mar', attritionRate: 3.8, promotionRate: 1.8 },
    { name: 'Apr', attritionRate: 3.5, promotionRate: 2.2 },
    { name: 'May', attritionRate: 3.1, promotionRate: 3.0 },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">HR Intelligence Cockpit</h1>
          <p className="text-sm text-muted-foreground">
            Monitor employee lifecycles, punch records, leaves pipeline, goals progression, and AI attrition metrics.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button onClick={fetchStats} variant="secondary" className="flex items-center gap-2">
            <RefreshCw className="h-4 w-4" />
            Reload Metrics
          </Button>
          <Button onClick={handleSeedData} disabled={loading} variant="primary" className="flex items-center gap-2">
            <Play className="h-4 w-4" />
            {loading ? 'Seeding...' : 'Seed HR Structure'}
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
        {[
          { label: 'Employees', val: stats.employees, icon: <Users className="h-4 w-4" /> },
          { label: 'Today Punch', val: stats.attendance, icon: <Clock className="h-4 w-4" /> },
          { label: 'Active Leaves', val: stats.leaves, icon: <Calendar className="h-4 w-4" /> },
          { label: 'Open Jobs', val: stats.recruitment, icon: <Briefcase className="h-4 w-4" /> },
          { label: 'Goals Set', val: stats.performance, icon: <TrendingUp className="h-4 w-4" /> },
          { label: 'Courses', val: stats.training, icon: <Award className="h-4 w-4" /> },
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
            <CardTitle>AI Readiness: Staff Attrition & Promotion Trends</CardTitle>
            <CardDescription>Future integration telemetry tracking company stability indices</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[240px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={attritionData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="attritionGrad" x1="0" y1="0" x2="0" y2="1">
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
                    dataKey="attritionRate"
                    stroke="var(--foreground)"
                    fillOpacity={1}
                    fill="url(#attritionGrad)"
                    strokeWidth={1.5}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>AI Predictor Indicators</CardTitle>
            <CardDescription>Prepared models attributes tracking</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-2 p-3 bg-secondary/30 rounded border border-border">
              <Info className="h-5 w-5 text-primary shrink-0" />
              <p className="text-xs text-muted-foreground">
                All models are designed to capture telemetry for employee attrition risk, promotion recommendations, and burnout detections.
              </p>
            </div>
            <div className="text-xs space-y-2">
              <div className="flex justify-between border-b border-border pb-1">
                <span className="text-muted-foreground">Attrition Predictors</span>
                <span className="font-semibold font-mono text-[10px] text-primary">Ready</span>
              </div>
              <div className="flex justify-between border-b border-border pb-1">
                <span className="text-muted-foreground">Salary Guidance ML</span>
                <span className="font-semibold font-mono text-[10px] text-primary">Ready</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Burnout Detection Telemetry</span>
                <span className="font-semibold font-mono text-[10px] text-primary">Ready</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
export default HRDashboard;
