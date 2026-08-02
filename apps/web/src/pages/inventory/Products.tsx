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

const productSchema = z.object({
  name: z.string().min(2, 'Product Name must be at least 2 characters'),
  sku: z.string().min(3, 'SKU must be at least 3 characters'),
  barcode: z.string().optional().nullable(),
  category_id: z.string().min(1, 'Category is required'),
  unit_id: z.string().min(1, 'Unit of measure is required'),
  brand_id: z.string().optional().nullable(),
  safety_stock: z.preprocess((val) => parseInt(val as string) || 0, z.number().min(0)),
  reorder_level: z.preprocess((val) => parseInt(val as string) || 0, z.number().min(0)),
});

interface Product {
  id: string;
  name: string;
  sku: string;
  barcode: string | null;
  category_id: string;
  unit_id: string;
  brand_id: string | null;
  status: string;
  safety_stock: number;
  reorder_level: number;
}

export function InventoryProducts() {
  const { addNotification } = useNotification();
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [units, setUnits] = useState<any[]>([]);
  const [brands, setBrands] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedProd, setSelectedProd] = useState<Product | null>(null);

  const {
    register,
    handleSubmit,
    setValue,
    reset,
    formState: { errors },
  } = useForm<any>({
    resolver: zodResolver(productSchema),
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [prodRes, catRes, unitRes, brandRes] = await Promise.all([
        apiClient.get(`/api/v1/inventory/products?search=${search}`),
        apiClient.get('/api/v1/inventory/categories'),
        apiClient.get('/api/v1/inventory/products/units'),
        apiClient.get('/api/v1/inventory/products/brands'),
      ]);
      setProducts(prodRes.data.data || []);
      setCategories(catRes.data.data || []);
      setUnits(unitRes.data.data || []);
      setBrands(brandRes.data.data || []);
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
        brand_id: values.brand_id || null,
        barcode: values.barcode || null,
      };

      if (selectedProd) {
        await apiClient.put(`/api/v1/inventory/products/${selectedProd.id}`, payload);
        addNotification('Product updated successfully', 'success');
      } else {
        await apiClient.post('/api/v1/inventory/products', payload);
        addNotification('Product catalog master registered', 'success');
      }
      setModalOpen(false);
      reset();
      setSelectedProd(null);
      fetchData();
    } catch (err: any) {
      addNotification(err.response?.data?.detail || 'Operation failed', 'error');
    }
  };

  const handleEdit = (prod: Product) => {
    setSelectedProd(prod);
    setValue('name', prod.name);
    setValue('sku', prod.sku);
    setValue('barcode', prod.barcode || '');
    setValue('category_id', prod.category_id);
    setValue('unit_id', prod.unit_id);
    setValue('brand_id', prod.brand_id || '');
    setValue('safety_stock', prod.safety_stock);
    setValue('reorder_level', prod.reorder_level);
    setModalOpen(true);
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this product?')) return;
    try {
      await apiClient.delete(`/api/v1/inventory/products/${id}`);
      addNotification('Product removed from catalog', 'success');
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
      await apiClient.post('/api/v1/inventory/products/bulk-upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      addNotification('Bulk product catalog CSV import completed', 'success');
      fetchData();
    } catch (err: any) {
      addNotification(err.message || 'Bulk upload failed', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Product Master Catalog</h1>
          <p className="text-sm text-muted-foreground">Manage SKUs registry, assign safety thresholds, and print barcode labels.</p>
        </div>
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-2 px-3 py-2 border border-border rounded bg-secondary/35 text-xs font-semibold cursor-pointer select-none hover:bg-secondary">
            <Upload className="h-4 w-4" />
            Bulk Upload CSV
            <input type="file" accept=".csv" className="hidden" onChange={handleCsvUpload} />
          </label>
          <a
            href={`${getApiBaseUrl()}/api/v1/inventory/products/export/csv`}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2 px-3 py-2 border border-border rounded bg-secondary/35 text-xs font-semibold hover:bg-secondary cursor-pointer select-none"
          >
            <Download className="h-4 w-4" />
            Export CSV
          </a>
          <Button
            onClick={() => {
              setSelectedProd(null);
              reset({
                name: '',
                sku: '',
                barcode: '',
                category_id: categories[0]?.id || '',
                unit_id: units[0]?.id || '',
                brand_id: '',
                safety_stock: 0,
                reorder_level: 0,
              });
              setModalOpen(true);
            }}
            variant="primary"
            className="flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            Add Product
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>SKU Catalog</CardTitle>
            <CardDescription>Product safety stock metrics, unique SKU keys, and barcodes.</CardDescription>
          </div>
          <div className="relative w-64">
            <Search className="absolute left-2.5 top-3 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search by SKU, name, or barcode..."
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
                    <th className="py-3 px-4">Product Name</th>
                    <th className="py-3 px-4">SKU Code</th>
                    <th className="py-3 px-4">Barcode</th>
                    <th className="py-3 px-4 text-right">Safety Stock</th>
                    <th className="py-3 px-4 text-right">Reorder Point</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {products.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="py-8 text-center text-muted-foreground">
                        No products cataloged. Try seeding structures to test.
                      </td>
                    </tr>
                  ) : (
                    products.map((p) => (
                      <tr key={p.id} className="border-b border-border hover:bg-secondary/10">
                        <td className="py-3.5 px-4 font-semibold text-primary">{p.name}</td>
                        <td className="py-3.5 px-4 text-xs font-mono uppercase text-muted-foreground">{p.sku}</td>
                        <td className="py-3.5 px-4 text-xs font-mono">{p.barcode || 'N/A'}</td>
                        <td className="py-3.5 px-4 text-right font-mono font-semibold">{p.safety_stock}</td>
                        <td className="py-3.5 px-4 text-right font-mono font-semibold text-amber-500">{p.reorder_level}</td>
                        <td className="py-3.5 px-4 text-xs font-semibold uppercase">
                          <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-500">
                            {p.status}
                          </span>
                        </td>
                        <td className="py-3.5 px-4 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => handleEdit(p)}
                              className="p-1.5 hover:bg-secondary rounded text-muted-foreground hover:text-foreground"
                            >
                              <Edit className="h-4 w-4" />
                            </button>
                            <button
                              onClick={() => handleDelete(p.id)}
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

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title={selectedProd ? 'Edit SKU Specifications' : 'Add Product'}>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input label="Product Name" {...register('name')} error={errors.name?.message as string} />
          <Input label="SKU Code" {...register('sku')} error={errors.sku?.message as string} disabled={!!selectedProd} />
          <Input label="Barcode" {...register('barcode')} />

          <div className="grid grid-cols-2 gap-3">
            <div className="flex flex-col space-y-1.5">
              <label className="text-sm font-medium">Category</label>
              <select
                {...register('category_id')}
                className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none"
              >
                <option value="">-- Select Category --</option>
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>
            <div className="flex flex-col space-y-1.5">
              <label className="text-sm font-medium">Unit of Measure</label>
              <select
                {...register('unit_id')}
                className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none"
              >
                <option value="">-- Select Unit --</option>
                {units.map((u) => (
                  <option key={u.id} value={u.id}>{u.name} ({u.code})</option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex flex-col space-y-1.5">
            <label className="text-sm font-medium">Brand Partner</label>
            <select
              {...register('brand_id')}
              className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none"
            >
              <option value="">None</option>
              {brands.map((b) => (
                <option key={b.id} value={b.id}>{b.name}</option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Input label="Safety Stock" type="number" {...register('safety_stock')} error={errors.safety_stock?.message as string} />
            <Input label="Reorder Level" type="number" {...register('reorder_level')} error={errors.reorder_level?.message as string} />
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary">
              {selectedProd ? 'Update Specifications' : 'Catalog SKU'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
export default InventoryProducts;
