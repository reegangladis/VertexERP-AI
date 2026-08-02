import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Plus, Loader2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { Input } from '@/components/Input';
import { useNotification } from '@/hooks/useNotification';
import { apiClient } from '@/services/apiClient';

const taskSchema = z.object({
  title: z.string().min(3, 'Title must be at least 3 characters'),
  description: z.string().optional(),
  due_date: z.string().min(1, 'Due date is required'),
  priority: z.string().default('medium'),
});

export function CRMActivities() {
  const { addNotification } = useNotification();
  const [tasks, setTasks] = useState<any[]>([]);
  const [meetings, setMeetings] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<any>({
    resolver: zodResolver(taskSchema),
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [tasksRes, meetingsRes] = await Promise.all([
        apiClient.get('/api/v1/crm/activities/tasks'),
        apiClient.get('/api/v1/crm/activities/meetings'),
      ]);
      setTasks(tasksRes.data.data || []);
      setMeetings(meetingsRes.data.data || []);
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
      await apiClient.post('/api/v1/crm/activities/tasks', values);
      addNotification('Task created successfully', 'success');
      setModalOpen(false);
      reset();
      fetchData();
    } catch (err: any) {
      addNotification(err.response?.data?.detail || 'Task setup failed', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Activities log</h1>
          <p className="text-sm text-muted-foreground">Monitor scheduled events, record customer calls, and audit tasks.</p>
        </div>
        <Button onClick={() => setModalOpen(true)} variant="primary" className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Assign Task
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Tasks Registry */}
        <Card>
          <CardHeader>
            <CardTitle>Assigned Tasks</CardTitle>
            <CardDescription>Task priorities, status lists, and close dates.</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex justify-center py-6">
                <Loader2 className="h-6 w-6 animate-spin text-primary" />
              </div>
            ) : (
              <div className="space-y-3">
                {tasks.length === 0 ? (
                  <p className="text-xs text-muted-foreground italic text-center py-4">No tasks pending.</p>
                ) : (
                  tasks.map((t) => (
                    <div key={t.id} className="p-3 border border-border rounded bg-secondary/15 flex justify-between items-center text-xs">
                      <div>
                        <h4 className="font-semibold text-foreground">{t.title}</h4>
                        <p className="text-[10px] text-muted-foreground">Due: {t.due_date} • Priority: {t.priority}</p>
                      </div>
                      <span className="bg-secondary px-2 py-0.5 rounded text-[10px] uppercase font-mono">{t.status}</span>
                    </div>
                  ))
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Meetings */}
        <Card>
          <CardHeader>
            <CardTitle>Meetings Schedule</CardTitle>
            <CardDescription>Customer alignment meetings, duration rates, and video link URLs.</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex justify-center py-6">
                <Loader2 className="h-6 w-6 animate-spin text-primary" />
              </div>
            ) : (
              <div className="space-y-3">
                {meetings.length === 0 ? (
                  <p className="text-xs text-muted-foreground italic text-center py-4">No meetings scheduled.</p>
                ) : (
                  meetings.map((m) => (
                    <div key={m.id} className="p-3 border border-border rounded bg-secondary/15 text-xs space-y-1">
                      <div className="flex justify-between items-start">
                        <h4 className="font-semibold text-primary">{m.title}</h4>
                        <span className="text-[10px] font-mono text-muted-foreground">{m.duration_minutes} mins</span>
                      </div>
                      <p className="text-[10px] text-muted-foreground">Scheduled: {new Date(m.scheduled_at).toLocaleString()}</p>
                      {m.location_or_url && (
                        <p className="text-[10px] text-primary truncate">Link: {m.location_or_url}</p>
                      )}
                    </div>
                  ))
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title="Assign Activity Task">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input label="Task Title" {...register('title')} error={errors.title?.message as string} />
          <Input label="Description" {...register('description')} />
          <Input label="Due Date" type="date" {...register('due_date')} error={errors.due_date?.message as string} />

          <div className="flex flex-col space-y-1.5">
            <label className="text-sm font-medium">Priority</label>
            <select
              {...register('priority')}
              className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none"
            >
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary">Configure Task</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
export default CRMActivities;
