# -*- coding: utf-8 -*-
"""公司对比分析模块"""

def compare_companies(company_a_data, company_b_data):
    """
    对比两家公司的数据
    :param company_a_data: 公司A的数据字典
    :param company_b_data: 公司B的数据字典
    :return: 对比结果字典
    """
    comparison = {
        'company_a': company_a_data.get('name', '公司A'),
        'company_b': company_b_data.get('name', '公司B'),
        'dimensions': [],
        'summary': {
            'a_advantages': [],
            'b_advantages': [],
            'similar': []
        }
    }
    
    # 基本信息对比
    basic_dimensions = [
        ('公司名称', company_a_data.get('name'), company_b_data.get('name')),
        ('所属行业', company_a_data.get('industry'), company_b_data.get('industry')),
        ('细分领域', company_a_data.get('sub_industry'), company_b_data.get('sub_industry')),
        ('公司规模', company_a_data.get('scale'), company_b_data.get('scale')),
        ('成立年份', company_a_data.get('established_year'), company_b_data.get('established_year')),
        ('融资状态', company_a_data.get('funding_status'), company_b_data.get('funding_status'))
    ]
    
    for label, a_val, b_val in basic_dimensions:
        comparison['dimensions'].append({
            'category': '基本信息',
            'label': label,
            'value_a': a_val or '-',
            'value_b': b_val or '-',
            'winner': 'tie' if str(a_val) == str(b_val) else None
        })
    
    # 薪酬福利对比
    a_salary = company_a_data.get('salary', {})
    b_salary = company_b_data.get('salary', {})
    
    salary_dimensions = [
        ('平均月薪', a_salary.get('avg_monthly'), b_salary.get('avg_monthly')),
        ('薪资范围', a_salary.get('salary_range'), b_salary.get('salary_range')),
        ('年终奖金', a_salary.get('year_end_bonus'), b_salary.get('year_end_bonus')),
        ('调薪频率', a_salary.get('salary_adjustment'), b_salary.get('salary_adjustment'))
    ]
    
    for label, a_val, b_val in salary_dimensions:
        comparison['dimensions'].append({
            'category': '薪酬福利',
            'label': label,
            'value_a': a_val or '-',
            'value_b': b_val or '-',
            'winner': 'tie' if str(a_val) == str(b_val) else None
        })
    
    # 员工口碑对比
    a_rep = company_a_data.get('reputation', {})
    b_rep = company_b_data.get('reputation', {})
    
    rep_dimensions = [
        ('综合评分', a_rep.get('overall_rating'), b_rep.get('overall_rating')),
        ('推荐率', a_rep.get('recommendation_rate'), b_rep.get('recommendation_rate')),
        ('CEO认可度', a_rep.get('ceo_approval_rate'), b_rep.get('ceo_approval_rate'))
    ]
    
    for label, a_val, b_val in rep_dimensions:
        comparison['dimensions'].append({
            'category': '员工口碑',
            'label': label,
            'value_a': a_val or '-',
            'value_b': b_val or '-',
            'winner': 'tie' if str(a_val) == str(b_val) else None
        })
    
    # 面试经验对比
    a_interview = company_a_data.get('interview', {})
    b_interview = company_b_data.get('interview', {})
    
    interview_dimensions = [
        ('面试难度', a_interview.get('interview_difficulty'), b_interview.get('interview_difficulty')),
        ('面试轮数', a_interview.get('interview_rounds'), b_interview.get('interview_rounds')),
        ('通过率', a_interview.get('positive_rate'), b_interview.get('positive_rate'))
    ]
    
    for label, a_val, b_val in interview_dimensions:
        comparison['dimensions'].append({
            'category': '面试经验',
            'label': label,
            'value_a': a_val or '-',
            'value_b': b_val or '-',
            'winner': 'tie' if str(a_val) == str(b_val) else None
        })
    
    # 风险对比
    a_risk = company_a_data.get('labor_risk', {})
    b_risk = company_b_data.get('labor_risk', {})
    
    risk_level_map = {'低': 1, '中': 2, '高': 3}
    
    comparison['dimensions'].append({
        'category': '风险评估',
        'label': '风险等级',
        'value_a': a_risk.get('risk_level') or '-',
        'value_b': b_risk.get('risk_level') or '-',
        'winner': _compare_risk(a_risk.get('risk_level'), b_risk.get('risk_level'))
    })
    
    # 生成总结
    comparison['summary']['a_advantages'] = _find_advantages(comparison, 'a')
    comparison['summary']['b_advantages'] = _find_advantages(comparison, 'b')
    comparison['summary']['similar'] = _find_similar(comparison)
    
    return comparison

def _compare_risk(a_level, b_level):
    """比较风险等级"""
    risk_map = {'低': 1, '中': 2, '高': 3}
    a_val = risk_map.get(a_level, 2)
    b_val = risk_map.get(b_level, 2)
    
    if a_val < b_val:
        return 'a'
    elif b_val < a_val:
        return 'b'
    return 'tie'

def _find_advantages(comparison, company):
    """找出某公司的优势维度"""
    advantages = []
    for dim in comparison['dimensions']:
        if dim.get('winner') == company:
            advantages.append(dim['label'])
    return advantages

def _find_similar(comparison):
    """找出相似维度"""
    similar = []
    for dim in comparison['dimensions']:
        if dim.get('winner') == 'tie':
            similar.append(dim['label'])
    return similar

def personalized_score(company_data, user_preferences):
    """
    根据用户偏好计算个性化匹配度
    :param company_data: 公司数据
    :param user_preferences: 用户偏好字典，包含各维度权重
    :return: 匹配分数和各维度得分
    """
    weights = {
        'salary': user_preferences.get('salary_weight', 30),
        'culture': user_preferences.get('culture_weight', 25),
        'growth': user_preferences.get('growth_weight', 20),
        'worklife': user_preferences.get('worklife_weight', 15),
        'stability': user_preferences.get('stability_weight', 10)
    }
    
    total_weight = sum(weights.values())
    if total_weight == 0:
        total_weight = 100
    
    scores = {}
    
    # 薪资得分
    salary_data = company_data.get('salary', {})
    avg_salary = _parse_salary(salary_data.get('avg_monthly', '0'))
    scores['salary'] = min(100, (avg_salary / 50000) * 100)
    
    # 文化得分（基于员工评价）
    rep_data = company_data.get('reputation', {})
    rating = _parse_rating(rep_data.get('overall_rating', '0'))
    scores['culture'] = rating * 20
    
    # 发展潜力得分（基于公司规模和融资状态）
    funding_status = company_data.get('funding_status', '')
    scale = company_data.get('scale', '')
    growth_score = 50
    if '上市' in funding_status:
        growth_score += 20
    elif 'C轮' in funding_status or 'D轮' in funding_status:
        growth_score += 15
    elif 'A轮' in funding_status or 'B轮' in funding_status:
        growth_score += 10
    
    if '500人' in scale or '1000人' in scale:
        growth_score += 10
    scores['growth'] = min(100, growth_score)
    
    # 工作生活平衡得分（基于加班评价）
    cons = rep_data.get('cons', [])
    worklife_score = 70
    if any('加班' in c for c in cons):
        worklife_score -= 20
    if any('压力' in c for c in cons):
        worklife_score -= 10
    scores['worklife'] = max(0, worklife_score)
    
    # 稳定性得分（基于风险等级）
    risk_level = company_data.get('labor_risk', {}).get('risk_level', '中')
    risk_map = {'低': 90, '中': 60, '高': 30}
    scores['stability'] = risk_map.get(risk_level, 60)
    
    # 计算总分
    total_score = 0
    for key, weight in weights.items():
        total_score += (scores[key] * weight) / total_weight
    
    return {
        'total_score': round(total_score, 1),
        'dimension_scores': scores,
        'weighted_scores': {k: round(v * weights[k] / total_weight, 1) for k, v in scores.items()}
    }

def _parse_salary(salary_str):
    """解析薪资字符串"""
    if not salary_str:
        return 0
    try:
        # 提取数字部分
        num_str = ''.join([c for c in salary_str if c.isdigit() or c == '.'])
        return float(num_str)
    except Exception:
        return 0

def _parse_rating(rating_str):
    """解析评分字符串"""
    if not rating_str:
        return 0
    try:
        # 提取第一个数字
        parts = rating_str.split('/')
        if len(parts) > 0:
            return float(parts[0])
        return float(rating_str)
    except Exception:
        return 0

def calculate_radar_data(company_data):
    """
    计算风险雷达图数据
    :param company_data: 公司数据
    :return: 雷达图数据字典
    """
    radar_data = {
        '法律风险': 50,
        '财务状况': 50,
        '运营稳定性': 50,
        '员工满意度': 50,
        '发展潜力': 50,
        '行业竞争力': 50
    }
    
    if not company_data or not isinstance(company_data, dict) or len(company_data) == 0:
        return radar_data
    
    # 法律风险（基于劳动风险）
    risk_level = company_data.get('labor_risk', {}).get('risk_level', '中')
    risk_items = company_data.get('labor_risk', {}).get('risk_items', [])
    
    risk_score = 70
    risk_map = {'低': 85, '中': 60, '高': 30}
    risk_score = risk_map.get(risk_level, 60)
    
    if len(risk_items) > 0:
        risk_score -= len(risk_items) * 10
    radar_data['法律风险'] = max(0, min(100, risk_score))
    
    # 财务状况（基于融资状态）
    funding_status = company_data.get('funding_status', '')
    if '上市' in funding_status:
        radar_data['财务状况'] = 85
    elif 'C轮' in funding_status or 'D轮' in funding_status:
        radar_data['财务状况'] = 75
    elif 'A轮' in funding_status or 'B轮' in funding_status:
        radar_data['财务状况'] = 65
    elif '天使轮' in funding_status:
        radar_data['财务状况'] = 50
    
    # 运营稳定性（基于公司规模和成立时间）
    established_year = company_data.get('established_year', '0')
    try:
        years = 2024 - int(established_year)
        if years >= 10:
            radar_data['运营稳定性'] = 80
        elif years >= 5:
            radar_data['运营稳定性'] = 65
        else:
            radar_data['运营稳定性'] = 50
    except Exception:
        pass
    
    scale = company_data.get('scale', '')
    if '500人' in scale:
        radar_data['运营稳定性'] = min(100, radar_data['运营稳定性'] + 10)
    elif '1000人' in scale or '10000人' in scale:
        radar_data['运营稳定性'] = min(100, radar_data['运营稳定性'] + 15)
    
    # 员工满意度（基于口碑评分）
    rep = company_data.get('reputation', {})
    rating = _parse_rating(rep.get('overall_rating', '0'))
    radar_data['员工满意度'] = min(100, rating * 20)
    
    # 发展潜力（基于融资和行业）
    industry = company_data.get('industry', '')
    growth_score = 60
    hot_industries = ['人工智能', '新能源', '生物医药', '半导体', '云计算', '互联网']
    if any(ind in industry for ind in hot_industries):
        growth_score += 20
    radar_data['发展潜力'] = growth_score
    
    # 行业竞争力（基于公司规模和行业地位）
    comp_score = 50
    if '上市' in funding_status:
        comp_score += 25
    if '500人' in scale or '1000人' in scale or '10000人' in scale:
        comp_score += 15
    radar_data['行业竞争力'] = min(100, comp_score)
    
    return radar_data
