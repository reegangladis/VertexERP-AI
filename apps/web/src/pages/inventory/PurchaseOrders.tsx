import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Plus, Truck, Loader2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { Input } from '@/components/Input';
import { useNotification } from '@/hooks/useNotification';
import { apiClient } from '@/services/apiClient';

const poSchema = z.object({
  supplier_id: z.string().min(1, 'Supplier is required'),
  po_number: z.string().min(3, 'PO Number is required'),
  product_id: z.string().min(1, 'Product is required'),
  quantity: z.preprocess((val) => parseInt(val as string) || 0, z.number().min(1, 'Quantity must be at least 1')),
  unit_price: z.preprocess((val) => parseFloat(val as string) || 0, z.number().min(0.01, 'Unit price must be positive')),
});

interface PurchaseOrder {
  id: string;
  po_number: string;
  supplier_id: string;
  status: string;
  total_amount: number;
}

export function InventoryPurchaseOrders() {
  const { addNotification } = useNotification();
  const [purchaseOrders, setPurchaseOrders] = useState<PurchaseOrder[]>([]);
  const [suppliers, setSuppliers] = useState<any[]>([]);
  const [products, setProducts] = useState<any[]>([]);
  const [warehouses, setWarehouses] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [receiptModalOpen, setReceiptModalOpen] = useState(false);
  const [activePoId, setActivePoId] = useState('');
  const [selectedWarehouseId, setSelectedWarehouseId] = useState('');

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<any>({
    resolver: zodResolver(poSchema),
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [poRes, supRes, prodRes, warRes] = await Promise.all([
        apiClient.get('/api/v1/inventory/purchase-orders'),
        apiClient.get('/api/v1/inventory/suppliers'),
        apiClient.get('/api/v1/inventory/products'),
        apiClient.get('/api/v1/inventory/warehouses'),
      ]);
      setPurchaseOrders(poRes.data.data || []);
      setSuppliers(supRes.data.data || []);
      setProducts(prodRes.data.data || []);
      setWarehouses(warRes.data.data || []);
      if (warRes.data.data?.length > 0) {
        setSelectedWarehouseId(warRes.data.data[0].id);
      }
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
        supplier_id: values.supplier_id,
        po_number: values.po_number,
        items: [
          {
            product_id: values.product_id,
            quantity: values.quantity,
            unit_price: values.unit_price,
          },
        ],
      };
      await apiClient.post('/api/v1/inventory/purchase-orders', payload);
      addNotification('Purchase Order created successfully', 'success');
      setModalOpen(false);
      reset();
      fetchData();
    } catch (err: any) {
      addNotification(err.response?.data?.detail || 'PO creation failed', 'error');
    }
  };

  const handleReceiveGoods = async () => {
    try {
      await apiClient.post(`/api/v1/inventory/purchase-orders/${activePoId}/receive?warehouse_id=${selectedWarehouseId}`);
      addNotification('Goods received under new GRN. Stock levels updated.', 'success');
      setReceiptModalOpen(false);
      fetchData();
    } catch (err: any) {
      addNotification(err.response?.data?.detail || 'Receipt step failed', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Purchase Orders (PO)</h1>
          <p className="text-sm text-muted-foreground">Draft PO contracts, verify approvals status, and validate goods receipt (GRN) items.</p>
        </div>
        <Button onClick={() => setModalOpen(true)} variant="primary" className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Setup PO
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Procurement Orders</CardTitle>
          <CardDescription>Procurement ledger tracking total amounts and validation statuses.</CardDescription>
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
                    <th className="py-2.5 px-3">PO Number</th>
                    <th className="py-2.5 px-3">Supplier ID</th>
                    <th className="py-2.5 px-3 text-right">Total Value</th>
                    <th className="py-2.5 px-3">Status</th>
                    <th className="py-2.5 px-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {purchaseOrders.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="py-6 text-center text-muted-foreground text-xs">No PO records tracked. Seed data to check.</td>
                    </tr>
                  ) : (
                    purchaseOrders.map((po) => (
                      <tr key={po.id} className="border-b border-border hover:bg-secondary/10 text-xs">
                        <td className="py-3 px-3 font-semibold text-foreground">{po.po_number}</td>
                        <td className="py-3 px-3 font-mono">Supplier {po.supplier_id.slice(0, 8)}...</td>
                        <td className="py-3 px-3 text-right font-mono font-semibold text-emerald-500">${po.total_amount}</td>
                        <td className="py-3 px-3 uppercase font-semibold">
                          <span className={`px-2 py-0.5 rounded text-[10px] ${
                            po.status === 'received' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-amber-500/10 text-amber-500'
                          }`}>
                            {po.status}
                          </span>
                        </td>
                        <td className="py-3 px-3 text-right">
                          {po.status !== 'received' && (
                            <button
                              onClick={() => {
                                setActivePoId(po.id);
                                setReceiptModalOpen(true);
                              }}
                              className="p-1.5 hover:bg-emerald-500/10 text-emerald-500 rounded border border-emerald-500/20"
                              title="Receive Goods (GRN)"
                            >
                              <Truck className="h-4 w-4" />
                            </button>
                          )}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title="Setup Purchase Order">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input label="PO Number Code" {...register('po_number')} error={errors.po_number?.message as string} placeholder="PO-2026-X00" />
          
          <div className="flex flex-col space-y-1.5">
            <label className="text-sm font-medium">Supplier Partner</label>
            <select
              {...register('supplier_id')}
              className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none"
            >
              <option value="">-- Select Supplier --</option>
              {suppliers.map((s) => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
          </div>

          <div className="border-t border-border pt-3 space-y-3">
            <h4 className="text-xs font-bold text-muted-foreground uppercase font-mono">Select PO Line Item</h4>
            <div className="flex flex-col space-y-1.5">
              <label className="text-xs font-semibold">Product SKU</label>
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
            <div className="grid grid-cols-2 gap-3">
              <Input label="Quantity" type="number" {...register('quantity')} error={errors.quantity?.message as string} />
              <Input label="Unit Price ($)" type="number" step="0.01" {...register('unit_price')} error={errors.unit_price?.message as string} />
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary">Create PO</Button>
          </div>
        </form>
      </Modal>

      <Modal isOpen={receiptModalOpen} onClose={() => setReceiptModalOpen(false)} title="Validate Goods Receipt Note (GRN)">
        <div className="space-y-4">
          <div className="flex flex-col space-y-1.5">
            <label className="text-sm font-medium">Target Warehouse Facility</label>
            <select
              value={selectedWarehouseId}
              onChange={(e) => setSelectedWarehouseId(e.target.value)}
              className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none"
            >
              {warehouses.map((w) => (
                <option key={w.id} value={w.id}>{w.name}</option>
              ))}
            </select>
          </div>
          <p className="text-xs text-muted-foreground">
            Receiving goods will automatically generate a Goods Receipt Note (GRN), trigger transaction logs, and increase stock levels under the selected facility.
          </p>
          <div className="flex justify-end gap-2 pt-4">
            <Button variant="secondary" onClick={() => setReceiptModalOpen(false)}>Cancel</Button>
            <Button onClick={handleReceiveGoods} variant="primary">Receive & Audit Stock</Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
export default InventoryPurchaseOrders;
