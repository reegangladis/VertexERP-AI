import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { ArrowRightLeft, CheckCircle2, Loader2, ArrowRight } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { Input } from '@/components/Input';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/Table';
import { useNotification } from '@/hooks/useNotification';
import { apiClient } from '@/services/apiClient';

const interTransferSchema = z.object({
  source_warehouse_id: z.string().min(1, 'Source warehouse is required'),
  target_warehouse_id: z.string().min(1, 'Target warehouse is required'),
  product_id: z.string().min(1, 'Product is required'),
  quantity: z.preprocess((val) => parseInt(val as string) || 0, z.number().min(1, 'Quantity must be at least 1')),
});

export function InventoryStockTransfers() {
  const { addNotification } = useNotification();
  const [movements, setMovements] = useState<any[]>([]);
  const [interTransfers, setInterTransfers] = useState<any[]>([]);
  const [products, setProducts] = useState<any[]>([]);
  const [warehouses, setWarehouses] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [processing, setProcessing] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<any>({
    resolver: zodResolver(interTransferSchema),
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [movRes, interRes, prodRes, warRes] = await Promise.all([
        apiClient.get('/api/v1/inventory/transfers'),
        apiClient.get('/api/v1/inventory/transfers/inter-warehouse'),
        apiClient.get('/api/v1/inventory/products'),
        apiClient.get('/api/v1/inventory/warehouses'),
      ]);
      setMovements(movRes.data.data || []);
      setInterTransfers(interRes.data.data || []);
      setProducts(prodRes.data.data || []);
      setWarehouses(warRes.data.data || []);
    } catch (err) {
      console.error("Failed to fetch transfers", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const onSubmitInterTransfer = async (values: any) => {
    if (values.source_warehouse_id === values.target_warehouse_id) {
      addNotification('Source and target warehouse must be different', 'error');
      return;
    }
    setProcessing(true);
    try {
      const payload = {
        source_warehouse_id: values.source_warehouse_id,
        target_warehouse_id: values.target_warehouse_id,
        items: [
          {
            product_id: values.product_id,
            quantity: values.quantity,
          },
        ],
      };
      await apiClient.post('/api/v1/inventory/transfers/inter-warehouse', payload);
      addNotification('Inter-warehouse stock transfer initiated successfully', 'success');
      setModalOpen(false);
      reset();
      fetchData();
    } catch (err: any) {
      addNotification(err.response?.data?.detail || 'Stock transfer failed', 'error');
    } finally {
      setProcessing(false);
    }
  };

  const handleApproveTransfer = async (id: string) => {
    try {
      await apiClient.put(`/api/v1/inventory/transfers/inter-warehouse/${id}/approve`);
      addNotification('Stock transfer approved & warehouse inventory synchronized!', 'success');
      fetchData();
    } catch (err: any) {
      addNotification(err.response?.data?.detail || 'Approval failed', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Stock Transfers & Movements Engine</h1>
          <p className="text-sm text-muted-foreground">Initiate inter-warehouse stock transfers, approve relocation batches, and track bin movements.</p>
        </div>
        <Button onClick={() => setModalOpen(true)} variant="primary" className="flex items-center gap-2">
          <ArrowRightLeft className="h-4 w-4" />
          Initiate Inter-Warehouse Transfer
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Inter-Warehouse Transfers Table */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Inter-Warehouse Transfers</CardTitle>
            <CardDescription>Multi-facility stock shipments and rebalancing status.</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex justify-center py-6">
                <Loader2 className="h-6 w-6 animate-spin text-primary" />
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Transfer #</TableHead>
                    <TableHead>Source WH</TableHead>
                    <TableHead>Target WH</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {interTransfers.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center text-xs text-muted-foreground py-6">
                        No inter-warehouse stock transfers requested yet.
                      </TableCell>
                    </TableRow>
                  ) : (
                    interTransfers.map((t) => {
                      const srcWh = warehouses.find(w => w.id === t.source_warehouse_id);
                      const tgtWh = warehouses.find(w => w.id === t.target_warehouse_id);
                      return (
                        <TableRow key={t.id}>
                          <TableCell className="font-mono text-xs font-bold text-primary">{t.transfer_number}</TableCell>
                          <TableCell className="font-mono text-xs">{srcWh ? srcWh.name : t.source_warehouse_id.slice(0, 8)}</TableCell>
                          <TableCell className="font-mono text-xs">{tgtWh ? tgtWh.name : t.target_warehouse_id.slice(0, 8)}</TableCell>
                          <TableCell className="uppercase text-[10px] font-bold">
                            <span className={`px-2 py-0.5 rounded ${
                              t.status === 'completed' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-amber-500/10 text-amber-500'
                            }`}>
                              {t.status}
                            </span>
                          </TableCell>
                          <TableCell className="text-right">
                            {t.status !== 'completed' && (
                              <Button
                                size="sm"
                                variant="secondary"
                                onClick={() => handleApproveTransfer(t.id)}
                                className="text-[10px] h-7 px-2 flex items-center gap-1 bg-emerald-600/10 text-emerald-500 hover:bg-emerald-600/20"
                              >
                                <CheckCircle2 className="h-3 w-3" /> Approve Transfer
                              </Button>
                            )}
                          </TableCell>
                        </TableRow>
                      );
                    })
                  )}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        {/* Intra-Bin Stock Movements */}
        <Card className="md:col-span-1">
          <CardHeader>
            <CardTitle>Internal Bin Log</CardTitle>
            <CardDescription>Intra-warehouse bin movements.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {movements.length === 0 ? (
              <p className="text-xs text-muted-foreground italic py-2">No intra-bin movements logged.</p>
            ) : (
              movements.map((m) => (
                <div key={m.id} className="p-3 border border-border rounded-xl bg-secondary/15 space-y-1 text-xs font-mono">
                  <div className="flex justify-between font-bold text-primary">
                    <span>Move #{m.id.slice(0, 6)}</span>
                    <span className="text-emerald-500">Qty: {m.quantity}</span>
                  </div>
                  <div className="flex items-center gap-1 text-[10px] text-muted-foreground">
                    <span>{m.from_bin_id ? m.from_bin_id.slice(0, 6) : 'Receiving'}</span>
                    <ArrowRight className="h-3 w-3" />
                    <span>{m.to_bin_id ? m.to_bin_id.slice(0, 6) : 'Scrap/Disp'}</span>
                  </div>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>

      {/* Inter-Warehouse Transfer Modal */}
      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title="Initiate Inter-Warehouse Stock Transfer">
        <form onSubmit={handleSubmit(onSubmitInterTransfer)} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div className="flex flex-col space-y-1.5">
              <label className="text-sm font-medium">Source Warehouse</label>
              <select
                {...register('source_warehouse_id')}
                className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none"
              >
                <option value="">-- Source WH --</option>
                {warehouses.map((w) => (
                  <option key={w.id} value={w.id}>{w.name}</option>
                ))}
              </select>
              {errors.source_warehouse_id && <p className="text-xs text-red-500">{errors.source_warehouse_id.message as string}</p>}
            </div>

            <div className="flex flex-col space-y-1.5">
              <label className="text-sm font-medium">Target Warehouse</label>
              <select
                {...register('target_warehouse_id')}
                className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none"
              >
                <option value="">-- Target WH --</option>
                {warehouses.map((w) => (
                  <option key={w.id} value={w.id}>{w.name}</option>
                ))}
              </select>
              {errors.target_warehouse_id && <p className="text-xs text-red-500">{errors.target_warehouse_id.message as string}</p>}
            </div>
          </div>

          <div className="flex flex-col space-y-1.5">
            <label className="text-sm font-medium">Select Product to Relocate</label>
            <select
              {...register('product_id')}
              className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none"
            >
              <option value="">-- Select Product --</option>
              {products.map((p) => (
                <option key={p.id} value={p.id}>{p.name} ({p.sku})</option>
              ))}
            </select>
            {errors.product_id && <p className="text-xs text-red-500">{errors.product_id.message as string}</p>}
          </div>

          <Input label="Quantity to Relocate" type="number" {...register('quantity')} error={errors.quantity?.message as string} />

          <div className="flex justify-end gap-2 pt-4">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" disabled={processing} variant="primary">
              {processing ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Initiate Transfer'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
export default InventoryStockTransfers;
