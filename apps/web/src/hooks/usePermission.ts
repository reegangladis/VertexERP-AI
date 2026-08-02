/**
 * usePermission — Enterprise RBAC Permission Checking Hook
 *
 * Checks if the current authenticated user has specific permission(s) or wildcard access.
 * Returns boolean flag for UI conditional rendering.
 */

import { useAuth } from '@/store/AuthContext';

export function usePermission(requiredPermissions?: string | string[]): {
  hasPermission: boolean;
  isLoading: boolean;
  userPermissions: string[];
} {
  const { permissions, isLoading, hasPermission: authHasPermission } = useAuth();

  if (!requiredPermissions) {
    return {
      hasPermission: true,
      isLoading,
      userPermissions: permissions,
    };
  }

  const allowed = authHasPermission(requiredPermissions);

  return {
    hasPermission: allowed,
    isLoading,
    userPermissions: permissions,
  };
}

export default usePermission;
