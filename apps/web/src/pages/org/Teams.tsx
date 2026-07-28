import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Plus, Edit, Trash2, Search, Upload, Download, Loader2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Input } from '@/components/Input';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { useNotification } from '@/hooks/useNotification';
import { apiClient, getApiBaseUrl } from '@/services/apiClient';

const teamSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  slug: z.string().min(2, 'Slug must be at least 2 characters'),
  description: z.string().optional(),
  department_id: z.string().min(1, 'Department is required'),
  parent_team_id: z.string().nullable().optional(),
  status: z.string().default('active'),
});

type TeamFormValues = z.infer<typeof teamSchema>;

interface Team {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  department_id: string;
  parent_team_id: string | null;
  status: string;
}

export function OrgTeams() {
  const { addNotification } = useNotification();
  const [teams, setTeams] = useState<Team[]>([]);
  const [departments, setDepartments] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null);

  const {
    register,
    handleSubmit,
    setValue,
    reset,
    formState: { errors },
  } = useForm<any>({
    resolver: zodResolver(teamSchema),
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [teamsRes, deptsRes] = await Promise.all([
        apiClient.get(`/api/v1/teams?search=${search}`),
        apiClient.get('/api/v1/departments'),
      ]);
      setTeams(teamsRes.data.data || []);
      setDepartments(deptsRes.data.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [search]);

  const onSubmit = async (values: TeamFormValues) => {
    try {
      const formattedValues = {
        ...values,
        parent_team_id: values.parent_team_id || null,
      };

      if (selectedTeam) {
        await apiClient.put(`/api/v1/teams/${selectedTeam.id}`, formattedValues);
        addNotification('Team updated successfully', 'success');
      } else {
        await apiClient.post('/api/v1/teams', formattedValues);
        addNotification('Team created successfully', 'success');
      }
      setModalOpen(false);
      reset();
      setSelectedTeam(null);
      fetchData();
    } catch (err: any) {
      addNotification(err.message || 'Operation failed', 'error');
    }
  };

  const handleEdit = (team: Team) => {
    setSelectedTeam(team);
    setValue('name', team.name);
    setValue('slug', team.slug);
    setValue('description', team.description || '');
    setValue('department_id', team.department_id);
    setValue('parent_team_id', team.parent_team_id || '');
    setValue('status', team.status);
    setModalOpen(true);
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this team?')) return;
    try {
      await apiClient.delete(`/api/v1/teams/${id}`);
      addNotification('Team deleted successfully', 'success');
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
      await apiClient.post('/api/v1/teams/bulk-upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      addNotification('Bulk import completed', 'success');
      fetchData();
    } catch (err: any) {
      addNotification(err.message || 'Bulk upload failed', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Team Management</h1>
          <p className="text-sm text-muted-foreground">Setup sub-teams, leads, and coordinate operational mapping units.</p>
        </div>
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-2 px-3 py-2 border border-border rounded bg-secondary/35 text-xs font-semibold cursor-pointer select-none hover:bg-secondary">
            <Upload className="h-4 w-4" />
            Bulk Upload CSV
            <input type="file" accept=".csv" className="hidden" onChange={handleCsvUpload} />
          </label>
          <a
            href={`${getApiBaseUrl()}/api/v1/teams/export/csv`}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2 px-3 py-2 border border-border rounded bg-secondary/35 text-xs font-semibold hover:bg-secondary cursor-pointer select-none"
          >
            <Download className="h-4 w-4" />
            Export CSV
          </a>
          <Button
            onClick={() => {
              setSelectedTeam(null);
              reset({
                name: '',
                slug: '',
                description: '',
                department_id: departments[0]?.id || '',
                parent_team_id: '',
                status: 'active',
              });
              setModalOpen(true);
            }}
            variant="primary"
            className="flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            Add Team
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Teams Directory</CardTitle>
            <CardDescription>Visual list of operational sub-teams and working blocks.</CardDescription>
          </div>
          <div className="relative w-64">
            <Search className="absolute left-2.5 top-3 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search teams..."
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
                    <th className="py-3 px-4">Name</th>
                    <th className="py-3 px-4">Slug</th>
                    <th className="py-3 px-4">Description</th>
                    <th className="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {teams.length === 0 ? (
                    <tr>
                      <td colSpan={4} className="py-8 text-center text-muted-foreground">
                        No teams found. Try seeding data to verify.
                      </td>
                    </tr>
                  ) : (
                    teams.map((t) => (
                      <tr key={t.id} className="border-b border-border hover:bg-secondary/10">
                        <td className="py-3.5 px-4 font-semibold">{t.name}</td>
                        <td className="py-3.5 px-4 font-mono text-xs">{t.slug}</td>
                        <td className="py-3.5 px-4 text-muted-foreground text-xs">{t.description || '-'}</td>
                        <td className="py-3.5 px-4 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => handleEdit(t)}
                              className="p-1.5 hover:bg-secondary rounded text-muted-foreground hover:text-foreground"
                            >
                              <Edit className="h-4 w-4" />
                            </button>
                            <button
                              onClick={() => handleDelete(t.id)}
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

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title={selectedTeam ? 'Edit Team' : 'Add Team'}>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Team Name"
            {...register('name')}
            error={errors.name?.message as string}
          />
          <Input
            label="Slug Identifier"
            {...register('slug')}
            error={errors.slug?.message as string}
          />
          <Input
            label="Description"
            {...register('description')}
            error={errors.description?.message as string}
          />
          <div className="flex flex-col space-y-1.5">
            <label className="text-sm font-medium">Department</label>
            <select
              {...register('department_id')}
              className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            >
              {departments.map((d) => (
                <option key={d.id} value={d.id}>{d.name}</option>
              ))}
            </select>
            {errors.department_id && <p className="text-xs text-red-500">{errors.department_id.message as string}</p>}
          </div>
          <div className="flex flex-col space-y-1.5">
            <label className="text-sm font-medium">Parent Team</label>
            <select
              {...register('parent_team_id')}
              className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            >
              <option value="">-- None (Root Team) --</option>
              {teams
                .filter((t) => t.id !== selectedTeam?.id)
                .map((t) => (
                  <option key={t.id} value={t.id}>{t.name}</option>
                ))}
            </select>
          </div>
          <div className="flex justify-end gap-2 pt-4">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary">
              {selectedTeam ? 'Update' : 'Create'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
export default OrgTeams;
