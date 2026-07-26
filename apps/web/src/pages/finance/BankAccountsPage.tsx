import React, { useState, useEffect } from 'react';
import { Plus, Building2, CheckCircle2, RefreshCw } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { useNotification } from '@/hooks/useNotification';
import { financeService, BankAccount } from '@/services/financeService';

export function BankAccountsPage() {
  const { addNotification } = useNotification();
  const [accounts, setAccounts] = useState<BankAccount[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [formData, setFormData] = useState({
    account_name: 'Primary Corporate Operating Account',
    bank_name: 'JPMorgan Chase Bank',
    account_number: '9876543210',
    swift_code: 'CHASUS33',
    current_balance: 98500.0,
  });

  const loadBankAccounts = async () => {
    setLoading(true);
    try {
      const data = await financeService.getBankAccounts();
      setAccounts(data);
    } catch (err) {
      addNotification('Failed to load bank accounts.', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBankAccounts();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await financeService.createBankAccount(formData);
      addNotification('Bank account registered.', 'success');
      setIsModalOpen(false);
      loadBankAccounts();
    } catch (err: any) {
      addNotification(err?.message || 'Failed to add bank account.', 'error');
    }
  };

  const handleReconcile = async (account: BankAccount) => {
    try {
      const res = await financeService.reconcileBank({
        bank_account_id: account.id,
        statement_date: new Date().toISOString().split('T')[0],
        statement_balance: account.current_balance,
      });
      addNotification('Bank reconciliation completed! Statement matched GL balance.', 'success');
    } catch (err: any) {
      addNotification('Reconciliation error.', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Banking & Cash Management</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Manage corporate bank accounts, bank feeds, deposits, withdrawals, and bank statement reconciliations
          </p>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          <Plus className="w-4 h-4 mr-2" /> Add Bank Account
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {accounts.map((b) => (
          <Card key={b.id} className="border-t-4 border-blue-600">
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle>{b.account_name}</CardTitle>
                  <CardDescription>{b.bank_name} • Account #{b.account_number}</CardDescription>
                </div>
                <Building2 className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider">Current GL Balance</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">${b.current_balance?.toLocaleString()} {b.currency}</p>
              </div>
              <Button size="sm" variant="outline" className="w-full" onClick={() => handleReconcile(b)}>
                <CheckCircle2 className="w-4 h-4 mr-1 text-emerald-500" /> Reconcile Statement
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-md space-y-4 shadow-xl">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white">Add Bank Account</h3>
            <form onSubmit={handleCreate} className="space-y-3">
              <div>
                <label className="text-xs font-semibold text-gray-500 dark:text-gray-400">Account Name</label>
                <input
                  type="text"
                  required
                  className="w-full mt-1 p-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded text-sm text-gray-900 dark:text-white"
                  value={formData.account_name}
                  onChange={(e) => setFormData({ ...formData, account_name: e.target.value })}
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-gray-500 dark:text-gray-400">Bank Name</label>
                <input
                  type="text"
                  required
                  className="w-full mt-1 p-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded text-sm text-gray-900 dark:text-white"
                  value={formData.bank_name}
                  onChange={(e) => setFormData({ ...formData, bank_name: e.target.value })}
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-xs font-semibold text-gray-500 dark:text-gray-400">Account Number</label>
                  <input
                    type="text"
                    required
                    className="w-full mt-1 p-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded text-sm text-gray-900 dark:text-white"
                    value={formData.account_number}
                    onChange={(e) => setFormData({ ...formData, account_number: e.target.value })}
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-gray-500 dark:text-gray-400">Opening Balance ($)</label>
                  <input
                    type="number"
                    className="w-full mt-1 p-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded text-sm text-gray-900 dark:text-white"
                    value={formData.current_balance}
                    onChange={(e) => setFormData({ ...formData, current_balance: parseFloat(e.target.value) || 0 })}
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <Button type="button" variant="outline" onClick={() => setIsModalOpen(false)}>Cancel</Button>
                <Button type="submit">Save Account</Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
