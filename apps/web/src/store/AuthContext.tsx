/**
 * AuthContext — Enterprise Global Authentication & RBAC State Provider
 *
 * Exposes:
 * - user, isAuthenticated, isLoading
 * - organization, roles, permissions
 * - login(), register(), logout(), logoutAll(), refreshUser(), updateUser()
 * - hasPermission(), hasRole(), getDefaultDashboardRoute()
 */

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient, tokenStorage } from '@/services/apiClient';

// ─────────────────────────────────────────
// Types & Permission Specs
// ─────────────────────────────────────────

export interface RoleObject {
  id: string;
  name: string;
  description: string | null;
  permissions?: Array<{ id: string; code: string; name: string }>;
}

export interface OrganizationObject {
  id: string;
  name: string;
  slug: string;
  status?: string;
  currency?: string;
  country?: string;
  timezone?: string;
}

export interface AuthUser {
  id: string;
  first_name: string;
  last_name: string;
  username: string;
  email: string;
  phone: string | null;
  avatar: string | null;
  status: string;
  email_verified: boolean;
  phone_verified: boolean;
  last_login: string | null;
  timezone: string;
  language: string;
  mfa_enabled: boolean;
  organization_id: string | null;
  organization?: OrganizationObject | null;
  roles: RoleObject[];
  permissions?: string[];
}

export interface RegisterPayload {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  password: string;
  org_name: string;
  org_slug: string;
  industry?: string;
  company_size?: string;
  country?: string;
  timezone?: string;
}

interface AuthContextValue {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  organization: OrganizationObject | null;
  roles: string[];
  permissions: string[];
  login: (email: string, password: string) => Promise<AuthUser>;
  register: (payload: RegisterPayload) => Promise<AuthUser>;
  logout: () => Promise<void>;
  logoutAll: () => Promise<void>;
  refreshUser: () => Promise<void>;
  updateUser: (patch: Partial<AuthUser>) => void;
  hasPermission: (permission: string | string[]) => boolean;
  hasRole: (role: string | string[]) => boolean;
  getDefaultDashboardRoute: () => string;
}

// Default role fallback permissions for enterprise modules
const ROLE_PERMISSIONS_FALLBACK: Record<string, string[]> = {
  'Super Admin': ['*'],
  'Organization Admin': ['*'],
  'Admin': ['*'],
  'HR Manager': ['employees.read', 'employees.create', 'employees.update', 'employees.delete', 'hr.read', 'hr.write', 'payroll.read', 'payroll.write', 'reports.export'],
  'HR Executive': ['employees.read', 'employees.create', 'employees.update', 'hr.read'],
  'Finance Manager': ['finance.read', 'finance.create', 'finance.update', 'finance.delete', 'finance.approve', 'reports.export'],
  'Accountant': ['finance.read', 'finance.create', 'finance.update'],
  'Inventory Manager': ['inventory.read', 'inventory.create', 'inventory.update', 'inventory.delete', 'reports.export'],
  'Warehouse Staff': ['inventory.read', 'inventory.update'],
  'Sales Manager': ['crm.read', 'crm.create', 'crm.update', 'crm.delete', 'reports.export'],
  'CRM Manager': ['crm.read', 'crm.create', 'crm.update', 'crm.delete', 'reports.export'],
  'Sales Executive': ['crm.read', 'crm.create', 'crm.update'],
  'Project Manager': ['workflows.read', 'workflows.write', 'copilot.use', 'rag.use'],
  'Employee': ['employees.read', 'attendance.self', 'leave.self', 'profile.update'],
  'Manager': ['employees.read', 'hr.read', 'crm.read', 'inventory.read', 'finance.read'],
  'Viewer': ['*.read'],
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  // Extract roles string array
  const roles = useMemo<string[]>(() => {
    if (!user || !user.roles) return [];
    return user.roles.map((r) => r.name);
  }, [user]);

  // Extract / calculate unified permissions array
  const permissions = useMemo<string[]>(() => {
    if (!user) return [];

    // If explicit permissions array present on user
    if (user.permissions && Array.isArray(user.permissions) && user.permissions.length > 0) {
      return user.permissions;
    }

    // Collect permissions from roles objects
    const collected = new Set<string>();
    if (user.roles) {
      for (const r of user.roles) {
        if (r.permissions && Array.isArray(r.permissions)) {
          r.permissions.forEach((p) => collected.add(p.code));
        }
        // Fallback role mapping
        const fallback = ROLE_PERMISSIONS_FALLBACK[r.name];
        if (fallback) {
          fallback.forEach((p) => collected.add(p));
        }
      }
    }

    // Default admin fallback
    if (collected.size === 0) {
      collected.add('*');
    }

    return Array.from(collected);
  }, [user]);

  const organization = useMemo<OrganizationObject | null>(() => {
    return user?.organization || null;
  }, [user]);

  /**
   * Check if user has specific permission(s)
   */
  const hasPermission = useCallback(
    (required: string | string[]): boolean => {
      if (!user) return false;
      if (permissions.includes('*')) return true;

      const reqArray = Array.isArray(required) ? required : [required];
      return reqArray.some((req) => {
        if (permissions.includes(req)) return true;
        // Check wildcard namespace (e.g. "finance.*" matches "finance.read")
        const [domain] = req.split('.');
        if (domain && permissions.includes(`${domain}.*`)) return true;
        if (permissions.includes('*.read') && req.endsWith('.read')) return true;
        return false;
      });
    },
    [user, permissions],
  );

  /**
   * Check if user has specific role(s)
   */
  const hasRole = useCallback(
    (requiredRole: string | string[]): boolean => {
      if (!user) return false;
      if (roles.includes('Super Admin') || roles.includes('Organization Admin')) return true;

      const reqArray = Array.isArray(requiredRole) ? requiredRole : [requiredRole];
      return reqArray.some((r) => roles.includes(r));
    },
    [user, roles],
  );

  /**
   * Determine default dashboard landing route by role
   */
  const getDefaultDashboardRoute = useCallback((): string => {
    if (!user) return '/auth/login';

    if (hasRole(['Super Admin', 'Organization Admin', 'Admin'])) {
      return '/dashboard';
    }
    if (hasRole(['HR Manager', 'HR Executive'])) {
      return '/hr/dashboard';
    }
    if (hasRole(['Finance Manager', 'Accountant'])) {
      return '/finance/dashboard';
    }
    if (hasRole(['Inventory Manager', 'Warehouse Staff'])) {
      return '/inventory/dashboard';
    }
    if (hasRole(['Sales Manager', 'Sales Executive', 'CRM Manager'])) {
      return '/crm/dashboard';
    }
    if (hasRole('Employee')) {
      return '/hr/dashboard';
    }
    return '/dashboard';
  }, [user, hasRole]);

  /**
   * Fetch current user profile from GET /api/v1/auth/me
   */
  const refreshUser = useCallback(async () => {
    const token = tokenStorage.getAccessToken();
    if (!token) {
      setUser(null);
      setIsLoading(false);
      return;
    }
    try {
      const res = await apiClient.get('/api/v1/auth/me');
      const userData: AuthUser = res.data?.data ?? res.data;
      setUser(userData);
      localStorage.setItem('vertex_user', JSON.stringify(userData));
    } catch {
      tokenStorage.clearTokens();
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Hydrate user on mount
  useEffect(() => {
    const cachedUser = localStorage.getItem('vertex_user');
    if (cachedUser) {
      try {
        setUser(JSON.parse(cachedUser));
      } catch {
        // ignore corrupt cache
      }
    }
    refreshUser();
  }, [refreshUser]);

  /**
   * Login user via POST /api/v1/auth/login
   */
  const login = useCallback(
    async (email: string, password: string): Promise<AuthUser> => {
      const res = await apiClient.post('/api/v1/auth/login', { email, password });
      const data = res.data?.data ?? res.data;

      tokenStorage.setTokens(data.access_token, data.refresh_token);

      const meRes = await apiClient.get('/api/v1/auth/me');
      const userData: AuthUser = meRes.data?.data ?? meRes.data;
      setUser(userData);
      localStorage.setItem('vertex_user', JSON.stringify(userData));
      return userData;
    },
    [],
  );

  /**
   * Register new organization & admin via POST /api/v1/auth/register
   */
  const register = useCallback(
    async (payload: RegisterPayload): Promise<AuthUser> => {
      const res = await apiClient.post('/api/v1/auth/register', payload);
      const data = res.data?.data ?? res.data;

      if (data.access_token && data.refresh_token) {
        tokenStorage.setTokens(data.access_token, data.refresh_token);
      }

      const meRes = await apiClient.get('/api/v1/auth/me');
      const userData: AuthUser = meRes.data?.data ?? meRes.data;
      setUser(userData);
      localStorage.setItem('vertex_user', JSON.stringify(userData));
      return userData;
    },
    [],
  );

  /**
   * Logout single session via POST /api/v1/auth/logout
   */
  const logout = useCallback(async () => {
    const refreshToken = tokenStorage.getRefreshToken();
    try {
      if (refreshToken) {
        await apiClient.post('/api/v1/auth/logout', { refresh_token: refreshToken });
      }
    } catch {
      // Best-effort
    } finally {
      tokenStorage.clearTokens();
      setUser(null);
      navigate('/auth/login', { replace: true });
    }
  }, [navigate]);

  /**
   * Logout all sessions via DELETE /api/v1/auth/logout-all
   */
  const logoutAll = useCallback(async () => {
    try {
      await apiClient.delete('/api/v1/auth/logout-all');
    } catch {
      // Best-effort
    } finally {
      tokenStorage.clearTokens();
      setUser(null);
      navigate('/auth/login', { replace: true });
    }
  }, [navigate]);

  /**
   * Update local user state
   */
  const updateUser = useCallback((patch: Partial<AuthUser>) => {
    setUser((prev) => {
      if (!prev) return null;
      const updated = { ...prev, ...patch };
      localStorage.setItem('vertex_user', JSON.stringify(updated));
      return updated;
    });
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: !!user,
      isLoading,
      organization,
      roles,
      permissions,
      login,
      register,
      logout,
      logoutAll,
      refreshUser,
      updateUser,
      hasPermission,
      hasRole,
      getDefaultDashboardRoute,
    }),
    [
      user,
      isLoading,
      organization,
      roles,
      permissions,
      login,
      register,
      logout,
      logoutAll,
      refreshUser,
      updateUser,
      hasPermission,
      hasRole,
      getDefaultDashboardRoute,
    ],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
