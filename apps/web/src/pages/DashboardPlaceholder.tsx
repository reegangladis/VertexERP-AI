import { useState } from 'react';
import { motion } from 'framer-motion';
import { AgGridReact } from 'ag-grid-react';
import type { ColDef } from 'ag-grid-community';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { Server, Cpu, Database, TrendingUp, LayoutDashboard, CheckCircle2 } from 'lucide-react';

// AG Grid style imports
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';

// Types for AG Grid data
interface SystemService {
  name: string;
  type: string;
  endpoint: string;
  port: number;
  status: string;
  version: string;
}

export function DashboardPlaceholder() {
  // Mock performance data for chart
  const chartData = [
    { time: '09:00', cpu: 12, memory: 42, requests: 24 },
    { time: '10:00', cpu: 18, memory: 45, requests: 38 },
    { time: '11:00', cpu: 15, memory: 44, requests: 30 },
    { time: '12:00', cpu: 28, memory: 49, requests: 85 },
    { time: '13:00', cpu: 32, memory: 52, requests: 92 },
    { time: '14:00', cpu: 22, memory: 50, requests: 55 },
    { time: '15:00', cpu: 24, memory: 51, requests: 62 },
  ];

  // Grid column definitions typed explicitly with ColDef
  const [columnDefs] = useState<ColDef<SystemService>[]>([
    { field: 'name', headerName: 'Service Name', sortable: true, filter: true, flex: 1 },
    { field: 'type', headerName: 'Layer', sortable: true, filter: true, flex: 1 },
    { field: 'endpoint', headerName: 'Access Endpoint', flex: 1.5 },
    { field: 'port', headerName: 'Container Port', width: 140, sortable: true },
    { field: 'version', headerName: 'Release Version', width: 140 },
    {
      field: 'status',
      headerName: 'Status',
      width: 130,
      cellRenderer: (params: { value: string }) => {
        const isHealthy = params.value === 'Healthy';
        return (
          <div className="flex items-center space-x-1.5 h-full">
            <span
              className={`h-2 w-2 rounded-full ${isHealthy ? 'bg-emerald-500' : 'bg-red-500'}`}
            />
            <span className="text-xs font-mono">{params.value}</span>
          </div>
        );
      },
    },
  ]);

  // Grid rows
  const [rowData] = useState<SystemService[]>([
    {
      name: 'vertexerp_frontend',
      type: 'Frontend Web',
      endpoint: 'http://localhost:3000',
      port: 80,
      status: 'Healthy',
      version: '1.1.0',
    },
    {
      name: 'vertexerp_backend',
      type: 'FastAPI Core',
      endpoint: 'http://localhost:8000/api/v1',
      port: 8000,
      status: 'Healthy',
      version: '1.1.0',
    },
    {
      name: 'vertexerp_postgres',
      type: 'Database (Postgres 17)',
      endpoint: 'localhost:5432',
      port: 5432,
      status: 'Healthy',
      version: '17.0',
    },
    {
      name: 'vertexerp_redis',
      type: 'Cache Server (Redis 7)',
      endpoint: 'localhost:6379',
      port: 6379,
      status: 'Healthy',
      version: '7.0',
    },
  ]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="space-y-8"
    >
      {/* Top Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <LayoutDashboard className="h-5 w-5" />
            Core Console
          </h1>
          <p className="text-sm text-muted-foreground">
            System resources and services management panel.
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs border border-border px-3 py-1.5 rounded bg-secondary/30 select-none">
          <CheckCircle2 className="h-4 w-4 text-emerald-500" />
          <span className="font-mono text-muted-foreground">Sprint 1.1 Architecture Validated</span>
        </div>
      </div>

      {/* Grid of Key stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="border border-border p-6 rounded bg-card flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-xs text-muted-foreground uppercase font-mono tracking-wider">
              System Status
            </span>
            <h4 className="text-xl font-bold font-mono">100.0%</h4>
          </div>
          <div className="p-3 border border-border bg-secondary/30 rounded">
            <Server className="h-5 w-5 text-muted-foreground" />
          </div>
        </div>

        <div className="border border-border p-6 rounded bg-card flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-xs text-muted-foreground uppercase font-mono tracking-wider">
              CPU Average
            </span>
            <h4 className="text-xl font-bold font-mono">21.5%</h4>
          </div>
          <div className="p-3 border border-border bg-secondary/30 rounded">
            <Cpu className="h-5 w-5 text-muted-foreground" />
          </div>
        </div>

        <div className="border border-border p-6 rounded bg-card flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-xs text-muted-foreground uppercase font-mono tracking-wider">
              Active Services
            </span>
            <h4 className="text-xl font-bold font-mono">4 / 4</h4>
          </div>
          <div className="p-3 border border-border bg-secondary/30 rounded">
            <Database className="h-5 w-5 text-muted-foreground" />
          </div>
        </div>
      </div>

      {/* Recharts Analytics Panel */}
      <div className="border border-border rounded bg-card p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <h3 className="text-base font-semibold">Service Performance Trends</h3>
            <p className="text-xs text-muted-foreground">
              Resource usage telemetry over past 6 hours
            </p>
          </div>
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <TrendingUp className="h-4 w-4" />
            Live Updates
          </div>
        </div>

        <div className="h-[240px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.2} />
                  <stop offset="95%" stopColor="var(--primary)" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" />
              <XAxis dataKey="time" stroke="var(--muted)" fontSize={11} tickLine={false} />
              <YAxis stroke="var(--muted)" fontSize={11} tickLine={false} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--card)',
                  borderColor: 'var(--border)',
                  color: 'var(--foreground)',
                  fontSize: 12,
                }}
              />
              <Area
                type="monotone"
                dataKey="requests"
                stroke="var(--foreground)"
                fillOpacity={1}
                fill="url(#colorCpu)"
                strokeWidth={1.5}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* AG Grid Services Panel */}
      <div className="border border-border rounded bg-card p-6 space-y-4">
        <div>
          <h3 className="text-base font-semibold">Infrastructure Orchestration</h3>
          <p className="text-xs text-muted-foreground">
            Operational containers mapped in the bridge network
          </p>
        </div>

        <div className="ag-theme-alpine w-full h-[220px] rounded border border-border overflow-hidden">
          <AgGridReact
            rowData={rowData}
            columnDefs={columnDefs}
            domLayout="normal"
          />
        </div>
      </div>
    </motion.div>
  );
}
export default DashboardPlaceholder;
