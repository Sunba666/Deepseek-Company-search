"use client";

type AnalyticEvent =
  | { type: "page_view"; path: string }
  | { type: "search"; query: string; results: number }
  | { type: "favorite"; targetType: "job" | "company"; targetId: string }
  | { type: "apply_click"; jobId: string; companyId: string }
  | { type: "referral_copy"; referralId: string; code: string }
  | { type: "ai_copilot_message"; message: string }
  | { type: "resume_upload"; fileType: string }
  | { type: "job_view"; jobId: string };

export function track(event: AnalyticEvent) {
  if (typeof window === "undefined") return;
  try {
    const payload = { ...event, timestamp: new Date().toISOString(), url: window.location.href };
    console.debug("[Analytics]", payload);
    // In production, send to analytics API:
    // navigator.sendBeacon("/api/v1/analytics/track", JSON.stringify(payload));
  } catch {}
}

export function usePageTracking() {
  if (typeof window !== "undefined") {
    track({ type: "page_view", path: window.location.pathname });
  }
}
