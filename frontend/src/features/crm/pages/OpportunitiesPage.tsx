import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { crmApi } from "../api/crmApi";
import { DealItem, CustomerAccountItem } from "../types";
import { formatCurrency } from "@/lib/utils";
import { DollarSign, Plus, ArrowRight, Briefcase, TrendingUp } from "lucide-react";

interface StageConfig {
  id: string;
  name: string;
  probability: number;
  color: string;
}

const STAGES: StageConfig[] = [
  { id: "PROSPECTING", name: "Prospecting", probability: 10, color: "border-slate-300 bg-slate-50 text-slate-700" },
  { id: "QUALIFICATION", name: "Qualification", probability: 25, color: "border-blue-300 bg-blue-50 text-blue-700" },
  { id: "NEEDS_ANALYSIS", name: "Needs Analysis", probability: 40, color: "border-indigo-300 bg-indigo-50 text-indigo-700" },
  { id: "PROPOSAL", name: "Proposal / Quote", probability: 60, color: "border-purple-300 bg-purple-50 text-purple-700" },
  { id: "NEGOTIATION", name: "Negotiation", probability: 80, color: "border-amber-300 bg-amber-50 text-amber-700" },
  { id: "CLOSED_WON", name: "Closed Won", probability: 100, color: "border-emerald-300 bg-emerald-50 text-emerald-700" },
  { id: "CLOSED_LOST", name: "Closed Lost", probability: 0, color: "border-rose-300 bg-rose-50 text-rose-700" },
];

export const OpportunitiesPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [showAddModal, setShowAddModal] = useState(false);
  const [formData, setFormData] = useState<Partial<DealItem>>({
    title: "",
    value: 10000,
    currency: "USD",
    stage_id: "PROSPECTING",
    customer_id: "",
    win_probability_pct: 10,
    status: "OPEN",
  });

  const { data: deals = [], isLoading } = useQuery<DealItem[]>({
    queryKey: ["crm-deals"],
    queryFn: crmApi.getDeals,
  });

  const { data: accounts = [] } = useQuery<CustomerAccountItem[]>({
    queryKey: ["crm-accounts"],
    queryFn: crmApi.getCustomers,
  });

  const stageMutation = useMutation({
    mutationFn: ({ dealId, stageId, prob }: { dealId: string; stageId: string; prob: number }) =>
      crmApi.updateDealStage(dealId, stageId, prob),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["crm-deals"] });
      queryClient.invalidateQueries({ queryKey: ["crm-metrics"] });
    },
  });

  const createMutation = useMutation({
    mutationFn: crmApi.createDeal,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["crm-deals"] });
      setShowAddModal(false);
      setFormData({
        title: "",
        value: 10000,
        currency: "USD",
        stage_id: "PROSPECTING",
        customer_id: "",
        win_probability_pct: 10,
        status: "OPEN",
      });
    },
  });

  const accountMap = new Map(accounts.map((a) => [a.id, a.name]));

  // Calculate totals
  const totalPipelineValue = deals
    .filter((d) => d.stage_id !== "CLOSED_LOST")
    .reduce((sum, d) => sum + (d.value || 0), 0);

  const weightedForecast = deals
    .filter((d) => d.stage_id !== "CLOSED_LOST")
    .reduce((sum, d) => sum + (d.value || 0) * ((d.win_probability_pct || 0) / 100), 0);

  const wonTotal = deals
    .filter((d) => d.stage_id === "CLOSED_WON")
    .reduce((sum, d) => sum + (d.value || 0), 0);

  const handleStageAdvance = (deal: DealItem, currentStageIndex: number) => {
    if (currentStageIndex < STAGES.length - 2) {
      const nextStage = STAGES[currentStageIndex + 1];
      stageMutation.mutate({
        dealId: deal.id,
        stageId: nextStage.id,
        prob: nextStage.probability,
      });
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Opportunities Pipeline</h1>
          <p className="text-sm text-slate-500">
            Salesforce-style visual deal flow, stage probability progression, and weighted pipeline forecasting.
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 text-white font-medium hover:bg-indigo-700 transition shadow-sm"
        >
          <Plus className="w-4 h-4" />
          <span>New Opportunity</span>
        </button>
      </div>

      {/* Metrics Header Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Pipeline Value</div>
            <div className="text-2xl font-bold text-slate-900 mt-1">{formatCurrency(totalPipelineValue)}</div>
            <div className="text-xs text-slate-400 mt-0.5">{deals.length} total active deals</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-indigo-50 flex items-center justify-center text-indigo-600">
            <DollarSign className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Weighted Forecast</div>
            <div className="text-2xl font-bold text-slate-900 mt-1">{formatCurrency(weightedForecast)}</div>
            <div className="text-xs text-emerald-600 font-medium mt-0.5">Probability-adjusted projection</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center text-emerald-600">
            <TrendingUp className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Closed Won Revenue</div>
            <div className="text-2xl font-bold text-emerald-600 mt-1">{formatCurrency(wonTotal)}</div>
            <div className="text-xs text-slate-400 mt-0.5">Realized sales conversions</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-emerald-100 flex items-center justify-center text-emerald-700">
            <Briefcase className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Kanban Board Container */}
      <div className="overflow-x-auto pb-4">
        <div className="flex gap-4 min-w-[1280px]">
          {STAGES.map((stage, idx) => {
            const stageDeals = deals.filter(
              (d) => (d.stage_id || "PROSPECTING").toUpperCase() === stage.id
            );
            const stageTotal = stageDeals.reduce((sum, d) => sum + (d.value || 0), 0);

            return (
              <div
                key={stage.id}
                className="w-72 flex-shrink-0 bg-slate-50/80 rounded-2xl border border-slate-200 p-3.5 flex flex-col max-h-[750px]"
              >
                {/* Stage Header */}
                <div className="flex items-center justify-between pb-3 border-b border-slate-200">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-800 text-sm">{stage.name}</span>
                    <span className="text-[11px] font-bold px-1.5 py-0.5 rounded-full bg-slate-200/80 text-slate-700">
                      {stageDeals.length}
                    </span>
                  </div>
                  <span className="text-xs font-semibold text-slate-500">{stage.probability}%</span>
                </div>

                <div className="text-xs font-medium text-slate-500 py-1.5">
                  Subtotal: <span className="font-bold text-slate-700">{formatCurrency(stageTotal)}</span>
                </div>

                {/* Stage Cards List */}
                <div className="flex-1 overflow-y-auto space-y-3 pt-2 pr-1">
                  {isLoading && (
                    <div className="text-xs text-slate-400 py-4 text-center">Loading deals...</div>
                  )}
                  {!isLoading && stageDeals.length === 0 && (
                    <div className="text-xs text-slate-400 py-6 text-center border-2 border-dashed border-slate-200 rounded-xl">
                      Empty stage
                    </div>
                  )}
                  {stageDeals.map((deal) => (
                    <div
                      key={deal.id}
                      className="bg-white rounded-xl border border-slate-200 shadow-sm p-3.5 hover:shadow-md transition group"
                    >
                      <div className="font-semibold text-slate-900 text-sm group-hover:text-indigo-600 transition">
                        {deal.title}
                      </div>

                      <div className="text-xs text-slate-500 font-medium mt-1 truncate">
                        {deal.customer_id ? accountMap.get(deal.customer_id) || "Direct Account" : "Unassigned Account"}
                      </div>

                      <div className="flex items-center justify-between mt-3 pt-2.5 border-t border-slate-100">
                        <span className="text-sm font-bold text-slate-900">
                          {formatCurrency(deal.value)}
                        </span>
                        <span className="text-[11px] font-semibold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded">
                          {deal.win_probability_pct ?? stage.probability}% Win
                        </span>
                      </div>

                      {/* Quick Advance Button */}
                      {idx < STAGES.length - 2 && (
                        <div className="mt-2.5 flex justify-end">
                          <button
                            onClick={() => handleStageAdvance(deal, idx)}
                            className="inline-flex items-center gap-1 text-[11px] font-medium text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 px-2 py-1 rounded transition"
                            title={`Advance to ${STAGES[idx + 1].name}`}
                          >
                            <span>Advance</span>
                            <ArrowRight className="w-3 h-3" />
                          </button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Add Deal Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-xl max-w-lg w-full p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="font-bold text-slate-900 text-lg">Create New Opportunity</h3>
              <button
                onClick={() => setShowAddModal(false)}
                className="text-slate-400 hover:text-slate-600 text-lg font-bold"
              >
                &times;
              </button>
            </div>

            <div className="space-y-3.5 text-sm">
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Opportunity Name *</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="e.g. Enterprise ERP Cloud Migration"
                  className="w-full px-3 py-2 border rounded-xl border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Customer Account</label>
                <select
                  value={formData.customer_id || ""}
                  onChange={(e) => setFormData({ ...formData, customer_id: e.target.value })}
                  className="w-full px-3 py-2 border rounded-xl border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                >
                  <option value="">Select Account (Optional)</option>
                  {accounts.map((a) => (
                    <option key={a.id} value={a.id}>
                      {a.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Estimated Value ($)</label>
                  <input
                    type="number"
                    value={formData.value}
                    onChange={(e) => setFormData({ ...formData, value: Number(e.target.value) })}
                    className="w-full px-3 py-2 border rounded-xl border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Pipeline Stage</label>
                  <select
                    value={formData.stage_id}
                    onChange={(e) => {
                      const st = STAGES.find((s) => s.id === e.target.value);
                      setFormData({
                        ...formData,
                        stage_id: e.target.value,
                        win_probability_pct: st ? st.probability : 20,
                      });
                    }}
                    className="w-full px-3 py-2 border rounded-xl border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                  >
                    {STAGES.map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.name} ({s.probability}%)
                      </option>
                    ))}
                  </select>
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
                onClick={() => createMutation.mutate(formData)}
                disabled={!formData.title || createMutation.isPending}
                className="px-4 py-2 rounded-xl bg-indigo-600 text-white font-medium hover:bg-indigo-700 disabled:opacity-50 transition"
              >
                {createMutation.isPending ? "Creating..." : "Save Opportunity"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
