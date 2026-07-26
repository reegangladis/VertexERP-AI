import { useState, useEffect } from 'react';
import { Clock, Play, Square, Loader2, ArrowRight } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { useNotification } from '@/hooks/useNotification';
import { apiClient } from '@/services/apiClient';

interface AttendanceRecord {
  id: string;
  employee_id: string;
  date: string;
  check_in: string | null;
  check_out: string | null;
  total_hours: number;
  status: string;
  is_late_arrival: boolean;
  is_early_exit: boolean;
  overtime_minutes: number;
}

export function HRAttendance() {
  const { addNotification } = useNotification();
  const [employees, setEmployees] = useState<any[]>([]);
  const [selectedEmpId, setSelectedEmpId] = useState('');
  const [records, setRecords] = useState<AttendanceRecord[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchData = async () => {
    try {
      const [empRes, attRes] = await Promise.all([
        apiClient.get('/api/v1/employees'),
        apiClient.get('/api/v1/attendance'),
      ]);
      const activeEmps = empRes.data.data || [];
      setEmployees(activeEmps);
      if (activeEmps.length > 0 && !selectedEmpId) {
        setSelectedEmpId(activeEmps[0].id);
      }
      setRecords(attRes.data.data || []);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCheckIn = async () => {
    if (!selectedEmpId) return;
    setLoading(true);
    try {
      await apiClient.post('/api/v1/attendance/check-in', {
        employee_id: selectedEmpId,
      });
      addNotification('Check-in successful!', 'success');
      fetchData();
    } catch (err: any) {
      addNotification(err.response?.data?.detail || 'Check-in failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleCheckOut = async () => {
    if (!selectedEmpId) return;
    setLoading(true);
    try {
      await apiClient.post('/api/v1/attendance/check-out', {
        employee_id: selectedEmpId,
      });
      addNotification('Check-out successful!', 'success');
      fetchData();
    } catch (err: any) {
      addNotification(err.response?.data?.detail || 'Check-out failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Time & Attendance</h1>
        <p className="text-sm text-muted-foreground">Log employee shift hours, punch check-ins, breaks, and overtime telemetry.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="md:col-span-1">
          <CardHeader>
            <CardTitle>Shift Control Center</CardTitle>
            <CardDescription>Punch check-in/out for active employees.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-col space-y-1.5">
              <label className="text-sm font-medium">Select Employee</label>
              <select
                value={selectedEmpId}
                onChange={(e) => setSelectedEmpId(e.target.value)}
                className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none"
              >
                {employees.map((emp) => (
                  <option key={emp.id} value={emp.id}>
                    {emp.employee_code}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex flex-col gap-3 pt-2">
              <Button onClick={handleCheckIn} disabled={loading} className="w-full flex items-center justify-center gap-2" variant="primary">
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
                Punch Check In
              </Button>
              <Button onClick={handleCheckOut} disabled={loading} className="w-full flex items-center justify-center gap-2" variant="secondary">
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Square className="h-4 w-4" />}
                Punch Check Out
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Attendance Log Registry</CardTitle>
            <CardDescription>Visual history of working shifts, breaks, late marks, and overtime limits.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left border-collapse">
                <thead>
                  <tr className="border-b border-border text-muted-foreground text-xs uppercase font-mono">
                    <th className="py-2.5 px-3">Date</th>
                    <th className="py-2.5 px-3">In / Out Timestamps</th>
                    <th className="py-2.5 px-3 text-right">Hours</th>
                    <th className="py-2.5 px-3 text-right">Overtime</th>
                    <th className="py-2.5 px-3 text-right">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {records.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="py-8 text-center text-muted-foreground text-xs">
                        No check-ins logged for today.
                      </td>
                    </tr>
                  ) : (
                    records.map((r) => (
                      <tr key={r.id} className="border-b border-border hover:bg-secondary/10 text-xs">
                        <td className="py-3 px-3 font-semibold font-mono">{r.date}</td>
                        <td className="py-3 px-3">
                          <div className="flex items-center gap-1.5 font-mono text-[11px]">
                            <span className="text-emerald-500">{r.check_in ? new Date(r.check_in).toLocaleTimeString() : '--:--'}</span>
                            <ArrowRight className="h-3 w-3 text-muted-foreground" />
                            <span className="text-red-500">{r.check_out ? new Date(r.check_out).toLocaleTimeString() : '--:--'}</span>
                          </div>
                        </td>
                        <td className="py-3 px-3 text-right font-mono font-semibold">{r.total_hours} hrs</td>
                        <td className="py-3 px-3 text-right font-mono text-muted-foreground">{r.overtime_minutes} mins</td>
                        <td className="py-3 px-3 text-right font-semibold uppercase">
                          <span className={`px-2 py-0.5 rounded text-[10px] ${r.is_late_arrival ? 'bg-amber-500/10 text-amber-500' : 'bg-emerald-500/10 text-emerald-500'}`}>
                            {r.is_late_arrival ? 'Late' : 'Present'}
                          </span>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
export default HRAttendance;
