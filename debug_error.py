import sys
import traceback
import io

# 设置编码
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# 记录导入顺序和时间
print('开始导入模块...')

try:
    print('1. 导入基础模块')
    import os
    
    print('2. 导入Flask')
    from flask import Flask, request, render_template
    
    print('3. 导入公司lookup模块')
    sys.path.insert(0, 'e:/Company-lookup/src')
    
    print('4. 导入offer_parser')
    from company_lookup.services.offer_parser import parse_offer_text
    
    print('5. 导入ai_analyzer')
    from company_lookup.ai_analyzer import analyze_offers, query_company_info
    
    print('所有模块导入成功!')
    
    # 测试数据
    offer_text1 = '阿里巴巴 P6，月薪35K，16薪，公积金12%，杭州，通勤30分钟'
    offer_text2 = '腾讯 T3，月薪32K，15薪，公积金12%，深圳，通勤45分钟'
    
    print('开始解析Offer...')
    offer1 = parse_offer_text(offer_text1)
    offer2 = parse_offer_text(offer_text2)
    
    print(f'Offer1: {offer1}')
    print(f'Offer2: {offer2}')
    
    print('开始分析...')
    result = analyze_offers([offer1, offer2])
    print(f'分析结果: {result.keys()}')
    
    print('测试成功!')
    
except Exception as e:
    print(f'错误类型: {type(e).__name__}')
    print(f'错误信息: {e}')
    traceback.print_exc()
