# JobNav AI 运维手册

> 版本: v1.0 GA
> 维护团队: SRE

---

## 一、日常运维任务

### 每日检查
```bash
# 1. 系统健康
curl http://localhost:3001/api/v1/health

# 2. 容器状态
docker ps

# 3. 磁盘使用
df -h

# 4. 数据库大小
docker exec jobnav-postgres psql -U jobnav -c "SELECT pg_database_size('jobnav')/1024/1024 as size_mb;"
```

### 每周任务
- 检查错误日志: `docker-compose logs --tail=100 backend | grep ERROR`
- 数据库备份: `./scripts/backup.sh`
- 检查 AI Token 消耗
- 更新内推码状态

### 每月任务
- 系统更新 (apt update)
- 安全补丁
- 性能基准测试
- 日志轮转检查

## 二、告警规则

| 指标 | 阈值 | 动作 |
|------|:----:|------|
| API 响应时间 | > 500ms | 告警 |
| 错误率 | > 1% | 告警 |
| CPU 使用率 | > 80% | 扩容 |
| 内存使用率 | > 85% | 扩容 |
| 磁盘使用率 | > 90% | 清理 |
| AI API 错误率 | > 5% | 切换 Provider |
| PostgreSQL 连接数 | > 80 | 告警 |

## 三、扩容方案

### 垂直扩容
- 升级服务器配置 (CPU/RAM)
- PostgreSQL: shared_buffers = 内存的 25%
- Node.js: --max-old-space-size

### 水平扩容
- 后端: `docker-compose up -d --scale backend=3`
- PostgreSQL: 主从复制
- Redis: Cluster 模式
- Elasticsearch: 多节点集群

## 四、故障恢复

### 数据库恢复
```bash
# 从备份恢复
docker exec -i jobnav-postgres psql -U jobnav jobnav < backup/20240101.sql

# 重置并迁移
npx prisma migrate deploy
npx prisma db seed
```

### 缓存重建
```bash
# 清除 Redis
docker exec jobnav-redis redis-cli FLUSHALL

# 重建 ES 索引
curl -X POST http://localhost:9200/_reindex
```

### 容器恢复
```bash
# 重启单个服务
docker-compose restart backend

# 全量重建
docker-compose down -v
docker-compose up -d
```

## 五、备份策略

```bash
#!/bin/bash
# scripts/backup.sh
BACKUP_DIR="/backups/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# 数据库
docker exec jobnav-postgres pg_dump -U jobnav jobnav | gzip > $BACKUP_DIR/db.sql.gz

# 上传到 MinIO
docker exec jobnav-minio mc cp $BACKUP_DIR/db.sql.gz local/jobnav-backups/

# 保留 7 天
find /backups -mtime +7 -delete
```

## 六、日志管理

```yaml
# docker-compose 日志配置
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## 七、安全运维

- 每月检查安全更新
- 每季度权限审计
- 每半年渗透测试
- 密钥定期轮换 (90天)
- 访问日志保留 180 天
