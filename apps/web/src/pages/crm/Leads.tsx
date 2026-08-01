import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Plus, Edit, Trash2, Search, Upload, Download, Loader2, UserCheck, ArrowRightLeft } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Input } from '@/components/Input';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { useNotification } from '@/hooks/useNotification';
import { apiClient, getApiBaseUrl } from '@/services/apiClient';

const leadSchema = z.object({
  first_name: z.string().min(2, 'First name must be at least 2 characters'),
  last_name: z.string().min(2, 'Last name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  phone: z.string().optional().nullable(),
  company: z.string().optional().nullable(),
  status: z.string().default('new'),
});

interface Lead {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string | null;
  company: string | null;
  status: string;
  score: number;
}

export function CRMLeads() {
  const { addNotification } = useNotification();
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [convertModalOpen, setConvertModalOpen] = useState(false);
  const [leadToConvert, setLeadToConvert] = useState<Lead | null>(null);
  const [converting, setConverting] = useState(false);
  const [dealAmount, setDealAmount] = useState<number>(5000);

  const {
    register,
    handleSubmit,
    setValue,
    reset,
    formState: { errors },
  } = useForm<any>({
    resolver: zodResolver(leadSchema),
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get(`/api/v1/crm/leads?search=${search}`);
      setLeads(res.data.data || []);
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
        phone: values.phone || null,
        company: values.company || null,
      };

      if (selectedLead) {
        await apiClient.put(`/api/v1/crm/leads/${selectedLead.id}`, payload);
        addNotification('Lead updated successfully', 'success');
      } else {
        await apiClient.post('/api/v1/crm/leads', payload);
        addNotification('Lead captured successfully', 'success');
      }
      setModalOpen(false);
      reset();
      setSelectedLead(null);
      fetchData();
    } catch (err: any) {
      addNotification(err.response?.data?.detail || 'Operation failed', 'error');
    }
  };

  const handleEdit = (lead: Lead) => {
    setSelectedLead(lead);
    setValue('first_name', lead.first_name);
    setValue('last_name', lead.last_name);
    setValue('email', lead.email);
    setValue('phone', lead.phone || '');
    setValue('company', lead.company || '');
    setValue('status', lead.status);
    setModalOpen(true);
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this lead?')) return;
    try {
      await apiClient.delete(`/api/v1/crm/leads/${id}`);
      addNotification('Lead record deleted', 'success');
      fetchData();
    } catch (err: any) {
      addNotification(err.message || 'Deletion failed', 'error');
    }
  };

  const handleConvertLead = async () => {
    if (!leadToConvert) return;
    setConverting(true);
    try {
      await apiClient.post(`/api/v1/crm/leads/${leadToConvert.id}/convert`, {
        customer_name: leadToConvert.company || `${leadToConvert.first_name} ${leadToConvert.last_name}`,
        create_opportunity: true,
        opportunity_title: `Opportunity - ${leadToConvert.company || leadToConvert.first_name}`,
        deal_amount: dealAmount,
      });
      addNotification(`Lead ${leadToConvert.first_name} converted to Customer and Deal successfully!`, 'success');
      setConvertModalOpen(false);
      setLeadToConvert(null);
      fetchData();
    } catch (err: any) {
      addNotification(err.response?.data?.detail || 'Lead conversion failed', 'error');
    } finally {
      setConverting(false);
    }
  };

  const handleCsvUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      await apiClient.post('/api/v1/crm/leads/bulk-upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      addNotification('Bulk lead CSV import completed', 'success');
      fetchData();
    } catch (err: any) {
      addNotification(err.message || 'Bulk upload failed', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Leads Inbox & Conversion</h1>
          <p className="text-sm text-muted-foreground">Manage captured lead directories, AI lead scoring, and convert qualified leads to accounts.</p>
        </div>
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-2 px-3 py-2 border border-border rounded bg-secondary/35 text-xs font-semibold cursor-pointer select-none hover:bg-secondary">
            <Upload className="h-4 w-4" />
            Bulk Upload CSV
            <input type="file" accept=".csv" className="hidden" onChange={handleCsvUpload} />
          </label>
          <a
            href={`${getApiBaseUrl()}/api/v1/crm/leads/export/csv`}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2 px-3 py-2 border border-border rounded bg-secondary/35 text-xs font-semibold hover:bg-secondary cursor-pointer select-none"
          >
            <Download className="h-4 w-4" />
            Export CSV
          </a>
          <Button
            onClick={() => {
              setSelectedLead(null);
              reset({
                first_name: '',
                last_name: '',
                email: '',
                phone: '',
                company: '',
                status: 'new',
              });
              setModalOpen(true);
            }}
            variant="primary"
            className="flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            Add Lead
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Captured Leads</CardTitle>
            <CardDescription>Qualified/unqualified marketing leads registry.</CardDescription>
          </div>
          <div className="relative w-64">
            <Search className="absolute left-2.5 top-3 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search by first/last name..."
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
                    <th className="py-3 px-4">Lead Name</th>
                    <th className="py-3 px-4">Company</th>
                    <th className="py-3 px-4">Contact Details</th>
                    <th className="py-3 px-4 text-right">Lead Score</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {leads.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="py-8 text-center text-muted-foreground">
                        No leads in inbox. Try seeding data to verify.
                      </td>
                    </tr>
                  ) : (
                    leads.map((l) => (
                      <tr key={l.id} className="border-b border-border hover:bg-secondary/10">
                        <td className="py-3.5 px-4 font-semibold text-foreground">
                          {l.first_name} {l.last_name}
                        </td>
                        <td className="py-3.5 px-4 text-xs font-mono">{l.company || 'N/A'}</td>
                        <td className="py-3.5 px-4">
                          <div className="text-xs font-mono text-muted-foreground">
                            <p>{l.email}</p>
                            <p>{l.phone || ''}</p>
                          </div>
                        </td>
                        <td className="py-3.5 px-4 text-right font-mono font-bold text-primary">
                          {l.score}
                        </td>
                        <td className="py-3.5 px-4 text-xs font-semibold uppercase">
                          <span className={`px-2 py-0.5 rounded ${
                            l.status === 'converted' ? 'bg-purple-500/10 text-purple-500' :
                            l.status === 'qualified' ? 'bg-emerald-500/10 text-emerald-500' :
                            l.status === 'lost' ? 'bg-red-500/10 text-red-500' : 'bg-amber-500/10 text-amber-500'
                          }`}>
                            {l.status}
                          </span>
                        </td>
                        <td className="py-3.5 px-4 text-right">
                          <div className="flex items-center justify-end gap-2">
                            {l.status !== 'converted' && (
                              <Button
                                size="sm"
                                variant="secondary"
                                onClick={() => {
                                  setLeadToConvert(l);
                                  setConvertModalOpen(true);
                                }}
                                className="text-[10px] h-7 px-2 flex items-center gap-1 text-purple-500 hover:text-purple-600"
                              >
                                <ArrowRightLeft className="h-3 w-3" /> Convert
                              </Button>
                            )}
                            <button
                              onClick={() => handleEdit(l)}
                              className="p-1.5 hover:bg-secondary rounded text-muted-foreground hover:text-foreground"
                            >
                              <Edit className="h-4 w-4" />
                            </button>
                            <button
                              onClick={() => handleDelete(l.id)}
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

      {/* Add / Edit Modal */}
      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title={selectedLead ? 'Edit Lead Profile' : 'Capture Lead'}>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <Input label="First Name" {...register('first_name')} error={errors.first_name?.message as string} />
            <Input label="Last Name" {...register('last_name')} error={errors.last_name?.message as string} />
          </div>

          <Input label="Email Address" type="email" {...register('email')} error={errors.email?.message as string} />
          <Input label="Phone Number" {...register('phone')} />
          <Input label="Company Name" {...register('company')} />

          <div className="flex flex-col space-y-1.5">
            <label className="text-sm font-medium">Status</label>
            <select
              {...register('status')}
              className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none"
            >
              <option value="new">New</option>
              <option value="contacted">Contacted</option>
              <option value="qualified">Qualified</option>
              <option value="lost">Lost</option>
            </select>
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary">
              {selectedLead ? 'Update' : 'Capture'}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Lead Conversion Modal */}
      <Modal isOpen={convertModalOpen} onClose={() => setConvertModalOpen(false)} title="Convert Lead to Account & Deal">
        {leadToConvert && (
          <div className="space-y-4 text-xs">
            <p className="text-muted-foreground">
              Converting lead <strong className="text-primary">{leadToConvert.first_name} {leadToConvert.last_name}</strong> will create a Customer Account and initial Sales Deal in the pipeline.
            </p>
            <div className="space-y-3 p-3 border border-border rounded-xl bg-secondary/15">
              <div className="flex justify-between">
                <span className="text-muted-foreground font-mono">Account Name:</span>
                <span className="font-bold">{leadToConvert.company || `${leadToConvert.first_name} ${leadToConvert.last_name}`}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground font-mono">Primary Contact:</span>
                <span>{leadToConvert.email}</span>
              </div>
            </div>

            <Input
              label="Estimated Deal Value ($)"
              type="number"
              value={dealAmount}
              onChange={(e) => setDealAmount(parseFloat(e.target.value) || 0)}
            />

            <div className="flex justify-end gap-2 pt-2">
              <Button variant="secondary" onClick={() => setConvertModalOpen(false)}>Cancel</Button>
              <Button onClick={handleConvertLead} disabled={converting} variant="primary" className="bg-purple-600 hover:bg-purple-700">
                {converting ? <Loader2 className="h-4 w-4 animate-spin" /> : <UserCheck className="h-4 w-4" />}
                Convert Lead
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
export default CRMLeads;
