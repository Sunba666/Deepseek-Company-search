# Company Lookup

多维度公司查询与分析工具，帮助求职者全面了解目标公司。

## 功能特性

- **多维度分析**: 从工商信息、薪酬福利、员工口碑、面试经验等多个维度分析公司
- **公司对比**: 将多个公司进行横向对比，选择最适合自己的平台
- **AI智能分析**: 基于多维度数据，AI生成个性化求职建议
- **HTMX动态加载**: 页面片段动态刷新，用户体验更流畅

## 快速开始

### 安装

```bash
pip install -e .
```

### 命令行使用

```bash
company-lookup 阿里巴巴
```

### Web服务

```bash
python -m company_lookup
```

访问 http://localhost:5000

## 项目结构

```
company_lookup/
├── plugins/          # 插件目录
│   ├── base.py       # 插件基类
│   ├── company_info.py
│   ├── labor_risk.py
│   ├── salary.py
│   ├── reputation.py
│   ├── interview.py
│   └── development.py
├── templates/        # HTML模板
├── static/          # 静态资源
├── app.py           # Flask应用
├── ai_analyzer.py   # AI分析器
└── comparer.py      # 公司对比
```

## License

MIT