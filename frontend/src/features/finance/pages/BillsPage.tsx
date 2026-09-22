import React, { useEffect, useState } from "react";
import {
  CreditCard,
  Plus,
  Search,
  CheckCircle2,
  AlertCircle,
  FileText,
  Building2,
  Send,
  Trash2,
} from "lucide-react";
import { financeApi } from "../api/financeApi";
import { Account, Bill, VendorParty } from "../types";

export const BillsPage: React.FC = () => {
  const [bills, setBills] = useState<Bill[]>([]);
  const [vendors, setVendors] = useState<VendorParty[]>([]);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedStatus, setSelectedStatus] = useState<string>("ALL");
  const [showModal, setShowModal] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Form State
  const [vendorId, setVendorId] = useState("");
  const [vendorRef, setVendorRef] = useState("");
  const [billDate, setBillDate] = useState(new Date().toISOString().split("T")[0]);
  const [dueDate, setDueDate] = useState(
    new Date(Date.now() + 30 * 86400000).toISOString().split("T")[0]
  );
  const [lines, setLines] = useState<Array<{ description: string; expense_account_id: string; quantity: number; unit_price: number; tax_rate: number }>>([
    { description: "Office Cloud Hosting & Infrastructure", expense_account_id: "", quantity: 1, unit_price: 500, tax_rate: 0 },
  ]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [billsRes, vendRes, acctRes] = await Promise.all([
        financeApi.getBills({ page: 1, page_size: 100 }),
        financeApi.getVendors(),
        financeApi.getAccounts({ account_type: "EXPENSE", page: 1, page_size: 100 }),
      ]);
      setBills(billsRes.items || []);
      setVendors(vendRes.items || []);
      setAccounts(acctRes.items || []);
    } catch (err: any) {
      setErrorMsg("Failed to load vendor bills.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleAddLine = () => {
    setLines([...lines, { description: "", expense_account_id: "", quantity: 1, unit_price: 0, tax_rate: 0 }]);
  };

  const handleRemoveLine = (idx: number) => {
    if (lines.length <= 1) return;
    setLines(lines.filter((_, i) => i !== idx));
  };

  const calculateSubtotal = () =>
    lines.reduce((acc, l) => acc + (l.quantity * l.unit_price || 0), 0);

  const calculateTotal = () => calculateSubtotal();

  const handleCreateAndPost = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!vendorId) {
      setErrorMsg("Please select a vendor.");
      return;
    }
    setErrorMsg(null);
    try {
      const bill = await financeApi.createBill({
        vendor_id: vendorId,
        vendor_invoice_ref: vendorRef,
        bill_date: billDate,
        due_date: dueDate,
        currency: "USD",
        lines: lines.map((l) => ({
          description: l.description,
          expense_account_id: l.expense_account_id || (accounts[0] ? accounts[0].id : ""),
          quantity: l.quantity,
          unit_price: l.unit_price,
          tax_rate: l.tax_rate,
        })),
      });

      // Post the bill to generate AP ledger entries
      await financeApi.postBill(bill.id);
      setShowModal(false);
      setLines([{ description: "", expense_account_id: "", quantity: 1, unit_price: 0, tax_rate: 0 }]);
      loadData();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to create vendor bill.");
    }
  };

  const handlePostBill = async (billId: string) => {
    try {
      await financeApi.postBill(billId);
      loadData();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to post bill.");
    }
  };

  const filteredBills = bills.filter((b) => {
    const matchesSearch =
      b.bill_number.toLowerCase().includes(search.toLowerCase()) ||
      (b.vendor_invoice_ref || "").toLowerCase().includes(search.toLowerCase());
    const matchesStatus = selectedStatus === "ALL" || b.status === selectedStatus;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-3">
            <span className="p-2 rounded-xl bg-rose-500/20 border border-rose-500/30 text-rose-400">
              <CreditCard className="w-6 h-6" />
            </span>
            Vendor Bills (Accounts Payable)
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Vendor obligations and payables management with double-entry AP posting.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-sm font-semibold transition shadow-lg shadow-rose-600/20"
        >
          <Plus className="w-4 h-4" />
          Enter Vendor Bill
        </button>
      </div>

      {/* Filters Bar */}
      <div className="flex flex-col sm:flex-row gap-3 items-center justify-between p-4 rounded-2xl bg-slate-900/60 border border-slate-800">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Search bill number or vendor ref..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-slate-800/80 border border-slate-700 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-rose-500"
          />
        </div>

        <div className="flex items-center gap-1.5 overflow-x-auto w-full sm:w-auto">
          {["ALL", "POSTED", "DRAFT", "PAID"].map((status) => (
            <button
              key={status}
              onClick={() => setSelectedStatus(status)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                selectedStatus === status
                  ? "bg-rose-600 text-white shadow-sm"
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

      {/* Bills Table */}
      <div className="rounded-2xl bg-slate-900/60 border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-800/50 text-slate-400 font-medium border-b border-slate-800 text-xs uppercase tracking-wider">
              <tr>
                <th className="px-6 py-4">Bill #</th>
                <th className="px-6 py-4">Vendor Ref</th>
                <th className="px-6 py-4">Bill / Due Date</th>
                <th className="px-6 py-4">Total Amount</th>
                <th className="px-6 py-4">Amount Due</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50 text-slate-300">
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-6 py-10 text-center text-slate-500">
                    Loading vendor bills...
                  </td>
                </tr>
              ) : filteredBills.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-10 text-center text-slate-500">
                    No vendor bills recorded.
                  </td>
                </tr>
              ) : (
                filteredBills.map((bill) => (
                  <tr key={bill.id} className="hover:bg-slate-800/30 transition">
                    <td className="px-6 py-4 font-mono font-bold text-white">{bill.bill_number}</td>
                    <td className="px-6 py-4 text-xs text-slate-400">{bill.vendor_invoice_ref || "-"}</td>
                    <td className="px-6 py-4 text-xs text-slate-400">
                      {bill.bill_date} &rarr; <span className="text-slate-300">{bill.due_date}</span>
                    </td>
                    <td className="px-6 py-4 font-mono font-semibold text-white">
                      ${Number(bill.total_amount).toFixed(2)}
                    </td>
                    <td className="px-6 py-4 font-mono font-semibold text-rose-400">
                      ${Number(bill.amount_due).toFixed(2)}
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center px-2.5 py-1 rounded-md text-xs font-semibold border ${
                          bill.status === "PAID"
                            ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                            : bill.status === "POSTED"
                            ? "bg-rose-500/10 text-rose-400 border-rose-500/20"
                            : "bg-slate-700 text-slate-300 border-slate-600"
                        }`}
                      >
                        {bill.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      {bill.status === "DRAFT" && (
                        <button
                          onClick={() => handlePostBill(bill.id)}
                          className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-rose-600 hover:bg-rose-500 text-white transition inline-flex items-center gap-1.5"
                        >
                          <Send className="w-3 h-3" /> Post Bill
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

      {/* Create Bill Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-2xl w-full p-6 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <CreditCard className="w-5 h-5 text-rose-400" />
              Enter Vendor Bill
            </h3>

            <form onSubmit={handleCreateAndPost} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-medium text-slate-400 block mb-1">Vendor / Supplier</label>
                  <select
                    required
                    value={vendorId}
                    onChange={(e) => setVendorId(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-rose-500"
                  >
                    <option value="">Select Vendor...</option>
                    {vendors.map((v) => (
                      <option key={v.id} value={v.id}>
                        {v.code} - {v.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-400 block mb-1">Vendor Invoice # Ref</label>
                  <input
                    type="text"
                    placeholder="e.g. INV-99212"
                    value={vendorRef}
                    onChange={(e) => setVendorRef(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-rose-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-medium text-slate-400 block mb-1">Bill Date</label>
                  <input
                    type="date"
                    required
                    value={billDate}
                    onChange={(e) => setBillDate(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-rose-500"
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-400 block mb-1">Due Date</label>
                  <input
                    type="date"
                    required
                    value={dueDate}
                    onChange={(e) => setDueDate(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-rose-500"
                  />
                </div>
              </div>

              {/* Line Items */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-medium text-slate-400">Expense Items</label>
                  <button
                    type="button"
                    onClick={handleAddLine}
                    className="text-xs text-rose-400 hover:underline flex items-center gap-1 font-semibold"
                  >
                    <Plus className="w-3.5 h-3.5" /> Add Item
                  </button>
                </div>

                {lines.map((l, idx) => (
                  <div key={idx} className="flex items-center gap-2 p-2.5 rounded-xl bg-slate-800/60 border border-slate-700/60">
                    <input
                      type="text"
                      required
                      placeholder="Expense item description"
                      value={l.description}
                      onChange={(e) => {
                        const updated = [...lines];
                        updated[idx].description = e.target.value;
                        setLines(updated);
                      }}
                      className="flex-1 px-2.5 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-white text-xs"
                    />

                    <select
                      value={l.expense_account_id}
                      onChange={(e) => {
                        const updated = [...lines];
                        updated[idx].expense_account_id = e.target.value;
                        setLines(updated);
                      }}
                      className="w-36 px-2 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-white text-xs"
                    >
                      <option value="">Expense Account</option>
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
                      placeholder="Cost"
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

                <div className="flex justify-end p-3 rounded-xl bg-slate-800 border border-slate-700 text-xs font-mono">
                  <span className="text-white font-bold">Total Bill: ${calculateTotal().toFixed(2)}</span>
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
                  className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-sm font-semibold transition"
                >
                  Create & Post Bill
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
