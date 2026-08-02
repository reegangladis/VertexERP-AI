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

const courseSchema = z.object({
  title: z.string().min(3, 'Course title must be at least 3 characters'),
  description: z.string().optional(),
  instructor: z.string().min(2, 'Instructor must be at least 2 characters'),
  duration_hours: z.preprocess((val) => parseFloat(val as string) || 0, z.number().min(0.5, 'Duration must be at least 0.5 hours')),
});

export function HRTraining() {
  const { addNotification } = useNotification();
  const [courses, setCourses] = useState<any[]>([]);
  const [records, setRecords] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<any>({
    resolver: zodResolver(courseSchema),
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [coursesRes, recordsRes] = await Promise.all([
        apiClient.get('/api/v1/training/courses'),
        apiClient.get('/api/v1/training/records'),
      ]);
      setCourses(coursesRes.data.data || []);
      setRecords(recordsRes.data.data || []);
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
      await apiClient.post('/api/v1/training/courses', values);
      addNotification('Course catalog entry added successfully', 'success');
      setModalOpen(false);
      reset();
      fetchData();
    } catch (err: any) {
      addNotification(err.response?.data?.detail || 'Add failed', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">L&D Training Center</h1>
          <p className="text-sm text-muted-foreground">Manage certification courses, student schedules, and completion records.</p>
        </div>
        <Button onClick={() => setModalOpen(true)} variant="primary" className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Publish Course
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Course Catalog */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Certification courses directory</CardTitle>
            <CardDescription>Available trainings, description parameters, and duration metrics.</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex justify-center py-6">
                <Loader2 className="h-6 w-6 animate-spin text-primary" />
              </div>
            ) : (
              <div className="space-y-4">
                {courses.length === 0 ? (
                  <p className="text-xs text-muted-foreground italic py-2">No courses registered.</p>
                ) : (
                  courses.map((c) => (
                    <div key={c.id} className="p-4 border border-border rounded bg-secondary/15 space-y-2">
                      <div className="flex justify-between items-start">
                        <div>
                          <h4 className="text-sm font-bold text-primary">{c.title}</h4>
                          <p className="text-[11px] text-muted-foreground font-mono">Instructor: {c.instructor} • Duration: {c.duration_hours} hrs</p>
                        </div>
                      </div>
                      <p className="text-xs text-muted-foreground">{c.description}</p>
                    </div>
                  ))
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Enrollment Progress */}
        <Card className="md:col-span-1">
          <CardHeader>
            <CardTitle>Active Assignments progress</CardTitle>
            <CardDescription>Employee progression rates and completions list.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {records.length === 0 ? (
              <p className="text-xs text-muted-foreground italic text-center py-4">No employees assigned to courses.</p>
            ) : (
              records.map((rec) => (
                <div key={rec.id} className="p-3 border border-border rounded bg-card space-y-2 text-xs">
                  <div className="flex justify-between font-semibold">
                    <span className="text-primary truncate max-w-[120px]">Employee {rec.employee_id.slice(0, 8)}...</span>
                    <span className="font-mono text-muted-foreground uppercase">{rec.status}</span>
                  </div>
                  <div className="w-full bg-secondary rounded-full h-1 overflow-hidden">
                    <div className="bg-primary h-1" style={{ width: `${rec.progress}%` }}></div>
                  </div>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title="Publish Course">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input label="Course Title" {...register('title')} error={errors.title?.message as string} />
          <Input label="Description" {...register('description')} />
          <Input label="Instructor Name" {...register('instructor')} error={errors.instructor?.message as string} />
          <Input label="Duration (Hours)" type="number" step="0.5" {...register('duration_hours')} error={errors.duration_hours?.message as string} />

          <div className="flex justify-end gap-2 pt-4">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary">Publish Course</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
export default HRTraining;
