from .company_info import CompanyInfoPlugin
from .labor_risk import LaborRiskPlugin
from .salary import SalaryPlugin
from .reputation import ReputationPlugin
from .interview import InterviewPlugin
from .development import DevelopmentPlugin

def get_active_plugins():
    """返回启用的插件列表，可根据环境变量筛选"""
    plugins = [
        CompanyInfoPlugin(),
        LaborRiskPlugin(),
        SalaryPlugin(),
        ReputationPlugin(),
        InterviewPlugin(),
        DevelopmentPlugin()
    ]
    # 未来可读取配置控制启停
    return plugins

def fetch_all(company_name, credit_code=None):
    """调用所有插件，返回字典 {plugin_name: data}"""
    results = {}
    for plugin in get_active_plugins():
        try:
            results[plugin.name] = plugin.fetch(company_name, credit_code)
        except Exception as e:
            results[plugin.name] = {"error": str(e)}
    return results