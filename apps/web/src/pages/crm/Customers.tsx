import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link } from 'react-router-dom';
import { Plus, Edit, Trash2, Search, Upload, Download, Loader2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Input } from '@/components/Input';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { useNotification } from '@/hooks/useNotification';
import { apiClient } from '@/services/apiClient';

const customerSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  type: z.string().default('business'),
  industry: z.string().optional().nullable(),
  status: z.string().default('active'),
  tags: z.preprocess((val) => (val ? String(val).split(',') : []), z.array(z.string())),
});

interface Customer {
  id: string;
  name: string;
  type: string;
  industry: string | null;
  status: string;
  tags?: { list?: string[] };
}

export function CRMCustomers() {
  const { addNotification } = useNotification();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedCust, setSelectedCust] = useState<Customer | null>(null);

  const {
    register,
    handleSubmit,
    setValue,
    reset,
    formState: { errors },
  } = useForm<any>({
    resolver: zodResolver(customerSchema),
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get(`/api/v1/crm/customers?search=${search}`);
      setCustomers(res.data.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [search]);

  const onSubmit = async (values: any) => {
    try {
      const payload = {
        ...values,
        tags: values.tags || [],
      };

      if (selectedCust) {
        await apiClient.put(`/api/v1/crm/customers/${selectedCust.id}`, payload);
        addNotification('Customer profile updated successfully', 'success');
      } else {
        await apiClient.post('/api/v1/crm/customers', payload);
        addNotification('Customer profile created successfully', 'success');
      }
      setModalOpen(false);
      reset();
      setSelectedCust(null);
      fetchData();
    } catch (err: any) {
      addNotification(err.message || 'Operation failed', 'error');
    }
  };

  const handleEdit = (cust: Customer) => {
    setSelectedCust(cust);
    setValue('name', cust.name);
    setValue('type', cust.type);
    setValue('industry', cust.industry || '');
    setValue('status', cust.status);
    setValue('tags', cust.tags?.list?.join(',') || '');
    setModalOpen(true);
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this customer?')) return;
    try {
      await apiClient.delete(`/api/v1/crm/customers/${id}`);
      addNotification('Customer account deleted successfully', 'success');
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
      await apiClient.post('/api/v1/crm/customers/bulk-upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      addNotification('Bulk customer CSV import completed', 'success');
      fetchData();
    } catch (err: any) {
      addNotification(err.message || 'Bulk upload failed', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Customer directory</h1>
          <p className="text-sm text-muted-foreground">Manage business accounts, communications log, and status tags.</p>
        </div>
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-2 px-3 py-2 border border-border rounded bg-secondary/35 text-xs font-semibold cursor-pointer select-none hover:bg-secondary">
            <Upload className="h-4 w-4" />
            Bulk Upload CSV
            <input type="file" accept=".csv" className="hidden" onChange={handleCsvUpload} />
          </label>
          <a
            href="http://localhost:8000/api/v1/crm/customers/export/csv"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2 px-3 py-2 border border-border rounded bg-secondary/35 text-xs font-semibold hover:bg-secondary cursor-pointer select-none"
          >
            <Download className="h-4 w-4" />
            Export CSV
          </a>
          <Button
            onClick={() => {
              setSelectedCust(null);
              reset({
                name: '',
                type: 'business',
                industry: '',
                status: 'active',
                tags: '',
              });
              setModalOpen(true);
            }}
            variant="primary"
            className="flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            Add Customer
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Client Registry</CardTitle>
            <CardDescription>Accounts profiles, tag sets, and operational flags.</CardDescription>
          </div>
          <div className="relative w-64">
            <Search className="absolute left-2.5 top-3 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search by client name..."
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
                    <th className="py-3 px-4">Client Name</th>
                    <th className="py-3 px-4">Account Type</th>
                    <th className="py-3 px-4">Industry Sector</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {customers.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="py-8 text-center text-muted-foreground">
                        No customers found. Try seeding data to verify.
                      </td>
                    </tr>
                  ) : (
                    customers.map((c) => (
                      <tr key={c.id} className="border-b border-border hover:bg-secondary/10">
                        <td className="py-3.5 px-4 font-semibold text-primary">
                          <Link to={`/crm/customers/${c.id}`} className="hover:underline">
                            {c.name}
                          </Link>
                        </td>
                        <td className="py-3.5 px-4 text-xs font-mono uppercase text-muted-foreground">{c.type}</td>
                        <td className="py-3.5 px-4 text-xs">{c.industry || 'N/A'}</td>
                        <td className="py-3.5 px-4 text-xs font-semibold uppercase">
                          <span className={`px-2 py-0.5 rounded ${c.status === 'active' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-red-500/10 text-red-500'}`}>
                            {c.status}
                          </span>
                        </td>
                        <td className="py-3.5 px-4 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => handleEdit(c)}
                              className="p-1.5 hover:bg-secondary rounded text-muted-foreground hover:text-foreground"
                            >
                              <Edit className="h-4 w-4" />
                            </button>
                            <button
                              onClick={() => handleDelete(c.id)}
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

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title={selectedCust ? 'Edit Customer Profile' : 'Add Customer'}>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input label="Customer Name" {...register('name')} error={errors.name?.message as string} />
          
          <div className="grid grid-cols-2 gap-3">
            <div className="flex flex-col space-y-1.5">
              <label className="text-sm font-medium">Account Type</label>
              <select
                {...register('type')}
                className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none"
              >
                <option value="business">Business</option>
                <option value="individual">Individual</option>
              </select>
            </div>
            <div className="flex flex-col space-y-1.5">
              <label className="text-sm font-medium">Status</label>
              <select
                {...register('status')}
                className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none"
              >
                <option value="active">Active</option>
                <option value="churned">Churned</option>
              </select>
            </div>
          </div>

          <Input label="Industry Sector" {...register('industry')} />
          <Input label="Tags (comma-separated)" {...register('tags')} placeholder="vip,enterprise,retained" />

          <div className="flex justify-end gap-2 pt-4">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary">
              {selectedCust ? 'Update' : 'Create'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
export default CRMCustomers;
