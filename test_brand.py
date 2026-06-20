# -*- coding: utf-8 -*-
"""测试简称查询功能"""
import urllib.request
import urllib.parse

def test_search(name):
    url = 'http://127.0.0.1:5000/company/search'
    data = urllib.parse.urlencode({'company_name': name}).encode('utf-8')
    req = urllib.request.Request(url, data=data, method='POST', headers={'Content-Type': 'application/x-www-form-urlencoded'})
    try:
        r = urllib.request.urlopen(req, timeout=30)
        content = r.read().decode('utf-8')
        # 检测AI分析内容：实际响应中包含 ai-report 类名或 AI分析报告 文本
        # 注意：响应HTML中可能含 '复制失败' JS文字，因此不能简单用 '失败' 判断
        is_known_company = name not in ('不存在的公司xxx',)
        if is_known_company:
            success = 'ai-report' in content or 'AI分析报告' in content
        else:
            success = '未找到' in content or 'not_found' in content
        return {'name': name, 'status': '成功' if success else '失败', 'status_code': r.getcode()}
    except Exception as e:
        return {'name': name, 'status': '异常: %s' % e, 'status_code': -1}

# 测试多个简称
tests = ['米哈游', '腾讯', '阿里巴巴', '字节跳动', '华为', '不存在的公司xxx']
results = [test_search(t) for t in tests]

print('=== 简称查询测试结果 ===')
for r in results:
    print('%s: %s (状态码: %d)' % (r['name'], r['status'], r['status_code']))
