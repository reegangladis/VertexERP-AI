import React from "react";
import { cn, formatDateTime } from "@/lib/utils";
import { Phone, Users, Mail, CheckSquare, FileText, Calendar } from "lucide-react";

export interface ActivityItem {
  id: string;
  type: "CALL" | "MEETING" | "EMAIL" | "TASK" | "NOTE" | "FOLLOW_UP";
  subject: string;
  description?: string;
  assignedTo?: string;
  dueDate?: string;
  completedAt?: string;
  status?: string;
}

export interface ActivityTimelineProps {
  activities: ActivityItem[];
  onAddActivity?: () => void;
  className?: string;
}

export const ActivityTimeline: React.FC<ActivityTimelineProps> = ({
  activities,
  onAddActivity,
  className,
}) => {
  const getIcon = (type: ActivityItem["type"]) => {
    switch (type) {
      case "CALL":
        return <Phone className="w-3.5 h-3.5 text-blue-400" />;
      case "MEETING":
        return <Users className="w-3.5 h-3.5 text-purple-400" />;
      case "EMAIL":
        return <Mail className="w-3.5 h-3.5 text-amber-400" />;
      case "TASK":
        return <CheckSquare className="w-3.5 h-3.5 text-emerald-400" />;
      case "FOLLOW_UP":
        return <Calendar className="w-3.5 h-3.5 text-cyan-400" />;
      default:
        return <FileText className="w-3.5 h-3.5 text-slate-400" />;
    }
  };

  return (
    <div className={cn("space-y-4", className)}>
      <div className="flex items-center justify-between">
        <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          Interaction & Activity History
        </h4>
        {onAddActivity && (
          <button
            onClick={onAddActivity}
            className="text-xs text-brand-400 hover:text-brand-300 font-medium"
          >
            + Log Activity
          </button>
        )}
      </div>

      {activities.length === 0 ? (
        <div className="text-xs text-slate-500 py-4 text-center italic bg-slate-900/30 rounded-lg border border-slate-800">
          No activities logged yet.
        </div>
      ) : (
        <div className="relative pl-6 border-l-2 border-slate-800 space-y-4">
          {activities.map((act) => (
            <div key={act.id} className="relative group">
              <div className="absolute -left-[35px] top-1 w-6 h-6 rounded-full border border-slate-700 bg-slate-900 flex items-center justify-center">
                {getIcon(act.type)}
              </div>

              <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-3 text-xs space-y-1">
                <div className="flex items-center justify-between gap-2">
                  <span className="font-semibold text-slate-200">{act.subject}</span>
                  <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                    {act.type}
                  </span>
                </div>

                {act.description && (
                  <p className="text-slate-300 leading-relaxed">{act.description}</p>
                )}

                <div className="pt-1 flex flex-wrap items-center gap-3 text-[11px] text-slate-500">
                  {act.dueDate && <span>Due: {formatDateTime(act.dueDate)}</span>}
                  {act.completedAt && <span>Completed: {formatDateTime(act.completedAt)}</span>}
                  {act.assignedTo && <span>Owner: {act.assignedTo}</span>}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
