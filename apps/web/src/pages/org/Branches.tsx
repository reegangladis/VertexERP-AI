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
import { apiClient, getApiBaseUrl } from '@/services/apiClient';

const branchSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  slug: z.string().min(2, 'Slug must be at least 2 characters'),
  code: z.string().optional(),
  timezone: z.string().default('UTC'),
  city: z.string().optional(),
  country: z.string().optional(),
  parent_branch_id: z.string().nullable().optional(),
});

type BranchFormValues = z.infer<typeof branchSchema>;

interface Branch {
  id: string;
  name: string;
  slug: string;
  code: string | null;
  timezone: string;
  city: string | null;
  country: string | null;
  parent_branch_id: string | null;
}

export function OrgBranches() {
  const { addNotification } = useNotification();
  const [branches, setBranches] = useState<Branch[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedBranch, setSelectedBranch] = useState<Branch | null>(null);

  const {
    register,
    handleSubmit,
    setValue,
    reset,
    formState: { errors },
  } = useForm<any>({
    resolver: zodResolver(branchSchema),
  });

  const fetchBranches = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get(`/api/v1/branches?search=${search}`);
      setBranches(res.data.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBranches();
  }, [search]);

  const onSubmit = async (values: BranchFormValues) => {
    try {
      if (selectedBranch) {
        await apiClient.put(`/api/v1/branches/${selectedBranch.id}`, values);
        addNotification('Branch updated successfully', 'success');
      } else {
        await apiClient.post('/api/v1/branches', values);
        addNotification('Branch created successfully', 'success');
      }
      setModalOpen(false);
      reset();
      setSelectedBranch(null);
      fetchBranches();
    } catch (err: any) {
      addNotification(err.message || 'Operation failed', 'error');
    }
  };

  const handleEdit = (branch: Branch) => {
    setSelectedBranch(branch);
    setValue('name', branch.name);
    setValue('slug', branch.slug);
    setValue('code', branch.code || '');
    setValue('timezone', branch.timezone);
    setValue('city', branch.city || '');
    setValue('country', branch.country || '');
    setValue('parent_branch_id', branch.parent_branch_id);
    setModalOpen(true);
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this branch?')) return;
    try {
      await apiClient.delete(`/api/v1/branches/${id}`);
      addNotification('Branch deleted successfully', 'success');
      fetchBranches();
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
      await apiClient.post('/api/v1/branches/bulk-upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      addNotification('Bulk import completed', 'success');
      fetchBranches();
    } catch (err: any) {
      addNotification(err.message || 'Bulk upload failed', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Branch Registry</h1>
          <p className="text-sm text-muted-foreground">Manage organizational subdivisions, working timezones, and geographic registry coordinates.</p>
        </div>
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-2 px-3 py-2 border border-border rounded bg-secondary/35 text-xs cursor-pointer select-none font-semibold hover:bg-secondary">
            <Upload className="h-4 w-4" />
            Bulk Upload CSV
            <input type="file" accept=".csv" className="hidden" onChange={handleCsvUpload} />
          </label>
          <a
            href={`${getApiBaseUrl()}/api/v1/branches/export/csv`}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2 px-3 py-2 border border-border rounded bg-secondary/35 text-xs font-semibold hover:bg-secondary cursor-pointer select-none"
          >
            <Download className="h-4 w-4" />
            Export CSV
          </a>
          <Button
            onClick={() => {
              setSelectedBranch(null);
              reset({
                name: '',
                slug: '',
                code: '',
                timezone: 'UTC',
                city: '',
                country: '',
                parent_branch_id: null,
              });
              setModalOpen(true);
            }}
            variant="primary"
            className="flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            Add Branch
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Registered Branches</CardTitle>
            <CardDescription>A list of offices, satellite branches, and logistics centers.</CardDescription>
          </div>
          <div className="relative w-64">
            <Search className="absolute left-2.5 top-3 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search branches..."
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
                    <th className="py-3 px-4">Timezone</th>
                    <th className="py-3 px-4">Location</th>
                    <th className="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {branches.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="py-8 text-center text-muted-foreground">
                        No branches found. Try seeding data.
                      </td>
                    </tr>
                  ) : (
                    branches.map((b) => (
                      <tr key={b.id} className="border-b border-border hover:bg-secondary/10">
                        <td className="py-3.5 px-4 font-semibold">{b.name}</td>
                        <td className="py-3.5 px-4 font-mono text-xs">{b.code || '-'}</td>
                        <td className="py-3.5 px-4 text-xs font-mono">{b.timezone}</td>
                        <td className="py-3.5 px-4 text-muted-foreground">
                          {b.city ? `${b.city}, ${b.country || ''}` : '-'}
                        </td>
                        <td className="py-3.5 px-4 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => handleEdit(b)}
                              className="p-1.5 hover:bg-secondary rounded text-muted-foreground hover:text-foreground"
                            >
                              <Edit className="h-4 w-4" />
                            </button>
                            <button
                              onClick={() => handleDelete(b.id)}
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

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title={selectedBranch ? 'Edit Branch' : 'Add Branch'}>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Branch Name"
            {...register('name')}
            error={errors.name?.message as string}
          />
          <Input
            label="Slug Address"
            {...register('slug')}
            error={errors.slug?.message as string}
          />
          <Input
            label="Branch Code"
            {...register('code')}
            error={errors.code?.message as string}
          />
          <Input
            label="Timezone ID"
            {...register('timezone')}
            error={errors.timezone?.message as string}
          />
          <div className="grid grid-cols-2 gap-3">
            <Input label="City" {...register('city')} />
            <Input label="Country" {...register('country')} />
          </div>
          <div className="flex justify-end gap-2 pt-4">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary">
              {selectedBranch ? 'Update' : 'Create'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
export default OrgBranches;
