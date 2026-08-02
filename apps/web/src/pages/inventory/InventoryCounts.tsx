import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Plus, Loader2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { useNotification } from '@/hooks/useNotification';
import { apiClient } from '@/services/apiClient';

const countSchema = z.object({
  warehouse_id: z.string().min(1, 'Warehouse is required'),
});

interface Count {
  id: string;
  warehouse_id: string;
  status: string;
}

export function InventoryCounts() {
  const { addNotification } = useNotification();
  const [counts, setCounts] = useState<Count[]>([]);
  const [warehouses, setWarehouses] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<any>({
    resolver: zodResolver(countSchema),
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [countsRes, warRes] = await Promise.all([
        apiClient.get('/api/v1/inventory/counts'),
        apiClient.get('/api/v1/inventory/warehouses'),
      ]);
      setCounts(countsRes.data.data || []);
      setWarehouses(warRes.data.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const onSubmit = async (values: any) => {
    try {
      await apiClient.post('/api/v1/inventory/counts', values);
      addNotification('Inventory count audit session started', 'success');
      setModalOpen(false);
      reset();
      fetchData();
    } catch (err: any) {
      addNotification(err.response?.data?.detail || 'Session creation failed', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Stock Taking & Cycle Counts</h1>
          <p className="text-sm text-muted-foreground">Perform physical counts, reconcile discrepancies, and print variance reports.</p>
        </div>
        <Button onClick={() => setModalOpen(true)} variant="primary" className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Audit Stock Count
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Physical Count Sessions</CardTitle>
          <CardDescription>Inventory taking audits lists and status progress metrics.</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center py-6">
              <Loader2 className="h-6 w-6 animate-spin text-primary" />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left border-collapse">
                <thead>
                  <tr className="border-b border-border text-muted-foreground text-xs uppercase font-mono">
                    <th className="py-2.5 px-3">Session ID</th>
                    <th className="py-2.5 px-3">Warehouse ID</th>
                    <th className="py-2.5 px-3">Audit Status</th>
                    <th className="py-2.5 px-3 text-right">Progress</th>
                  </tr>
                </thead>
                <tbody>
                  {counts.length === 0 ? (
                    <tr>
                      <td colSpan={4} className="py-6 text-center text-muted-foreground text-xs">No active count sessions started. Seed data to check.</td>
                    </tr>
                  ) : (
                    counts.map((c) => (
                      <tr key={c.id} className="border-b border-border hover:bg-secondary/10 text-xs">
                        <td className="py-3 px-3 font-mono text-primary font-semibold">{c.id.slice(0, 8)}...</td>
                        <td className="py-3 px-3 font-mono">Warehouse {c.warehouse_id.slice(0, 8)}...</td>
                        <td className="py-3 px-3 uppercase font-semibold">
                          <span className={`px-2 py-0.5 rounded text-[10px] ${
                            c.status === 'completed' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-amber-500/10 text-amber-500'
                          }`}>
                            {c.status}
                          </span>
                        </td>
                        <td className="py-3 px-3 text-right font-mono text-muted-foreground">In Progress</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title="Audit Stock Count Session">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="flex flex-col space-y-1.5">
            <label className="text-sm font-medium">Warehouse Facility to Audit</label>
            <select
              {...register('warehouse_id')}
              className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none"
            >
              <option value="">-- Select Warehouse --</option>
              {warehouses.map((w) => (
                <option key={w.id} value={w.id}>{w.name}</option>
              ))}
            </select>
            {errors.warehouse_id && <p className="text-xs text-red-500">{errors.warehouse_id.message as string}</p>}
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary">Start Session</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
export default InventoryCounts;
