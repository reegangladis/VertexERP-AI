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

const buSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  slug: z.string().min(2, 'Slug must be at least 2 characters'),
  code: z.string().optional(),
  description: z.string().optional(),
  status: z.string().default('active'),
});

type BUFormValues = z.infer<typeof buSchema>;

interface BusinessUnit {
  id: string;
  name: string;
  slug: string;
  code: string | null;
  description: string | null;
  status: string;
}

export function OrgBusinessUnits() {
  const { addNotification } = useNotification();
  const [units, setUnits] = useState<BusinessUnit[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedUnit, setSelectedUnit] = useState<BusinessUnit | null>(null);

  const {
    register,
    handleSubmit,
    setValue,
    reset,
    formState: { errors },
  } = useForm<any>({
    resolver: zodResolver(buSchema),
  });

  const fetchUnits = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get(`/api/v1/business-units?search=${search}`);
      setUnits(res.data.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUnits();
  }, [search]);

  const onSubmit = async (values: BUFormValues) => {
    try {
      if (selectedUnit) {
        await apiClient.put(`/api/v1/business-units/${selectedUnit.id}`, values);
        addNotification('Business unit updated successfully', 'success');
      } else {
        await apiClient.post('/api/v1/business-units', values);
        addNotification('Business unit created successfully', 'success');
      }
      setModalOpen(false);
      reset();
      setSelectedUnit(null);
      fetchUnits();
    } catch (err: any) {
      addNotification(err.message || 'Operation failed', 'error');
    }
  };

  const handleEdit = (unit: BusinessUnit) => {
    setSelectedUnit(unit);
    setValue('name', unit.name);
    setValue('slug', unit.slug);
    setValue('code', unit.code || '');
    setValue('description', unit.description || '');
    setValue('status', unit.status);
    setModalOpen(true);
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this business unit?')) return;
    try {
      await apiClient.delete(`/api/v1/business-units/${id}`);
      addNotification('Business unit deleted successfully', 'success');
      fetchUnits();
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
      await apiClient.post('/api/v1/business-units/bulk-upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      addNotification('Bulk import completed', 'success');
      fetchUnits();
    } catch (err: any) {
      addNotification(err.message || 'Bulk upload failed', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Business Units</h1>
          <p className="text-sm text-muted-foreground">Manage strategic enterprise business divisions, operational units, and multi-line structures.</p>
        </div>
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-2 px-3 py-2 border border-border rounded bg-secondary/35 text-xs font-semibold cursor-pointer select-none hover:bg-secondary">
            <Upload className="h-4 w-4" />
            Bulk Upload CSV
            <input type="file" accept=".csv" className="hidden" onChange={handleCsvUpload} />
          </label>
          <a
            href={`${getApiBaseUrl()}/api/v1/business-units/export/csv`}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2 px-3 py-2 border border-border rounded bg-secondary/35 text-xs font-semibold hover:bg-secondary cursor-pointer select-none"
          >
            <Download className="h-4 w-4" />
            Export CSV
          </a>
          <Button
            onClick={() => {
              setSelectedUnit(null);
              reset({
                name: '',
                slug: '',
                code: '',
                description: '',
                status: 'active',
              });
              setModalOpen(true);
            }}
            variant="primary"
            className="flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            Add Business Unit
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Registered Business Units</CardTitle>
            <CardDescription>A list of functional business divisions across the enterprise.</CardDescription>
          </div>
          <div className="relative w-64">
            <Search className="absolute left-2.5 top-3 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search business units..."
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
                    <th className="py-3 px-4">Slug</th>
                    <th className="py-3 px-4">Description</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {units.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="py-8 text-center text-muted-foreground">
                        No business units found. Try seeding enterprise data.
                      </td>
                    </tr>
                  ) : (
                    units.map((u) => (
                      <tr key={u.id} className="border-b border-border hover:bg-secondary/10">
                        <td className="py-3.5 px-4 font-semibold">{u.name}</td>
                        <td className="py-3.5 px-4 font-mono text-xs">{u.code || '-'}</td>
                        <td className="py-3.5 px-4 font-mono text-xs text-muted-foreground">{u.slug}</td>
                        <td className="py-3.5 px-4 text-xs text-muted-foreground max-w-xs truncate">{u.description || '-'}</td>
                        <td className="py-3.5 px-4 text-xs font-semibold uppercase">
                          <span className={`px-2 py-0.5 rounded ${u.status === 'active' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-red-500/10 text-red-500'}`}>
                            {u.status}
                          </span>
                        </td>
                        <td className="py-3.5 px-4 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => handleEdit(u)}
                              className="p-1.5 hover:bg-secondary rounded text-muted-foreground hover:text-foreground"
                            >
                              <Edit className="h-4 w-4" />
                            </button>
                            <button
                              onClick={() => handleDelete(u.id)}
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

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title={selectedUnit ? 'Edit Business Unit' : 'Add Business Unit'}>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Business Unit Name"
            {...register('name')}
            error={errors.name?.message as string}
          />
          <Input
            label="Slug Address"
            {...register('slug')}
            error={errors.slug?.message as string}
          />
          <Input
            label="Business Unit Code"
            {...register('code')}
            error={errors.code?.message as string}
          />
          <Input
            label="Description"
            {...register('description')}
            error={errors.description?.message as string}
          />
          <div className="flex flex-col space-y-1.5">
            <label className="text-sm font-medium">Status</label>
            <select
              {...register('status')}
              className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            >
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
          <div className="flex justify-end gap-2 pt-4">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary">
              {selectedUnit ? 'Update' : 'Create'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
export default OrgBusinessUnits;
