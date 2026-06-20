import sys
import traceback
import io

sys.path.insert(0, 'e:/Company-lookup/src')

# 设置编码
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

try:
    from flask import Flask, request, render_template
    
    app = Flask(__name__)
    
    # 模拟路由
    @app.route('/test-offer', methods=['POST'])
    def test_offer():
        try:
            offers = request.form.getlist('offers')
            print(f'收到Offers: {offers}')
            
            from company_lookup.services.offer_parser import parse_offer_text
            from company_lookup.ai_analyzer import analyze_offers
            
            parsed_offers = [parse_offer_text(o) for o in offers]
            print(f'解析结果: {parsed_offers}')
            
            result = analyze_offers(parsed_offers)
            print(f'分析结果: {result}')
            
            return 'Success'
        except Exception as e:
            print(f'错误类型: {type(e).__name__}')
            print(f'错误信息: {e}')
            traceback.print_exc()
            return f'Error: {e}'
    
    # 运行测试
    with app.test_request_context():
        # 模拟请求
        from werkzeug.test import EnvironBuilder
        builder = EnvironBuilder(
            method='POST',
            data={'offers': ['阿里巴巴 P6，月薪35K', '腾讯 T3，月薪32K']}
        )
        env = builder.get_environ()
        
        with app.request_context(env):
            response = test_offer()
            print(f'响应: {response}')
            
except Exception as e:
    print(f'主错误: {e}')
    traceback.print_exc()
