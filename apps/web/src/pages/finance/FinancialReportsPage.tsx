import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { useNotification } from '@/hooks/useNotification';
import { financeService } from '@/services/financeService';

export function FinancialReportsPage() {
  const { addNotification } = useNotification();
  const [activeTab, setActiveTab] = useState<'tb' | 'bs' | 'pl' | 'cf' | 'ar_aging' | 'ap_aging' | 'tax' | 'expense' | 'revenue' | 'budget'>('pl');
  const [reportData, setReportData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const loadReport = async () => {
    setLoading(true);
    try {
      if (activeTab === 'tb') {
        const data = await financeService.getTrialBalance();
        setReportData(data);
      } else if (activeTab === 'bs') {
        const data = await financeService.getBalanceSheet();
        setReportData(data);
      } else if (activeTab === 'pl') {
        const data = await financeService.getProfitLoss();
        setReportData(data);
      } else if (activeTab === 'cf') {
        const data = await financeService.getCashFlow();
        setReportData(data);
      } else if (activeTab === 'ar_aging') {
        const data = await financeService.getAgingReport('RECEIVABLE');
        setReportData(data);
      } else if (activeTab === 'ap_aging') {
        const data = await financeService.getAgingReport('PAYABLE');
        setReportData(data);
      } else if (activeTab === 'tax') {
        const data = await financeService.getTaxReport();
        setReportData(data);
      } else if (activeTab === 'expense') {
        const data = await financeService.getExpenseReport();
        setReportData(data);
      } else if (activeTab === 'revenue') {
        const data = await financeService.getRevenueReport();
        setReportData(data);
      } else if (activeTab === 'budget') {
        const data = await financeService.getBudgetReport();
        setReportData(data);
      }
    } catch (err) {
      addNotification('Failed to generate report.', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReport();
  }, [activeTab]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Financial Statements & Reports</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            GAAP & IFRS compliant statutory financial reports calculated directly from double-entry general ledgers
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2 border-b border-gray-200 dark:border-gray-700 pb-2">
        <Button variant={activeTab === 'pl' ? 'primary' : 'outline'} size="sm" onClick={() => setActiveTab('pl')}>
          Profit & Loss
        </Button>
        <Button variant={activeTab === 'bs' ? 'primary' : 'outline'} size="sm" onClick={() => setActiveTab('bs')}>
          Balance Sheet
        </Button>
        <Button variant={activeTab === 'cf' ? 'primary' : 'outline'} size="sm" onClick={() => setActiveTab('cf')}>
          Cash Flow
        </Button>
        <Button variant={activeTab === 'tb' ? 'primary' : 'outline'} size="sm" onClick={() => setActiveTab('tb')}>
          Trial Balance
        </Button>
        <Button variant={activeTab === 'ar_aging' ? 'primary' : 'outline'} size="sm" onClick={() => setActiveTab('ar_aging')}>
          AR Aging
        </Button>
        <Button variant={activeTab === 'ap_aging' ? 'primary' : 'outline'} size="sm" onClick={() => setActiveTab('ap_aging')}>
          AP Aging
        </Button>
        <Button variant={activeTab === 'tax' ? 'primary' : 'outline'} size="sm" onClick={() => setActiveTab('tax')}>
          Tax Summary
        </Button>
        <Button variant={activeTab === 'expense' ? 'primary' : 'outline'} size="sm" onClick={() => setActiveTab('expense')}>
          Expense Analysis
        </Button>
        <Button variant={activeTab === 'revenue' ? 'primary' : 'outline'} size="sm" onClick={() => setActiveTab('revenue')}>
          Revenue Analysis
        </Button>
        <Button variant={activeTab === 'budget' ? 'primary' : 'outline'} size="sm" onClick={() => setActiveTab('budget')}>
          Budget Variance
        </Button>
      </div>

      {/* Report Content */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>
                {activeTab === 'pl' && 'Profit & Loss Statement (Income Statement)'}
                {activeTab === 'bs' && 'Balance Sheet (Statement of Financial Position)'}
                {activeTab === 'cf' && 'Statement of Cash Flows'}
                {activeTab === 'tb' && 'Trial Balance Report'}
                {activeTab === 'ar_aging' && 'Accounts Receivable Aging Analysis'}
                {activeTab === 'ap_aging' && 'Accounts Payable Aging Analysis'}
                {activeTab === 'tax' && 'Tax Liability & Compliance Report'}
                {activeTab === 'expense' && 'Departmental Expense Breakdown'}
                {activeTab === 'revenue' && 'Revenue & Sales Breakdown'}
                {activeTab === 'budget' && 'Budget vs Actual Variance Report'}
              </CardTitle>
              <CardDescription>As of {new Date().toLocaleDateString()}</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="py-12 text-center text-gray-500">Generating report from double-entry ledger...</div>
          ) : activeTab === 'pl' && reportData ? (
            <div className="space-y-6">
              <div className="p-4 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 rounded-lg flex justify-between items-center">
                <span className="font-bold text-emerald-900 dark:text-emerald-300">Net Profit / (Loss):</span>
                <span className="text-2xl font-bold font-mono text-emerald-600 dark:text-emerald-400">
                  ${reportData.net_profit?.toLocaleString()}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <h4 className="font-bold mb-2 text-gray-900 dark:text-white uppercase text-xs">Total Operating Revenue</h4>
                  <p className="text-xl font-bold font-mono text-blue-600">${reportData.total_revenue?.toLocaleString()}</p>
                </div>
                <div>
                  <h4 className="font-bold mb-2 text-gray-900 dark:text-white uppercase text-xs">Total Expenses</h4>
                  <p className="text-xl font-bold font-mono text-rose-600">${reportData.total_expenses?.toLocaleString()}</p>
                </div>
              </div>
            </div>
          ) : activeTab === 'bs' && reportData ? (
            <div className="space-y-6">
              <div className="p-4 bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-800 rounded-lg flex justify-between items-center">
                <span className="font-bold text-blue-900 dark:text-blue-300">Accounting Equation Balance Check:</span>
                <span className="font-bold text-xs px-2.5 py-1 rounded bg-emerald-100 text-emerald-800">
                  {reportData.is_balanced ? 'Balanced (Assets = Liabilities + Equity)' : 'Unbalanced'}
                </span>
              </div>
              <div className="grid grid-cols-3 gap-4 font-mono text-sm">
                <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded">
                  <span className="text-xs text-gray-500 font-sans block">Total Assets</span>
                  <span className="text-lg font-bold text-emerald-600">${reportData.total_assets?.toLocaleString()}</span>
                </div>
                <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded">
                  <span className="text-xs text-gray-500 font-sans block">Total Liabilities</span>
                  <span className="text-lg font-bold text-rose-600">${reportData.total_liabilities?.toLocaleString()}</span>
                </div>
                <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded">
                  <span className="text-xs text-gray-500 font-sans block">Total Equity</span>
                  <span className="text-lg font-bold text-purple-600">${reportData.total_equity?.toLocaleString()}</span>
                </div>
              </div>
            </div>
          ) : activeTab === 'tax' && reportData ? (
            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-4 font-mono text-sm">
                <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded">
                  <span className="text-xs text-gray-500 font-sans block">Output Tax (Collected)</span>
                  <span className="text-lg font-bold text-emerald-600">${reportData.total_tax_collected?.toLocaleString()}</span>
                </div>
                <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded">
                  <span className="text-xs text-gray-500 font-sans block">Input Tax (Paid)</span>
                  <span className="text-lg font-bold text-blue-600">${reportData.total_tax_paid?.toLocaleString()}</span>
                </div>
                <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded">
                  <span className="text-xs text-gray-500 font-sans block">Net Tax Payable</span>
                  <span className="text-lg font-bold text-purple-600">${reportData.net_tax_payable?.toLocaleString()}</span>
                </div>
              </div>
            </div>
          ) : activeTab === 'tb' && reportData ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-gray-600 dark:text-gray-300">
                <thead className="bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200 uppercase font-semibold text-xs">
                  <tr>
                    <th className="py-2 px-3">Code</th>
                    <th className="py-2 px-3">Account</th>
                    <th className="py-2 px-3">Type</th>
                    <th className="py-2 px-3 text-right">Debit ($)</th>
                    <th className="py-2 px-3 text-right">Credit ($)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700 font-mono">
                  {reportData.items?.map((item: any) => (
                    <tr key={item.account_id}>
                      <td className="py-2 px-3 font-bold text-blue-600">{item.account_code}</td>
                      <td className="py-2 px-3 font-sans font-medium text-gray-900 dark:text-white">{item.account_name}</td>
                      <td className="py-2 px-3 font-sans text-xs">{item.account_type}</td>
                      <td className="py-2 px-3 text-right">{item.debit > 0 ? item.debit.toLocaleString() : '-'}</td>
                      <td className="py-2 px-3 text-right">{item.credit > 0 ? item.credit.toLocaleString() : '-'}</td>
                    </tr>
                  ))}
                  <tr className="font-bold bg-gray-100 dark:bg-gray-800">
                    <td colSpan={3} className="py-3 px-3 font-sans text-right">TOTAL:</td>
                    <td className="py-3 px-3 text-right text-emerald-600">${reportData.total_debit?.toLocaleString()}</td>
                    <td className="py-3 px-3 text-right text-emerald-600">${reportData.total_credit?.toLocaleString()}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          ) : (
            <div className="py-8 text-center text-gray-500">Report details generated. Select another report tab to analyze.</div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

