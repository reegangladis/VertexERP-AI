import React, { useEffect, useState } from "react";
import { GitMerge, Plus, Clock, Wrench, Search, ChevronRight, X, Layers, CheckCircle2 } from "lucide-react";
import { manufacturingApi } from "../api/manufacturingApi";
import { Routing, RoutingOperation } from "../types";

export const RoutingsPage: React.FC = () => {
  const [routings, setRoutings] = useState<Routing[]>([]);
  const [selectedRouting, setSelectedRouting] = useState<Routing | null>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newCode, setNewCode] = useState("");
  const [newName, setNewName] = useState("");
  const [newProductId, setNewProductId] = useState("");
  const [newDescription, setNewDescription] = useState("");
  const [operations, setOperations] = useState<Array<{ sequence: number; operation_name: string; work_center_id: string; setup_time_hours: string; run_time_per_unit_hours: string }>>([
    { sequence: 10, operation_name: "Cell Module Welding", work_center_id: "", setup_time_hours: "0.50", run_time_per_unit_hours: "0.10" },
  ]);

  useEffect(() => {
    loadRoutings();
  }, []);

  async function loadRoutings() {
    setLoading(true);
    try {
      const res = await manufacturingApi.getRoutings({ page: 1, page_size: 50 });
      const items = res.items || [];
      setRoutings(items);
      if (items.length > 0 && !selectedRouting) {
        setSelectedRouting(items[0]);
      }
    } catch (err) {
      console.error("Failed to load routings", err);
    } finally {
      setLoading(false);
    }
  }

  function handleAddOperationRow() {
    const nextSeq = (operations.length + 1) * 10;
    setOperations([
      ...operations,
      { sequence: nextSeq, operation_name: "", work_center_id: "", setup_time_hours: "0.25", run_time_per_unit_hours: "0.05" },
    ]);
  }

  async function handleCreateRouting(e: React.FormEvent) {
    e.preventDefault();
    try {
      const payload = {
        code: newCode,
        name: newName,
        product_id: newProductId,
        description: newDescription,
        operations: operations.filter((op) => op.operation_name && op.work_center_id),
      };
      await manufacturingApi.createRouting(payload);
      setIsModalOpen(false);
      setNewCode("");
      setNewName("");
      setNewProductId("");
      loadRoutings();
    } catch (err) {
      console.error("Failed to create routing", err);
      alert("Failed to create routing. Please ensure valid Product and Work Center UUIDs.");
    }
  }

  const filtered = routings.filter(
    (r) =>
      r.code.toLowerCase().includes(search.toLowerCase()) ||
      r.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2.5">
            <GitMerge className="w-7 h-7 text-cyan-400" /> Manufacturing Routings & Operations
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Define sequential production operations, setup durations, machine run times, and work center routings.
          </p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 font-medium text-sm text-white transition-all shadow-lg shadow-cyan-600/30 self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" /> Create Routing Master
        </button>
      </div>

      {/* 2-Column Explorer */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Routings List */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 space-y-4">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            <input
              type="text"
              placeholder="Search routing by code..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-slate-800/80 border border-slate-700/80 rounded-xl pl-9 pr-4 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div className="space-y-2 max-h-[600px] overflow-y-auto pr-1">
            {filtered.length === 0 ? (
              <div className="p-8 text-center text-slate-500 text-xs">No routings found.</div>
            ) : (
              filtered.map((routing) => {
                const isSelected = selectedRouting?.id === routing.id;
                return (
                  <div
                    key={routing.id}
                    onClick={() => setSelectedRouting(routing)}
                    className={`p-4 rounded-xl cursor-pointer transition-all border ${
                      isSelected
                        ? "bg-cyan-950/40 border-cyan-500 text-slate-100 shadow-md"
                        : "bg-slate-800/40 border-slate-800 hover:bg-slate-800/70 text-slate-300"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-sm">{routing.code}</span>
                      <span className="text-[10px] bg-emerald-500/10 text-emerald-400 font-bold px-2 py-0.5 rounded">
                        {routing.is_active ? "ACTIVE" : "INACTIVE"}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-1 truncate">{routing.name}</p>
                    <div className="flex items-center justify-between text-[11px] text-slate-500 mt-3 pt-2 border-t border-slate-800">
                      <span>{routing.operations?.length || 0} Sequential Steps</span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Right: Operations Detail */}
        <div className="lg:col-span-2 bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
          {selectedRouting ? (
            <div className="space-y-6">
              <div className="pb-4 border-b border-slate-800">
                <h2 className="text-xl font-bold text-slate-100">{selectedRouting.code}</h2>
                <p className="text-sm text-slate-400 mt-0.5">{selectedRouting.name}</p>
                {selectedRouting.description && (
                  <p className="text-xs text-slate-500 mt-2">{selectedRouting.description}</p>
                )}
              </div>

              {/* Sequential Steps Timeline */}
              <div>
                <h3 className="text-sm font-semibold text-slate-200 mb-4 flex items-center gap-2">
                  <Clock className="w-4 h-4 text-cyan-400" /> Sequential Operation Steps
                </h3>

                <div className="space-y-3">
                  {!selectedRouting.operations || selectedRouting.operations.length === 0 ? (
                    <div className="p-6 text-center text-slate-500 text-xs rounded-xl border border-slate-800">
                      No operation sequence steps defined for this routing.
                    </div>
                  ) : (
                    selectedRouting.operations.map((op, idx) => (
                      <div
                        key={op.id || idx}
                        className="bg-slate-800/50 border border-slate-800 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                      >
                        <div className="flex items-start gap-3">
                          <div className="w-8 h-8 rounded-lg bg-cyan-500/10 text-cyan-400 flex items-center justify-center font-bold text-xs border border-cyan-500/20">
                            {op.sequence}
                          </div>
                          <div>
                            <h4 className="text-sm font-semibold text-slate-100">{op.operation_name}</h4>
                            <p className="text-xs text-slate-400 mt-0.5 font-mono">
                              Work Center: {op.work_center_id}
                            </p>
                          </div>
                        </div>

                        <div className="flex items-center gap-4 text-xs">
                          <div className="bg-slate-900/60 px-3 py-1.5 rounded-lg border border-slate-800">
                            <span className="text-slate-500">Setup: </span>
                            <span className="font-semibold text-slate-200">{Number(op.setup_time_hours).toFixed(2)}h</span>
                          </div>
                          <div className="bg-slate-900/60 px-3 py-1.5 rounded-lg border border-slate-800">
                            <span className="text-slate-500">Run/Unit: </span>
                            <span className="font-semibold text-slate-200">{Number(op.run_time_per_unit_hours).toFixed(2)}h</span>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-16 text-slate-500 text-sm">
              Select a routing on the left to inspect operation sequences.
            </div>
          )}
        </div>
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6 shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <h2 className="text-lg font-bold text-slate-100">Create Manufacturing Routing</h2>
              <button
                onClick={() => setIsModalOpen(false)}
                className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateRouting} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Routing Code *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. RT-BAT-001"
                    value={newCode}
                    onChange={(e) => setNewCode(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-cyan-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Routing Name *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Battery Module Assembly Line"
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Product UUID *</label>
                <input
                  type="text"
                  required
                  placeholder="Product ID for this routing"
                  value={newProductId}
                  onChange={(e) => setNewProductId(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-cyan-500"
                />
              </div>

              {/* Operations */}
              <div className="pt-2 border-t border-slate-800">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold text-slate-300">Operation Sequence Steps</span>
                  <button
                    type="button"
                    onClick={handleAddOperationRow}
                    className="text-xs text-cyan-400 hover:text-cyan-300 font-medium flex items-center gap-1"
                  >
                    <Plus className="w-3.5 h-3.5" /> Add Step
                  </button>
                </div>

                <div className="space-y-2">
                  {operations.map((op, idx) => (
                    <div key={idx} className="flex items-center gap-2">
                      <input
                        type="number"
                        placeholder="Seq"
                        value={op.sequence}
                        onChange={(e) => {
                          const updated = [...operations];
                          updated[idx].sequence = Number(e.target.value);
                          setOperations(updated);
                        }}
                        className="w-16 bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-100"
                      />
                      <input
                        type="text"
                        placeholder="Operation Name"
                        value={op.operation_name}
                        onChange={(e) => {
                          const updated = [...operations];
                          updated[idx].operation_name = e.target.value;
                          setOperations(updated);
                        }}
                        className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
                      />
                      <input
                        type="text"
                        placeholder="Work Center UUID"
                        value={op.work_center_id}
                        onChange={(e) => {
                          const updated = [...operations];
                          updated[idx].work_center_id = e.target.value;
                          setOperations(updated);
                        }}
                        className="w-36 bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-100"
                      />
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-sm text-slate-300 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-sm text-white font-semibold shadow-lg shadow-cyan-600/30"
                >
                  Save Routing
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
