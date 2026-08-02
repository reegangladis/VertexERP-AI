import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { DollarSign, ShieldCheck, Plus, Loader2, Play, FileText, CheckCircle2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { Input } from '@/components/Input';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/Table';
import { useNotification } from '@/hooks/useNotification';
import { apiClient } from '@/services/apiClient';

const salarySchema = z.object({
  employee_id: z.string().min(1, 'Employee is required'),
  base_salary: z.preprocess((val) => parseFloat(val as string) || 0, z.number().min(100, 'Base salary must be at least 100')),
  effective_from: z.string().min(1, 'Effective date is required'),
});

export function HRPayroll() {
  const { addNotification } = useNotification();
  const [employees, setEmployees] = useState<any[]>([]);
  const [structures, setStructures] = useState<any[]>([]);
  const [runs, setRuns] = useState<any[]>([]);
  const [payslips, setPayslips] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [payslipModalOpen, setPayslipModalOpen] = useState(false);
  const [selectedPayslip, setSelectedPayslip] = useState<any>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<any>({
    resolver: zodResolver(salarySchema),
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [empRes, salaryRes, runsRes, payslipsRes] = await Promise.all([
        apiClient.get('/api/v1/employees'),
        apiClient.get('/api/v1/payroll/salary-structures'),
        apiClient.get('/api/v1/payroll/runs'),
        apiClient.get('/api/v1/payroll/payslips'),
      ]);
      setEmployees(empRes.data.data || []);
      setStructures(salaryRes.data.data || []);
      setRuns(runsRes.data.data || []);
      setPayslips(payslipsRes.data.data || []);
    } catch (err) {
      console.error("Failed to load payroll data", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const onSubmit = async (values: any) => {
    try {
      await apiClient.post('/api/v1/payroll/salary-structures', {
        ...values,
        allowances: { HRA: values.base_salary * 0.1, Travel: 500.0 },
        deductions: { PF: values.base_salary * 0.05, Tax: values.base_salary * 0.15 },
        benefits: { 'Health Insurance': 'Standard plan' },
      });
      addNotification('Salary structure configured successfully', 'success');
      setModalOpen(false);
      reset();
      fetchData();
    } catch (err: any) {
      addNotification(err.response?.data?.detail || 'Salary setup failed', 'error');
    }
  };

  const handleRunPayroll = async () => {
    setProcessing(true);
    try {
      const now = new Date();
      const month = now.getMonth() + 1;
      const year = now.getFullYear();
      await apiClient.post('/api/v1/payroll/process', {
        period_month: month,
        period_year: year,
      });
      addNotification(`Monthly payroll for ${month}/${year} processed successfully!`, 'success');
      fetchData();
    } catch (err: any) {
      addNotification(err.response?.data?.detail || 'Payroll processing failed', 'error');
    } finally {
      setProcessing(false);
    }
  };

  const latestRun = runs[0];

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Payroll Engine & Administration</h1>
          <p className="text-sm text-muted-foreground">Process monthly payroll runs, compute net salaries, generate payslips, and manage salary structures.</p>
        </div>
        <div className="flex items-center gap-3">
          <Button onClick={handleRunPayroll} disabled={processing} variant="primary" className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700">
            {processing ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4 fill-current" />}
            Execute Monthly Payroll
          </Button>
          <Button onClick={() => setModalOpen(true)} variant="secondary" className="flex items-center gap-2">
            <Plus className="h-4 w-4" />
            Setup Salary Structure
          </Button>
        </div>
      </div>

      {/* Telemetry Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4 flex items-center gap-4">
          <div className="p-3 bg-emerald-500/10 text-emerald-500 rounded-xl">
            <DollarSign className="h-6 w-6" />
          </div>
          <div>
            <p className="text-xs text-muted-foreground font-mono">Latest Gross Payroll</p>
            <h3 className="text-lg font-bold font-mono text-emerald-500">${latestRun ? latestRun.total_gross.toLocaleString() : '0.00'}</h3>
          </div>
        </Card>
        <Card className="p-4 flex items-center gap-4">
          <div className="p-3 bg-blue-500/10 text-blue-500 rounded-xl">
            <ShieldCheck className="h-6 w-6" />
          </div>
          <div>
            <p className="text-xs text-muted-foreground font-mono">Total Net Disbursed</p>
            <h3 className="text-lg font-bold font-mono text-blue-500">${latestRun ? latestRun.total_net.toLocaleString() : '0.00'}</h3>
          </div>
        </Card>
        <Card className="p-4 flex items-center gap-4">
          <div className="p-3 bg-amber-500/10 text-amber-500 rounded-xl">
            <FileText className="h-6 w-6" />
          </div>
          <div>
            <p className="text-xs text-muted-foreground font-mono">Payslips Generated</p>
            <h3 className="text-lg font-bold font-mono text-amber-500">{payslips.length}</h3>
          </div>
        </Card>
        <Card className="p-4 flex items-center gap-4">
          <div className="p-3 bg-purple-500/10 text-purple-500 rounded-xl">
            <CheckCircle2 className="h-6 w-6" />
          </div>
          <div>
            <p className="text-xs text-muted-foreground font-mono">Active Salary Structures</p>
            <h3 className="text-lg font-bold font-mono text-purple-500">{structures.length}</h3>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Generated Payslips & Salary Disbursal</CardTitle>
            <CardDescription>Generated payslips for current and historical payroll periods.</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex justify-center py-6">
                <Loader2 className="h-6 w-6 animate-spin text-primary" />
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Employee Code</TableHead>
                    <TableHead>Base Salary</TableHead>
                    <TableHead>Allowances</TableHead>
                    <TableHead>Deductions</TableHead>
                    <TableHead>Net Pay</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {payslips.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={6} className="text-center text-xs text-muted-foreground py-6">
                        No payslips generated yet. Click "Execute Monthly Payroll" to compute salaries.
                      </TableCell>
                    </TableRow>
                  ) : (
                    payslips.map((p) => {
                      const emp = employees.find(e => e.id === p.employee_id);
                      return (
                        <TableRow key={p.id}>
                          <TableCell className="font-mono text-xs font-bold">{emp ? emp.employee_code : p.employee_id.slice(0, 8)}</TableCell>
                          <TableCell className="font-mono text-xs">${p.base_salary}</TableCell>
                          <TableCell className="font-mono text-xs text-emerald-500">+${p.total_allowances}</TableCell>
                          <TableCell className="font-mono text-xs text-red-500">-${p.total_deductions}</TableCell>
                          <TableCell className="font-mono text-xs font-bold text-emerald-500">${p.net_salary}</TableCell>
                          <TableCell>
                            <Button
                              size="sm"
                              variant="secondary"
                              onClick={() => {
                                setSelectedPayslip({ ...p, empCode: emp ? emp.employee_code : 'N/A' });
                                setPayslipModalOpen(true);
                              }}
                              className="text-[10px] h-7 px-2"
                            >
                              View Payslip
                            </Button>
                          </TableCell>
                        </TableRow>
                      );
                    })
                  )}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        <Card className="md:col-span-1">
          <CardHeader>
            <CardTitle>Configured Salary Tiers</CardTitle>
            <CardDescription>Base pay levels and effective ranges.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {structures.length === 0 ? (
              <p className="text-xs text-muted-foreground italic py-2">No structures configured yet.</p>
            ) : (
              structures.map((s) => {
                const emp = employees.find(e => e.id === s.employee_id);
                return (
                  <div key={s.id} className="p-3 border border-border rounded-xl bg-secondary/15 flex justify-between items-center text-xs">
                    <div>
                      <h4 className="font-semibold text-primary font-mono">{emp ? emp.employee_code : s.employee_id.slice(0, 8)}</h4>
                      <p className="text-[10px] text-muted-foreground">Effective: {s.effective_from}</p>
                    </div>
                    <div className="text-right">
                      <span className="font-mono text-sm font-bold text-emerald-500">${s.base_salary}</span>
                      <p className="text-[10px] text-muted-foreground font-mono">Base / Month</p>
                    </div>
                  </div>
                );
              })
            )}
          </CardContent>
        </Card>
      </div>

      {/* Setup Salary Structure Modal */}
      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title="Setup Salary Structure">
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

          <Input label="Base Salary (Monthly $)" type="number" {...register('base_salary')} error={errors.base_salary?.message as string} />
          <Input label="Effective From" type="date" {...register('effective_from')} error={errors.effective_from?.message as string} />

          <div className="flex justify-end gap-2 pt-4">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary">Configure Structure</Button>
          </div>
        </form>
      </Modal>

      {/* View Payslip Detail Modal */}
      <Modal isOpen={payslipModalOpen} onClose={() => setPayslipModalOpen(false)} title={`Payslip Details — ${selectedPayslip?.empCode || ''}`}>
        {selectedPayslip && (
          <div className="space-y-4 text-xs">
            <div className="p-4 border border-border rounded-xl bg-secondary/15 space-y-2">
              <div className="flex justify-between font-mono">
                <span className="text-muted-foreground">Employee:</span>
                <span className="font-bold">{selectedPayslip.empCode}</span>
              </div>
              <div className="flex justify-between font-mono">
                <span className="text-muted-foreground">Base Salary:</span>
                <span>${selectedPayslip.base_salary}</span>
              </div>
              <div className="flex justify-between font-mono text-emerald-500">
                <span>Total Allowances:</span>
                <span>+${selectedPayslip.total_allowances}</span>
              </div>
              <div className="flex justify-between font-mono text-red-500">
                <span>Total Deductions:</span>
                <span>-${selectedPayslip.total_deductions}</span>
              </div>
              <div className="border-t border-border pt-2 flex justify-between font-mono text-sm font-bold text-primary">
                <span>Net Salary Payable:</span>
                <span className="text-emerald-500">${selectedPayslip.net_salary}</span>
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <Button variant="secondary" onClick={() => setPayslipModalOpen(false)}>Close</Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
export default HRPayroll;
