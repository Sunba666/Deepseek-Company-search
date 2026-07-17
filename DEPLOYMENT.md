# JobNav AI 部署指南

> 版本: v1.0 RC  
> 环境: Production

---

## 一、环境要求

| 组件 | 版本 | 说明 |
|------|:----:|------|
| Docker | 24+ | 容器运行环境 |
| Docker Compose | 2.20+ | 多容器编排 |
| Node.js | 20 LTS | 本地开发 |
| PostgreSQL | 16 | 主数据库 |
| Redis | 7 | 缓存 + 队列 |
| Elasticsearch | 8.12 | 全文搜索 |
| MinIO | latest | 对象存储 |

## 二、快速启动（开发环境）

```bash
# 1. 克隆项目
git clone https://github.com/jobnav-ai/jobnav.git
cd jobnav

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 填写 AI_API_KEY 等配置

# 3. 启动所有服务
docker-compose up -d

# 4. 数据库迁移
cd backend
npx prisma migrate dev
npx prisma db seed

# 5. 访问
# 前端: http://localhost:3000
# 后端: http://localhost:3001
# API 文档: http://localhost:3001/api/docs
# MinIO: http://localhost:9001 (admin/minioadmin)
```

## 三、环境变量说明

### 后端 (.env)

| 变量 | 默认值 | 说明 |
|------|--------|------|
| DATABASE_URL | postgresql://jobnav:jobnav123@localhost:5432/jobnav | PostgreSQL 连接 |
| REDIS_URL | redis://localhost:6379 | Redis 连接 |
| JWT_SECRET | （必填） | JWT 签名密钥 |
| AI_API_KEY | （必填） | AI 模型 API Key |
| AI_PROVIDER | deepseek | AI 模型提供商 |
| AI_MODEL | deepseek-chat | AI 模型名称 |
| CORS_ORIGIN | http://localhost:3000 | CORS 允许源 |
| S3_ENDPOINT | http://localhost:9000 | MinIO 端点 |
| S3_ACCESS_KEY | minioadmin | MinIO 访问密钥 |
| S3_SECRET_KEY | minioadmin | MinIO 秘密密钥 |

### 前端 (.env.local)

| 变量 | 默认值 | 说明 |
|------|--------|------|
| NEXT_PUBLIC_API_URL | http://localhost:3001/api/v1 | 后端 API 地址 |
| NEXT_PUBLIC_SITE_URL | http://localhost:3000 | 站点 URL |

## 四、生产部署

### 4.1 域名 & HTTPS（Nginx）

```nginx
# /etc/nginx/sites-available/jobnav
server {
    listen 443 ssl;
    server_name jobnav.ai;

    ssl_certificate /etc/letsencrypt/live/jobnav.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/jobnav.ai/privkey.pem;

    # Frontend
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API
    location /api/ {
        proxy_pass http://127.0.0.1:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://127.0.0.1:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Uploads
    location /uploads/ {
        proxy_pass http://127.0.0.1:3001;
        proxy_set_header Host $host;
    }
}
```

### 4.2 生产启动

```bash
# 构建并启动
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 查看日志
docker-compose logs -f backend frontend

# 数据备份
docker exec jobnav-postgres pg_dump -U jobnav jobnav > backup/$(date +%Y%m%d).sql
```

### 4.3 性能优化

- 前端: Vercel 部署（推荐）
- 后端: 2-4 副本水平扩展
- PostgreSQL: 连接池（pgbouncer）
- Redis: Cluster 模式（生产）
- Elasticsearch: 3 节点集群
- CDN: 静态资源加速

## 五、数据库迁移

```bash
# 创建迁移
npx prisma migrate dev --name init

# 生产迁移
npx prisma migrate deploy

# 数据填充
npx prisma db seed

# Prisma Studio（数据管理）
npx prisma studio
```

## 六、监控与维护

### 6.1 健康检查

```bash
# 系统健康
curl http://localhost:3001/api/v1/health

# 预期响应:
# { "status": "ok", "database": "ok", "cache": { "hits": 0, "misses": 0, "hitRate": "N/A" } }
```

### 6.2 日志

```bash
# 实时日志
docker-compose logs -f

# 错误日志
docker-compose logs backend | grep ERROR
```

### 6.3 备份策略

- 数据库: 每日全量备份，保留 7 天
- 文件存储: MinIO 跨区域复制
- 配置文件: Git 仓库管理

## 七、安全清单

- [ ] JWT 密钥更换为高强度随机字符串
- [ ] HTTPS 证书配置
- [ ] CORS 限制为具体域名
- [ ] API 限流（Throttler 已配置）
- [ ] Helmet 安全头已启用
- [ ] 数据库密码更换
- [ ] MinIO 访问密钥更换
- [ ] AI API Key 加密存储
- [ ] 日志脱敏配置
- [ ] 定期安全审计

## 八、故障排查

| 问题 | 可能原因 | 解决 |
|------|---------|------|
| 数据库连接失败 | PostgreSQL 未启动 | docker-compose restart postgres |
| Redis 连接失败 | Redis 未启动 | docker-compose restart redis |
| AI 返回错误 | API Key 无效 | 检查 .env 中的 AI_API_KEY |
| 搜索无结果 | ES 索引未创建 | 运行同步脚本 |
| 文件上传失败 | MinIO Bucket 未创建 | 创建 jobnav bucket |
| 前端 API 报错 | 后端未启动 | docker-compose restart backend |
