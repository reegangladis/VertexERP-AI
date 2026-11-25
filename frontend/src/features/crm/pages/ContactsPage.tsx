import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { crmApi } from "../api/crmApi";
import { ContactItem, CustomerAccountItem } from "../types";
import { DataTable } from "@/components/ui/DataTable";
import { StatCard } from "@/components/ui/StatCard";
import { getInitials } from "@/lib/utils";
import { UserCheck, Plus, Mail, Phone, Building2, Search, CheckCircle2 } from "lucide-react";

export const ContactsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState("");
  const [showAddModal, setShowAddModal] = useState(false);
  const [formData, setFormData] = useState<Partial<ContactItem>>({
    first_name: "",
    last_name: "",
    email: "",
    phone: "",
    title: "",
    department: "",
    customer_id: "",
    is_primary: false,
  });

  const { data: contacts = [], isLoading } = useQuery<ContactItem[]>({
    queryKey: ["crm-contacts"],
    queryFn: () => crmApi.getContacts(),
  });

  const { data: accounts = [] } = useQuery<CustomerAccountItem[]>({
    queryKey: ["crm-accounts"],
    queryFn: crmApi.getCustomers,
  });

  const createMutation = useMutation({
    mutationFn: crmApi.createContact,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["crm-contacts"] });
      setShowAddModal(false);
      setFormData({
        first_name: "",
        last_name: "",
        email: "",
        phone: "",
        title: "",
        department: "",
        customer_id: "",
        is_primary: false,
      });
    },
  });

  const accountMap = new Map(accounts.map((a) => [a.id, a.name]));

  const filteredContacts = contacts.filter((c) => {
    const fullName = `${c.first_name} ${c.last_name}`.toLowerCase();
    const email = (c.email || "").toLowerCase();
    const title = (c.title || "").toLowerCase();
    const account = (c.customer_id ? accountMap.get(c.customer_id) || "" : "").toLowerCase();
    const s = searchTerm.toLowerCase();
    return fullName.includes(s) || email.includes(s) || title.includes(s) || account.includes(s);
  });

  const primaryCount = contacts.filter((c) => c.is_primary).length;

  const columns = [
    {
      header: "Contact Name",
      accessorKey: "first_name",
      cell: (row: ContactItem) => {
        const fullName = `${row.first_name} ${row.last_name}`;
        return (
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-zinc-800/80 border border-zinc-800 flex items-center justify-center text-zinc-200 font-bold text-xs">
              {getInitials(fullName)}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-zinc-100">{fullName}</span>
                {row.is_primary && (
                  <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-semibold bg-brand-500/15 text-brand-300 border border-brand-500/30">
                    <CheckCircle2 className="w-2.5 h-2.5" /> Primary
                  </span>
                )}
              </div>
              <div className="text-xs text-zinc-400">{row.title || "Key Stakeholder"}</div>
            </div>
          </div>
        );
      },
    },
    {
      header: "Account / Company",
      accessorKey: "customer_id",
      cell: (row: ContactItem) => (
        <div className="flex items-center gap-1.5 text-zinc-200 font-medium">
          <Building2 className="w-3.5 h-3.5 text-slate-400" />
          <span>{row.customer_id ? accountMap.get(row.customer_id) || "Direct Client" : "Unassigned"}</span>
        </div>
      ),
    },
    {
      header: "Department",
      accessorKey: "department",
      cell: (row: ContactItem) => (
        <span className="text-xs text-zinc-300 bg-zinc-800/80 px-2 py-0.5 rounded-md">
          {row.department || "Executive"}
        </span>
      ),
    },
    {
      header: "Direct Phone",
      accessorKey: "phone",
      cell: (row: ContactItem) => (
        <div className="flex items-center gap-1.5 text-xs text-zinc-300">
          <Phone className="w-3.5 h-3.5 text-slate-400" />
          <span>{row.phone || "N/A"}</span>
        </div>
      ),
    },
    {
      header: "Email Address",
      accessorKey: "email",
      cell: (row: ContactItem) => (
        <div className="flex items-center gap-1.5 text-xs text-brand-400">
          <Mail className="w-3.5 h-3.5 text-indigo-400" />
          <span>{row.email || "N/A"}</span>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-zinc-100 tracking-tight">Business Contacts</h1>
          <p className="text-sm text-zinc-400">
            Client stakeholders, decision makers, and corporate points of contact.
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-brand-600 text-white font-medium hover:bg-brand-500 transition shadow-sm"
        >
          <Plus className="w-4 h-4" />
          <span>New Contact</span>
        </button>
      </div>

      {/* KPI Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <StatCard
          title="Total Contacts"
          value={contacts.length}
          subtitle="Directory of business stakeholders"
          icon={<UserCheck className="w-5 h-5 text-brand-400" />}
        />
        <StatCard
          title="Primary Decision Makers"
          value={primaryCount}
          subtitle="Designated primary corporate leads"
          icon={<CheckCircle2 className="w-5 h-5 text-emerald-400" />}
        />
        <StatCard
          title="Connected Accounts"
          value={accounts.length}
          subtitle="Accounts with linked stakeholders"
          icon={<Building2 className="w-5 h-5 text-emerald-400" />}
        />
      </div>

      {/* Contacts Table Card */}
      <div className="bg-zinc-900/80 rounded-2xl border border-zinc-800 shadow-sm p-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="relative flex-1 max-w-sm">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by contact name, email, or account..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 rounded-xl border border-zinc-800 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600"
            />
          </div>
        </div>

        <DataTable
          columns={columns}
          data={filteredContacts}
          isLoading={isLoading}
          emptyMessage="No contacts recorded yet."
        />
      </div>

      {/* Add Contact Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-zinc-900/80 rounded-2xl border border-zinc-800 shadow-xl max-w-lg w-full p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-zinc-800/80 pb-3">
              <h3 className="font-bold text-zinc-100 text-lg">Add Business Contact</h3>
              <button
                onClick={() => setShowAddModal(false)}
                className="text-slate-400 hover:text-zinc-300 text-lg font-bold"
              >
                &times;
              </button>
            </div>

            <div className="space-y-3.5 text-sm">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-zinc-300 mb-1">First Name *</label>
                  <input
                    type="text"
                    value={formData.first_name}
                    onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                    placeholder="Jane"
                    className="w-full px-3 py-2 border rounded-xl border-zinc-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-zinc-300 mb-1">Last Name *</label>
                  <input
                    type="text"
                    value={formData.last_name}
                    onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                    placeholder="Doe"
                    className="w-full px-3 py-2 border rounded-xl border-zinc-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-zinc-300 mb-1">Customer Account</label>
                <select
                  value={formData.customer_id || ""}
                  onChange={(e) => setFormData({ ...formData, customer_id: e.target.value })}
                  className="w-full px-3 py-2 border rounded-xl border-zinc-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                >
                  <option value="">Select Account (Optional)</option>
                  {accounts.map((a) => (
                    <option key={a.id} value={a.id}>
                      {a.name} ({a.customer_type})
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-zinc-300 mb-1">Job Title</label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    placeholder="VP of Procurement"
                    className="w-full px-3 py-2 border rounded-xl border-zinc-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-zinc-300 mb-1">Department</label>
                  <input
                    type="text"
                    value={formData.department}
                    onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                    placeholder="Purchasing / IT"
                    className="w-full px-3 py-2 border rounded-xl border-zinc-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-zinc-300 mb-1">Work Email</label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    placeholder="jane.doe@client.com"
                    className="w-full px-3 py-2 border rounded-xl border-zinc-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-zinc-300 mb-1">Phone Number</label>
                  <input
                    type="text"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    placeholder="+1 (555) 012-3456"
                    className="w-full px-3 py-2 border rounded-xl border-zinc-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                  />
                </div>
              </div>

              <div className="flex items-center gap-2 pt-2">
                <input
                  type="checkbox"
                  id="is_primary"
                  checked={formData.is_primary}
                  onChange={(e) => setFormData({ ...formData, is_primary: e.target.checked })}
                  className="rounded border-zinc-700 text-brand-400 focus:ring-indigo-500"
                />
                <label htmlFor="is_primary" className="text-xs font-medium text-zinc-200">
                  Designate as primary contact for this account
                </label>
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
                disabled={!formData.first_name || !formData.last_name || createMutation.isPending}
                className="px-4 py-2 rounded-xl bg-brand-600 text-white font-medium hover:bg-brand-500 disabled:opacity-50 transition"
              >
                {createMutation.isPending ? "Saving..." : "Save Contact"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
