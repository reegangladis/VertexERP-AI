import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link } from 'react-router-dom';
import { Plus, Home, MapPin, Building, Loader2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Input } from '@/components/Input';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { useNotification } from '@/hooks/useNotification';
import { apiClient } from '@/services/apiClient';

const warehouseSchema = z.object({
  name: z.string().min(3, 'Name must be at least 3 characters'),
  code: z.string().min(2, 'Code must be at least 2 characters'),
  address: z.string().optional(),
  capacity_cubic_meters: z.preprocess((val) => parseFloat(val as string) || 0, z.number().min(0)),
});

interface Warehouse {
  id: string;
  name: string;
  code: string;
  address: string | null;
  capacity_cubic_meters: number | null;
}

export function InventoryWarehouses() {
  const { addNotification } = useNotification();
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<any>({
    resolver: zodResolver(warehouseSchema),
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/api/v1/inventory/warehouses');
      setWarehouses(res.data.data || []);
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
      await apiClient.post('/api/v1/inventory/warehouses', values);
      addNotification('Warehouse structure logged', 'success');
      setModalOpen(false);
      reset();
      fetchData();
    } catch (err: any) {
      addNotification(err.response?.data?.detail || 'Setup failed', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Warehouse Console</h1>
          <p className="text-sm text-muted-foreground">Monitor storage capacities, configure layout racks, and assign managers.</p>
        </div>
        <Button onClick={() => setModalOpen(true)} variant="primary" className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Add Warehouse
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Storage Facilities</CardTitle>
          <CardDescription>Available storage warehouses, volume spaces, and locations addresses.</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center py-6">
              <Loader2 className="h-6 w-6 animate-spin text-primary" />
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {warehouses.length === 0 ? (
                <p className="text-xs text-muted-foreground italic col-span-2 text-center py-4">No warehouses configured. Try seeding data.</p>
              ) : (
                warehouses.map((w) => (
                  <div key={w.id} className="p-4 border border-border rounded bg-card flex flex-col justify-between h-36">
                    <div className="flex justify-between items-start">
                      <div className="space-y-1">
                        <h4 className="font-bold text-sm text-primary">
                          <Link to={`/inventory/warehouses/${w.id}`} className="hover:underline">
                            {w.name}
                          </Link>
                        </h4>
                        <p className="text-[10px] font-mono text-muted-foreground uppercase">Facility Code: {w.code}</p>
                      </div>
                      <span className="bg-secondary/40 border border-border px-2 py-0.5 rounded text-[9px] font-mono text-muted-foreground">
                        {w.capacity_cubic_meters || 'N/A'} m³ Capacity
                      </span>
                    </div>

                    <div className="flex items-center gap-1.5 text-xs text-muted-foreground pt-4">
                      <MapPin className="h-3.5 w-3.5 shrink-0" />
                      <span className="truncate">{w.address || 'Malibu, CA'}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </CardContent>
      </Card>

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title="Add Warehouse Facility">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input label="Warehouse Name" {...register('name')} error={errors.name?.message as string} />
          <Input label="Warehouse Code" {...register('code')} error={errors.code?.message as string} placeholder="STK-MAIN, GOTH-SLO" />
          <Input label="Address" {...register('address')} />
          <Input label="Capacity Volumetric (Cubic Meters)" type="number" {...register('capacity_cubic_meters')} error={errors.capacity_cubic_meters?.message as string} />

          <div className="flex justify-end gap-2 pt-4">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary">Create Facility</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
export default InventoryWarehouses;
