import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  useCalendars,
  useCalendarDetails,
  useCreateCalendar,
  useDeleteCalendar,
} from "../api/queries";
import { workCalendarSchema } from "../schemas/organization.schemas";
import { WorkCalendar, WorkingDay } from "../types/organization.types";
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
import { Calendar, Plus, Trash2, Clock, Check, X as XIcon } from "lucide-react";

type CalendarFormData = z.infer<typeof workCalendarSchema>;

const DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

export const CalendarsPage: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedCalendarId, setSelectedCalendarId] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  const { data: calendars, isLoading, isError, error, refetch } = useCalendars();
  const { data: calendarDetails, isLoading: lDetails } = useCalendarDetails(selectedCalendarId || "");
  const createMutation = useCreateCalendar();
  const deleteMutation = useDeleteCalendar();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<CalendarFormData>({
    resolver: zodResolver(workCalendarSchema),
    defaultValues: {
      code: "",
      name: "",
      description: "",
      time_zone: "America/New_York",
      is_default: false,
      standard_hours_per_day: 8,
      is_active: true,
    },
  });

  const onSubmit = async (data: CalendarFormData) => {
    setFormError(null);
    try {
      await createMutation.mutateAsync(data);
      reset();
      setIsModalOpen(false);
    } catch (err: any) {
      setFormError(err.message || "Failed to create calendar");
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm("Are you sure you want to delete this work calendar?")) {
      try {
        await deleteMutation.mutateAsync(id);
      } catch (err: any) {
        alert(err.message || "Failed to delete calendar");
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Calendar className="w-5 h-5 text-cyan-400" /> Work Calendars & Shifts
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Configure working day schedules, shift operating hours, and standard timezone profiles.
          </p>
        </div>
        <RequirePermission permission="organization:calendars:write">
          <Button onClick={() => setIsModalOpen(true)} className="gap-2 text-xs">
            <Plus className="w-4 h-4" /> Add Work Calendar
          </Button>
        </RequirePermission>
      </div>

      {isError && (
        <Alert variant="error" title="Failed to load calendars">
          {error?.message || "An error occurred while fetching work calendars."}
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

      {!isLoading && !isError && calendars?.length === 0 && (
        <EmptyState
          icon={<Calendar className="w-8 h-8 text-slate-400" />}
          title="No work calendars created"
          description="Create standard 40-hour work schedules or regional shift calendars."
          actionLabel="Create Calendar"
          onAction={() => setIsModalOpen(true)}
        />
      )}

      {!isLoading && !isError && calendars && calendars.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {calendars.map((cal: WorkCalendar) => (
            <div
              key={cal.id}
              className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-all space-y-4"
            >
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-slate-100">{cal.name}</span>
                    {cal.is_default && <Badge variant="info">Default</Badge>}
                  </div>
                  <div className="font-mono text-xs text-brand-400 mt-0.5">{cal.code}</div>
                </div>
                <RequirePermission permission="organization:calendars:write">
                  <button
                    onClick={() => handleDelete(cal.id)}
                    className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded-lg transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </RequirePermission>
              </div>

              <div className="space-y-1 text-xs text-slate-400 border-t border-slate-800/80 pt-3">
                <div className="flex justify-between">
                  <span>Timezone:</span>
                  <span className="text-slate-200 font-medium">{cal.time_zone}</span>
                </div>
                <div className="flex justify-between">
                  <span>Standard Hours/Day:</span>
                  <span className="text-slate-200 font-medium">{cal.standard_hours_per_day} hrs</span>
                </div>
              </div>

              <Button
                variant="secondary"
                size="sm"
                className="w-full text-xs gap-1.5"
                onClick={() => setSelectedCalendarId(cal.id)}
              >
                <Clock className="w-3.5 h-3.5" /> View Working Days Schedule
              </Button>
            </div>
          ))}
        </div>
      )}

      {/* View Working Days Schedule Modal */}
      <Modal
        isOpen={!!selectedCalendarId}
        onClose={() => setSelectedCalendarId(null)}
        title="Weekly Working Days Schedule"
        description={calendarDetails ? `${calendarDetails.name} (${calendarDetails.time_zone})` : ""}
        maxWidth="md"
      >
        {lDetails ? (
          <Skeleton className="h-48 w-full" />
        ) : (
          <div className="space-y-2">
            {calendarDetails?.working_days?.map((wd: WorkingDay) => (
              <div
                key={wd.id}
                className="flex items-center justify-between p-3 rounded-lg bg-slate-950/60 border border-slate-800 text-xs"
              >
                <span className="font-medium text-slate-200">{DAYS_OF_WEEK[wd.day_of_week]}</span>
                <div className="flex items-center gap-3">
                  {wd.is_working_day ? (
                    <span className="text-slate-400">
                      {wd.start_time} — {wd.end_time}
                    </span>
                  ) : (
                    <span className="text-slate-500 italic">Off Day</span>
                  )}
                  <Badge variant={wd.is_working_day ? "success" : "neutral"}>
                    {wd.is_working_day ? "Working" : "Weekend"}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        )}
      </Modal>

      {/* Create Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Create Work Calendar"
        description="Configure a new work schedule calendar with standard working hours."
      >
        {formError && (
          <div className="mb-4">
            <Alert variant="error">{formError}</Alert>
          </div>
        )}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Calendar Code"
            placeholder="e.g. CAL-US-STD"
            required
            {...register("code")}
            error={errors.code?.message}
          />
          <Input
            label="Calendar Name"
            placeholder="e.g. US Standard 40hr Schedule"
            required
            {...register("name")}
            error={errors.name?.message}
          />
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Timezone"
              placeholder="e.g. America/New_York"
              required
              {...register("time_zone")}
              error={errors.time_zone?.message}
            />
            <Input
              label="Standard Hours/Day"
              type="number"
              step="0.5"
              placeholder="8"
              required
              {...register("standard_hours_per_day")}
              error={errors.standard_hours_per_day?.message}
            />
          </div>
          <Textarea
            label="Description"
            placeholder="Shift notes, applicability..."
            {...register("description")}
          />
          <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer pt-2">
            <input
              type="checkbox"
              className="rounded bg-slate-950 border-slate-700 text-brand-600 focus:ring-brand-500"
              {...register("is_default")}
            />
            Set as Default Calendar for Tenant
          </label>
          <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
            <Button type="button" variant="ghost" size="sm" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="sm" isLoading={isSubmitting}>
              Create Calendar
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
