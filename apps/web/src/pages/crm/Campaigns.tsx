import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Play, Plus, Loader2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { Input } from '@/components/Input';
import { useNotification } from '@/hooks/useNotification';
import { apiClient } from '@/services/apiClient';

const campaignSchema = z.object({
  name: z.string().min(3, 'Campaign Name must be at least 3 characters'),
  type: z.string().default('email'),
  start_date: z.string().min(1, 'Start date is required'),
  end_date: z.string().min(1, 'End date is required'),
  budget: z.preprocess((val) => parseFloat(val as string) || 0, z.number().min(0)),
  expected_revenue: z.preprocess((val) => parseFloat(val as string) || 0, z.number().min(0)),
});

interface Campaign {
  id: string;
  name: string;
  type: string;
  status: string;
  start_date: string;
  end_date: string;
  budget: number;
  expected_revenue: number;
}

export function CRMCampaigns() {
  const { addNotification } = useNotification();
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<any>({
    resolver: zodResolver(campaignSchema),
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/api/v1/crm/campaigns');
      setCampaigns(res.data.data || []);
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
      await apiClient.post('/api/v1/crm/campaigns', values);
      addNotification('Marketing campaign launched successfully', 'success');
      setModalOpen(false);
      reset();
      fetchData();
    } catch (err: any) {
      addNotification(err.response?.data?.detail || 'Campaign creation failed', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Marketing Campaigns</h1>
          <p className="text-sm text-muted-foreground">Monitor performance, audit budgets, and map outreach channels.</p>
        </div>
        <Button onClick={() => setModalOpen(true)} variant="primary" className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Launch Campaign
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Outreach Performance</CardTitle>
          <CardDescription>Email, SMS, and social media campaign trackers.</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center py-6">
              <Loader2 className="h-6 w-6 animate-spin text-primary" />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left border-collapse">
                <thead>
                  <tr className="border-b border-border text-muted-foreground text-xs uppercase font-mono">
                    <th className="py-2.5 px-3">Campaign Name</th>
                    <th className="py-2.5 px-3">Outreach Type</th>
                    <th className="py-2.5 px-3 text-right">Budget Limit</th>
                    <th className="py-2.5 px-3 text-right">Target Revenue</th>
                    <th className="py-2.5 px-3 text-right">Period Range</th>
                    <th className="py-2.5 px-3">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {campaigns.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="py-6 text-center text-muted-foreground text-xs">No outreach campaigns active.</td>
                    </tr>
                  ) : (
                    campaigns.map((c) => (
                      <tr key={c.id} className="border-b border-border hover:bg-secondary/10 text-xs">
                        <td className="py-3 px-3 font-semibold text-foreground">{c.name}</td>
                        <td className="py-3 px-3 uppercase font-mono text-[10px]">{c.type}</td>
                        <td className="py-3 px-3 text-right font-mono font-semibold">${c.budget}</td>
                        <td className="py-3 px-3 text-right font-mono font-semibold text-emerald-500">${c.expected_revenue}</td>
                        <td className="py-3 px-3 text-right font-mono text-muted-foreground">{c.start_date} to {c.end_date}</td>
                        <td className="py-3 px-3 uppercase font-semibold">
                          <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-500/10 text-emerald-500">
                            {c.status}
                          </span>
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

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title="Launch Marketing Campaign">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input label="Campaign Name" {...register('name')} error={errors.name?.message as string} />
          
          <div className="flex flex-col space-y-1.5">
            <label className="text-sm font-medium">Channel Type</label>
            <select
              {...register('type')}
              className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none"
            >
              <option value="email">Email Blast</option>
              <option value="sms">SMS Broadcaster</option>
              <option value="social">Social Media Ads</option>
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Input label="Start Date" type="date" {...register('start_date')} error={errors.start_date?.message as string} />
            <Input label="End Date" type="date" {...register('end_date')} error={errors.end_date?.message as string} />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Input label="Outreach Budget ($)" type="number" {...register('budget')} error={errors.budget?.message as string} />
            <Input label="Expected Returns ($)" type="number" {...register('expected_revenue')} error={errors.expected_revenue?.message as string} />
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary">Launch Outreach</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
export default CRMCampaigns;
