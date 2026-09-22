import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  useCostCenters,
  useCreateCostCenter,
  useDeleteCostCenter,
  useDepartments,
} from "../api/queries";
import { costCenterSchema } from "../schemas/organization.schemas";
import { CostCenter } from "../types/organization.types";
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
import { formatCurrency } from "@/lib/utils";
import { DollarSign, Plus, Trash2 } from "lucide-react";

type CostCenterFormData = z.infer<typeof costCenterSchema>;

export const CostCentersPage: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const { data: costCenters, isLoading, isError, error, refetch } = useCostCenters();
  const { data: departments } = useDepartments();
  const createMutation = useCreateCostCenter();
  const deleteMutation = useDeleteCostCenter();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<CostCenterFormData>({
    resolver: zodResolver(costCenterSchema),
    defaultValues: {
      code: "",
      name: "",
      description: "",
      department_id: "",
      annual_budget: 0,
      currency: "USD",
      is_active: true,
    },
  });

  const onSubmit = async (data: CostCenterFormData) => {
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
      setFormError(err.message || "Failed to create cost center");
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm("Are you sure you want to delete this cost center?")) {
      try {
        await deleteMutation.mutateAsync(id);
      } catch (err: any) {
        alert(err.message || "Failed to delete cost center");
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <DollarSign className="w-5 h-5 text-emerald-400" /> Cost Centers & Budgets
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Financial tracking units, departmental budget allocations, and spending controls.
          </p>
        </div>
        <RequirePermission permission="organization:cost_centers:write">
          <Button onClick={() => setIsModalOpen(true)} className="gap-2 text-xs">
            <Plus className="w-4 h-4" /> Add Cost Center
          </Button>
        </RequirePermission>
      </div>

      {isError && (
        <Alert variant="error" title="Failed to load cost centers">
          {error?.message || "An error occurred while fetching cost centers."}
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

      {!isLoading && !isError && costCenters?.length === 0 && (
        <EmptyState
          icon={<DollarSign className="w-8 h-8 text-slate-400" />}
          title="No cost centers registered"
          description="Create cost centers to allocate budgets and manage organizational expenditure."
          actionLabel="Create Cost Center"
          onAction={() => setIsModalOpen(true)}
        />
      )}

      {!isLoading && !isError && costCenters && costCenters.length > 0 && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Code</TableHead>
                <TableHead>Cost Center Name</TableHead>
                <TableHead>Annual Budget</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {costCenters.map((c: CostCenter) => (
                <TableRow key={c.id}>
                  <TableCell className="font-mono text-xs font-semibold text-brand-400">
                    {c.code}
                  </TableCell>
                  <TableCell className="font-medium text-slate-100">{c.name}</TableCell>
                  <TableCell className="font-mono text-sm font-semibold text-emerald-400">
                    {formatCurrency(c.annual_budget, c.currency)}
                  </TableCell>
                  <TableCell>
                    <Badge variant={c.is_active ? "success" : "danger"}>
                      {c.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <RequirePermission permission="organization:cost_centers:write">
                      <button
                        onClick={() => handleDelete(c.id)}
                        className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded-lg transition-colors"
                        title="Delete Cost Center"
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
        title="Add Cost Center"
        description="Allocate an annual budget tracking center for a department or team."
      >
        {formError && (
          <div className="mb-4">
            <Alert variant="error">{formError}</Alert>
          </div>
        )}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Cost Center Code"
              placeholder="e.g. CC-ENG-01"
              required
              {...register("code")}
              error={errors.code?.message}
            />
            <Input
              label="Cost Center Name"
              placeholder="e.g. Core Engineering R&D"
              required
              {...register("name")}
              error={errors.name?.message}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Annual Budget ($)"
              type="number"
              step="1000"
              placeholder="500000"
              required
              {...register("annual_budget")}
              error={errors.annual_budget?.message}
            />
            <Select label="Department (Optional)" {...register("department_id")}>
              <option value="">None (General)</option>
              {departments?.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name} ({d.code})
                </option>
              ))}
            </Select>
          </div>

          <Textarea
            label="Description"
            placeholder="Budget mandate, expense policies..."
            {...register("description")}
          />

          <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
            <Button type="button" variant="ghost" size="sm" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="sm" isLoading={isSubmitting}>
              Create Cost Center
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
