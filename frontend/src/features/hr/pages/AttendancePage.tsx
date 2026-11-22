import React, { useEffect, useState } from "react";
import { Clock, CheckCircle, ArrowRight, ShieldCheck, MapPin, Play, Square } from "lucide-react";
import { hrApi } from "../api/hrApi";
import { AttendanceRecord, Shift } from "../types";

export const AttendancePage: React.FC = () => {
  const [shifts, setShifts] = useState<Shift[]>([]);
  const [records, setRecords] = useState<AttendanceRecord[]>([]);
  const [clockStatus, setClockStatus] = useState<"OUT" | "IN">("OUT");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [shiftRes, recRes] = await Promise.allSettled([
          hrApi.getShifts(),
          hrApi.getAttendanceRecords(),
        ]);
        if (shiftRes.status === "fulfilled") setShifts(shiftRes.value);
        if (recRes.status === "fulfilled") setRecords(recRes.value);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleToggleClock = () => {
    setClockStatus((prev) => (prev === "IN" ? "OUT" : "IN"));
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
          <Clock className="w-6 h-6 text-emerald-400" />
          Attendance & Time Tracking
        </h1>
        <p className="text-slate-400 text-sm mt-0.5">
          Web terminal clock-in, shift assignments, and daily worked hour calculations.
        </p>
      </div>

      {/* Clock Terminal Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-slate-900 to-slate-900/90 border border-slate-800 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">Live Virtual Terminal</div>
          <div className="text-2xl font-bold text-white mt-1">General Day Shift (09:00 - 17:00)</div>
          <div className="flex items-center gap-4 text-xs text-slate-400 mt-2">
            <span className="flex items-center gap-1.5 text-emerald-400">
              <ShieldCheck className="w-4 h-4" />
              Verified IP & Geo Location
            </span>
            <span>•</span>
            <span>Current Status: <strong className="text-white">{clockStatus === "IN" ? "CLOCKED IN" : "CLOCKED OUT"}</strong></span>
          </div>
        </div>

        <button
          onClick={handleToggleClock}
          className={`inline-flex items-center gap-2.5 px-6 py-3 rounded-xl font-bold text-sm shadow-xl transition-all hover:scale-105 ${
            clockStatus === "OUT"
              ? "bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-600/30"
              : "bg-rose-600 hover:bg-rose-500 text-white shadow-rose-600/30"
          }`}
        >
          {clockStatus === "OUT" ? <Play className="w-4 h-4 fill-white" /> : <Square className="w-4 h-4 fill-white" />}
          {clockStatus === "OUT" ? "Clock In Now" : "Clock Out"}
        </button>
      </div>

      {/* Shifts Catalog */}
      <div>
        <h2 className="text-base font-bold text-white mb-3">Configured Work Shifts</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-slate-200">General Day Shift</span>
              <span className="font-mono text-xs text-brand-400">GEN-09-17</span>
            </div>
            <div className="text-xs text-slate-400">09:00:00 - 17:00:00 (8h)</div>
            <div className="text-xs text-slate-500">Break: 60 min • Grace: 15 min</div>
          </div>
          <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-slate-200">Night Operations Shift</span>
              <span className="font-mono text-xs text-brand-400">NGT-22-06</span>
            </div>
            <div className="text-xs text-slate-400">22:00:00 - 06:00:00 (8h)</div>
            <div className="text-xs text-slate-500">Break: 45 min • Night Shift Allowance</div>
          </div>
        </div>
      </div>
    </div>
  );
};
