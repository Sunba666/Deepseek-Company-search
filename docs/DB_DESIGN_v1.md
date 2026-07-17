# 数据库设计 — JobNav AI

> 版本：v1.0
> 状态：初稿
> 基于 PostgreSQL + TypeORM

---

## 一、设计原则

1. **规范化**：遵循第三范式（3NF），减少数据冗余
2. **可扩展**：预留扩展字段，支持未来需求
3. **性能优先**：合理索引设计，覆盖高频查询
4. **完整性**：外键约束、非空约束、默认值
5. **可追溯**：所有表包含 created_at / updated_at / deleted_at
6. **命名规范**：snake_case、表名复数、字段清晰

---

## 二、实体关系总览

```
+----------+     +----------+     +----------+
|  用户     |     |  公司     |     |  岗位     |
+----------+     +----------+     +----------+
     |                |                |
     | 1:N            | 1:N            | 1:N
     v                v                v
+----------+     +----------+     +----------+
| 收藏      |     | 岗位      |     | 内推信息  |
| 投递记录  |     | 面经      |     | 岗位标签  |
| 搜索历史  |     | 薪资数据  |     +----------+
| 消息通知  |     | 公司画像  |
+----------+     +----------+
```

---

## 三、核心表设计

### 3.1 用户表 (users)

```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    phone           VARCHAR(20) UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    nickname        VARCHAR(100),
    avatar_url      VARCHAR(500),
    role            VARCHAR(20) NOT NULL DEFAULT 'user',  -- user / admin / super_admin
    status          VARCHAR(20) NOT NULL DEFAULT 'active', -- active / banned / inactive

    -- 求职信息
    years_exp       INTEGER,
    education       VARCHAR(50),        -- 博士 / 硕士 / 本科 / 大专
    current_city    VARCHAR(100),
    current_company VARCHAR(200),
    current_title   VARCHAR(200),
    skills          TEXT[],
    expected_salary_min INTEGER,
    expected_salary_max INTEGER,
    preferred_cities   TEXT[],
    preferred_categories TEXT[],

    -- 认证
    email_verified  BOOLEAN DEFAULT FALSE,
    oauth_provider  VARCHAR(50),        -- github / google / wechat
    oauth_id        VARCHAR(255),
    refresh_token   TEXT,

    -- 时间
    last_login_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_created_at ON users(created_at);
```

### 3.2 公司表 (companies)

```sql
CREATE TABLE companies (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    name_en         VARCHAR(255),
    slug            VARCHAR(255) UNIQUE NOT NULL,   -- URL 友好标识
    logo_url        VARCHAR(500),
    website         VARCHAR(500),
    description     TEXT,
    industry        VARCHAR(100),                    -- 互联网 / 金融 / 医疗 ...
    scale           VARCHAR(50),                     -- <50 / 50-200 / 200-2000 / 2000+
    stage           VARCHAR(50),                     -- 天使轮 / A轮 / B轮 / C轮 / D轮 / 上市公司 / 独角兽
    stock_code      VARCHAR(20),
    is_listed       BOOLEAN DEFAULT FALSE,
    is_foreign      BOOLEAN DEFAULT FALSE,
    is_unicorn      BOOLEAN DEFAULT FALSE,
    is_state_owned  BOOLEAN DEFAULT FALSE,

    -- 招聘信息
    hiring_count    INTEGER DEFAULT 0,               -- 在招岗位数
    average_salary  INTEGER,                         -- 平均薪资 (K/month)
    interview_difficulty VARCHAR(20),                -- 容易 / 中等 / 困难
    education_requirement VARCHAR(50),
    referral_activity INTEGER DEFAULT 0,             -- 内推活跃度

    -- 地址信息
    city            VARCHAR(100),
    address         VARCHAR(500),

    -- 来源
    source          VARCHAR(100),
    source_url      VARCHAR(500),
    source_id       VARCHAR(255),

    -- 时间
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

CREATE INDEX idx_companies_name ON companies(name);
CREATE INDEX idx_companies_slug ON companies(slug);
CREATE INDEX idx_companies_industry ON companies(industry);
CREATE INDEX idx_companies_stage ON companies(stage);
CREATE INDEX idx_companies_city ON companies(city);
```

### 3.3 岗位表 (jobs)

```sql
CREATE TABLE jobs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      UUID NOT NULL REFERENCES companies(id),
    company_name    VARCHAR(255) NOT NULL,           -- 冗余，避免频繁 JOIN

    title           VARCHAR(255) NOT NULL,
    category        VARCHAR(50) NOT NULL,            -- 研发 / AI / 产品 / 运营 / 设计 ...
    sub_category    VARCHAR(50),                     -- Java / Golang / Python / 前端 ...

    -- 地点
    city            VARCHAR(100) NOT NULL,
    is_remote       BOOLEAN DEFAULT FALSE,

    -- 薪资
    salary_min      INTEGER,                         -- K/month
    salary_max      INTEGER,
    salary_monthly  INTEGER,                         -- 固定月薪
    stock_options   VARCHAR(100),                    -- 期权/股票说明

    -- 要求
    experience      VARCHAR(50),                     -- 应届 / 1-3年 / 3-5年 / 5年以上
    education       VARCHAR(50),                     -- 不限 / 大专 / 本科 / 硕士 / 博士
    skills          TEXT[],                          -- 技能标签数组

    -- 内容
    description     TEXT,                            -- 职位描述（Markdown）
    requirements    TEXT,                            -- 任职要求
    benefits        TEXT,                            -- 福利待遇
    description_raw TEXT,                            -- JD 原文

    -- 投递信息
    source_url      VARCHAR(500),                    -- 官网投递链接
    source_platform VARCHAR(100),                    -- 来源平台
    is_active       BOOLEAN DEFAULT TRUE,
    is_featured     BOOLEAN DEFAULT FALSE,

    -- 时间轴
    published_at    TIMESTAMPTZ,                     -- 发布时间
    expired_at      TIMESTAMPTZ,                     -- 截止时间
    closed_at       TIMESTAMPTZ,                     -- 关闭时间
    crawled_at      TIMESTAMPTZ,                     -- 采集时间
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

CREATE INDEX idx_jobs_company_id ON jobs(company_id);
CREATE INDEX idx_jobs_category ON jobs(category);
CREATE INDEX idx_jobs_sub_category ON jobs(sub_category);
CREATE INDEX idx_jobs_city ON jobs(city);
CREATE INDEX idx_jobs_experience ON jobs(experience);
CREATE INDEX idx_jobs_is_active ON jobs(is_active);
CREATE INDEX idx_jobs_published_at ON jobs(published_at);
CREATE INDEX idx_jobs_salary ON jobs(salary_min, salary_max);
CREATE INDEX idx_jobs_search ON jobs USING gin(skills);
CREATE INDEX idx_jobs_title_fts ON jobs USING gin(to_tsvector('simple', title));
```

### 3.4 内推信息表 (referrals)

```sql
CREATE TABLE referrals (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      UUID NOT NULL REFERENCES companies(id),
    company_name    VARCHAR(255) NOT NULL,
    job_id          UUID REFERENCES jobs(id),

    -- 内推信息
    referral_code   VARCHAR(100) NOT NULL,
    referral_link   VARCHAR(500),
    referrer_name   VARCHAR(100),
    referrer_title  VARCHAR(200),
    is_employee     BOOLEAN DEFAULT FALSE,           -- 是否员工认证
    is_verified     BOOLEAN DEFAULT FALSE,           -- 是否已验证

    -- 可信度评分
    confidence_score INTEGER DEFAULT 0,              -- 0-100
    confidence_level VARCHAR(20),                    -- 高可信 / 中等 / 低可信
    confidence_reason TEXT,                          -- 评分依据

    -- 验证信息
    verified_count  INTEGER DEFAULT 0,               -- 验证次数
    success_count   INTEGER DEFAULT 0,               -- 成功次数
    fail_count      INTEGER DEFAULT 0,               -- 失败次数
    last_verified_at TIMESTAMPTZ,

    -- 来源
    source          VARCHAR(100),                    -- 脉脉 / 知乎 / 牛客网 ...
    source_url      VARCHAR(500),

    -- 状态
    status          VARCHAR(20) DEFAULT 'active',    -- active / expired / invalid
    expires_at      TIMESTAMPTZ,
    notes           TEXT,

    -- 时间
    published_at    TIMESTAMPTZ,
    crawled_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

CREATE INDEX idx_referrals_company_id ON referrals(company_id);
CREATE INDEX idx_referrals_job_id ON referrals(job_id);
CREATE INDEX idx_referrals_status ON referrals(status);
CREATE INDEX idx_referrals_confidence ON referrals(confidence_score);
CREATE INDEX idx_referrals_code ON referrals(referral_code);
```

### 3.5 投递记录表 (applications)

```sql
CREATE TABLE applications (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    job_id          UUID NOT NULL REFERENCES jobs(id),
    company_id      UUID NOT NULL REFERENCES companies(id),

    -- 状态机
    status          VARCHAR(30) NOT NULL DEFAULT 'saved',
    -- saved -> ready_to_apply -> applied -> hr_viewed
    -- -> written_test -> interview_1 -> interview_2 -> hr_interview
    -- -> offer -> rejected -> withdrawn

    status_history  JSONB DEFAULT '[]',              -- 状态变更历史

    -- 内推信息
    referral_id     UUID REFERENCES referrals(id),
    referral_code_used VARCHAR(100),

    -- 投递信息
    applied_at      TIMESTAMPTZ,
    applied_url     VARCHAR(500),
    applied_note    TEXT,

    -- 反馈
    feedback        TEXT,
    rating          INTEGER,                         -- 1-5 星评价

    -- 时间
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ,

    UNIQUE(user_id, job_id)
);

CREATE INDEX idx_applications_user_id ON applications(user_id);
CREATE INDEX idx_applications_job_id ON applications(job_id);
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_applications_created_at ON applications(created_at);
```

### 3.6 收藏表 (favorites)

```sql
CREATE TABLE favorites (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    target_type     VARCHAR(20) NOT NULL,            -- job / company
    target_id       UUID NOT NULL,
    notes           VARCHAR(500),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(user_id, target_type, target_id)
);

CREATE INDEX idx_favorites_user_id ON favorites(user_id);
CREATE INDEX idx_favorites_target ON favorites(target_type, target_id);
```

### 3.7 面经表 (interviews)

```sql
CREATE TABLE interviews (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      UUID NOT NULL REFERENCES companies(id),
    job_category    VARCHAR(50),
    job_title       VARCHAR(255),

    -- 内容
    content         TEXT NOT NULL,
    interview_rounds INTEGER,                        -- 面试轮次
    duration_days   INTEGER,                         -- 面试周期
    difficulty      VARCHAR(20),                     -- 容易 / 中等 / 困难
    result          VARCHAR(50),                     -- offer / rejected / unknown

    -- 题目
    algorithm_questions TEXT[],                      -- 算法题
    knowledge_questions TEXT[],                      -- 八股文
    hr_questions        TEXT[],                      -- HR 问题

    -- 来源
    source          VARCHAR(100),
    source_url      VARCHAR(500),
    author_id       UUID REFERENCES users(id),

    -- 状态
    status          VARCHAR(20) DEFAULT 'pending',   -- pending / approved / rejected
    helpful_count   INTEGER DEFAULT 0,

    -- 时间
    interview_date  TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

CREATE INDEX idx_interviews_company_id ON interviews(company_id);
CREATE INDEX idx_interviews_category ON interviews(job_category);
CREATE INDEX idx_interviews_status ON interviews(status);
CREATE INDEX idx_interviews_difficulty ON interviews(difficulty);
```

### 3.8 薪资数据表 (salary_data)

```sql
CREATE TABLE salary_data (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      UUID REFERENCES companies(id),
    job_category    VARCHAR(50) NOT NULL,
    job_title       VARCHAR(255),
    city            VARCHAR(100) NOT NULL,
    experience      VARCHAR(50),

    -- 统计值
    salary_avg      NUMERIC(10,2),                   -- 平均薪资 (K/month)
    salary_median   NUMERIC(10,2),
    salary_p25      NUMERIC(10,2),
    salary_p75      NUMERIC(10,2),
    salary_min      NUMERIC(10,2),
    salary_max      NUMERIC(10,2),
    sample_count    INTEGER DEFAULT 0,               -- 样本数

    -- 来源
    source          VARCHAR(100),

    -- 时间
    period          VARCHAR(20),                     -- 2024-Q1
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(company_id, job_category, city, experience, period)
);

CREATE INDEX idx_salary_company ON salary_data(company_id);
CREATE INDEX idx_salary_category ON salary_data(job_category);
CREATE INDEX idx_salary_city ON salary_data(city);
```

### 3.9 公司画像表 (company_profiles)

```sql
CREATE TABLE company_profiles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      UUID UNIQUE NOT NULL REFERENCES companies(id),

    -- AI 分析结果
    overall_score   NUMERIC(3,1),                    -- 综合评分 0-10
    hiring_trend    VARCHAR(50),                     -- 增长 / 稳定 / 下降
    hiring_heat     INTEGER,                         -- 招聘热度 0-100
    avg_response_time VARCHAR(50),                   -- 平均响应时间
    referral_activity INTEGER,                       -- 内推活跃度 0-100

    -- 维度评分
    salary_score    NUMERIC(3,1),
    culture_score   NUMERIC(3,1),
    growth_score    NUMERIC(3,1),
    stability_score NUMERIC(3,1),

    -- 总结
    summary         TEXT,                            -- AI 总结
    pros            TEXT[],                          -- 优点
    cons            TEXT[],                          -- 缺点
    tips            TEXT,                            -- 求职建议

    -- 分析元数据
    analyzed_by     VARCHAR(50),                     -- AI 模型
    analyzed_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 3.10 AI 分析记录表 (ai_analyses)

```sql
CREATE TABLE ai_analyses (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    target_type     VARCHAR(20) NOT NULL,            -- job / company / resume / referral
    target_id       UUID NOT NULL,
    user_id         UUID REFERENCES users(id),

    -- 分析结果
    analysis_type   VARCHAR(50) NOT NULL,            -- jd_match / resume_match / referral_score / career_advice
    result          JSONB NOT NULL,                  -- 结构化分析结果
    confidence      NUMERIC(3,2),                    -- 置信度

    -- 使用信息
    model_used      VARCHAR(50),                     -- deepseek-chat / gpt-4 / claude-3
    tokens_used     INTEGER,
    response_time_ms INTEGER,

    -- 反馈
    user_rating     INTEGER,                         -- 用户对分析的评分
    user_feedback   TEXT,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ai_analyses_target ON ai_analyses(target_type, target_id);
CREATE INDEX idx_ai_analyses_type ON ai_analyses(analysis_type);
CREATE INDEX idx_ai_analyses_user ON ai_analyses(user_id);
CREATE INDEX idx_ai_analyses_created ON ai_analyses(created_at);
```

### 3.11 消息通知表 (notifications)

```sql
CREATE TABLE notifications (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),

    -- 类型
    type            VARCHAR(30) NOT NULL,
    -- job_update / job_closed / new_referral / referral_expired
    -- application_status / system / weekly_digest

    -- 内容
    title           VARCHAR(200) NOT NULL,
    body            TEXT,
    link            VARCHAR(500),                    -- 跳转链接
    metadata        JSONB,                           -- 附加数据

    -- 状态
    is_read         BOOLEAN DEFAULT FALSE,
    read_at         TIMESTAMPTZ,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_read ON notifications(user_id, is_read);
CREATE INDEX idx_notifications_type ON notifications(type);
CREATE INDEX idx_notifications_created ON notifications(created_at);
```

### 3.12 搜索历史表 (search_history)

```sql
CREATE TABLE search_history (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),

    -- 搜索内容
    query           TEXT NOT NULL,
    filters         JSONB,                           -- 筛选条件
    result_count    INTEGER,
    clicked_job_id  UUID REFERENCES jobs(id),

    -- 分析
    search_type     VARCHAR(20),                     -- keyword / ai / category
    is_ai_search    BOOLEAN DEFAULT FALSE,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_search_history_user ON search_history(user_id);
CREATE INDEX idx_search_history_created ON search_history(created_at);
CREATE INDEX idx_search_history_query ON search_history USING gin(to_tsvector('simple', query));
```

### 3.13 技能标签表 (skills)

```sql
CREATE TABLE skills (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(100) NOT NULL UNIQUE,
    category        VARCHAR(50),                     -- language / framework / tool / soft
    aliases         TEXT[],                          -- 别名
    popularity      INTEGER DEFAULT 0,               -- 热度
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_skills_category ON skills(category);
CREATE INDEX idx_skills_popularity ON skills(popularity);
```

### 3.14 岗位_技能关联表 (job_skills)

```sql
CREATE TABLE job_skills (
    job_id          UUID NOT NULL REFERENCES jobs(id),
    skill_id        UUID NOT NULL REFERENCES skills(id),
    is_required     BOOLEAN DEFAULT TRUE,
    importance      INTEGER DEFAULT 5,               -- 1-10
    PRIMARY KEY (job_id, skill_id)
);
```

### 3.15 用户行为日志表 (user_activity_logs)

```sql
CREATE TABLE user_activity_logs (
    id              BIGSERIAL PRIMARY KEY,
    user_id         UUID REFERENCES users(id),
    session_id      VARCHAR(100),

    -- 行为
    action          VARCHAR(50) NOT NULL,            -- page_view / search / click / apply / favorite
    target_type     VARCHAR(20),
    target_id       UUID,
    metadata        JSONB,

    -- 技术信息
    ip_address      VARCHAR(45),
    user_agent      TEXT,
    referer         VARCHAR(500),

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
) PARTITION BY RANGE (created_at);

CREATE INDEX idx_activity_user ON user_activity_logs(user_id);
CREATE INDEX idx_activity_action ON user_activity_logs(action);
CREATE INDEX idx_activity_created ON user_activity_logs(created_at);
```

### 3.16 系统日志表 (system_logs)

```sql
CREATE TABLE system_logs (
    id              BIGSERIAL PRIMARY KEY,
    level           VARCHAR(20) NOT NULL,            -- info / warn / error / fatal
    module          VARCHAR(50) NOT NULL,            -- auth / jobs / ai / crawler ...
    action          VARCHAR(100),
    message         TEXT,
    metadata        JSONB,
    stack_trace     TEXT,
    ip_address      VARCHAR(45),
    user_id         UUID REFERENCES users(id),

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_system_logs_level ON system_logs(level);
CREATE INDEX idx_system_logs_module ON system_logs(module);
CREATE INDEX idx_system_logs_created ON system_logs(created_at);
```

---

## 四、Redis 缓存设计

### 4.1 缓存键命名规范

```
prefix:module:key[:subkey]
```

示例：

```
cache:job:123                    -- 岗位详情
cache:company:abc               -- 公司详情
cache:hot:companies             -- 热门公司
cache:hot:jobs                  -- 热门岗位
cache:user:456:profile          -- 用户信息
cache:ai:analysis:job:123       -- AI 分析结果
```

### 4.2 缓存策略

| 数据类型 | TTL | 更新策略 |
|---------|:---:|---------|
| 热门公司列表 | 5 min | 定时刷新 |
| 热门岗位列表 | 5 min | 定时刷新 |
| 岗位详情 | 30 min | 写穿透 |
| 公司详情 | 30 min | 写穿透 |
| 用户会话 | 7 days | LRU |
| AI 分析结果 | 1 hour | 按需刷新 |
| 配置信息 | 1 hour | 事件驱动 |

### 4.3 数据结构

```json
// 热门排行榜 (Sorted Set)
key: "hot:companies"
score: 访问量
member: company_id

// 用户会话 (String)
key: "session:{token}"
value: { userId, role, expiresAt }

// 搜索缓存 (String)
key: "search:{hash(query+filters)}"
value: { results, total, page }
```

---

## 五、Elasticsearch 索引设计

### 5.1 岗位索引 (jobs)

```json
{
  "index": "jobs",
  "settings": {
    "analysis": {
      "analyzer": {
        "ik_smart_analyzer": { "type": "custom", "tokenizer": "ik_smart" }
      }
    }
  },
  "mappings": {
    "properties": {
      "title": { "type": "text", "analyzer": "ik_smart_analyzer", "fields": { "keyword": { "type": "keyword" } } },
      "company_name": { "type": "text", "analyzer": "ik_smart_analyzer" },
      "description": { "type": "text", "analyzer": "ik_smart_analyzer" },
      "city": { "type": "keyword" },
      "category": { "type": "keyword" },
      "skills": { "type": "keyword" },
      "salary_min": { "type": "integer" },
      "salary_max": { "type": "integer" },
      "experience": { "type": "keyword" },
      "is_active": { "type": "boolean" },
      "published_at": { "type": "date" }
    }
  }
}
```

### 5.2 公司索引 (companies)

```json
{
  "index": "companies",
  "mappings": {
    "properties": {
      "name": { "type": "text", "analyzer": "ik_smart_analyzer" },
      "name_en": { "type": "keyword" },
      "industry": { "type": "keyword" },
      "city": { "type": "keyword" },
      "description": { "type": "text", "analyzer": "ik_smart_analyzer" }
    }
  }
}
```

---

## 六、数据字典（枚举值）

### 6.1 岗位分类

```
category: 研发 / AI / 产品 / 运营 / 设计 / 测试 / 运维 / 数据分析 / 安全 / 算法 / 市场 / 销售 / 职能

sub_category:
  研发: Java / Golang / Python / C++ / 前端 / React / Vue / Node / 全栈 / Android / iOS
  AI: 大模型 / Agent / NLP / CV / 推荐算法 / 数据挖掘 / AI产品
  产品: 产品经理 / AI产品 / 数据产品 / 支付产品 / 增长产品
  运营: 用户运营 / 内容运营 / 社区运营 / 海外运营 / 增长运营
  设计: UI / UX / 视觉 / 动效 / 交互设计
```

### 6.2 城市列表

```
北京 / 上海 / 深圳 / 杭州 / 广州 / 成都 / 西安 / Remote
```

### 6.3 投递状态机

```
saved -> ready_to_apply -> applied -> hr_viewed -> written_test
  -> interview_1 -> interview_2 -> hr_interview -> offer
  -> rejected / withdrawn (任何状态都可转入)
```

### 6.4 用户角色

```
user (普通用户) -> admin (管理员) -> super_admin (超级管理员)
```

---

## 七、后续设计说明

1. **数据迁移**：使用 TypeORM migrations 管理数据库版本
2. **数据种子**：预置初始数据（热门城市、技能标签、公司模板）
3. **备份策略**：每日全量备份 + WAL 增量备份
4. **读写分离**：后期考虑主从复制，读库分担查询压力
5. **分库分表**：用户行为日志按时间分区，用户表按 ID 分片
6. **软删除**：所有业务表使用 deleted_at 实现软删除

---

## 下一步

[OK] 数据库设计完成，等待确认后进入 步骤 5：API 设计 + 步骤 6：UI 设计
