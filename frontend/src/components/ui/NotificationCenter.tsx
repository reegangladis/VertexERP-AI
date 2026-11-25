import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Bell, Clock, AlertTriangle, Info, CheckCircle2 } from "lucide-react";
import { cn, formatDateTime } from "@/lib/utils";
import { demoStore, useDemoStore } from "@/lib/demo-store";

export const NotificationCenter: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const navigate = useNavigate();
  const demoState = useDemoStore();
  const notifications = demoState.notifications;

  const unreadCount = notifications.filter((n) => !n.isRead).length;

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/70 rounded-xl transition-colors relative border border-transparent hover:border-zinc-700"
        title="Notifications"
      >
        <Bell className="w-4 h-4" />
        {unreadCount > 0 && (
          <span className="min-w-[16px] h-4 px-1 rounded-full bg-brand-500 text-white text-[9px] font-bold flex items-center justify-center absolute -top-1 -right-1 shadow-md shadow-brand-500/50">
            {unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 sm:w-96 rounded-2xl border border-zinc-800 bg-zinc-900/95 backdrop-blur-xl shadow-2xl z-50 overflow-hidden">
          <div className="px-4 py-3 border-b border-zinc-800 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-zinc-100">Notifications</span>
              {unreadCount > 0 && (
                <span className="px-1.5 py-0.5 rounded-full text-[10px] font-bold bg-brand-500/20 text-brand-300 border border-brand-500/30">
                  {unreadCount} new
                </span>
              )}
            </div>
            {unreadCount > 0 && (
              <button
                onClick={() => demoStore.markAllNotificationsRead()}
                className="text-[11px] text-brand-400 hover:text-brand-300 font-medium"
              >
                Mark all as read
              </button>
            )}
          </div>

          <div className="max-h-80 overflow-y-auto divide-y divide-zinc-800/70">
            {notifications.length === 0 ? (
              <div className="py-8 text-center text-xs text-zinc-500">
                No notifications to display.
              </div>
            ) : (
              notifications.map((item) => (
                <div
                  key={item.id}
                  onClick={() => {
                    demoStore.markNotificationRead(item.id);
                    if (item.link) {
                      navigate(item.link);
                      setIsOpen(false);
                    }
                  }}
                  className={cn(
                    "p-3.5 transition-colors cursor-pointer hover:bg-zinc-800/60 flex gap-3 text-xs",
                    !item.isRead && "bg-brand-500/[0.06]"
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
                  <div className="space-y-1 flex-1">
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-semibold text-zinc-100">{item.title}</span>
                      {!item.isRead && (
                        <span className="w-1.5 h-1.5 rounded-full bg-brand-400 shrink-0" />
                      )}
                    </div>
                    <p className="text-zinc-400 leading-relaxed text-[11px]">{item.message}</p>
                    <div className="text-[10px] text-zinc-500">
                      {formatDateTime(item.createdAt)}
                    </div>
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
