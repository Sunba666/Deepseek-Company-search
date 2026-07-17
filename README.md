# 🚀 JobNav AI — AI 驱动求职导航平台

**发现岗位 → AI 匹配 → 聚合内推 → 官网投递**

## 快速开始

```bash
# 一键启动全部服务
docker-compose up -d

# 访问
前端: http://localhost:3000
后端: http://localhost:3001
API 文档: http://localhost:3001/api/docs
```

## 技术栈

| 层 | 技术 |
|:--|------|
| **前端** | Next.js 16 · React 19 · TypeScript · Tailwind CSS · shadcn/ui |
| **后端** | NestJS 11 · TypeScript · Prisma ORM |
| **数据库** | PostgreSQL 16 · Redis 7 · Elasticsearch 8 |
| **存储** | MinIO (S3 兼容) |
| **AI** | DeepSeek / OpenAI / Claude（统一 Provider，可切换）|
| **部署** | Docker Compose · GitHub Actions CI/CD |

## 功能一览

| 功能 | 说明 |
|:----|------|
| 🏢 **公司聚合** | 500+ 公司信息、AI 画像、招聘趋势 |
| 🔍 **岗位搜索** | 多维筛选、AI 自然语言搜索、分类浏览 |
| 🎯 **内推广场** | AI 可信度评分、一键复制、官网跳转 |
| 🤖 **AI Copilot** | 流式对话、JD 分析、岗位推荐、简历优化 |
| 📋 **投递管理** | CRM 看板、11 态状态机、投递统计 |
| ⚙️ **管理后台** | 用户/岗位/内推管理、AI 配置、日志 |

## 目录结构

```
├── frontend/       # Next.js 前端 (11 页面)
├── backend/        # NestJS 后端 (15 模块, 40+ API)
├── docs/           # 产品/技术文档
├── docker-compose.yml
└── DEPLOYMENT.md   # 部署指南
```

## 开发

```bash
# 后端
cd backend && npm run start:dev

# 前端
cd frontend && npm run dev
```

## 授权

MIT © JobNav AI Team
