import React from "react";
import { cn, formatDateTime } from "@/lib/utils";
import { CheckCircle2, Clock, XCircle, ArrowLeftCircle, User } from "lucide-react";
import { StatusBadge } from "./StatusBadge";

export interface ApprovalStep {
  id?: string;
  level?: number;
  label?: string;
  step_name?: string;
  approver?: string;
  approverName?: string;
  approverRole?: string;
  status: "PENDING" | "APPROVED" | "REJECTED" | "RETURNED" | "SKIPPED";
  actionDate?: string;
  timestamp?: string;
  comment?: string;
  comments?: string;
}

export interface ApprovalTimelineProps {
  steps: ApprovalStep[];
  className?: string;
}

export const ApprovalTimeline: React.FC<ApprovalTimelineProps> = ({ steps, className }) => {
  return (
    <div className={cn("space-y-4", className)}>
      <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
        Approval Lifecycle Timeline
      </h4>
      <div className="relative pl-6 border-l-2 border-slate-800 space-y-6">
        {steps.map((step, idx) => {
          let Icon = Clock;
          let iconColor = "text-amber-400 bg-amber-500/10 border-amber-500/30";

          if (step.status === "APPROVED") {
            Icon = CheckCircle2;
            iconColor = "text-emerald-400 bg-emerald-500/10 border-emerald-500/30";
          } else if (step.status === "REJECTED") {
            Icon = XCircle;
            iconColor = "text-rose-400 bg-rose-500/10 border-rose-500/30";
          } else if (step.status === "RETURNED") {
            Icon = ArrowLeftCircle;
            iconColor = "text-purple-400 bg-purple-500/10 border-purple-500/30";
          }

          return (
            <div key={step.id || idx} className="relative group">
              {/* Timeline marker icon */}
              <div
                className={cn(
                  "absolute -left-[35px] top-0.5 w-6 h-6 rounded-full border flex items-center justify-center",
                  iconColor
                )}
              >
                <Icon className="w-3.5 h-3.5" />
              </div>

              {/* Step Details */}
              <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-3 text-xs space-y-1.5">
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-1.5">
                    <User className="w-3.5 h-3.5 text-slate-400" />
                    <span className="font-semibold text-slate-200">{step.approverName || step.approver || step.label || "Reviewer"}</span>
                    {step.approverRole && (
                      <span className="text-slate-400">({step.approverRole})</span>
                    )}
                  </div>
                  <StatusBadge status={step.status} />
                </div>

                {(step.actionDate || step.timestamp) && (
                  <div className="text-[11px] text-slate-500">
                    Action logged: {formatDateTime(step.actionDate || step.timestamp || "")}
                  </div>
                )}

                {(step.comments || step.comment) && (
                  <p className="mt-1 text-slate-300 italic bg-slate-800/40 p-2 rounded border border-slate-800">
                    "{step.comments || step.comment}"
                  </p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
