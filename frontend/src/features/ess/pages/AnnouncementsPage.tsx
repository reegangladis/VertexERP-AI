import React from "react";
import { Bell, Pin, Calendar, User, ShieldCheck } from "lucide-react";

export const AnnouncementsPage: React.FC = () => {
  const announcements = [
    {
      id: "ANN-001",
      title: "Annual Open Enrollment: Healthcare & Insurance Benefits 2027",
      category: "HR",
      publishedAt: "Nov 20, 2026",
      author: "Sarah Connor (Director of Human Resources)",
      isPinned: true,
      content:
        "The annual healthcare open enrollment window for 2027 is now open through December 15, 2026. Employees can modify health, vision, and dental plans, and adjust 401(k) / PF statutory contributions via the ESS portal.",
    },
    {
      id: "ANN-002",
      title: "Enterprise Town Hall & Q3 Executive Performance Review",
      category: "COMPANY",
      publishedAt: "Nov 15, 2026",
      author: "Leadership Operations Desk",
      isPinned: true,
      content:
        "Join us for our upcoming quarterly global company town hall on Friday, December 04, at 10:00 AM PST. We will review our Q3 financial performance, new product milestones in Vertex AI, and celebrate team promotions.",
    },
    {
      id: "ANN-003",
      title: "Office Holiday Schedule for Thanksgiving & Year-End",
      category: "EVENT",
      publishedAt: "Nov 10, 2026",
      author: "Workplace Experience Team",
      isPinned: false,
      content:
        "Corporate offices will be closed on Thursday, November 26, and Friday, November 27 in observance of Thanksgiving. Please ensure all emergency on-call rotations are scheduled with your engineering leads.",
    },
  ];

  return (
    <div className="space-y-6 max-w-5xl">
      {/* Top Header */}
      <div>
        <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
          <Bell className="w-5 h-5 text-brand-400" />
          <span>Company Announcements & Broadcasts</span>
        </h1>
        <p className="text-xs text-slate-400">
          Official corporate communications, policy updates, and executive notices.
        </p>
      </div>

      {/* Announcements List */}
      <div className="space-y-4">
        {announcements.map((ann) => (
          <div
            key={ann.id}
            className={`p-6 rounded-2xl border transition-all ${
              ann.isPinned
                ? "border-brand-500/50 bg-gradient-to-r from-slate-900/90 to-brand-950/20 shadow-lg shadow-brand-950/40"
                : "border-slate-800 bg-slate-900/60"
            }`}
          >
            <div className="flex items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                {ann.isPinned && (
                  <span className="flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded bg-brand-500/20 text-brand-400 border border-brand-500/30">
                    <Pin className="w-3 h-3 rotate-45" />
                    PINNED
                  </span>
                )}
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                  {ann.category}
                </span>
              </div>
              <span className="text-xs text-slate-500 flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5" />
                {ann.publishedAt}
              </span>
            </div>

            <h3 className="mt-3 text-base font-bold text-slate-100">{ann.title}</h3>
            <p className="mt-2 text-xs text-slate-300 leading-relaxed">{ann.content}</p>

            <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center gap-2 text-[11px] text-slate-400">
              <User className="w-3.5 h-3.5 text-slate-500" />
              <span>Published by {ann.author}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
