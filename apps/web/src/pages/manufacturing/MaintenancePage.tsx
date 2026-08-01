import React, { useEffect, useState } from 'react';
import { Wrench, Plus, AlertOctagon, CheckCircle2, Clock, X, Trash2 } from 'lucide-react';
import { manufacturingService, MaintenanceRequest, Machine } from '@/services/manufacturingService';

export function MaintenancePage() {
  const [requests, setRequests] = useState<MaintenanceRequest[]>([]);
  const [machines, setMachines] = useState<Machine[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Modals
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [showLogModal, setShowLogModal] = useState<boolean>(false);
  const [selectedReqId, setSelectedReqId] = useState<string | null>(null);

  // Form
  const [ticketNumber, setTicketNumber] = useState<string>('');
  const [machineId, setMachineId] = useState<string>('');
  const [title, setTitle] = useState<string>('');
  const [issueType, setIssueType] = useState<string>('CORRECTIVE');
  const [priority, setPriority] = useState<string>('MEDIUM');
  const [description, setDescription] = useState<string>('');
  const [technician, setTechnician] = useState<string>('Eng. Alex Rivera');

  // Work Log Form
  const [workDone, setWorkDone] = useState<string>('');
  const [partsReplaced, setPartsReplaced] = useState<string>('');
  const [logCost, setLogCost] = useState<number>(150.0);

  const fetchInitialData = async () => {
    setLoading(true);
    try {
      const [reqList, mList] = await Promise.all([
        manufacturingService.getMaintenanceRequests(),
        manufacturingService.getMachines(),
      ]);
      setRequests(reqList);
      setMachines(mList);
      if (mList.length > 0) setMachineId(mList[0].id);
    } catch (err) {
      console.error('Error fetching maintenance requests', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInitialData();
  }, []);

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await manufacturingService.createMaintenanceRequest({
        ticket_number: ticketNumber,
        machine_id: machineId,
        title,
        issue_type: issueType,
        priority,
        description,
        assigned_technician: technician,
      });
      setShowCreateModal(false);
      setTicketNumber('');
      setTitle('');
      fetchInitialData();
    } catch (err) {
      console.error('Error creating maintenance request', err);
    }
  };

  const handleLogSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedReqId) return;
    const req = requests.find((r) => r.id === selectedReqId);
    try {
      await manufacturingService.logMaintenanceWork({
        request_id: selectedReqId,
        machine_id: req ? req.machine_id : machineId,
        technician_name: technician,
        work_done: workDone,
        parts_replaced: partsReplaced,
        total_cost: logCost,
      });
      setShowLogModal(false);
      setWorkDone('');
      fetchInitialData();
    } catch (err) {
      console.error('Error logging maintenance work', err);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this maintenance ticket?')) return;
    try {
      await manufacturingService.deleteMaintenanceRequest(id);
      fetchInitialData();
    } catch (err) {
      console.error('Error deleting maintenance request', err);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Wrench className="h-6 w-6 text-primary" />
            Machine Preventive & Corrective Maintenance
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Service Tickets, Emergency Breakdown Dispatch, Spare Parts Logging & Maintenance History
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 text-xs font-semibold bg-primary text-primary-foreground rounded-lg shadow hover:bg-primary/90 transition-colors"
        >
          <Plus className="h-4 w-4" />
          File Maintenance Ticket
        </button>
      </div>

      <div className="bg-card border border-border rounded-xl p-4 shadow-sm space-y-4">
        <div className="border border-border rounded-lg overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-muted/50 border-b border-border font-medium text-muted-foreground uppercase tracking-wider text-[10px]">
              <tr>
                <th className="px-4 py-3">Ticket #</th>
                <th className="px-4 py-3">Title & Machine</th>
                <th className="px-4 py-3">Issue Type</th>
                <th className="px-4 py-3">Priority</th>
                <th className="px-4 py-3">Technician</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/60 text-foreground">
              {requests.map((req) => (
                <tr key={req.id} className="hover:bg-muted/30">
                  <td className="px-4 py-3 font-mono font-bold text-foreground">{req.ticket_number}</td>
                  <td className="px-4 py-3">
                    <div className="font-bold text-foreground">{req.title}</div>
                    <div className="text-[11px] text-muted-foreground font-mono">Machine: {req.machine_id.substring(0, 8)}...</div>
                  </td>
                  <td className="px-4 py-3">{req.issue_type}</td>
                  <td className="px-4 py-3 font-semibold">{req.priority}</td>
                  <td className="px-4 py-3">{req.assigned_technician || 'Unassigned'}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        req.status === 'RESOLVED' || req.status === 'CLOSED'
                          ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20'
                          : req.status === 'IN_PROGRESS'
                          ? 'bg-blue-500/10 text-blue-500 border border-blue-500/20'
                          : 'bg-amber-500/10 text-amber-500 border border-amber-500/20'
                      }`}
                    >
                      {req.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-1.5">
                      {req.status !== 'RESOLVED' && req.status !== 'CLOSED' && (
                        <button
                          onClick={() => {
                            setSelectedReqId(req.id);
                            setShowLogModal(true);
                          }}
                          className="px-2 py-1 text-[11px] font-semibold bg-emerald-600 text-white rounded hover:bg-emerald-700"
                        >
                          Resolve & Log
                        </button>
                      )}
                      <button onClick={() => handleDelete(req.id)} className="p-1 text-red-400 hover:bg-red-400/10 rounded">
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}

              {requests.length === 0 && !loading && (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-muted-foreground">
                    No Maintenance Requests found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* CREATE MAINTENANCE TICKET MODAL */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-card border border-border rounded-xl max-w-md w-full p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <h3 className="text-lg font-bold text-foreground">File Maintenance Ticket</h3>
              <button onClick={() => setShowCreateModal(false)} className="text-muted-foreground hover:text-foreground">
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleCreateSubmit} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-medium text-foreground mb-1">Ticket #</label>
                  <input
                    type="text"
                    required
                    placeholder="MNT-2026-101"
                    value={ticketNumber}
                    onChange={(e) => setTicketNumber(e.target.value)}
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                  />
                </div>
                <div>
                  <label className="block font-medium text-foreground mb-1">Target Machine</label>
                  <select
                    value={machineId}
                    onChange={(e) => setMachineId(e.target.value)}
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                  >
                    {machines.map((m) => (
                      <option key={m.id} value={m.id}>
                        {m.name} ({m.code})
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block font-medium text-foreground mb-1">Issue Title</label>
                <input
                  type="text"
                  required
                  placeholder="Hydraulic pump pressure loss"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-medium text-foreground mb-1">Issue Type</label>
                  <select
                    value={issueType}
                    onChange={(e) => setIssueType(e.target.value)}
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                  >
                    <option value="CORRECTIVE">CORRECTIVE</option>
                    <option value="PREVENTIVE">PREVENTIVE</option>
                    <option value="BREAKDOWN">EMERGENCY BREAKDOWN</option>
                  </select>
                </div>
                <div>
                  <label className="block font-medium text-foreground mb-1">Priority</label>
                  <select
                    value={priority}
                    onChange={(e) => setPriority(e.target.value)}
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                  >
                    <option value="LOW">LOW</option>
                    <option value="MEDIUM">MEDIUM</option>
                    <option value="HIGH">HIGH</option>
                    <option value="URGENT">URGENT</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block font-medium text-foreground mb-1">Assigned Technician</label>
                <input
                  type="text"
                  value={technician}
                  onChange={(e) => setTechnician(e.target.value)}
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-border">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 border border-border rounded-lg hover:bg-muted"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary text-primary-foreground rounded-lg font-semibold shadow hover:bg-primary/90"
                >
                  Submit Ticket
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* RESOLVE & LOG REPAIR WORK MODAL */}
      {showLogModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-card border border-border rounded-xl max-w-md w-full p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                Resolve Maintenance & Log Work
              </h3>
              <button onClick={() => setShowLogModal(false)} className="text-muted-foreground hover:text-foreground">
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleLogSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block font-medium text-foreground mb-1">Work Done Description</label>
                <textarea
                  rows={3}
                  required
                  value={workDone}
                  onChange={(e) => setWorkDone(e.target.value)}
                  placeholder="Replaced hydraulic seal valve and calibrated pressure..."
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-medium text-foreground mb-1">Parts Replaced</label>
                  <input
                    type="text"
                    placeholder="Valves, O-Rings"
                    value={partsReplaced}
                    onChange={(e) => setPartsReplaced(e.target.value)}
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                  />
                </div>
                <div>
                  <label className="block font-medium text-foreground mb-1">Total Cost ($)</label>
                  <input
                    type="number"
                    value={logCost}
                    onChange={(e) => setLogCost(Number(e.target.value))}
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-border">
                <button
                  type="button"
                  onClick={() => setShowLogModal(false)}
                  className="px-4 py-2 border border-border rounded-lg hover:bg-muted"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-emerald-600 text-white rounded-lg font-semibold shadow hover:bg-emerald-700"
                >
                  Resolve & Close
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
