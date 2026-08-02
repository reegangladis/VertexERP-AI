import { useState, useEffect } from 'react';
import {
  Package,
  Layers,
  Building,
  Truck,
  RefreshCw,
  Play,
  Info,
  DollarSign
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

export function InventoryDashboard() {
  const { addNotification } = useNotification();
  const [stats, setStats] = useState({
    products: 0,
    categories: 0,
    warehouses: 0,
    suppliers: 0,
    pos: 0,
  });
  const [loading, setLoading] = useState(false);

  const fetchStats = async () => {
    try {
      const [prodRes, catRes, warRes, supRes, poRes] = await Promise.all([
        apiClient.get('/api/v1/inventory/products'),
        apiClient.get('/api/v1/inventory/categories'),
        apiClient.get('/api/v1/inventory/warehouses'),
        apiClient.get('/api/v1/inventory/suppliers'),
        apiClient.get('/api/v1/inventory/purchase-orders')
      ]);

      setStats({
        products: prodRes.data.data?.length || 0,
        categories: catRes.data.data?.length || 0,
        warehouses: warRes.data.data?.length || 0,
        suppliers: supRes.data.data?.length || 0,
        pos: poRes.data.data?.length || 0,
      });
    } catch (err) {
      console.error("Failed to load inventory stats", err);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const handleSeedData = async () => {
    setLoading(true);
    try {
      await apiClient.post('/api/v1/organizations/seed-enterprise-data');
      addNotification('Inventory structure seeded successfully!', 'success');
      await fetchStats();
    } catch (err: any) {
      addNotification(err.message || 'Seeding failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const chartData = [
    { name: 'Stark Vault', StockValue: 125000, CapacityUsed: 45 },
    { name: 'Wayne Gotham', StockValue: 380000, CapacityUsed: 72 },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Inventory & Warehouse Intelligence</h1>
          <p className="text-sm text-muted-foreground">
            Monitor SKU levels, verify warehouse storage bins capacity, and oversee supplier procurement cycles.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button onClick={fetchStats} variant="secondary" className="flex items-center gap-2">
            <RefreshCw className="h-4 w-4" />
            Reload Metrics
          </Button>
          <Button onClick={handleSeedData} disabled={loading} variant="primary" className="flex items-center gap-2">
            <Play className="h-4 w-4" />
            {loading ? 'Seeding...' : 'Seed Inventory Structure'}
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {[
          { label: 'Products Master', val: stats.products, icon: <Package className="h-4 w-4" /> },
          { label: 'Categories', val: stats.categories, icon: <Layers className="h-4 w-4" /> },
          { label: 'Active Warehouses', val: stats.warehouses, icon: <Building className="h-4 w-4" /> },
          { label: 'Supplier Profiles', val: stats.suppliers, icon: <Truck className="h-4 w-4" /> },
          { label: 'Purchase Orders', val: stats.pos, icon: <DollarSign className="h-4 w-4" /> },
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
            <CardTitle>AI Readiness: Storage Value and Capacity metrics</CardTitle>
            <CardDescription>Valuation index and current volumetric space usage percentage per warehouse</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[240px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
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
                  <Bar dataKey="StockValue" fill="var(--primary)" radius={[4, 4, 0, 0]} name="Stock Value ($)" />
                  <Bar dataKey="CapacityUsed" fill="var(--muted)" radius={[4, 4, 0, 0]} name="Capacity Used (%)" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>AI Optimization Telemetry</CardTitle>
            <CardDescription>Telemetry hooks logged to database</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-2 p-3 bg-secondary/30 rounded border border-border">
              <Info className="h-5 w-5 text-primary shrink-0" />
              <p className="text-xs text-muted-foreground">
                Stock movements, supplier ratings, and purchase orders are logged with precise indexes to facilitate future AI predictions.
              </p>
            </div>
            <div className="text-xs space-y-2">
              <div className="flex justify-between border-b border-border pb-1">
                <span className="text-muted-foreground">Demand Forecasting</span>
                <span className="font-semibold font-mono text-[10px] text-primary">Data Pipeline Ready</span>
              </div>
              <div className="flex justify-between border-b border-border pb-1">
                <span className="text-muted-foreground">Stockout Prediction</span>
                <span className="font-semibold font-mono text-[10px] text-primary">Data Pipeline Ready</span>
              </div>
              <div className="flex justify-between border-b border-border pb-1">
                <span className="text-muted-foreground">Supplier Rating</span>
                <span className="font-semibold font-mono text-[10px] text-primary">Data Pipeline Ready</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Purchase Recommender</span>
                <span className="font-semibold font-mono text-[10px] text-primary">Data Pipeline Ready</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
export default InventoryDashboard;
