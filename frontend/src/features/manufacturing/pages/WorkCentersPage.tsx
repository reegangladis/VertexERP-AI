import React, { useEffect, useState } from "react";
import { Factory, Plus, Cpu, Clock, DollarSign, Search, CheckCircle2, AlertTriangle, X, Wrench } from "lucide-react";
import { manufacturingApi } from "../api/manufacturingApi";
import { WorkCenter, Machine } from "../types";

export const WorkCentersPage: React.FC = () => {
  const [workCenters, setWorkCenters] = useState<WorkCenter[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filterType, setFilterType] = useState<string>("ALL");

  // Create Work Center Modal
  const [isWcModalOpen, setIsWcModalOpen] = useState(false);
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [wcType, setWcType] = useState("MACHINING");
  const [capacity, setCapacity] = useState("8.00");
  const [costPerHour, setCostPerHour] = useState("50.0000");
  const [overheadCost, setOverheadCost] = useState("20.0000");

  // Create Machine Modal
  const [isMachineModalOpen, setIsMachineModalOpen] = useState(false);
  const [selectedWcId, setSelectedWcId] = useState("");
  const [mCode, setMCode] = useState("");
  const [mName, setMName] = useState("");
  const [mSerial, setMSerial] = useState("");
  const [mHourlyCost, setMHourlyCost] = useState("30.0000");

  useEffect(() => {
    loadWorkCenters();
  }, []);

  async function loadWorkCenters() {
    setLoading(true);
    try {
      const res = await manufacturingApi.getWorkCenters({ page: 1, page_size: 50 });
      setWorkCenters(res.items || []);
    } catch (err) {
      console.error("Failed to load work centers", err);
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateWorkCenter(e: React.FormEvent) {
    e.preventDefault();
    try {
      await manufacturingApi.createWorkCenter({
        code,
        name,
        work_center_type: wcType as any,
        capacity_per_day_hours: capacity,
        cost_per_hour: costPerHour,
        overhead_cost_per_hour: overheadCost,
        status: "ACTIVE",
        is_active: true,
      });
      setIsWcModalOpen(false);
      setCode("");
      setName("");
      loadWorkCenters();
    } catch (err) {
      console.error("Failed to create work center", err);
      alert("Failed to create work center.");
    }
  }

  async function handleCreateMachine(e: React.FormEvent) {
    e.preventDefault();
    try {
      await manufacturingApi.createMachine({
        work_center_id: selectedWcId,
        code: mCode,
        name: mName,
        serial_number: mSerial,
        hourly_cost: mHourlyCost,
        status: "OPERATIONAL",
      });
      setIsMachineModalOpen(false);
      setMCode("");
      setMName("");
      setMSerial("");
      loadWorkCenters();
    } catch (err) {
      console.error("Failed to add machine", err);
      alert("Failed to add machine.");
    }
  }

  const filtered = workCenters.filter((wc) => {
    const matchesSearch =
      wc.code.toLowerCase().includes(search.toLowerCase()) ||
      wc.name.toLowerCase().includes(search.toLowerCase());
    const matchesType = filterType === "ALL" || wc.work_center_type === filterType;
    return matchesSearch && matchesType;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2.5">
            <Factory className="w-7 h-7 text-amber-400" /> Work Centers & Machinery
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Plant floor work stations, capacity hours, labor/overhead rates, and attached machine assets.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsWcModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-amber-600 hover:bg-amber-500 font-medium text-sm text-white transition-all shadow-lg shadow-amber-600/30"
          >
            <Plus className="w-4 h-4" /> Add Work Center
          </button>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/60 border border-slate-800 rounded-2xl p-4">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search work centers..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-800/80 border border-slate-700 rounded-xl pl-9 pr-4 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500"
          />
        </div>

        <div className="flex flex-wrap gap-1.5">
          {["ALL", "MACHINING", "ASSEMBLY", "PACKAGING", "TESTING", "FABRICATION"].map((type) => (
            <button
              key={type}
              onClick={() => setFilterType(type)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                filterType === type
                  ? "bg-amber-500/20 text-amber-400 border border-amber-500/40"
                  : "bg-slate-800/50 text-slate-400 hover:text-slate-200 border border-slate-800"
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      {/* Work Centers Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filtered.length === 0 ? (
          <div className="col-span-full py-16 text-center text-slate-500 bg-slate-900/40 rounded-2xl border border-slate-800">
            No work centers found.
          </div>
        ) : (
          filtered.map((wc) => (
            <div key={wc.id} className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-5 hover:border-slate-700 transition-all">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-slate-100 text-base">{wc.code}</span>
                    <span className="text-[10px] bg-amber-500/10 text-amber-400 border border-amber-500/20 font-bold px-2 py-0.5 rounded">
                      {wc.work_center_type}
                    </span>
                  </div>
                  <h3 className="text-sm font-semibold text-slate-300 mt-1">{wc.name}</h3>
                </div>

                <span
                  className={`text-xs font-semibold px-2.5 py-1 rounded-full ${
                    wc.status === "ACTIVE"
                      ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                      : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                  }`}
                >
                  {wc.status}
                </span>
              </div>

              {/* Rates / Capacity Specs */}
              <div className="grid grid-cols-3 gap-3 text-xs bg-slate-800/40 p-3.5 rounded-xl border border-slate-800">
                <div>
                  <span className="text-slate-500 block">Daily Capacity</span>
                  <span className="font-bold text-slate-200 mt-0.5 block">{Number(wc.capacity_per_day_hours).toFixed(1)} hrs</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Labor Rate</span>
                  <span className="font-bold text-slate-200 mt-0.5 block">${Number(wc.cost_per_hour).toFixed(2)}/hr</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Overhead Rate</span>
                  <span className="font-bold text-slate-200 mt-0.5 block">${Number(wc.overhead_cost_per_hour).toFixed(2)}/hr</span>
                </div>
              </div>

              {/* Machines Section */}
              <div className="pt-2 border-t border-slate-800">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                    <Cpu className="w-3.5 h-3.5 text-amber-400" /> Attached Equipment ({wc.machines?.length || 0})
                  </span>
                  <button
                    onClick={() => {
                      setSelectedWcId(wc.id);
                      setIsMachineModalOpen(true);
                    }}
                    className="text-xs text-amber-400 hover:text-amber-300 font-medium flex items-center gap-1"
                  >
                    <Plus className="w-3 h-3" /> Add Machine
                  </button>
                </div>

                <div className="space-y-2">
                  {!wc.machines || wc.machines.length === 0 ? (
                    <p className="text-xs text-slate-500 py-2 italic">No dedicated machinery assigned to this center.</p>
                  ) : (
                    wc.machines.map((m) => (
                      <div
                        key={m.id}
                        className="flex items-center justify-between p-2.5 rounded-lg bg-slate-800/60 border border-slate-800 text-xs"
                      >
                        <div>
                          <span className="font-semibold text-slate-200">{m.name}</span>
                          <span className="text-slate-500 text-[11px] ml-2 font-mono">({m.code})</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-slate-400 font-medium">${Number(m.hourly_cost).toFixed(2)}/hr</span>
                          <span
                            className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                              m.status === "OPERATIONAL"
                                ? "bg-emerald-500/10 text-emerald-400"
                                : "bg-rose-500/10 text-rose-400"
                            }`}
                          >
                            {m.status}
                          </span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Add Work Center Modal */}
      {isWcModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-lg font-bold text-slate-100">Add Work Center</h2>
              <button onClick={() => setIsWcModalOpen(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateWorkCenter} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Code *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. WC-PACK-01"
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-amber-500"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Final Packaging & Shipping Bay"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-amber-500"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Type</label>
                  <select
                    value={wcType}
                    onChange={(e) => setWcType(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-amber-500"
                  >
                    <option value="MACHINING">MACHINING</option>
                    <option value="ASSEMBLY">ASSEMBLY</option>
                    <option value="PACKAGING">PACKAGING</option>
                    <option value="TESTING">TESTING</option>
                    <option value="FABRICATION">FABRICATION</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Capacity (hrs/day)</label>
                  <input
                    type="number"
                    step="0.5"
                    value={capacity}
                    onChange={(e) => setCapacity(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Labor Cost ($/hr)</label>
                  <input
                    type="number"
                    step="1"
                    value={costPerHour}
                    onChange={(e) => setCostPerHour(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Overhead ($/hr)</label>
                  <input
                    type="number"
                    step="1"
                    value={overheadCost}
                    onChange={(e) => setOverheadCost(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsWcModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 text-sm text-slate-300 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-sm text-white font-semibold shadow-lg shadow-amber-600/30"
                >
                  Save Work Center
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Machine Modal */}
      {isMachineModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-lg font-bold text-slate-100">Add Equipment / Machine</h2>
              <button onClick={() => setIsMachineModalOpen(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateMachine} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Machine Code *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. MCH-CNC-04"
                  value={mCode}
                  onChange={(e) => setMCode(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-amber-500"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Machine Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Haas 5-Axis Milling Machine"
                  value={mName}
                  onChange={(e) => setMName(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-amber-500"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Serial Number</label>
                  <input
                    type="text"
                    placeholder="Serial #"
                    value={mSerial}
                    onChange={(e) => setMSerial(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Hourly Cost ($/hr)</label>
                  <input
                    type="number"
                    step="1"
                    value={mHourlyCost}
                    onChange={(e) => setMHourlyCost(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsMachineModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 text-sm text-slate-300 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-sm text-white font-semibold shadow-lg shadow-amber-600/30"
                >
                  Save Equipment
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
