import React, { useState } from "react";
import { Bell, Check, Clock, AlertTriangle, Info, CheckCircle2 } from "lucide-react";
import { cn, formatDateTime } from "@/lib/utils";

export interface NotificationItem {
  id: string;
  title: string;
  message: string;
  type: "INFO" | "WARNING" | "ACTION_REQUIRED" | "SUCCESS";
  createdAt: string;
  isRead: boolean;
  link?: string;
}

const mockNotifications: NotificationItem[] = [
  {
    id: "notif-1",
    title: "Leave Request Submitted",
    message: "Sarah Connor has requested 2 days of Casual Leave pending review.",
    type: "ACTION_REQUIRED",
    createdAt: new Date().toISOString(),
    isRead: false,
    link: "/admin/approvals",
  },
  {
    id: "notif-2",
    title: "Payroll Run Completed",
    message: "Monthly payroll batch for November 2026 was processed successfully.",
    type: "SUCCESS",
    createdAt: new Date(Date.now() - 3600000).toISOString(),
    isRead: false,
    link: "/admin/hr/payroll",
  },
  {
    id: "notif-3",
    title: "Overdue Lead Follow-Up",
    message: "Follow-up meeting with Cyberdyne Systems is overdue by 1 day.",
    type: "WARNING",
    createdAt: new Date(Date.now() - 86400000).toISOString(),
    isRead: true,
    link: "/admin/crm/leads",
  },
];

export const NotificationCenter: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState<NotificationItem[]>(mockNotifications);

  const unreadCount = notifications.filter((n) => !n.isRead).length;

  const markAllRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, isRead: true })));
  };

  const markAsRead = (id: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, isRead: true } : n))
    );
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 rounded-lg transition-colors relative"
        title="Notifications"
      >
        <Bell className="w-4 h-4" />
        {unreadCount > 0 && (
          <span className="w-2 h-2 rounded-full bg-brand-500 absolute top-1.5 right-1.5 animate-pulse" />
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 sm:w-96 rounded-xl border border-slate-800 bg-slate-900/95 backdrop-blur-xl shadow-2xl z-50 overflow-hidden">
          <div className="px-4 py-3 border-b border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-slate-200">Notifications</span>
              {unreadCount > 0 && (
                <span className="px-1.5 py-0.5 rounded-full text-[10px] font-bold bg-brand-500/20 text-brand-400 border border-brand-500/30">
                  {unreadCount} new
                </span>
              )}
            </div>
            {unreadCount > 0 && (
              <button
                onClick={markAllRead}
                className="text-[11px] text-brand-400 hover:text-brand-300 font-medium"
              >
                Mark all as read
              </button>
            )}
          </div>

          <div className="max-h-80 overflow-y-auto divide-y divide-slate-800/60">
            {notifications.length === 0 ? (
              <div className="py-8 text-center text-xs text-slate-500">
                No notifications to display.
              </div>
            ) : (
              notifications.map((item) => (
                <div
                  key={item.id}
                  onClick={() => markAsRead(item.id)}
                  className={cn(
                    "p-3.5 transition-colors cursor-pointer hover:bg-slate-800/40 flex gap-3 text-xs",
                    !item.isRead && "bg-brand-500/[0.03]"
                  )}
                >
                  <div className="mt-0.5 shrink-0">
                    {item.type === "ACTION_REQUIRED" && (
                      <Clock className="w-4 h-4 text-amber-400" />
                    )}
                    {item.type === "SUCCESS" && (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    )}
                    {item.type === "WARNING" && (
                      <AlertTriangle className="w-4 h-4 text-rose-400" />
                    )}
                    {item.type === "INFO" && <Info className="w-4 h-4 text-brand-400" />}
                  </div>

                  <div className="flex-1 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-200">{item.title}</span>
                      <span className="text-[10px] text-slate-500">
                        {formatDateTime(item.createdAt)}
                      </span>
                    </div>
                    <p className="text-slate-400 text-[11px] leading-relaxed">{item.message}</p>
                    {item.link && (
                      <a
                        href={item.link}
                        className="inline-block text-[11px] text-brand-400 hover:underline pt-0.5"
                      >
                        View Details &rarr;
                      </a>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};
