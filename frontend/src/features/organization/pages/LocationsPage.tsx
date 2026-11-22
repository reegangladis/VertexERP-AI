import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  useLocations,
  useCreateLocation,
  useDeleteLocation,
  useBranches,
} from "../api/queries";
import { locationSchema } from "../schemas/organization.schemas";
import { Location } from "../types/organization.types";
import { z } from "zod";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
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
import { MapPin, Plus, Trash2 } from "lucide-react";

type LocationFormData = z.infer<typeof locationSchema>;

export const LocationsPage: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const { data: locations, isLoading, isError, error, refetch } = useLocations();
  const { data: branches } = useBranches();
  const createMutation = useCreateLocation();
  const deleteMutation = useDeleteLocation();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<LocationFormData>({
    resolver: zodResolver(locationSchema),
    defaultValues: {
      code: "",
      name: "",
      location_type: "OFFICE",
      address_line1: "",
      city: "",
      state: "",
      postal_code: "",
      country: "USA",
      is_active: true,
    },
  });

  const onSubmit = async (data: LocationFormData) => {
    setFormError(null);
    try {
      await createMutation.mutateAsync(data);
      reset();
      setIsModalOpen(false);
    } catch (err: any) {
      setFormError(err.message || "Failed to create location");
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm("Are you sure you want to delete this facility location?")) {
      try {
        await deleteMutation.mutateAsync(id);
      } catch (err: any) {
        alert(err.message || "Failed to delete location");
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <MapPin className="w-5 h-5 text-rose-400" /> Physical Sites & Facility Locations
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Manage warehouses, data centers, manufacturing plants, and branch office sites.
          </p>
        </div>
        <RequirePermission permission="organization:locations:write">
          <Button onClick={() => setIsModalOpen(true)} className="gap-2 text-xs">
            <Plus className="w-4 h-4" /> Add Location
          </Button>
        </RequirePermission>
      </div>

      {isError && (
        <Alert variant="error" title="Failed to load locations">
          {error?.message || "An error occurred while fetching locations."}
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

      {!isLoading && !isError && locations?.length === 0 && (
        <EmptyState
          icon={<MapPin className="w-8 h-8 text-slate-400" />}
          title="No locations registered"
          description="Register physical facilities, fulfillment hubs, or regional offices."
          actionLabel="Create Location"
          onAction={() => setIsModalOpen(true)}
        />
      )}

      {!isLoading && !isError && locations && locations.length > 0 && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Code</TableHead>
                <TableHead>Location Name</TableHead>
                <TableHead>Facility Type</TableHead>
                <TableHead>City / Region</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {locations.map((l: Location) => (
                <TableRow key={l.id}>
                  <TableCell className="font-mono text-xs font-semibold text-brand-400">
                    {l.code}
                  </TableCell>
                  <TableCell className="font-medium text-slate-100">{l.name}</TableCell>
                  <TableCell>
                    <Badge variant="info">{l.location_type}</Badge>
                  </TableCell>
                  <TableCell className="text-slate-400 text-xs">
                    {l.city}, {l.state} ({l.country})
                  </TableCell>
                  <TableCell>
                    <Badge variant={l.is_active ? "success" : "danger"}>
                      {l.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <RequirePermission permission="organization:locations:write">
                      <button
                        onClick={() => handleDelete(l.id)}
                        className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded-lg transition-colors"
                        title="Delete Location"
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
        title="Add Facility Location"
        description="Register a new site, warehouse, plant, or store."
        maxWidth="lg"
      >
        {formError && (
          <div className="mb-4">
            <Alert variant="error">{formError}</Alert>
          </div>
        )}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Location Code"
              placeholder="e.g. LOC-WH-01"
              required
              {...register("code")}
              error={errors.code?.message}
            />
            <Input
              label="Location Name"
              placeholder="e.g. Austin Fulfillment Center"
              required
              {...register("name")}
              error={errors.name?.message}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Select label="Facility Type" {...register("location_type")}>
              <option value="OFFICE">Office</option>
              <option value="WAREHOUSE">Warehouse</option>
              <option value="PLANT">Manufacturing Plant</option>
              <option value="STORE">Retail Store</option>
              <option value="DATACENTER">Data Center</option>
            </Select>

            <Input
              label="Street Address"
              placeholder="500 Innovation Way"
              required
              {...register("address_line1")}
              error={errors.address_line1?.message}
            />
          </div>

          <div className="grid grid-cols-3 gap-3">
            <Input
              label="City"
              placeholder="Austin"
              required
              {...register("city")}
              error={errors.city?.message}
            />
            <Input
              label="State"
              placeholder="TX"
              required
              {...register("state")}
              error={errors.state?.message}
            />
            <Input
              label="Postal Code"
              placeholder="78701"
              required
              {...register("postal_code")}
              error={errors.postal_code?.message}
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Latitude (Optional)"
              type="number"
              step="any"
              placeholder="30.2672"
              {...register("latitude")}
            />
            <Input
              label="Longitude (Optional)"
              type="number"
              step="any"
              placeholder="-97.7431"
              {...register("longitude")}
            />
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
            <Button type="button" variant="ghost" size="sm" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="sm" isLoading={isSubmitting}>
              Create Location
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
