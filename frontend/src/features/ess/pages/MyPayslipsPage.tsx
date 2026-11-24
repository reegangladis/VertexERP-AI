import React, { useState } from "react";
import { formatCurrency, formatDate } from "@/lib/utils";
import { Button } from "@/components/ui/Button";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { FileText, Download, Printer, ShieldCheck, DollarSign } from "lucide-react";

export const MyPayslipsPage: React.FC = () => {
  const [selectedPayslipId, setSelectedPayslipId] = useState("PS-2026-10");

  const payslipsList = [
    { id: "PS-2026-10", month: "October 2026", gross: 7500.0, deductions: 1250.0, net: 6250.0, status: "PAID" },
    { id: "PS-2026-09", month: "September 2026", gross: 7500.0, deductions: 1250.0, net: 6250.0, status: "PAID" },
    { id: "PS-2026-08", month: "August 2026", gross: 7500.0, deductions: 1250.0, net: 6250.0, status: "PAID" },
    { id: "PS-2026-07", month: "July 2026", gross: 7200.0, deductions: 1200.0, net: 6000.0, status: "PAID" },
  ];

  const currentPayslip = {
    id: "PS-2026-10",
    month: "October 2026",
    employeeName: "Alex Rivera",
    employeeNumber: "EMP-00102",
    designation: "Senior Full Stack Engineer",
    department: "Enterprise Engineering",
    bankName: "JPMorgan Chase Bank, N.A.",
    accountNumber: "••••••••4812",
    panOrTaxId: "US-TAX-89274",
    payPeriod: "Oct 01, 2026 - Oct 31, 2026",
    payDate: "Oct 31, 2026",
    paidDays: 31,
    earnings: [
      { name: "Basic Salary", amount: 4500.0 },
      { name: "House Rent Allowance (HRA)", amount: 1800.0 },
      { name: "Medical Allowance", amount: 400.0 },
      { name: "Special Professional Allowance", amount: 800.0 },
    ],
    deductions: [
      { name: "Provident Fund (Employee 12%)", amount: 540.0 },
      { name: "Income Tax Withholding (TDS)", amount: 650.0 },
      { name: "Professional Tax", amount: 60.0 },
    ],
  };

  const totalEarnings = currentPayslip.earnings.reduce((acc, curr) => acc + curr.amount, 0);
  const totalDeductions = currentPayslip.deductions.reduce((acc, curr) => acc + curr.amount, 0);
  const netPayable = totalEarnings - totalDeductions;

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <FileText className="w-5 h-5 text-brand-400" />
            <span>My Payslips & Salary Breakdown</span>
          </h1>
          <p className="text-xs text-slate-400">
            View detailed monthly remuneration, itemized allowances, tax withholdings, and net pay.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => window.print()}
            className="text-xs flex items-center gap-1.5"
          >
            <Printer className="w-3.5 h-3.5" />
            <span>Print</span>
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={() => alert("Downloading PDF payslip...")}
            className="text-xs flex items-center gap-1.5"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download PDF</span>
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Left Column: Months list */}
        <div className="lg:col-span-1 space-y-2">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
            Available Pay Periods
          </h3>
          {payslipsList.map((p) => (
            <div
              key={p.id}
              onClick={() => setSelectedPayslipId(p.id)}
              className={`p-3.5 rounded-xl border transition-all cursor-pointer text-xs space-y-1 ${
                selectedPayslipId === p.id
                  ? "border-brand-500 bg-brand-500/10 text-slate-100"
                  : "border-slate-800 bg-slate-900/60 hover:bg-slate-850 text-slate-400"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-200">{p.month}</span>
                <StatusBadge status={p.status} />
              </div>
              <div className="text-[11px] text-slate-500 flex justify-between">
                <span>Net Pay:</span>
                <span className="font-semibold text-emerald-400">{formatCurrency(p.net)}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Right Column: Detailed Payslip Paper Layout */}
        <div className="lg:col-span-3 rounded-2xl border border-slate-800 bg-slate-900/80 backdrop-blur-md p-6 sm:p-8 space-y-6">
          {/* Header of Payslip */}
          <div className="flex flex-col sm:flex-row justify-between items-start gap-4 border-b border-slate-800 pb-6">
            <div>
              <div className="text-xs font-bold uppercase tracking-wider text-brand-400">
                VertexERP Enterprise Inc.
              </div>
              <h2 className="text-xl font-bold text-slate-100 mt-1">
                Payslip for {currentPayslip.month}
              </h2>
              <div className="text-xs text-slate-400 mt-0.5">Pay Date: {currentPayslip.payDate}</div>
            </div>

            <div className="text-right sm:text-right">
              <div className="text-xs text-slate-400">Total Net Take-Home:</div>
              <div className="text-2xl font-bold text-emerald-400">{formatCurrency(netPayable)}</div>
              <span className="inline-block mt-1 px-2 py-0.5 text-[10px] font-bold rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                Direct Deposit Cleared
              </span>
            </div>
          </div>

          {/* Employee & Bank Info Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 text-xs">
            <div>
              <span className="text-slate-400 text-[10px] uppercase">Employee Name</span>
              <div className="font-semibold text-slate-200">{currentPayslip.employeeName}</div>
            </div>
            <div>
              <span className="text-slate-400 text-[10px] uppercase">Employee ID</span>
              <div className="font-semibold text-slate-200">{currentPayslip.employeeNumber}</div>
            </div>
            <div>
              <span className="text-slate-400 text-[10px] uppercase">Designation</span>
              <div className="font-semibold text-slate-200">{currentPayslip.designation}</div>
            </div>
            <div>
              <span className="text-slate-400 text-[10px] uppercase">Department</span>
              <div className="font-semibold text-slate-200">{currentPayslip.department}</div>
            </div>
            <div>
              <span className="text-slate-400 text-[10px] uppercase">Disbursed Account</span>
              <div className="font-semibold text-slate-200">{currentPayslip.accountNumber}</div>
            </div>
            <div>
              <span className="text-slate-400 text-[10px] uppercase">Paid Days</span>
              <div className="font-semibold text-slate-200">{currentPayslip.paidDays} Days</div>
            </div>
          </div>

          {/* Earnings & Deductions Tables */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Earnings */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center justify-between border-b border-slate-800 pb-2">
                <span>Earnings Breakdown</span>
                <span>Amount</span>
              </h4>
              <div className="space-y-2 text-xs">
                {currentPayslip.earnings.map((e, idx) => (
                  <div key={idx} className="flex justify-between text-slate-300">
                    <span>{e.name}</span>
                    <span className="font-semibold text-slate-200">{formatCurrency(e.amount)}</span>
                  </div>
                ))}
              </div>
              <div className="pt-3 border-t border-slate-800 flex justify-between text-xs font-bold text-slate-100">
                <span>Total Gross Earnings</span>
                <span className="text-emerald-400">{formatCurrency(totalEarnings)}</span>
              </div>
            </div>

            {/* Deductions */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-rose-400 flex items-center justify-between border-b border-slate-800 pb-2">
                <span>Deductions & Taxes</span>
                <span>Amount</span>
              </h4>
              <div className="space-y-2 text-xs">
                {currentPayslip.deductions.map((d, idx) => (
                  <div key={idx} className="flex justify-between text-slate-300">
                    <span>{d.name}</span>
                    <span className="font-semibold text-rose-400">-{formatCurrency(d.amount)}</span>
                  </div>
                ))}
              </div>
              <div className="pt-3 border-t border-slate-800 flex justify-between text-xs font-bold text-slate-100">
                <span>Total Deductions</span>
                <span className="text-rose-400">-{formatCurrency(totalDeductions)}</span>
              </div>
            </div>
          </div>

          {/* Net Calculation Bar */}
          <div className="p-4 rounded-xl bg-gradient-to-r from-emerald-950/40 to-slate-900 border border-emerald-500/30 flex items-center justify-between text-sm">
            <span className="font-semibold text-slate-200">Net Disbursed Take-Home</span>
            <span className="text-xl font-bold text-emerald-400">{formatCurrency(netPayable)}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
