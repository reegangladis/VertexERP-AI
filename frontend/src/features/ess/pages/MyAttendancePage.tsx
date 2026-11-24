import React, { useState } from "react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { Input } from "@/components/ui/Input";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Calendar, ChevronLeft, ChevronRight, Clock, AlertCircle, CheckCircle2 } from "lucide-react";

export const MyAttendancePage: React.FC = () => {
  const [selectedMonth, setSelectedMonth] = useState("November 2026");
  const [isRegularizeOpen, setIsRegularizeOpen] = useState(false);
  const [selectedDay, setSelectedDay] = useState<number | null>(23);

  // Form state for regularization
  const [regDate, setRegDate] = useState("2026-11-20");
  const [reqCheckIn, setReqCheckIn] = useState("09:00");
  const [reqCheckOut, setReqCheckOut] = useState("18:00");
  const [regReason, setRegReason] = useState("");
  const [submittedMessage, setSubmittedMessage] = useState<string | null>(null);

  // Monthly calendar days with greytHR standard statuses:
  // P = Present, A = Absent, OD = On Duty, H = Holiday, L = Leave, R = Rest Day (Weekend)
  const calendarDays = [
    { day: 1, status: "R", hours: 0 },
    { day: 2, status: "P", hours: 8.5, in: "09:02", out: "17:32" },
    { day: 3, status: "P", hours: 8.2, in: "08:55", out: "17:10" },
    { day: 4, status: "P", hours: 8.4, in: "09:00", out: "17:25" },
    { day: 5, status: "P", hours: 8.0, in: "09:10", out: "17:12" },
    { day: 6, status: "P", hours: 8.7, in: "08:48", out: "17:30" },
    { day: 7, status: "R", hours: 0 },
    { day: 8, status: "R", hours: 0 },
    { day: 9, status: "P", hours: 8.5, in: "08:58", out: "17:28" },
    { day: 10, status: "P", hours: 8.1, in: "09:05", out: "17:10" },
    { day: 11, status: "H", hours: 0, label: "Veterans Day" },
    { day: 12, status: "P", hours: 8.6, in: "08:50", out: "17:25" },
    { day: 13, status: "P", hours: 8.3, in: "09:00", out: "17:18" },
    { day: 14, status: "R", hours: 0 },
    { day: 15, status: "R", hours: 0 },
    { day: 16, status: "P", hours: 8.2, in: "09:05", out: "17:18" },
    { day: 17, status: "P", hours: 8.5, in: "08:55", out: "17:25" },
    { day: 18, status: "L", hours: 0, label: "Casual Leave" },
    { day: 19, status: "OD", hours: 8.0, in: "09:00", out: "17:00", label: "Client Visit" },
    { day: 20, status: "PENDING", hours: 0, label: "Missing Punch Out" },
    { day: 21, status: "R", hours: 0 },
    { day: 22, status: "R", hours: 0 },
    { day: 23, status: "P", hours: 8.25, in: "09:00", out: "17:15" },
    { day: 24, status: "P", hours: 0, in: "09:05", out: "--" },
    { day: 25, status: "-", hours: 0 },
    { day: 26, status: "H", hours: 0, label: "Thanksgiving" },
    { day: 27, status: "H", hours: 0, label: "Day After Thanksgiving" },
    { day: 28, status: "R", hours: 0 },
    { day: 29, status: "R", hours: 0 },
    { day: 30, status: "-", hours: 0 },
  ];

  const handleRegularizeSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmittedMessage("Attendance Regularization Request submitted to your manager for approval.");
    setTimeout(() => {
      setIsRegularizeOpen(false);
      setSubmittedMessage(null);
    }, 2000);
  };

  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case "P":
        return "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";
      case "A":
        return "bg-rose-500/20 text-rose-400 border-rose-500/30";
      case "OD":
        return "bg-amber-500/20 text-amber-400 border-amber-500/30";
      case "H":
        return "bg-blue-500/20 text-blue-400 border-blue-500/30";
      case "L":
        return "bg-purple-500/20 text-purple-400 border-purple-500/30";
      case "R":
        return "bg-slate-800 text-slate-500 border-slate-700/50";
      case "PENDING":
        return "bg-amber-500/30 text-amber-300 border-amber-400 animate-pulse";
      default:
        return "bg-slate-900 text-slate-600 border-slate-800";
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header & Regularization Action */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Calendar className="w-5 h-5 text-brand-400" />
            <span>Monthly Attendance Calendar</span>
          </h1>
          <p className="text-xs text-slate-400">
            View your daily punches, shift attendance codes, and submit regularization requests.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1 bg-slate-900 border border-slate-800 rounded-lg p-1 text-xs">
            <Button variant="ghost" size="sm" className="h-7 px-2">
              <ChevronLeft className="w-3.5 h-3.5" />
            </Button>
            <span className="font-semibold text-slate-200 px-2">{selectedMonth}</span>
            <Button variant="ghost" size="sm" className="h-7 px-2">
              <ChevronRight className="w-3.5 h-3.5" />
            </Button>
          </div>

          <Button
            variant="primary"
            size="sm"
            onClick={() => setIsRegularizeOpen(true)}
            className="text-xs font-semibold"
          >
            Apply Regularization
          </Button>
        </div>
      </div>

      {/* Legend Bar */}
      <div className="flex flex-wrap items-center gap-4 p-3 rounded-xl border border-slate-800 bg-slate-900/60 text-xs">
        <span className="text-slate-400 font-semibold uppercase text-[10px]">Status Codes:</span>
        <div className="flex items-center gap-1.5">
          <span className="w-5 h-5 rounded flex items-center justify-center font-bold text-[10px] bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
            P
          </span>
          <span className="text-slate-300">Present</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-5 h-5 rounded flex items-center justify-center font-bold text-[10px] bg-rose-500/20 text-rose-400 border border-rose-500/30">
            A
          </span>
          <span className="text-slate-300">Absent</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-5 h-5 rounded flex items-center justify-center font-bold text-[10px] bg-amber-500/20 text-amber-400 border border-amber-500/30">
            OD
          </span>
          <span className="text-slate-300">On Duty</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-5 h-5 rounded flex items-center justify-center font-bold text-[10px] bg-purple-500/20 text-purple-400 border border-purple-500/30">
            L
          </span>
          <span className="text-slate-300">Leave</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-5 h-5 rounded flex items-center justify-center font-bold text-[10px] bg-blue-500/20 text-blue-400 border border-blue-500/30">
            H
          </span>
          <span className="text-slate-300">Holiday</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-5 h-5 rounded flex items-center justify-center font-bold text-[10px] bg-slate-800 text-slate-500 border border-slate-700/50">
            R
          </span>
          <span className="text-slate-300">Rest Day (Weekend)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-5 h-5 rounded flex items-center justify-center font-bold text-[10px] bg-amber-500/30 text-amber-300 border border-amber-400">
            ?
          </span>
          <span className="text-slate-300">Correction Needed</span>
        </div>
      </div>

      {/* Interactive Attendance Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-3">
        {calendarDays.map((item) => (
          <div
            key={item.day}
            onClick={() => setSelectedDay(item.day)}
            className={cn(
              "p-3 rounded-xl border transition-all cursor-pointer flex flex-col justify-between min-h-[95px]",
              selectedDay === item.day
                ? "border-brand-500 bg-brand-500/10 shadow-lg shadow-brand-950"
                : "border-slate-800 bg-slate-900/60 hover:border-slate-700 hover:bg-slate-850"
            )}
          >
            <div className="flex items-center justify-between">
              <span className="text-sm font-bold text-slate-200">{item.day}</span>
              <span
                className={cn(
                  "px-1.5 py-0.5 rounded text-[10px] font-bold border",
                  getStatusBadgeColor(item.status)
                )}
              >
                {item.status}
              </span>
            </div>

            <div className="mt-2 text-[11px] space-y-0.5">
              {item.in && item.out ? (
                <>
                  <div className="text-slate-400">In: {item.in}</div>
                  <div className="text-slate-400">Out: {item.out}</div>
                  <div className="font-semibold text-brand-400">{item.hours}h</div>
                </>
              ) : item.label ? (
                <div className="text-slate-400 italic text-[10px] truncate">{item.label}</div>
              ) : (
                <div className="text-slate-600">--</div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Selected Day Punch Detail Card */}
      {selectedDay && (
        <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-brand-600/20 border border-brand-500/30 flex items-center justify-center text-brand-400">
              <Clock className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-slate-100">
                Log for Nov {selectedDay}, 2026
              </h4>
              <p className="text-xs text-slate-400">
                Shift: General Day Shift (09:00 - 18:00) &bull; Grace Period: 15 mins
              </p>
            </div>
          </div>

          <div className="flex items-center gap-6 text-xs">
            <div>
              <span className="text-slate-400 block text-[10px]">PUNCH IN</span>
              <span className="font-semibold text-slate-100 text-sm">09:00 AM</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px]">PUNCH OUT</span>
              <span className="font-semibold text-slate-100 text-sm">05:15 PM</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px]">CALCULATED DURATION</span>
              <span className="font-bold text-emerald-400 text-sm">8h 15m</span>
            </div>
          </div>
        </div>
      )}

      {/* Attendance Regularization Modal */}
      <Modal
        isOpen={isRegularizeOpen}
        onClose={() => setIsRegularizeOpen(false)}
        title="Attendance Regularization Request"
      >
        <form onSubmit={handleRegularizeSubmit} className="space-y-4">
          <p className="text-xs text-slate-400">
            Submit a correction request for missing punch-in/out or duty outside of the office.
          </p>

          {submittedMessage ? (
            <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4" />
              <span>{submittedMessage}</span>
            </div>
          ) : (
            <>
              <Input
                label="Date to Regularize"
                type="date"
                value={regDate}
                onChange={(e) => setRegDate(e.target.value)}
                required
              />

              <div className="grid grid-cols-2 gap-3">
                <Input
                  label="Requested Check-In"
                  type="time"
                  value={reqCheckIn}
                  onChange={(e) => setReqCheckIn(e.target.value)}
                  required
                />
                <Input
                  label="Requested Check-Out"
                  type="time"
                  value={reqCheckOut}
                  onChange={(e) => setReqCheckOut(e.target.value)}
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Reason for Regularization
                </label>
                <textarea
                  value={regReason}
                  onChange={(e) => setRegReason(e.target.value)}
                  placeholder="e.g., Client meeting at external premises or card reader glitch"
                  required
                  rows={3}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-100 focus:outline-none focus:border-brand-500"
                />
              </div>

              <div className="pt-2 flex justify-end gap-2">
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => setIsRegularizeOpen(false)}
                  className="text-xs"
                >
                  Cancel
                </Button>
                <Button type="submit" variant="primary" className="text-xs">
                  Submit to Manager
                </Button>
              </div>
            </>
          )}
        </form>
      </Modal>
    </div>
  );
};
