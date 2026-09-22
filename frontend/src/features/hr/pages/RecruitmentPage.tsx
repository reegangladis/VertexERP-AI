import React, { useEffect, useState } from "react";
import { Briefcase, Users, Plus, Star, ArrowRight } from "lucide-react";
import { hrApi } from "../api/hrApi";
import { JobApplicant, JobRequisition } from "../types";

export const RecruitmentPage: React.FC = () => {
  const [requisitions, setRequisitions] = useState<JobRequisition[]>([]);
  const [applicants, setApplicants] = useState<JobApplicant[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadATS() {
      try {
        const [reqRes, appRes] = await Promise.allSettled([
          hrApi.getRequisitions(),
          hrApi.getApplicants(),
        ]);
        if (reqRes.status === "fulfilled") setRequisitions(reqRes.value);
        if (appRes.status === "fulfilled") setApplicants(appRes.value);
      } finally {
        setLoading(false);
      }
    }
    loadATS();
  }, []);

  const stages = ["APPLIED", "SCREENING", "INTERVIEW", "OFFER", "HIRED"];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
          <Briefcase className="w-6 h-6 text-blue-400" />
          Recruitment & Applicant Tracking System
        </h1>
        <p className="text-slate-400 text-sm mt-0.5">
          Job requisition approvals, candidate stage pipelines, interview feedback scoring, and job offers.
        </p>
      </div>

      {/* Requisitions List */}
      <div>
        <h2 className="text-base font-bold text-white mb-3">Open Job Openings</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-slate-100">Senior AI Backend Engineer</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400">OPEN</span>
            </div>
            <div className="text-xs text-slate-400">Headcount: 2 • Full-Time (Mid/Senior)</div>
            <div className="text-xs font-mono text-brand-400">$120,000 - $160,000 USD</div>
          </div>
          <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-slate-100">Frontend Architect</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400">OPEN</span>
            </div>
            <div className="text-xs text-slate-400">Headcount: 1 • Full-Time (Senior)</div>
            <div className="text-xs font-mono text-brand-400">$130,000 - $150,000 USD</div>
          </div>
        </div>
      </div>

      {/* Candidate Pipeline Stages */}
      <div>
        <h2 className="text-base font-bold text-white mb-3">Candidate Hiring Pipeline</h2>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          {stages.map((stage) => (
            <div key={stage} className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex flex-col gap-3 min-h-[140px]">
              <div className="flex items-center justify-between text-xs font-bold uppercase tracking-wider text-slate-400 border-b border-slate-800 pb-2">
                <span>{stage}</span>
                <span className="w-5 h-5 rounded-full bg-slate-800 flex items-center justify-center text-[10px] text-slate-300">
                  {stage === "HIRED" ? 1 : 0}
                </span>
              </div>
              {stage === "HIRED" && (
                <div className="p-3 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs space-y-1">
                  <div className="font-semibold text-slate-100">Alice Smith</div>
                  <div className="text-slate-400 text-[11px]">Frontend Architect</div>
                  <div className="flex items-center gap-1 text-amber-400 text-[11px]">
                    <Star className="w-3 h-3 fill-amber-400" />
                    5.0 Rating
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
