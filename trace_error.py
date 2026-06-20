import sys
import traceback
import io

sys.path.insert(0, 'e:/Company-lookup/src')

# 重定向stdout和stderr
class SafeStream:
    def __init__(self, original):
        self.original = original
        
    def write(self, data):
        try:
            self.original.write(data)
        except:
            pass
            
    def flush(self):
        try:
            self.original.flush()
        except:
            pass

sys.stdout = SafeStream(sys.stdout)
sys.stderr = SafeStream(sys.stderr)

try:
    from company_lookup.services.offer_parser import parse_offer_text
    from company_lookup.ai_analyzer import analyze_offers, query_company_info
    
    # 测试数据
    offer_text1 = '阿里巴巴 P6，月薪35K，16薪，公积金12%，杭州，通勤30分钟'
    offer_text2 = '腾讯 T3，月薪32K，15薪，公积金12%，深圳，通勤45分钟'
    
    print('步骤1: 解析Offer 1')
    offer1 = parse_offer_text(offer_text1)
    print('Offer1:', offer1)
    
    print('步骤2: 解析Offer 2')
    offer2 = parse_offer_text(offer_text2)
    print('Offer2:', offer2)
    
    print('步骤3: 查询公司信息 - 阿里巴巴')
    company1 = query_company_info('阿里巴巴')
    print('公司信息1 keys:', list(company1.keys()))
    
    print('步骤4: 查询公司信息 - 腾讯')
    company2 = query_company_info('腾讯')
    print('公司信息2 keys:', list(company2.keys()))
    
    print('步骤5: 分析Offers')
    result = analyze_offers([offer1, offer2])
    print('分析结果 keys:', list(result.keys()))
    print('最优选择:', result.get('winner'))
    
    print('步骤6: 测试渲染模板')
    from flask import Flask, render_template_string
    app = Flask(__name__)
    with app.app_context():
        template = '''
            {% if result and result.winner %}
            <div>最优选择: {{ result.winner }}</div>
            {% endif %}
        '''
        html = render_template_string(template, result=result)
        print('HTML渲染成功')
    
    print('所有步骤完成!')
    
except Exception as e:
    print('错误:', e)
    traceback.print_exc()
