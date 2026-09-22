import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useBranches, useCreateBranch, useDeleteBranch } from "../api/queries";
import { branchSchema } from "../schemas/organization.schemas";
import { Branch } from "../types/organization.types";
import { z } from "zod";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
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
import { Building2, Plus, Trash2 } from "lucide-react";

type BranchFormData = z.infer<typeof branchSchema>;

export const BranchesPage: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const { data: branches, isLoading, isError, error, refetch } = useBranches();
  const createMutation = useCreateBranch();
  const deleteMutation = useDeleteBranch();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<BranchFormData>({
    resolver: zodResolver(branchSchema),
    defaultValues: {
      code: "",
      name: "",
      address_line1: "",
      city: "",
      state: "",
      postal_code: "",
      country: "USA",
      is_headquarters: false,
      is_active: true,
    },
  });

  const onSubmit = async (data: BranchFormData) => {
    setFormError(null);
    try {
      await createMutation.mutateAsync(data);
      reset();
      setIsModalOpen(false);
    } catch (err: any) {
      setFormError(err.message || "Failed to create branch");
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm("Are you sure you want to delete this branch?")) {
      try {
        await deleteMutation.mutateAsync(id);
      } catch (err: any) {
        alert(err.message || "Failed to delete branch");
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Building2 className="w-5 h-5 text-brand-400" /> Physical Branches
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Manage company branch offices, headquarters, and location infrastructure.
          </p>
        </div>
        <RequirePermission permission="organization:branches:write">
          <Button onClick={() => setIsModalOpen(true)} className="gap-2 text-xs">
            <Plus className="w-4 h-4" /> Add Branch
          </Button>
        </RequirePermission>
      </div>

      {/* Error State */}
      {isError && (
        <Alert variant="error" title="Failed to load branches">
          {error?.message || "An error occurred while fetching branch records."}
          <div className="mt-2">
            <Button size="sm" variant="outline" onClick={() => refetch()}>
              Retry
            </Button>
          </div>
        </Alert>
      )}

      {/* Loading Skeleton */}
      {isLoading && (
        <div className="space-y-3">
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-12 w-full" />
        </div>
      )}

      {/* Empty State */}
      {!isLoading && !isError && branches?.length === 0 && (
        <EmptyState
          icon={<Building2 className="w-8 h-8 text-slate-400" />}
          title="No branches registered"
          description="Get started by creating your first organizational branch or office location."
          actionLabel="Create Branch"
          onAction={() => setIsModalOpen(true)}
        />
      )}

      {/* Data Table */}
      {!isLoading && !isError && branches && branches.length > 0 && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Code</TableHead>
                <TableHead>Branch Name</TableHead>
                <TableHead>Location</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {branches.map((b: Branch) => (
                <TableRow key={b.id}>
                  <TableCell className="font-mono text-xs font-semibold text-brand-400">
                    {b.code}
                  </TableCell>
                  <TableCell className="font-medium text-slate-100">{b.name}</TableCell>
                  <TableCell className="text-slate-400">
                    {b.city}, {b.state} ({b.country})
                  </TableCell>
                  <TableCell>
                    {b.is_headquarters ? (
                      <Badge variant="info">HQ</Badge>
                    ) : (
                      <Badge variant="neutral">Branch</Badge>
                    )}
                  </TableCell>
                  <TableCell>
                    <Badge variant={b.is_active ? "success" : "danger"}>
                      {b.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <RequirePermission permission="organization:branches:write">
                      <button
                        onClick={() => handleDelete(b.id)}
                        className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded-lg transition-colors"
                        title="Delete Branch"
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

      {/* Create Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Add Physical Branch"
        description="Register a new branch or office site under this organization."
        maxWidth="lg"
      >
        {formError && (
          <div className="mb-4">
            <Alert variant="error">{formError}</Alert>
          </div>
        )}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Branch Code"
              placeholder="e.g. BR-NYC"
              required
              {...register("code")}
              error={errors.code?.message}
            />
            <Input
              label="Branch Name"
              placeholder="e.g. New York Headquarters"
              required
              {...register("name")}
              error={errors.name?.message}
            />
          </div>

          <Input
            label="Street Address"
            placeholder="e.g. 100 Broadway, Suite 400"
            required
            {...register("address_line1")}
            error={errors.address_line1?.message}
          />

          <div className="grid grid-cols-3 gap-3">
            <Input
              label="City"
              placeholder="New York"
              required
              {...register("city")}
              error={errors.city?.message}
            />
            <Input
              label="State"
              placeholder="NY"
              required
              {...register("state")}
              error={errors.state?.message}
            />
            <Input
              label="Postal Code"
              placeholder="10005"
              required
              {...register("postal_code")}
              error={errors.postal_code?.message}
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Phone"
              placeholder="+1-212-555-0100"
              {...register("phone")}
              error={errors.phone?.message}
            />
            <Input
              label="Email"
              placeholder="branch@company.com"
              {...register("email")}
              error={errors.email?.message}
            />
          </div>

          <div className="flex items-center gap-4 pt-2">
            <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
              <input
                type="checkbox"
                className="rounded bg-slate-950 border-slate-700 text-brand-600 focus:ring-brand-500"
                {...register("is_headquarters")}
              />
              Headquarters Flag
            </label>
            <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
              <input
                type="checkbox"
                className="rounded bg-slate-950 border-slate-700 text-brand-600 focus:ring-brand-500"
                {...register("is_active")}
              />
              Active
            </label>
          </div>

          <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => setIsModalOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="sm" isLoading={isSubmitting}>
              Create Branch
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
