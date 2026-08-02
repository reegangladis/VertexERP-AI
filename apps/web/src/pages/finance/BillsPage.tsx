import React, { useState, useEffect } from 'react';
import { Plus, DollarSign } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { useNotification } from '@/hooks/useNotification';
import { financeService, SupplierBill } from '@/services/financeService';
import { apiClient } from '@/services/apiClient';

export function BillsPage() {
  const { addNotification } = useNotification();
  const [bills, setBills] = useState<SupplierBill[]>([]);
  const [suppliers, setSuppliers] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [formData, setFormData] = useState({
    supplier_id: '',
    bill_date: new Date().toISOString().split('T')[0],
    due_date: new Date(Date.now() + 30 * 86400000).toISOString().split('T')[0],
    description: 'Raw Materials & Vendor Supplies',
    quantity: 1,
    unit_price: 1200,
  });

  const loadData = async () => {
    setLoading(true);
    try {
      const [billData, suppRes] = await Promise.all([
        financeService.getBills(),
        apiClient.get('/api/v1/inventory/suppliers').catch(() => ({ data: { data: [] } })),
      ]);
      setBills(billData);
      setSuppliers(suppRes.data.data || []);
    } catch (err) {
      addNotification('Failed to load supplier bills.', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.supplier_id) {
      addNotification('Please select a supplier.', 'error');
      return;
    }
    try {
      await financeService.createBill({
        supplier_id: formData.supplier_id,
        bill_date: formData.bill_date,
        due_date: formData.due_date,
        items: [
          {
            description: formData.description,
            quantity: formData.quantity,
            unit_price: formData.unit_price,
          },
        ],
      });
      addNotification('Supplier bill recorded & GL posted.', 'success');
      setIsModalOpen(false);
      loadData();
    } catch (err: any) {
      addNotification(err?.message || 'Failed to record bill.', 'error');
    }
  };

  const handlePay = async (bill: SupplierBill) => {
    try {
      await financeService.createPayment({
        payment_type: 'DISBURSEMENT',
        supplier_id: bill.supplier_id,
        bill_id: bill.id,
        payment_date: new Date().toISOString().split('T')[0],
        amount: bill.total_amount - bill.paid_amount,
        payment_method: 'BANK_TRANSFER',
      });
      addNotification('Vendor disbursement paid.', 'success');
      loadData();
    } catch (err: any) {
      addNotification(err?.message || 'Failed to record vendor payment.', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Accounts Payable (Bills)</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Record supplier vendor bills, schedule disbursements, and track payables aging
          </p>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          <Plus className="w-4 h-4 mr-2" /> Record Bill
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Supplier Bills Register</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-gray-600 dark:text-gray-300">
              <thead className="bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200 uppercase font-semibold text-xs">
                <tr>
                  <th className="py-3 px-4">Bill #</th>
                  <th className="py-3 px-4">Bill Date</th>
                  <th className="py-3 px-4">Due Date</th>
                  <th className="py-3 px-4 text-right">Total Amount</th>
                  <th className="py-3 px-4 text-right">Paid Amount</th>
                  <th className="py-3 px-4 text-center">Status</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {bills.map((bill) => (
                  <tr key={bill.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                    <td className="py-3 px-4 font-mono font-bold text-rose-600 dark:text-rose-400">{bill.bill_number}</td>
                    <td className="py-3 px-4">{bill.bill_date}</td>
                    <td className="py-3 px-4">{bill.due_date}</td>
                    <td className="py-3 px-4 text-right font-mono font-bold">${bill.total_amount?.toLocaleString()}</td>
                    <td className="py-3 px-4 text-right font-mono text-emerald-600">${bill.paid_amount?.toLocaleString()}</td>
                    <td className="py-3 px-4 text-center">
                      <span
                        className={`inline-block px-2.5 py-0.5 text-xs font-semibold rounded-full ${
                          bill.status === 'PAID'
                            ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                            : 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300'
                        }`}
                      >
                        {bill.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      {bill.status !== 'PAID' && (
                        <Button size="sm" onClick={() => handlePay(bill)}>
                          <DollarSign className="w-3.5 h-3.5 mr-1" /> Pay Vendor
                        </Button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-md space-y-4 shadow-xl">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white">Record Supplier Bill</h3>
            <form onSubmit={handleCreate} className="space-y-3">
              <div>
                <label className="text-xs font-semibold text-gray-500 dark:text-gray-400">Supplier Vendor</label>
                <select
                  required
                  className="w-full mt-1 p-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded text-sm text-gray-900 dark:text-white"
                  value={formData.supplier_id}
                  onChange={(e) => setFormData({ ...formData, supplier_id: e.target.value })}
                >
                  <option value="">Select Supplier...</option>
                  {suppliers.map((s) => (
                    <option key={s.id} value={s.id}>{s.name}</option>
                  ))}
                  {suppliers.length === 0 && <option value="00000000-0000-0000-0000-000000000002">Global Vendor Supplier</option>}
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-gray-500 dark:text-gray-400">Bill Item Description</label>
                <input
                  type="text"
                  required
                  className="w-full mt-1 p-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded text-sm text-gray-900 dark:text-white"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-xs font-semibold text-gray-500 dark:text-gray-400">Qty</label>
                  <input
                    type="number"
                    className="w-full mt-1 p-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded text-sm text-gray-900 dark:text-white"
                    value={formData.quantity}
                    onChange={(e) => setFormData({ ...formData, quantity: parseFloat(e.target.value) || 1 })}
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-gray-500 dark:text-gray-400">Unit Cost ($)</label>
                  <input
                    type="number"
                    className="w-full mt-1 p-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded text-sm text-gray-900 dark:text-white"
                    value={formData.unit_price}
                    onChange={(e) => setFormData({ ...formData, unit_price: parseFloat(e.target.value) || 0 })}
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <Button type="button" variant="outline" onClick={() => setIsModalOpen(false)}>Cancel</Button>
                <Button type="submit">Save Bill</Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
