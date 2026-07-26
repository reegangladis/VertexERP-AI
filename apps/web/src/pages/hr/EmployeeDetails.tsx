import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, User, Phone, Mail, MapPin, Calendar, FileText, UserPlus, Clock } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { apiClient } from '@/services/apiClient';

interface Profile {
  personal_email?: string;
  personal_phone?: string;
  date_of_birth?: string;
  gender?: string;
  nationality?: string;
  current_address?: string;
  photo_url?: string;
  emergency_contacts?: Array<{ name: string; relationship: string; phone: string }>;
}

interface Employee {
  id: string;
  employee_code: string;
  employment_type: string;
  status: string;
  date_joined: string;
  profile?: Profile;
}

export function HREmployeeDetails() {
  const { id } = useParams<{ id: string }>();
  const [employee, setEmployee] = useState<Employee | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchEmployee = async () => {
      try {
        const res = await apiClient.get(`/api/v1/employees`);
        const found = (res.data.data || []).find((emp: Employee) => emp.id === id);
        setEmployee(found || null);
      } catch (err) {
        console.error("Failed to fetch employee detail", err);
      } finally {
        setLoading(false);
      }
    };
    fetchEmployee();
  }, [id]);

  if (loading) {
    return <div className="text-center py-8 text-sm">Loading profile details...</div>;
  }

  if (!employee) {
    return (
      <div className="space-y-4">
        <Link to="/hr/employees" className="flex items-center gap-1.5 text-xs text-primary hover:underline">
          <ArrowLeft className="h-3.5 w-3.5" /> Back to Directory
        </Link>
        <div className="p-8 border border-dashed rounded text-center text-muted-foreground text-sm">
          Employee profile not found.
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Link to="/hr/employees" className="flex items-center gap-1.5 text-xs text-primary hover:underline">
          <ArrowLeft className="h-3.5 w-3.5" /> Back to Directory
        </Link>
        <span className="font-mono text-xs uppercase text-muted-foreground">ID: {employee.id}</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Profile Card */}
        <Card className="md:col-span-1">
          <CardContent className="pt-6 text-center space-y-4">
            <div className="h-24 w-24 bg-primary/10 rounded-full mx-auto flex items-center justify-center border-2 border-primary/20">
              {employee.profile?.photo_url ? (
                <img src={employee.profile.photo_url} alt="Profile" className="h-24 w-24 rounded-full object-cover" />
              ) : (
                <User className="h-10 w-10 text-primary" />
              )}
            </div>
            <div>
              <h2 className="text-lg font-bold font-mono text-primary">{employee.employee_code}</h2>
              <p className="text-xs text-muted-foreground capitalize">{employee.employment_type} • {employee.status}</p>
            </div>
            <div className="border-t border-border pt-4 text-left space-y-3 text-xs">
              <div className="flex items-center gap-2 text-muted-foreground">
                <Mail className="h-3.5 w-3.5 shrink-0" />
                <span>{employee.profile?.personal_email || 'No email bound'}</span>
              </div>
              <div className="flex items-center gap-2 text-muted-foreground">
                <Phone className="h-3.5 w-3.5 shrink-0" />
                <span>{employee.profile?.personal_phone || 'No phone number'}</span>
              </div>
              <div className="flex items-center gap-2 text-muted-foreground">
                <Calendar className="h-3.5 w-3.5 shrink-0" />
                <span>Joined {employee.date_joined}</span>
              </div>
              <div className="flex items-center gap-2 text-muted-foreground">
                <MapPin className="h-3.5 w-3.5 shrink-0" />
                <span>{employee.profile?.current_address || 'No address logged'}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Detailed Tabs */}
        <div className="md:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Personal & Emergency Contacts</CardTitle>
              <CardDescription>Emergency contacts mapped for safety protocols.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-xs">
                <div>
                  <span className="text-muted-foreground block">Gender</span>
                  <span className="font-semibold capitalize">{employee.profile?.gender || 'N/A'}</span>
                </div>
                <div>
                  <span className="text-muted-foreground block">Nationality</span>
                  <span className="font-semibold">{employee.profile?.nationality || 'N/A'}</span>
                </div>
              </div>
              
              <div className="border-t border-border pt-4">
                <h4 className="text-xs font-semibold uppercase tracking-wider mb-2 font-mono">Emergency Contacts</h4>
                {employee.profile?.emergency_contacts && employee.profile.emergency_contacts.length > 0 ? (
                  <div className="space-y-2">
                    {employee.profile.emergency_contacts.map((c, idx) => (
                      <div key={idx} className="flex justify-between items-center text-xs p-2 bg-secondary/20 rounded border border-border">
                        <div>
                          <p className="font-semibold">{c.name}</p>
                          <p className="text-[10px] text-muted-foreground capitalize">{c.relationship}</p>
                        </div>
                        <span className="font-mono text-muted-foreground">{c.phone}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-muted-foreground italic">No emergency contacts logged.</p>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Onboarding Workflow checklist</CardTitle>
              <CardDescription>Workflow setup for new joiner checklists.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 text-xs">
              <div className="flex items-center gap-2">
                <input type="checkbox" defaultChecked disabled className="rounded border-input text-primary focus:ring-primary h-4 w-4" />
                <span className="text-muted-foreground line-through">Draft offer letter & manager signature</span>
              </div>
              <div className="flex items-center gap-2">
                <input type="checkbox" defaultChecked disabled className="rounded border-input text-primary focus:ring-primary h-4 w-4" />
                <span className="text-muted-foreground line-through">Emergency details & ID document uploads</span>
              </div>
              <div className="flex items-center gap-2">
                <input type="checkbox" disabled className="rounded border-input text-primary focus:ring-primary h-4 w-4" />
                <span>IT Asset placeholder allocation (MacBook/ThinkPad setup)</span>
              </div>
              <div className="flex items-center gap-2">
                <input type="checkbox" disabled className="rounded border-input text-primary focus:ring-primary h-4 w-4" />
                <span>Welcome kit delivery dispatch tracker</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
export default HREmployeeDetails;
