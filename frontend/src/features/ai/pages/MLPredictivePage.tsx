import React, { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { aiApi } from "../api/aiApi";
import { StatCard } from "@/components/ui/StatCard";
import { StatusBadge } from "@/components/ui/StatusBadge";
import {
  Brain,
  Target,
  UserX,
  TrendingUp,
  Sparkles,
  ShieldAlert,
  ArrowRight,
  CheckCircle2,
  AlertTriangle,
} from "lucide-react";

export const MLPredictivePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"LEAD_SCORING" | "ATTRITION">("LEAD_SCORING");

  // Lead Scoring State
  const [leadForm, setLeadForm] = useState({
    industry: "Technology",
    company_size: 250,
    estimated_budget: 65000,
    lead_source: "DIRECT",
    interaction_count: 5,
    decision_maker_identified: true,
  });

  // Attrition State
  const [attritionForm, setAttritionForm] = useState({
    tenure_months: 28,
    monthly_overtime_hours: 14,
    months_since_last_promotion: 26,
    satisfaction_survey_score: 3.2,
    compensation_ratio_to_market: 0.9,
    leaves_taken_last_quarter: 3,
  });

  const leadScoreMutation = useMutation({
    mutationFn: aiApi.scoreLead,
  });

  const attritionMutation = useMutation({
    mutationFn: aiApi.predictAttritionRisk,
  });

  const handleScoreLead = (e: React.FormEvent) => {
    e.preventDefault();
    leadScoreMutation.mutate(leadForm);
  };

  const handlePredictAttrition = (e: React.FormEvent) => {
    e.preventDefault();
    attritionMutation.mutate(attritionForm);
  };

  const leadResult = leadScoreMutation.data;
  const attritionResult = attritionMutation.data;

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div>
        <h1 className="text-2xl font-bold text-zinc-100 tracking-tight flex items-center gap-2.5">
          <Brain className="w-7 h-7 text-brand-400" />
          <span>Predictive Machine Learning Workbench</span>
        </h1>
        <p className="text-sm text-zinc-400">
          Supervised predictive models for Deal Lead Scoring and Employee Retention & Attrition Risk.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-3 border-b border-zinc-800 pb-3">
        <button
          onClick={() => setActiveTab("LEAD_SCORING")}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition ${
            activeTab === "LEAD_SCORING"
              ? "bg-brand-600 text-white shadow-sm"
              : "bg-zinc-900/80 text-zinc-300 border border-zinc-800 hover:bg-zinc-950/70"
          }`}
        >
          <Target className="w-4 h-4" />
          <span>Lead Conversion Scoring</span>
        </button>
        <button
          onClick={() => setActiveTab("ATTRITION")}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition ${
            activeTab === "ATTRITION"
              ? "bg-brand-600 text-white shadow-sm"
              : "bg-zinc-900/80 text-zinc-300 border border-zinc-800 hover:bg-zinc-950/70"
          }`}
        >
          <UserX className="w-4 h-4" />
          <span>Employee Attrition Risk</span>
        </button>
      </div>

      {/* Tab 1: Lead Conversion Scoring */}
      {activeTab === "LEAD_SCORING" && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Input Parameters Form */}
          <div className="lg:col-span-5 bg-zinc-900/80 p-6 rounded-2xl border border-zinc-800 shadow-sm space-y-4">
            <div className="border-b border-zinc-800/80 pb-3">
              <h2 className="font-bold text-zinc-100 text-base">Opportunity Attributes</h2>
              <p className="text-xs text-zinc-400">Adjust candidate parameters to evaluate win propensity.</p>
            </div>

            <form onSubmit={handleScoreLead} className="space-y-3.5 text-xs">
              <div>
                <label className="block font-semibold text-zinc-300 mb-1">Target Industry</label>
                <select
                  value={leadForm.industry}
                  onChange={(e) => setLeadForm({ ...leadForm, industry: e.target.value })}
                  className="w-full px-3 py-2 border rounded-xl border-zinc-800 text-xs focus:ring-2 focus:ring-indigo-500/20"
                >
                  <option value="Technology">Technology & SaaS</option>
                  <option value="Healthcare">Healthcare & Bio</option>
                  <option value="Financial Services">Financial Services & Banking</option>
                  <option value="Manufacturing">Manufacturing & Supply Chain</option>
                  <option value="Retail">Retail & E-commerce</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-zinc-300 mb-1">Company Size (Employees)</label>
                  <input
                    type="number"
                    value={leadForm.company_size}
                    onChange={(e) => setLeadForm({ ...leadForm, company_size: Number(e.target.value) })}
                    className="w-full px-3 py-2 bg-zinc-950 text-zinc-100 border rounded-xl border-zinc-800 text-xs focus:outline-none focus:border-brand-500"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-zinc-300 mb-1">Budget Allocation ($)</label>
                  <input
                    type="number"
                    value={leadForm.estimated_budget}
                    onChange={(e) => setLeadForm({ ...leadForm, estimated_budget: Number(e.target.value) })}
                    className="w-full px-3 py-2 bg-zinc-950 text-zinc-100 border rounded-xl border-zinc-800 text-xs focus:outline-none focus:border-brand-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-zinc-300 mb-1">Acquisition Source</label>
                  <select
                    value={leadForm.lead_source}
                    onChange={(e) => setLeadForm({ ...leadForm, lead_source: e.target.value })}
                    className="w-full px-3 py-2 bg-zinc-950 text-zinc-100 border rounded-xl border-zinc-800 text-xs focus:outline-none focus:border-brand-500"
                  >
                    <option value="DIRECT">Direct Inbound</option>
                    <option value="REFERRAL">Partner Referral</option>
                    <option value="OUTBOUND">Outbound Campaign</option>
                    <option value="EVENT">Trade Exhibition</option>
                  </select>
                </div>
                <div>
                  <label className="block font-semibold text-zinc-300 mb-1">Engagements / Touchpoints</label>
                  <input
                    type="number"
                    value={leadForm.interaction_count}
                    onChange={(e) => setLeadForm({ ...leadForm, interaction_count: Number(e.target.value) })}
                    className="w-full px-3 py-2 bg-zinc-950 text-zinc-100 border rounded-xl border-zinc-800 text-xs focus:outline-none focus:border-brand-500"
                  />
                </div>
              </div>

              <div className="flex items-center gap-2 pt-1">
                <input
                  type="checkbox"
                  id="decision_maker"
                  checked={leadForm.decision_maker_identified}
                  onChange={(e) => setLeadForm({ ...leadForm, decision_maker_identified: e.target.checked })}
                  className="rounded border-zinc-700 text-brand-400"
                />
                <label htmlFor="decision_maker" className="font-medium text-zinc-200">
                  C-Level / Budget Signer explicitly identified
                </label>
              </div>

              <button
                type="submit"
                disabled={leadScoreMutation.isPending}
                className="w-full mt-4 py-2.5 rounded-xl bg-brand-600 text-white font-bold hover:bg-brand-500 transition flex items-center justify-center gap-2 shadow-sm"
              >
                <Sparkles className="w-4 h-4" />
                <span>{leadScoreMutation.isPending ? "Scoring Model Running..." : "Execute Lead Scoring"}</span>
              </button>
            </form>
          </div>

          {/* Model Inference Results */}
          <div className="lg:col-span-7 space-y-4">
            {!leadResult && !leadScoreMutation.isPending && (
              <div className="bg-zinc-900/80 p-12 rounded-2xl border border-zinc-800 shadow-sm text-center space-y-3">
                <Target className="w-12 h-12 text-slate-300 mx-auto" />
                <h3 className="font-bold text-zinc-200 text-base">Inference Ready</h3>
                <p className="text-xs text-slate-400 max-w-sm mx-auto">
                  Click "Execute Lead Scoring" to run the calibrated feature pipeline and generate win probability.
                </p>
              </div>
            )}

            {leadResult && (
              <div className="bg-zinc-900/80 p-6 rounded-2xl border border-zinc-800 shadow-sm space-y-5">
                <div className="flex items-center justify-between border-b border-zinc-800/80 pb-4">
                  <div>
                    <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Model Assessment</span>
                    <div className="flex items-center gap-3 mt-1">
                      <span className="text-4xl font-extrabold text-zinc-100">{leadResult.score}</span>
                      <span className="text-xs text-slate-400 font-bold">/ 100</span>
                      <span
                        className={`text-xs font-bold px-2.5 py-1 rounded-full ${
                          leadResult.rating === "HOT"
                            ? "bg-rose-500/15 text-rose-300 border border-rose-500/30"
                            : leadResult.rating === "WARM"
                            ? "bg-amber-500/15 text-amber-300 border border-amber-500/30"
                            : "bg-zinc-800/80 text-zinc-200"
                        }`}
                      >
                        {leadResult.rating} LEAD
                      </span>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-semibold text-slate-400 uppercase">Win Probability</span>
                    <div className="text-2xl font-bold text-brand-400 mt-1">
                      {Math.round(leadResult.win_probability * 100)}%
                    </div>
                  </div>
                </div>

                {/* Strategic Recommended Action */}
                <div className="p-4 rounded-xl bg-brand-500/15/70 border border-indigo-100">
                  <div className="text-xs font-bold text-indigo-900 uppercase tracking-wide">AI Recommendation</div>
                  <div className="text-xs text-indigo-800 mt-1 font-medium">{leadResult.recommended_action}</div>
                </div>

                {/* Feature Drivers Breakdown */}
                <div>
                  <h4 className="text-xs font-bold text-zinc-100 uppercase tracking-wider mb-2.5">
                    Feature Impact Weights
                  </h4>
                  <div className="space-y-2">
                    {leadResult.key_factors.map((f: any, idx: number) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between p-2.5 rounded-xl bg-zinc-950/70 border border-zinc-800/80 text-xs"
                      >
                        <div className="flex items-center gap-2">
                          {f.impact === "POSITIVE" ? (
                            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                          ) : (
                            <AlertTriangle className="w-4 h-4 text-amber-400" />
                          )}
                          <span className="font-semibold text-zinc-100">{f.factor}</span>
                        </div>
                        <span
                          className={`font-bold ${
                            f.impact === "POSITIVE" ? "text-emerald-300" : "text-amber-300"
                          }`}
                        >
                          {f.impact === "POSITIVE" ? `+${f.weight_pct}%` : `-${f.weight_pct}%`}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 2: Employee Attrition Risk */}
      {activeTab === "ATTRITION" && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Input Parameters Form */}
          <div className="lg:col-span-5 bg-zinc-900/80 p-6 rounded-2xl border border-zinc-800 shadow-sm space-y-4">
            <div className="border-b border-zinc-800/80 pb-3">
              <h2 className="font-bold text-zinc-100 text-base">Employee Engagement Profile</h2>
              <p className="text-xs text-zinc-400">Telemetry variables for predictive churn analysis.</p>
            </div>

            <form onSubmit={handlePredictAttrition} className="space-y-3.5 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-zinc-300 mb-1">Company Tenure (Months)</label>
                  <input
                    type="number"
                    value={attritionForm.tenure_months}
                    onChange={(e) =>
                      setAttritionForm({ ...attritionForm, tenure_months: Number(e.target.value) })
                    }
                    className="w-full px-3 py-2 bg-zinc-950 text-zinc-100 border rounded-xl border-zinc-800 text-xs focus:outline-none focus:border-brand-500"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-zinc-300 mb-1">Monthly Overtime (Hours)</label>
                  <input
                    type="number"
                    value={attritionForm.monthly_overtime_hours}
                    onChange={(e) =>
                      setAttritionForm({ ...attritionForm, monthly_overtime_hours: Number(e.target.value) })
                    }
                    className="w-full px-3 py-2 bg-zinc-950 text-zinc-100 border rounded-xl border-zinc-800 text-xs focus:outline-none focus:border-brand-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-zinc-300 mb-1">Months Since Promotion</label>
                  <input
                    type="number"
                    value={attritionForm.months_since_last_promotion}
                    onChange={(e) =>
                      setAttritionForm({
                        ...attritionForm,
                        months_since_last_promotion: Number(e.target.value),
                      })
                    }
                    className="w-full px-3 py-2 bg-zinc-950 text-zinc-100 border rounded-xl border-zinc-800 text-xs focus:outline-none focus:border-brand-500"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-zinc-300 mb-1">Satisfaction Score (1-5)</label>
                  <input
                    type="number"
                    step="0.1"
                    min="1"
                    max="5"
                    value={attritionForm.satisfaction_survey_score}
                    onChange={(e) =>
                      setAttritionForm({
                        ...attritionForm,
                        satisfaction_survey_score: Number(e.target.value),
                      })
                    }
                    className="w-full px-3 py-2 bg-zinc-950 text-zinc-100 border rounded-xl border-zinc-800 text-xs focus:outline-none focus:border-brand-500"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold text-zinc-300 mb-1">
                  Compensation Ratio vs Market (e.g. 1.0 = at par)
                </label>
                <input
                  type="number"
                  step="0.05"
                  min="0.5"
                  max="2.0"
                  value={attritionForm.compensation_ratio_to_market}
                  onChange={(e) =>
                    setAttritionForm({
                      ...attritionForm,
                      compensation_ratio_to_market: Number(e.target.value),
                    })
                  }
                  className="w-full px-3 py-2 bg-zinc-950 text-zinc-100 border rounded-xl border-zinc-800 text-xs focus:outline-none focus:border-brand-500"
                />
              </div>

              <button
                type="submit"
                disabled={attritionMutation.isPending}
                className="w-full mt-4 py-2.5 rounded-xl bg-rose-600 text-white font-bold hover:bg-rose-700 transition flex items-center justify-center gap-2 shadow-sm"
              >
                <ShieldAlert className="w-4 h-4" />
                <span>{attritionMutation.isPending ? "Calculating Risk..." : "Predict Attrition Probability"}</span>
              </button>
            </form>
          </div>

          {/* Model Inference Results */}
          <div className="lg:col-span-7 space-y-4">
            {!attritionResult && !attritionMutation.isPending && (
              <div className="bg-zinc-900/80 p-12 rounded-2xl border border-zinc-800 shadow-sm text-center space-y-3">
                <UserX className="w-12 h-12 text-slate-300 mx-auto" />
                <h3 className="font-bold text-zinc-200 text-base">Retention Analysis Ready</h3>
                <p className="text-xs text-slate-400 max-w-sm mx-auto">
                  Evaluate behavioral risk factors to predict employee flight risk and generate intervention strategies.
                </p>
              </div>
            )}

            {attritionResult && (
              <div className="bg-zinc-900/80 p-6 rounded-2xl border border-zinc-800 shadow-sm space-y-5">
                <div className="flex items-center justify-between border-b border-zinc-800/80 pb-4">
                  <div>
                    <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Attrition Risk Level</span>
                    <div className="flex items-center gap-3 mt-1">
                      <span className="text-4xl font-extrabold text-zinc-100">{attritionResult.risk_score}</span>
                      <span className="text-xs text-slate-400 font-bold">/ 100</span>
                      <span
                        className={`text-xs font-bold px-2.5 py-1 rounded-full ${
                          attritionResult.risk_level === "HIGH"
                            ? "bg-rose-100 text-rose-800 border border-rose-500/40"
                            : attritionResult.risk_level === "MEDIUM"
                            ? "bg-amber-100 text-amber-800 border border-amber-500/40"
                            : "bg-emerald-100 text-emerald-800 border border-emerald-500/40"
                        }`}
                      >
                        {attritionResult.risk_level} RISK
                      </span>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-semibold text-slate-400 uppercase">Churn Probability</span>
                    <div className="text-2xl font-bold text-rose-400 mt-1">
                      {Math.round(attritionResult.churn_probability * 100)}%
                    </div>
                  </div>
                </div>

                {/* Risk Drivers */}
                <div>
                  <h4 className="text-xs font-bold text-zinc-100 uppercase tracking-wider mb-2">
                    Identified Risk Factors
                  </h4>
                  <ul className="space-y-1.5 text-xs text-zinc-200">
                    {attritionResult.risk_drivers.map((d: string, idx: number) => (
                      <li key={idx} className="flex items-start gap-2 bg-rose-500/15/60 p-2 rounded-lg border border-rose-100">
                        <AlertTriangle className="w-3.5 h-3.5 text-rose-400 mt-0.5 flex-shrink-0" />
                        <span>{d}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Retention Strategies */}
                <div>
                  <h4 className="text-xs font-bold text-zinc-100 uppercase tracking-wider mb-2">
                    Recommended Retention Interventions
                  </h4>
                  <ul className="space-y-1.5 text-xs text-zinc-200">
                    {attritionResult.retention_strategies.map((s: string, idx: number) => (
                      <li key={idx} className="flex items-start gap-2 bg-emerald-500/15/60 p-2 rounded-lg border border-emerald-100">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 mt-0.5 flex-shrink-0" />
                        <span>{s}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
