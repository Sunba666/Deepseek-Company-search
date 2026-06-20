# -*- coding: utf-8 -*-
"""测试公司查询功能（同步版本 - 原异步路由已合并）"""
import urllib.request
import urllib.parse
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except AttributeError:
    pass

# 步骤1：提交同步查询
url = 'http://127.0.0.1:5000/company/search'
data = urllib.parse.urlencode({'company_name': '华为'}).encode('utf-8')
req = urllib.request.Request(url, data=data, method='POST', headers={'Content-Type': 'application/x-www-form-urlencoded'})
try:
    r = urllib.request.urlopen(req, timeout=60)
    content = r.read().decode('utf-8')
    print('=== 公司查询测试 ===')
    print('状态码:', r.getcode())
    print('响应大小:', len(content), 'B')
    print('含AI分析内容:', 'AI' in content and '分析' in content)
    print('含风险数据:', '风险' in content or 'risk' in content)
    print('含薪资数据:', '薪资' in content or '薪酬' in content)
    print()
    print('测试通过 ✅')
except Exception as e:
    print('查询失败:', e)
    print()
    print('测试失败 ❌')
