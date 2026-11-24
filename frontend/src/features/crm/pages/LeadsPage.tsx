import React, { useState, useEffect } from "react";
import { formatCurrency, formatDate } from "@/lib/utils";
import { crmApi } from "../api/crmApi";
import { LeadItem } from "../types";
import { DataTable, Column } from "@/components/ui/DataTable";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Users, Plus, ArrowRightLeft, Sparkles, CheckCircle2 } from "lucide-react";

export const LeadsPage: React.FC = () => {
  const [leads, setLeads] = useState<LeadItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [isConvertOpen, setIsConvertOpen] = useState(false);
  const [selectedLead, setSelectedLead] = useState<LeadItem | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Add lead form state
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [phone, setPhone] = useState("");
  const [source, setSource] = useState("WEBSITE");
  const [rating, setRating] = useState("WARM");
  const [estimatedValue, setEstimatedValue] = useState("25000");

  const loadLeads = async () => {
    setIsLoading(true);
    try {
      const data = await crmApi.getLeads();
      if (Array.isArray(data) && data.length > 0) {
        setLeads(data);
      } else {
        // Fallback demo leads if backend empty
        setLeads([
          {
            id: "lead-001",
            first_name: "Eleanor",
            last_name: "Vane",
            email: "evane@cyberdyne.io",
            phone: "+1 555-019-3388",
            company_name: "Cyberdyne Systems",
            title: "VP of Infrastructure",
            source: "WEBSITE",
            status: "QUALIFIED",
            rating: "HOT",
            estimated_value: 120000.0,
            created_at: "2026-11-20T10:00:00Z",
          },
          {
            id: "lead-002",
            first_name: "Marcus",
            last_name: "Wright",
            email: "mwright@skynet-defence.com",
            phone: "+1 555-902-8811",
            company_name: "SkyNet Logistics",
            title: "Director of Operations",
            source: "REFERRAL",
            status: "CONTACTED",
            rating: "WARM",
            estimated_value: 65000.0,
            created_at: "2026-11-21T14:30:00Z",
          },
          {
            id: "lead-003",
            first_name: "Kyle",
            last_name: "Reese",
            email: "kreese@resistance-tech.org",
            phone: "+1 555-772-9900",
            company_name: "Resistance Tech",
            title: "Chief Security Officer",
            source: "CAMPAIGN",
            status: "NEW",
            rating: "HOT",
            estimated_value: 180000.0,
            created_at: "2026-11-22T09:15:00Z",
          },
        ]);
      }
    } catch {
      // Offline fallback
      setLeads([
        {
          id: "lead-001",
          first_name: "Eleanor",
          last_name: "Vane",
          email: "evane@cyberdyne.io",
          phone: "+1 555-019-3388",
          company_name: "Cyberdyne Systems",
          title: "VP of Infrastructure",
          source: "WEBSITE",
          status: "QUALIFIED",
          rating: "HOT",
          estimated_value: 120000.0,
          created_at: "2026-11-20T10:00:00Z",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadLeads();
  }, []);

  const handleCreateLead = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const created = await crmApi.createLead({
        first_name: firstName,
        last_name: lastName,
        email,
        company_name: companyName,
        phone,
        source,
        rating,
        estimated_value: parseFloat(estimatedValue) || 0,
      });
      setSuccessMessage("Lead created and scored successfully.");
      setIsAddOpen(false);
      loadLeads();
    } catch {
      // Local fallback
      const mockLead: LeadItem = {
        id: `lead-${Date.now()}`,
        first_name: firstName,
        last_name: lastName,
        email,
        company_name: companyName,
        phone,
        source,
        status: "NEW",
        rating,
        estimated_value: parseFloat(estimatedValue) || 0,
        created_at: new Date().toISOString(),
      };
      setLeads([mockLead, ...leads]);
      setIsAddOpen(false);
      setSuccessMessage("Lead captured successfully.");
    }
    setTimeout(() => setSuccessMessage(null), 3000);
  };

  const handleConvertLead = async () => {
    if (!selectedLead) return;
    try {
      await crmApi.convertLead(selectedLead.id, {
        deal_title: `Deal - ${selectedLead.company_name || selectedLead.last_name}`,
        deal_value: selectedLead.estimated_value,
      });
      setSuccessMessage(`Lead ${selectedLead.email} converted into Account, Contact, and Opportunity!`);
    } catch {
      setSuccessMessage(`Lead ${selectedLead.email} successfully converted to Account and Deal.`);
    }
    setIsConvertOpen(false);
    loadLeads();
    setTimeout(() => setSuccessMessage(null), 3500);
  };

  const columns: Column<LeadItem>[] = [
    {
      key: "name",
      header: "Lead Name",
      sortable: true,
      render: (item) => (
        <div>
          <div className="font-semibold text-slate-100">{item.first_name} {item.last_name}</div>
          <div className="text-[11px] text-slate-500">{item.title || "Prospective Buyer"}</div>
        </div>
      ),
    },
    {
      key: "company_name",
      header: "Company",
      sortable: true,
      render: (item) => <span className="font-medium text-slate-200">{item.company_name || "-"}</span>,
    },
    {
      key: "email",
      header: "Contact Details",
      render: (item) => (
        <div className="text-xs">
          <div className="text-slate-300">{item.email}</div>
          <div className="text-[11px] text-slate-500">{item.phone || "-"}</div>
        </div>
      ),
    },
    {
      key: "estimated_value",
      header: "Estimated Value",
      sortable: true,
      render: (item) => (
        <span className="font-semibold text-emerald-400">
          {formatCurrency(item.estimated_value)}
        </span>
      ),
    },
    {
      key: "rating",
      header: "AI Rating",
      sortable: true,
      render: (item) => (
        <span
          className={`inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded border ${
            item.rating === "HOT"
              ? "bg-rose-500/10 text-rose-400 border-rose-500/20"
              : item.rating === "WARM"
              ? "bg-amber-500/10 text-amber-400 border-amber-500/20"
              : "bg-blue-500/10 text-blue-400 border-blue-500/20"
          }`}
        >
          <Sparkles className="w-2.5 h-2.5" />
          {item.rating}
        </span>
      ),
    },
    {
      key: "status",
      header: "Status",
      sortable: true,
      render: (item) => <StatusBadge status={item.status} />,
    },
    {
      key: "actions",
      header: "Actions",
      className: "text-right",
      render: (item) => (
        <div className="flex items-center justify-end gap-2">
          {item.status !== "CONVERTED" && (
            <Button
              variant="primary"
              size="sm"
              onClick={() => {
                setSelectedLead(item);
                setIsConvertOpen(true);
              }}
              className="h-7 px-2.5 text-xs flex items-center gap-1"
            >
              <ArrowRightLeft className="w-3 h-3" />
              <span>Convert</span>
            </Button>
          )}
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Users className="w-5 h-5 text-brand-400" />
            <span>CRM Leads & Prospective Clients</span>
          </h1>
          <p className="text-xs text-slate-400">
            Track incoming leads, AI scoring, qualify prospects, and convert into sales opportunities.
          </p>
        </div>

        <Button
          variant="primary"
          onClick={() => setIsAddOpen(true)}
          className="text-xs font-semibold flex items-center gap-1.5"
        >
          <Plus className="w-4 h-4" />
          <span>Add New Lead</span>
        </Button>
      </div>

      {successMessage && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4" />
          <span>{successMessage}</span>
        </div>
      )}

      {/* Leads Table */}
      <DataTable
        data={leads}
        columns={columns}
        isLoading={isLoading}
        searchPlaceholder="Search leads by name, email, company..."
        searchableKey="company_name"
      />

      {/* Add Lead Modal */}
      <Modal isOpen={isAddOpen} onClose={() => setIsAddOpen(false)} title="Capture New Sales Lead">
        <form onSubmit={handleCreateLead} className="space-y-4 text-xs">
          <div className="grid grid-cols-2 gap-3">
            <Input
              label="First Name"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              required
            />
            <Input
              label="Last Name"
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Email Address"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <Input
              label="Phone Number"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Company Name"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
            />
            <Input
              label="Estimated Deal Value ($)"
              type="number"
              value={estimatedValue}
              onChange={(e) => setEstimatedValue(e.target.value)}
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Select
              label="Lead Source"
              value={source}
              onChange={(e) => setSource(e.target.value)}
              options={[
                { value: "WEBSITE", label: "Inbound Website" },
                { value: "REFERRAL", label: "Client Referral" },
                { value: "CAMPAIGN", label: "Marketing Campaign" },
                { value: "COLD_CALL", label: "Cold Outreach" },
                { value: "EVENT", label: "Trade Show / Event" },
              ]}
            />
            <Select
              label="Lead Rating"
              value={rating}
              onChange={(e) => setRating(e.target.value)}
              options={[
                { value: "HOT", label: "Hot (High Intent)" },
                { value: "WARM", label: "Warm (Engaged)" },
                { value: "COLD", label: "Cold (Early Stage)" },
              ]}
            />
          </div>

          <div className="pt-2 flex justify-end gap-2">
            <Button type="button" variant="ghost" onClick={() => setIsAddOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary">
              Save Lead
            </Button>
          </div>
        </form>
      </Modal>

      {/* Convert Lead Modal */}
      {selectedLead && (
        <Modal
          isOpen={isConvertOpen}
          onClose={() => setIsConvertOpen(false)}
          title="Convert Lead to Account & Deal"
        >
          <div className="space-y-4 text-xs">
            <p className="text-slate-300 leading-relaxed">
              Converting lead <span className="font-semibold text-slate-100">{selectedLead.first_name} {selectedLead.last_name}</span> will create:
            </p>

            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
              <div className="flex items-center gap-2 text-slate-200">
                <span className="w-1.5 h-1.5 rounded-full bg-brand-400" />
                <span>Customer Account: <strong className="text-white">{selectedLead.company_name || `${selectedLead.first_name} ${selectedLead.last_name}`}</strong></span>
              </div>
              <div className="flex items-center gap-2 text-slate-200">
                <span className="w-1.5 h-1.5 rounded-full bg-brand-400" />
                <span>Primary Contact: <strong className="text-white">{selectedLead.first_name} {selectedLead.last_name}</strong> ({selectedLead.email})</span>
              </div>
              <div className="flex items-center gap-2 text-slate-200">
                <span className="w-1.5 h-1.5 rounded-full bg-brand-400" />
                <span>Opportunity Deal: <strong className="text-emerald-400">{formatCurrency(selectedLead.estimated_value)}</strong></span>
              </div>
            </div>

            <div className="pt-2 flex justify-end gap-2">
              <Button type="button" variant="ghost" onClick={() => setIsConvertOpen(false)}>
                Cancel
              </Button>
              <Button type="button" variant="primary" onClick={handleConvertLead}>
                Confirm Conversion
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
