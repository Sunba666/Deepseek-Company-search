# 监控配置指南

## Prometheus 配置
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:3001']
    metrics_path: '/metrics'
```

## Grafana Dashboard
导入以下面板:
- Node Exporter Full
- PostgreSQL
- Redis
- Docker
- NestJS

## Sentry 集成
```typescript
// backend/src/main.ts
import * as Sentry from '@sentry/node';
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 0.1,
});
```

## 日志中心 (ELK)
```yaml
# docker-compose 扩展
  logstash:
    image: logstash:8.12.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
  kibana:
    image: kibana:8.12.0
    ports: ["5601:5601"]
```
