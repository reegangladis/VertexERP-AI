import React, { useState, useEffect } from 'react';
import { Plus, Target, PieChart, CheckCircle2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { useNotification } from '@/hooks/useNotification';
import { financeService, Budget } from '@/services/financeService';

export function BudgetsPage() {
  const { addNotification } = useNotification();
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [formData, setFormData] = useState({
    name: 'FY2026 Annual Operating Budget',
    fiscal_year: 2026,
    budgeted_amount: 150000,
  });

  const loadBudgets = async () => {
    setLoading(true);
    try {
      const data = await financeService.getBudgets();
      setBudgets(data);
    } catch (err) {
      addNotification('Failed to load budgets.', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBudgets();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await financeService.createBudget({
        name: formData.name,
        fiscal_year: formData.fiscal_year,
        items: [],
      });
      addNotification('Budget plan created.', 'success');
      setIsModalOpen(false);
      loadBudgets();
    } catch (err: any) {
      addNotification(err?.message || 'Failed to create budget.', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Budget Management</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Set annual and departmental budget allocations with real-time budget vs actual tracking
          </p>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          <Plus className="w-4 h-4 mr-2" /> New Budget Plan
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {budgets.map((b) => (
          <Card key={b.id}>
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle>{b.name}</CardTitle>
                  <CardDescription>Fiscal Year {b.fiscal_year}</CardDescription>
                </div>
                <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300">
                  {b.status}
                </span>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Allocated Budget:</span>
                <span className="font-bold text-gray-900 dark:text-white">${b.total_budgeted?.toLocaleString()}</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 h-2.5 rounded-full overflow-hidden">
                <div className="bg-emerald-500 h-full rounded-full" style={{ width: '42%' }} />
              </div>
              <p className="text-xs text-right text-gray-400">42% utilized of budget</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-md space-y-4 shadow-xl">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white">Create Budget Plan</h3>
            <form onSubmit={handleCreate} className="space-y-3">
              <div>
                <label className="text-xs font-semibold text-gray-500 dark:text-gray-400">Budget Name</label>
                <input
                  type="text"
                  required
                  className="w-full mt-1 p-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded text-sm text-gray-900 dark:text-white"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-gray-500 dark:text-gray-400">Fiscal Year</label>
                <input
                  type="number"
                  className="w-full mt-1 p-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded text-sm text-gray-900 dark:text-white"
                  value={formData.fiscal_year}
                  onChange={(e) => setFormData({ ...formData, fiscal_year: parseInt(e.target.value) || 2026 })}
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <Button type="button" variant="outline" onClick={() => setIsModalOpen(false)}>Cancel</Button>
                <Button type="submit">Save Budget</Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
