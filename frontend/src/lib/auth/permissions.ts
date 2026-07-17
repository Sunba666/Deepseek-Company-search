export type UserRole = "guest" | "user" | "premium" | "enterprise" | "admin" | "super_admin";

export type Permission =
  | "view:jobs"
  | "view:companies"
  | "view:referrals"
  | "view:pipeline"
  | "view:salary"
  | "view:interviews"
  | "view:hot"
  | "view:admin"
  | "use:ai-copilot"
  | "use:ai-recommend"
  | "use:ai-resume"
  | "use:ai-interview"
  | "create:application"
  | "create:referral-feedback"
  | "manage:users"
  | "manage:companies"
  | "manage:jobs"
  | "manage:referrals"
  | "manage:system";

const rolePermissions: Record<UserRole, Permission[]> = {
  guest: ["view:jobs", "view:companies", "view:referrals", "view:hot"],
  user: [
    "view:jobs", "view:companies", "view:referrals", "view:hot",
    "view:pipeline", "use:ai-copilot", "use:ai-recommend",
    "create:application", "create:referral-feedback",
  ],
  premium: [
    "view:jobs", "view:companies", "view:referrals", "view:hot",
    "view:pipeline", "view:salary", "view:interviews",
    "use:ai-copilot", "use:ai-recommend", "use:ai-resume", "use:ai-interview",
    "create:application", "create:referral-feedback",
  ],
  enterprise: [
    "view:jobs", "view:companies", "view:referrals", "view:hot",
    "view:pipeline", "view:salary", "view:interviews",
    "use:ai-copilot", "use:ai-recommend", "use:ai-resume", "use:ai-interview",
    "create:application", "create:referral-feedback",
  ],
  admin: [
    "view:jobs", "view:companies", "view:referrals", "view:hot",
    "view:pipeline", "view:salary", "view:interviews", "view:admin",
    "use:ai-copilot", "use:ai-recommend", "use:ai-resume",
    "create:application", "create:referral-feedback",
    "manage:users", "manage:companies", "manage:jobs", "manage:referrals",
  ],
  super_admin: [
    "view:jobs", "view:companies", "view:referrals", "view:hot",
    "view:pipeline", "view:salary", "view:interviews", "view:admin",
    "use:ai-copilot", "use:ai-recommend", "use:ai-resume",
    "create:application", "create:referral-feedback",
    "manage:users", "manage:companies", "manage:jobs", "manage:referrals", "manage:system",
  ],
};

export function hasPermission(role: UserRole, permission: Permission): boolean {
  return rolePermissions[role]?.includes(permission) ?? false;
}

export function getPermissionsForRole(role: UserRole): Permission[] {
  return rolePermissions[role] ?? rolePermissions.guest;
}

export function canAccessRoute(role: UserRole, path: string): boolean {
  if (role === "super_admin" || role === "admin") return true;
  if (path.startsWith("/admin")) return hasPermission(role, "view:admin");
  if (path.startsWith("/pipeline")) return hasPermission(role, "view:pipeline");
  if (path.startsWith("/salary")) return hasPermission(role, "view:salary");
  if (path.startsWith("/interviews")) return hasPermission(role, "view:interviews");
  return true;
}
