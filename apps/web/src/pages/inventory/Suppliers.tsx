import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Plus, Edit, Search, Upload, Download, Loader2, Star } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Input } from '@/components/Input';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { useNotification } from '@/hooks/useNotification';
import { apiClient, getApiBaseUrl } from '@/services/apiClient';

const supplierSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  code: z.string().min(2, 'Code must be at least 2 characters'),
  gst_vat: z.string().optional().nullable(),
  payment_terms: z.string().default('Net 30'),
});

interface Supplier {
  id: string;
  name: string;
  code: string;
  gst_vat: string | null;
  payment_terms: string | null;
  rating: number | null;
}

export function InventorySuppliers() {
  const { addNotification } = useNotification();
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [modalOpen, setModalOpen] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<any>({
    resolver: zodResolver(supplierSchema),
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get(`/api/v1/inventory/suppliers?search=${search}`);
      setSuppliers(res.data.data || []);
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
      await apiClient.post('/api/v1/inventory/suppliers', values);
      addNotification('Supplier profile created successfully', 'success');
      setModalOpen(false);
      reset();
      fetchData();
    } catch (err: any) {
      addNotification(err.response?.data?.detail || 'Operation failed', 'error');
    }
  };

  const handleCsvUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      await apiClient.post('/api/v1/inventory/suppliers/bulk-upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      addNotification('Bulk supplier CSV import completed', 'success');
      fetchData();
    } catch (err: any) {
      addNotification(err.message || 'Bulk upload failed', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Suppliers Directory</h1>
          <p className="text-sm text-muted-foreground">Manage vendor profiles, verify GST/VAT details, and audit procurement lead-times.</p>
        </div>
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-2 px-3 py-2 border border-border rounded bg-secondary/35 text-xs font-semibold cursor-pointer select-none hover:bg-secondary">
            <Upload className="h-4 w-4" />
            Bulk Upload CSV
            <input type="file" accept=".csv" className="hidden" onChange={handleCsvUpload} />
          </label>
          <a
            href={`${getApiBaseUrl()}/api/v1/inventory/suppliers/export/csv`}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2 px-3 py-2 border border-border rounded bg-secondary/35 text-xs font-semibold hover:bg-secondary cursor-pointer select-none"
          >
            <Download className="h-4 w-4" />
            Export CSV
          </a>
          <Button
            onClick={() => {
              reset({
                name: '',
                code: '',
                gst_vat: '',
                payment_terms: 'Net 30',
              });
              setModalOpen(true);
            }}
            variant="primary"
            className="flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            Add Supplier
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Partner Vendors</CardTitle>
            <CardDescription>Suppliers ratings, VAT registrations, and billing terms.</CardDescription>
          </div>
          <div className="relative w-64">
            <Search className="absolute left-2.5 top-3 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search by name or code..."
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
                    <th className="py-3 px-4">Supplier Name</th>
                    <th className="py-3 px-4">Supplier Code</th>
                    <th className="py-3 px-4">GST/VAT</th>
                    <th className="py-3 px-4">Payment Terms</th>
                    <th className="py-3 px-4 text-right">Rating Score</th>
                  </tr>
                </thead>
                <tbody>
                  {suppliers.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="py-8 text-center text-muted-foreground">
                        No suppliers registered. Try seeding data.
                      </td>
                    </tr>
                  ) : (
                    suppliers.map((s) => (
                      <tr key={s.id} className="border-b border-border hover:bg-secondary/10">
                        <td className="py-3.5 px-4 font-semibold text-foreground">{s.name}</td>
                        <td className="py-3.5 px-4 text-xs font-mono uppercase text-muted-foreground">{s.code}</td>
                        <td className="py-3.5 px-4 text-xs font-mono">{s.gst_vat || 'N/A'}</td>
                        <td className="py-3.5 px-4 text-xs font-mono">{s.payment_terms || 'Net 30'}</td>
                        <td className="py-3.5 px-4 text-right">
                          <div className="flex items-center justify-end gap-1 font-mono font-bold text-amber-500">
                            <Star className="h-3.5 w-3.5 fill-amber-500 text-amber-500" />
                            <span>{s.rating || '5.0'}</span>
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

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title="Register Supplier Partner">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input label="Supplier Name" {...register('name')} error={errors.name?.message as string} />
          <Input label="Supplier Code" {...register('code')} error={errors.code?.message as string} placeholder="ACM-IND, SUP-001" />
          <Input label="GST/VAT ID" {...register('gst_vat')} />
          <Input label="Payment Terms" {...register('payment_terms')} placeholder="Net 30, Net 60, COD" />

          <div className="flex justify-end gap-2 pt-4">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary">Create Profile</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
export default InventorySuppliers;
