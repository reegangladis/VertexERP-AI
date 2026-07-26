import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Plus, Check, X, Award, AlertTriangle, Loader2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { Input } from '@/components/Input';
import { useNotification } from '@/hooks/useNotification';
import { apiClient } from '@/services/apiClient';

const dealSchema = z.object({
  customer_id: z.string().min(1, 'Customer account is required'),
  title: z.string().min(3, 'Deal title must be at least 3 characters'),
  amount: z.preprocess((val) => parseFloat(val as string) || 0, z.number().min(1, 'Amount must be greater than 0')),
  probability: z.preprocess((val) => parseInt(val as string) || 10, z.number().min(0).max(100)),
});

interface Deal {
  id: string;
  customer_id: string;
  title: string;
  amount: number;
  probability: number;
  status: string;
  won_lost_reason: string | null;
}

export function CRMDeals() {
  const { addNotification } = useNotification();
  const [deals, setDeals] = useState<Deal[]>([]);
  const [customers, setCustomers] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [resultModalOpen, setResultModalOpen] = useState(false);
  const [activeDealId, setActiveDealId] = useState('');
  const [dealResultStatus, setDealResultStatus] = useState<'won' | 'lost'>('won');
  const [resultReason, setResultReason] = useState('');

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<any>({
    resolver: zodResolver(dealSchema),
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [dealsRes, custRes] = await Promise.all([
        apiClient.get('/api/v1/crm/deals'),
        apiClient.get('/api/v1/crm/customers'),
      ]);
      setDeals(dealsRes.data.data || []);
      setCustomers(custRes.data.data || []);
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
      await apiClient.post('/api/v1/crm/deals', values);
      addNotification('Deal added to pipeline successfully', 'success');
      setModalOpen(false);
      reset();
      fetchData();
    } catch (err: any) {
      addNotification(err.response?.data?.detail || 'Deal creation failed', 'error');
    }
  };

  const handleProcessResult = async () => {
    try {
      await apiClient.put(`/api/v1/crm/deals/${activeDealId}/result`, {
        status: dealResultStatus,
        won_lost_reason: resultReason,
      });
      addNotification(`Deal updated to ${dealResultStatus}`, 'success');
      setResultModalOpen(false);
      setResultReason('');
      fetchData();
    } catch (err: any) {
      addNotification(err.response?.data?.detail || 'Update failed', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Deals Ledger</h1>
          <p className="text-sm text-muted-foreground">Log new contracts, estimate potential values, and track probabilities.</p>
        </div>
        <Button onClick={() => setModalOpen(true)} variant="primary" className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Setup Deal
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Pipeline Deals</CardTitle>
          <CardDescription>Estimated revenue ledger and current close probabilities.</CardDescription>
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
                    <th className="py-2.5 px-3">Deal Title</th>
                    <th className="py-2.5 px-3">Client Account</th>
                    <th className="py-2.5 px-3 text-right">Value Amount</th>
                    <th className="py-2.5 px-3 text-right">Probability</th>
                    <th className="py-2.5 px-3">Status</th>
                    <th className="py-2.5 px-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {deals.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="py-6 text-center text-muted-foreground text-xs">No active pipeline deals logged.</td>
                    </tr>
                  ) : (
                    deals.map((d) => (
                      <tr key={d.id} className="border-b border-border hover:bg-secondary/10 text-xs">
                        <td className="py-3 px-3 font-semibold text-foreground">{d.title}</td>
                        <td className="py-3 px-3 font-mono">Customer {d.customer_id.slice(0, 8)}...</td>
                        <td className="py-3 px-3 text-right font-mono font-semibold text-emerald-500">${d.amount}</td>
                        <td className="py-3 px-3 text-right font-mono text-muted-foreground">{d.probability}%</td>
                        <td className="py-3 px-3 uppercase font-semibold">
                          <span className={`px-2 py-0.5 rounded text-[10px] ${
                            d.status === 'won' ? 'bg-emerald-500/10 text-emerald-500' :
                            d.status === 'lost' ? 'bg-red-500/10 text-red-500' : 'bg-primary/10 text-primary'
                          }`}>
                            {d.status}
                          </span>
                        </td>
                        <td className="py-3 px-3 text-right">
                          {d.status === 'pipeline' && (
                            <div className="flex items-center justify-end gap-1.5">
                              <button
                                onClick={() => {
                                  setActiveDealId(d.id);
                                  setDealResultStatus('won');
                                  setResultModalOpen(true);
                                }}
                                className="p-1 hover:bg-emerald-500/10 text-emerald-500 rounded border border-emerald-500/20"
                                title="Mark Won"
                              >
                                <Check className="h-3.5 w-3.5" />
                              </button>
                              <button
                                onClick={() => {
                                  setActiveDealId(d.id);
                                  setDealResultStatus('lost');
                                  setResultModalOpen(true);
                                }}
                                className="p-1 hover:bg-red-500/10 text-red-500 rounded border border-red-500/20"
                                title="Mark Lost"
                              >
                                <X className="h-3.5 w-3.5" />
                              </button>
                            </div>
                          )}
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

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title="Setup Deal Contract">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="flex flex-col space-y-1.5">
            <label className="text-sm font-medium">Customer Account</label>
            <select
              {...register('customer_id')}
              className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none"
            >
              <option value="">-- Select Customer --</option>
              {customers.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
            {errors.customer_id && <p className="text-xs text-red-500">{errors.customer_id.message as string}</p>}
          </div>

          <Input label="Deal Title" {...register('title')} error={errors.title?.message as string} />
          <Input label="Estimated Amount ($)" type="number" {...register('amount')} error={errors.amount?.message as string} />
          <Input label="Probability (%)" type="number" {...register('probability')} error={errors.probability?.message as string} />

          <div className="flex justify-end gap-2 pt-4">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary">Create Deal</Button>
          </div>
        </form>
      </Modal>

      <Modal isOpen={resultModalOpen} onClose={() => setResultModalOpen(false)} title={`Close Deal as ${dealResultStatus === 'won' ? 'Won' : 'Lost'}`}>
        <div className="space-y-4">
          <Input
            label={dealResultStatus === 'won' ? 'Won Reason' : 'Lost Reason'}
            value={resultReason}
            onChange={(e) => setResultReason(e.target.value)}
            placeholder={dealResultStatus === 'won' ? 'Why was this deal won?' : 'Why was this deal lost?'}
          />
          <div className="flex justify-end gap-2 pt-4">
            <Button variant="secondary" onClick={() => setResultModalOpen(false)}>Cancel</Button>
            <Button onClick={handleProcessResult} variant="primary">Submit Status</Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
export default CRMDeals;
