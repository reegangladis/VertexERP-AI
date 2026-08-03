import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Users,
  UserPlus,
  Search,
  Filter,
  FileText,
  PhoneCall,
  Award,
  Briefcase,
  HardDrive,
  History,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Mail,
  Phone,
  MapPin,
  Building,
  Calendar,
  Sparkles,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { apiClient } from '@/services/apiClient';

// ─────────────────────────────────────────
// 1. Employee Directory Page
// ─────────────────────────────────────────

export function EmployeeDirectoryPage() {
  const [employees, setEmployees] = useState<any[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);

  const loadEmployees = async () => {
    setLoading(true);
    try {
      const url = search ? `/api/v1/employees?query=${encodeURIComponent(search)}` : '/api/v1/employees';
      const res = await apiClient.get(url);
      setEmployees(res.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEmployees();
  }, [search]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Employee Directory</h1>
          <p className="text-sm text-muted-foreground">Core HR Employee Master Data console.</p>
        </div>
        <div className="flex items-center gap-3">
          <Button onClick={loadEmployees} disabled={loading} variant="secondary" className="flex items-center gap-2">
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Search & Filter bar */}
      <Card className="p-4">
        <div className="flex flex-col md:flex-row gap-3 items-center">
          <div className="relative flex-1 w-full">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search by Employee #, Email, or Name..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 text-xs border border-border rounded-md bg-background focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>
          <div className="flex items-center gap-2 text-xs font-mono text-muted-foreground">
            <span>Showing {employees.length} employee(s)</span>
          </div>
        </div>
      </Card>

      {/* Employee List Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {employees.map((emp) => (
          <Card key={emp.id} className="hover:border-primary/50 transition-colors">
            <CardHeader className="pb-3">
              <div className="flex justify-between items-start">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-primary/10 text-primary font-bold text-sm flex items-center justify-center border border-primary/20">
                    {emp.official_email[0].toUpperCase()}
                  </div>
                  <div>
                    <CardTitle className="text-base font-bold font-mono">{emp.employee_number}</CardTitle>
                    <CardDescription className="text-xs truncate">{emp.official_email}</CardDescription>
                  </div>
                </div>
                <span className="px-2 py-0.5 text-[10px] uppercase font-mono font-semibold rounded bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">
                  {emp.employment_status}
                </span>
              </div>
            </CardHeader>
            <CardContent className="space-y-3 text-xs">
              <div className="space-y-1 font-mono text-muted-foreground">
                <p className="flex items-center gap-2">
                  <Building className="h-3.5 w-3.5 text-primary" />
                  Type: <span className="text-foreground">{emp.employment_type}</span>
                </p>
                <p className="flex items-center gap-2">
                  <MapPin className="h-3.5 w-3.5 text-primary" />
                  Location: <span className="text-foreground">{emp.work_location || 'Headquarters'}</span>
                </p>
              </div>

              {/* Profile Completion Bar */}
              <div className="space-y-1">
                <div className="flex justify-between text-[10px] font-mono text-muted-foreground">
                  <span>Profile Completion</span>
                  <span className="font-semibold text-primary">{emp.profile_completion_percentage || 50}%</span>
                </div>
                <div className="w-full bg-secondary h-1.5 rounded-full overflow-hidden">
                  <div
                    className="bg-primary h-full rounded-full transition-all duration-300"
                    style={{ width: `${emp.profile_completion_percentage || 50}%` }}
                  />
                </div>
              </div>

              <div className="pt-2 border-t border-border flex justify-end">
                <Link
                  to={`/hr/employees/${emp.id}`}
                  className="text-xs font-semibold text-primary hover:underline flex items-center gap-1"
                >
                  View Profile Details →
                </Link>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────
// 2. Employee Profile Detail View
// ─────────────────────────────────────────

export function EmployeeProfileDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [emp, setEmp] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'profile' | 'documents' | 'contacts' | 'skills' | 'assets' | 'history'>('profile');

  useEffect(() => {
    if (id) {
      apiClient.get(`/api/v1/employees/${id}`).then((res) => setEmp(res.data)).catch(console.error);
    }
  }, [id]);

  if (!emp) {
    return (
      <div className="p-8 text-center text-muted-foreground animate-pulse">
        Loading Employee Master Record...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Employee Master Header */}
      <Card className="bg-gradient-to-r from-primary/10 via-background to-background border-primary/20">
        <CardHeader>
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-primary text-primary-foreground font-bold text-2xl flex items-center justify-center shadow-md">
                {emp.official_email[0].toUpperCase()}
              </div>
              <div>
                <CardTitle className="text-xl font-bold font-mono">{emp.employee_number}</CardTitle>
                <CardDescription className="text-sm font-mono text-muted-foreground">{emp.official_email}</CardDescription>
                <div className="flex items-center gap-2 mt-2">
                  <span className="px-2.5 py-0.5 text-xs rounded bg-primary/20 text-primary border border-primary/30 font-mono">
                    {emp.employment_type}
                  </span>
                  <span className="px-2.5 py-0.5 text-xs rounded bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 font-mono">
                    {emp.employment_status}
                  </span>
                </div>
              </div>
            </div>
            <div className="text-right space-y-1 text-xs font-mono">
              <p className="text-muted-foreground">Joined: {emp.joining_date ? new Date(emp.joining_date).toLocaleDateString() : 'N/A'}</p>
              <p className="text-muted-foreground">Location: {emp.work_location || 'Main Office'}</p>
              <p className="text-primary font-semibold">Profile Completion: {emp.profile_completion_percentage}%</p>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Tabs */}
      <div className="flex border-b border-border space-x-4 overflow-x-auto text-xs font-semibold">
        {[
          { key: 'profile', label: 'Personal Profile', icon: <Users className="h-4 w-4" /> },
          { key: 'documents', label: `Documents (${emp.documents?.length || 0})`, icon: <FileText className="h-4 w-4" /> },
          { key: 'contacts', label: `Contacts (${emp.emergency_contacts?.length || 0})`, icon: <PhoneCall className="h-4 w-4" /> },
          { key: 'skills', label: `Skills & Certs (${(emp.skills?.length || 0) + (emp.certifications?.length || 0)})`, icon: <Award className="h-4 w-4" /> },
          { key: 'assets', label: `Assets (${emp.assets?.length || 0})`, icon: <HardDrive className="h-4 w-4" /> },
          { key: 'history', label: `Employment History (${emp.history?.length || 0})`, icon: <History className="h-4 w-4" /> },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as any)}
            className={`pb-3 flex items-center gap-2 border-b-2 transition-colors ${
              activeTab === tab.key
                ? 'border-primary text-primary font-bold'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <Card>
        <CardContent className="pt-6">
          {activeTab === 'profile' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
              <div>
                <p className="text-muted-foreground uppercase text-[10px]">Personal Email</p>
                <p className="text-sm font-semibold">{emp.profile?.personal_email || 'N/A'}</p>
              </div>
              <div>
                <p className="text-muted-foreground uppercase text-[10px]">Personal Phone</p>
                <p className="text-sm font-semibold">{emp.profile?.personal_phone || 'N/A'}</p>
              </div>
              <div>
                <p className="text-muted-foreground uppercase text-[10px]">City / Country</p>
                <p className="text-sm font-semibold">{emp.profile?.city || 'N/A'}, {emp.profile?.country || 'N/A'}</p>
              </div>
              <div>
                <p className="text-muted-foreground uppercase text-[10px]">Bio</p>
                <p className="text-sm font-semibold">{emp.profile?.bio || 'No bio specified.'}</p>
              </div>
            </div>
          )}

          {activeTab === 'documents' && (
            <div className="space-y-3">
              {emp.documents?.length === 0 ? (
                <p className="text-xs text-muted-foreground">No documents uploaded yet.</p>
              ) : (
                emp.documents?.map((doc: any) => (
                  <div key={doc.id} className="p-3 border border-border rounded flex justify-between items-center text-xs font-mono">
                    <div>
                      <p className="font-semibold text-sm">{doc.document_name}</p>
                      <p className="text-muted-foreground">{doc.document_type}</p>
                    </div>
                    <span className="px-2 py-0.5 rounded bg-secondary text-foreground">{doc.verified ? 'Verified' : 'Pending'}</span>
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === 'contacts' && (
            <div className="space-y-3">
              {emp.emergency_contacts?.length === 0 ? (
                <p className="text-xs text-muted-foreground">No emergency contacts listed.</p>
              ) : (
                emp.emergency_contacts?.map((c: any) => (
                  <div key={c.id} className="p-3 border border-border rounded flex justify-between items-center text-xs font-mono">
                    <div>
                      <p className="font-semibold text-sm">{c.name} ({c.relationship})</p>
                      <p className="text-muted-foreground">{c.phone} • {c.email || 'No Email'}</p>
                    </div>
                    {c.primary_contact && <span className="px-2 py-0.5 rounded bg-primary/20 text-primary">Primary</span>}
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === 'skills' && (
            <div className="space-y-4 text-xs font-mono">
              <div>
                <h4 className="font-semibold text-sm mb-2">Skills ({emp.skills?.length || 0})</h4>
                <div className="flex flex-wrap gap-2">
                  {emp.skills?.map((s: any) => (
                    <span key={s.id} className="px-3 py-1 bg-secondary rounded border border-border">
                      {s.skill_name} ({s.skill_level})
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <h4 className="font-semibold text-sm mb-2">Certifications ({emp.certifications?.length || 0})</h4>
                <div className="space-y-2">
                  {emp.certifications?.map((c: any) => (
                    <div key={c.id} className="p-2 border border-border rounded">
                      <p className="font-semibold">{c.certificate_name}</p>
                      <p className="text-muted-foreground">Issuer: {c.issuer}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'assets' && (
            <div className="space-y-2 text-xs font-mono">
              {emp.assets?.length === 0 ? (
                <p className="text-muted-foreground">No physical assets issued.</p>
              ) : (
                emp.assets?.map((a: any) => (
                  <div key={a.id} className="p-3 border border-border rounded flex justify-between items-center">
                    <div>
                      <p className="font-semibold">{a.asset_name}</p>
                      <p className="text-muted-foreground">Code: {a.asset_code} | SN: {a.serial_number || 'N/A'}</p>
                    </div>
                    <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-500">{a.status}</span>
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === 'history' && (
            <div className="space-y-3 text-xs font-mono">
              {emp.history?.map((h: any) => (
                <div key={h.id} className="p-3 border border-border rounded">
                  <p className="font-semibold">{h.reason || 'Employment Status Event'}</p>
                  <p className="text-muted-foreground">Effective: {new Date(h.effective_from).toLocaleDateString()}</p>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
