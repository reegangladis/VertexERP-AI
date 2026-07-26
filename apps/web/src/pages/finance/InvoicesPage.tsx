import React, { useState, useEffect } from 'react';
import { Plus, Search, DollarSign, Send, CheckCircle2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { useNotification } from '@/hooks/useNotification';
import { financeService, CustomerInvoice } from '@/services/financeService';
import { apiClient } from '@/services/apiClient';

export function InvoicesPage() {
  const { addNotification } = useNotification();
  const [invoices, setInvoices] = useState<CustomerInvoice[]>([]);
  const [customers, setCustomers] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [formData, setFormData] = useState({
    customer_id: '',
    issue_date: new Date().toISOString().split('T')[0],
    due_date: new Date(Date.now() + 30 * 86400000).toISOString().split('T')[0],
    description: 'Enterprise ERP Subscription & Services',
    quantity: 1,
    unit_price: 2500,
  });

  const loadData = async () => {
    setLoading(true);
    try {
      const [invData, custRes] = await Promise.all([
        financeService.getInvoices(),
        apiClient.get('/api/v1/crm/customers').catch(() => ({ data: { data: [] } })),
      ]);
      setInvoices(invData);
      setCustomers(custRes.data.data || []);
    } catch (err) {
      addNotification('Failed to load invoices.', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.customer_id) {
      addNotification('Please select a customer.', 'error');
      return;
    }
    try {
      await financeService.createInvoice({
        customer_id: formData.customer_id,
        issue_date: formData.issue_date,
        due_date: formData.due_date,
        items: [
          {
            description: formData.description,
            quantity: formData.quantity,
            unit_price: formData.unit_price,
          },
        ],
      });
      addNotification('Customer invoice created & GL posted.', 'success');
      setIsModalOpen(false);
      loadData();
    } catch (err: any) {
      addNotification(err?.message || 'Failed to create invoice.', 'error');
    }
  };

  const handlePay = async (invoice: CustomerInvoice) => {
    try {
      await financeService.createPayment({
        payment_type: 'RECEIPT',
        customer_id: invoice.customer_id,
        invoice_id: invoice.id,
        payment_date: new Date().toISOString().split('T')[0],
        amount: invoice.total_amount - invoice.paid_amount,
        payment_method: 'BANK_TRANSFER',
      });
      addNotification('Payment received and recorded.', 'success');
      loadData();
    } catch (err: any) {
      addNotification(err?.message || 'Failed to record payment.', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Accounts Receivable (Invoices)</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Issue customer sales invoices, track payments, and calculate aging telemetry
          </p>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          <Plus className="w-4 h-4 mr-2" /> New Invoice
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Customer Invoices</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-gray-600 dark:text-gray-300">
              <thead className="bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200 uppercase font-semibold text-xs">
                <tr>
                  <th className="py-3 px-4">Invoice #</th>
                  <th className="py-3 px-4">Issue Date</th>
                  <th className="py-3 px-4">Due Date</th>
                  <th className="py-3 px-4 text-right">Total Amount</th>
                  <th className="py-3 px-4 text-right">Paid Amount</th>
                  <th className="py-3 px-4 text-center">Status</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {invoices.map((inv) => (
                  <tr key={inv.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                    <td className="py-3 px-4 font-mono font-bold text-blue-600 dark:text-blue-400">{inv.invoice_number}</td>
                    <td className="py-3 px-4">{inv.issue_date}</td>
                    <td className="py-3 px-4">{inv.due_date}</td>
                    <td className="py-3 px-4 text-right font-mono font-bold">${inv.total_amount?.toLocaleString()}</td>
                    <td className="py-3 px-4 text-right font-mono text-emerald-600">${inv.paid_amount?.toLocaleString()}</td>
                    <td className="py-3 px-4 text-center">
                      <span
                        className={`inline-block px-2.5 py-0.5 text-xs font-semibold rounded-full ${
                          inv.status === 'PAID'
                            ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                            : inv.status === 'SENT'
                            ? 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300'
                            : 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300'
                        }`}
                      >
                        {inv.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      {inv.status !== 'PAID' && (
                        <Button size="sm" onClick={() => handlePay(inv)}>
                          <DollarSign className="w-3.5 h-3.5 mr-1" /> Record Payment
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
            <h3 className="text-lg font-bold text-gray-900 dark:text-white">Create Customer Invoice</h3>
            <form onSubmit={handleCreate} className="space-y-3">
              <div>
                <label className="text-xs font-semibold text-gray-500 dark:text-gray-400">Customer</label>
                <select
                  required
                  className="w-full mt-1 p-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded text-sm text-gray-900 dark:text-white"
                  value={formData.customer_id}
                  onChange={(e) => setFormData({ ...formData, customer_id: e.target.value })}
                >
                  <option value="">Select Customer...</option>
                  {customers.map((c) => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                  {customers.length === 0 && <option value="00000000-0000-0000-0000-000000000001">Global Enterprise Customer</option>}
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-gray-500 dark:text-gray-400">Line Item Description</label>
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
                  <label className="text-xs font-semibold text-gray-500 dark:text-gray-400">Unit Price ($)</label>
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
                <Button type="submit">Issue Invoice</Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
