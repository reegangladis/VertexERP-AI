import React, { useEffect, useState } from "react";
import { TrendingUp, Target, Award, CheckCircle2, Star } from "lucide-react";
import { hrApi } from "../api/hrApi";
import { EmployeeGoal, PerformanceReviewPeriod } from "../types";

export const PerformancePage: React.FC = () => {
  const [periods, setPeriods] = useState<PerformanceReviewPeriod[]>([]);
  const [goals, setGoals] = useState<EmployeeGoal[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadPerformance() {
      try {
        const [pRes, gRes] = await Promise.allSettled([
          hrApi.getReviewPeriods(),
          hrApi.getGoals(),
        ]);
        if (pRes.status === "fulfilled") setPeriods(pRes.value);
        if (gRes.status === "fulfilled") setGoals(gRes.value);
      } finally {
        setLoading(false);
      }
    }
    loadPerformance();
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
          <TrendingUp className="w-6 h-6 text-rose-400" />
          Performance Management & OKRs
        </h1>
        <p className="text-slate-400 text-sm mt-0.5">
          Appraisal review cycles, OKR goal setting, and multi-stage evaluation workflows.
        </p>
      </div>

      {/* Review Cycle Banner */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-rose-400">Current Appraisal Cycle</span>
          <div className="text-xl font-bold text-white mt-1">H1 2024 Performance Review Period</div>
          <div className="text-xs text-slate-400 mt-1">Cycle: 2024-01-01 to 2024-06-30 • Status: ACTIVE</div>
        </div>
        <span className="px-3 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
          Evaluation Stage Active
        </span>
      </div>

      {/* OKRs & Goals Tracking */}
      <div className="rounded-xl bg-slate-900 border border-slate-800 p-6 space-y-4">
        <h2 className="text-base font-bold text-white">Active Objectives & Key Results (OKRs)</h2>
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/60 space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <span className="font-semibold text-slate-100">Deliver Complete HR Domain Architecture</span>
                <div className="text-xs text-slate-400 mt-0.5">Weightage: 3.0 • Individual OKR</div>
              </div>
              <span className="text-xs font-bold text-brand-400">75% Completed</span>
            </div>
            <div className="w-full h-2 rounded-full bg-slate-700 overflow-hidden">
              <div className="h-full bg-brand-500 rounded-full" style={{ width: "75%" }} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
