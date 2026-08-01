import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, User, Phone, Mail, Globe, Tag, CheckSquare, Plus } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { useNotification } from '@/hooks/useNotification';
import { apiClient } from '@/services/apiClient';

interface Contact {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string | null;
  job_title: string | null;
  is_primary: boolean;
}

interface Customer {
  id: string;
  name: string;
  type: string;
  industry: string | null;
  status: string;
  tags?: { list?: string[] };
}

export function CRMCustomerDetails() {
  const { id } = useParams<{ id: string }>();
  const { addNotification } = useNotification();
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        const [custRes, contactRes] = await Promise.all([
          apiClient.get(`/api/v1/crm/customers/${id}`),
          apiClient.get(`/api/v1/crm/contacts?customer_id=${id}`),
        ]);
        setCustomer(custRes.data.data || null);
        setContacts(contactRes.data.data || []);
      } catch (err) {
        console.error("Failed to load customer details", err);
      } finally {
        setLoading(false);
      }
    };
    if (id) fetchDetails();
  }, [id]);

  if (loading) {
    return <div className="text-center py-8 text-sm">Loading client account profile...</div>;
  }

  if (!customer) {
    return (
      <div className="space-y-4">
        <Link to="/crm/customers" className="flex items-center gap-1.5 text-xs text-primary hover:underline">
          <ArrowLeft className="h-3.5 w-3.5" /> Back to Customers
        </Link>
        <div className="p-8 border border-dashed rounded text-center text-muted-foreground text-sm">
          Customer account profile not found.
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Link to="/crm/customers" className="flex items-center gap-1.5 text-xs text-primary hover:underline">
          <ArrowLeft className="h-3.5 w-3.5" /> Back to Customers
        </Link>
        <span className="font-mono text-xs uppercase text-muted-foreground">Account ID: {customer.id}</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Profile Card */}
        <Card className="md:col-span-1">
          <CardContent className="pt-6 space-y-4">
            <div>
              <h2 className="text-lg font-bold text-foreground">{customer.name}</h2>
              <p className="text-xs text-muted-foreground capitalize">{customer.type} Account • {customer.status}</p>
            </div>
            
            <div className="border-t border-border pt-4 space-y-3 text-xs">
              <div className="flex items-center gap-2 text-muted-foreground">
                <Globe className="h-3.5 w-3.5 shrink-0" />
                <span>Industry: {customer.industry || 'Not Specified'}</span>
              </div>
              <div className="flex items-center gap-2 text-muted-foreground">
                <Tag className="h-3.5 w-3.5 shrink-0" />
                <div className="flex flex-wrap gap-1">
                  {customer.tags?.list?.map((t, idx) => (
                    <span key={idx} className="bg-secondary/40 px-1.5 py-0.5 rounded text-[9px] font-mono border border-border">
                      {t}
                    </span>
                  )) || <span className="italic">No tags logged</span>}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Contacts & Activity checklists */}
        <div className="md:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Bound Contacts directory</CardTitle>
              <CardDescription>Primary contacts, job titles, and email communications.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {contacts.length === 0 ? (
                <p className="text-xs text-muted-foreground italic">No contacts registered for this account.</p>
              ) : (
                contacts.map((c) => (
                  <div key={c.id} className="p-3 border border-border rounded bg-secondary/15 flex justify-between items-center text-xs">
                    <div>
                      <p className="font-semibold text-primary">{c.first_name} {c.last_name}</p>
                      <p className="text-[10px] text-muted-foreground">{c.job_title || 'N/A'} • {c.is_primary ? 'Primary Contact' : 'Secondary Contact'}</p>
                    </div>
                    <div className="text-right space-y-1">
                      <div className="flex items-center gap-1 justify-end text-muted-foreground font-mono text-[10px]">
                        <Mail className="h-3 w-3" />
                        <span>{c.email}</span>
                      </div>
                      {c.phone && (
                        <div className="flex items-center gap-1 justify-end text-muted-foreground font-mono text-[10px]">
                          <Phone className="h-3 w-3" />
                          <span>{c.phone}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Customer notes & communications Preferences</CardTitle>
              <CardDescription>Client newsletter and marketing permissions.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 text-xs">
              <div className="flex items-center gap-2">
                <input type="checkbox" defaultChecked disabled className="rounded border-input text-primary h-4 w-4" />
                <span>Opt-in for Email Marketing campaigns</span>
              </div>
              <div className="flex items-center gap-2">
                <input type="checkbox" defaultChecked disabled className="rounded border-input text-primary h-4 w-4" />
                <span>Opt-in for Quarterly alignment phone calls</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
export default CRMCustomerDetails;
