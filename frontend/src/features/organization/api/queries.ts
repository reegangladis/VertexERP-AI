import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import {
  Branch,
  BusinessUnit,
  CostCenter,
  Department,
  DepartmentTreeNode,
  Designation,
  Holiday,
  Location,
  Team,
  TeamMember,
  WorkCalendar,
  WorkingDay,
} from "../types/organization.types";

// ========================
// 1. Branches
// ========================
export function useBranches() {
  return useQuery({
    queryKey: ["branches"],
    queryFn: () => apiClient<Branch[]>("/branches/"),
  });
}

export function useCreateBranch() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Branch>) =>
      apiClient<Branch>("/branches/", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["branches"] });
    },
  });
}

export function useDeleteBranch() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) =>
      apiClient<void>(`/branches/${id}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["branches"] });
    },
  });
}

// ========================
// 2. Departments
// ========================
export function useDepartments() {
  return useQuery({
    queryKey: ["departments"],
    queryFn: () => apiClient<Department[]>("/departments/"),
  });
}

export function useDepartmentTree() {
  return useQuery({
    queryKey: ["departments", "tree"],
    queryFn: () => apiClient<DepartmentTreeNode[]>("/departments/tree"),
  });
}

export function useCreateDepartment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Department>) =>
      apiClient<Department>("/departments/", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["departments"] });
    },
  });
}

export function useDeleteDepartment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) =>
      apiClient<void>(`/departments/${id}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["departments"] });
    },
  });
}

// ========================
// 3. Teams
// ========================
export function useTeams() {
  return useQuery({
    queryKey: ["teams"],
    queryFn: () => apiClient<Team[]>("/teams/"),
  });
}

export function useCreateTeam() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Team>) =>
      apiClient<Team>("/teams/", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["teams"] });
    },
  });
}

export function useTeamMembers(teamId: string) {
  return useQuery({
    queryKey: ["teams", teamId, "members"],
    queryFn: () => apiClient<TeamMember[]>(`/teams/${teamId}/members`),
    enabled: !!teamId,
  });
}

export function useAddTeamMember(teamId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { user_id: string; role: string }) =>
      apiClient<TeamMember>(`/teams/${teamId}/members`, {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["teams", teamId, "members"] });
    },
  });
}

export function useDeleteTeam() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) =>
      apiClient<void>(`/teams/${id}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["teams"] });
    },
  });
}

// ========================
// 4. Designations
// ========================
export function useDesignations() {
  return useQuery({
    queryKey: ["designations"],
    queryFn: () => apiClient<Designation[]>("/designations/"),
  });
}

export function useCreateDesignation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Designation>) =>
      apiClient<Designation>("/designations/", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["designations"] });
    },
  });
}

export function useDeleteDesignation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) =>
      apiClient<void>(`/designations/${id}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["designations"] });
    },
  });
}

// ========================
// 5. Business Units
// ========================
export function useBusinessUnits() {
  return useQuery({
    queryKey: ["business-units"],
    queryFn: () => apiClient<BusinessUnit[]>("/business-units/"),
  });
}

export function useCreateBusinessUnit() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<BusinessUnit>) =>
      apiClient<BusinessUnit>("/business-units/", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["business-units"] });
    },
  });
}

export function useDeleteBusinessUnit() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) =>
      apiClient<void>(`/business-units/${id}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["business-units"] });
    },
  });
}

// ========================
// 6. Cost Centers
// ========================
export function useCostCenters() {
  return useQuery({
    queryKey: ["cost-centers"],
    queryFn: () => apiClient<CostCenter[]>("/cost-centers/"),
  });
}

export function useCreateCostCenter() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<CostCenter>) =>
      apiClient<CostCenter>("/cost-centers/", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cost-centers"] });
    },
  });
}

export function useDeleteCostCenter() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) =>
      apiClient<void>(`/cost-centers/${id}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cost-centers"] });
    },
  });
}

// ========================
// 7. Locations
// ========================
export function useLocations() {
  return useQuery({
    queryKey: ["locations"],
    queryFn: () => apiClient<Location[]>("/locations/"),
  });
}

export function useCreateLocation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Location>) =>
      apiClient<Location>("/locations/", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["locations"] });
    },
  });
}

export function useDeleteLocation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) =>
      apiClient<void>(`/locations/${id}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["locations"] });
    },
  });
}

// ========================
// 8. Calendars
// ========================
export function useCalendars() {
  return useQuery({
    queryKey: ["calendars"],
    queryFn: () => apiClient<WorkCalendar[]>("/calendars/"),
  });
}

export function useCalendarDetails(calendarId: string) {
  return useQuery({
    queryKey: ["calendars", calendarId],
    queryFn: () => apiClient<WorkCalendar>(`/calendars/${calendarId}`),
    enabled: !!calendarId,
  });
}

export function useCreateCalendar() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<WorkCalendar>) =>
      apiClient<WorkCalendar>("/calendars/", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["calendars"] });
    },
  });
}

export function useDeleteCalendar() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) =>
      apiClient<void>(`/calendars/${id}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["calendars"] });
    },
  });
}

// ========================
// 9. Holidays
// ========================
export function useHolidays(year?: number) {
  return useQuery({
    queryKey: ["holidays", year],
    queryFn: () => {
      const qs = year ? `?year=${year}` : "";
      return apiClient<Holiday[]>(`/holidays/${qs}`);
    },
  });
}

export function useCreateHoliday() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Holiday>) =>
      apiClient<Holiday>("/holidays/", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["holidays"] });
    },
  });
}

export function useDeleteHoliday() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) =>
      apiClient<void>(`/holidays/${id}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["holidays"] });
    },
  });
}
