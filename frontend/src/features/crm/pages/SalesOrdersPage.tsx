import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { crmApi } from "../api/crmApi";
import { SalesOrderItemDto, CustomerAccountItem } from "../types";
import { DataTable } from "@/components/ui/DataTable";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { StatCard } from "@/components/ui/StatCard";
import { formatCurrency, formatDate } from "@/lib/utils";
import { ShoppingCart, CheckCircle, Search, Truck } from "lucide-react";

export const SalesOrdersPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState("");

  const { data: orders = [], isLoading } = useQuery<SalesOrderItemDto[]>({
    queryKey: ["crm-orders"],
    queryFn: crmApi.getSalesOrders,
  });

  const { data: accounts = [] } = useQuery<CustomerAccountItem[]>({
    queryKey: ["crm-accounts"],
    queryFn: crmApi.getCustomers,
  });

  const accountMap = new Map(accounts.map((a) => [a.id, a.name]));

  const filteredOrders = orders.filter((o) => {
    const oNum = (o.order_number || "").toLowerCase();
    const cName = (o.customer_id ? accountMap.get(o.customer_id) || "" : "").toLowerCase();
    return oNum.includes(searchTerm.toLowerCase()) || cName.includes(searchTerm.toLowerCase());
  });

  const totalRevenue = orders.reduce((sum, o) => sum + (o.grand_total || 0), 0);
  const confirmedCount = orders.filter((o) => o.status === "CONFIRMED").length;

  const columns = [
    {
      header: "Order Number",
      accessorKey: "order_number",
      cell: (row: SalesOrderItemDto) => (
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-emerald-50 flex items-center justify-center text-emerald-600 font-bold text-xs">
            <ShoppingCart className="w-4 h-4" />
          </div>
          <div>
            <div className="font-semibold text-slate-900">{row.order_number}</div>
            <div className="text-[11px] text-slate-500">
              {row.created_at ? formatDate(row.created_at) : "N/A"}
            </div>
          </div>
        </div>
      ),
    },
    {
      header: "Customer Account",
      accessorKey: "customer_id",
      cell: (row: SalesOrderItemDto) => (
        <span className="font-medium text-slate-800">
          {row.customer_id ? accountMap.get(row.customer_id) || "Direct Client" : "Unassigned"}
        </span>
      ),
    },
    {
      header: "Order Amount",
      accessorKey: "grand_total",
      cell: (row: SalesOrderItemDto) => (
        <span className="font-bold text-slate-900">{formatCurrency(row.grand_total)}</span>
      ),
    },
    {
      header: "Fulfillment Status",
      accessorKey: "status",
      cell: (row: SalesOrderItemDto) => (
        <StatusBadge status={row.status || "CONFIRMED"} />
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Sales Orders</h1>
          <p className="text-sm text-slate-500">
            Binding sales contracts, order confirmation tracking, and invoicing progression.
          </p>
        </div>
      </div>

      {/* KPI Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <StatCard
          title="Total Confirmed Orders"
          value={orders.length}
          subtitle="Processed through sales cycle"
          icon={<ShoppingCart className="w-5 h-5 text-indigo-600" />}
        />
        <StatCard
          title="Cumulative Order Value"
          value={formatCurrency(totalRevenue)}
          subtitle="Total booking value"
          icon={<CheckCircle className="w-5 h-5 text-emerald-600" />}
        />
        <StatCard
          title="Active in Fulfillment"
          value={confirmedCount}
          subtitle="Orders awaiting dispatch / delivery"
          icon={<Truck className="w-5 h-5 text-amber-600" />}
        />
      </div>

      {/* Orders Table Card */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="relative flex-1 max-w-sm">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by order number or account..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600"
            />
          </div>
        </div>

        <DataTable
          columns={columns}
          data={filteredOrders}
          isLoading={isLoading}
          emptyMessage="No sales orders confirmed yet."
        />
      </div>
    </div>
  );
};
