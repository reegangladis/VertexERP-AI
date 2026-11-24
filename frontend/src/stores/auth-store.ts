import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { apiClient } from "@/lib/api-client";
import { queryClient } from "@/lib/query-client";

export interface CurrentUserDto {
  user_id: string;
  email: string;
  full_name: string;
  tenant_id: string;
  organization_id: string;
  roles: string[];
  permissions: string[];
  is_active: boolean;
}

export interface UserSessionState {
  userId: string | null;
  email: string | null;
  fullName: string | null;
  tenantId: string | null;
  organizationId: string | null;
  roles: string[];
  permissions: string[];
  isAuthenticated: boolean;
  isLoading: boolean;
  setAuth: (payload: {
    userId: string;
    email: string;
    fullName: string;
    tenantId: string;
    organizationId: string;
    roles: string[];
    permissions: string[];
  }) => void;
  clearAuth: () => void;
  logout: () => Promise<void>;
  checkSession: () => Promise<boolean>;
  hasPermission: (permissionCode: string) => boolean;
}

export const useAuthStore = create<UserSessionState>()(
  persist(
    (set, get) => ({
      userId: null,
      email: null,
      fullName: null,
      tenantId: null,
      organizationId: null,
      roles: [],
      permissions: [],
      isAuthenticated: false,
      isLoading: false,

      setAuth: (payload) => {
        set({
          userId: payload.userId,
          email: payload.email,
          fullName: payload.fullName,
          tenantId: payload.tenantId,
          organizationId: payload.organizationId,
          roles: payload.roles,
          permissions: payload.permissions,
          isAuthenticated: true,
          isLoading: false,
        });
      },

      clearAuth: () => {
        set({
          userId: null,
          email: null,
          fullName: null,
          tenantId: null,
          organizationId: null,
          roles: [],
          permissions: [],
          isAuthenticated: false,
          isLoading: false,
        });
      },

      logout: async () => {
        try {
          await apiClient("/identity/auth/logout", { method: "POST" });
        } catch {
          // Backend or network failure: local session and cache are still cleanly evicted
        }
        queryClient.clear();
        get().clearAuth();
      },

      checkSession: async () => {
        // If an authenticated session is already active in persisted storage, retain it
        if (get().isAuthenticated && get().userId) {
          try {
            const user = await apiClient<CurrentUserDto>("/identity/auth/me");
            if (user && user.user_id) {
              set({
                userId: user.user_id,
                email: user.email,
                fullName: user.full_name || get().fullName,
                tenantId: user.tenant_id,
                organizationId: user.organization_id,
                roles: user.roles || get().roles,
                permissions: user.permissions || get().permissions,
                isAuthenticated: true,
                isLoading: false,
              });
              return true;
            }
          } catch {
            // Backend offline or preview deployment: preserve existing authenticated session
            set({ isLoading: false });
            return true;
          }
        }

        set({ isLoading: true });
        try {
          const user = await apiClient<CurrentUserDto>("/identity/auth/me");
          if (user && user.user_id) {
            set({
              userId: user.user_id,
              email: user.email,
              fullName: user.full_name,
              tenantId: user.tenant_id,
              organizationId: user.organization_id,
              roles: user.roles || [],
              permissions: user.permissions || [],
              isAuthenticated: true,
              isLoading: false,
            });
            return true;
          }
        } catch {
          // Unauthenticated or expired session
        }
        get().clearAuth();
        return false;
      },

      hasPermission: (permissionCode: string) => {
        const { permissions, roles } = get();
        if (roles.includes("TenantAdmin") || roles.includes("SUPER_ADMIN") || roles.includes("SystemAdmin")) return true;
        if (permissions.includes("*") || permissions.includes(permissionCode)) return true;
        return permissions.some((p) => {
          if (p.endsWith(":*")) {
            const prefix = p.slice(0, -2);
            return permissionCode === prefix || permissionCode.startsWith(prefix + ":");
          }
          return false;
        });
      },
    }),
    {
      name: "vertexerp_auth_session",
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        userId: state.userId,
        email: state.email,
        fullName: state.fullName,
        tenantId: state.tenantId,
        organizationId: state.organizationId,
        roles: state.roles,
        permissions: state.permissions,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
