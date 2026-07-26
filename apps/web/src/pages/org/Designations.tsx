import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Plus, Edit, Trash2, Search, Upload, Download, Loader2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Input } from '@/components/Input';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { useNotification } from '@/hooks/useNotification';
import { apiClient } from '@/services/apiClient';

const desigSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  slug: z.string().min(2, 'Slug must be at least 2 characters'),
  title: z.string().min(1, 'Title is required'),
  code: z.string().optional(),
  job_level: z.string().optional(),
  grade: z.string().optional(),
  reporting_level: z.coerce.number().min(1, 'Reporting level must be at least 1'),
  description: z.string().optional(),
});

type DesigFormValues = z.infer<typeof desigSchema>;

interface Designation {
  id: string;
  name: string;
  slug: string;
  title: string;
  code: string | null;
  job_level: string | null;
  grade: string | null;
  reporting_level: number;
  description: string | null;
}

export function OrgDesignations() {
  const { addNotification } = useNotification();
  const [designations, setDesignations] = useState<Designation[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedDesig, setSelectedDesig] = useState<Designation | null>(null);

  const {
    register,
    handleSubmit,
    setValue,
    reset,
    formState: { errors },
  } = useForm<any>({
    resolver: zodResolver(desigSchema),
  });

  const fetchDesignations = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get(`/api/v1/designations?search=${search}`);
      setDesignations(res.data.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDesignations();
  }, [search]);

  const onSubmit = async (values: DesigFormValues) => {
    try {
      if (selectedDesig) {
        await apiClient.put(`/api/v1/designations/${selectedDesig.id}`, values);
        addNotification('Designation updated successfully', 'success');
      } else {
        await apiClient.post('/api/v1/designations', values);
        addNotification('Designation created successfully', 'success');
      }
      setModalOpen(false);
      reset();
      setSelectedDesig(null);
      fetchDesignations();
    } catch (err: any) {
      addNotification(err.message || 'Operation failed', 'error');
    }
  };

  const handleEdit = (desig: Designation) => {
    setSelectedDesig(desig);
    setValue('name', desig.name);
    setValue('slug', desig.slug);
    setValue('title', desig.title);
    setValue('code', desig.code || '');
    setValue('job_level', desig.job_level || '');
    setValue('grade', desig.grade || '');
    setValue('reporting_level', desig.reporting_level);
    setValue('description', desig.description || '');
    setModalOpen(true);
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this designation?')) return;
    try {
      await apiClient.delete(`/api/v1/designations/${id}`);
      addNotification('Designation deleted successfully', 'success');
      fetchDesignations();
    } catch (err: any) {
      addNotification(err.message || 'Deletion failed', 'error');
    }
  };

  const handleCsvUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      await apiClient.post('/api/v1/designations/bulk-upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      addNotification('Bulk import completed', 'success');
      fetchDesignations();
    } catch (err: any) {
      addNotification(err.message || 'Bulk upload failed', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Designations & Job Levels</h1>
          <p className="text-sm text-muted-foreground">Define corporate job titles, reporting grades, and hierarchy levels.</p>
        </div>
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-2 px-3 py-2 border border-border rounded bg-secondary/35 text-xs font-semibold cursor-pointer select-none hover:bg-secondary">
            <Upload className="h-4 w-4" />
            Bulk Upload CSV
            <input type="file" accept=".csv" className="hidden" onChange={handleCsvUpload} />
          </label>
          <a
            href="http://localhost:8000/api/v1/designations/export/csv"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2 px-3 py-2 border border-border rounded bg-secondary/35 text-xs font-semibold hover:bg-secondary cursor-pointer select-none"
          >
            <Download className="h-4 w-4" />
            Export CSV
          </a>
          <Button
            onClick={() => {
              setSelectedDesig(null);
              reset({
                name: '',
                slug: '',
                title: '',
                code: '',
                job_level: '',
                grade: '',
                reporting_level: 1,
                description: '',
              });
              setModalOpen(true);
            }}
            variant="primary"
            className="flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            Add Designation
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Designations Directory</CardTitle>
            <CardDescription>Full hierarchy of levels from CEO to entry-level employee.</CardDescription>
          </div>
          <div className="relative w-64">
            <Search className="absolute left-2.5 top-3 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search designations..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 h-10 w-full border border-input rounded-md bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left border-collapse">
                <thead>
                  <tr className="border-b border-border text-muted-foreground text-xs uppercase font-mono">
                    <th className="py-3 px-4">Title</th>
                    <th className="py-3 px-4">Job Level</th>
                    <th className="py-3 px-4">Grade</th>
                    <th className="py-3 px-4 text-center font-mono">Reporting Order</th>
                    <th className="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {designations.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="py-8 text-center text-muted-foreground">
                        No designations found. Seed corporate data to verify.
                      </td>
                    </tr>
                  ) : (
                    designations.map((d) => (
                      <tr key={d.id} className="border-b border-border hover:bg-secondary/10">
                        <td className="py-3.5 px-4 font-semibold">{d.title}</td>
                        <td className="py-3.5 px-4 text-xs">{d.job_level || '-'}</td>
                        <td className="py-3.5 px-4 font-mono text-xs">{d.grade || '-'}</td>
                        <td className="py-3.5 px-4 text-center font-mono font-semibold text-xs">{d.reporting_level}</td>
                        <td className="py-3.5 px-4 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => handleEdit(d)}
                              className="p-1.5 hover:bg-secondary rounded text-muted-foreground hover:text-foreground"
                            >
                              <Edit className="h-4 w-4" />
                            </button>
                            <button
                              onClick={() => handleDelete(d.id)}
                              className="p-1.5 hover:bg-secondary rounded text-red-500 hover:text-red-600"
                            >
                              <Trash2 className="h-4 w-4" />
                            </button>
                          </div>
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

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title={selectedDesig ? 'Edit Designation' : 'Add Designation'}>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Designation Name"
            {...register('name')}
            error={errors.name?.message as string}
          />
          <Input
            label="Slug Identifier"
            {...register('slug')}
            error={errors.slug?.message as string}
          />
          <Input
            label="Official Title"
            {...register('title')}
            error={errors.title?.message as string}
          />
          <div className="grid grid-cols-2 gap-3">
            <Input label="Job Level (e.g. Executive, Lead)" {...register('job_level')} />
            <Input label="Grade (e.g. G1, L3)" {...register('grade')} />
          </div>
          <Input
            label="Reporting Level (1 to 10 scale)"
            type="number"
            {...register('reporting_level')}
            error={errors.reporting_level?.message as string}
          />
          <Input label="Description" {...register('description')} />
          <div className="flex justify-end gap-2 pt-4">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary">
              {selectedDesig ? 'Update' : 'Create'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
export default OrgDesignations;
