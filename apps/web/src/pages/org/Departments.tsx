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

const deptSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  slug: z.string().min(2, 'Slug must be at least 2 characters'),
  code: z.string().optional(),
  budget: z.coerce.number().min(0, 'Budget must be positive'),
  status: z.string().default('active'),
  branch_id: z.string().nullable().optional(),
  parent_department_id: z.string().nullable().optional(),
});

type DeptFormValues = z.infer<typeof deptSchema>;

interface Department {
  id: string;
  name: string;
  slug: string;
  code: string | null;
  budget: number;
  status: string;
  branch_id: string | null;
  parent_department_id: string | null;
}

export function OrgDepartments() {
  const { addNotification } = useNotification();
  const [departments, setDepartments] = useState<Department[]>([]);
  const [branches, setBranches] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedDept, setSelectedDept] = useState<Department | null>(null);

  const {
    register,
    handleSubmit,
    setValue,
    reset,
    formState: { errors },
  } = useForm<any>({
    resolver: zodResolver(deptSchema),
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [deptRes, branchRes] = await Promise.all([
        apiClient.get(`/api/v1/departments?search=${search}`),
        apiClient.get('/api/v1/branches'),
      ]);
      setDepartments(deptRes.data.data || []);
      setBranches(branchRes.data.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [search]);

  const onSubmit = async (values: DeptFormValues) => {
    try {
      const formattedValues = {
        ...values,
        branch_id: values.branch_id || null,
        parent_department_id: values.parent_department_id || null,
      };

      if (selectedDept) {
        await apiClient.put(`/api/v1/departments/${selectedDept.id}`, formattedValues);
        addNotification('Department updated successfully', 'success');
      } else {
        await apiClient.post('/api/v1/departments', formattedValues);
        addNotification('Department created successfully', 'success');
      }
      setModalOpen(false);
      reset();
      setSelectedDept(null);
      fetchData();
    } catch (err: any) {
      addNotification(err.message || 'Operation failed', 'error');
    }
  };

  const handleEdit = (dept: Department) => {
    setSelectedDept(dept);
    setValue('name', dept.name);
    setValue('slug', dept.slug);
    setValue('code', dept.code || '');
    setValue('budget', dept.budget);
    setValue('status', dept.status);
    setValue('branch_id', dept.branch_id || '');
    setValue('parent_department_id', dept.parent_department_id || '');
    setModalOpen(true);
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this department?')) return;
    try {
      await apiClient.delete(`/api/v1/departments/${id}`);
      addNotification('Department deleted successfully', 'success');
      fetchData();
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
      await apiClient.post('/api/v1/departments/bulk-upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      addNotification('Bulk import completed', 'success');
      fetchData();
    } catch (err: any) {
      addNotification(err.message || 'Bulk upload failed', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Department Administration</h1>
          <p className="text-sm text-muted-foreground">Manage departments, define corporate budget limits, and link branch coordinates.</p>
        </div>
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-2 px-3 py-2 border border-border rounded bg-secondary/35 text-xs font-semibold cursor-pointer select-none hover:bg-secondary">
            <Upload className="h-4 w-4" />
            Bulk Upload CSV
            <input type="file" accept=".csv" className="hidden" onChange={handleCsvUpload} />
          </label>
          <a
            href="http://localhost:8000/api/v1/departments/export/csv"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2 px-3 py-2 border border-border rounded bg-secondary/35 text-xs font-semibold hover:bg-secondary cursor-pointer select-none"
          >
            <Download className="h-4 w-4" />
            Export CSV
          </a>
          <Button
            onClick={() => {
              setSelectedDept(null);
              reset({
                name: '',
                slug: '',
                code: '',
                budget: 0,
                status: 'active',
                branch_id: '',
                parent_department_id: '',
              });
              setModalOpen(true);
            }}
            variant="primary"
            className="flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            Add Department
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Departments Directory</CardTitle>
            <CardDescription>All primary engineering, hr, executive, and financial divisions.</CardDescription>
          </div>
          <div className="relative w-64">
            <Search className="absolute left-2.5 top-3 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search departments..."
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
                    <th className="py-3 px-4">Name</th>
                    <th className="py-3 px-4">Code</th>
                    <th className="py-3 px-4 font-mono">Budget Placeholder</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {departments.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="py-8 text-center text-muted-foreground">
                        No departments found. Seed corporate data to verify.
                      </td>
                    </tr>
                  ) : (
                    departments.map((d) => (
                      <tr key={d.id} className="border-b border-border hover:bg-secondary/10">
                        <td className="py-3.5 px-4 font-semibold">{d.name}</td>
                        <td className="py-3.5 px-4 font-mono text-xs">{d.code || '-'}</td>
                        <td className="py-3.5 px-4 font-mono text-xs">${d.budget.toLocaleString()}</td>
                        <td className="py-3.5 px-4 text-xs font-semibold uppercase">
                          <span className={`px-2 py-0.5 rounded ${d.status === 'active' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-red-500/10 text-red-500'}`}>
                            {d.status}
                          </span>
                        </td>
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

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title={selectedDept ? 'Edit Department' : 'Add Department'}>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Department Name"
            {...register('name')}
            error={errors.name?.message as string}
          />
          <Input
            label="Slug Address"
            {...register('slug')}
            error={errors.slug?.message as string}
          />
          <Input
            label="Department Code"
            {...register('code')}
            error={errors.code?.message as string}
          />
          <Input
            label="Budget limit (USD)"
            type="number"
            {...register('budget')}
            error={errors.budget?.message as string}
          />
          <div className="flex flex-col space-y-1.5">
            <label className="text-sm font-medium">Associated Branch</label>
            <select
              {...register('branch_id')}
              className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            >
              <option value="">-- No Branch (Global) --</option>
              {branches.map((b) => (
                <option key={b.id} value={b.id}>{b.name}</option>
              ))}
            </select>
          </div>
          <div className="flex flex-col space-y-1.5">
            <label className="text-sm font-medium">Parent Department</label>
            <select
              {...register('parent_department_id')}
              className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            >
              <option value="">-- None (Root) --</option>
              {departments
                .filter((d) => d.id !== selectedDept?.id)
                .map((d) => (
                  <option key={d.id} value={d.id}>{d.name}</option>
                ))}
            </select>
          </div>
          <div className="flex justify-end gap-2 pt-4">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary">
              {selectedDept ? 'Update' : 'Create'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
export default OrgDepartments;
