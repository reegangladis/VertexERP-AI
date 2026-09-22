import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  useDepartments,
  useDepartmentTree,
  useCreateDepartment,
  useDeleteDepartment,
} from "../api/queries";
import { departmentSchema } from "../schemas/organization.schemas";
import { Department, DepartmentTreeNode } from "../types/organization.types";
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
import { GitFork, Plus, Trash2, ChevronRight, FolderTree } from "lucide-react";

type DepartmentFormData = z.infer<typeof departmentSchema>;

export const DepartmentsPage: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<"table" | "tree">("table");

  const { data: departments, isLoading, isError, error, refetch } = useDepartments();
  const { data: tree } = useDepartmentTree();
  const createMutation = useCreateDepartment();
  const deleteMutation = useDeleteDepartment();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<DepartmentFormData>({
    resolver: zodResolver(departmentSchema),
    defaultValues: {
      code: "",
      name: "",
      description: "",
      parent_department_id: "",
      is_active: true,
    },
  });

  const onSubmit = async (data: DepartmentFormData) => {
    setFormError(null);
    try {
      const payload = {
        ...data,
        parent_department_id: data.parent_department_id || null,
      };
      await createMutation.mutateAsync(payload);
      reset();
      setIsModalOpen(false);
    } catch (err: any) {
      setFormError(err.message || "Failed to create department");
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm("Are you sure you want to delete this department?")) {
      try {
        await deleteMutation.mutateAsync(id);
      } catch (err: any) {
        alert(err.message || "Failed to delete department");
      }
    }
  };

  const renderTreeNodes = (nodes: DepartmentTreeNode[], depth = 0) => {
    return (
      <div className="space-y-2">
        {nodes.map((node) => (
          <div key={node.id} className="space-y-2">
            <div
              className="flex items-center justify-between p-3 rounded-xl bg-slate-900/60 border border-slate-800"
              style={{ marginLeft: `${depth * 24}px` }}
            >
              <div className="flex items-center gap-3">
                <ChevronRight className="w-4 h-4 text-brand-400 shrink-0" />
                <div>
                  <div className="text-sm font-semibold text-slate-100 flex items-center gap-2">
                    {node.name}
                    <span className="text-[10px] font-mono text-brand-400 bg-brand-500/10 px-1.5 py-0.5 rounded border border-brand-500/20">
                      {node.code}
                    </span>
                  </div>
                  {node.description && (
                    <div className="text-xs text-slate-400">{node.description}</div>
                  )}
                </div>
              </div>
              <Badge variant={node.is_active ? "success" : "danger"}>
                {node.is_active ? "Active" : "Inactive"}
              </Badge>
            </div>
            {node.children && node.children.length > 0 && renderTreeNodes(node.children, depth + 1)}
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <GitFork className="w-5 h-5 text-indigo-400" /> Functional Departments
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Organize departments, functional units, and departmental hierarchies.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center bg-slate-900 border border-slate-800 rounded-lg p-1 text-xs">
            <button
              onClick={() => setViewMode("table")}
              className={`px-3 py-1 rounded-md transition-colors ${
                viewMode === "table" ? "bg-slate-800 text-white font-medium" : "text-slate-400"
              }`}
            >
              Table View
            </button>
            <button
              onClick={() => setViewMode("tree")}
              className={`px-3 py-1 rounded-md transition-colors ${
                viewMode === "tree" ? "bg-slate-800 text-white font-medium" : "text-slate-400"
              }`}
            >
              Hierarchy Tree
            </button>
          </div>

          <RequirePermission permission="organization:departments:write">
            <Button onClick={() => setIsModalOpen(true)} className="gap-2 text-xs">
              <Plus className="w-4 h-4" /> Add Department
            </Button>
          </RequirePermission>
        </div>
      </div>

      {/* Error State */}
      {isError && (
        <Alert variant="error" title="Failed to load departments">
          {error?.message || "An error occurred while fetching department records."}
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
      {!isLoading && !isError && departments?.length === 0 && (
        <EmptyState
          icon={<GitFork className="w-8 h-8 text-slate-400" />}
          title="No departments registered"
          description="Create your first department such as Engineering, Sales, or Operations."
          actionLabel="Create Department"
          onAction={() => setIsModalOpen(true)}
        />
      )}

      {/* Data Table View */}
      {!isLoading && !isError && departments && departments.length > 0 && viewMode === "table" && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Code</TableHead>
                <TableHead>Department Name</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {departments.map((d: Department) => (
                <TableRow key={d.id}>
                  <TableCell className="font-mono text-xs font-semibold text-brand-400">
                    {d.code}
                  </TableCell>
                  <TableCell className="font-medium text-slate-100">{d.name}</TableCell>
                  <TableCell className="text-slate-400 text-xs">
                    {d.description || "—"}
                  </TableCell>
                  <TableCell>
                    <Badge variant={d.is_active ? "success" : "danger"}>
                      {d.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <RequirePermission permission="organization:departments:write">
                      <button
                        onClick={() => handleDelete(d.id)}
                        className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded-lg transition-colors"
                        title="Delete Department"
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

      {/* Tree Hierarchy View */}
      {!isLoading && !isError && tree && tree.length > 0 && viewMode === "tree" && (
        <div className="p-4 bg-slate-950/40 border border-slate-800 rounded-xl">
          {renderTreeNodes(tree)}
        </div>
      )}

      {/* Create Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Add Department"
        description="Register a new organizational functional department."
      >
        {formError && (
          <div className="mb-4">
            <Alert variant="error">{formError}</Alert>
          </div>
        )}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Department Code"
            placeholder="e.g. ENG"
            required
            {...register("code")}
            error={errors.code?.message}
          />

          <Input
            label="Department Name"
            placeholder="e.g. Engineering & Technology"
            required
            {...register("name")}
            error={errors.name?.message}
          />

          <Select
            label="Parent Department (Optional)"
            {...register("parent_department_id")}
            error={errors.parent_department_id?.message}
          >
            <option value="">None (Top-Level Department)</option>
            {departments?.map((dept) => (
              <option key={dept.id} value={dept.id}>
                {dept.name} ({dept.code})
              </option>
            ))}
          </Select>

          <Textarea
            label="Description"
            placeholder="Key responsibilities and goals..."
            {...register("description")}
            error={errors.description?.message}
          />

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
              Create Department
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
