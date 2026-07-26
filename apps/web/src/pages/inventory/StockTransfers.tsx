import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Plus, RefreshCw, Loader2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { Input } from '@/components/Input';
import { useNotification } from '@/hooks/useNotification';
import { apiClient } from '@/services/apiClient';

const transferSchema = z.object({
  product_id: z.string().min(1, 'Product is required'),
  warehouse_id: z.string().min(1, 'Warehouse is required'),
  from_bin_id: z.string().optional().nullable(),
  to_bin_id: z.string().optional().nullable(),
  quantity: z.preprocess((val) => parseInt(val as string) || 0, z.number().min(1, 'Quantity must be at least 1')),
});

interface Transfer {
  id: string;
  product_id: string;
  from_bin_id: string | null;
  to_bin_id: string | null;
  quantity: number;
}

export function InventoryStockTransfers() {
  const { addNotification } = useNotification();
  const [transfers, setTransfers] = useState<Transfer[]>([]);
  const [products, setProducts] = useState<any[]>([]);
  const [warehouses, setWarehouses] = useState<any[]>([]);
  const [bins, setBins] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<any>({
    resolver: zodResolver(transferSchema),
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [transRes, prodRes, warRes, binRes] = await Promise.all([
        apiClient.get('/api/v1/inventory/transfers'),
        apiClient.get('/api/v1/inventory/products'),
        apiClient.get('/api/v1/inventory/warehouses'),
        apiClient.get('/api/v1/inventory/warehouses/bins'),
      ]);
      setTransfers(transRes.data.data || []);
      setProducts(prodRes.data.data || []);
      setWarehouses(warRes.data.data || []);
      setBins(binRes.data.data || []);
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
      const payload = {
        ...values,
        from_bin_id: values.from_bin_id || null,
        to_bin_id: values.to_bin_id || null,
      };
      await apiClient.post('/api/v1/inventory/transfers', payload);
      addNotification('Stock transfer completed successfully', 'success');
      setModalOpen(false);
      reset();
      fetchData();
    } catch (err: any) {
      addNotification(err.response?.data?.detail || 'Stock transfer failed', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Stock Movements Ledger</h1>
          <p className="text-sm text-muted-foreground">Perform physical stock bin transfers, scrap damaged products, and audit paths.</p>
        </div>
        <Button onClick={() => setModalOpen(true)} variant="primary" className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Transfer Stock
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Inventory Movements</CardTitle>
          <CardDescription>Stock paths tracking from origin bin to final destination bin.</CardDescription>
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
                    <th className="py-2.5 px-3">Movement ID</th>
                    <th className="py-2.5 px-3">Product SKU</th>
                    <th className="py-2.5 px-3">From Bin</th>
                    <th className="py-2.5 px-3">To Bin</th>
                    <th className="py-2.5 px-3 text-right">Quantity</th>
                  </tr>
                </thead>
                <tbody>
                  {transfers.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="py-6 text-center text-muted-foreground text-xs">No stock movements logged. Seed data to check.</td>
                    </tr>
                  ) : (
                    transfers.map((t) => (
                      <tr key={t.id} className="border-b border-border hover:bg-secondary/10 text-xs">
                        <td className="py-3 px-3 font-mono text-primary font-semibold">{t.id.slice(0, 8)}...</td>
                        <td className="py-3 px-3 font-mono">Product {t.product_id.slice(0, 8)}...</td>
                        <td className="py-3 px-3 font-mono">{t.from_bin_id ? `Bin ${t.from_bin_id.slice(0, 8)}` : 'Supplier/External'}</td>
                        <td className="py-3 px-3 font-mono">{t.to_bin_id ? `Bin ${t.to_bin_id.slice(0, 8)}` : 'Customer/Scrapped'}</td>
                        <td className="py-3 px-3 text-right font-mono font-semibold">{t.quantity}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title="Perform Stock Transfer">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="flex flex-col space-y-1.5">
            <label className="text-sm font-medium">Select Product</label>
            <select
              {...register('product_id')}
              className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none"
            >
              <option value="">-- Select Product --</option>
              {products.map((p) => (
                <option key={p.id} value={p.id}>{p.name} ({p.sku})</option>
              ))}
            </select>
          </div>

          <div className="flex flex-col space-y-1.5">
            <label className="text-sm font-medium">Warehouse Facility</label>
            <select
              {...register('warehouse_id')}
              className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none"
            >
              <option value="">-- Select Warehouse --</option>
              {warehouses.map((w) => (
                <option key={w.id} value={w.id}>{w.name}</option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="flex flex-col space-y-1.5">
              <label className="text-sm font-medium">From Bin Coordinate</label>
              <select
                {...register('from_bin_id')}
                className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none"
              >
                <option value="">External / Inbound Receipt</option>
                {bins.map((b) => (
                  <option key={b.id} value={b.id}>Bin {b.bin_code}</option>
                ))}
              </select>
            </div>
            <div className="flex flex-col space-y-1.5">
              <label className="text-sm font-medium">To Bin Coordinate</label>
              <select
                {...register('to_bin_id')}
                className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none"
              >
                <option value="">External / Scrap Location</option>
                {bins.map((b) => (
                  <option key={b.id} value={b.id}>Bin {b.bin_code}</option>
                ))}
              </select>
            </div>
          </div>

          <Input label="Quantity to Transfer" type="number" {...register('quantity')} error={errors.quantity?.message as string} />

          <div className="flex justify-end gap-2 pt-4">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary">Process Transfer</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
export default InventoryStockTransfers;
