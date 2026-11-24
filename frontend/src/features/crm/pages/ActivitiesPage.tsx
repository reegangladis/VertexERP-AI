import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { crmApi } from "../api/crmApi";
import { ActivityLogItem } from "../types";
import { DataTable } from "@/components/ui/DataTable";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { StatCard } from "@/components/ui/StatCard";
import { formatDateTime } from "@/lib/utils";
import { PhoneCall, Calendar, Mail, CheckSquare, Plus, Search } from "lucide-react";

export const ActivitiesPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState("");
  const [typeFilter, setTypeFilter] = useState<string>("ALL");
  const [showAddModal, setShowAddModal] = useState(false);
  const [formData, setFormData] = useState<Partial<ActivityLogItem>>({
    activity_type: "CALL",
    title: "",
    description: "",
    status: "PENDING",
    priority: "MEDIUM",
    scheduled_start: new Date().toISOString().slice(0, 16),
  });

  const { data: activities = [], isLoading } = useQuery<ActivityLogItem[]>({
    queryKey: ["crm-activities"],
    queryFn: crmApi.getActivities,
  });

  const createMutation = useMutation({
    mutationFn: crmApi.createActivity,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["crm-activities"] });
      setShowAddModal(false);
      setFormData({
        activity_type: "CALL",
        title: "",
        description: "",
        status: "PENDING",
        priority: "MEDIUM",
        scheduled_start: new Date().toISOString().slice(0, 16),
      });
    },
  });

  const filteredActivities = activities.filter((act) => {
    const matchesSearch =
      act.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (act.description && act.description.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesType = typeFilter === "ALL" || act.activity_type === typeFilter;
    return matchesSearch && matchesType;
  });

  const pendingCount = activities.filter((a) => a.status === "PENDING").length;
  const completedCount = activities.filter((a) => a.status === "COMPLETED").length;

  const getActivityIcon = (type: string) => {
    switch (type) {
      case "CALL":
        return <PhoneCall className="w-4 h-4 text-blue-600" />;
      case "MEETING":
        return <Calendar className="w-4 h-4 text-purple-600" />;
      case "EMAIL":
        return <Mail className="w-4 h-4 text-indigo-600" />;
      default:
        return <CheckSquare className="w-4 h-4 text-emerald-600" />;
    }
  };

  const columns = [
    {
      header: "Activity Type",
      accessorKey: "activity_type",
      cell: (row: ActivityLogItem) => (
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-slate-100 flex items-center justify-center">
            {getActivityIcon(row.activity_type)}
          </div>
          <span className="font-semibold text-slate-800 text-xs">{row.activity_type}</span>
        </div>
      ),
    },
    {
      header: "Title & Details",
      accessorKey: "title",
      cell: (row: ActivityLogItem) => (
        <div>
          <div className="font-semibold text-slate-900">{row.title}</div>
          {row.description && <div className="text-xs text-slate-500 line-clamp-1">{row.description}</div>}
        </div>
      ),
    },
    {
      header: "Priority",
      accessorKey: "priority",
      cell: (row: ActivityLogItem) => (
        <span
          className={`text-[11px] font-bold px-2 py-0.5 rounded-full ${
            row.priority === "HIGH"
              ? "bg-rose-50 text-rose-700 border border-rose-200"
              : row.priority === "MEDIUM"
              ? "bg-amber-50 text-amber-700 border border-amber-200"
              : "bg-slate-100 text-slate-600"
          }`}
        >
          {row.priority}
        </span>
      ),
    },
    {
      header: "Scheduled For",
      accessorKey: "scheduled_start",
      cell: (row: ActivityLogItem) => (
        <span className="text-xs text-slate-600 font-medium">
          {row.scheduled_start ? formatDateTime(row.scheduled_start) : "Not scheduled"}
        </span>
      ),
    },
    {
      header: "Status",
      accessorKey: "status",
      cell: (row: ActivityLogItem) => (
        <StatusBadge status={row.status || "PENDING"} />
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Sales Activities & Follow-ups</h1>
          <p className="text-sm text-slate-500">
            Log calls, meetings, client emails, and scheduled business interactions.
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 text-white font-medium hover:bg-indigo-700 transition shadow-sm"
        >
          <Plus className="w-4 h-4" />
          <span>Log Activity</span>
        </button>
      </div>

      {/* KPI Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <StatCard
          title="Total Activities Logged"
          value={activities.length}
          subtitle="All engagements across leads and accounts"
          icon={<CheckSquare className="w-5 h-5 text-indigo-600" />}
        />
        <StatCard
          title="Pending Follow-ups"
          value={pendingCount}
          subtitle="Scheduled tasks requiring attention"
          icon={<Calendar className="w-5 h-5 text-amber-600" />}
        />
        <StatCard
          title="Completed Engagements"
          value={completedCount}
          subtitle="Concluded sales interactions"
          icon={<CheckSquare className="w-5 h-5 text-emerald-600" />}
        />
      </div>

      {/* Activities Table Card */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="relative flex-1 max-w-sm">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by title or description..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600"
            />
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500 font-medium">Filter Type:</span>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="px-3 py-1.5 border rounded-xl border-slate-200 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
            >
              <option value="ALL">All Activities</option>
              <option value="CALL">Calls</option>
              <option value="MEETING">Meetings</option>
              <option value="EMAIL">Emails</option>
              <option value="EVENT">Events</option>
            </select>
          </div>
        </div>

        <DataTable
          columns={columns}
          data={filteredActivities}
          isLoading={isLoading}
          emptyMessage="No sales activities recorded."
        />
      </div>

      {/* Log Activity Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-xl max-w-lg w-full p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="font-bold text-slate-900 text-lg">Log Sales Activity</h3>
              <button
                onClick={() => setShowAddModal(false)}
                className="text-slate-400 hover:text-slate-600 text-lg font-bold"
              >
                &times;
              </button>
            </div>

            <div className="space-y-3.5 text-sm">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Activity Type</label>
                  <select
                    value={formData.activity_type}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        activity_type: e.target.value as "CALL" | "MEETING" | "EMAIL" | "EVENT",
                      })
                    }
                    className="w-full px-3 py-2 border rounded-xl border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                  >
                    <option value="CALL">Phone Call</option>
                    <option value="MEETING">Customer Meeting</option>
                    <option value="EMAIL">Email Follow-up</option>
                    <option value="EVENT">Trade Event / Demo</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Priority</label>
                  <select
                    value={formData.priority}
                    onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                    className="w-full px-3 py-2 border rounded-xl border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                  >
                    <option value="LOW">Low</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HIGH">High</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Activity Title *</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="e.g. Discovery call with Chief Procurement Officer"
                  className="w-full px-3 py-2 border rounded-xl border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Notes / Description</label>
                <textarea
                  rows={3}
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Key discussion points, objections, next action items..."
                  className="w-full px-3 py-2 border rounded-xl border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Scheduled Date & Time</label>
                  <input
                    type="datetime-local"
                    value={formData.scheduled_start}
                    onChange={(e) => setFormData({ ...formData, scheduled_start: e.target.value })}
                    className="w-full px-3 py-2 border rounded-xl border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Status</label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                    className="w-full px-3 py-2 border rounded-xl border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                  >
                    <option value="PENDING">Pending / Scheduled</option>
                    <option value="COMPLETED">Completed</option>
                    <option value="CANCELLED">Cancelled</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-4 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setShowAddModal(false)}
                className="px-4 py-2 rounded-xl border border-slate-200 text-slate-700 hover:bg-slate-50 font-medium"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => createMutation.mutate(formData)}
                disabled={!formData.title || createMutation.isPending}
                className="px-4 py-2 rounded-xl bg-indigo-600 text-white font-medium hover:bg-indigo-700 disabled:opacity-50 transition"
              >
                {createMutation.isPending ? "Logging..." : "Log Activity"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
