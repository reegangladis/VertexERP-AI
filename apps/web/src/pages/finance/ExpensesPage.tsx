import React, { useState, useEffect } from 'react';
import { Plus, Check, DollarSign } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { useNotification } from '@/hooks/useNotification';
import { financeService, ExpenseClaim, ExpenseCategory } from '@/services/financeService';

export function ExpensesPage() {
  const { addNotification } = useNotification();
  const [claims, setClaims] = useState<ExpenseClaim[]>([]);
  const [categories, setCategories] = useState<ExpenseCategory[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [formData, setFormData] = useState({
    employee_id: '00000000-0000-0000-0000-000000000003',
    category_id: '',
    claim_date: new Date().toISOString().split('T')[0],
    amount: 150.0,
    description: 'Client Dinner & Travel Expense',
  });

  const loadData = async () => {
    setLoading(true);
    try {
      const [claimData, catData] = await Promise.all([
        financeService.getExpenseClaims(),
        financeService.getExpenseCategories(),
      ]);
      setClaims(claimData);
      setCategories(catData);
      if (catData.length > 0) {
        setFormData((prev) => ({ ...prev, category_id: catData[0].id }));
      }
    } catch (err) {
      addNotification('Failed to load expense claims.', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.category_id) {
      addNotification('Expense category required.', 'error');
      return;
    }
    try {
      await financeService.createExpenseClaim(formData);
      addNotification('Expense claim submitted.', 'success');
      setIsModalOpen(false);
      loadData();
    } catch (err: any) {
      addNotification(err?.message || 'Failed to submit claim.', 'error');
    }
  };

  const handleApprove = async (id: string) => {
    try {
      await financeService.approveExpenseClaim(id);
      addNotification('Expense claim approved.', 'success');
      loadData();
    } catch (err: any) {
      addNotification(err?.message || 'Failed to approve claim.', 'error');
    }
  };

  const handleReimburse = async (id: string) => {
    try {
      await financeService.reimburseExpenseClaim(id);
      addNotification('Expense claim reimbursed & GL updated.', 'success');
      loadData();
    } catch (err: any) {
      addNotification(err?.message || 'Failed to reimburse claim.', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Expense Management</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Submit employee expense reimbursement claims, approvals, receipt tracking, and GL posting
          </p>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          <Plus className="w-4 h-4 mr-2" /> Submit Claim
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Expense Claims Register</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-gray-600 dark:text-gray-300">
              <thead className="bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200 uppercase font-semibold text-xs">
                <tr>
                  <th className="py-3 px-4">Claim #</th>
                  <th className="py-3 px-4">Date</th>
                  <th className="py-3 px-4">Description</th>
                  <th className="py-3 px-4 text-right">Amount</th>
                  <th className="py-3 px-4 text-center">Status</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {claims.map((claim) => (
                  <tr key={claim.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                    <td className="py-3 px-4 font-mono font-bold text-indigo-600 dark:text-indigo-400">{claim.claim_number}</td>
                    <td className="py-3 px-4">{claim.claim_date}</td>
                    <td className="py-3 px-4">{claim.description}</td>
                    <td className="py-3 px-4 text-right font-mono font-bold">${claim.amount?.toLocaleString()}</td>
                    <td className="py-3 px-4 text-center">
                      <span
                        className={`inline-block px-2.5 py-0.5 text-xs font-semibold rounded-full ${
                          claim.status === 'REIMBURSED'
                            ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                            : claim.status === 'APPROVED'
                            ? 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300'
                            : 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300'
                        }`}
                      >
                        {claim.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right space-x-2">
                      {claim.status === 'SUBMITTED' && (
                        <Button size="sm" onClick={() => handleApprove(claim.id)}>
                          <Check className="w-3.5 h-3.5 mr-1" /> Approve
                        </Button>
                      )}
                      {claim.status === 'APPROVED' && (
                        <Button size="sm" variant="outline" onClick={() => handleReimburse(claim.id)}>
                          <DollarSign className="w-3.5 h-3.5 mr-1 text-emerald-500" /> Reimburse
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
            <h3 className="text-lg font-bold text-gray-900 dark:text-white">Submit Expense Claim</h3>
            <form onSubmit={handleCreate} className="space-y-3">
              <div>
                <label className="text-xs font-semibold text-gray-500 dark:text-gray-400">Expense Category</label>
                <select
                  required
                  className="w-full mt-1 p-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded text-sm text-gray-900 dark:text-white"
                  value={formData.category_id}
                  onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
                >
                  {categories.map((c) => (
                    <option key={c.id} value={c.id}>{c.name} ({c.code})</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-gray-500 dark:text-gray-400">Description</label>
                <input
                  type="text"
                  required
                  className="w-full mt-1 p-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded text-sm text-gray-900 dark:text-white"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-gray-500 dark:text-gray-400">Amount ($)</label>
                <input
                  type="number"
                  step="0.01"
                  required
                  className="w-full mt-1 p-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded text-sm text-gray-900 dark:text-white"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: parseFloat(e.target.value) || 0 })}
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <Button type="button" variant="outline" onClick={() => setIsModalOpen(false)}>Cancel</Button>
                <Button type="submit">Submit Claim</Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
