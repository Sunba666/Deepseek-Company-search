"use client";

import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store";
import { hasPermission, canAccessRoute, type UserRole, type Permission } from "./permissions";

export function useAuth() {
  const { user, token, isAuthenticated, logout } = useAuthStore();
  const router = useRouter();
  const role: UserRole = user?.role ?? "guest";

  return {
    user,
    token,
    isAuthenticated,
    role,
    can: (permission: Permission) => hasPermission(role, permission),
    canAccess: (path: string) => canAccessRoute(role, path),
    requireAuth: () => { if (!isAuthenticated) router.push("/login"); },
    logout: () => { logout(); router.push("/"); },
  };
}
