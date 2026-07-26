import React, { useState, useEffect } from 'react';
import { Plus, Search, Layers, CheckCircle, AlertCircle } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { useNotification } from '@/hooks/useNotification';
import { financeService, Account } from '@/services/financeService';

export function ChartOfAccountsPage() {
  const { addNotification } = useNotification();
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [formData, setFormData] = useState({
    account_code: '',
    account_name: '',
    account_type: 'Assets',
    account_subtype: 'Current Assets',
    currency: 'USD',
    opening_balance: 0,
  });

  const loadAccounts = async () => {
    setLoading(true);
    try {
      const data = await financeService.getAccounts();
      setAccounts(data);
    } catch (err) {
      addNotification('Failed to load Chart of Accounts.', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAccounts();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await financeService.createAccount(formData);
      addNotification('Account created successfully.', 'success');
      setIsModalOpen(false);
      loadAccounts();
    } catch (err: any) {
      addNotification(err?.message || 'Failed to create account.', 'error');
    }
  };

  const filtered = accounts.filter(
    (a) =>
      a.account_name.toLowerCase().includes(search.toLowerCase()) ||
      a.account_code.toLowerCase().includes(search.toLowerCase()) ||
      a.account_type.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Chart of Accounts</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Define hierarchical ledger accounts across Assets, Liabilities, Equity, Income, and Expenses
          </p>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          <Plus className="w-4 h-4 mr-2" /> Add Account
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <CardTitle>Account Hierarchy & Balances</CardTitle>
            <div className="relative w-full md:w-64">
              <Search className="w-4 h-4 absolute left-3 top-3 text-gray-400" />
              <input
                type="text"
                placeholder="Search account code or name..."
                className="w-full pl-9 pr-4 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm focus:outline-none"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-gray-600 dark:text-gray-300">
              <thead className="bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200 uppercase font-semibold text-xs">
                <tr>
                  <th className="py-3 px-4">Code</th>
                  <th className="py-3 px-4">Account Name</th>
                  <th className="py-3 px-4">Type</th>
                  <th className="py-3 px-4">Subtype</th>
                  <th className="py-3 px-4 text-right">Opening Balance</th>
                  <th className="py-3 px-4 text-right">Current Balance</th>
                  <th className="py-3 px-4 text-center">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {filtered.map((acct) => (
                  <tr key={acct.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                    <td className="py-3 px-4 font-mono font-bold text-blue-600 dark:text-blue-400">{acct.account_code}</td>
                    <td className="py-3 px-4 font-medium text-gray-900 dark:text-white">{acct.account_name}</td>
                    <td className="py-3 px-4">
                      <span
                        className={`inline-block px-2.5 py-0.5 text-xs font-semibold rounded-full ${
                          acct.account_type === 'Assets'
                            ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                            : acct.account_type === 'Liabilities'
                            ? 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300'
                            : acct.account_type === 'Income'
                            ? 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300'
                            : 'bg-purple-100 text-purple-800 dark:bg-purple-950 dark:text-purple-300'
                        }`}
                      >
                        {acct.account_type}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-gray-500">{acct.account_subtype || '-'}</td>
                    <td className="py-3 px-4 text-right font-mono">${acct.opening_balance?.toLocaleString()}</td>
                    <td className="py-3 px-4 text-right font-mono font-bold text-gray-900 dark:text-white">${acct.balance?.toLocaleString()}</td>
                    <td className="py-3 px-4 text-center">
                      {acct.is_active ? (
                        <span className="text-emerald-600 font-medium text-xs inline-flex items-center"><CheckCircle className="w-3.5 h-3.5 mr-1"/> Active</span>
                      ) : (
                        <span className="text-gray-400 font-medium text-xs">Inactive</span>
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
            <h3 className="text-lg font-bold text-gray-900 dark:text-white">Create Account</h3>
            <form onSubmit={handleCreate} className="space-y-3">
              <div>
                <label className="text-xs font-semibold text-gray-500 dark:text-gray-400">Account Code</label>
                <input
                  type="text"
                  required
                  className="w-full mt-1 p-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded text-sm text-gray-900 dark:text-white focus:outline-none"
                  value={formData.account_code}
                  onChange={(e) => setFormData({ ...formData, account_code: e.target.value })}
                />
              </div>
              <div>
                <label className="text-xs font-semibold text-gray-500 dark:text-gray-400">Account Name</label>
                <input
                  type="text"
                  required
                  className="w-full mt-1 p-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded text-sm text-gray-900 dark:text-white focus:outline-none"
                  value={formData.account_name}
                  onChange={(e) => setFormData({ ...formData, account_name: e.target.value })}
                />
              </div>
              <div>
                <label className="text-xs font-semibold text-gray-500 dark:text-gray-400">Type</label>
                <select
                  className="w-full mt-1 p-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded text-sm text-gray-900 dark:text-white focus:outline-none"
                  value={formData.account_type}
                  onChange={(e) => setFormData({ ...formData, account_type: e.target.value })}
                >
                  <option value="Assets">Assets</option>
                  <option value="Liabilities">Liabilities</option>
                  <option value="Equity">Equity</option>
                  <option value="Income">Income</option>
                  <option value="Expenses">Expenses</option>
                </select>
              </div>
              <div>
                <label className="text-xs font-semibold text-gray-500 dark:text-gray-400">Opening Balance ($)</label>
                <input
                  type="number"
                  step="0.01"
                  className="w-full mt-1 p-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded text-sm text-gray-900 dark:text-white focus:outline-none"
                  value={formData.opening_balance}
                  onChange={(e) => setFormData({ ...formData, opening_balance: parseFloat(e.target.value) || 0 })}
                />
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
