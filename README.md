# 🚀 JobNav AI — AI 驱动求职导航平台

**发现岗位 · AI 匹配 · 聚合内推 · 官网投递**

一站式 AI 求职导航平台：聚合企业信息、招聘动态和内推资源，结合 AI 技术为求职者提供从岗位发现到投递管理的全流程支持。

---

## 快速开始

```bash
# 1. 配置 DeepSeek API Key（在 backend/.env 中）
AI_API_KEY=sk-your-key-here

# 2. 一键启动全部服务（6 个容器）
docker compose -f docker-compose.yml up -d

# 3. 初始化数据库 + 填充样例数据
cd backend
npx prisma migrate dev --name init
npx prisma db seed
```

### 访问地址

| 服务 | 地址 |
|:----|------|
| 🌐 前端 | http://localhost:3000 |
| 🔌 后端 API | http://localhost:3001 |
| 📖 API 文档 | http://localhost:3001/api/docs |
| 📧 测试账号 | `admin@jobnav.ai` / `admin123` |

---

## 技术栈

| 层 | 技术 |
|:--|------|
| **前端** | Next.js 16 · React 19 · TypeScript · Tailwind CSS · shadcn/ui · Zustand |
| **后端** | NestJS 11 · TypeScript · Prisma ORM · PostgreSQL |
| **缓存** | Redis 7 |
| **搜索** | Elasticsearch 8 |
| **存储** | MinIO (S3 兼容) |
| **AI** | DeepSeek API（可切换 OpenAI） |
| **部署** | Docker Compose · 6 容器编排 |

---

## 功能一览（17 个路由，40+ API 端点）

### 🏢 公司聚合
| 页面 | 说明 |
|:----|------|
| `/companies` | 浏览 7 个行业分类、多维度筛选 |
| `/companies/[slug]` | 公司详情 + 在招岗位 |

### 🔍 岗位搜索
| 页面 | 说明 |
|:----|------|
| `/jobs` | 多维筛选（城市/经验/学历/薪资）、分类浏览、AI 搜索 |
| `/jobs/[id]` | 岗位详情、技能标签、AI 匹配分析 |

### 🎯 内推广场
| 页面 | 说明 |
|:----|------|
| `/referrals` | 可信度评分（算法驱动）、一键复制、官网跳转、收藏 |
| 发布内推 | 填写表单 → 自动计算可信度 |
| 评价系统 | 1-5 星评分、响应速度、是否成功入职 → 动态更新可信度 |
| 举报系统 | 无效/垃圾/过期举报，影响可信度分数 |

### 🤖 AI Copilot
| 功能 | 说明 |
|:----|------|
| 💬 流式对话 | 多轮上下文、会话管理（新建/切换/删除/收藏） |
| 📄 **简历分析** | 上传 TXT/MD 简历 → AI 输出结构化分析（优势/改进/推荐方向） |
| 🎙️ **模拟面试** | 5 轮 AI 面试 → 逐轮反馈 → 最终评分（技术/沟通/解决问题） |
| 🔍 **JD 分析** | 粘贴 JD → AI 分析匹配度/已具备/缺失技能 |
| 📊 **个性化推荐** | 基于技能/搜索历史/收藏/投递 → AI 推荐岗位+公司+学习建议 |

### 📋 求职 CRM（投递管理）
| 页面 | 说明 |
|:----|------|
| `/pipeline` | 看板/列表/统计 三视图 |
| 状态流转 | 10 态状态机：收藏 → 准备 → 已投递 → HR查看 → 笔试 → 一面 → 二面 → HR面 → Offer → 拒绝 |
| 面试记录 | 跟踪每轮面试（面试官/时长/反馈/结果） |
| 备注管理 | 随时记录求职备注 |
| 薪资记录 | 期望薪资 + 实际薪资 |

### 👤 用户系统
| 页面 | 说明 |
|:----|------|
| `/login` | 注册/登录（JWT Token） |
| `/settings` | 个人信息编辑、修改密码、简历管理 |
| 角色体系 | `user`（求职者）· `admin`（企业）· `super_admin`（超级管理员） |

### ⚙️ 企业管理后台
| 页面 | 说明 |
|:----|------|
| `/admin` | 概览仪表板（用户/公司/岗位/内推/投递统计） |
| 用户管理 | 角色切换、启用/禁用 |
| 岗位管理 | 上架/下架、发布新岗位（完整表单） |
| 系统日志 | 实时查看系统日志 |

### 其他页面
| 路由 | 说明 |
|:----|------|
| `/about` | 关于我们 |
| `/privacy` | 隐私政策 |
| `/terms` | 服务条款 |
| `/feedback` | 意见反馈（类型选择 + 表单提交） |

---

## 目录结构

```
company-lookup/
├── frontend/                     # Next.js 16 前端
│   ├── src/
│   │   ├── app/                  # 17 个路由页面
│   │   │   ├── (public)/         # 公开页面（Navbar + Footer）
│   │   │   ├── (dashboard)/      # 仪表板页面（仅 Navbar）
│   │   │   └── admin/            # 管理后台
│   │   ├── components/           # 共享组件（card/button/modal/badge...）
│   │   ├── lib/ai/               # AI Provider 抽象层
│   │   ├── services/api.ts       # API 客户端（axios）
│   │   ├── store/                # Zustand 状态管理
│   │   └── types/                # TypeScript 类型定义
│   └── Dockerfile
│
├── backend/                      # NestJS 11 后端
│   ├── prisma/
│   │   ├── schema.prisma         # 16 个数据模型
│   │   ├── seed.ts               # 种子数据（7 公司/6 岗位/10 内推）
│   │   └── migrations/           # 数据库迁移
│   ├── src/
│   │   ├── modules/
│   │   │   ├── ai/               # AI 服务（DeepSeek 代理/推荐/面试）
│   │   │   ├── auth/             # 认证（JWT/密码找回）
│   │   │   ├── user/             # 用户 + 简历管理
│   │   │   ├── company/          # 公司 CRUD
│   │   │   ├── job/              # 岗位 CRUD
│   │   │   ├── referral/         # 内推（发布/收藏/评价/举报）
│   │   │   ├── application/      # 投递管理（状态机/面试记录）
│   │   │   └── admin/            # 管理后台
│   │   └── common/               # 公共（拦截器/过滤器/守卫）
│   └── Dockerfile
│
└── docker-compose.yml            # 6 容器编排
```

---

## 数据模型（16 个）

| 模型 | 说明 |
|:----|------|
| `User` | 用户（支持角色/技能/薪资偏好） |
| `Company` | 企业信息 |
| `Job` | 岗位（含技能/薪资/分类） |
| `Referral` | 内推（含可信度评分/验证/成功统计） |
| `Application` | 投递（11 态状态机 + 历史记录） |
| `InterviewRecord` | 面试记录 |
| `Favorite` | 收藏（岗位/公司） |
| `Resume` | 简历管理 |
| `SearchHistory` | 搜索历史（用于推荐） |
| `ReferralFavorite/Rating/Report` | 内推收藏/评价/举报 |
| `AIConversation/AIMessage` | AI 对话持久化 |
| `Notification/ActivityLog/SystemLog` | 通知/日志 |

---

## AI 可信度评分算法

```
base = 50
+15  员工内推
+5/次 验证次数 (上限 20)
+15x 历史成功率
+10x 平均用户评分/5
+3/次 快速响应
-2/次 慢速响应
最终值 [10, 100]
```

---

## API 概览（主要端点）

| 模块 | 端点 | 功能 |
|:----|:-----|------|
| **Auth** | `POST /api/v1/auth/login` | 登录 |
| | `POST /api/v1/auth/register` | 注册 |
| | `POST /api/v1/auth/change-password` | 修改密码 |
| | `POST /api/v1/auth/forgot-password` | 忘记密码 |
| **AI** | `POST /api/v1/ai/chat` | AI 对话 |
| | `POST /api/v1/ai/stream` | 流式对话 |
| | `POST /api/v1/ai/analyze-resume` | 简历分析 |
| | `POST /api/v1/ai/mock-interview` | 模拟面试 |
| | `POST /api/v1/ai/personalized-recommend` | 个性化推荐 |
| **Referral** | `GET/POST /api/v1/referrals` | 内推列表/发布 |
| | `POST /api/v1/referrals/:id/favorite` | 收藏 |
| | `POST /api/v1/referrals/:id/rate` | 评价 |
| | `POST /api/v1/referrals/:id/report` | 举报 |
| **Application** | `GET/POST /api/v1/applications` | 投递列表/创建 |
| | `PATCH /api/v1/applications/:id/status` | 状态推进 |
| | `GET/POST /api/v1/applications/:id/interviews` | 面试记录 |

---

## 开发

```bash
# 后端开发
cd backend
cp .env.example .env     # 配置 DATABASE_URL 和 AI_API_KEY
npm run start:dev

# 前端开发
cd frontend
npm run dev

# 数据库
npx prisma migrate dev   # 本地迁移
npx prisma db seed       # 填充种子数据

# 构建检查
cd frontend && npm run build
```

---

## Docker 部署

```bash
# 构建并启动
docker compose down
docker compose build --no-cache   # 首次构建
docker compose up -d

# 初始化数据库
docker compose exec backend npx prisma migrate dev --name init
docker compose exec backend npx prisma db seed

# 查看日志
docker compose logs -f backend
docker compose logs -f frontend

# 检查状态
docker compose ps
```

---

## 项目路线图

| Phase | 状态 | 内容 |
|:-----|:----|:-----|
| 8.1 | ✅ | 系统稳定化 — Docker 6 服务运行、编码修复 |
| 8.2 | ✅ | 真实数据联调 — 8 页面从 Mock 到真实 API |
| 8.3 | ✅ | 内推广场完善 — 发布/收藏/评价/举报/可信度算法 |
| 8.4 | ✅ | AI Copilot 升级 — 对话持久化/简历分析/模拟面试 |
| 8.5 | ✅ | 求职 CRM — 看板/列表/统计 + 面试记录 |
| 8.6 | ✅ | 用户系统 — 注册/密码/简历/设置页 |
| 8.7 | ✅ | AI 推荐系统 — 个性化推荐引擎 |
| 8.8 | ✅ | 企业端管理后台 — 用户/岗位/日志管理 |
| 8.9 | ✅ | 稳定性与体验 — error/loading/empty 状态全覆盖 |

---

## License

MIT © JobNav AI Team
