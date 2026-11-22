import React from "react";
import { useAuthStore } from "@/stores/auth-store";

export interface RequirePermissionProps {
  permission: string | string[];
  requireAll?: boolean;
  fallback?: React.ReactNode;
  children: React.ReactNode;
}

export const RequirePermission: React.FC<RequirePermissionProps> = ({
  permission,
  requireAll = false,
  fallback = null,
  children,
}) => {
  const { hasPermission } = useAuthStore();
  const permissions = Array.isArray(permission) ? permission : [permission];

  const isAllowed = requireAll
    ? permissions.every((p) => hasPermission(p))
    : permissions.some((p) => hasPermission(p));

  if (!isAllowed) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
};
