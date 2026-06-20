# -*- coding: utf-8 -*-
"""插件模块"""

def fetch_all(company_name):
    """
    获取公司所有信息
    :param company_name: 公司名称
    :return: 空列表（兼容原有接口）
    """
    return []

# 预留接口，便于未来扩展
def register_plugin(plugin):
    """注册插件"""
    pass

def get_plugins():
    """获取所有插件"""
    return []
