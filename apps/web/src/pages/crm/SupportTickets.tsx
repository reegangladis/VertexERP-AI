import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { ShieldAlert, Plus, Check, Loader2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { Input } from '@/components/Input';
import { useNotification } from '@/hooks/useNotification';
import { apiClient } from '@/services/apiClient';

const ticketSchema = z.object({
  customer_id: z.string().min(1, 'Customer account is required'),
  category: z.string().default('technical'),
  priority: z.string().default('medium'),
});

interface Ticket {
  id: string;
  customer_id: string;
  category: string;
  priority: string;
  status: string;
  resolution_notes: string | null;
}

export function CRMSupportTickets() {
  const { addNotification } = useNotification();
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [customers, setCustomers] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [resolveModalOpen, setResolveModalOpen] = useState(false);
  const [activeTicketId, setActiveTicketId] = useState('');
  const [resolutionNotes, setResolutionNotes] = useState('');

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<any>({
    resolver: zodResolver(ticketSchema),
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [ticketRes, custRes] = await Promise.all([
        apiClient.get('/api/v1/crm/support-tickets'),
        apiClient.get('/api/v1/crm/customers'),
      ]);
      setTickets(ticketRes.data.data || []);
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
      await apiClient.post('/api/v1/crm/support-tickets', values);
      addNotification('Support ticket registered', 'success');
      setModalOpen(false);
      reset();
      fetchData();
    } catch (err: any) {
      addNotification(err.response?.data?.detail || 'Registration failed', 'error');
    }
  };

  const handleResolveTicket = async () => {
    try {
      await apiClient.put(`/api/v1/crm/support-tickets/${activeTicketId}`, {
        status: 'resolved',
        resolution_notes: resolutionNotes,
      });
      addNotification('Support ticket resolved successfully', 'success');
      setResolveModalOpen(false);
      setResolutionNotes('');
      fetchData();
    } catch (err: any) {
      addNotification(err.response?.data?.detail || 'Resolution step failed', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Support Tickets</h1>
          <p className="text-sm text-muted-foreground">Audit support requests, assign tickets to teams, and record resolution notes.</p>
        </div>
        <Button onClick={() => setModalOpen(true)} variant="primary" className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          File Ticket
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Client Support Requests</CardTitle>
          <CardDescription>Billing, technical features, and priority logs.</CardDescription>
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
                    <th className="py-2.5 px-3">Ticket ID</th>
                    <th className="py-2.5 px-3">Client Account</th>
                    <th className="py-2.5 px-3">Category</th>
                    <th className="py-2.5 px-3 text-right">Priority</th>
                    <th className="py-2.5 px-3">Status</th>
                    <th className="py-2.5 px-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {tickets.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="py-6 text-center text-muted-foreground text-xs">No active support tickets logged.</td>
                    </tr>
                  ) : (
                    tickets.map((t) => (
                      <tr key={t.id} className="border-b border-border hover:bg-secondary/10 text-xs">
                        <td className="py-3 px-3 font-mono text-primary font-semibold">{t.id.slice(0, 8)}...</td>
                        <td className="py-3 px-3 font-mono">Customer {t.customer_id.slice(0, 8)}...</td>
                        <td className="py-3 px-3 uppercase">{t.category}</td>
                        <td className="py-3 px-3 text-right font-mono text-muted-foreground">{t.priority}</td>
                        <td className="py-3 px-3 uppercase font-semibold">
                          <span className={`px-2 py-0.5 rounded text-[10px] ${
                            t.status === 'resolved' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-amber-500/10 text-amber-500'
                          }`}>
                            {t.status}
                          </span>
                        </td>
                        <td className="py-3 px-3 text-right">
                          {t.status !== 'resolved' && (
                            <button
                              onClick={() => {
                                setActiveTicketId(t.id);
                                setResolveModalOpen(true);
                              }}
                              className="p-1 hover:bg-emerald-500/10 text-emerald-500 rounded border border-emerald-500/20"
                              title="Resolve Ticket"
                            >
                              <Check className="h-3.5 w-3.5" />
                            </button>
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

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title="File Support Case">
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

          <div className="grid grid-cols-2 gap-3">
            <div className="flex flex-col space-y-1.5">
              <label className="text-sm font-medium">Category</label>
              <select
                {...register('category')}
                className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none"
              >
                <option value="technical">Technical</option>
                <option value="billing">Billing</option>
                <option value="feature_request">Feature Request</option>
              </select>
            </div>
            <div className="flex flex-col space-y-1.5">
              <label className="text-sm font-medium">Priority</label>
              <select
                {...register('priority')}
                className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none"
              >
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary">File Ticket</Button>
          </div>
        </form>
      </Modal>

      <Modal isOpen={resolveModalOpen} onClose={() => setResolveModalOpen(false)} title="Resolve Support Case">
        <div className="space-y-4">
          <Input
            label="Resolution Notes"
            value={resolutionNotes}
            onChange={(e) => setResolutionNotes(e.target.value)}
            placeholder="How was this ticket resolved?"
          />
          <div className="flex justify-end gap-2 pt-4">
            <Button variant="secondary" onClick={() => setResolveModalOpen(false)}>Cancel</Button>
            <Button onClick={handleResolveTicket} variant="primary">Resolve Ticket</Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
export default CRMSupportTickets;
