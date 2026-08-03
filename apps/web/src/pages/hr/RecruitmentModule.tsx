import React, { useState } from 'react';
import {
  Briefcase,
  Users,
  UserPlus,
  Calendar,
  CheckCircle2,
  XCircle,
  Plus,
  Search,
  Filter,
  FileText,
  Award,
  TrendingUp,
  Clock,
  ExternalLink,
  Star,
  ChevronRight,
  Send,
  UserCheck,
  Building,
  Check,
  X,
  Layers,
} from 'lucide-react';

const mockRequisitions = [
  { id: 'req1', title: 'Senior AI & Cloud Architect', code: 'REQ-AI-01', vacancies: 2, priority: 'High', budget: '$150,000', status: 'Approved', department: 'Engineering' },
  { id: 'req2', title: 'Lead Full Stack Engineer (React/FastAPI)', code: 'REQ-FS-02', vacancies: 3, priority: 'Urgent', budget: '$130,000', status: 'Open', department: 'Product' },
];

const mockPipelineCandidates = [
  { id: 'c1', name: 'Sarah Connor', role: 'Senior AI Architect', stage: 'Interview', exp: '6.5 yrs', rating: 4.8, source: 'LinkedIn', email: 'sarah.c@sky.net' },
  { id: 'c2', name: 'Alex Rivera', role: 'Lead Full Stack Engineer', stage: 'Screening', exp: '5.0 yrs', rating: 4.2, source: 'Career Portal', email: 'alex.r@dev.io' },
  { id: 'c3', name: 'Elena Rostova', role: 'Senior AI Architect', stage: 'Offer', exp: '8.0 yrs', rating: 4.9, source: 'Referral', email: 'elena@ai-labs.org' },
  { id: 'c4', name: 'David Kim', role: 'DevOps Engineer', stage: 'Hired', exp: '4.5 yrs', rating: 4.6, source: 'Indeed', email: 'dkim@cloud.com' },
];

const mockInterviewsToday = [
  { id: 'int1', candidate: 'Sarah Connor', round: 'System Architecture Deep-Dive', type: 'Technical', time: '02:00 PM - 03:00 PM', interviewer: 'John Doe (Lead Arch)' },
  { id: 'int2', candidate: 'Alex Rivera', round: 'Engineering Leadership Interview', type: 'Managerial', time: '04:00 PM - 05:00 PM', interviewer: 'Jane Smith (VP Eng)' },
];

const stages = ['Applied', 'Screening', 'Interview', 'Offer', 'Hired'];

export function RecruitmentModule() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'requisitions' | 'pipeline' | 'interviews' | 'offers'>('dashboard');
  const [isAddReqModalOpen, setIsAddReqModalOpen] = useState(false);
  const [reqTitle, setReqTitle] = useState('');
  const [vacancies, setVacancies] = useState(1);
  const [priority, setPriority] = useState('High');

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-purple-950 via-slate-900 to-purple-950 rounded-xl p-6 text-white shadow-xl border border-purple-900/40">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-purple-400 font-mono text-xs uppercase tracking-wider font-semibold mb-1">
              <Briefcase className="w-4 h-4" /> Phase 8 — Enterprise Recruitment & Talent Acquisition
            </div>
            <h1 className="text-2xl font-bold tracking-tight">Talent Acquisition & Hiring Hub</h1>
            <p className="text-sm text-slate-300 mt-1">
              Job requisitions, candidate pipeline tracking, multi-round interviews, feedback scoring & offer conversions.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsAddReqModalOpen(true)}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold rounded-lg shadow-md transition flex items-center gap-2"
            >
              <Plus className="w-4 h-4" /> Create Requisition
            </button>
          </div>
        </div>

        {/* Sub-Navigation Tabs */}
        <div className="flex items-center gap-2 mt-6 overflow-x-auto border-t border-slate-800/80 pt-4 scrollbar-none">
          {[
            { id: 'dashboard', label: 'Recruitment Overview', icon: <TrendingUp className="w-3.5 h-3.5" /> },
            { id: 'requisitions', label: 'Job Requisitions & Openings', icon: <Briefcase className="w-3.5 h-3.5" /> },
            { id: 'pipeline', label: 'Candidate Pipeline Kanban', icon: <Users className="w-3.5 h-3.5" /> },
            { id: 'interviews', label: 'Interview Schedule & Feedback', icon: <Calendar className="w-3.5 h-3.5" /> },
            { id: 'offers', label: 'Job Offers & Onboarding', icon: <Award className="w-3.5 h-3.5" /> },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition flex items-center gap-1.5 whitespace-nowrap ${
                activeTab === tab.id
                  ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* 1. OVERVIEW VIEW */}
      {activeTab === 'dashboard' && (
        <div className="space-y-6">
          {/* KPI Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-card p-5 rounded-xl border border-border shadow-sm space-y-2">
              <div className="flex items-center justify-between text-muted-foreground">
                <span className="text-xs font-medium">Open Positions</span>
                <Briefcase className="w-4 h-4 text-purple-500" />
              </div>
              <h3 className="text-2xl font-extrabold text-foreground">5 Vacancies</h3>
              <p className="text-[10px] text-purple-400 font-mono">2 Active Requisitions</p>
            </div>

            <div className="bg-card p-5 rounded-xl border border-border shadow-sm space-y-2">
              <div className="flex items-center justify-between text-muted-foreground">
                <span className="text-xs font-medium">Active Candidates in Pipeline</span>
                <Users className="w-4 h-4 text-sky-500" />
              </div>
              <h3 className="text-2xl font-extrabold text-foreground">24 Candidates</h3>
              <p className="text-[10px] text-sky-500 font-mono">Across 5 Stages</p>
            </div>

            <div className="bg-card p-5 rounded-xl border border-border shadow-sm space-y-2">
              <div className="flex items-center justify-between text-muted-foreground">
                <span className="text-xs font-medium">Interviews Scheduled Today</span>
                <Calendar className="w-4 h-4 text-amber-500" />
              </div>
              <h3 className="text-2xl font-extrabold text-foreground">2 Sessions</h3>
              <p className="text-[10px] text-amber-500 font-mono">Technical & Management</p>
            </div>

            <div className="bg-card p-5 rounded-xl border border-border shadow-sm space-y-2">
              <div className="flex items-center justify-between text-muted-foreground">
                <span className="text-xs font-medium">Avg. Time-to-Hire</span>
                <Clock className="w-4 h-4 text-emerald-500" />
              </div>
              <h3 className="text-2xl font-extrabold text-foreground">18.5 Days</h3>
              <p className="text-[10px] text-emerald-500 font-mono">Industry Top Tier Benchmark</p>
            </div>
          </div>

          {/* Grid Layout: Interviews Today & Funnel Metrics */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Interviews Today */}
            <div className="lg:col-span-2 bg-card p-5 rounded-xl border border-border shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-purple-500" /> Today's Interview Schedule
                </h3>
                <span className="text-xs text-purple-400 font-mono font-semibold">August 03, 2026</span>
              </div>
              <div className="space-y-3">
                {mockInterviewsToday.map((int) => (
                  <div key={int.id} className="p-4 bg-secondary/20 rounded-xl border border-border/60 flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="text-xs font-bold text-foreground">{int.candidate}</p>
                        <span className="px-2 py-0.5 bg-purple-500/10 text-purple-400 text-[10px] font-bold rounded">
                          {int.type}
                        </span>
                      </div>
                      <p className="text-[11px] text-muted-foreground mt-0.5">
                        {int.round} — <span className="font-semibold text-foreground">{int.time}</span>
                      </p>
                      <p className="text-[10px] text-muted-foreground mt-1">Interviewer: {int.interviewer}</p>
                    </div>
                    <button className="px-3 py-1.5 bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold rounded-lg transition">
                      Join Video Call
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* Funnel Stage Breakdown */}
            <div className="bg-card p-5 rounded-xl border border-border shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
                  <Layers className="w-4 h-4 text-sky-500" /> Hiring Pipeline Funnel
                </h3>
              </div>
              <div className="space-y-3">
                {[
                  { stage: 'Applied / Sourced', count: 15, pct: '100%' },
                  { stage: 'Screening', count: 8, pct: '53%' },
                  { stage: 'Technical & Panel', count: 5, pct: '33%' },
                  { stage: 'Offer Extended', count: 2, pct: '13%' },
                  { stage: 'Hired & Converted', count: 5, pct: '33%' },
                ].map((f, idx) => (
                  <div key={idx} className="space-y-1">
                    <div className="flex justify-between text-xs font-medium">
                      <span className="text-muted-foreground">{f.stage}</span>
                      <span className="font-bold text-foreground">{f.count} candidates</span>
                    </div>
                    <div className="w-full bg-secondary/50 rounded-full h-1.5 overflow-hidden">
                      <div className="bg-purple-500 h-full" style={{ width: f.pct }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 2. PIPELINE KANBAN VIEW */}
      {activeTab === 'pipeline' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-foreground">Candidate Recruitment Pipeline</h3>
            <span className="text-xs text-muted-foreground font-mono">4 Candidates in Active View</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {stages.map((stg) => {
              const candsInStage = mockPipelineCandidates.filter((c) => c.stage === stg);
              return (
                <div key={stg} className="bg-card p-4 rounded-xl border border-border/70 space-y-3 min-h-[400px]">
                  <div className="flex items-center justify-between border-b border-border pb-2">
                    <span className="text-xs font-bold text-foreground">{stg}</span>
                    <span className="px-2 py-0.5 bg-secondary text-muted-foreground text-[10px] font-bold rounded-full">
                      {candsInStage.length}
                    </span>
                  </div>

                  <div className="space-y-3">
                    {candsInStage.map((cand) => (
                      <div key={cand.id} className="p-3 bg-secondary/30 rounded-xl border border-border/60 hover:border-purple-500/50 transition cursor-pointer space-y-2">
                        <div className="flex items-center justify-between">
                          <p className="text-xs font-bold text-foreground">{cand.name}</p>
                          <div className="flex items-center gap-0.5 text-amber-500 text-[11px] font-bold">
                            <Star className="w-3 h-3 fill-amber-500" /> {cand.rating}
                          </div>
                        </div>
                        <p className="text-[11px] text-muted-foreground">{cand.role}</p>
                        <div className="flex items-center justify-between pt-1 border-t border-border/40 text-[10px] text-muted-foreground font-mono">
                          <span>{cand.exp}</span>
                          <span className="text-purple-400 font-semibold">{cand.source}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* CREATE REQUISITION MODAL */}
      {isAddReqModalOpen && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-card w-full max-w-lg rounded-2xl border border-border shadow-2xl p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <h3 className="text-base font-bold text-foreground flex items-center gap-2">
                <Briefcase className="w-5 h-5 text-purple-500" /> Create Job Requisition
              </h3>
              <button onClick={() => setIsAddReqModalOpen(false)} className="text-muted-foreground hover:text-foreground">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold mb-1">Position Title</label>
                <input
                  type="text"
                  value={reqTitle}
                  onChange={(e) => setReqTitle(e.target.value)}
                  placeholder="e.g. Lead Software Engineer"
                  className="w-full p-2.5 rounded-lg border border-border bg-background text-foreground"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block font-semibold mb-1">Vacancies</label>
                  <input
                    type="number"
                    value={vacancies}
                    onChange={(e) => setVacancies(Number(e.target.value))}
                    className="w-full p-2.5 rounded-lg border border-border bg-background text-foreground"
                  />
                </div>
                <div>
                  <label className="block font-semibold mb-1">Priority</label>
                  <select
                    value={priority}
                    onChange={(e) => setPriority(e.target.value)}
                    className="w-full p-2.5 rounded-lg border border-border bg-background text-foreground"
                  >
                    <option>Low</option>
                    <option>Medium</option>
                    <option>High</option>
                    <option>Urgent</option>
                  </select>
                </div>
              </div>

              <div className="p-3 bg-purple-500/10 rounded-lg border border-purple-500/20 text-purple-400 font-mono text-[11px]">
                ℹ Submitting this requisition will route it for department head & budget approval.
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-3 border-t border-border">
              <button
                onClick={() => setIsAddReqModalOpen(false)}
                className="px-4 py-2 bg-secondary text-foreground text-xs font-semibold rounded-lg hover:bg-secondary/80"
              >
                Cancel
              </button>
              <button
                onClick={() => setIsAddReqModalOpen(false)}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold rounded-lg shadow transition"
              >
                Submit Requisition
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default RecruitmentModule;
