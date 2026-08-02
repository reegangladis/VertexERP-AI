import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Plus, FolderOpen, Loader2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Input } from '@/components/Input';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { useNotification } from '@/hooks/useNotification';
import { apiClient } from '@/services/apiClient';

const categorySchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  code: z.string().min(2, 'Code must be at least 2 characters'),
  description: z.string().optional(),
});

interface Category {
  id: string;
  name: string;
  code: string;
  description: string | null;
}

export function InventoryCategories() {
  const { addNotification } = useNotification();
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<any>({
    resolver: zodResolver(categorySchema),
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/api/v1/inventory/categories');
      setCategories(res.data.data || []);
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
      await apiClient.post('/api/v1/inventory/categories', values);
      addNotification('Product Category registered successfully', 'success');
      setModalOpen(false);
      reset();
      fetchData();
    } catch (err: any) {
      addNotification(err.response?.data?.detail || 'Setup failed', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Product Categories Hierarchy</h1>
          <p className="text-sm text-muted-foreground">Classify inventory products under parent-child classification divisions.</p>
        </div>
        <Button onClick={() => setModalOpen(true)} variant="primary" className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Add Category
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Catalog Divisions</CardTitle>
          <CardDescription>Product category classifications codes and description keys.</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center py-6">
              <Loader2 className="h-6 w-6 animate-spin text-primary" />
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {categories.length === 0 ? (
                <p className="text-xs text-muted-foreground italic col-span-3 text-center py-4">No categories configured. Try seeding data.</p>
              ) : (
                categories.map((cat) => (
                  <div key={cat.id} className="p-4 border border-border rounded bg-secondary/10 flex gap-3 items-start">
                    <FolderOpen className="h-5 w-5 text-primary shrink-0 mt-0.5" />
                    <div>
                      <h4 className="font-semibold text-xs text-foreground">{cat.name}</h4>
                      <p className="text-[10px] font-mono text-muted-foreground uppercase">{cat.code}</p>
                      <p className="text-[10px] text-muted-foreground/80 pt-1.5">{cat.description || 'No description logged'}</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </CardContent>
      </Card>

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title="Add Product Category">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input label="Category Name" {...register('name')} error={errors.name?.message as string} />
          <Input label="Category Code" {...register('code')} error={errors.code?.message as string} placeholder="ELEC, MECH, APPL" />
          <Input label="Description" {...register('description')} />

          <div className="flex justify-end gap-2 pt-4">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary">Create Category</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
export default InventoryCategories;
