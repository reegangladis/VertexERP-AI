import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { crmApi } from "../api/crmApi";
import { CustomerAccountItem } from "../types";
import { DataTable } from "@/components/ui/DataTable";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { StatCard } from "@/components/ui/StatCard";
import { formatCurrency, formatDate } from "@/lib/utils";
import { Building2, Plus, Phone, Mail, Globe, DollarSign, Search } from "lucide-react";

export const AccountsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState("");
  const [showAddModal, setShowAddModal] = useState(false);
  const [formData, setFormData] = useState<Partial<CustomerAccountItem>>({
    name: "",
    customer_type: "CORPORATE",
    industry: "",
    website: "",
    phone: "",
    email: "",
    credit_limit: 50000,
    status: "ACTIVE",
  });

  const { data: accounts = [], isLoading } = useQuery<CustomerAccountItem[]>({
    queryKey: ["crm-accounts"],
    queryFn: crmApi.getCustomers,
  });

  const createMutation = useMutation({
    mutationFn: crmApi.createCustomer,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["crm-accounts"] });
      setShowAddModal(false);
      setFormData({
        name: "",
        customer_type: "CORPORATE",
        industry: "",
        website: "",
        phone: "",
        email: "",
        credit_limit: 50000,
        status: "ACTIVE",
      });
    },
  });

  const filteredAccounts = accounts.filter(
    (acc) =>
      acc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (acc.industry && acc.industry.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (acc.email && acc.email.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const totalCredit = accounts.reduce((acc, curr) => acc + (curr.credit_limit || 0), 0);
  const activeCount = accounts.filter((a) => a.status === "ACTIVE").length;

  const columns = [
    {
      header: "Account Name",
      accessorKey: "name",
      cell: (row: CustomerAccountItem) => (
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-brand-500/15 flex items-center justify-center text-brand-400 font-bold">
            <Building2 className="w-5 h-5" />
          </div>
          <div>
            <div className="font-semibold text-zinc-100">{row.name}</div>
            <div className="text-xs text-zinc-400">{row.customer_type}</div>
          </div>
        </div>
      ),
    },
    {
      header: "Industry",
      accessorKey: "industry",
      cell: (row: CustomerAccountItem) => (
        <span className="text-zinc-200 font-medium">{row.industry || "General Enterprise"}</span>
      ),
    },
    {
      header: "Contact Details",
      accessorKey: "email",
      cell: (row: CustomerAccountItem) => (
        <div className="text-xs space-y-1">
          {row.email && (
            <div className="flex items-center gap-1.5 text-zinc-300">
              <Mail className="w-3.5 h-3.5 text-slate-400" />
              <span>{row.email}</span>
            </div>
          )}
          {row.phone && (
            <div className="flex items-center gap-1.5 text-zinc-300">
              <Phone className="w-3.5 h-3.5 text-slate-400" />
              <span>{row.phone}</span>
            </div>
          )}
          {row.website && (
            <div className="flex items-center gap-1.5 text-brand-400">
              <Globe className="w-3.5 h-3.5 text-indigo-400" />
              <span>{row.website}</span>
            </div>
          )}
        </div>
      ),
    },
    {
      header: "Credit Limit",
      accessorKey: "credit_limit",
      cell: (row: CustomerAccountItem) => (
        <span className="font-semibold text-zinc-100">
          {formatCurrency(row.credit_limit || 0)}
        </span>
      ),
    },
    {
      header: "Status",
      accessorKey: "status",
      cell: (row: CustomerAccountItem) => (
        <StatusBadge status={row.status || "ACTIVE"} />
      ),
    },
    {
      header: "Created Date",
      accessorKey: "created_at",
      cell: (row: CustomerAccountItem) => (
        <span className="text-xs text-zinc-400">
          {row.created_at ? formatDate(row.created_at) : "N/A"}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-zinc-100 tracking-tight">Customer Accounts</h1>
          <p className="text-sm text-zinc-400">
            Enterprise clients, corporate accounts, and organizational relationships.
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-brand-600 text-white font-medium hover:bg-brand-500 transition shadow-sm"
        >
          <Plus className="w-4 h-4" />
          <span>New Account</span>
        </button>
      </div>

      {/* KPI Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <StatCard
          title="Total Accounts"
          value={accounts.length}
          subtitle={`${activeCount} active client portfolios`}
          icon={<Building2 className="w-5 h-5 text-brand-400" />}
        />
        <StatCard
          title="Active Corporate Clients"
          value={activeCount}
          subtitle="Generating recurrent business"
          icon={<Building2 className="w-5 h-5 text-emerald-400" />}
        />
        <StatCard
          title="Cumulative Credit Line"
          value={formatCurrency(totalCredit)}
          subtitle="Authorized trade credit facilities"
          icon={<DollarSign className="w-5 h-5 text-amber-400" />}
        />
      </div>

      {/* Accounts Table Card */}
      <div className="bg-zinc-900/80 rounded-2xl border border-zinc-800 shadow-sm p-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="relative flex-1 max-w-sm">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by account name, industry, or email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 rounded-xl border border-zinc-800 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600"
            />
          </div>
        </div>

        <DataTable
          columns={columns}
          data={filteredAccounts}
          isLoading={isLoading}
          emptyMessage="No customer accounts registered yet."
        />
      </div>

      {/* Add Account Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-zinc-900/80 rounded-2xl border border-zinc-800 shadow-xl max-w-lg w-full p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-zinc-800/80 pb-3">
              <h3 className="font-bold text-zinc-100 text-lg">Create Customer Account</h3>
              <button
                onClick={() => setShowAddModal(false)}
                className="text-slate-400 hover:text-zinc-300 text-lg font-bold"
              >
                &times;
              </button>
            </div>

            <div className="space-y-3.5 text-sm">
              <div>
                <label className="block text-xs font-semibold text-zinc-300 mb-1">Company / Account Name *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="Acme Global Inc."
                  className="w-full px-3 py-2 border rounded-xl border-zinc-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-zinc-300 mb-1">Customer Type</label>
                  <select
                    value={formData.customer_type}
                    onChange={(e) => setFormData({ ...formData, customer_type: e.target.value })}
                    className="w-full px-3 py-2 border rounded-xl border-zinc-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                  >
                    <option value="CORPORATE">Corporate</option>
                    <option value="INDIVIDUAL">Individual</option>
                    <option value="GOVERNMENT">Government</option>
                    <option value="PARTNER">Partner</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-zinc-300 mb-1">Industry</label>
                  <input
                    type="text"
                    value={formData.industry}
                    onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                    placeholder="e.g. Technology, Healthcare"
                    className="w-full px-3 py-2 border rounded-xl border-zinc-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-zinc-300 mb-1">Corporate Email</label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    placeholder="contact@acme.com"
                    className="w-full px-3 py-2 border rounded-xl border-zinc-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-zinc-300 mb-1">Phone Number</label>
                  <input
                    type="text"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    placeholder="+1 (555) 019-2831"
                    className="w-full px-3 py-2 border rounded-xl border-zinc-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-zinc-300 mb-1">Website</label>
                  <input
                    type="text"
                    value={formData.website}
                    onChange={(e) => setFormData({ ...formData, website: e.target.value })}
                    placeholder="https://acme.com"
                    className="w-full px-3 py-2 border rounded-xl border-zinc-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-zinc-300 mb-1">Credit Limit ($)</label>
                  <input
                    type="number"
                    value={formData.credit_limit}
                    onChange={(e) => setFormData({ ...formData, credit_limit: Number(e.target.value) })}
                    className="w-full px-3 py-2 border rounded-xl border-zinc-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                  />
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-4 border-t border-zinc-800/80">
              <button
                type="button"
                onClick={() => setShowAddModal(false)}
                className="px-4 py-2 rounded-xl border border-zinc-800 text-zinc-200 hover:bg-zinc-950/70 font-medium"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => createMutation.mutate(formData)}
                disabled={!formData.name || createMutation.isPending}
                className="px-4 py-2 rounded-xl bg-brand-600 text-white font-medium hover:bg-brand-500 disabled:opacity-50 transition"
              >
                {createMutation.isPending ? "Creating..." : "Save Account"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
