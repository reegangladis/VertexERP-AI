import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { DollarSign, ShieldAlert, Plus, Loader2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { Input } from '@/components/Input';
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
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);

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
      const [empRes, salaryRes] = await Promise.all([
        apiClient.get('/api/v1/employees'),
        apiClient.get('/api/v1/payroll/salary-structures'),
      ]);
      setEmployees(empRes.data.data || []);
      setStructures(salaryRes.data.data || []);
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

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Payroll Administration</h1>
          <p className="text-sm text-muted-foreground">Configure salary structures, basic pay levels, tax components, and benefits directories.</p>
        </div>
        <Button onClick={() => setModalOpen(true)} variant="primary" className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Setup Salary Structure
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Configured Salary Tiers</CardTitle>
            <CardDescription>Base pay levels, allowances, deductions, and effective ranges.</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex justify-center py-6">
                <Loader2 className="h-6 w-6 animate-spin text-primary" />
              </div>
            ) : (
              <div className="space-y-3">
                {structures.length === 0 ? (
                  <p className="text-xs text-muted-foreground italic py-2">No structures set up. Seed data to check samples.</p>
                ) : (
                  structures.map((s) => (
                    <div key={s.id} className="p-4 border border-border rounded bg-secondary/15 flex justify-between items-center text-xs">
                      <div>
                        <h4 className="font-semibold text-primary font-mono">Employee: {s.employee_id.slice(0, 8)}...</h4>
                        <p className="text-muted-foreground">Effective: {s.effective_from}</p>
                      </div>
                      <div className="text-right">
                        <span className="font-mono text-base font-bold text-emerald-500">${s.base_salary}</span>
                        <p className="text-[10px] text-muted-foreground font-mono">Base / Month</p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="md:col-span-1">
          <CardHeader>
            <CardTitle>Calculation Engine status</CardTitle>
            <CardDescription>System status indicators</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-xs">
            <div className="flex items-center gap-2 p-3 bg-amber-500/10 border border-amber-500/20 text-amber-500 rounded">
              <ShieldAlert className="h-5 w-5 shrink-0" />
              <span>Payroll calculation engine is disabled. Database mappings and tax structures are configured for future operations.</span>
            </div>
          </CardContent>
        </Card>
      </div>

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

          <Input label="Base Salary (Monthly)" type="number" {...register('base_salary')} error={errors.base_salary?.message as string} />
          <Input label="Effective From" type="date" {...register('effective_from')} error={errors.effective_from?.message as string} />

          <div className="flex justify-end gap-2 pt-4">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary">Configure Structure</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
export default HRPayroll;
