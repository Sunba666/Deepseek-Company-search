export type FeatureFlag =
  | "ai-copilot"
  | "ai-resume"
  | "referral-plaza"
  | "salary-center"
  | "interview-center"
  | "admin-panel"
  | "hot-board"
  | "pipeline-crm";

const featureFlags: Record<FeatureFlag, boolean> = {
  "ai-copilot": true,
  "ai-resume": true,
  "referral-plaza": true,
  "salary-center": false,
  "interview-center": false,
  "admin-panel": false,
  "hot-board": true,
  "pipeline-crm": true,
};

export function isFeatureEnabled(flag: FeatureFlag): boolean {
  if (typeof window !== "undefined") {
    const override = localStorage.getItem("ff_" + flag);
    if (override !== null) return override === "true";
  }
  return featureFlags[flag];
}

export function setFeatureFlag(flag: FeatureFlag, enabled: boolean) {
  localStorage.setItem("ff_" + flag, String(enabled));
}

export function getAllFlags(): Record<FeatureFlag, boolean> {
  return Object.keys(featureFlags).reduce((acc, key) => {
    acc[key as FeatureFlag] = isFeatureEnabled(key as FeatureFlag);
    return acc;
  }, {} as Record<FeatureFlag, boolean>);
}
