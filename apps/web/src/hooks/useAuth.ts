/**
 * useAuth — Convenience hook for consuming global authentication state.
 *
 * Re-exports useAuth from AuthContext so components can import from a
 * standard hook path without coupling to the store directory.
 *
 * Usage:
 *   import { useAuth } from '@/hooks/useAuth';
 *   const { user, isAuthenticated, login, logout } = useAuth();
 */

export { useAuth } from '@/store/AuthContext';
export type { AuthUser } from '@/store/AuthContext';
