import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { crmApi } from "../api/crmApi";
import { QuotationItemDto, CustomerAccountItem } from "../types";
import { DataTable } from "@/components/ui/DataTable";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { StatCard } from "@/components/ui/StatCard";
import { formatCurrency, formatDate } from "@/lib/utils";
import { FileText, Plus, ShoppingCart, Search, Trash2 } from "lucide-react";

interface LineItem {
  description: string;
  quantity: number;
  unit_price: number;
  discount_pct: number;
  tax_pct: number;
}

export const QuotationsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState("");
  const [showAddModal, setShowAddModal] = useState(false);
  const [customerId, setCustomerId] = useState("");
  const [validUntil, setValidUntil] = useState(
    new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10)
  );
  const [items, setItems] = useState<LineItem[]>([
    { description: "Enterprise Cloud Subscription (Annual)", quantity: 1, unit_price: 12000, discount_pct: 0, tax_pct: 10 },
  ]);

  const { data: quotations = [], isLoading } = useQuery<QuotationItemDto[]>({
    queryKey: ["crm-quotations"],
    queryFn: crmApi.getQuotations,
  });

  const { data: accounts = [] } = useQuery<CustomerAccountItem[]>({
    queryKey: ["crm-accounts"],
    queryFn: crmApi.getCustomers,
  });

  const accountMap = new Map(accounts.map((a) => [a.id, a.name]));

  const createMutation = useMutation({
    mutationFn: crmApi.createQuotation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["crm-quotations"] });
      setShowAddModal(false);
      setCustomerId("");
      setItems([{ description: "", quantity: 1, unit_price: 0, discount_pct: 0, tax_pct: 10 }]);
    },
  });

  const convertMutation = useMutation({
    mutationFn: crmApi.convertQuotationToOrder,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["crm-quotations"] });
      queryClient.invalidateQueries({ queryKey: ["crm-orders"] });
    },
  });

  const addLineItem = () => {
    setItems([...items, { description: "", quantity: 1, unit_price: 0, discount_pct: 0, tax_pct: 10 }]);
  };

  const removeLineItem = (index: number) => {
    if (items.length > 1) {
      setItems(items.filter((_, i) => i !== index));
    }
  };

  const updateLineItem = (index: number, field: keyof LineItem, val: any) => {
    const updated = [...items];
    updated[index] = { ...updated[index], [field]: val };
    setItems(updated);
  };

  const modalSubtotal = items.reduce((sum, item) => {
    const base = item.quantity * item.unit_price;
    const discount = base * (item.discount_pct / 100);
    return sum + (base - discount);
  }, 0);

  const modalTax = items.reduce((sum, item) => {
    const base = item.quantity * item.unit_price;
    const discounted = base * (1 - item.discount_pct / 100);
    return sum + discounted * (item.tax_pct / 100);
  }, 0);

  const modalGrandTotal = modalSubtotal + modalTax;

  const filteredQuotes = quotations.filter((q) => {
    const qNum = (q.quotation_number || "").toLowerCase();
    const cName = (q.customer_id ? accountMap.get(q.customer_id) || "" : "").toLowerCase();
    return qNum.includes(searchTerm.toLowerCase()) || cName.includes(searchTerm.toLowerCase());
  });

  const totalQuotesValue = quotations.reduce((sum, q) => sum + (q.grand_total || 0), 0);
  const convertedCount = quotations.filter((q) => q.status === "CONVERTED").length;

  const columns = [
    {
      header: "Quote Number",
      accessorKey: "quotation_number",
      cell: (row: QuotationItemDto) => (
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-indigo-50 flex items-center justify-center text-indigo-600 font-bold text-xs">
            <FileText className="w-4 h-4" />
          </div>
          <div>
            <div className="font-semibold text-slate-900">{row.quotation_number}</div>
            <div className="text-[11px] text-slate-500">
              {row.created_at ? formatDate(row.created_at) : "N/A"}
            </div>
          </div>
        </div>
      ),
    },
    {
      header: "Account",
      accessorKey: "customer_id",
      cell: (row: QuotationItemDto) => (
        <span className="font-medium text-slate-800">
          {row.customer_id ? accountMap.get(row.customer_id) || "Direct Client" : "Unassigned"}
        </span>
      ),
    },
    {
      header: "Grand Total",
      accessorKey: "grand_total",
      cell: (row: QuotationItemDto) => (
        <div>
          <div className="font-bold text-slate-900">{formatCurrency(row.grand_total)}</div>
          <div className="text-[10px] text-slate-500">
            Subtotal: {formatCurrency(row.subtotal)}
          </div>
        </div>
      ),
    },
    {
      header: "Valid Until",
      accessorKey: "valid_until",
      cell: (row: QuotationItemDto) => (
        <span className="text-xs text-slate-600">
          {row.valid_until ? formatDate(row.valid_until) : "N/A"}
        </span>
      ),
    },
    {
      header: "Status",
      accessorKey: "status",
      cell: (row: QuotationItemDto) => (
        <StatusBadge status={row.status || "DRAFT"} />
      ),
    },
    {
      header: "Actions",
      accessorKey: "id",
      cell: (row: QuotationItemDto) => (
        <div>
          {row.status !== "CONVERTED" && (
            <button
              onClick={() => convertMutation.mutate(row.id)}
              disabled={convertMutation.isPending}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-50 text-emerald-700 hover:bg-emerald-100 font-medium text-xs transition border border-emerald-200"
            >
              <ShoppingCart className="w-3.5 h-3.5" />
              <span>Convert to Order</span>
            </button>
          )}
          {row.status === "CONVERTED" && (
            <span className="text-xs font-semibold text-slate-400">Order Generated</span>
          )}
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Sales Quotations</h1>
          <p className="text-sm text-slate-500">
            Create multi-line item price estimates, manage validity, and convert accepted quotes to binding sales orders.
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 text-white font-medium hover:bg-indigo-700 transition shadow-sm"
        >
          <Plus className="w-4 h-4" />
          <span>New Quotation</span>
        </button>
      </div>

      {/* KPI Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <StatCard
          title="Total Quotations"
          value={quotations.length}
          subtitle="Formal commercial proposals"
          icon={<FileText className="w-5 h-5 text-indigo-600" />}
        />
        <StatCard
          title="Cumulative Value"
          value={formatCurrency(totalQuotesValue)}
          subtitle="Gross quoted pipeline sum"
          icon={<FileText className="w-5 h-5 text-purple-600" />}
        />
        <StatCard
          title="Converted into Orders"
          value={convertedCount}
          subtitle="Accepted contracts in fulfillment"
          icon={<ShoppingCart className="w-5 h-5 text-emerald-600" />}
        />
      </div>

      {/* Quotations Table Card */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="relative flex-1 max-w-sm">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by quote number or account..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600"
            />
          </div>
        </div>

        <DataTable
          columns={columns}
          data={filteredQuotes}
          isLoading={isLoading}
          emptyMessage="No quotations generated yet."
        />
      </div>

      {/* Add Quotation Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4 overflow-y-auto">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-xl max-w-2xl w-full p-6 space-y-4 my-8">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="font-bold text-slate-900 text-lg">Generate Quotation</h3>
              <button
                onClick={() => setShowAddModal(false)}
                className="text-slate-400 hover:text-slate-600 text-lg font-bold"
              >
                &times;
              </button>
            </div>

            <div className="space-y-4 text-sm">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Customer Account *</label>
                  <select
                    value={customerId}
                    onChange={(e) => setCustomerId(e.target.value)}
                    className="w-full px-3 py-2 border rounded-xl border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                  >
                    <option value="">Select Account</option>
                    {accounts.map((a) => (
                      <option key={a.id} value={a.id}>
                        {a.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Valid Until Date</label>
                  <input
                    type="date"
                    value={validUntil}
                    onChange={(e) => setValidUntil(e.target.value)}
                    className="w-full px-3 py-2 border rounded-xl border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                  />
                </div>
              </div>

              {/* Line Items */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">Itemized Line Items</span>
                  <button
                    type="button"
                    onClick={addLineItem}
                    className="text-xs font-medium text-indigo-600 hover:text-indigo-700 flex items-center gap-1"
                  >
                    <Plus className="w-3.5 h-3.5" /> Add Item
                  </button>
                </div>

                <div className="space-y-2.5">
                  {items.map((item, index) => (
                    <div key={index} className="flex items-center gap-2 bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                      <input
                        type="text"
                        placeholder="Item Description"
                        value={item.description}
                        onChange={(e) => updateLineItem(index, "description", e.target.value)}
                        className="flex-2 px-2.5 py-1.5 border rounded-lg border-slate-200 text-xs w-5/12 bg-white"
                      />
                      <input
                        type="number"
                        placeholder="Qty"
                        value={item.quantity}
                        onChange={(e) => updateLineItem(index, "quantity", Number(e.target.value))}
                        className="px-2 py-1.5 border rounded-lg border-slate-200 text-xs w-16 bg-white text-right"
                      />
                      <input
                        type="number"
                        placeholder="Unit $"
                        value={item.unit_price}
                        onChange={(e) => updateLineItem(index, "unit_price", Number(e.target.value))}
                        className="px-2 py-1.5 border rounded-lg border-slate-200 text-xs w-24 bg-white text-right"
                      />
                      <input
                        type="number"
                        placeholder="Disc %"
                        value={item.discount_pct}
                        onChange={(e) => updateLineItem(index, "discount_pct", Number(e.target.value))}
                        className="px-2 py-1.5 border rounded-lg border-slate-200 text-xs w-16 bg-white text-right"
                      />
                      <input
                        type="number"
                        placeholder="Tax %"
                        value={item.tax_pct}
                        onChange={(e) => updateLineItem(index, "tax_pct", Number(e.target.value))}
                        className="px-2 py-1.5 border rounded-lg border-slate-200 text-xs w-16 bg-white text-right"
                      />
                      <button
                        type="button"
                        onClick={() => removeLineItem(index)}
                        className="text-slate-400 hover:text-rose-600 p-1 rounded"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Totals Summary */}
              <div className="bg-slate-50 rounded-xl p-4 border border-slate-200 space-y-1.5 text-xs">
                <div className="flex justify-between text-slate-600">
                  <span>Subtotal:</span>
                  <span className="font-semibold">{formatCurrency(modalSubtotal)}</span>
                </div>
                <div className="flex justify-between text-slate-600">
                  <span>Tax:</span>
                  <span className="font-semibold">{formatCurrency(modalTax)}</span>
                </div>
                <div className="flex justify-between text-slate-900 font-bold text-sm pt-2 border-t border-slate-200">
                  <span>Grand Total:</span>
                  <span>{formatCurrency(modalGrandTotal)}</span>
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-4 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setShowAddModal(false)}
                className="px-4 py-2 rounded-xl border border-slate-200 text-slate-700 hover:bg-slate-50 font-medium"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() =>
                  createMutation.mutate({
                    customer_id: customerId,
                    valid_until: validUntil,
                    items: items.map((it) => ({
                      description: it.description,
                      quantity: it.quantity,
                      unit_price: it.unit_price,
                      discount_pct: it.discount_pct,
                      tax_pct: it.tax_pct,
                    })),
                  })
                }
                disabled={!customerId || createMutation.isPending}
                className="px-4 py-2 rounded-xl bg-indigo-600 text-white font-medium hover:bg-indigo-700 disabled:opacity-50 transition"
              >
                {createMutation.isPending ? "Generating..." : "Save Quotation"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
