import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Briefcase, Users, Calendar, Plus, Loader2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { Input } from '@/components/Input';
import { useNotification } from '@/hooks/useNotification';
import { apiClient } from '@/services/apiClient';

const jobSchema = z.object({
  title: z.string().min(3, 'Job title must be at least 3 characters'),
  description: z.string().min(10, 'Job description must be at least 10 characters'),
  requirements: z.string().optional(),
  employment_type: z.string().default('full-time'),
});

export function HRRecruitment() {
  const { addNotification } = useNotification();
  const [jobs, setJobs] = useState<any[]>([]);
  const [candidates, setCandidates] = useState<any[]>([]);
  const [applications, setApplications] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<any>({
    resolver: zodResolver(jobSchema),
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [jobsRes, candRes, appRes] = await Promise.all([
        apiClient.get('/api/v1/recruitment/jobs'),
        apiClient.get('/api/v1/recruitment/candidates'),
        apiClient.get('/api/v1/recruitment/applications'),
      ]);
      setJobs(jobsRes.data.data || []);
      setCandidates(candRes.data.data || []);
      setApplications(appRes.data.data || []);
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
      await apiClient.post('/api/v1/recruitment/jobs', values);
      addNotification('Job position published successfully', 'success');
      setModalOpen(false);
      reset();
      fetchData();
    } catch (err: any) {
      addNotification(err.response?.data?.detail || 'Publishing failed', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Recruitment & Hiring</h1>
          <p className="text-sm text-muted-foreground">Manage corporate jobs catalog, track applicant status, and audit interview feedback.</p>
        </div>
        <Button onClick={() => setModalOpen(true)} variant="primary" className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Create Job Position
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Active Openings */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Active Openings catalog</CardTitle>
            <CardDescription>Open positions list, requirements guidelines, and recruitment settings.</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex justify-center py-6">
                <Loader2 className="h-6 w-6 animate-spin text-primary" />
              </div>
            ) : (
              <div className="space-y-4">
                {jobs.length === 0 ? (
                  <p className="text-xs text-muted-foreground italic py-2">No job positions open.</p>
                ) : (
                  jobs.map((job) => (
                    <div key={job.id} className="p-4 border border-border rounded bg-secondary/15 space-y-2">
                      <div className="flex justify-between items-start">
                        <div>
                          <h4 className="text-sm font-bold text-primary">{job.title}</h4>
                          <p className="text-[11px] text-muted-foreground uppercase font-mono">{job.employment_type} • {job.status}</p>
                        </div>
                      </div>
                      <p className="text-xs text-muted-foreground">{job.description}</p>
                    </div>
                  ))
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Candidate Pipeline */}
        <Card className="md:col-span-1">
          <CardHeader>
            <CardTitle>Candidate Pipelines</CardTitle>
            <CardDescription>Visual applicant pipeline list and details.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {candidates.length === 0 ? (
              <p className="text-xs text-muted-foreground italic">No candidates enrolled.</p>
            ) : (
              candidates.map((c) => (
                <div key={c.id} className="p-3 border border-border rounded bg-card flex flex-col space-y-1 text-xs">
                  <div className="flex justify-between font-semibold text-primary">
                    <span>{c.first_name} {c.last_name}</span>
                    <span className="font-mono text-[9px] uppercase text-muted-foreground">{c.id.slice(0, 8)}</span>
                  </div>
                  <p className="text-muted-foreground truncate">{c.headline || 'No headline logged'}</p>
                  {c.skills && c.skills.list && (
                    <div className="flex flex-wrap gap-1 pt-1.5">
                      {c.skills.list.map((skill: string, idx: number) => (
                        <span key={idx} className="bg-secondary/40 border border-border text-muted-foreground rounded px-1.5 py-0.5 text-[9px] font-mono">
                          {skill}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title="Create Job Opening">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input label="Job Title" {...register('title')} error={errors.title?.message as string} />
          <div className="flex flex-col space-y-1.5">
            <label className="text-sm font-medium">Description</label>
            <textarea
              {...register('description')}
              rows={3}
              className="border border-input rounded-md bg-background p-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
            {errors.description && <p className="text-xs text-red-500">{errors.description.message as string}</p>}
          </div>

          <div className="flex flex-col space-y-1.5">
            <label className="text-sm font-medium">Requirements</label>
            <textarea
              {...register('requirements')}
              rows={2}
              className="border border-input rounded-md bg-background p-3 text-sm focus:outline-none"
            />
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary">Publish Position</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
export default HRRecruitment;
