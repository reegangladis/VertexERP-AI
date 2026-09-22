import React, { useEffect, useState } from "react";
import {
  Receipt,
  Plus,
  Search,
  CheckCircle2,
  AlertCircle,
  FileText,
  User,
  Send,
  DollarSign,
  Trash2,
} from "lucide-react";
import { financeApi } from "../api/financeApi";
import { Account, CustomerParty, Invoice, InvoiceLine } from "../types";

export const InvoicesPage: React.FC = () => {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [customers, setCustomers] = useState<CustomerParty[]>([]);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedStatus, setSelectedStatus] = useState<string>("ALL");
  const [showModal, setShowModal] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Form State
  const [customerId, setCustomerId] = useState("");
  const [issueDate, setIssueDate] = useState(new Date().toISOString().split("T")[0]);
  const [dueDate, setDueDate] = useState(
    new Date(Date.now() + 30 * 86400000).toISOString().split("T")[0]
  );
  const [lines, setLines] = useState<Array<{ description: string; account_id: string; quantity: number; unit_price: number; tax_rate: number }>>([
    { description: "Standard Consulting Service", account_id: "", quantity: 1, unit_price: 1000, tax_rate: 0 },
  ]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [invRes, custRes, acctRes] = await Promise.all([
        financeApi.getInvoices({ page: 1, page_size: 100 }),
        financeApi.getCustomers(),
        financeApi.getAccounts({ account_type: "REVENUE", page: 1, page_size: 100 }),
      ]);
      setInvoices(invRes.items || []);
      setCustomers(custRes.items || []);
      setAccounts(acctRes.items || []);
    } catch (err: any) {
      setErrorMsg("Failed to load invoices.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleAddLine = () => {
    setLines([...lines, { description: "", account_id: "", quantity: 1, unit_price: 0, tax_rate: 0 }]);
  };

  const handleRemoveLine = (idx: number) => {
    if (lines.length <= 1) return;
    setLines(lines.filter((_, i) => i !== idx));
  };

  const calculateSubtotal = () =>
    lines.reduce((acc, l) => acc + (l.quantity * l.unit_price || 0), 0);

  const calculateTax = () =>
    lines.reduce((acc, l) => acc + (l.quantity * l.unit_price * (l.tax_rate / 100) || 0), 0);

  const calculateTotal = () => calculateSubtotal() + calculateTax();

  const handleCreateAndPost = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!customerId) {
      setErrorMsg("Please select a customer.");
      return;
    }
    setErrorMsg(null);
    try {
      const inv = await financeApi.createInvoice({
        customer_id: customerId,
        issue_date: issueDate,
        due_date: dueDate,
        currency: "USD",
        lines: lines.map((l) => ({
          description: l.description,
          account_id: l.account_id || (accounts[0] ? accounts[0].id : ""),
          quantity: l.quantity,
          unit_price: l.unit_price,
          tax_rate: l.tax_rate,
        })),
      });

      // Post the invoice to create AR ledger entry
      await financeApi.postInvoice(inv.id);
      setShowModal(false);
      setLines([{ description: "", account_id: "", quantity: 1, unit_price: 0, tax_rate: 0 }]);
      loadData();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to create invoice.");
    }
  };

  const handlePostInvoice = async (invoiceId: string) => {
    try {
      await financeApi.postInvoice(invoiceId);
      loadData();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to post invoice.");
    }
  };

  const filteredInvoices = invoices.filter((inv) => {
    const matchesSearch =
      inv.invoice_number.toLowerCase().includes(search.toLowerCase()) ||
      (inv.notes || "").toLowerCase().includes(search.toLowerCase());
    const matchesStatus = selectedStatus === "ALL" || inv.status === selectedStatus;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-3">
            <span className="p-2 rounded-xl bg-blue-500/20 border border-blue-500/30 text-blue-400">
              <Receipt className="w-6 h-6" />
            </span>
            Sales Invoices (Accounts Receivable)
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Customer invoicing with automatic AR general ledger journal generation upon posting.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold transition shadow-lg shadow-blue-600/20"
        >
          <Plus className="w-4 h-4" />
          Create Invoice
        </button>
      </div>

      {/* Filters Bar */}
      <div className="flex flex-col sm:flex-row gap-3 items-center justify-between p-4 rounded-2xl bg-slate-900/60 border border-slate-800">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Search invoice number..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-slate-800/80 border border-slate-700 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-blue-500"
          />
        </div>

        <div className="flex items-center gap-1.5 overflow-x-auto w-full sm:w-auto">
          {["ALL", "POSTED", "DRAFT", "PAID"].map((status) => (
            <button
              key={status}
              onClick={() => setSelectedStatus(status)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                selectedStatus === status
                  ? "bg-blue-600 text-white shadow-sm"
                  : "bg-slate-800/60 text-slate-400 hover:text-slate-200 border border-slate-700/50"
              }`}
            >
              {status}
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

      {/* Invoices Table */}
      <div className="rounded-2xl bg-slate-900/60 border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-800/50 text-slate-400 font-medium border-b border-slate-800 text-xs uppercase tracking-wider">
              <tr>
                <th className="px-6 py-4">Invoice #</th>
                <th className="px-6 py-4">Issue / Due Date</th>
                <th className="px-6 py-4">Total Amount</th>
                <th className="px-6 py-4">Amount Due</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50 text-slate-300">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-10 text-center text-slate-500">
                    Loading invoices...
                  </td>
                </tr>
              ) : filteredInvoices.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-10 text-center text-slate-500">
                    No sales invoices found.
                  </td>
                </tr>
              ) : (
                filteredInvoices.map((inv) => (
                  <tr key={inv.id} className="hover:bg-slate-800/30 transition">
                    <td className="px-6 py-4 font-mono font-bold text-white">{inv.invoice_number}</td>
                    <td className="px-6 py-4 text-xs text-slate-400">
                      {inv.issue_date} &rarr; <span className="text-slate-300">{inv.due_date}</span>
                    </td>
                    <td className="px-6 py-4 font-mono font-semibold text-white">
                      ${Number(inv.total_amount).toFixed(2)}
                    </td>
                    <td className="px-6 py-4 font-mono font-semibold text-amber-400">
                      ${Number(inv.amount_due).toFixed(2)}
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center px-2.5 py-1 rounded-md text-xs font-semibold border ${
                          inv.status === "PAID"
                            ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                            : inv.status === "POSTED"
                            ? "bg-blue-500/10 text-blue-400 border-blue-500/20"
                            : "bg-slate-700 text-slate-300 border-slate-600"
                        }`}
                      >
                        {inv.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      {inv.status === "DRAFT" && (
                        <button
                          onClick={() => handlePostInvoice(inv.id)}
                          className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white transition inline-flex items-center gap-1.5"
                        >
                          <Send className="w-3 h-3" /> Post Invoice
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

      {/* Create Invoice Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-2xl w-full p-6 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Receipt className="w-5 h-5 text-blue-400" />
              New Customer Sales Invoice
            </h3>

            <form onSubmit={handleCreateAndPost} className="space-y-4">
              <div>
                <label className="text-xs font-medium text-slate-400 block mb-1">Customer</label>
                <select
                  required
                  value={customerId}
                  onChange={(e) => setCustomerId(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-blue-500"
                >
                  <option value="">Select Customer...</option>
                  {customers.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.code} - {c.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-medium text-slate-400 block mb-1">Issue Date</label>
                  <input
                    type="date"
                    required
                    value={issueDate}
                    onChange={(e) => setIssueDate(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-400 block mb-1">Due Date</label>
                  <input
                    type="date"
                    required
                    value={dueDate}
                    onChange={(e) => setDueDate(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              {/* Line Items */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-medium text-slate-400">Invoice Items</label>
                  <button
                    type="button"
                    onClick={handleAddLine}
                    className="text-xs text-blue-400 hover:underline flex items-center gap-1 font-semibold"
                  >
                    <Plus className="w-3.5 h-3.5" /> Add Item
                  </button>
                </div>

                {lines.map((l, idx) => (
                  <div key={idx} className="flex items-center gap-2 p-2.5 rounded-xl bg-slate-800/60 border border-slate-700/60">
                    <input
                      type="text"
                      required
                      placeholder="Item description"
                      value={l.description}
                      onChange={(e) => {
                        const updated = [...lines];
                        updated[idx].description = e.target.value;
                        setLines(updated);
                      }}
                      className="flex-1 px-2.5 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-white text-xs"
                    />

                    <select
                      value={l.account_id}
                      onChange={(e) => {
                        const updated = [...lines];
                        updated[idx].account_id = e.target.value;
                        setLines(updated);
                      }}
                      className="w-36 px-2 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-white text-xs"
                    >
                      <option value="">Revenue Account</option>
                      {accounts.map((a) => (
                        <option key={a.id} value={a.id}>
                          {a.code} - {a.name}
                        </option>
                      ))}
                    </select>

                    <input
                      type="number"
                      step="1"
                      min="1"
                      placeholder="Qty"
                      value={l.quantity}
                      onChange={(e) => {
                        const updated = [...lines];
                        updated[idx].quantity = parseFloat(e.target.value) || 1;
                        setLines(updated);
                      }}
                      className="w-16 px-2 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-white text-xs text-right"
                    />

                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      placeholder="Price"
                      value={l.unit_price}
                      onChange={(e) => {
                        const updated = [...lines];
                        updated[idx].unit_price = parseFloat(e.target.value) || 0;
                        setLines(updated);
                      }}
                      className="w-24 px-2 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-white text-xs text-right"
                    />

                    {lines.length > 1 && (
                      <button
                        type="button"
                        onClick={() => handleRemoveLine(idx)}
                        className="p-1.5 text-rose-400 hover:bg-rose-500/10 rounded-lg"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                ))}

                {/* Subtotals */}
                <div className="flex justify-end p-3 rounded-xl bg-slate-800 border border-slate-700 text-xs font-mono space-x-6">
                  <span className="text-slate-400">Subtotal: ${calculateSubtotal().toFixed(2)}</span>
                  <span className="text-white font-bold">Total: ${calculateTotal().toFixed(2)}</span>
                </div>
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
                  className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold transition"
                >
                  Create & Post Invoice
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
