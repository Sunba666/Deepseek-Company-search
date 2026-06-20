# 代码修复方案文档

## 一、问题总览

| 序号 | 文件 | 问题类型 | 严重程度 |
|------|------|----------|----------|
| 1 | `comparer.py` | 文件不完整，缺少 import 和类定义 | 高 |
| 2 | `ai_analyzer.py` | 未定义变量 `AI_BACKEND` | 高 |
| 3 | `plugins/__init__.py` | 插件调用方式与基类定义不匹配 | 高 |
| 4 | `plugins/base.py` | 缺少 `name` 和 `display_name` 属性 | 中 |
| 5 | `app.py` | 导入的函数签名与调用不匹配 | 高 |
| 6 | `ai_analyzer.py` | `build_prompt` 函数定义不完整 | 高 |
| 7 | `plugins/__init__.py` | `get_active_plugins` 返回实例但未注册到 manager | 中 |
| 8 | 整体架构 | 异步/同步实现混乱 | 中 |

---

## 二、详细问题分析与修复方案

---

### 问题 1: `comparer.py` - 文件不完整

**问题描述**:
- 文件从第 1 行开始就是函数定义 `compare_companies`，缺少必要的 import 语句
- 没有文件头部的模块说明
- 缺少 `Comparer` 类定义（我之前创建的版本有类定义，但当前文件内容被覆盖了）

**当前代码**:
```python
def compare_companies(companies_data: dict) -> dict:
    # ...
```

**修复方案**:
```python
"""Company comparison and personalized scoring module."""

from typing import Any


class Comparer:
    """Compare companies and generate personalized recommendations."""

    def __init__(self):
        self.dimension_weights = {
            "salary": 0.3,
            "reputation": 0.2,
            "development": 0.2,
            "worklife": 0.15,
            "stability": 0.15,
        }

    def compare_companies(self, companies_data: dict) -> dict:
        """Compare multiple companies."""
        ...

    def personalized_score(self, company_data: dict, preferences: dict) -> dict:
        """Score company based on user preferences."""
        ...


# Global instance
comparer = Comparer()
```

---

### 问题 2: `ai_analyzer.py` - 未定义变量 `AI_BACKEND`

**问题描述**:
- 第 3 行使用了 `AI_BACKEND` 变量，但该变量在任何地方都未定义
- `call_openai` 和 `call_ollama` 函数引用了 `AI_BACKEND` 但未导入

**当前代码**:
```python
# 原有的 import 和 AI_BACKEND 等配置
import os, json, requests
from .plugins import fetch_all  # 新增导入

def analyze_company(company_name: str, user_context: str = "") -> dict:
    # ...
    if AI_BACKEND == "openai":
        return call_openai(prompt)
    elif AI_BACKEND == "ollama":
        return call_ollama(prompt)
    else:
        raise ValueError("AI_BACKEND 环境变量需为 'openai' 或 'ollama'")
```

**修复方案**:
```python
import os
import json
import requests
from .plugins import fetch_all

# AI 后端配置
AI_BACKEND = os.getenv("AI_BACKEND", "ollama")  # 提供默认值


def analyze_company(company_name: str, user_context: str = "") -> dict:
    """Analyze company with AI based on all plugin data."""
    data = fetch_all(company_name)
    prompt = build_prompt(data, user_context)

    if AI_BACKEND == "openai":
        return call_openai(prompt)
    elif AI_BACKEND == "ollama":
        return call_ollama(prompt)
    else:
        raise ValueError("AI_BACKEND 环境变量需为 'openai' 或 'ollama'")


def build_prompt(all_data: dict, user_context: str) -> str:
    """Build prompt for AI analysis."""
    # 完整实现
    ...


def call_openai(prompt: str) -> dict:
    """Call OpenAI API."""
    # 完整实现
    ...


def call_ollama(prompt: str) -> dict:
    """Call Ollama API."""
    # 完整实现
    ...
```

---

### 问题 3: `plugins/__init__.py` - 插件调用方式与基类定义不匹配

**问题描述**:
- `plugins/__init__.py` 中调用 `plugin.fetch(company_name, credit_code)` 时传递了两个参数
- 但 `base.py` 中 `BasePlugin.fetch` 方法的第一个参数是 `self`，会变成三个参数（self, company_name, credit_code）

**当前代码**:
```python
# plugins/__init__.py
def fetch_all(company_name, credit_code=None):
    for plugin in get_active_plugins():
        results[plugin.name] = plugin.fetch(company_name, credit_code)

# plugins/base.py
class BasePlugin(ABC):
    @abstractmethod
    def fetch(self, company_name: str, credit_code: str = None) -> dict:
        pass
```

**修复方案**:
`base.py` 中的 `fetch` 是实例方法，第一个参数 `self` 会自动绑定，所以签名应该是：
```python
def fetch(self, company_name: str, credit_code: str = None) -> dict:
    pass
```

这样 `plugin.fetch(company_name, credit_code)` 调用时，`self` 由 `plugin` 实例自动提供，参数完全匹配。

---

### 问题 4: `plugins/base.py` - 缺少 `name` 和 `display_name` 属性

**问题描述**:
- `base.py` 中 `BasePlugin` 没有定义 `name` 和 `display_name` 属性
- 但在 `comparer.py` 和 `ai_analyzer.py` 中通过 `plugin.name` 访问

**当前代码**:
```python
class BasePlugin(ABC):
    name: str = ""
    description: str = ""

    @abstractmethod
    def fetch(self, company_name: str, credit_code: str = None) -> dict:
        pass
```

**修复方案**:
```python
class BasePlugin(ABC):
    """Abstract base class for company data plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin identifier."""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable plugin name."""
        pass

    @abstractmethod
    def fetch(self, company_name: str, credit_code: str = None) -> dict:
        """Fetch data for the given company."""
        pass
```

各插件需要实现 `@property` 装饰的 `name` 和 `display_name`。

---

### 问题 5: `app.py` - 导入的函数签名与调用不匹配

**问题描述**:
- 第 3 行导入 `from .ai_analyzer import analyze_company as ai_analyze`
- 第 30 行调用 `analysis = ai_analyze(query, user_context)` 传递了两个参数
- 但 `analyze_company` 函数只接受 `company_name` 一个必需参数

**当前代码**:
```python
@app.route("/analyze", methods=["POST"])
def analyze():
    query = request.form.get("query", "").strip()
    user_context = request.form.get("user_context", "").strip()
    # ...
    analysis = ai_analyze(query, user_context)  # 两个参数
```

**修复方案**:
选项 A - 修改 `analyze_company` 函数签名以接受 `user_context`：
```python
def analyze_company(company_name: str, user_context: str = "") -> dict:
    # ...
```

选项 B - 修改路由调用，只传递公司名称：
```python
analysis = ai_analyze(query)
```

**推荐选项 A**，保持与 `app.py` 中调用一致。

---

### 问题 6: `ai_analyzer.py` - `build_prompt` 函数定义不完整

**问题描述**:
- `build_prompt` 函数在代码中被引用，但函数体只有 docstring，没有实际实现
- `call_openai` 和 `call_ollama` 函数也存在同样问题

**修复方案**:
```python
def build_prompt(all_data: dict, user_context: str) -> str:
    """Build prompt for AI analysis."""
    full_json = json.dumps(all_data, ensure_ascii=False, indent=2)
    user_part = f"\n\n用户补充信息：{user_context}" if user_context else ""

    return f"""你是一位资深的职业规划与求职顾问，同时具备企业背景调查专业知识。
请基于以下多维度企业数据，从求职者的角度进行全面分析。

### 企业综合数据
{full_json}

### 用户提供的信息
{user_part}

请用 JSON 格式输出（不要包含其他文字）：
{{
  "overview": "一句话总结公司对求职者的吸引力",
  "pros_for_jobseeker": ["优势1", "优势2"],
  "cons_for_jobseeker": ["劣势或风险1"],
  "culture_fit": "描述适合哪类求职者",
  "salary_competitiveness": "薪酬竞争力分析",
  "stability": "公司稳定性评估（高/中/低）及理由",
  "development_potential": "个人成长空间评价",
  "risk_alert": "入职前需要重点核实的风险点",
  "suggested_questions": ["面试时可询问的问题1", "问题2"],
  "final_advice": "是否推荐入职（推荐/谨慎/不推荐）及详细理由"
}}
"""


def call_openai(prompt: str) -> dict:
    """Call OpenAI API for analysis."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"error": "OPENAI_API_KEY not set"}

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        return parse_json(result["choices"][0]["message"]["content"])
    except Exception as e:
        return {"error": str(e)}


def call_ollama(prompt: str) -> dict:
    """Call Ollama API for analysis."""
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")

    payload = {
        "model": os.getenv("OLLAMA_MODEL", "llama2"),
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(
            f"{ollama_url}/api/generate",
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        return parse_json(result.get("response", ""))
    except Exception as e:
        return {"error": str(e)}


def parse_json(text: str) -> dict:
    """Parse JSON from AI response."""
    try:
        # Try direct JSON parse
        return json.loads(text)
    except:
        # Try extracting JSON from markdown code blocks
        import re
        match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return {"error": "Failed to parse AI response", "raw": text}
```

---

### 问题 7: `plugins/__init__.py` - 未使用 PluginManager

**问题描述**:
- `PluginManager` 类在文件中被导入，但从未使用
- `fetch_all` 函数直接调用 `get_active_plugins()`，绕过了管理器

**修复方案**:
使用我之前创建的 `PluginManager`：
```python
from .base import BasePlugin
from .company_info import CompanyInfoPlugin
from .labor_risk import LaborRiskPlugin
from .salary import SalaryPlugin
from .reputation import ReputationPlugin
from .interview import InterviewPlugin
from .development import DevelopmentPlugin

__all__ = [
    "BasePlugin",
    "CompanyInfoPlugin",
    "LaborRiskPlugin",
    "SalaryPlugin",
    "ReputationPlugin",
    "InterviewPlugin",
    "DevelopmentPlugin",
    "get_plugin_manager",
]


class PluginManager:
    """Manages all plugins for data fetching."""

    def __init__(self):
        self._plugins = {}

    def register(self, name: str, plugin: BasePlugin):
        self._plugins[name] = plugin

    def get_plugin(self, name: str) -> BasePlugin:
        return self._plugins.get(name)

    def get_all_plugins(self) -> dict[str, BasePlugin]:
        return self._plugins.copy()


# Global plugin manager instance
_manager = PluginManager()

# Register default plugins
_manager.register("company_info", CompanyInfoPlugin())
_manager.register("labor_risk", LaborRiskPlugin())
_manager.register("salary", SalaryPlugin())
_manager.register("reputation", ReputationPlugin())
_manager.register("interview", InterviewPlugin())
_manager.register("development", DevelopmentPlugin())


def get_plugin_manager() -> PluginManager:
    """Get the global plugin manager instance."""
    return _manager


def fetch_all(company_name: str, credit_code: str = None) -> dict:
    """Fetch data from all registered plugins."""
    results = {}
    for name, plugin in _manager.get_all_plugins().items():
        try:
            results[name] = plugin.fetch(company_name, credit_code)
        except Exception as e:
            results[name] = {"error": str(e)}
    return results


def get_active_plugins() -> list:
    """Return list of active plugin instances."""
    return list(_manager.get_all_plugins().values())
```

---

### 问题 8: 异步/同步实现混乱

**问题描述**:
- 我最初创建的 `plugins` 使用了 `async/await` 异步模式
- 但 `app.py` 和 `plugins/__init__.py` 中使用的是同步调用
- `BasePlugin.fetch` 被定义为抽象方法但不是异步的

**修复方案**:
统一为**同步实现**（推荐）：
- 所有插件的 `fetch` 方法改为普通方法，不使用 `async`
- `plugins/__init__.py` 中的 `fetch_all` 改为同步函数
- 如需异步支持，可在应用层使用 `asyncio.to_thread()`

---

## 三、修复优先级建议

| 优先级 | 问题 | 原因 |
|--------|------|------|
| P0 | 问题 1, 2, 5, 6 | 导致程序无法运行 |
| P1 | 问题 3, 4 | 导致数据获取功能失效 |
| P2 | 问题 7, 8 | 代码结构问题，但不影响基本功能 |

---

## 四、修复后的文件结构

修复完成后，各文件应满足以下调用关系：

```
app.py
├── from .ai_analyzer import analyze_company  ✓
│   └── analyze_company(query, user_context)  ✓
│       ├── fetch_all(company_name)  ✓
│       └── build_prompt(data, user_context)  ✓
├── from .comparer import compare_companies, personalized_score  ✓
│   └── Comparer 类方法  ✓
└── from .plugins import fetch_all  ✓
    └── PluginManager.fetch_all  ✓

plugins/__init__.py
├── BasePlugin, 各插件类  ✓
├── PluginManager  ✓
├── fetch_all()  ✓
└── get_active_plugins()  ✓

plugins/base.py
├── BasePlugin 抽象类
│   ├── @property name  ✓
│   ├── @property display_name  ✓
│   └── fetch(self, company_name, credit_code=None)  ✓

plugins/*.py (各插件)
├── name property  ✓
├── display_name property  ✓
└── fetch(self, company_name, credit_code=None)  ✓
```

---

## 五、验证清单

修复完成后，应验证以下调用正常工作：

```python
# 1. 插件加载
from company_lookup.plugins import fetch_all, get_active_plugins
plugins = get_active_plugins()
assert len(plugins) == 6

# 2. 数据获取
data = fetch_all("测试公司")
assert "company_info" in data
assert "salary" in data
assert "error" not in data.get("company_info", {})

# 3. AI 分析
from company_lookup.ai_analyzer import analyze_company
result = analyze_company("测试公司", "我想了解薪酬")
assert "overview" in result or "error" in result

# 4. 公司对比
from company_lookup.comparer import personalized_score
data = fetch_all("测试公司")
score = personalized_score(data, {"expected_salary": "20K"})
assert "score" in score
```
