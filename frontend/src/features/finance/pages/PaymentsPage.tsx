import React, { useEffect, useState } from "react";
import {
  DollarSign,
  Plus,
  Search,
  CheckCircle2,
  AlertCircle,
  ArrowUpRight,
  ArrowDownLeft,
  Building2,
  Receipt,
  CreditCard,
  Send,
} from "lucide-react";
import { financeApi } from "../api/financeApi";
import { BankAccount, CustomerParty, Invoice, Payment, VendorParty } from "../types";

export const PaymentsPage: React.FC = () => {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [customers, setCustomers] = useState<CustomerParty[]>([]);
  const [vendors, setVendors] = useState<VendorParty[]>([]);
  const [bankAccounts, setBankAccounts] = useState<BankAccount[]>([]);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [paymentTypeFilter, setPaymentTypeFilter] = useState<string>("ALL");
  const [showModal, setShowModal] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Form State
  const [paymentType, setPaymentType] = useState<"RECEIPT" | "DISBURSEMENT">("RECEIPT");
  const [partnerId, setPartnerId] = useState("");
  const [bankAccountId, setBankAccountId] = useState("");
  const [amount, setAmount] = useState("1000");
  const [paymentDate, setPaymentDate] = useState(new Date().toISOString().split("T")[0]);
  const [paymentMethod, setPaymentMethod] = useState("BANK");
  const [reference, setReference] = useState("");
  const [selectedInvoiceId, setSelectedInvoiceId] = useState("");

  const loadData = async () => {
    try {
      setLoading(true);
      const [payRes, custRes, vendRes, bankRes, invRes] = await Promise.all([
        financeApi.getPayments({ page: 1, page_size: 100 }),
        financeApi.getCustomers(),
        financeApi.getVendors(),
        financeApi.getBankAccounts(),
        financeApi.getInvoices({ status: "POSTED", page: 1, page_size: 100 }),
      ]);
      setPayments(payRes.items || []);
      setCustomers(custRes.items || []);
      setVendors(vendRes.items || []);
      const banks = bankRes.items || [];
      setBankAccounts(banks);
      if (banks.length > 0 && !bankAccountId) {
        setBankAccountId(banks[0].id);
      }
      setInvoices(invRes.items || []);
    } catch (err: any) {
      setErrorMsg("Failed to load payments.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateAndPost = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!partnerId) {
      setErrorMsg("Please select a partner.");
      return;
    }
    setErrorMsg(null);
    try {
      const payAmount = parseFloat(amount) || 0;
      const allocations = selectedInvoiceId
        ? [{ invoice_id: selectedInvoiceId, allocated_amount: payAmount }]
        : [];

      const pay = await financeApi.createPayment({
        payment_type: paymentType,
        partner_type: paymentType === "RECEIPT" ? "CUSTOMER" : "VENDOR",
        partner_id: partnerId,
        bank_account_id: bankAccountId || undefined,
        payment_date: paymentDate,
        payment_method: paymentMethod,
        currency: "USD",
        amount: payAmount.toString(),
        reference,
        allocations,
      });

      // Post the payment to update GL, Bank Balance, and Reconcile Invoices
      await financeApi.postPayment(pay.id);
      setShowModal(false);
      setReference("");
      setSelectedInvoiceId("");
      loadData();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to process payment.");
    }
  };

  const handlePostPayment = async (paymentId: string) => {
    try {
      await financeApi.postPayment(paymentId);
      loadData();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to post payment.");
    }
  };

  const filteredPayments = payments.filter((p) => {
    const matchesSearch =
      p.payment_number.toLowerCase().includes(search.toLowerCase()) ||
      (p.reference || "").toLowerCase().includes(search.toLowerCase());
    const matchesType = paymentTypeFilter === "ALL" || p.payment_type === paymentTypeFilter;
    return matchesSearch && matchesType;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-3">
            <span className="p-2 rounded-xl bg-teal-500/20 border border-teal-500/30 text-teal-400">
              <DollarSign className="w-6 h-6" />
            </span>
            Payments & Document Allocations
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Customer collections and vendor disbursements with automated document matching and bank reconciliation.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-500 text-white text-sm font-semibold transition shadow-lg shadow-teal-600/20"
        >
          <Plus className="w-4 h-4" />
          Record Payment
        </button>
      </div>

      {/* Filters Bar */}
      <div className="flex flex-col sm:flex-row gap-3 items-center justify-between p-4 rounded-2xl bg-slate-900/60 border border-slate-800">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Search payment number or ref..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-slate-800/80 border border-slate-700 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-teal-500"
          />
        </div>

        <div className="flex items-center gap-1.5 overflow-x-auto w-full sm:w-auto">
          {["ALL", "RECEIPT", "DISBURSEMENT"].map((t) => (
            <button
              key={t}
              onClick={() => setPaymentTypeFilter(t)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                paymentTypeFilter === t
                  ? "bg-teal-600 text-white shadow-sm"
                  : "bg-slate-800/60 text-slate-400 hover:text-slate-200 border border-slate-700/50"
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm flex items-center gap-3">
          <AlertCircle className="w-5 h-5 shrink-0" />
          {errorMsg}
        </div>
      )}

      {/* Payments Table */}
      <div className="rounded-2xl bg-slate-900/60 border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-800/50 text-slate-400 font-medium border-b border-slate-800 text-xs uppercase tracking-wider">
              <tr>
                <th className="px-6 py-4">Payment #</th>
                <th className="px-6 py-4">Type</th>
                <th className="px-6 py-4">Date / Method</th>
                <th className="px-6 py-4">Amount</th>
                <th className="px-6 py-4">Allocated / Unallocated</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50 text-slate-300">
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-6 py-10 text-center text-slate-500">
                    Loading payments...
                  </td>
                </tr>
              ) : filteredPayments.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-10 text-center text-slate-500">
                    No payment records found.
                  </td>
                </tr>
              ) : (
                filteredPayments.map((p) => (
                  <tr key={p.id} className="hover:bg-slate-800/30 transition">
                    <td className="px-6 py-4 font-mono font-bold text-white">{p.payment_number}</td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold border ${
                          p.payment_type === "RECEIPT"
                            ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                            : "bg-rose-500/10 text-rose-400 border-rose-500/20"
                        }`}
                      >
                        {p.payment_type === "RECEIPT" ? (
                          <ArrowDownLeft className="w-3.5 h-3.5" />
                        ) : (
                          <ArrowUpRight className="w-3.5 h-3.5" />
                        )}
                        {p.payment_type}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-400">
                      {p.payment_date} &bull; <span className="text-slate-300">{p.payment_method}</span>
                    </td>
                    <td className="px-6 py-4 font-mono font-semibold text-white">
                      ${Number(p.amount).toFixed(2)}
                    </td>
                    <td className="px-6 py-4 font-mono text-xs">
                      <span className="text-emerald-400">${Number(p.allocated_amount).toFixed(2)}</span> /{" "}
                      <span className="text-slate-400">${Number(p.unallocated_amount).toFixed(2)}</span>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center px-2.5 py-1 rounded-md text-xs font-semibold border ${
                          p.status === "POSTED"
                            ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                            : "bg-slate-700 text-slate-300 border-slate-600"
                        }`}
                      >
                        {p.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      {p.status === "DRAFT" && (
                        <button
                          onClick={() => handlePostPayment(p.id)}
                          className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-teal-600 hover:bg-teal-500 text-white transition inline-flex items-center gap-1.5"
                        >
                          <Send className="w-3 h-3" /> Post Payment
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Record Payment Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <DollarSign className="w-5 h-5 text-teal-400" />
              Record Financial Payment
            </h3>

            <form onSubmit={handleCreateAndPost} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-medium text-slate-400 block mb-1">Transaction Flow</label>
                  <select
                    value={paymentType}
                    onChange={(e) => {
                      setPaymentType(e.target.value as any);
                      setPartnerId("");
                    }}
                    className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-teal-500"
                  >
                    <option value="RECEIPT">Customer Receipt (AR)</option>
                    <option value="DISBURSEMENT">Vendor Disbursement (AP)</option>
                  </select>
                </div>

                <div>
                  <label className="text-xs font-medium text-slate-400 block mb-1">
                    {paymentType === "RECEIPT" ? "Customer" : "Vendor"}
                  </label>
                  <select
                    required
                    value={partnerId}
                    onChange={(e) => setPartnerId(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-teal-500"
                  >
                    <option value="">Select Party...</option>
                    {paymentType === "RECEIPT"
                      ? customers.map((c) => (
                          <option key={c.id} value={c.id}>
                            {c.code} - {c.name}
                          </option>
                        ))
                      : vendors.map((v) => (
                          <option key={v.id} value={v.id}>
                            {v.code} - {v.name}
                          </option>
                        ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-medium text-slate-400 block mb-1">Payment Amount ($)</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0.01"
                    required
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-teal-500"
                  />
                </div>

                <div>
                  <label className="text-xs font-medium text-slate-400 block mb-1">Treasury / Bank Account</label>
                  <select
                    value={bankAccountId}
                    onChange={(e) => setBankAccountId(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-teal-500"
                  >
                    {bankAccounts.map((b) => (
                      <option key={b.id} value={b.id}>
                        {b.bank_name} - {b.account_name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-medium text-slate-400 block mb-1">Payment Date</label>
                  <input
                    type="date"
                    required
                    value={paymentDate}
                    onChange={(e) => setPaymentDate(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-teal-500"
                  />
                </div>

                <div>
                  <label className="text-xs font-medium text-slate-400 block mb-1">Payment Method</label>
                  <select
                    value={paymentMethod}
                    onChange={(e) => setPaymentMethod(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-teal-500"
                  >
                    <option value="BANK">Wire / Bank Transfer</option>
                    <option value="CHECK">Check</option>
                    <option value="CARD">Credit / Debit Card</option>
                    <option value="CASH">Cash</option>
                  </select>
                </div>
              </div>

              {paymentType === "RECEIPT" && (
                <div>
                  <label className="text-xs font-medium text-slate-400 block mb-1">Allocate to Open Invoice (Optional)</label>
                  <select
                    value={selectedInvoiceId}
                    onChange={(e) => setSelectedInvoiceId(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-teal-500"
                  >
                    <option value="">No automatic allocation (Unallocated Receipt)</option>
                    {invoices.map((inv) => (
                      <option key={inv.id} value={inv.id}>
                        {inv.invoice_number} - Balance Due: ${Number(inv.amount_due).toFixed(2)}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <div>
                <label className="text-xs font-medium text-slate-400 block mb-1">Payment Reference / Cheque #</label>
                <input
                  type="text"
                  placeholder="e.g. WIRE-881920"
                  value={reference}
                  onChange={(e) => setReference(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-teal-500"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-medium transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-teal-600 hover:bg-teal-500 text-white text-sm font-semibold transition"
                >
                  Post Payment
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
