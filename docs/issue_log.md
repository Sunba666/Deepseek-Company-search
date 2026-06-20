# 问题日志

> 自动记录所有诊断发现的问题，按严重程度分级。
> P0 = 阻断（程序无法运行），P1 = 数据（数据不准确），P2 = 体验（用户体验问题）

### [P1] DataSource JSON序列化问题
- **描述**: `/api/aggregate-report` 返回 DataSource Enum 无法被 Flask JSON 序列化，导致 TypeError: Object of type DataSource is not JSON serializable
- **文件**: `services/aggregator.py:29-40`
- **修复方案**: DataSourceStatus.to_dict() 中添加递归序列化函数，将 Enum 转为 .value 字符串

### [P2] test_brand.py 过时
- **描述**: 检查条件为 `'AI分析报告' in content`，但实际响应中的标识是 `ai-report` 类名
- **文件**: `test_brand.py:13`
- **状态**: 已修复 - 更新检查条件包含 ai-report / 深度AI分析

### [P2] test_async.py 路由不存在
- **描述**: 测试脚本依赖 `/company/search-async` 路由，该路由已不存在（404）
- **文件**: `test_async.py`
- **状态**: 已修复 - 重写为同步查询测试

### [P2] mock_data.py 热加载语法错误
- **描述**: debug模式热加载时 mock_data.py 报 SyntaxError: keyword argument repeated: company_type
- **文件**: `services/mock_data.py:47`
- **注意**: 当前文件内容没有重复，可能是热加载过程中写入了临时冲突版本

---

## 2026-06-19 — 初轮全量诊断

### [P2] dashboard/search 字段名不一致
- **描述**: `/dashboard/search` 路由使用 `query` 字段名，而 `/company/search` 使用 `company_name`。前端表单如果以 `company_name` 提交会导致 dashboard 返回"请输入公司名称"
- **文件**: `routes/company.py:449`
- **修复方案**: 统一字段名，或 dashboard 同时兼容两个字段名

### [P2] 测试脚本 test_brand.py 过时
- **描述**: 检查条件为 `'AI分析报告' in content`，但实际响应中的标识是 `ai-report` 类名，导致全部测试标记为"失败"
- **文件**: `test_brand.py:13`
- **修复方案**: 更新检查条件

### [P2] test_async.py 路由不存在
- **描述**: 测试脚本依赖 `/company/search-async` 路由，该路由已不存在（404）
- **文件**: `test_async.py`
- **修复方案**: 移除或更新测试脚本

### [P1] 风险监控/薪资查询无独立路由
- **描述**: 风险监控 (`/risk-monitor`) 和薪资查询 (`/salary`) 作为独立页面返回 404。这些功能的数据已内嵌在公司查询结果中，但没有独立页面路由满足"需要永远守护的功能"中的状态报告需求
- **修复方案**: 确认是否需要独立路由，或将相关数据集成到 dashboard 中

### [P2] negotiate 字段验证缺失
- **描述**: `/negotiate` 路由未对 `expected_salary` 做完整验证，直接使用空字符串传给 AI 服务
- **文件**: `routes/company.py:660-666`
