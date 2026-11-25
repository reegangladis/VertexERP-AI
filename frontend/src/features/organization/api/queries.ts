import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient, isServerlessDemoMode } from "@/lib/api-client";
import { demoStore } from "@/lib/demo-store";
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
} from "../types/organization.types";

async function withDemoFallback<T>(
  apiCall: () => Promise<T>,
  demoFallback: () => T
): Promise<T> {
  try {
    const result = await apiCall();
    if (isServerlessDemoMode()) {
      return demoFallback();
    }
    return result;
  } catch {
    return demoFallback();
  }
}

// ========================
// 1. Branches
// ========================
export function useBranches() {
  return useQuery({
    queryKey: ["branches"],
    queryFn: () =>
      withDemoFallback(
        () => apiClient<Branch[]>("/branches/"),
        () => demoStore.getState().branches
      ),
  });
}

export function useCreateBranch() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: Partial<Branch>) => {
      try {
        const res = await apiClient<Branch>("/branches/", {
          method: "POST",
          body: JSON.stringify(data),
        });
        if (isServerlessDemoMode()) return demoStore.createBranch(data);
        return res;
      } catch {
        return demoStore.createBranch(data);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["branches"] });
    },
  });
}

export function useDeleteBranch() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      try {
        await apiClient<void>(`/branches/${id}`, { method: "DELETE" });
        if (isServerlessDemoMode()) demoStore.deleteBranch(id);
      } catch {
        demoStore.deleteBranch(id);
      }
    },
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
    queryFn: () =>
      withDemoFallback(
        () => apiClient<Department[]>("/departments/"),
        () => demoStore.getState().departments
      ),
  });
}

export function useDepartmentTree() {
  return useQuery({
    queryKey: ["departments", "tree"],
    queryFn: () =>
      withDemoFallback(
        () => apiClient<DepartmentTreeNode[]>("/departments/tree"),
        () => demoStore.getDepartmentTree()
      ),
  });
}

export function useCreateDepartment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: Partial<Department>) => {
      try {
        const res = await apiClient<Department>("/departments/", {
          method: "POST",
          body: JSON.stringify(data),
        });
        if (isServerlessDemoMode()) return demoStore.createDepartment(data);
        return res;
      } catch {
        return demoStore.createDepartment(data);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["departments"] });
    },
  });
}

export function useDeleteDepartment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      try {
        await apiClient<void>(`/departments/${id}`, { method: "DELETE" });
        if (isServerlessDemoMode()) demoStore.deleteDepartment(id);
      } catch {
        demoStore.deleteDepartment(id);
      }
    },
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
    queryFn: () =>
      withDemoFallback(
        () => apiClient<Team[]>("/teams/"),
        () => demoStore.getState().teams
      ),
  });
}

export function useCreateTeam() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: Partial<Team>) => {
      try {
        const res = await apiClient<Team>("/teams/", {
          method: "POST",
          body: JSON.stringify(data),
        });
        if (isServerlessDemoMode()) return demoStore.createTeam(data);
        return res;
      } catch {
        return demoStore.createTeam(data);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["teams"] });
    },
  });
}

export function useTeamMembers(teamId: string) {
  return useQuery({
    queryKey: ["teams", teamId, "members"],
    queryFn: () =>
      withDemoFallback(
        () => apiClient<TeamMember[]>(`/teams/${teamId}/members`),
        () => demoStore.getState().teamMembers[teamId] || []
      ),
    enabled: !!teamId,
  });
}

export function useAddTeamMember(teamId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: { user_id: string; role: string }) => {
      try {
        const res = await apiClient<TeamMember>(`/teams/${teamId}/members`, {
          method: "POST",
          body: JSON.stringify(data),
        });
        if (isServerlessDemoMode()) return demoStore.addTeamMember(teamId, data.user_id, data.role);
        return res;
      } catch {
        return demoStore.addTeamMember(teamId, data.user_id, data.role);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["teams", teamId, "members"] });
    },
  });
}

export function useDeleteTeam() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      try {
        await apiClient<void>(`/teams/${id}`, { method: "DELETE" });
        if (isServerlessDemoMode()) demoStore.deleteTeam(id);
      } catch {
        demoStore.deleteTeam(id);
      }
    },
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
    queryFn: () =>
      withDemoFallback(
        () => apiClient<Designation[]>("/designations/"),
        () => demoStore.getState().designations
      ),
  });
}

export function useCreateDesignation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: Partial<Designation>) => {
      try {
        const res = await apiClient<Designation>("/designations/", {
          method: "POST",
          body: JSON.stringify(data),
        });
        if (isServerlessDemoMode()) return demoStore.createDesignation(data);
        return res;
      } catch {
        return demoStore.createDesignation(data);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["designations"] });
    },
  });
}

export function useDeleteDesignation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      try {
        await apiClient<void>(`/designations/${id}`, { method: "DELETE" });
        if (isServerlessDemoMode()) demoStore.deleteDesignation(id);
      } catch {
        demoStore.deleteDesignation(id);
      }
    },
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
    queryFn: () =>
      withDemoFallback(
        () => apiClient<BusinessUnit[]>("/business-units/"),
        () => demoStore.getState().businessUnits
      ),
  });
}

export function useCreateBusinessUnit() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: Partial<BusinessUnit>) => {
      try {
        const res = await apiClient<BusinessUnit>("/business-units/", {
          method: "POST",
          body: JSON.stringify(data),
        });
        if (isServerlessDemoMode()) return demoStore.createBusinessUnit(data);
        return res;
      } catch {
        return demoStore.createBusinessUnit(data);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["business-units"] });
    },
  });
}

export function useDeleteBusinessUnit() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      try {
        await apiClient<void>(`/business-units/${id}`, { method: "DELETE" });
        if (isServerlessDemoMode()) demoStore.deleteBusinessUnit(id);
      } catch {
        demoStore.deleteBusinessUnit(id);
      }
    },
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
    queryFn: () =>
      withDemoFallback(
        () => apiClient<CostCenter[]>("/cost-centers/"),
        () => demoStore.getState().costCenters
      ),
  });
}

export function useCreateCostCenter() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: Partial<CostCenter>) => {
      try {
        const res = await apiClient<CostCenter>("/cost-centers/", {
          method: "POST",
          body: JSON.stringify(data),
        });
        if (isServerlessDemoMode()) return demoStore.createCostCenter(data);
        return res;
      } catch {
        return demoStore.createCostCenter(data);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cost-centers"] });
    },
  });
}

export function useDeleteCostCenter() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      try {
        await apiClient<void>(`/cost-centers/${id}`, { method: "DELETE" });
        if (isServerlessDemoMode()) demoStore.deleteCostCenter(id);
      } catch {
        demoStore.deleteCostCenter(id);
      }
    },
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
    queryFn: () =>
      withDemoFallback(
        () => apiClient<Location[]>("/locations/"),
        () => demoStore.getState().locations
      ),
  });
}

export function useCreateLocation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: Partial<Location>) => {
      try {
        const res = await apiClient<Location>("/locations/", {
          method: "POST",
          body: JSON.stringify(data),
        });
        if (isServerlessDemoMode()) return demoStore.createLocation(data);
        return res;
      } catch {
        return demoStore.createLocation(data);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["locations"] });
    },
  });
}

export function useDeleteLocation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      try {
        await apiClient<void>(`/locations/${id}`, { method: "DELETE" });
        if (isServerlessDemoMode()) demoStore.deleteLocation(id);
      } catch {
        demoStore.deleteLocation(id);
      }
    },
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
    queryFn: () =>
      withDemoFallback(
        () => apiClient<WorkCalendar[]>("/calendars/"),
        () => demoStore.getState().calendars
      ),
  });
}

export function useCalendarDetails(calendarId: string) {
  return useQuery({
    queryKey: ["calendars", calendarId],
    queryFn: () =>
      withDemoFallback(
        () => apiClient<WorkCalendar>(`/calendars/${calendarId}`),
        () =>
          demoStore.getState().calendars.find((c) => c.id === calendarId) ||
          demoStore.getState().calendars[0]
      ),
    enabled: !!calendarId,
  });
}

export function useCreateCalendar() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: Partial<WorkCalendar>) => {
      try {
        const res = await apiClient<WorkCalendar>("/calendars/", {
          method: "POST",
          body: JSON.stringify(data),
        });
        if (isServerlessDemoMode()) return demoStore.createCalendar(data);
        return res;
      } catch {
        return demoStore.createCalendar(data);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["calendars"] });
    },
  });
}

export function useDeleteCalendar() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      try {
        await apiClient<void>(`/calendars/${id}`, { method: "DELETE" });
        if (isServerlessDemoMode()) demoStore.deleteCalendar(id);
      } catch {
        demoStore.deleteCalendar(id);
      }
    },
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
    queryFn: () =>
      withDemoFallback(
        () => {
          const qs = year ? `?year=${year}` : "";
          return apiClient<Holiday[]>(`/holidays/${qs}`);
        },
        () => {
          const all = demoStore.getState().holidays;
          if (!year) return all;
          return all.filter((h) => h.holiday_date.startsWith(String(year)));
        }
      ),
  });
}

export function useCreateHoliday() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: Partial<Holiday>) => {
      try {
        const res = await apiClient<Holiday>("/holidays/", {
          method: "POST",
          body: JSON.stringify(data),
        });
        if (isServerlessDemoMode()) return demoStore.createHoliday(data);
        return res;
      } catch {
        return demoStore.createHoliday(data);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["holidays"] });
    },
  });
}

export function useDeleteHoliday() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      try {
        await apiClient<void>(`/holidays/${id}`, { method: "DELETE" });
        if (isServerlessDemoMode()) demoStore.deleteHoliday(id);
      } catch {
        demoStore.deleteHoliday(id);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["holidays"] });
    },
  });
}
