import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Plus, Loader2, Check, X } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { Input } from '@/components/Input';
import { useNotification } from '@/hooks/useNotification';
import { apiClient } from '@/services/apiClient';

const leaveRequestSchema = z.object({
  employee_id: z.string().min(1, 'Employee is required'),
  leave_type_id: z.string().min(1, 'Leave type is required'),
  start_date: z.string().min(1, 'Start date is required'),
  end_date: z.string().min(1, 'End date is required'),
  reason: z.string().min(5, 'Reason must be at least 5 characters'),
});

export function HRLeaveManagement() {
  const { addNotification } = useNotification();
  const [employees, setEmployees] = useState<any[]>([]);
  const [leaveTypes, setLeaveTypes] = useState<any[]>([]);
  const [balances, setBalances] = useState<any[]>([]);
  const [requests, setRequests] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<any>({
    resolver: zodResolver(leaveRequestSchema),
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [empRes, typeRes, balRes, reqRes] = await Promise.all([
        apiClient.get('/api/v1/employees'),
        apiClient.get('/api/v1/leaves/types'),
        apiClient.get('/api/v1/leaves/balances'),
        apiClient.get('/api/v1/leaves/requests'),
      ]);
      setEmployees(empRes.data.data || []);
      setLeaveTypes(typeRes.data.data || []);
      setBalances(balRes.data.data || []);
      setRequests(reqRes.data.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const onSubmit = async (values: any) => {
    try {
      await apiClient.post('/api/v1/leaves/requests', values);
      addNotification('Leave request submitted successfully', 'success');
      setModalOpen(false);
      reset();
      fetchData();
    } catch (err: any) {
      addNotification(err.response?.data?.detail || 'Submission failed', 'error');
    }
  };

  const handleProcessRequest = async (id: string, status: 'approved' | 'rejected') => {
    try {
      await apiClient.put(`/api/v1/leaves/requests/${id}/approval`, {
        status,
        approval_comment: `${status === 'approved' ? 'Approved' : 'Rejected'} via HR panel.`,
      });
      addNotification(`Leave request ${status}`, 'success');
      fetchData();
    } catch (err: any) {
      addNotification(err.response?.data?.detail || 'Approval step failed', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Leave Management</h1>
          <p className="text-sm text-muted-foreground">Manage corporate leave types, verify employee balances, and audit approvals.</p>
        </div>
        <Button onClick={() => setModalOpen(true)} variant="primary" className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Apply for Leave
        </Button>
      </div>

      {/* Leave Balances */}
      <Card>
        <CardHeader>
          <CardTitle>Employee Leave Balances</CardTitle>
          <CardDescription>Visual breakdown of remaining, allocated, and used days.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {balances.length === 0 ? (
              <p className="text-xs text-muted-foreground italic py-2">No leave balances found.</p>
            ) : (
              balances.map((b) => (
                <div key={b.id} className="p-4 border border-border rounded bg-secondary/10 flex flex-col justify-between space-y-2">
                  <div className="flex justify-between items-center text-xs font-mono">
                    <span className="font-semibold text-primary">Employee {b.employee_id.slice(0, 8)}...</span>
                    <span className="text-muted-foreground uppercase">{b.year}</span>
                  </div>
                  <div className="flex justify-between items-end">
                    <div>
                      <p className="text-xs text-muted-foreground">Remaining days</p>
                      <h4 className="text-xl font-bold font-mono tracking-tight">{b.remaining} days</h4>
                    </div>
                    <span className="text-[10px] text-muted-foreground font-mono">Allocated: {b.allocated}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>

      {/* Requests Registry */}
      <Card>
        <CardHeader>
          <CardTitle>Leave Requests & Approvals Workflow</CardTitle>
          <CardDescription>File details, date ranges, and approval parameters.</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center py-6">
              <Loader2 className="h-6 w-6 animate-spin text-primary" />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left border-collapse">
                <thead>
                  <tr className="border-b border-border text-muted-foreground text-xs uppercase font-mono">
                    <th className="py-2.5 px-3">Employee</th>
                    <th className="py-2.5 px-3">Date Range</th>
                    <th className="py-2.5 px-3 text-right">Total Days</th>
                    <th className="py-2.5 px-3">Reason</th>
                    <th className="py-2.5 px-3">Status</th>
                    <th className="py-2.5 px-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {requests.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="py-6 text-center text-muted-foreground text-xs">No leave requests logged.</td>
                    </tr>
                  ) : (
                    requests.map((r) => (
                      <tr key={r.id} className="border-b border-border hover:bg-secondary/10 text-xs">
                        <td className="py-3 px-3 font-mono">Emp {r.employee_id.slice(0, 8)}...</td>
                        <td className="py-3 px-3 font-mono">{r.start_date} to {r.end_date}</td>
                        <td className="py-3 px-3 text-right font-mono font-semibold">{r.total_days} days</td>
                        <td className="py-3 px-3 text-muted-foreground truncate max-w-[150px]">{r.reason}</td>
                        <td className="py-3 px-3 uppercase font-semibold">
                          <span className={`px-2 py-0.5 rounded text-[10px] ${
                            r.status === 'approved' ? 'bg-emerald-500/10 text-emerald-500' :
                            r.status === 'rejected' ? 'bg-red-500/10 text-red-500' : 'bg-amber-500/10 text-amber-500'
                          }`}>
                            {r.status}
                          </span>
                        </td>
                        <td className="py-3 px-3 text-right">
                          {r.status === 'pending' && (
                            <div className="flex items-center justify-end gap-1.5">
                              <button
                                onClick={() => handleProcessRequest(r.id, 'approved')}
                                className="p-1 hover:bg-emerald-500/10 text-emerald-500 rounded border border-emerald-500/20"
                              >
                                <Check className="h-3.5 w-3.5" />
                              </button>
                              <button
                                onClick={() => handleProcessRequest(r.id, 'rejected')}
                                className="p-1 hover:bg-red-500/10 text-red-500 rounded border border-red-500/20"
                              >
                                <X className="h-3.5 w-3.5" />
                              </button>
                            </div>
                          )}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title="Apply for Leave">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="flex flex-col space-y-1.5">
            <label className="text-sm font-medium">Employee</label>
            <select
              {...register('employee_id')}
              className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none"
            >
              <option value="">-- Select Employee --</option>
              {employees.map((emp) => (
                <option key={emp.id} value={emp.id}>{emp.employee_code}</option>
              ))}
            </select>
            {errors.employee_id && <p className="text-xs text-red-500">{errors.employee_id.message as string}</p>}
          </div>

          <div className="flex flex-col space-y-1.5">
            <label className="text-sm font-medium">Leave Type</label>
            <select
              {...register('leave_type_id')}
              className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none"
            >
              <option value="">-- Select Type --</option>
              {leaveTypes.map((t) => (
                <option key={t.id} value={t.id}>{t.name} ({t.code})</option>
              ))}
            </select>
            {errors.leave_type_id && <p className="text-xs text-red-500">{errors.leave_type_id.message as string}</p>}
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Input label="Start Date" type="date" {...register('start_date')} error={errors.start_date?.message as string} />
            <Input label="End Date" type="date" {...register('end_date')} error={errors.end_date?.message as string} />
          </div>

          <Input label="Reason" {...register('reason')} error={errors.reason?.message as string} />

          <div className="flex justify-end gap-2 pt-4">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary">Submit Request</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
export default HRLeaveManagement;
