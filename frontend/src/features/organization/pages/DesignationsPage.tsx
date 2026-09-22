import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useDesignations, useCreateDesignation, useDeleteDesignation } from "../api/queries";
import { designationSchema } from "../schemas/organization.schemas";
import { Designation } from "../types/organization.types";
import { z } from "zod";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Textarea } from "@/components/ui/Textarea";
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
import { Award, Plus, Trash2 } from "lucide-react";

type DesignationFormData = z.infer<typeof designationSchema>;

export const DesignationsPage: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const { data: designations, isLoading, isError, error, refetch } = useDesignations();
  const createMutation = useCreateDesignation();
  const deleteMutation = useDeleteDesignation();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<DesignationFormData>({
    resolver: zodResolver(designationSchema),
    defaultValues: {
      code: "",
      name: "",
      description: "",
      level: 1,
      is_active: true,
    },
  });

  const onSubmit = async (data: DesignationFormData) => {
    setFormError(null);
    try {
      await createMutation.mutateAsync(data);
      reset();
      setIsModalOpen(false);
    } catch (err: any) {
      setFormError(err.message || "Failed to create designation");
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm("Are you sure you want to delete this designation?")) {
      try {
        await deleteMutation.mutateAsync(id);
      } catch (err: any) {
        alert(err.message || "Failed to delete designation");
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Award className="w-5 h-5 text-amber-400" /> Job Designations & Titles
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Configure job title classifications, career ladders, and level rankings (1-100).
          </p>
        </div>
        <RequirePermission permission="organization:designations:write">
          <Button onClick={() => setIsModalOpen(true)} className="gap-2 text-xs">
            <Plus className="w-4 h-4" /> Add Designation
          </Button>
        </RequirePermission>
      </div>

      {isError && (
        <Alert variant="error" title="Failed to load designations">
          {error?.message || "An error occurred while fetching designations."}
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

      {!isLoading && !isError && designations?.length === 0 && (
        <EmptyState
          icon={<Award className="w-8 h-8 text-slate-400" />}
          title="No designations defined"
          description="Create role titles such as Staff Engineer, Product Manager, or VP."
          actionLabel="Create Designation"
          onAction={() => setIsModalOpen(true)}
        />
      )}

      {!isLoading && !isError && designations && designations.length > 0 && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Level</TableHead>
                <TableHead>Code</TableHead>
                <TableHead>Title</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {designations.map((d: Designation) => (
                <TableRow key={d.id}>
                  <TableCell>
                    <Badge variant="info">Level {d.level}</Badge>
                  </TableCell>
                  <TableCell className="font-mono text-xs font-semibold text-brand-400">
                    {d.code}
                  </TableCell>
                  <TableCell className="font-medium text-slate-100">{d.name}</TableCell>
                  <TableCell className="text-slate-400 text-xs">{d.description || "—"}</TableCell>
                  <TableCell>
                    <Badge variant={d.is_active ? "success" : "danger"}>
                      {d.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <RequirePermission permission="organization:designations:write">
                      <button
                        onClick={() => handleDelete(d.id)}
                        className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded-lg transition-colors"
                        title="Delete Designation"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </RequirePermission>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      {/* Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Create Job Designation"
        description="Define a new organizational job title and ranking level."
      >
        {formError && (
          <div className="mb-4">
            <Alert variant="error">{formError}</Alert>
          </div>
        )}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="grid grid-cols-3 gap-3">
            <div className="col-span-2">
              <Input
                label="Designation Code"
                placeholder="e.g. SE-II"
                required
                {...register("code")}
                error={errors.code?.message}
              />
            </div>
            <Input
              label="Level (1-100)"
              type="number"
              min={1}
              max={100}
              required
              {...register("level")}
              error={errors.level?.message}
            />
          </div>
          <Input
            label="Designation Title"
            placeholder="e.g. Senior Software Engineer"
            required
            {...register("name")}
            error={errors.name?.message}
          />
          <Textarea
            label="Description"
            placeholder="Core competencies and scope..."
            {...register("description")}
          />
          <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
            <Button type="button" variant="ghost" size="sm" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="sm" isLoading={isSubmitting}>
              Create Designation
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
