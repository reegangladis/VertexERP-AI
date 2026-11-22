import React, { useEffect, useState } from "react";
import {
  Layers,
  Plus,
  Search,
  DollarSign,
  Tag,
  CheckCircle2,
  GitBranch,
  Calculator,
  ChevronRight,
  FileText,
  X,
  Trash2,
} from "lucide-react";
import { manufacturingApi } from "../api/manufacturingApi";
import { BillOfMaterial, BOMVersion, BOMComponent } from "../types";

export const BillsOfMaterialsPage: React.FC = () => {
  const [boms, setBoms] = useState<BillOfMaterial[]>([]);
  const [selectedBom, setSelectedBom] = useState<BillOfMaterial | null>(null);
  const [selectedVersion, setSelectedVersion] = useState<BOMVersion | null>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [costCalculation, setCostCalculation] = useState<string | null>(null);
  const [calculatingCost, setCalculatingCost] = useState(false);

  // Create BOM Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newCode, setNewCode] = useState("");
  const [newName, setNewName] = useState("");
  const [newProductId, setNewProductId] = useState("");
  const [newUomId, setNewUomId] = useState("");
  const [newQuantity, setNewQuantity] = useState("1.0000");
  const [newNotes, setNewNotes] = useState("");
  const [components, setComponents] = useState<Array<{ component_product_id: string; quantity: string; uom_id: string; scrap_percentage: string }>>([
    { component_product_id: "", quantity: "1.0000", uom_id: "", scrap_percentage: "0.00" },
  ]);

  useEffect(() => {
    loadBOMs();
  }, []);

  async function loadBOMs() {
    setLoading(true);
    try {
      const res = await manufacturingApi.getBOMs({ page: 1, page_size: 50 });
      const items = res.items || [];
      setBoms(items);
      if (items.length > 0 && !selectedBom) {
        setSelectedBom(items[0]);
        if (items[0].versions && items[0].versions.length > 0) {
          setSelectedVersion(items[0].versions[0]);
        }
      }
    } catch (err) {
      console.error("Failed to load BOMs", err);
    } finally {
      setLoading(false);
    }
  }

  async function handleSelectBom(bom: BillOfMaterial) {
    setSelectedBom(bom);
    setCostCalculation(null);
    if (bom.versions && bom.versions.length > 0) {
      setSelectedVersion(bom.versions[0]);
    } else {
      setSelectedVersion(null);
    }
  }

  async function handleCalculateCost(versionId: string) {
    setCalculatingCost(true);
    try {
      const res = await manufacturingApi.calculateBOMCost(versionId);
      setCostCalculation(res.theoretical_cost);
    } catch (err) {
      console.error("Failed to calculate BOM cost", err);
    } finally {
      setCalculatingCost(false);
    }
  }

  function handleAddComponentRow() {
    setComponents([
      ...components,
      { component_product_id: "", quantity: "1.0000", uom_id: "", scrap_percentage: "0.00" },
    ]);
  }

  function handleRemoveComponentRow(idx: number) {
    setComponents(components.filter((_, i) => i !== idx));
  }

  async function handleCreateBOM(e: React.FormEvent) {
    e.preventDefault();
    try {
      const payload = {
        code: newCode,
        name: newName,
        product_id: newProductId,
        uom_id: newUomId,
        quantity: newQuantity,
        notes: newNotes,
        components: components.filter((c) => c.component_product_id && c.uom_id),
      };
      await manufacturingApi.createBOM(payload);
      setIsModalOpen(false);
      // Reset form
      setNewCode("");
      setNewName("");
      setNewProductId("");
      setNewUomId("");
      loadBOMs();
    } catch (err) {
      console.error("Failed to create BOM", err);
      alert("Failed to create BOM. Please ensure valid Product and UOM UUIDs.");
    }
  }

  const filteredBOMs = boms.filter(
    (b) =>
      b.code.toLowerCase().includes(search.toLowerCase()) ||
      b.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2.5">
            <Layers className="w-7 h-7 text-indigo-400" /> Bills of Materials (BOM) Master
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Manage multi-level engineering BOMs, component lines, scrap tolerances, and dynamic cost estimation.
          </p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 font-medium text-sm text-white transition-all shadow-lg shadow-indigo-600/30 self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" /> Create Bill of Materials
        </button>
      </div>

      {/* Main 2-Column Explorer View */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: BOM List */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 space-y-4">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            <input
              type="text"
              placeholder="Search BOM by code or name..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-slate-800/80 border border-slate-700/80 rounded-xl pl-9 pr-4 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="space-y-2 max-h-[600px] overflow-y-auto pr-1">
            {filteredBOMs.length === 0 ? (
              <div className="p-8 text-center text-slate-500 text-xs">No BOM records found.</div>
            ) : (
              filteredBOMs.map((bom) => {
                const isSelected = selectedBom?.id === bom.id;
                return (
                  <div
                    key={bom.id}
                    onClick={() => handleSelectBom(bom)}
                    className={`p-4 rounded-xl cursor-pointer transition-all border ${
                      isSelected
                        ? "bg-indigo-950/40 border-indigo-500 text-slate-100 shadow-md"
                        : "bg-slate-800/40 border-slate-800 hover:bg-slate-800/70 text-slate-300"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-sm">{bom.code}</span>
                      <span
                        className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded ${
                          bom.status === "ACTIVE"
                            ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                            : "bg-slate-700 text-slate-400"
                        }`}
                      >
                        {bom.status}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-1 truncate">{bom.name}</p>
                    <div className="flex items-center justify-between text-[11px] text-slate-500 mt-3 pt-2 border-t border-slate-800">
                      <span>Base Qty: {Number(bom.quantity).toFixed(2)}</span>
                      <span>{bom.versions?.length || 0} Versions</span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Right: BOM Detail & Components Breakdown */}
        <div className="lg:col-span-2 bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
          {selectedBom ? (
            <div className="space-y-6">
              {/* Header Info */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-5 border-b border-slate-800 gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="text-xl font-bold text-slate-100">{selectedBom.code}</h2>
                    {selectedBom.is_default && (
                      <span className="text-[10px] bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-semibold px-2 py-0.5 rounded">
                        Default BOM
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-slate-400 mt-0.5">{selectedBom.name}</p>
                </div>

                {selectedVersion && (
                  <button
                    onClick={() => handleCalculateCost(selectedVersion.id)}
                    disabled={calculatingCost}
                    className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-semibold text-slate-200 transition-all shadow-sm"
                  >
                    <Calculator className="w-4 h-4 text-emerald-400" />
                    {calculatingCost ? "Calculating..." : "Compute Theoretical Cost"}
                  </button>
                )}
              </div>

              {/* Theoretical Cost Callout */}
              {costCalculation && (
                <div className="p-4 rounded-xl bg-emerald-950/30 border border-emerald-500/30 flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2 text-emerald-300">
                    <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                    <span>Theoretical Raw Material Unit Cost:</span>
                  </div>
                  <span className="text-xl font-bold text-emerald-400">${Number(costCalculation).toFixed(4)}</span>
                </div>
              )}

              {/* Version Selector Tabs */}
              {selectedBom.versions && selectedBom.versions.length > 0 && (
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <GitBranch className="w-4 h-4 text-indigo-400" />
                    <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                      BOM Revisions / Versions
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {selectedBom.versions.map((ver) => (
                      <button
                        key={ver.id}
                        onClick={() => {
                          setSelectedVersion(ver);
                          setCostCalculation(null);
                        }}
                        className={`px-3.5 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                          selectedVersion?.id === ver.id
                            ? "bg-indigo-600 border-indigo-500 text-white shadow"
                            : "bg-slate-800/80 border-slate-700 text-slate-400 hover:text-slate-200"
                        }`}
                      >
                        v{ver.version_number} ({ver.status})
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Components Table */}
              <div>
                <h3 className="text-sm font-semibold text-slate-200 mb-3 flex items-center gap-2">
                  <FileText className="w-4 h-4 text-slate-400" /> Component Bill of Materials Line Items
                </h3>
                <div className="overflow-x-auto rounded-xl border border-slate-800">
                  <table className="w-full text-left text-xs text-slate-300">
                    <thead className="bg-slate-800/80 text-slate-400 uppercase font-semibold">
                      <tr>
                        <th className="px-4 py-3">Pos</th>
                        <th className="px-4 py-3">Component Product ID</th>
                        <th className="px-4 py-3">Quantity</th>
                        <th className="px-4 py-3">Scrap %</th>
                        <th className="px-4 py-3">Op Seq</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                      {!selectedVersion || !selectedVersion.components || selectedVersion.components.length === 0 ? (
                        <tr>
                          <td colSpan={5} className="text-center py-6 text-slate-500">
                            No components defined for this BOM version.
                          </td>
                        </tr>
                      ) : (
                        selectedVersion.components.map((c, i) => (
                          <tr key={c.id || i} className="hover:bg-slate-800/30">
                            <td className="px-4 py-3 font-semibold text-slate-400">{c.position}</td>
                            <td className="px-4 py-3 font-mono text-slate-300">{c.component_product_id}</td>
                            <td className="px-4 py-3 font-bold text-slate-100">{Number(c.quantity).toFixed(4)}</td>
                            <td className="px-4 py-3 text-amber-400 font-medium">{Number(c.scrap_percentage).toFixed(2)}%</td>
                            <td className="px-4 py-3 text-slate-400">{c.operation_sequence ?? "—"}</td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-16 text-slate-500 text-sm">
              Select a Bill of Materials on the left to inspect components and version history.
            </div>
          )}
        </div>
      </div>

      {/* Create BOM Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6 shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <h2 className="text-lg font-bold text-slate-100">Create Bill of Materials</h2>
              <button
                onClick={() => setIsModalOpen(false)}
                className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateBOM} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">BOM Code *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. BOM-BAT-100"
                    value={newCode}
                    onChange={(e) => setNewCode(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">BOM Name *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. 100kWh Assembly BOM"
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Product UUID *</label>
                  <input
                    type="text"
                    required
                    placeholder="Product ID"
                    value={newProductId}
                    onChange={(e) => setNewProductId(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">UOM UUID *</label>
                  <input
                    type="text"
                    required
                    placeholder="UOM ID"
                    value={newUomId}
                    onChange={(e) => setNewUomId(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Base Quantity</label>
                  <input
                    type="number"
                    step="0.0001"
                    value={newQuantity}
                    onChange={(e) => setNewQuantity(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              {/* Component Rows */}
              <div className="pt-2 border-t border-slate-800">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold text-slate-300">Raw Material Components</span>
                  <button
                    type="button"
                    onClick={handleAddComponentRow}
                    className="text-xs text-indigo-400 hover:text-indigo-300 font-medium flex items-center gap-1"
                  >
                    <Plus className="w-3.5 h-3.5" /> Add Component
                  </button>
                </div>

                <div className="space-y-2">
                  {components.map((comp, idx) => (
                    <div key={idx} className="flex items-center gap-2">
                      <input
                        type="text"
                        placeholder="Component Product UUID"
                        value={comp.component_product_id}
                        onChange={(e) => {
                          const updated = [...components];
                          updated[idx].component_product_id = e.target.value;
                          setComponents(updated);
                        }}
                        className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-100 focus:outline-none focus:border-indigo-500"
                      />
                      <input
                        type="number"
                        placeholder="Qty"
                        value={comp.quantity}
                        onChange={(e) => {
                          const updated = [...components];
                          updated[idx].quantity = e.target.value;
                          setComponents(updated);
                        }}
                        className="w-20 bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-100"
                      />
                      <input
                        type="text"
                        placeholder="UOM ID"
                        value={comp.uom_id}
                        onChange={(e) => {
                          const updated = [...components];
                          updated[idx].uom_id = e.target.value;
                          setComponents(updated);
                        }}
                        className="w-28 bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-100"
                      />
                      <input
                        type="number"
                        placeholder="Scrap %"
                        value={comp.scrap_percentage}
                        onChange={(e) => {
                          const updated = [...components];
                          updated[idx].scrap_percentage = e.target.value;
                          setComponents(updated);
                        }}
                        className="w-20 bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-100"
                      />
                      {components.length > 1 && (
                        <button
                          type="button"
                          onClick={() => handleRemoveComponentRow(idx)}
                          className="p-1 text-slate-500 hover:text-rose-400"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
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
                  className="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-sm text-white font-semibold shadow-lg shadow-indigo-600/30"
                >
                  Save BOM
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
