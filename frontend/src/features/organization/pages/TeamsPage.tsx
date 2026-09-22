import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  useTeams,
  useTeamMembers,
  useCreateTeam,
  useDeleteTeam,
  useAddTeamMember,
  useDepartments,
} from "../api/queries";
import { teamSchema } from "../schemas/organization.schemas";
import { Team } from "../types/organization.types";
import { z } from "zod";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Textarea } from "@/components/ui/Textarea";
import { Select } from "@/components/ui/Select";
import { Modal } from "@/components/ui/Modal";
import { Badge } from "@/components/ui/Badge";
import { Alert } from "@/components/ui/Alert";
import { Skeleton } from "@/components/ui/Skeleton";
import { EmptyState } from "@/components/ui/EmptyState";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/Table";
import { RequirePermission } from "@/components/security/RequirePermission";
import { Users, Plus, Trash2, UserPlus } from "lucide-react";

type TeamFormData = z.infer<typeof teamSchema>;

export const TeamsPage: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeTeamIdForMembers, setActiveTeamIdForMembers] = useState<string | null>(null);
  const [memberUserId, setMemberUserId] = useState("");
  const [memberRole, setMemberRole] = useState("MEMBER");
  const [formError, setFormError] = useState<string | null>(null);

  const { data: teams, isLoading, isError, error, refetch } = useTeams();
  const { data: departments } = useDepartments();
  const { data: members, isLoading: lMembers } = useTeamMembers(activeTeamIdForMembers || "");

  const createMutation = useCreateTeam();
  const deleteMutation = useDeleteTeam();
  const addMemberMutation = useAddTeamMember(activeTeamIdForMembers || "");

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<TeamFormData>({
    resolver: zodResolver(teamSchema),
    defaultValues: {
      code: "",
      name: "",
      description: "",
      department_id: "",
      is_active: true,
    },
  });

  const onSubmit = async (data: TeamFormData) => {
    setFormError(null);
    try {
      const payload = {
        ...data,
        department_id: data.department_id || null,
      };
      await createMutation.mutateAsync(payload);
      reset();
      setIsModalOpen(false);
    } catch (err: any) {
      setFormError(err.message || "Failed to create team");
    }
  };

  const handleAddMember = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!memberUserId) return;
    try {
      await addMemberMutation.mutateAsync({
        user_id: memberUserId,
        role: memberRole,
      });
      setMemberUserId("");
    } catch (err: any) {
      alert(err.message || "Failed to add team member");
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm("Are you sure you want to delete this team?")) {
      try {
        await deleteMutation.mutateAsync(id);
      } catch (err: any) {
        alert(err.message || "Failed to delete team");
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Users className="w-5 h-5 text-sky-400" /> Teams & Pods
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Manage departmental units, cross-functional squads, and member rosters.
          </p>
        </div>
        <RequirePermission permission="organization:teams:write">
          <Button onClick={() => setIsModalOpen(true)} className="gap-2 text-xs">
            <Plus className="w-4 h-4" /> Add Team
          </Button>
        </RequirePermission>
      </div>

      {isError && (
        <Alert variant="error" title="Failed to load teams">
          {error?.message || "An error occurred while fetching teams."}
          <div className="mt-2">
            <Button size="sm" variant="outline" onClick={() => refetch()}>
              Retry
            </Button>
          </div>
        </Alert>
      )}

      {isLoading && (
        <div className="space-y-3">
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-12 w-full" />
        </div>
      )}

      {!isLoading && !isError && teams?.length === 0 && (
        <EmptyState
          icon={<Users className="w-8 h-8 text-slate-400" />}
          title="No teams created yet"
          description="Create functional or agile project teams to group members."
          actionLabel="Create Team"
          onAction={() => setIsModalOpen(true)}
        />
      )}

      {!isLoading && !isError && teams && teams.length > 0 && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Code</TableHead>
                <TableHead>Team Name</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {teams.map((t: Team) => (
                <TableRow key={t.id}>
                  <TableCell className="font-mono text-xs font-semibold text-brand-400">
                    {t.code}
                  </TableCell>
                  <TableCell className="font-medium text-slate-100">{t.name}</TableCell>
                  <TableCell className="text-slate-400 text-xs">{t.description || "—"}</TableCell>
                  <TableCell>
                    <Badge variant={t.is_active ? "success" : "danger"}>
                      {t.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-xs gap-1 text-slate-300"
                        onClick={() => setActiveTeamIdForMembers(t.id)}
                      >
                        <Users className="w-3.5 h-3.5" /> Members
                      </Button>
                      <RequirePermission permission="organization:teams:write">
                        <button
                          onClick={() => handleDelete(t.id)}
                          className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded-lg transition-colors"
                          title="Delete Team"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </RequirePermission>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      {/* Create Team Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Create Team"
        description="Register a new agile or functional team."
      >
        {formError && (
          <div className="mb-4">
            <Alert variant="error">{formError}</Alert>
          </div>
        )}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Team Code"
            placeholder="e.g. AI-PLATFORM"
            required
            {...register("code")}
            error={errors.code?.message}
          />
          <Input
            label="Team Name"
            placeholder="e.g. AI Platform Squad"
            required
            {...register("name")}
            error={errors.name?.message}
          />
          <Select label="Department (Optional)" {...register("department_id")}>
            <option value="">None (Independent Team)</option>
            {departments?.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name} ({d.code})
              </option>
            ))}
          </Select>
          <Textarea
            label="Description"
            placeholder="Team mandate, roadmap, and scope..."
            {...register("description")}
          />
          <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
            <Button type="button" variant="ghost" size="sm" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="sm" isLoading={isSubmitting}>
              Create Team
            </Button>
          </div>
        </form>
      </Modal>

      {/* Team Roster Modal */}
      <Modal
        isOpen={!!activeTeamIdForMembers}
        onClose={() => setActiveTeamIdForMembers(null)}
        title="Team Roster"
        description="Manage members and role assignments for this team."
        maxWidth="lg"
      >
        <div className="space-y-4">
          <form onSubmit={handleAddMember} className="flex gap-2">
            <Input
              placeholder="User ID (UUID)"
              value={memberUserId}
              onChange={(e) => setMemberUserId(e.target.value)}
              required
              className="flex-1"
            />
            <Select
              value={memberRole}
              onChange={(e) => setMemberRole(e.target.value)}
              className="w-36"
            >
              <option value="LEAD">Team Lead</option>
              <option value="MEMBER">Member</option>
              <option value="CONTRIBUTOR">Contributor</option>
            </Select>
            <Button type="submit" size="sm" variant="primary" className="shrink-0 gap-1">
              <UserPlus className="w-3.5 h-3.5" /> Add
            </Button>
          </form>

          {lMembers && <Skeleton className="h-24 w-full" />}

          {!lMembers && members && members.length === 0 && (
            <div className="text-center py-6 text-xs text-slate-400">
              No members assigned to this team yet.
            </div>
          )}

          {!lMembers && members && members.length > 0 && (
            <div className="divide-y divide-slate-800 border border-slate-800 rounded-lg overflow-hidden">
              {members.map((m) => (
                <div key={m.id} className="p-3 flex items-center justify-between text-xs">
                  <div className="font-mono text-slate-300">{m.user_id}</div>
                  <Badge variant="info">{m.role}</Badge>
                </div>
              ))}
            </div>
          )}
        </div>
      </Modal>
    </div>
  );
};
