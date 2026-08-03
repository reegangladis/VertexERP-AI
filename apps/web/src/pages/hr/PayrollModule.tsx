import React, { useState } from 'react';
import {
  DollarSign,
  CreditCard,
  CheckCircle2,
  XCircle,
  Clock,
  Plus,
  FileText,
  Download,
  UserCheck,
  TrendingUp,
  Layers,
  Award,
  ShieldCheck,
  Briefcase,
  Search,
  Filter,
  Eye,
  Check,
  X,
  FileSpreadsheet,
} from 'lucide-react';

const mockStructures = [
  { id: 'st1', name: 'Executive Leadership Grade A', code: 'EXEC-A', currency: 'USD', effectiveFrom: '2026-01-01', status: 'Active' },
  { id: 'st2', name: 'Engineering & Tech Grade B', code: 'ENG-B', currency: 'USD', effectiveFrom: '2026-01-01', status: 'Active' },
];

const mockComponents = [
  { name: 'Basic Pay', type: 'Basic', nature: 'Earning', method: '50% of CTC', taxable: true },
  { name: 'House Rent Allowance (HRA)', type: 'HRA', nature: 'Earning', method: '40% of Basic', taxable: true },
  { name: 'Special Allowance', type: 'Allowance', nature: 'Earning', method: 'Balance CTC', taxable: true },
  { name: 'Provident Fund (PF)', type: 'PF', nature: 'Deduction', method: '12% of Basic', taxable: false },
  { name: 'Professional Tax (PT)', type: 'Professional Tax', nature: 'Deduction', method: 'Statutory Flat', taxable: false },
  { name: 'Income Tax (TDS)', type: 'Income Tax', nature: 'Deduction', method: 'Regime Formula', taxable: false },
];

const mockPayrollRuns = [
  { id: 'pr1', period: 'August 2026', month: 8, year: 2026, status: 'Approved', totalGross: '$145,200.00', totalNet: '$112,400.00', employees: 28, processedAt: '2026-08-01' },
  { id: 'pr2', period: 'July 2026', month: 7, year: 2026, status: 'Completed', totalGross: '$142,000.00', totalNet: '$109,800.00', employees: 27, processedAt: '2026-07-01' },
];

const mockPayslips = [
  { id: 'ps1', employee: 'John Doe (EMP-102)', gross: 5042.19, deductions: 650.0, net: 4392.19, status: 'Paid', date: '2026-08-01' },
  { id: 'ps2', employee: 'Alice Smith (EMP-105)', gross: 4200.0, deductions: 580.0, net: 3620.0, status: 'Paid', date: '2026-08-01' },
];

const mockLoans = [
  { id: 'ln1', employee: 'John Doe (EMP-102)', type: 'Emergency Advance', principal: '$2,400.00', balance: '$1,600.00', emi: '$200.00', status: 'Active' },
  { id: 'ln2', employee: 'Robert Chen (EMP-110)', type: 'Housing Loan Assistance', principal: '$10,000.00', balance: '$8,500.00', emi: '$500.00', status: 'Active' },
];

export function PayrollModule() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'runs' | 'payslips' | 'structures' | 'assignments' | 'loans' | 'tax'>('dashboard');
  const [isGenerateModalOpen, setIsGenerateModalOpen] = useState(false);
  const [selectedMonth, setSelectedMonth] = useState(8);
  const [selectedYear, setSelectedYear] = useState(2026);

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-emerald-950 via-slate-900 to-emerald-950 rounded-xl p-6 text-white shadow-xl border border-emerald-900/40">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-emerald-400 font-mono text-xs uppercase tracking-wider font-semibold mb-1">
              <DollarSign className="w-4 h-4" /> Phase 7 — Enterprise Payroll & Compensation Platform
            </div>
            <h1 className="text-2xl font-bold tracking-tight">Payroll & Compensation Engine</h1>
            <p className="text-sm text-slate-300 mt-1">
              Automated monthly CTC calculation, statutory tax withholding, overtime earnings, loan EMI deductions & PDF payslips.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsGenerateModalOpen(true)}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg shadow-md transition flex items-center gap-2"
            >
              <Plus className="w-4 h-4" /> Run Monthly Payroll
            </button>
          </div>
        </div>

        {/* Sub-Navigation Tabs */}
        <div className="flex items-center gap-2 mt-6 overflow-x-auto border-t border-slate-800/80 pt-4 scrollbar-none">
          {[
            { id: 'dashboard', label: 'Payroll Overview', icon: <TrendingUp className="w-3.5 h-3.5" /> },
            { id: 'runs', label: 'Payroll Runs & Approvals', icon: <FileSpreadsheet className="w-3.5 h-3.5" /> },
            { id: 'payslips', label: 'Employee Payslips', icon: <FileText className="w-3.5 h-3.5" /> },
            { id: 'structures', label: 'Salary Structures & Components', icon: <Layers className="w-3.5 h-3.5" /> },
            { id: 'assignments', label: 'CTC Salary Assignments', icon: <Briefcase className="w-3.5 h-3.5" /> },
            { id: 'loans', label: 'Loans & EMIs', icon: <CreditCard className="w-3.5 h-3.5" /> },
            { id: 'tax', label: 'Tax Profiles', icon: <ShieldCheck className="w-3.5 h-3.5" /> },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition flex items-center gap-1.5 whitespace-nowrap ${
                activeTab === tab.id
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* 1. OVERVIEW VIEW */}
      {activeTab === 'dashboard' && (
        <div className="space-y-6">
          {/* KPI Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-card p-5 rounded-xl border border-border shadow-sm space-y-2">
              <div className="flex items-center justify-between text-muted-foreground">
                <span className="text-xs font-medium">Total Monthly Payroll Cost</span>
                <DollarSign className="w-4 h-4 text-emerald-500" />
              </div>
              <h3 className="text-2xl font-extrabold text-foreground">$145,200.00</h3>
              <p className="text-[10px] text-emerald-500 font-mono">+2.4% vs last month</p>
            </div>

            <div className="bg-card p-5 rounded-xl border border-border shadow-sm space-y-2">
              <div className="flex items-center justify-between text-muted-foreground">
                <span className="text-xs font-medium">Employees Paid</span>
                <UserCheck className="w-4 h-4 text-sky-500" />
              </div>
              <h3 className="text-2xl font-extrabold text-foreground">28 Active</h3>
              <p className="text-[10px] text-muted-foreground font-mono">100% Processed</p>
            </div>

            <div className="bg-card p-5 rounded-xl border border-border shadow-sm space-y-2">
              <div className="flex items-center justify-between text-muted-foreground">
                <span className="text-xs font-medium">Total Statutory Deductions</span>
                <CreditCard className="w-4 h-4 text-amber-500" />
              </div>
              <h3 className="text-2xl font-extrabold text-foreground">$32,800.00</h3>
              <p className="text-[10px] text-amber-500 font-mono">PF, PT & TDS Tax</p>
            </div>

            <div className="bg-card p-5 rounded-xl border border-border shadow-sm space-y-2">
              <div className="flex items-center justify-between text-muted-foreground">
                <span className="text-xs font-medium">Active Loans EMI Balance</span>
                <Award className="w-4 h-4 text-purple-500" />
              </div>
              <h3 className="text-2xl font-extrabold text-foreground">$10,100.00</h3>
              <p className="text-[10px] text-purple-400 font-mono">2 Active Loan Accounts</p>
            </div>
          </div>

          {/* Grid Layout: Recent Payroll Runs & Salary Components */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Recent Payroll Runs */}
            <div className="lg:col-span-2 bg-card p-5 rounded-xl border border-border shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
                  <FileSpreadsheet className="w-4 h-4 text-emerald-500" /> Recent Payroll Runs
                </h3>
                <span className="text-xs text-emerald-500 font-mono font-semibold">2026 Financial Period</span>
              </div>
              <div className="space-y-3">
                {mockPayrollRuns.map((pr) => (
                  <div key={pr.id} className="p-4 bg-secondary/20 rounded-xl border border-border/60 flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="text-xs font-bold text-foreground">{pr.period}</p>
                        <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-500 text-[10px] font-bold rounded">
                          {pr.status}
                        </span>
                      </div>
                      <p className="text-[11px] text-muted-foreground mt-0.5">
                        {pr.employees} Employees — Gross: <span className="font-semibold text-foreground">{pr.totalGross}</span> | Net: <span className="font-semibold text-emerald-500">{pr.totalNet}</span>
                      </p>
                    </div>
                    <button className="px-3 py-1.5 bg-secondary text-foreground text-xs font-semibold rounded-lg hover:bg-secondary/80 flex items-center gap-1">
                      <Eye className="w-3.5 h-3.5" /> View Payslips
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* Configured Salary Components */}
            <div className="bg-card p-5 rounded-xl border border-border shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
                  <Layers className="w-4 h-4 text-sky-500" /> Salary Breakdown Rules
                </h3>
              </div>
              <div className="space-y-2">
                {mockComponents.map((c, idx) => (
                  <div key={idx} className="p-2.5 bg-secondary/20 rounded-lg border border-border/50 flex items-center justify-between text-xs">
                    <div>
                      <p className="font-semibold text-foreground">{c.name}</p>
                      <p className="text-[10px] text-muted-foreground">{c.method}</p>
                    </div>
                    <span className={`px-2 py-0.5 text-[10px] font-bold rounded ${
                      c.nature === 'Earning' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-rose-500/10 text-rose-500'
                    }`}>
                      {c.nature}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 2. PAYSLIPS VIEW */}
      {activeTab === 'payslips' && (
        <div className="bg-card p-6 rounded-xl border border-border shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-foreground">Generated Employee Payslips</h3>
            <span className="text-xs text-muted-foreground font-mono">August 2026 Period</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-secondary/40 text-muted-foreground font-mono uppercase text-[10px]">
                <tr>
                  <th className="p-3">Employee</th>
                  <th className="p-3">Gross Salary</th>
                  <th className="p-3">Total Deductions</th>
                  <th className="p-3">Net Payable Salary</th>
                  <th className="p-3">Payment Status</th>
                  <th className="p-3 text-right">Download</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/50">
                {mockPayslips.map((ps) => (
                  <tr key={ps.id} className="hover:bg-secondary/10">
                    <td className="p-3 font-semibold text-foreground">{ps.employee}</td>
                    <td className="p-3 font-mono">${ps.gross.toFixed(2)}</td>
                    <td className="p-3 font-mono text-rose-500">${ps.deductions.toFixed(2)}</td>
                    <td className="p-3 font-bold text-emerald-500 font-mono">${ps.net.toFixed(2)}</td>
                    <td className="p-3">
                      <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-500 text-[10px] font-semibold rounded">
                        {ps.status}
                      </span>
                    </td>
                    <td className="p-3 text-right">
                      <button className="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-500 text-white text-[10px] font-semibold rounded transition flex items-center gap-1 ml-auto">
                        <Download className="w-3 h-3" /> PDF Payslip
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* GENERATE PAYROLL MODAL */}
      {isGenerateModalOpen && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-card w-full max-w-md rounded-2xl border border-border shadow-2xl p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <h3 className="text-base font-bold text-foreground flex items-center gap-2">
                <FileSpreadsheet className="w-5 h-5 text-emerald-500" /> Run Monthly Payroll
              </h3>
              <button onClick={() => setIsGenerateModalOpen(false)} className="text-muted-foreground hover:text-foreground">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold mb-1">Select Month</label>
                <select
                  value={selectedMonth}
                  onChange={(e) => setSelectedMonth(Number(e.target.value))}
                  className="w-full p-2.5 rounded-lg border border-border bg-background text-foreground"
                >
                  <option value={8}>August (08)</option>
                  <option value={9}>September (09)</option>
                  <option value={10}>October (10)</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold mb-1">Financial Year</label>
                <input
                  type="number"
                  value={selectedYear}
                  onChange={(e) => setSelectedYear(Number(e.target.value))}
                  className="w-full p-2.5 rounded-lg border border-border bg-background text-foreground"
                />
              </div>

              <div className="p-3 bg-emerald-500/10 rounded-lg border border-emerald-500/20 text-emerald-400 font-mono text-[11px] space-y-1">
                <p className="font-bold">Automated Calculation Checklist:</p>
                <p>✔ Core CTC Salary Assignments</p>
                <p>✔ Phase 5 Overtime Hours & Attendance</p>
                <p>✔ Phase 6 Unpaid Leave Deductions</p>
                <p>✔ Loan EMI Deductions & Statutory TDS</p>
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-3 border-t border-border">
              <button
                onClick={() => setIsGenerateModalOpen(false)}
                className="px-4 py-2 bg-secondary text-foreground text-xs font-semibold rounded-lg hover:bg-secondary/80"
              >
                Cancel
              </button>
              <button
                onClick={() => setIsGenerateModalOpen(false)}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg shadow transition"
              >
                Execute Payroll Calculation
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default PayrollModule;
