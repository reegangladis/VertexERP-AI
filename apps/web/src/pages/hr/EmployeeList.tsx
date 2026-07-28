import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link } from 'react-router-dom';
import { Plus, Edit, Trash2, Search, Upload, Download, Loader2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Input } from '@/components/Input';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { useNotification } from '@/hooks/useNotification';
import { apiClient, getApiBaseUrl } from '@/services/apiClient';

const employeeSchema = z.object({
  employee_code: z.string().min(2, 'Employee Code must be at least 2 characters'),
  employment_type: z.string().default('full-time'),
  status: z.string().default('active'),
  date_joined: z.string().min(1, 'Date joined is required'),
  branch_id: z.string().optional().nullable(),
  department_id: z.string().optional().nullable(),
  designation_id: z.string().optional().nullable(),
  manager_id: z.string().optional().nullable(),
});

interface Employee {
  id: string;
  employee_code: string;
  employment_type: string;
  status: string;
  date_joined: string;
  branch_id: string | null;
  department_id: string | null;
  designation_id: string | null;
  manager_id: string | null;
}

export function HREmployeeList() {
  const { addNotification } = useNotification();
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [branches, setBranches] = useState<any[]>([]);
  const [departments, setDepartments] = useState<any[]>([]);
  const [designations, setDesignations] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedEmp, setSelectedEmp] = useState<Employee | null>(null);

  const {
    register,
    handleSubmit,
    setValue,
    reset,
    formState: { errors },
  } = useForm<any>({
    resolver: zodResolver(employeeSchema),
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [empRes, branchRes, deptRes, desigRes] = await Promise.all([
        apiClient.get(`/api/v1/employees?search=${search}`),
        apiClient.get('/api/v1/branches'),
        apiClient.get('/api/v1/departments'),
        apiClient.get('/api/v1/designations'),
      ]);
      setEmployees(empRes.data.data || []);
      setBranches(branchRes.data.data || []);
      setDepartments(deptRes.data.data || []);
      setDesignations(desigRes.data.data || []);
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
        branch_id: values.branch_id || null,
        department_id: values.department_id || null,
        designation_id: values.designation_id || null,
        manager_id: values.manager_id || null,
      };

      if (selectedEmp) {
        await apiClient.put(`/api/v1/employees/${selectedEmp.id}`, payload);
        addNotification('Employee profile updated successfully', 'success');
      } else {
        await apiClient.post('/api/v1/employees', payload);
        addNotification('Employee created successfully', 'success');
      }
      setModalOpen(false);
      reset();
      setSelectedEmp(null);
      fetchData();
    } catch (err: any) {
      addNotification(err.message || 'Operation failed', 'error');
    }
  };

  const handleEdit = (emp: Employee) => {
    setSelectedEmp(emp);
    setValue('employee_code', emp.employee_code);
    setValue('employment_type', emp.employment_type);
    setValue('status', emp.status);
    setValue('date_joined', emp.date_joined);
    setValue('branch_id', emp.branch_id || '');
    setValue('department_id', emp.department_id || '');
    setValue('designation_id', emp.designation_id || '');
    setValue('manager_id', emp.manager_id || '');
    setModalOpen(true);
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this employee?')) return;
    try {
      await apiClient.delete(`/api/v1/employees/${id}`);
      addNotification('Employee profile deleted successfully', 'success');
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
      await apiClient.post('/api/v1/employees/bulk-upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      addNotification('Bulk employee CSV import completed', 'success');
      fetchData();
    } catch (err: any) {
      addNotification(err.message || 'Bulk upload failed', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Employee Directory</h1>
          <p className="text-sm text-muted-foreground">Manage active employee lifecycles, division coordinates, and profile details.</p>
        </div>
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-2 px-3 py-2 border border-border rounded bg-secondary/35 text-xs font-semibold cursor-pointer select-none hover:bg-secondary">
            <Upload className="h-4 w-4" />
            Bulk Upload CSV
            <input type="file" accept=".csv" className="hidden" onChange={handleCsvUpload} />
          </label>
          <a
            href={`${getApiBaseUrl()}/api/v1/employees/export/csv`}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2 px-3 py-2 border border-border rounded bg-secondary/35 text-xs font-semibold hover:bg-secondary cursor-pointer select-none"
          >
            <Download className="h-4 w-4" />
            Export CSV
          </a>
          <Button
            onClick={() => {
              setSelectedEmp(null);
              reset({
                employee_code: '',
                employment_type: 'full-time',
                status: 'active',
                date_joined: new Date().toISOString().split('T')[0],
                branch_id: '',
                department_id: '',
                designation_id: '',
                manager_id: '',
              });
              setModalOpen(true);
            }}
            variant="primary"
            className="flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            Add Employee
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Staff Records</CardTitle>
            <CardDescription>Full listing of onboarded, active, or terminated corporate employees.</CardDescription>
          </div>
          <div className="relative w-64">
            <Search className="absolute left-2.5 top-3 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search by code or name..."
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
                    <th className="py-3 px-4">Employee Code</th>
                    <th className="py-3 px-4">Employment Type</th>
                    <th className="py-3 px-4">Joined Date</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {employees.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="py-8 text-center text-muted-foreground">
                        No employees found. Try seeding data to verify.
                      </td>
                    </tr>
                  ) : (
                    employees.map((e) => (
                      <tr key={e.id} className="border-b border-border hover:bg-secondary/10">
                        <td className="py-3.5 px-4 font-semibold font-mono text-primary">
                          <Link to={`/hr/employees/${e.id}`} className="hover:underline">
                            {e.employee_code}
                          </Link>
                        </td>
                        <td className="py-3.5 px-4 text-xs font-mono uppercase text-muted-foreground">{e.employment_type}</td>
                        <td className="py-3.5 px-4 text-xs font-mono">{e.date_joined}</td>
                        <td className="py-3.5 px-4 text-xs font-semibold uppercase">
                          <span className={`px-2 py-0.5 rounded ${e.status === 'active' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-red-500/10 text-red-500'}`}>
                            {e.status}
                          </span>
                        </td>
                        <td className="py-3.5 px-4 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => handleEdit(e)}
                              className="p-1.5 hover:bg-secondary rounded text-muted-foreground hover:text-foreground"
                            >
                              <Edit className="h-4 w-4" />
                            </button>
                            <button
                              onClick={() => handleDelete(e.id)}
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

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title={selectedEmp ? 'Edit Employee Profile' : 'Add Employee'}>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Employee Code"
            {...register('employee_code')}
            error={errors.employee_code?.message as string}
          />
          <div className="grid grid-cols-2 gap-3">
            <div className="flex flex-col space-y-1.5">
              <label className="text-sm font-medium">Employment Type</label>
              <select
                {...register('employment_type')}
                className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              >
                <option value="full-time">Full-Time</option>
                <option value="part-time">Part-Time</option>
                <option value="contractor">Contractor</option>
                <option value="intern">Intern</option>
              </select>
            </div>
            <div className="flex flex-col space-y-1.5">
              <label className="text-sm font-medium">Status</label>
              <select
                {...register('status')}
                className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              >
                <option value="active">Active</option>
                <option value="terminated">Terminated</option>
                <option value="pending">Pending</option>
              </select>
            </div>
          </div>

          <Input
            label="Date Joined"
            type="date"
            {...register('date_joined')}
            error={errors.date_joined?.message as string}
          />

          <div className="grid grid-cols-2 gap-3">
            <div className="flex flex-col space-y-1.5">
              <label className="text-sm font-medium">Branch Location</label>
              <select
                {...register('branch_id')}
                className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none"
              >
                <option value="">-- Global HQ --</option>
                {branches.map((b) => (
                  <option key={b.id} value={b.id}>{b.name}</option>
                ))}
              </select>
            </div>
            <div className="flex flex-col space-y-1.5">
              <label className="text-sm font-medium">Department Division</label>
              <select
                {...register('department_id')}
                className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none"
              >
                <option value="">-- None --</option>
                {departments.map((d) => (
                  <option key={d.id} value={d.id}>{d.name}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="flex flex-col space-y-1.5">
              <label className="text-sm font-medium">Designation</label>
              <select
                {...register('designation_id')}
                className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none"
              >
                <option value="">-- Unassigned --</option>
                {designations.map((ds) => (
                  <option key={ds.id} value={ds.id}>{ds.title}</option>
                ))}
              </select>
            </div>
            <div className="flex flex-col space-y-1.5">
              <label className="text-sm font-medium">Manager</label>
              <select
                {...register('manager_id')}
                className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none"
              >
                <option value="">-- None --</option>
                {employees
                  .filter((emp) => emp.id !== selectedEmp?.id)
                  .map((emp) => (
                    <option key={emp.id} value={emp.id}>{emp.employee_code}</option>
                  ))}
              </select>
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary">
              {selectedEmp ? 'Update' : 'Create'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
export default HREmployeeList;
