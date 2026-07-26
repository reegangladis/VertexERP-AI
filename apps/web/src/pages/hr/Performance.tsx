import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Award, Target, TrendingUp, Plus, Loader2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { Input } from '@/components/Input';
import { useNotification } from '@/hooks/useNotification';
import { apiClient } from '@/services/apiClient';

const goalSchema = z.object({
  employee_id: z.string().min(1, 'Employee is required'),
  title: z.string().min(3, 'Goal title must be at least 3 characters'),
  description: z.string().optional(),
  target_date: z.string().min(1, 'Target date is required'),
});

export function HRPerformance() {
  const { addNotification } = useNotification();
  const [employees, setEmployees] = useState<any[]>([]);
  const [goals, setGoals] = useState<any[]>([]);
  const [reviews, setReviews] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<any>({
    resolver: zodResolver(goalSchema),
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [empRes, goalsRes, revRes] = await Promise.all([
        apiClient.get('/api/v1/employees'),
        apiClient.get('/api/v1/performance/goals'),
        apiClient.get('/api/v1/performance/reviews'),
      ]);
      setEmployees(empRes.data.data || []);
      setGoals(goalsRes.data.data || []);
      setReviews(revRes.data.data || []);
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
      await apiClient.post('/api/v1/performance/goals', {
        ...values,
        progress: 0,
        status: 'not_started',
      });
      addNotification('Individual goal configured successfully', 'success');
      setModalOpen(false);
      reset();
      fetchData();
    } catch (err: any) {
      addNotification(err.response?.data?.detail || 'Goal setting failed', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Performance Tiers & Goals</h1>
          <p className="text-sm text-muted-foreground">Log employee target goals, KPI progress, and manager review cycles.</p>
        </div>
        <Button onClick={() => setModalOpen(true)} variant="primary" className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Assign Target Goal
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Performance Goals */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Staff KPIs & Goals</CardTitle>
            <CardDescription>Progress checklist and target completion dates.</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex justify-center py-6">
                <Loader2 className="h-6 w-6 animate-spin text-primary" />
              </div>
            ) : (
              <div className="space-y-4">
                {goals.length === 0 ? (
                  <p className="text-xs text-muted-foreground italic py-2">No active goals configured.</p>
                ) : (
                  goals.map((g) => (
                    <div key={g.id} className="p-4 border border-border rounded bg-secondary/15 space-y-2">
                      <div className="flex justify-between items-start">
                        <div>
                          <h4 className="text-sm font-bold text-primary">{g.title}</h4>
                          <p className="text-[11px] text-muted-foreground uppercase font-mono">Employee: {g.employee_id.slice(0, 8)}... • Target: {g.target_date}</p>
                        </div>
                        <span className="text-xs font-mono font-bold text-primary">{g.progress}%</span>
                      </div>
                      <div className="w-full bg-secondary rounded-full h-1.5 overflow-hidden">
                        <div className="bg-primary h-1.5" style={{ width: `${g.progress}%` }}></div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Review Cycles */}
        <Card className="md:col-span-1">
          <CardHeader>
            <CardTitle>Review Logs History</CardTitle>
            <CardDescription>Historic manager scorecards, ratings, and self assessment statements.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {reviews.length === 0 ? (
              <p className="text-xs text-muted-foreground italic">No review cards saved.</p>
            ) : (
              reviews.map((r) => (
                <div key={r.id} className="p-3 border border-border rounded bg-card space-y-1.5 text-xs">
                  <div className="flex justify-between items-center font-semibold">
                    <span className="text-primary uppercase font-mono text-[10px]">{r.review_cycle}</span>
                    <span className="font-mono text-emerald-500 font-bold">{r.rating} / 5.0</span>
                  </div>
                  <p className="text-muted-foreground italic">"{r.manager_feedback || 'No comments logged'}"</p>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title="Assign Target Goal">
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

          <Input label="Goal Title" {...register('title')} error={errors.title?.message as string} />
          <Input label="Description" {...register('description')} />
          <Input label="Target Date" type="date" {...register('target_date')} error={errors.target_date?.message as string} />

          <div className="flex justify-end gap-2 pt-4">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary">Set Target</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
export default HRPerformance;
