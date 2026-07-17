# API 设计 — JobNav AI

> 版本：v1.0
> 状态：初稿
> 基础路径：/api/v1

---

## 一、API 设计规范

### 1.1 通用规范

| 规范 | 说明 |
|------|------|
| 协议 | HTTPS |
| 基础路径 | /api/v1 |
| 数据格式 | JSON（Content-Type: application/json）|
| 认证 | Bearer Token（JWT）|
| 分页 | ?page=1&limit=20（默认 page=1, limit=20）|
| 排序 | ?sort=created_at&order=desc |
| 筛选 | ?field=value |
| 搜索 | ?q=keyword |

### 1.2 通用响应格式

**成功响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": { ... },
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "total_pages": 5
  }
}
```

**错误响应：**
```json
{
  "code": 40001,
  "message": "岗位不存在",
  "details": { "field": "job_id", "reason": "not_found" }
}
```

### 1.3 HTTP 状态码

| 状态码 | 说明 |
|:------:|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 409 | 资源冲突 |
| 422 | 参数校验失败 |
| 429 | 请求频率限制 |
| 500 | 服务器内部错误 |

---

## 二、认证模块 (Auth)

### 2.1 注册

```
POST /api/v1/auth/register

Request:
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "nickname": "求职者小明",
  "agree_terms": true
}

Response 201:
{
  "code": 0,
  "data": {
    "user": { "id": "uuid", "email": "...", "nickname": "..." },
    "access_token": "eyJ...",
    "refresh_token": "eyJ..."
  }
}
```

### 2.2 登录

```
POST /api/v1/auth/login

Request:
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

Response 200:
{
  "code": 0,
  "data": {
    "user": { ... },
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "expires_in": 7200
  }
}
```

### 2.3 OAuth 登录

```
POST /api/v1/auth/oauth

Request:
{
  "provider": "github",
  "code": "oauth_authorization_code"
}

Response 200:
{
  "code": 0,
  "data": {
    "user": { ... },
    "access_token": "eyJ...",
    "is_new_user": true
  }
}
```

### 2.4 刷新 Token

```
POST /api/v1/auth/refresh

Request:
{
  "refresh_token": "eyJ..."
}

Response 200:
{
  "code": 0,
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "expires_in": 7200
  }
}
```

---

## 三、用户模块 (Users)

### 3.1 获取当前用户信息

```
GET /api/v1/users/me
Authorization: Bearer {token}

Response 200:
{
  "code": 0,
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "nickname": "求职者小明",
    "avatar_url": "...",
    "role": "user",
    "years_exp": 3,
    "education": "本科",
    "current_city": "上海",
    "skills": ["Java", "Spring Boot", "MySQL"],
    "expected_salary_min": 30,
    "expected_salary_max": 50,
    "preferred_cities": ["上海", "杭州"],
    "stats": {
      "total_applications": 12,
      "interview_rate": 0.5,
      "offer_rate": 0.25
    }
  }
}
```

### 3.2 更新用户信息

```
PATCH /api/v1/users/me
Authorization: Bearer {token}

Request:
{
  "nickname": "新昵称",
  "years_exp": 5,
  "skills": ["Java", "Python", "AWS"],
  "expected_salary_min": 40
}
```

### 3.3 上传简历

```
POST /api/v1/users/me/resume
Authorization: Bearer {token}
Content-Type: multipart/form-data

Request:
file: resume.pdf

Response 200:
{
  "code": 0,
  "data": {
    "resume_url": "s3://...",
    "parsed": {
      "skills": ["Java", "Python"],
      "experience": 3,
      "education": "硕士"
    }
  }
}
```

---

## 四、公司模块 (Companies)

### 4.1 公司列表

```
GET /api/v1/companies?page=1&limit=20&industry=互联网&city=上海&sort=hiring_count

Response 200:
{
  "code": 0,
  "data": [
    {
      "id": "uuid",
      "name": "字节跳动",
      "slug": "bytedance",
      "logo_url": "...",
      "industry": "互联网",
      "city": "北京",
      "scale": "2000+",
      "stage": "独角兽",
      "hiring_count": 128,
      "average_salary": 45,
      "is_featured": true
    }
  ],
  "meta": { "page": 1, "limit": 20, "total": 200 }
}
```

### 4.2 公司详情

```
GET /api/v1/companies/:slug

Response 200:
{
  "code": 0,
  "data": {
    "id": "uuid",
    "name": "字节跳动",
    "slug": "bytedance",
    "description": "...",
    "hiring_count": 128,
    "jobs": [ ... ],                   // 在招岗位
    "profile": {                       // AI 公司画像
      "overall_score": 8.5,
      "hiring_trend": "增长",
      "salary_score": 8.0,
      "culture_score": 7.5,
      "summary": "字节跳动正处于快速扩张期..."
    }
  }
}
```

### 4.3 公司搜索

```
GET /api/v1/companies/search?q=字节&city=北京

Response 200:
{
  "code": 0,
  "data": [ ... ]
}
```

### 4.4 公司岗位列表

```
GET /api/v1/companies/:slug/jobs?category=研发&is_active=true

Response 200:
{
  "code": 0,
  "data": [ ... ]
}
```

---

## 五、岗位模块 (Jobs)

### 5.1 岗位列表（筛选/搜索）

```
GET /api/v1/jobs
  ?category=研发
  &sub_category=Java
  &city=上海
  &experience=3-5年
  &salary_min=30
  &salary_max=60
  &is_remote=false
  &sort=published_at
  &order=desc
  &page=1
  &limit=20

Response 200:
{
  "code": 0,
  "data": [
    {
      "id": "uuid",
      "title": "Java 后端开发工程师",
      "company": { "id": "uuid", "name": "字节跳动", "slug": "bytedance", "logo_url": "..." },
      "city": "上海",
      "salary_min": 30,
      "salary_max": 60,
      "experience": "3-5年",
      "education": "本科",
      "skills": ["Java", "Spring Boot", "MySQL", "Redis"],
      "referral_count": 3,
      "is_new": true,
      "published_at": "2024-01-15T00:00:00Z",
      "match_score": 85                    // AI 匹配度（当用户已登录且有简历时）
    }
  ],
  "meta": { "page": 1, "limit": 20, "total": 156 }
}
```

### 5.2 岗位详情

```
GET /api/v1/jobs/:id

Response 200:
{
  "code": 0,
  "data": {
    "id": "uuid",
    "title": "Java 后端开发工程师",
    "company": { ... },
    "city": "上海",
    "salary_min": 30,
    "salary_max": 60,
    "salary_monthly": 15,
    "experience": "3-5年",
    "education": "本科",
    "skills": ["Java", "Spring Boot", "MySQL"],
    "description": "# 岗位职责
...",
    "requirements": "# 任职要求
...",
    "benefits": "六险一金、免费三餐...",
    "source_url": "https://jobs.bytedance.com/...",
    "timeline": {
      "published_at": "2024-01-15",
      "updated_at": "2024-01-20",
      "expired_at": "2024-02-29",
      "is_active": true
    },
    "referrals": [
      {
        "id": "uuid",
        "code": "NTABkC8",
        "confidence_score": 95,
        "confidence_level": "高可信",
        "referrer_name": "张三",
        "is_employee": true,
        "published_at": "2024-01-18"
      }
    ],
    "is_favorited": false,
    "application_status": null
  }
}
```

### 5.3 岗位搜索

```
GET /api/v1/jobs/search?q=上海Java后端开发&page=1

Response 200: (同岗位列表格式)
```

### 5.4 自然语言搜索（AI）

```
GET /api/v1/jobs/ai-search?q=推荐上海AI产品经理岗位

Response 200:
{
  "code": 0,
  "data": {
    "parsed_query": {
      "city": "上海",
      "category": "AI",
      "sub_category": "AI产品",
      "intent": "recommend"
    },
    "results": [ ... ],
    "ai_summary": "为您找到上海地区 8 个 AI 产品经理岗位..."
  }
}
```

---

## 六、内推模块 (Referrals)

### 6.1 内推列表

```
GET /api/v1/referrals?company_id=uuid&status=active&sort=confidence_score&order=desc&page=1

Response 200:
{
  "code": 0,
  "data": [
    {
      "id": "uuid",
      "company": { "id": "uuid", "name": "字节跳动" },
      "job_title": "Java 后端开发",
      "referral_code": "NTABkC8",
      "referral_link": "...",
      "referrer_name": "张三",
      "is_employee": true,
      "confidence_score": 95,
      "confidence_level": "高可信",
      "published_at": "2024-01-18",
      "expires_at": "2024-02-18"
    }
  ],
  "meta": { "page": 1, "limit": 20, "total": 50 }
}
```

### 6.2 内推详情

```
GET /api/v1/referrals/:id

Response 200:
{
  "code": 0,
  "data": {
    "id": "uuid",
    "company": { ... },
    "job": { "id": "uuid", "title": "Java 后端开发" },
    "referral_code": "NTABkC8",
    "referral_link": "...",
    "referrer_name": "张三",
    "referrer_title": "高级工程师",
    "is_employee": true,
    "is_verified": true,
    "confidence_score": 95,
    "confidence_level": "高可信",
    "confidence_reason": "员工认证 + 多人验证 + 7天内发布",
    "verified_count": 5,
    "success_count": 2,
    "source": "脉脉",
    "source_url": "...",
    "published_at": "2024-01-18",
    "expires_at": "2024-02-18"
  }
}
```

### 6.3 内推反馈（用户报告失效）

```
POST /api/v1/referrals/:id/feedback
Authorization: Bearer {token}

Request:
{
  "status": "expired",      // valid / expired / invalid
  "note": "内推码已失效"
}
```

---

## 七、AI 分析模块 (AI)

### 7.1 AI 岗位推荐（基于简历）

```
POST /api/v1/ai/recommend-jobs
Authorization: Bearer {token}

Request (可选，不传则使用已有简历):
{
  "resume_text": "3年Java后端经验，熟练Spring Boot...",
  "skills": ["Java", "Spring Boot"],
  "experience": 3,
  "education": "本科",
  "city": "上海",
  "preferences": {
    "salary_min": 30,
    "salary_max": 50,
    "categories": ["研发"],
    "companies": ["字节跳动", "腾讯"]
  }
}

Response 200:
{
  "code": 0,
  "data": [
    {
      "job": { "id": "uuid", "title": "...", "company": "..." },
      "match_score": 92,
      "match_label": "非常匹配",
      "estimated_salary": "35K-50K",
      "reasons": [
        "3年Java经验与岗位要求高度匹配",
        "Spring Boot 经验丰富",
        "上海地区，通勤便利"
      ],
      "missing_skills": ["分布式系统设计"],
      "learning_tips": "建议学习《Designing Data-Intensive Applications》"
    }
  ],
  "ai_summary": "根据您的背景，推荐以上 8 个岗位..."
}
```

### 7.2 AI JD 分析

```
POST /api/v1/ai/analyze-jd/:jobId
Authorization: Bearer {token}

Response 200:
{
  "code": 0,
  "data": {
    "match_score": 85,
    "match_label": "比较匹配",
    "skill_match": {
      "matched": ["Java", "Spring Boot", "MySQL"],
      "missing": ["Redis", "Kafka"],
      "bonus": ["大流量高并发经验"]
    },
    "resume_tips": [
      "突出你在高并发场景下的经验",
      "补充 Redis 使用经验",
      "量化项目成果（如：QPS 提升 50%）"
    ],
    "learning_plan": "建议在 2 周内掌握 Redis 基础...",
    "salary_analysis": {
      "market_avg": "35K",
      "market_range": "25K-50K",
      "your_estimate": "30K-40K"
    }
  }
}
```

### 7.3 AI 简历匹配

```
POST /api/v1/ai/resume-match
Authorization: Bearer {token}
Content-Type: multipart/form-data

Request:
file: resume.pdf
job_id: uuid

Response 200:
{
  "code": 0,
  "data": {
    "ats_score": 72,
    "keyword_match_rate": 0.65,
    "suggested_keywords": ["Redis", "Kafka", "分布式事务"],
    "format_tips": ["使用标准标题格式", "增加量化指标"],
    "section_scores": {
      "experience": 80,
      "education": 90,
      "skills": 65,
      "projects": 70
    }
  }
}
```

### 7.4 AI 公司画像

```
GET /api/v1/ai/company-profile/:companyId

Response 200:
{
  "code": 0,
  "data": {
    "overall_score": 8.5,
    "dimensions": {
      "salary": { "score": 8.0, "comment": "薪资高于行业平均 20%" },
      "culture": { "score": 7.5, "comment": "工程师文化浓厚" },
      "growth": { "score": 9.0, "comment": "业务快速增长中" },
      "stability": { "score": 7.0, "comment": "裁员风险中等" }
    },
    "hiring_trend": {
      "trend": "增长",
      "heat": 85,
      "hot_jobs": ["AI 算法工程师", "后端开发"],
      "total_hc": 200
    },
    "pros": ["薪资高", "成长快", "技术氛围好"],
    "cons": ["加班多", "竞争激烈"],
    "summary": "字节跳动目前处于快速扩张期..."
  }
}
```

### 7.5 AI Copilot（对话）

```
POST /api/v1/ai/copilot
Authorization: Bearer {token}

Request:
{
  "message": "推荐上海AI产品经理的岗位",
  "context": {
    "current_page": "/jobs",
    "current_job_id": "uuid"        // 可选，当前浏览的岗位
  },
  "history": [                      // 对话历史
    { "role": "user", "content": "你好" },
    { "role": "assistant", "content": "你好！我是 JobNav AI 求职助手..." }
  ]
}

// SSE (Server-Sent Events) 流式响应
Response:
data: {"type": "intent", "data": {"intent": "recommend", "params": {...}}}
data: {"type": "searching", "data": {"query": "上海 AI 产品经理 岗位"}}
data: {"type": "result", "data": {"jobs": [...], "count": 8}}
data: {"type": "message", "data": {"content": "为您找到 8 个上海 AI 产品经理岗位..."}}
data: {"type": "done"}
```

---

## 八、投递管理模块 (Applications)

### 8.1 投递列表

```
GET /api/v1/applications?status=saved&page=1&limit=20
Authorization: Bearer {token}

Response 200:
{
  "code": 0,
  "data": [
    {
      "id": "uuid",
      "job": { "id": "uuid", "title": "...", "company": "..." },
      "status": "saved",
      "referral_code_used": "NTABkC8",
      "applied_at": null,
      "updated_at": "2024-01-20T00:00:00Z"
    }
  ],
  "stats": {
    "total": 12,
    "saved": 3,
    "applied": 5,
    "interviewing": 2,
    "offer": 1,
    "rejected": 1,
    "interview_rate": 0.5,
    "offer_rate": 0.25
  }
}
```

### 8.2 创建投递记录

```
POST /api/v1/applications
Authorization: Bearer {token}

Request:
{
  "job_id": "uuid",
  "referral_id": "uuid",           // 可选
  "notes": "使用内推码 NTABkC8 投递"
}

Response 201:
{
  "code": 0,
  "data": { "id": "uuid", "status": "saved" }
}
```

### 8.3 更新投递状态

```
PATCH /api/v1/applications/:id
Authorization: Bearer {token}

Request:
{
  "status": "applied",
  "applied_at": "2024-01-20T10:00:00Z",
  "notes": "已完成官网投递"
}

Response 200: { "code": 0, "data": { ... } }
```

### 8.4 批量更新状态

```
POST /api/v1/applications/batch
Authorization: Bearer {token}

Request:
{
  "ids": ["uuid1", "uuid2"],
  "status": "interview_1"
}
```

---

## 九、收藏模块 (Favorites)

### 9.1 收藏列表

```
GET /api/v1/favorites?type=job&page=1
Authorization: Bearer {token}

Response 200: { "code": 0, "data": [...] }
```

### 9.2 添加收藏

```
POST /api/v1/favorites
Authorization: Bearer {token}

Request:
{
  "target_type": "job",            // job / company
  "target_id": "uuid"
}
```

### 9.3 取消收藏

```
DELETE /api/v1/favorites/:id
Authorization: Bearer {token}
```

---

## 十、消息通知模块 (Notifications)

### 10.1 通知列表

```
GET /api/v1/notifications?unread_only=false&page=1
Authorization: Bearer {token}

Response 200: { "code": 0, "data": [...] }
```

### 10.2 标记已读

```
PATCH /api/v1/notifications/read
Authorization: Bearer {token}

Request: { "ids": ["uuid1", "uuid2"] }
// 或全部标记已读
Request: { "all": true }
```

### 10.3 未读数量

```
GET /api/v1/notifications/unread-count
Authorization: Bearer {token}

Response: { "code": 0, "data": { "count": 5 } }
```

---

## 十一、热门榜模块 (Hot)

### 11.1 热门公司

```
GET /api/v1/hot/companies

Response 200:
{
  "code": 0,
  "data": [
    { "rank": 1, "company": { ... }, "score": 1000, "change": "+2" },
    { "rank": 2, "company": { ... }, "score": 850, "change": "-1" }
  ]
}
```

### 11.2 热门岗位

```
GET /api/v1/hot/jobs

Response: { "code": 0, "data": [...] }
```

### 11.3 热门技能

```
GET /api/v1/hot/skills

Response: { "code": 0, "data": [{"skill": "AI 算法", "count": 200}] }
```

---

## 十二、面经模块 (Interviews)

### 12.1 面经列表

```
GET /api/v1/interviews?company_id=uuid&category=研发&page=1

Response 200: { "code": 0, "data": [...] }
```

### 12.2 面经详情

```
GET /api/v1/interviews/:id
```

### 12.3 创建面经

```
POST /api/v1/interviews
Authorization: Bearer {token}

Request:
{
  "company_id": "uuid",
  "job_category": "研发",
  "job_title": "Java 后端开发",
  "content": "面试一共 4 轮...",
  "interview_rounds": 4,
  "difficulty": "困难",
  "result": "offer",
  "algorithm_questions": ["LeetCode 146 LRU"],
  "knowledge_questions": ["MySQL 索引原理"],
  "hr_questions": ["为什么离职"]
}
```

---

## 十三、AI 每日机会模块 (Daily)

### 13.1 今日新增

```
GET /api/v1/daily/new-jobs

Response:
{
  "code": 0,
  "data": {
    "date": "2024-01-20",
    "total_new": 156,
    "by_company": [
      { "company": "字节跳动", "count": 31 },
      { "company": "腾讯", "count": 12 }
    ]
  }
}
```

### 13.2 AI 求职日报

```
GET /api/v1/daily/digest
Authorization: Bearer {token}

Response:
{
  "code": 0,
  "data": {
    "date": "2024-01-20",
    "summary": "今日新增 156 个岗位，推荐关注字节跳动 AI 算法岗位...",
    "recommended": [ ... ],
    "trending_skills": ["AI Agent", "RAG"],
    "salary_highlights": "AI 算法工程师平均薪资较上周上涨 5%"
  }
}
```

---

## 十四、后台管理 API (Admin)

### 14.1 用户管理

```
GET    /api/v1/admin/users          -- 用户列表
PATCH  /api/v1/admin/users/:id      -- 更新用户（封禁/角色）
```

### 14.2 公司管理

```
GET    /api/v1/admin/companies       -- 公司列表
POST   /api/v1/admin/companies       -- 创建公司
PATCH  /api/v1/admin/companies/:id   -- 更新公司
DELETE /api/v1/admin/companies/:id   -- 删除公司
```

### 14.3 岗位管理

```
GET    /api/v1/admin/jobs            -- 岗位列表（含审核）
PATCH  /api/v1/admin/jobs/:id        -- 审核/上下架
```

### 14.4 AI 配置

```
GET    /api/v1/admin/ai-config       -- 查看 AI 配置
PUT    /api/v1/admin/ai-config       -- 更新 AI 配置

Request:
{
  "provider": "deepseek",            // openai / claude / gemini / deepseek
  "model": "deepseek-chat",
  "api_key": "sk-...",
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 4096
  }
}
```

### 14.5 数据统计

```
GET /api/v1/admin/statistics?period=weekly

Response:
{
  "users": { "total": 10000, "new_this_week": 500, "active_daily": 2000 },
  "jobs": { "total": 5000, "active": 3000, "new_today": 50 },
  "applications": { "total": 8000, "this_week": 300 },
  "referrals": { "total": 500, "valid": 350 }
}
```

---

## 十五、API 速率限制

| API | 限制 | 策略 |
|-----|:----:|------|
| 公开接口 | 60 req/min | IP 维度 |
| 认证接口 | 10 req/min | IP 维度 |
| 业务接口 | 120 req/min | 用户维度 |
| AI 接口 | 20 req/min | 用户维度 |
| 管理接口 | 60 req/min | 用户维度 |

---

## 十六、WebSocket 事件

### 16.1 连接

```
WS /ws?token=jwt_token
```

### 16.2 事件列表

| 事件 | 方向 | 说明 |
|------|:----:|------|
| notification.new | Server -> Client | 新通知 |
| job.status_changed | Server -> Client | 岗位状态变化 |
| referral.new | Server -> Client | 新内推 |
| ai.copilot.response | Server -> Client | AI 助手流式响应 |
| application.updated | Server -> Client | 投递状态更新 |

---

## 后续开发指引

| 后续步骤 | 引用 |
|---------|------|
| UI 设计 | 每个 API 对应一个页面的数据需求 |
| 前端开发 | API 路径对应 Next.js 页面路由 |
| 后端实现 | NestJS Module + Controller + Service 拆分 |
| AI 模块 | 统一 AI Provider 接口，支持多模型切换 |

---

## 下一步

[OK] API 设计完成（15 个模块），等待确认后进入 步骤 6：UI 设计
