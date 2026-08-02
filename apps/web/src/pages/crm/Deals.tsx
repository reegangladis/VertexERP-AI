import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Plus, Check, X, FileText, ShoppingCart, Loader2, ArrowRight } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { Input } from '@/components/Input';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/Table';
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
  const [quotations, setQuotations] = useState<any[]>([]);
  const [salesOrders, setSalesOrders] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [resultModalOpen, setResultModalOpen] = useState(false);
  const [quoteModalOpen, setQuoteModalOpen] = useState(false);
  const [activeDeal, setActiveDeal] = useState<Deal | null>(null);
  const [dealResultStatus, setDealResultStatus] = useState<'won' | 'lost'>('won');
  const [resultReason, setResultReason] = useState('');
  const [quoteAmount, setQuoteAmount] = useState<number>(0);
  const [quoteTerms, setQuoteTerms] = useState<string>('Net 30 days. Includes standard support.');
  const [quoteValidUntil, setQuoteValidUntil] = useState<string>(new Date(Date.now() + 30 * 86400000).toISOString().split('T')[0]);

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
      const [dealsRes, custRes, quotesRes, ordersRes] = await Promise.all([
        apiClient.get('/api/v1/crm/deals'),
        apiClient.get('/api/v1/crm/customers'),
        apiClient.get('/api/v1/crm/deals/quotations'),
        apiClient.get('/api/v1/crm/deals/sales-orders'),
      ]);
      setDeals(dealsRes.data.data || []);
      setCustomers(custRes.data.data || []);
      setQuotations(quotesRes.data.data || []);
      setSalesOrders(ordersRes.data.data || []);
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
    if (!activeDeal) return;
    try {
      await apiClient.put(`/api/v1/crm/deals/${activeDeal.id}/result`, {
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

  const handleCreateQuotation = async () => {
    if (!activeDeal) return;
    try {
      await apiClient.post('/api/v1/crm/deals/quotations', {
        deal_id: activeDeal.id,
        total_amount: quoteAmount || activeDeal.amount,
        terms: quoteTerms,
        valid_until: quoteValidUntil,
      });
      addNotification('Formal Quotation generated successfully', 'success');
      setQuoteModalOpen(false);
      fetchData();
    } catch (err: any) {
      addNotification(err.response?.data?.detail || 'Quotation creation failed', 'error');
    }
  };

  const handleConvertToOrder = async (quotationId: string) => {
    try {
      await apiClient.post(`/api/v1/crm/deals/quotations/${quotationId}/convert-to-order`);
      addNotification('Quotation converted to Sales Order successfully!', 'success');
      fetchData();
    } catch (err: any) {
      addNotification(err.response?.data?.detail || 'Conversion failed', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Deals & Sales Orders Ledger</h1>
          <p className="text-sm text-muted-foreground">Manage deal pipelines, generate formal quotations, and convert approved quotes to Sales Orders.</p>
        </div>
        <Button onClick={() => setModalOpen(true)} variant="primary" className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Setup Deal
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Pipeline Deals & Quotations</CardTitle>
            <CardDescription>Active sales pipeline, probabilities, and quotation status.</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex justify-center py-6">
                <Loader2 className="h-6 w-6 animate-spin text-primary" />
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Deal Title</TableHead>
                    <TableHead>Client Account</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead>Prob.</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {deals.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={6} className="text-center text-xs text-muted-foreground py-6">
                        No active pipeline deals logged.
                      </TableCell>
                    </TableRow>
                  ) : (
                    deals.map((d) => {
                      const cust = customers.find(c => c.id === d.customer_id);
                      return (
                        <TableRow key={d.id}>
                          <TableCell className="font-semibold text-xs">{d.title}</TableCell>
                          <TableCell className="font-mono text-xs">{cust ? cust.name : d.customer_id.slice(0, 8)}</TableCell>
                          <TableCell className="font-mono text-xs font-semibold text-emerald-500">${d.amount}</TableCell>
                          <TableCell className="font-mono text-xs text-muted-foreground">{d.probability}%</TableCell>
                          <TableCell className="uppercase text-[10px] font-bold">
                            <span className={`px-2 py-0.5 rounded ${
                              d.status === 'won' ? 'bg-emerald-500/10 text-emerald-500' :
                              d.status === 'lost' ? 'bg-red-500/10 text-red-500' : 'bg-primary/10 text-primary'
                            }`}>
                              {d.status}
                            </span>
                          </TableCell>
                          <TableCell className="text-right">
                            <div className="flex items-center justify-end gap-1.5">
                              {d.status === 'pipeline' && (
                                <>
                                  <Button
                                    size="sm"
                                    variant="secondary"
                                    onClick={() => {
                                      setActiveDeal(d);
                                      setQuoteAmount(d.amount);
                                      setQuoteModalOpen(true);
                                    }}
                                    className="text-[10px] h-7 px-2 flex items-center gap-1"
                                  >
                                    <FileText className="h-3 w-3" /> Quote
                                  </Button>
                                  <button
                                    onClick={() => {
                                      setActiveDeal(d);
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
                                      setActiveDeal(d);
                                      setDealResultStatus('lost');
                                      setResultModalOpen(true);
                                    }}
                                    className="p-1 hover:bg-red-500/10 text-red-500 rounded border border-red-500/20"
                                    title="Mark Lost"
                                  >
                                    <X className="h-3.5 w-3.5" />
                                  </button>
                                </>
                              )}
                            </div>
                          </TableCell>
                        </TableRow>
                      );
                    })
                  )}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        {/* Quotations & Sales Orders Ledger */}
        <Card className="md:col-span-1 space-y-4">
          <CardHeader>
            <CardTitle>Quotations & Sales Orders</CardTitle>
            <CardDescription>Convert quotes directly to Sales Orders.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h4 className="text-xs font-bold uppercase font-mono text-muted-foreground mb-2">Quotations ({quotations.length})</h4>
              {quotations.length === 0 ? (
                <p className="text-xs text-muted-foreground italic">No quotations issued yet.</p>
              ) : (
                <div className="space-y-2">
                  {quotations.map((q) => (
                    <div key={q.id} className="p-3 border border-border rounded-xl bg-secondary/15 flex justify-between items-center text-xs">
                      <div>
                        <p className="font-semibold text-primary font-mono">${q.total_amount || 0}</p>
                        <span className={`text-[10px] uppercase font-bold px-1.5 py-0.5 rounded ${
                          q.status === 'approved' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-amber-500/10 text-amber-500'
                        }`}>
                          {q.status}
                        </span>
                      </div>
                      {q.status !== 'approved' && (
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() => handleConvertToOrder(q.id)}
                          className="text-[10px] h-7 px-2 flex items-center gap-1 bg-emerald-600/10 text-emerald-500 hover:bg-emerald-600/20"
                        >
                          <ShoppingCart className="h-3 w-3" /> Order <ArrowRight className="h-3 w-3" />
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="border-t border-border pt-3">
              <h4 className="text-xs font-bold uppercase font-mono text-muted-foreground mb-2">Confirmed Sales Orders ({salesOrders.length})</h4>
              {salesOrders.length === 0 ? (
                <p className="text-xs text-muted-foreground italic">No sales orders created yet.</p>
              ) : (
                <div className="space-y-2">
                  {salesOrders.map((so) => (
                    <div key={so.id} className="p-3 border border-border rounded-xl bg-emerald-500/10 border-emerald-500/20 flex justify-between items-center text-xs">
                      <div>
                        <p className="font-bold text-emerald-500 font-mono">{so.order_number}</p>
                        <p className="text-[10px] text-muted-foreground">{so.order_date}</p>
                      </div>
                      <span className="font-bold font-mono text-emerald-500">${so.total_amount}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Setup Deal Modal */}
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

      {/* Create Quotation Modal */}
      <Modal isOpen={quoteModalOpen} onClose={() => setQuoteModalOpen(false)} title={`Generate Quotation — ${activeDeal?.title || ''}`}>
        <div className="space-y-4 text-xs">
          <Input
            label="Quotation Amount ($)"
            type="number"
            value={quoteAmount}
            onChange={(e) => setQuoteAmount(parseFloat(e.target.value) || 0)}
          />
          <Input
            label="Terms & Conditions"
            value={quoteTerms}
            onChange={(e) => setQuoteTerms(e.target.value)}
          />
          <Input
            label="Valid Until"
            type="date"
            value={quoteValidUntil}
            onChange={(e) => setQuoteValidUntil(e.target.value)}
          />

          <div className="flex justify-end gap-2 pt-2">
            <Button variant="secondary" onClick={() => setQuoteModalOpen(false)}>Cancel</Button>
            <Button onClick={handleCreateQuotation} variant="primary">Generate Quotation</Button>
          </div>
        </div>
      </Modal>

      {/* Close Deal Modal */}
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
