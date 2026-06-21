<div align="center">

# 求职尽调 · Company Lookup

**多维度公司查询与分析工具** — 帮助求职者全面了解目标公司

AI 驱动的求职研究平台 · 500+ 家持续发现公司 · 多源数据聚合 · 内推码智能采集

</div>

---

## 功能特性

### 🔍 公司查询
- 6 级实体解析管道 — 从简称、英文名、品牌名到工商注册名的智能匹配
- 知识库优先查询 — 500+ 家持续发现公司，新鲜度分层管理（7 天/30 天动态 TTL）
- 多维度数据展示：工商信息、薪酬福利、员工口碑、面试经验、司法风险

### 📊 公司对比
- 多公司横向对比，核心字段同屏展示
- AI 深度对比分析，生成差异化报告
- 综合评分体系，量化公司竞争力

### ⭐ 我的关注
- 一键收藏感兴趣的公司
- 关注列表页面，集中管理求职目标
- 数据持久化存储，跨会话保留

### 🎯 内推码聚合（NEW）
- 从脉脉、知乎自动采集内推码，聚合展示
- DeepSeek AI 批量验证内推码真伪（30min 周期）
- 用户反馈「已失效」兜底（3 次自动过期）
- 企业详情页内嵌该司内推码

### 🤖 AI 智能分析
- DeepSeek 驱动的高效分析（模型特性利用蒸馏数据，降低 Token 消耗）
- 求职者视角深度解读，个性化建议
- 面试题预测 + 模拟面试

### 🎯 求职匹配
- 按行业、城市、薪资、风险容忍度智能匹配
- 针对求职季优化的多维度评分引擎
- 匹配理由透明展示

### 📋 更多工具
- **Offer 对比** — 多 Offer 横向比较
- **简历优化** — AI 辅助简历改进
- **求职看板** — 招聘信息聚合看板

### 🛡️ 系统可靠性
- **4 个后台守护引擎** — 知识库维护、数据优化、公司发现、内推码采集，继承 **`BaseEngine`** 基类（统一线程管理 + 指数退避崩溃恢复 + 心跳标记）
- **统一健康监控** — 顶部大横幅（绿/黄/红）+ 实时心跳标记 + 崩溃计数 + 30s 自动刷新
- **API 统一健康端点** — `GET /api/health`，返回所有引擎状态
- **自动崩溃恢复** — 引擎异常时指数退避重试，不静默死亡
- **API 降级追踪** — 实时 API 不可用时自动降级 Mock 数据，并在系统状态页累计计数
- **知识库写回** — 实时 API 数据同步写回知识库，下次查询 0 网络开销
- **29 条集成测试** — `pytest tests/`，覆盖搜索、仪表盘、一致性、写回路径

---

## 技术栈

| 层 | 技术 |
|---|------|
| **后端框架** | Python 3.10+ · Flask 3.0+ |
| **模板引擎** | Jinja2 · HTMX（动态片段加载） |
| **数据存储** | SQLite（company_knowledge.db · company_data.db · jobboard.db） |
| **API 集成** | 天眼查 · 企查查 · 启信宝 · Tavily · DeepSeek |
| **AI 模型** | DeepSeek Chat（实体消歧 · 报告生成 · 数据蒸馏 · 内推码验证） |
| **后台引擎** | threading 守护线程 · BaseEngine 基类（维护 · 优化 · 发现 · 采集） |
| **测试** | pytest · pytest-asyncio |
| **代码质量** | Black · Ruff |

---

## 快速开始

### 环境要求

- Python 3.10+
- pip

### 安装

```bash
# 克隆仓库
git clone https://github.com/Sunba666/Deepseek-Company-search.git
cd Deepseek-Company-search

# 安装项目及依赖
pip install -e .

# 安装开发依赖（可选，运行测试需要）
pip install -e ".[dev]"
```

### 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，配置你的 API Key（详见下方 [API 数据源](#-api-数据源) 说明）。

### 启动 Web 服务

```bash
# 方式一：CLI 命令
company-lookup

# 方式二：Python 模块
python -m company_lookup

# 方式三：开发模式（热重载）
python run.py
```

访问 **http://localhost:5000**。

### 命令行模式

```bash
company-lookup 阿里巴巴
```

直接输出公司信息摘要，适合快速查询和脚本集成。

---

## 环境变量配置

```ini
# ========== Flask 基础 ==========
FLASK_ENV=development              # development / production
SECRET_KEY=change-me-in-production
LOG_LEVEL=INFO
SESSION_COOKIE_SECURE=false

# ========== 工商信息 API ==========
TIANYACHA_API_KEY=                # 天眼查（推荐） https://open.tianyancha.com
QICHACHA_API_KEY=                 # 企查查         https://www.qcc.com

# ========== 舆情搜索 API ==========
TAVILY_API_KEY=                   # Tavily（推荐）   https://tavily.com
BING_API_KEY=                     # 必应搜索         https://portal.azure.com

# ========== 司法风险 API ==========
QIXINBAO_API_KEY=                 # 启信宝         https://www.qixin.com

# ========== AI 分析 API ==========
DEEPSEEK_API_KEY=                 # DeepSeek        https://platform.deepseek.com
```

> **注意**：所有 API 均可选配置。未配置的系统自动降级为 Mock 数据（预置 12 家公司的完整示例数据），适合开发体验和生产环境的功能预览。

---

## API 数据源

### 三层架构

```
用户查询
  │
  ├─ ① 实体解析层 — 简称 → 标准工商注册名
  │    ├─ BrandMapping 白名单（94 个品牌）
  │    ├─ SQLite 别名表
  │    ├─ 模糊/前缀匹配
  │    ├─ Tavily 搜索补全
  │    ├─ DeepSeek AI 消歧
  │    └─ 关键词兜底
  │
  ├─ ② 数据聚合层 — 并行调用多个 API
  │    ├─ 天眼查 / 企查查 → 工商信息
  │    ├─ Tavily / 必应   → 舆情口碑
  │    ├─ 启信宝 / 裁判文书网 → 司法风险
  │    └─ 薪资/面试/口碑 → Mock 或插件
  │
  └─ ③ 知识库层 — 数据持久化
       ├─ company_knowledge.db（维度数据 + 蒸馏摘要）
       └─ company_data.db（原始缓存）
```

### 数据新鲜度（动态 TTL）

| 公司热度 | 新鲜窗口 | 刷新窗口 |
|---------|---------|---------|
| 🔥 高频查询 | 3 天 | 14 天 |
| 📊 常规 | 7 天 | 30 天 |
| ❄️ 低频 | 14 天 | 60 天 |

- 新鲜窗口内 → 直接返回知识库数据，0 网络调用
- 新鲜窗口外 → 返回旧数据 + 异步后台刷新
- 超过刷新窗口 → 标记过时，队列调度重新采集

---

## 项目结构

```
company-lookup/
├── data/                          # 数据文件
│   ├── mock_companies.json        # 12 家公司的 Mock 数据
│   ├── favorites.json             # 用户收藏
│   └── jobboard.db                # 求职看板 + 内推码数据
├── src/
│   └── company_lookup/
│       ├── app.py                 # Flask 应用工厂 + 后台引擎启动
│       ├── ai_analyzer.py         # AI 分析入口 + Mock 数据生成
│       ├── cli.py                 # 命令行入口
│       ├── config.py              # 配置类
│       ├── comparer.py            # 公司对比核心逻辑
│       ├── data_store.py          # 缓存层
│       ├── htmx_utils.py          # HTMX 工具函数
│       ├── routes/                # Flask 路由
│       │   ├── main.py            # 首页 + 导航 + 求职看板
│       │   ├── company.py         # 搜索 + 详情 + 系统状态 + 收藏
│       │   ├── compare.py         # 对比
│       │   ├── config.py          # API Key 配置页面
│       │   └── referral.py        # 内推码聚合页 + 搜索 + 反馈
│       ├── services/              # 业务逻辑层
│       │   ├── orchestrator.py    # 多源协同调度器
│       │   ├── entity_resolver.py # 6 级实体解析器
│       │   ├── unified_data_service.py # 统一数据服务（知识库优先）
│       │   ├── aggregator.py      # 数据聚合器（API + Mock 降级）
│       │   ├── knowledge_db.py    # 知识库数据库操作
│       │   ├── knowledge_collector.py  # 知识库采集器
│       │   ├── knowledge_maintainer.py # 维护引擎（继承 BaseEngine）
│       │   ├── optimization_engine.py  # 优化引擎（继承 BaseEngine）
│       │   ├── discovery_engine.py     # 发现引擎（继承 BaseEngine）
│       │   ├── referral_collector.py   # 内推码采集引擎（继承 BaseEngine）
│       │   ├── base_engine.py          # 后台引擎基类（线程管理+崩溃恢复+心跳）
│       │   ├── referral_service.py     # 内推码统一接口层
│       │   ├── referral_db.py          # 内推码数据库操作
│       │   ├── referral_ai_validator.py # 内推码 AI 批量验证
│       │   ├── scrapers/               # 内推码采集适配器
│       │   │   ├── __init__.py         # Scraper ABC 协议
│       │   │   ├── maimai.py           # 脉脉采集器
│       │   │   └── zhihu.py            # 知乎采集器
│       │   ├── job_matcher.py     # 求职匹配引擎
│       │   ├── entity_api.py      # 天眼查/企查查客户端
│       │   ├── sentiment_api.py   # Tavily/必应客户端
│       │   ├── risk_api.py        # 启信宝/裁判文书网客户端
│       │   ├── search_service.py  # 搜索校验（人名/公司名判定）
│       │   ├── config_manager.py  # API Key 管理 + 在线验证
│       │   ├── mock_data.py       # Mock 数据提供者
│       │   ├── dto.py             # 数据模型
│       │   ├── api_client.py      # 统一 HTTP 客户端
│       │   └── base_client.py     # 熔断器 + 基类
│       ├── db/
│       │   └── cache_db.py        # SQLite 缓存数据库
│       ├── plugins/               # 插件目录
│       ├── static/
│       │   └── style.css          # 全局样式 + 暗色模式
│       └── templates/             # Jinja2 模板
│           ├── base.html          # 布局 + 导航
│           ├── index.html         # 首页
│           ├── dashboard.html     # 公司查询
│           ├── company_detail.html # 公司详情 + ⭐ 关注 + 内推码
│           ├── compare.html       # 公司对比
│           ├── favorites.html     # 我的关注
│           ├── job_match.html     # 求职匹配
│           ├── system_health.html # 系统运行状态（含心跳监控）
│           ├── referral.html      # 内推码聚合页
│           ├── partials/
│           │   ├── referral_list.html   # 内推码列表片段
│           │   └── referral_codes.html  # 详情页内推码片段
│           └── ...
├── tests/
│   ├── conftest.py                # Flask test client fixture
│   └── test_search.py             # 29 条集成测试
├── docs/
│   └── adr/
│       └── ADR-001-api-data-writeback.md
├── .env.example                   # 环境变量模板
├── pyproject.toml                 # 项目元数据 + 工具配置
└── README.md
```

---

## 后台引擎

四个后台守护线程（继承 `BaseEngine` 基类），自动随应用启动（可通过 `DISABLE_BACKGROUND_SERVICES=true` 禁用）：

| 引擎 | 频率 | 职责 |
|------|------|------|
| **知识库维护引擎** | 10min 验证 / 1h 完整性 / 6h 刷新 | 验证关键字段、补充缺失维度、刷新 >30天过期数据、生成健康报告 |
| **永续优化引擎** | 2min 快速预检 / 10min 全量扫描 | 自动扫描并修复数据问题（API Key 失效、维度不足、Mock 降级） |
| **持续发现引擎** | 轮流执行 6 种发现策略 | 通过招聘信息、行业关键词、关联企业扩展发现新公司 |
| **内推码采集引擎** | 1h 采集 / 30min AI 验证 | 从脉脉、知乎采集内推码，DeepSeek 批量验证真伪 |

引擎状态在 **`/admin/system`** 可视化，包括：
- 🟢🟡🔴 顶部大横幅（整体健康状态一览）
- 每个引擎的运行状态、累计操作、心跳时间、崩溃次数
- 页面每 30 秒自动刷新

也可通过 `GET /api/health` 获取统一 JSON 状态。

---

## 测试

```bash
# 运行全部测试
pytest tests/

# 详细输出
pytest tests/ -v

# 单类测试
pytest tests/test_search.py::TestHomepageSearch -v
```

测试覆盖：
- **首页搜索** — 6 个知名公司成功 + 3 个无效输入场景
- **仪表盘搜索** — 11 个知名公司成功 + 3 个人名拦截
- **路径一致性** — 首页和仪表盘对同一公司的行为一致性验证
- **知识库写回** — 实时 API 数据写入维度表 + 时间戳更新验证

---

## 贡献指南

1. **Fork** 本仓库
2. **创建特性分支** (`git checkout -b feat/my-feature`)
3. **提交改动** (`git commit -am 'feat: add my feature'`)
4. **推送分支** (`git push origin feat/my-feature`)
5. **发起 Pull Request**

### 开发规范

- 代码风格：Black（line-length=100）+ Ruff
- 提交信息遵循 [Conventional Commits](https://www.conventionalcommits.org/)
- 新功能需包含测试（`pytest tests/` 全绿）
- 不引入新依赖前先评估是否能用现有方案解决

### 架构约定

- 路由层（`routes/`）保持轻薄，业务逻辑下沉到 `services/`
- 数据源新增一条 API 时：实现客户端类 → 注册到聚合器 → 修改 `MockDataProvider` 降级
- 新增后台引擎：继承 `BaseEngine` → 实现 `_run_loop()` → 在 `app.py` 启动
- 新增内推码平台：实现 Scraper ABC → 注册到 `ReferralCollector`

---

## 💰 赞助支持

如果你觉得这个项目对你有帮助，欢迎请作者喝杯咖啡 ☕️

| 微信支付 | 支付宝 |
|:---:|:---:|
| <img src="https://raw.githubusercontent.com/Sunba666/Deepseek-Company-search/master/src/company_lookup/static/images/wechat_pay.jpg" width="200"/> | <img src="https://raw.githubusercontent.com/Sunba666/Deepseek-Company-search/master/src/company_lookup/static/images/alipay.jpg" width="200"/> |

---

## License

MIT © Company Lookup Team

---

<div align="center">

**Built with ❤️ for job seekers**

</div>
