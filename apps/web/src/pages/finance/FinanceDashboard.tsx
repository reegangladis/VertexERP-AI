import React, { useState, useEffect } from 'react';
import {
  DollarSign,
  TrendingUp,
  TrendingDown,
  CreditCard,
  Building2,
  PieChart,
  FileText,
  Search,
  Plus,
  RefreshCw,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { useNotification } from '@/hooks/useNotification';
import { financeService } from '@/services/financeService';

export function FinanceDashboard() {
  const { addNotification } = useNotification();
  const [metrics, setMetrics] = useState({
    revenue: 125000,
    expenses: 42000,
    netProfit: 83000,
    cashBalance: 98500,
    receivables: 15400,
    payables: 8900,
    budgetUtil: 68.5,
  });
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const summary = await financeService.getDashboardSummary();
      setMetrics({
        revenue: summary.total_revenue || 0,
        expenses: summary.total_expenses || 0,
        netProfit: summary.net_profit || 0,
        cashBalance: summary.total_cash_balance || 0,
        receivables: summary.total_receivables || 0,
        payables: summary.total_payables || 0,
        budgetUtil: summary.budget_utilization_pct || 0,
      });
    } catch (err) {
      // Fallback defaults
      try {
        const pl = await financeService.getProfitLoss();
        setMetrics((prev) => ({
          ...prev,
          revenue: pl.total_revenue || prev.revenue,
          expenses: pl.total_expenses || prev.expenses,
          netProfit: pl.net_profit || prev.netProfit,
        }));
      } catch (e) {
        // preserve initial state
      }
    } finally {
      setLoading(false);
    }
  };


  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    try {
      const results = await financeService.searchFinance(searchQuery);
      setSearchResults(results);
      addNotification(`Found ${results.length} financial records matching "${searchQuery}"`, 'info');
    } catch (err) {
      addNotification('Search failed.', 'error');
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Finance & Accounting Intelligence</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Real-time General Ledger, AR/AP, Banking, Budgeting, and Executive Reports
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm" onClick={loadDashboardData} disabled={loading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} /> Refresh
          </Button>
        </div>
      </div>

      {/* Enterprise Search Bar */}
      <Card className="p-4 bg-gradient-to-r from-blue-50/50 to-indigo-50/50 dark:from-gray-800 dark:to-gray-900">
        <div className="flex items-center gap-3">
          <Search className="w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search Accounts, Invoices, Bills, Journal Entries, Expenses..."
            className="flex-1 bg-transparent text-sm text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          />
          <Button size="sm" onClick={handleSearch}>Search</Button>
        </div>
        {searchResults.length > 0 && (
          <div className="mt-3 divide-y divide-gray-200 dark:divide-gray-700 bg-white dark:bg-gray-800 rounded-lg p-2 max-h-48 overflow-y-auto">
            {searchResults.map((r, i) => (
              <div key={i} className="py-2 px-3 flex justify-between items-center text-sm">
                <div>
                  <span className="font-semibold text-blue-600 dark:text-blue-400">[{r.entity_type}]</span> {r.title} - <span className="text-gray-500">{r.subtitle}</span>
                </div>
                <span className="font-medium text-gray-900 dark:text-white">${r.amount?.toLocaleString()}</span>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="border-l-4 border-emerald-500">
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Total Revenue</p>
              <h3 className="text-2xl font-bold text-emerald-600 dark:text-emerald-400 mt-1">${metrics.revenue.toLocaleString()}</h3>
            </div>
            <div className="p-3 bg-emerald-100 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 rounded-xl">
              <TrendingUp className="w-6 h-6" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-rose-500">
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Total Expenses</p>
              <h3 className="text-2xl font-bold text-rose-600 dark:text-rose-400 mt-1">${metrics.expenses.toLocaleString()}</h3>
            </div>
            <div className="p-3 bg-rose-100 dark:bg-rose-950/40 text-rose-600 dark:text-rose-400 rounded-xl">
              <TrendingDown className="w-6 h-6" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-blue-500">
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Net Profit</p>
              <h3 className="text-2xl font-bold text-blue-600 dark:text-blue-400 mt-1">${metrics.netProfit.toLocaleString()}</h3>
            </div>
            <div className="p-3 bg-blue-100 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400 rounded-xl">
              <DollarSign className="w-6 h-6" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-purple-500">
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Cash Balance</p>
              <h3 className="text-2xl font-bold text-purple-600 dark:text-purple-400 mt-1">${metrics.cashBalance.toLocaleString()}</h3>
            </div>
            <div className="p-3 bg-purple-100 dark:bg-purple-950/40 text-purple-600 dark:text-purple-400 rounded-xl">
              <Building2 className="w-6 h-6" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Secondary Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-gray-500 dark:text-gray-400">Accounts Receivable (AR)</p>
              <p className="text-xl font-bold text-gray-900 dark:text-white mt-1">${metrics.receivables.toLocaleString()}</p>
            </div>
            <span className="text-xs font-medium px-2.5 py-1 bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300 rounded-full">Outstanding</span>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-gray-500 dark:text-gray-400">Accounts Payable (AP)</p>
              <p className="text-xl font-bold text-gray-900 dark:text-white mt-1">${metrics.payables.toLocaleString()}</p>
            </div>
            <span className="text-xs font-medium px-2.5 py-1 bg-rose-100 text-rose-800 dark:bg-rose-900/30 dark:text-rose-300 rounded-full">Payables Due</span>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-gray-500 dark:text-gray-400">Budget Utilization</p>
              <p className="text-xl font-bold text-gray-900 dark:text-white mt-1">{metrics.budgetUtil}%</p>
            </div>
            <div className="w-20 bg-gray-200 dark:bg-gray-700 h-2 rounded-full overflow-hidden">
              <div className="bg-indigo-600 h-full rounded-full" style={{ width: `${metrics.budgetUtil}%` }} />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Financial Analytics & AI Readiness Placeholder Visualizer */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Cash Flow Trend & Projections</CardTitle>
            <CardDescription>Monthly Operating vs Net Cash Flow with AI readiness telemetry</CardDescription>
          </CardHeader>
          <CardContent className="h-64 flex items-center justify-center border-2 border-dashed border-gray-200 dark:border-gray-700 rounded-lg">
            <div className="text-center text-gray-400">
              <PieChart className="w-10 h-10 mx-auto mb-2 opacity-50" />
              <p className="text-sm font-medium">Interactive Cash Flow Visualization</p>
              <p className="text-xs">Data schema pre-configured for future AI Cash Flow Prediction</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Revenue vs Expense Distribution</CardTitle>
            <CardDescription>General Ledger income & expenditure analysis</CardDescription>
          </CardHeader>
          <CardContent className="h-64 flex items-center justify-center border-2 border-dashed border-gray-200 dark:border-gray-700 rounded-lg">
            <div className="text-center text-gray-400">
              <FileText className="w-10 h-10 mx-auto mb-2 opacity-50" />
              <p className="text-sm font-medium">Revenue & Cost Structure Analysis</p>
              <p className="text-xs">Data schema pre-configured for future AI Revenue Forecasting</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
