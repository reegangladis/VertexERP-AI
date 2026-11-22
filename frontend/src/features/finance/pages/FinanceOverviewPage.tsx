import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  DollarSign,
  TrendingUp,
  Receipt,
  CreditCard,
  Scale,
  Building2,
  FileSpreadsheet,
  ArrowUpRight,
  ArrowDownLeft,
  CheckCircle2,
  Lock,
  Plus,
  Layers,
  ArrowRight,
} from "lucide-react";
import { financeApi } from "../api/financeApi";
import { JournalEntry, Invoice, Bill, BankAccount } from "../types";

export const FinanceOverviewPage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [totalCash, setTotalCash] = useState(0);
  const [totalAR, setTotalAR] = useState(0);
  const [totalAP, setTotalAP] = useState(0);
  const [netIncome, setNetIncome] = useState(0);
  const [recentJournals, setRecentJournals] = useState<JournalEntry[]>([]);
  const [recentInvoices, setRecentInvoices] = useState<Invoice[]>([]);
  const [recentBills, setRecentBills] = useState<Bill[]>([]);
  const [bankAccounts, setBankAccounts] = useState<BankAccount[]>([]);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [banksRes, invoicesRes, billsRes, journalsRes, pnlRes] = await Promise.allSettled([
          financeApi.getBankAccounts(),
          financeApi.getInvoices({ page: 1, page_size: 5 }),
          financeApi.getBills({ page: 1, page_size: 5 }),
          financeApi.getJournalEntries({ page: 1, page_size: 5 }),
          financeApi.getProfitLoss(),
        ]);

        if (banksRes.status === "fulfilled") {
          const accounts = banksRes.value.items || [];
          setBankAccounts(accounts);
          const cash = accounts.reduce((acc, a) => acc + (Number(a.current_balance) || 0), 0);
          setTotalCash(cash);
        }

        if (invoicesRes.status === "fulfilled") {
          const invs = invoicesRes.value.items || [];
          setRecentInvoices(invs);
          const ar = invs.reduce((acc, i) => acc + (Number(i.amount_due) || 0), 0);
          setTotalAR(ar);
        }

        if (billsRes.status === "fulfilled") {
          const bls = billsRes.value.items || [];
          setRecentBills(bls);
          const ap = bls.reduce((acc, b) => acc + (Number(b.amount_due) || 0), 0);
          setTotalAP(ap);
        }

        if (journalsRes.status === "fulfilled") {
          setRecentJournals(journalsRes.value.items || []);
        }

        if (pnlRes.status === "fulfilled") {
          setNetIncome(Number(pnlRes.value.net_income) || 0);
        }
      } finally {
        setLoading(false);
      }
    }
    loadDashboard();
  }, []);

  const kpis = [
    {
      title: "Cash & Treasury Reserves",
      value: `$${totalCash.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      sub: `${bankAccounts.length} Active Bank Accounts`,
      icon: <DollarSign className="w-5 h-5 text-emerald-400" />,
      color: "from-emerald-500/20 to-emerald-500/5 text-emerald-300 border-emerald-500/20",
    },
    {
      title: "Accounts Receivable (AR)",
      value: `$${totalAR.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      sub: "Outstanding customer receivables",
      icon: <ArrowUpRight className="w-5 h-5 text-blue-400" />,
      color: "from-blue-500/20 to-blue-500/5 text-blue-300 border-blue-500/20",
    },
    {
      title: "Accounts Payable (AP)",
      value: `$${totalAP.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      sub: "Pending vendor obligations",
      icon: <ArrowDownLeft className="w-5 h-5 text-rose-400" />,
      color: "from-rose-500/20 to-rose-500/5 text-rose-300 border-rose-500/20",
    },
    {
      title: "Net Operating Income",
      value: `$${netIncome.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      sub: "Current financial year to date",
      icon: <TrendingUp className="w-5 h-5 text-purple-400" />,
      color: "from-purple-500/20 to-purple-500/5 text-purple-300 border-purple-500/20",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-3">
            <span className="p-2 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 text-white shadow-lg shadow-emerald-500/20">
              <Scale className="w-6 h-6" />
            </span>
            Finance & Accounting Operations
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Enterprise double-entry ledger, fiscal controls, receivables, payables, and GAAP reporting.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Link
            to="/finance/journals"
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium transition shadow-lg shadow-emerald-600/20"
          >
            <Plus className="w-4 h-4" />
            New Journal Entry
          </Link>
          <Link
            to="/finance/reports"
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-sm font-medium transition"
          >
            <FileSpreadsheet className="w-4 h-4" />
            Financial Statements
          </Link>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map((kpi, idx) => (
          <div
            key={idx}
            className={`p-5 rounded-2xl bg-gradient-to-b ${kpi.color} border backdrop-blur-md relative overflow-hidden transition hover:scale-[1.01]`}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">
                {kpi.title}
              </span>
              <div className="p-2 rounded-xl bg-slate-900/60 border border-slate-700/50">
                {kpi.icon}
              </div>
            </div>
            <div className="mt-4">
              <h2 className="text-2xl font-extrabold text-white tracking-tight">
                {loading ? "..." : kpi.value}
              </h2>
              <p className="text-xs text-slate-400 mt-1">{kpi.sub}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Links / Subsystem Nav */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {[
          { label: "Chart of Accounts", to: "/finance/accounts", icon: <Layers className="w-4 h-4 text-emerald-400" /> },
          { label: "Fiscal Periods", to: "/finance/fiscal", icon: <Lock className="w-4 h-4 text-amber-400" /> },
          { label: "Double-Entry Journals", to: "/finance/journals", icon: <Scale className="w-4 h-4 text-purple-400" /> },
          { label: "Sales Invoices (AR)", to: "/finance/invoices", icon: <Receipt className="w-4 h-4 text-blue-400" /> },
          { label: "Vendor Bills (AP)", to: "/finance/bills", icon: <CreditCard className="w-4 h-4 text-rose-400" /> },
          { label: "Bank Accounts", to: "/finance/banks", icon: <Building2 className="w-4 h-4 text-teal-400" /> },
        ].map((item, i) => (
          <Link
            key={i}
            to={item.to}
            className="flex items-center gap-3 p-3.5 rounded-xl bg-slate-900/60 hover:bg-slate-800/80 border border-slate-800 hover:border-slate-700 transition text-slate-300 text-sm font-medium group"
          >
            <span className="p-2 rounded-lg bg-slate-800 border border-slate-700/60 group-hover:scale-105 transition">
              {item.icon}
            </span>
            <span className="truncate">{item.label}</span>
          </Link>
        ))}
      </div>

      {/* Recent Ledger Activity & Invoices */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Journal Entries */}
        <div className="rounded-2xl bg-slate-900/60 border border-slate-800 p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-semibold text-white flex items-center gap-2">
              <Scale className="w-4 h-4 text-emerald-400" />
              Recent Journal Entries
            </h3>
            <Link to="/finance/journals" className="text-xs text-emerald-400 hover:underline flex items-center gap-1">
              View All <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          <div className="space-y-2.5">
            {loading ? (
              <div className="text-slate-500 text-sm py-4 text-center">Loading journals...</div>
            ) : recentJournals.length === 0 ? (
              <div className="text-slate-500 text-sm py-4 text-center">No posted journal entries yet.</div>
            ) : (
              recentJournals.map((je) => (
                <div
                  key={je.id}
                  className="flex items-center justify-between p-3 rounded-xl bg-slate-800/40 border border-slate-800 hover:border-slate-700/80 transition"
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={`p-1.5 rounded-lg text-xs font-semibold ${
                        je.status === "POSTED"
                          ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                          : je.status === "REVERSED"
                          ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                          : "bg-slate-700/40 text-slate-400"
                      }`}
                    >
                      {je.status}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-white font-mono">{je.entry_number}</p>
                      <p className="text-xs text-slate-400">{je.notes || je.entry_type} &bull; {je.posting_date}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold text-white">
                      ${Number(je.total_debit).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </p>
                    <p className="text-xs text-slate-400">{je.lines.length} balanced lines</p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Recent Invoices & Receivables */}
        <div className="rounded-2xl bg-slate-900/60 border border-slate-800 p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-semibold text-white flex items-center gap-2">
              <Receipt className="w-4 h-4 text-blue-400" />
              Recent Customer Invoices
            </h3>
            <Link to="/finance/invoices" className="text-xs text-blue-400 hover:underline flex items-center gap-1">
              View All <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          <div className="space-y-2.5">
            {loading ? (
              <div className="text-slate-500 text-sm py-4 text-center">Loading invoices...</div>
            ) : recentInvoices.length === 0 ? (
              <div className="text-slate-500 text-sm py-4 text-center">No customer invoices recorded yet.</div>
            ) : (
              recentInvoices.map((inv) => (
                <div
                  key={inv.id}
                  className="flex items-center justify-between p-3 rounded-xl bg-slate-800/40 border border-slate-800 hover:border-slate-700/80 transition"
                >
                  <div>
                    <p className="text-sm font-medium text-white font-mono">{inv.invoice_number}</p>
                    <p className="text-xs text-slate-400">Due {inv.due_date} &bull; {inv.status}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold text-white">
                      ${Number(inv.total_amount).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </p>
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                        inv.status === "PAID"
                          ? "bg-emerald-500/10 text-emerald-400"
                          : inv.status === "POSTED"
                          ? "bg-blue-500/10 text-blue-400"
                          : "bg-slate-700 text-slate-300"
                      }`}
                    >
                      {inv.status}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
