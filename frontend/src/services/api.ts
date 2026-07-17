import apiClient from "@/api/client";
import type {
  ApiResponse,
  Company,
  Job,
  Referral,
  Application,
  Interview,
  JobFilters,
  PaginationMeta,
} from "@/types";

// ===== Auth =====
export const authApi = {
  login: (email: string, password: string) =>
    apiClient.post<ApiResponse<{ user: any; access_token: string }>>("/auth/login", { email, password }),
  register: (data: { email: string; password: string; nickname: string }) =>
    apiClient.post<ApiResponse<{ user: any; access_token: string }>>("/auth/register", data),
};

// ===== Companies =====
export const companyApi = {
  list: (params?: { page?: number; limit?: number; industry?: string; city?: string }) =>
    apiClient.get<ApiResponse<Company[]>>("/companies", { params }),
  detail: (slug: string) =>
    apiClient.get<ApiResponse<Company>>(`/companies/${slug}`),
  jobs: (slug: string, params?: { category?: string }) =>
    apiClient.get<ApiResponse<Job[]>>(`/companies/${slug}/jobs`, { params }),
};

// ===== Jobs =====
export const jobApi = {
  list: (params: JobFilters) =>
    apiClient.get<ApiResponse<Job[]>>("/jobs", { params }),
  detail: (id: string) =>
    apiClient.get<ApiResponse<Job>>(`/jobs/${id}`),
  search: (q: string) =>
    apiClient.get<ApiResponse<Job[]>>("/jobs/search", { params: { q } }),
  aiSearch: (q: string) =>
    apiClient.get<ApiResponse<{ parsed_query: any; results: Job[]; ai_summary: string }>>(
      "/jobs/ai-search",
      { params: { q } }
    ),
};

// ===== Referrals =====
export const referralApi = {
  list: (params?: { company_id?: string; status?: string; page?: number; userId?: string }) =>
    apiClient.get<ApiResponse<Referral[]>>("/referrals", { params }),
  detail: (id: string) =>
    apiClient.get<ApiResponse<Referral>>(`/referrals/${id}`),
  create: (data: { companyId: string; jobId?: string; referralCode: string; referralLink?: string; referrerName?: string; isEmployee?: boolean; notes?: string }) =>
    apiClient.post<ApiResponse<Referral>>("/referrals", data),
  toggleFavorite: (id: string) =>
    apiClient.post<ApiResponse<{ favorited: boolean }>>(`/referrals/${id}/favorite`),
  rate: (id: string, data: { score: number; comment?: string; responseTime?: string; isSuccess?: boolean }) =>
    apiClient.post<ApiResponse<{ confidenceScore: number; verifiedCount: number; successCount: number }>>(`/referrals/${id}/rate`, data),
  report: (id: string, data: { reason: string; detail?: string }) =>
    apiClient.post<ApiResponse<any>>(`/referrals/${id}/report`, data),
  feedback: (id: string, data: { status: string; note?: string }) =>
    apiClient.post(`/referrals/${id}/feedback`, data),
};

// ===== AI =====
export const aiApi = {
  recommendJobs: (data?: { resume_text?: string; skills?: string[]; city?: string }) =>
    apiClient.post<ApiResponse<{ job: Job; match_score: number; reasons: string[] }[]>>(
      "/ai/recommend-jobs", data
    ),
  analyzeJD: (jobId: string) =>
    apiClient.post<ApiResponse<any>>(`/ai/analyze-jd/${jobId}`),
  copilot: (message: string, history?: { role: string; content: string }[]) =>
    apiClient.post<ApiResponse<any>>("/ai/copilot", { message, history }),

  // Conversations
  createConversation: (userId?: string, title?: string) =>
    apiClient.post<ApiResponse<any>>("/ai/conversations", { userId, title }),
  listConversations: (userId: string) =>
    apiClient.get<ApiResponse<any[]>>(`/ai/conversations/${userId}`),
  getConversation: (id: string) =>
    apiClient.get<ApiResponse<any>>(`/ai/conversation/${id}`),
  deleteConversation: (id: string) =>
    apiClient.delete(`/ai/conversation/${id}`),
  toggleStarConversation: (id: string) =>
    apiClient.patch<ApiResponse<any>>(`/ai/conversation/${id}/star`),
  chatAndSave: (id: string, message: string) =>
    apiClient.post<ApiResponse<any>>(`/ai/conversation/${id}/chat`, { message }),

  // Resume analysis
  analyzeResume: (data: { resume_text: string; skills?: string[] }) =>
    apiClient.post<ApiResponse<any>>("/ai/analyze-resume", data),

  // Personalized recommendation
  personalizedRecommend: (data: { userId: string }) =>
    apiClient.post<ApiResponse<any>>("/ai/personalized-recommend", data),

  // Search history
  saveSearch: (data: { userId: string; query: string; searchType?: string; resultCount?: number }) =>
    apiClient.post<ApiResponse<any>>("/ai/save-search", data),

  getSearchHistory: (data: { userId: string }) =>
    apiClient.post<ApiResponse<any[]>>("/ai/search-history", data),

  // Mock interview
  mockInterview: (data: { job_title: string; company?: string; skills?: string[]; question?: string; history?: { question: string; answer: string }[] }) =>
    apiClient.post<ApiResponse<any>>("/ai/mock-interview", data),
};

// ===== Applications =====
export const applicationApi = {
  list: (params?: { status?: string; page?: number }) =>
    apiClient.get<ApiResponse<Application[]>>("/applications", { params }),
  detail: (id: string) =>
    apiClient.get<ApiResponse<Application>>(`/applications/${id}`),
  create: (data: { job_id: string; referral_id?: string; notes?: string }) =>
    apiClient.post<ApiResponse<Application>>("/applications", data),
  updateStatus: (id: string, data: { status: Application["status"] }) =>
    apiClient.patch<ApiResponse<Application>>(`/applications/${id}/status`, data),
  updateNotes: (id: string, data: { notes?: string; feedback?: string; salary?: number }) =>
    apiClient.patch<ApiResponse<Application>>(`/applications/${id}/notes`, data),
  getInterviews: (id: string) =>
    apiClient.get<ApiResponse<any[]>>(`/applications/${id}/interviews`),
  addInterview: (id: string, data: { round: number; interviewType: string; scheduledAt?: string; interviewer?: string; duration?: number; content?: string; feedback?: string; rating?: number; result?: string; notes?: string }) =>
    apiClient.post<ApiResponse<any>>(`/applications/${id}/interviews`, data),
};

// ===== Favorites =====
export const favoriteApi = {
  list: (type: "job" | "company") =>
    apiClient.get<ApiResponse<any[]>>("/favorites", { params: { type } }),
  add: (data: { target_type: "job" | "company"; target_id: string }) =>
    apiClient.post("/favorites", data),
  remove: (id: string) =>
    apiClient.delete(`/favorites/${id}`),
};

// ===== Interviews =====
export const interviewApi = {
  list: (params?: { company_id?: string; category?: string; page?: number }) =>
    apiClient.get<ApiResponse<Interview[]>>("/interviews", { params }),
};

// ===== Notifications =====
export const notificationApi = {
  list: (params?: { unread_only?: boolean }) =>
    apiClient.get<ApiResponse<any[]>>("/notifications", { params }),
  markRead: (ids: string[]) =>
    apiClient.patch("/notifications/read", { ids }),
  unreadCount: () =>
    apiClient.get<ApiResponse<{ count: number }>>("/notifications/unread-count"),
};
