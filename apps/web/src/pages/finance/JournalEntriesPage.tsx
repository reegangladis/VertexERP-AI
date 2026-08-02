import React, { useState, useEffect } from 'react';
import { Plus, Check, RotateCcw, AlertTriangle } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { useNotification } from '@/hooks/useNotification';
import { financeService, JournalEntry, Account } from '@/services/financeService';

export function JournalEntriesPage() {
  const { addNotification } = useNotification();
  const [entries, setEntries] = useState<JournalEntry[]>([]);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [lines, setLines] = useState([
    { account_id: '', debit: 0, credit: 0, description: '' },
    { account_id: '', debit: 0, credit: 0, description: '' },
  ]);
  const [narration, setNarration] = useState('');

  const loadData = async () => {
    setLoading(true);
    try {
      const [jeData, acctData] = await Promise.all([
        financeService.getJournalEntries(),
        financeService.getAccounts(),
      ]);
      setEntries(jeData);
      setAccounts(acctData);
    } catch (err) {
      addNotification('Failed to load journal entries.', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const totalDebit = lines.reduce((acc, l) => acc + (Number(l.debit) || 0), 0);
  const totalCredit = lines.reduce((acc, l) => acc + (Number(l.credit) || 0), 0);
  const isBalanced = totalDebit > 0 && Math.abs(totalDebit - totalCredit) < 0.01;

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isBalanced) {
      addNotification('Debits must equal Credits for double-entry posting.', 'error');
      return;
    }
    try {
      await financeService.createJournalEntry({
        entry_date: new Date().toISOString().split('T')[0],
        narration,
        lines: lines.filter((l) => l.account_id && (l.debit > 0 || l.credit > 0)),
      });
      addNotification('Journal entry created.', 'success');
      setIsModalOpen(false);
      loadData();
    } catch (err: any) {
      addNotification(err?.message || 'Failed to create journal entry.', 'error');
    }
  };

  const handlePost = async (id: string) => {
    try {
      await financeService.postJournalEntry(id);
      addNotification('Journal entry posted to General Ledger.', 'success');
      loadData();
    } catch (err: any) {
      addNotification(err?.message || 'Failed to post entry.', 'error');
    }
  };

  const handleReverse = async (id: string) => {
    try {
      await financeService.reverseJournalEntry(id);
      addNotification('Journal entry reversed successfully.', 'success');
      loadData();
    } catch (err: any) {
      addNotification(err?.message || 'Failed to reverse entry.', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">General Ledger Journal Entries</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Double-entry journal voucher management, automatic postings, and reversals
          </p>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          <Plus className="w-4 h-4 mr-2" /> New Journal Entry
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Journal Register</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-gray-600 dark:text-gray-300">
              <thead className="bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200 uppercase font-semibold text-xs">
                <tr>
                  <th className="py-3 px-4">Entry #</th>
                  <th className="py-3 px-4">Date</th>
                  <th className="py-3 px-4">Source</th>
                  <th className="py-3 px-4">Narration</th>
                  <th className="py-3 px-4 text-center">Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {entries.map((je) => (
                  <tr key={je.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                    <td className="py-3 px-4 font-mono font-bold text-blue-600 dark:text-blue-400">{je.entry_number}</td>
                    <td className="py-3 px-4">{je.entry_date}</td>
                    <td className="py-3 px-4 font-semibold text-xs text-gray-500">{je.source_type}</td>
                    <td className="py-3 px-4">{je.narration || '-'}</td>
                    <td className="py-3 px-4 text-center">
                      <span
                        className={`inline-block px-2.5 py-0.5 text-xs font-semibold rounded-full ${
                          je.status === 'POSTED'
                            ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                            : je.status === 'REVERSED'
                            ? 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300'
                            : 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300'
                        }`}
                      >
                        {je.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right space-x-2">
                      {je.status === 'DRAFT' && (
                        <Button size="sm" onClick={() => handlePost(je.id)}>
                          <Check className="w-3.5 h-3.5 mr-1" /> Post
                        </Button>
                      )}
                      {je.status === 'POSTED' && (
                        <Button size="sm" variant="outline" onClick={() => handleReverse(je.id)}>
                          <RotateCcw className="w-3.5 h-3.5 mr-1 text-rose-500" /> Reverse
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
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-2xl space-y-4 shadow-xl">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white">Create Journal Entry</h3>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-gray-500 dark:text-gray-400">Narration / Memo</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Monthly Accrual Adjustment"
                  className="w-full mt-1 p-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded text-sm text-gray-900 dark:text-white focus:outline-none"
                  value={narration}
                  onChange={(e) => setNarration(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs font-semibold text-gray-500 dark:text-gray-400">Double Entry Lines</label>
                {lines.map((line, idx) => (
                  <div key={idx} className="flex gap-2 items-center">
                    <select
                      required
                      className="flex-1 p-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded text-sm text-gray-900 dark:text-white"
                      value={line.account_id}
                      onChange={(e) => {
                        const updated = [...lines];
                        updated[idx].account_id = e.target.value;
                        setLines(updated);
                      }}
                    >
                      <option value="">Select Account...</option>
                      {accounts.map((a) => (
                        <option key={a.id} value={a.id}>
                          {a.account_code} - {a.account_name} ({a.account_type})
                        </option>
                      ))}
                    </select>

                    <input
                      type="number"
                      placeholder="Debit"
                      className="w-28 p-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded text-sm text-gray-900 dark:text-white"
                      value={line.debit}
                      onChange={(e) => {
                        const updated = [...lines];
                        updated[idx].debit = parseFloat(e.target.value) || 0;
                        setLines(updated);
                      }}
                    />

                    <input
                      type="number"
                      placeholder="Credit"
                      className="w-28 p-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded text-sm text-gray-900 dark:text-white"
                      value={line.credit}
                      onChange={(e) => {
                        const updated = [...lines];
                        updated[idx].credit = parseFloat(e.target.value) || 0;
                        setLines(updated);
                      }}
                    />
                  </div>
                ))}

                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setLines([...lines, { account_id: '', debit: 0, credit: 0, description: '' }])}
                >
                  + Add Line
                </Button>
              </div>

              {/* Total Balance Check */}
              <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-900 rounded-lg text-sm">
                <div>
                  <span className="font-semibold">Debits:</span> ${totalDebit.toFixed(2)} | <span className="font-semibold">Credits:</span> ${totalCredit.toFixed(2)}
                </div>
                {isBalanced ? (
                  <span className="text-emerald-600 font-bold text-xs inline-flex items-center"><Check className="w-4 h-4 mr-1"/> Balanced</span>
                ) : (
                  <span className="text-rose-500 font-bold text-xs inline-flex items-center"><AlertTriangle className="w-4 h-4 mr-1"/> Out of Balance</span>
                )}
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <Button type="button" variant="outline" onClick={() => setIsModalOpen(false)}>Cancel</Button>
                <Button type="submit" disabled={!isBalanced}>Save Entry</Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
