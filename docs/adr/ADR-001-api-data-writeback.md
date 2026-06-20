# ADR-001: 实时 API 数据写入知识库

**状态**：已实施
**日期**：2026-06-20
**Grilling 参与者**：Karpathy 视角 + 实际代码排查

## 语境

用户搜索公司时，缓存未命中后会调用实时 API 获取数据。
但这些数据只写入了旧缓存（`company_data.db`），没有回填知识库（`company_knowledge.db`），
因为 `_populate_knowledge()` 对已存在公司直接 `return`。

## 决策：C 变体

实时 API 数据回填知识库的维度表 + 更新时间戳，**不触发蒸馏数据重新生成**。

| 要做 | 不做 |
|------|------|
| API 返回的维度写入 `company_data` 表 | 不重新生成 `distilled` 数据 |
| 更新 `companies.last_verified_at` | 不触发 DeepSeek 调用 |
| 写入时标记 `source`（如"天眼查"） | 不改后台维护引擎逻辑 |

## 键名映射（API 层 → 知识库 data_type）

| API 层 source_id | 知识库 data_type |
|---|---|
| `tianyacha` / `qichacha` / `gsxt` | `basic` |
| `tavily` / `bing` | `sentiment` |
| `wenshu` / `qixinbao` | `risk` |
| `salary` | `salary` |
| `culture` | `culture` |
| `interview` | `interview` |
| `ai_summary` | `ai_summary` |
| `deepseek` / `mock` | 跳过 |

## 并发保证

`INSERT OR REPLACE INTO company_data (company_id, data_type, ...)` 是行级 UPSERT，
不同维度并发写互不阻塞，相同维度后写覆盖。

## 边界行为

| 场景 | 行为 |
|------|------|
| 公司不在知识库中 | 启动后台 `collect_company()` 全量采集（原逻辑不变） |
| API 返回部分维度 | 只覆盖有返回的维度，其他维度保留旧值 |
| API 全部失效 | `raw_data` 为空，`written=0`，不更新时间戳 |

## 不变的部分

- `distilled` 维度不重新生成
- 后台维护引擎照常运行
- 现有测试全部通过

## 涉及的提交

- `knowledge_db.py`: 新增 `update_verified_at()` 方法
- `unified_data_service.py`: 重写 `_populate_knowledge()`，移除 `return`，添加反向映射
- `tests/test_search.py`: 添加 `TestKnowledgeWriteBack` 验证写入路径 + 清理
