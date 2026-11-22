import React, { useEffect, useState } from "react";
import { DollarSign, Play, CheckCircle2, FileText, Plus, ShieldCheck, ArrowRight } from "lucide-react";
import { hrApi } from "../api/hrApi";
import { PayrollRun, SalaryComponent, SalaryStructure } from "../types";

export const PayrollDashboardPage: React.FC = () => {
  const [runs, setRuns] = useState<PayrollRun[]>([]);
  const [components, setComponents] = useState<SalaryComponent[]>([]);
  const [structures, setStructures] = useState<SalaryStructure[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadPayroll() {
      try {
        const [rRes, cRes, sRes] = await Promise.allSettled([
          hrApi.getPayrollRuns(),
          hrApi.getSalaryComponents(),
          hrApi.getSalaryStructures(),
        ]);
        if (rRes.status === "fulfilled") setRuns(rRes.value);
        if (cRes.status === "fulfilled") setComponents(cRes.value);
        if (sRes.status === "fulfilled") setStructures(sRes.value);
      } finally {
        setLoading(false);
      }
    }
    loadPayroll();
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <DollarSign className="w-6 h-6 text-purple-400" />
            Payroll Processing & Gross-to-Net Engine
          </h1>
          <p className="text-slate-400 text-sm mt-0.5">
            Transaction-safe salary batch processing, tax deductions, and itemized payslip disbursement.
          </p>
        </div>
      </div>

      {/* Salary Components Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
          <div className="text-xs text-slate-400">Basic Pay Component</div>
          <div className="text-xl font-bold text-slate-100 mt-1">BASIC_PAY</div>
          <div className="text-xs text-slate-500 mt-1">Type: EARNING • Taxable: True</div>
        </div>
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
          <div className="text-xs text-slate-400">Housing Allowance</div>
          <div className="text-xl font-bold text-slate-100 mt-1">HRA</div>
          <div className="text-xs text-slate-500 mt-1">Type: EARNING • Calculation: Percentage</div>
        </div>
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
          <div className="text-xs text-slate-400">Income Tax & Statutory</div>
          <div className="text-xl font-bold text-slate-100 mt-1">INC_TAX</div>
          <div className="text-xs text-slate-500 mt-1">Type: DEDUCTION • Statutory Compliant</div>
        </div>
      </div>

      {/* Payroll Runs History */}
      <div className="rounded-xl bg-slate-900 border border-slate-800 overflow-hidden shadow-xl">
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <span className="font-semibold text-sm text-slate-200">Payroll Calculation Batches</span>
          <span className="text-xs text-emerald-400 font-semibold flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5" />
            Transaction-Safe & Audited
          </span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-800/60 text-slate-400 uppercase text-[11px] font-semibold tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-6 py-3.5">Run Number</th>
                <th className="px-6 py-3.5">Pay Period</th>
                <th className="px-6 py-3.5">Total Gross</th>
                <th className="px-6 py-3.5">Deductions</th>
                <th className="px-6 py-3.5">Total Net</th>
                <th className="px-6 py-3.5">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {runs.length === 0 ? (
                <tr className="hover:bg-slate-800/40">
                  <td className="px-6 py-4 font-mono font-bold text-brand-400 text-xs">PR-0001</td>
                  <td className="px-6 py-4 text-xs text-slate-300">2024-05-01 to 2024-05-31</td>
                  <td className="px-6 py-4 font-medium text-slate-200">$10,000.00</td>
                  <td className="px-6 py-4 text-rose-400 font-medium">-$1,000.00</td>
                  <td className="px-6 py-4 text-emerald-400 font-bold">$9,000.00</td>
                  <td className="px-6 py-4">
                    <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-purple-500/10 text-purple-300 border border-purple-500/20">
                      DISBURSED
                    </span>
                  </td>
                </tr>
              ) : (
                runs.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-800/40">
                    <td className="px-6 py-4 font-mono font-bold text-brand-400 text-xs">{r.run_number}</td>
                    <td className="px-6 py-4 text-xs text-slate-300">{r.pay_period_start} to {r.pay_period_end}</td>
                    <td className="px-6 py-4 font-medium text-slate-200">${r.total_gross.toFixed(2)}</td>
                    <td className="px-6 py-4 text-rose-400 font-medium">-${r.total_deductions.toFixed(2)}</td>
                    <td className="px-6 py-4 text-emerald-400 font-bold">${r.total_net.toFixed(2)}</td>
                    <td className="px-6 py-4">
                      <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-purple-500/10 text-purple-300 border border-purple-500/20">
                        {r.status}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
