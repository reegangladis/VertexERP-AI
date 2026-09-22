import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useBusinessUnits, useCreateBusinessUnit, useDeleteBusinessUnit } from "../api/queries";
import { businessUnitSchema } from "../schemas/organization.schemas";
import { BusinessUnit } from "../types/organization.types";
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
import { Layers, Plus, Trash2 } from "lucide-react";

type BUFormData = z.infer<typeof businessUnitSchema>;

export const BusinessUnitsPage: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const { data: bus, isLoading, isError, error, refetch } = useBusinessUnits();
  const createMutation = useCreateBusinessUnit();
  const deleteMutation = useDeleteBusinessUnit();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<BUFormData>({
    resolver: zodResolver(businessUnitSchema),
    defaultValues: {
      code: "",
      name: "",
      description: "",
      is_active: true,
    },
  });

  const onSubmit = async (data: BUFormData) => {
    setFormError(null);
    try {
      await createMutation.mutateAsync(data);
      reset();
      setIsModalOpen(false);
    } catch (err: any) {
      setFormError(err.message || "Failed to create business unit");
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm("Are you sure you want to delete this business unit?")) {
      try {
        await deleteMutation.mutateAsync(id);
      } catch (err: any) {
        alert(err.message || "Failed to delete business unit");
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Layers className="w-5 h-5 text-purple-400" /> Strategic Business Units (SBUs)
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Manage high-level enterprise business units, commercial divisions, and product lines.
          </p>
        </div>
        <RequirePermission permission="organization:business_units:write">
          <Button onClick={() => setIsModalOpen(true)} className="gap-2 text-xs">
            <Plus className="w-4 h-4" /> Add Business Unit
          </Button>
        </RequirePermission>
      </div>

      {isError && (
        <Alert variant="error" title="Failed to load business units">
          {error?.message || "An error occurred while fetching business units."}
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

      {!isLoading && !isError && bus?.length === 0 && (
        <EmptyState
          icon={<Layers className="w-8 h-8 text-slate-400" />}
          title="No business units created"
          description="Create strategic business divisions to organize your commercial operations."
          actionLabel="Create Business Unit"
          onAction={() => setIsModalOpen(true)}
        />
      )}

      {!isLoading && !isError && bus && bus.length > 0 && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Code</TableHead>
                <TableHead>Business Unit Name</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {bus.map((b: BusinessUnit) => (
                <TableRow key={b.id}>
                  <TableCell className="font-mono text-xs font-semibold text-brand-400">
                    {b.code}
                  </TableCell>
                  <TableCell className="font-medium text-slate-100">{b.name}</TableCell>
                  <TableCell className="text-slate-400 text-xs">{b.description || "—"}</TableCell>
                  <TableCell>
                    <Badge variant={b.is_active ? "success" : "danger"}>
                      {b.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <RequirePermission permission="organization:business_units:write">
                      <button
                        onClick={() => handleDelete(b.id)}
                        className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded-lg transition-colors"
                        title="Delete Business Unit"
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
        title="Create Strategic Business Unit"
        description="Register a new strategic division or business line."
      >
        {formError && (
          <div className="mb-4">
            <Alert variant="error">{formError}</Alert>
          </div>
        )}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Business Unit Code"
            placeholder="e.g. BU-ENTERPRISE"
            required
            {...register("code")}
            error={errors.code?.message}
          />
          <Input
            label="Business Unit Name"
            placeholder="e.g. Enterprise Solutions & AI"
            required
            {...register("name")}
            error={errors.name?.message}
          />
          <Textarea
            label="Description"
            placeholder="Scope of operations, strategic mandate..."
            {...register("description")}
          />
          <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
            <Button type="button" variant="ghost" size="sm" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="sm" isLoading={isSubmitting}>
              Create Business Unit
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
