// ===== Core Domain Types =====

export interface User {
  id: string;
  email: string;
  nickname: string;
  avatarUrl?: string;
  role: "user" | "admin" | "super_admin";
  yearsExp?: number;
  education?: string;
  currentCity?: string;
  skills?: string[];
  expectedSalaryMin?: number;
  expectedSalaryMax?: number;
}

export interface Company {
  id: string;
  name: string;
  nameEn?: string;
  slug: string;
  logoUrl?: string;
  website?: string;
  industry: string;
  scale: string;
  stage: string;
  city: string;
  hiringCount: number;
  averageSalary?: number;
  isFeatured?: boolean;
}

export interface Job {
  id: string;
  title: string;
  company: Company;
  city: string;
  isRemote: boolean;
  salaryMin: number;
  salaryMax: number;
  experience: string;
  education: string;
  skills: string[];
  category: string;
  subCategory?: string;
  referralCount: number;
  matchScore?: number;
  isNew?: boolean;
  isFavorited?: boolean;
  publishedAt: string;
  sourceUrl?: string;
}

export interface Referral {
  id: string;
  company: Pick<Company, "id" | "name" | "slug"> & { logo?: string };
  jobTitle?: string;
  job?: Pick<Job, "id" | "title" | "salaryMin" | "salaryMax">;
  referralCode: string;
  referralLink?: string;
  referrerName?: string;
  referrerTitle?: string;
  isEmployee: boolean;
  isVerified: boolean;
  confidenceScore: number;
  confidenceLevel: "高可信" | "中等" | "低可信";
  verifiedCount: number;
  successCount: number;
  failCount: number;
  publishedAt: string;
  expiresAt?: string;
  source?: string;
  status?: string;
  isFavorited?: boolean;
  _count?: { referralFavorites: number; referralRatings: number };
}

export interface Application {
  id: string;
  job: Pick<Job, "id" | "title" | "salaryMin" | "salaryMax" | "city" | "experience" | "education" | "skills"> & { company: Pick<Company, "id" | "name" | "slug"> };
  status: ApplicationStatus;
  statusHistory?: { status: string; timestamp: string }[];
  referralId?: string;
  referralCodeUsed?: string;
  notes?: string;
  feedback?: string;
  rating?: number;
  expectedSalary?: number;
  actualSalary?: number;
  appliedAt?: string;
  appliedUrl?: string;
  updatedAt: string;
  _count?: { interviewRecords: number };
}

export type ApplicationStatus =
  | "saved"
  | "ready_to_apply"
  | "applied"
  | "hr_viewed"
  | "written_test"
  | "interview_1"
  | "interview_2"
  | "hr_interview"
  | "offer"
  | "rejected"
  | "withdrawn";

export interface Interview {
  id: string;
  company: Pick<Company, "id" | "name">;
  jobCategory: string;
  jobTitle?: string;
  content: string;
  interviewRounds: number;
  difficulty: "容易" | "中等" | "困难";
  result: "offer" | "rejected" | "unknown";
}

// ===== API Response Types =====

export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
  meta?: PaginationMeta;
}

export interface PaginationMeta {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
}

// ===== Filter Types =====

export interface JobFilters {
  category?: string;
  subCategory?: string;
  city?: string;
  experience?: string;
  education?: string;
  salaryMin?: number;
  salaryMax?: number;
  isRemote?: boolean;
  sort?: "published_at" | "salary" | "match_score";
  order?: "asc" | "desc";
  q?: string;
  page?: number;
  limit?: number;
}

export type JobCategory =
  | "研发" | "AI" | "产品" | "运营" | "设计"
  | "测试" | "运维" | "数据分析" | "安全" | "算法";

export const JOB_CATEGORIES: Record<JobCategory, string[]> = {
  "研发": ["Java", "Golang", "Python", "C++", "前端", "React", "Vue", "Node", "全栈", "Android", "iOS"],
  "AI": ["大模型", "Agent", "NLP", "CV", "推荐算法", "数据挖掘", "AI产品"],
  "产品": ["产品经理", "AI产品", "数据产品", "支付产品", "增长产品"],
  "运营": ["用户运营", "内容运营", "社区运营", "海外运营", "增长运营"],
  "设计": ["UI", "UX", "视觉", "动效", "交互设计"],
  "测试": ["功能测试", "自动化测试", "性能测试"],
  "运维": ["SRE", "运维开发", "DBA", "网络运维"],
  "数据分析": ["数据分析师", "数据仓库", "数据工程"],
  "安全": ["安全开发", "渗透测试", "安全运营"],
  "算法": ["推荐算法", "搜索算法", "广告算法", "运筹优化"],
};

export const CITIES = ["北京", "上海", "深圳", "杭州", "广州", "成都", "西安", "Remote"];
export const EXPERIENCE_LEVELS = ["应届", "1-3年", "3-5年", "5年以上"];
export const EDUCATION_LEVELS = ["不限", "大专", "本科", "硕士", "博士"];
export const COMPANY_STAGES = ["天使轮", "A轮", "B轮", "C轮", "D轮", "上市公司", "独角兽"];
