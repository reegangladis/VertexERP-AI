import React, { useEffect, useState } from "react";
import {
  Warehouse as WarehouseIcon,
  Plus,
  MapPin,
  Layers,
  CheckCircle2,
  XCircle,
  AlertCircle,
  ShieldAlert,
  Sparkles,
} from "lucide-react";
import { inventoryApi } from "../api/inventoryApi";
import { Location, Warehouse } from "../types";

export const WarehousesPage: React.FC = () => {
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [selectedWh, setSelectedWh] = useState<Warehouse | null>(null);
  const [locations, setLocations] = useState<Location[]>([]);
  const [loading, setLoading] = useState(true);
  const [locationsLoading, setLocationsLoading] = useState(false);

  // Modal states
  const [isWhModalOpen, setIsWhModalOpen] = useState(false);
  const [isLocModalOpen, setIsLocModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [whFormData, setWhFormData] = useState<Partial<Warehouse>>({
    code: "",
    name: "",
    warehouse_type: "STANDARD",
    is_primary: false,
    is_active: true,
  });

  const [locFormData, setLocFormData] = useState<Partial<Location>>({
    code: "",
    name: "",
    aisle: "A1",
    rack: "R1",
    shelf: "S1",
    bin: "B1",
    location_type: "STORAGE",
    is_active: true,
  });

  const loadWarehouses = async () => {
    try {
      setLoading(true);
      const res = await inventoryApi.getWarehouses();
      const items = res.items || [];
      setWarehouses(items);
      if (items.length > 0 && !selectedWh) {
        setSelectedWh(items[0]);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadWarehouses();
  }, []);

  useEffect(() => {
    async function loadLocations() {
      if (!selectedWh) return;
      try {
        setLocationsLoading(true);
        const locs = await inventoryApi.getWarehouseLocations(selectedWh.id);
        const locList = Array.isArray(locs) ? locs : ((locs as any)?.items || []);
        setLocations(locList);
      } catch (e) {
        setLocations([]);
      } finally {
        setLocationsLoading(false);
      }
    }
    loadLocations();
  }, [selectedWh]);

  const handleCreateWarehouse = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      if (!whFormData.code || !whFormData.name) {
        setError("Warehouse Code and Name are required.");
        setSubmitting(false);
        return;
      }
      await inventoryApi.createWarehouse({
        ...whFormData,
        code: whFormData.code.toUpperCase(),
      });
      setIsWhModalOpen(false);
      setWhFormData({
        code: "",
        name: "",
        warehouse_type: "STANDARD",
        is_primary: false,
        is_active: true,
      });
      await loadWarehouses();
    } catch (err: any) {
      setError(err?.message || "Failed to create warehouse");
    } finally {
      setSubmitting(false);
    }
  };

  const handleCreateLocation = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedWh) return;
    setError(null);
    setSubmitting(true);
    try {
      if (!locFormData.code || !locFormData.name) {
        setError("Location Code and Name are required.");
        setSubmitting(false);
        return;
      }
      await inventoryApi.createWarehouseLocation(selectedWh.id, {
        ...locFormData,
        code: locFormData.code.toUpperCase(),
      });
      setIsLocModalOpen(false);
      setLocFormData({
        code: "",
        name: "",
        aisle: "A1",
        rack: "R1",
        shelf: "S1",
        bin: "B1",
        location_type: "STORAGE",
        is_active: true,
      });
      const locs = await inventoryApi.getWarehouseLocations(selectedWh.id);
      setLocations(locs || []);
    } catch (err: any) {
      setError(err?.message || "Failed to create bin location");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl font-bold tracking-tight text-slate-100">
              Warehouses & Location Bins
            </h1>
            <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              {warehouses.length} Facilities
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Manage multi-warehouse storage facilities, quarantine zones, and granular bin hierarchies.
          </p>
        </div>

        <button
          onClick={() => setIsWhModalOpen(true)}
          className="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm shadow-emerald-600/30 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Add Warehouse
        </button>
      </div>

      {/* Main Grid: Warehouses List & Bins Detail */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Warehouses List */}
        <div className="space-y-3">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Storage Facilities
          </h2>
          {loading ? (
            <div className="p-8 text-center text-xs text-slate-500">Loading facilities...</div>
          ) : warehouses.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-500 bg-slate-900/60 border border-slate-800 rounded-xl">
              No warehouses configured.
            </div>
          ) : (
            warehouses.map((wh) => (
              <div
                key={wh.id}
                onClick={() => setSelectedWh(wh)}
                className={`p-4 rounded-xl border transition-all cursor-pointer ${
                  selectedWh?.id === wh.id
                    ? "bg-slate-800/90 border-emerald-500 shadow-md shadow-emerald-950/40"
                    : "bg-slate-900/60 border-slate-800 hover:border-slate-700 hover:bg-slate-800/40"
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-bold text-xs text-emerald-400">
                        {wh.code}
                      </span>
                      {wh.is_primary && (
                        <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300">
                          PRIMARY
                        </span>
                      )}
                    </div>
                    <h3 className="text-sm font-semibold text-slate-100 mt-1">{wh.name}</h3>
                  </div>
                  <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300">
                    {wh.warehouse_type}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Selected Warehouse & Location Bins */}
        <div className="lg:col-span-2 rounded-xl bg-slate-900/60 border border-slate-800 p-5 space-y-4">
          {selectedWh ? (
            <>
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="text-base font-bold text-slate-100">{selectedWh.name}</h2>
                    <span className="font-mono text-xs text-emerald-400 font-bold px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">
                      {selectedWh.code}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-1">
                    Facility Type: {selectedWh.warehouse_type} • Hierarchy: Aisle / Rack / Shelf / Bin
                  </p>
                </div>

                <button
                  onClick={() => setIsLocModalOpen(true)}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
                >
                  <Plus className="w-3.5 h-3.5 text-emerald-400" />
                  Add Bin / Location
                </button>
              </div>

              {/* Bins Table */}
              <div>
                <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">
                  Configured Storage Bins ({Array.isArray(locations) ? locations.length : 0})
                </h3>

                {locationsLoading ? (
                  <div className="py-10 text-center text-xs text-slate-500">
                    Loading locations and bins...
                  </div>
                ) : !Array.isArray(locations) || locations.length === 0 ? (
                  <div className="py-12 text-center text-slate-500 bg-slate-800/20 rounded-xl border border-slate-800">
                    <MapPin className="w-6 h-6 mx-auto text-slate-600 mb-2" />
                    No bin locations configured for this facility. Add standard storage bins.
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs text-slate-300">
                      <thead className="bg-slate-800/80 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-700/60">
                        <tr>
                          <th className="py-2.5 px-3">Bin Code</th>
                          <th className="py-2.5 px-3">Name</th>
                          <th className="py-2.5 px-3">Aisle / Rack / Shelf / Bin</th>
                          <th className="py-2.5 px-3">Type</th>
                          <th className="py-2.5 px-3 text-center">Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800">
                        {Array.isArray(locations) && locations.map((loc) => (
                          <tr key={loc.id} className="hover:bg-slate-800/40">
                            <td className="py-2.5 px-3 font-mono font-bold text-emerald-400">
                              {loc.code}
                            </td>
                            <td className="py-2.5 px-3 font-medium text-slate-200">{loc.name}</td>
                            <td className="py-2.5 px-3 font-mono text-slate-400">
                              {loc.aisle || "-"} / {loc.rack || "-"} / {loc.shelf || "-"} / {loc.bin || "-"}
                            </td>
                            <td className="py-2.5 px-3">
                              <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300">
                                {loc.location_type}
                              </span>
                            </td>
                            <td className="py-2.5 px-3 text-center">
                              <span className="text-[10px] font-bold text-emerald-400">ACTIVE</span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="py-16 text-center text-xs text-slate-500">
              Select a warehouse to view details and bin configurations.
            </div>
          )}
        </div>
      </div>

      {/* Create Warehouse Modal */}
      {isWhModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <WarehouseIcon className="w-5 h-5 text-emerald-400" />
                Add Warehouse Facility
              </h2>
              <button onClick={() => setIsWhModalOpen(false)} className="text-slate-400 hover:text-slate-200">
                ✕
              </button>
            </div>

            {error && (
              <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs">
                {error}
              </div>
            )}

            <form onSubmit={handleCreateWarehouse} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Facility Code *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. WH-CENTRAL"
                  value={whFormData.code}
                  onChange={(e) => setWhFormData({ ...whFormData, code: e.target.value })}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 uppercase font-mono focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Warehouse Name *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Central Distribution Hub"
                  value={whFormData.name}
                  onChange={(e) => setWhFormData({ ...whFormData, name: e.target.value })}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Facility Type
                </label>
                <select
                  value={whFormData.warehouse_type}
                  onChange={(e) => setWhFormData({ ...whFormData, warehouse_type: e.target.value as any })}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
                >
                  <option value="STANDARD">Standard Warehouse</option>
                  <option value="TRANSIT">Transit Hub</option>
                  <option value="QUARANTINE">Quarantine Facility</option>
                  <option value="RETURN">Returns Center</option>
                </select>
              </div>

              <div className="flex items-center gap-6 pt-2">
                <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={whFormData.is_primary}
                    onChange={(e) => setWhFormData({ ...whFormData, is_primary: e.target.checked })}
                    className="rounded border-slate-700 bg-slate-800 text-emerald-600 focus:ring-0"
                  />
                  <span>Primary Warehouse</span>
                </label>
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsWhModalOpen(false)}
                  className="px-4 py-2 text-xs font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 text-xs font-semibold rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm shadow-emerald-600/30 disabled:opacity-50"
                >
                  {submitting ? "Creating..." : "Create Facility"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Create Location Modal */}
      {isLocModalOpen && selectedWh && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <MapPin className="w-5 h-5 text-emerald-400" />
                Add Location Bin for {selectedWh.code}
              </h2>
              <button onClick={() => setIsLocModalOpen(false)} className="text-slate-400 hover:text-slate-200">
                ✕
              </button>
            </div>

            {error && (
              <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs">
                {error}
              </div>
            )}

            <form onSubmit={handleCreateLocation} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Bin Code *
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. A1-R01-S01-B01"
                    value={locFormData.code}
                    onChange={(e) => setLocFormData({ ...locFormData, code: e.target.value })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 uppercase font-mono focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Bin Name *
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Aisle 1 Rack 1"
                    value={locFormData.name}
                    onChange={(e) => setLocFormData({ ...locFormData, name: e.target.value })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-4 gap-2">
                <div>
                  <label className="block text-[10px] font-medium text-slate-400 mb-1">Aisle</label>
                  <input
                    type="text"
                    value={locFormData.aisle || ""}
                    onChange={(e) => setLocFormData({ ...locFormData, aisle: e.target.value })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-2 py-1.5 text-xs text-slate-200"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-medium text-slate-400 mb-1">Rack</label>
                  <input
                    type="text"
                    value={locFormData.rack || ""}
                    onChange={(e) => setLocFormData({ ...locFormData, rack: e.target.value })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-2 py-1.5 text-xs text-slate-200"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-medium text-slate-400 mb-1">Shelf</label>
                  <input
                    type="text"
                    value={locFormData.shelf || ""}
                    onChange={(e) => setLocFormData({ ...locFormData, shelf: e.target.value })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-2 py-1.5 text-xs text-slate-200"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-medium text-slate-400 mb-1">Bin</label>
                  <input
                    type="text"
                    value={locFormData.bin || ""}
                    onChange={(e) => setLocFormData({ ...locFormData, bin: e.target.value })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-2 py-1.5 text-xs text-slate-200"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Location Type
                </label>
                <select
                  value={locFormData.location_type}
                  onChange={(e) => setLocFormData({ ...locFormData, location_type: e.target.value as any })}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
                >
                  <option value="STORAGE">Standard Storage</option>
                  <option value="RECEIVING">Receiving Dock</option>
                  <option value="SHIPPING">Shipping Stage</option>
                  <option value="PICKING">Picking Fast-Track</option>
                  <option value="QUARANTINE">Quarantine Hold</option>
                </select>
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsLocModalOpen(false)}
                  className="px-4 py-2 text-xs font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 text-xs font-semibold rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm shadow-emerald-600/30 disabled:opacity-50"
                >
                  {submitting ? "Adding..." : "Add Bin"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
