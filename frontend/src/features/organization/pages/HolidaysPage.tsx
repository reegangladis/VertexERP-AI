import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useHolidays, useCreateHoliday, useDeleteHoliday } from "../api/queries";
import { holidaySchema } from "../schemas/organization.schemas";
import { Holiday } from "../types/organization.types";
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
import { formatDate } from "@/lib/utils";
import { Sun, Plus, Trash2 } from "lucide-react";

type HolidayFormData = z.infer<typeof holidaySchema>;

export const HolidaysPage: React.FC = () => {
  const [selectedYear, setSelectedYear] = useState<number>(new Date().getFullYear());
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const { data: holidays, isLoading, isError, error, refetch } = useHolidays(selectedYear);
  const createMutation = useCreateHoliday();
  const deleteMutation = useDeleteHoliday();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<HolidayFormData>({
    resolver: zodResolver(holidaySchema),
    defaultValues: {
      name: "",
      holiday_date: `${selectedYear}-01-01`,
      holiday_type: "NATIONAL",
      is_recurring: false,
      description: "",
    },
  });

  const onSubmit = async (data: HolidayFormData) => {
    setFormError(null);
    try {
      await createMutation.mutateAsync(data);
      reset();
      setIsModalOpen(false);
    } catch (err: any) {
      setFormError(err.message || "Failed to create holiday");
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm("Are you sure you want to delete this holiday?")) {
      try {
        await deleteMutation.mutateAsync(id);
      } catch (err: any) {
        alert(err.message || "Failed to delete holiday");
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Sun className="w-5 h-5 text-yellow-400" /> Organization Holidays
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Configure observed national, regional, and company holidays.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Select
            value={selectedYear}
            onChange={(e) => setSelectedYear(parseInt(e.target.value))}
            className="w-32 text-xs py-1.5"
          >
            <option value={2025}>2025</option>
            <option value={2026}>2026</option>
            <option value={2027}>2027</option>
          </Select>

          <RequirePermission permission="organization:holidays:write">
            <Button onClick={() => setIsModalOpen(true)} className="gap-2 text-xs">
              <Plus className="w-4 h-4" /> Add Holiday
            </Button>
          </RequirePermission>
        </div>
      </div>

      {isError && (
        <Alert variant="error" title="Failed to load holidays">
          {error?.message || "An error occurred while fetching holidays."}
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

      {!isLoading && !isError && holidays?.length === 0 && (
        <EmptyState
          icon={<Sun className="w-8 h-8 text-slate-400" />}
          title={`No holidays configured for ${selectedYear}`}
          description="Add national or corporate observed non-working holidays."
          actionLabel="Create Holiday"
          onAction={() => setIsModalOpen(true)}
        />
      )}

      {!isLoading && !isError && holidays && holidays.length > 0 && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Observed Date</TableHead>
                <TableHead>Holiday Name</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Recurrence</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {holidays.map((h: Holiday) => (
                <TableRow key={h.id}>
                  <TableCell className="font-mono text-xs font-semibold text-brand-400">
                    {formatDate(h.holiday_date)}
                  </TableCell>
                  <TableCell className="font-medium text-slate-100">{h.name}</TableCell>
                  <TableCell>
                    <Badge variant="info">{h.holiday_type}</Badge>
                  </TableCell>
                  <TableCell className="text-slate-400 text-xs">
                    {h.is_recurring ? "Yearly Recurring" : "One-Time"}
                  </TableCell>
                  <TableCell className="text-right">
                    <RequirePermission permission="organization:holidays:write">
                      <button
                        onClick={() => handleDelete(h.id)}
                        className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded-lg transition-colors"
                        title="Delete Holiday"
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
        title="Add Company Holiday"
        description="Register a national or corporate observed holiday."
      >
        {formError && (
          <div className="mb-4">
            <Alert variant="error">{formError}</Alert>
          </div>
        )}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Holiday Name"
            placeholder="e.g. New Year's Day"
            required
            {...register("name")}
            error={errors.name?.message}
          />

          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Observed Date (YYYY-MM-DD)"
              type="date"
              required
              {...register("holiday_date")}
              error={errors.holiday_date?.message}
            />

            <Select label="Holiday Type" {...register("holiday_type")}>
              <option value="NATIONAL">National Holiday</option>
              <option value="REGIONAL">Regional Holiday</option>
              <option value="COMPANY">Company Holiday</option>
              <option value="OPTIONAL">Optional / Floating Holiday</option>
            </Select>
          </div>

          <Textarea
            label="Description (Optional)"
            placeholder="Observance details..."
            {...register("description")}
          />

          <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer pt-2">
            <input
              type="checkbox"
              className="rounded bg-slate-950 border-slate-700 text-brand-600 focus:ring-brand-500"
              {...register("is_recurring")}
            />
            Yearly Recurring Holiday
          </label>

          <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
            <Button type="button" variant="ghost" size="sm" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="sm" isLoading={isSubmitting}>
              Create Holiday
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
