# 数据获取模块 - 封装外部数据源调用
import sys
import os

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.core.akshare_client import (
    get_stock_quote,
    get_etf_quote,
    get_fund_quote,
    get_stock_basic_info,
    get_etf_basic_info,
    get_fund_basic_info
)

def get_stock_data(code, force_update=False):
    """
    获取股票数据
    
    Args:
        code (str): 股票代码
        force_update (bool): 是否强制更新缓存
        
    Returns:
        dict: 股票数据
    """
    try:
        # 获取股票实时行情
        quote_data = get_stock_quote(code, force_update=force_update)
        
        if not quote_data:
            return None
        
        # 获取股票基本信息
        basic_info = get_stock_basic_info(code, force_update=force_update)
        
        if basic_info:
            quote_data.update(basic_info)
        
        return quote_data
    except Exception as e:
        print(f"获取股票数据失败: {e}")
        return None

def get_etf_data(code, force_update=False):
    """
    获取ETF数据
    
    Args:
        code (str): ETF代码
        force_update (bool): 是否强制更新缓存
        
    Returns:
        dict: ETF数据
    """
    try:
        # 获取ETF实时行情
        quote_data = get_etf_quote(code, force_update=force_update)
        
        if not quote_data:
            return None
        
        # 获取ETF基本信息
        basic_info = get_etf_basic_info(code, force_update=force_update)
        
        if basic_info:
            quote_data.update(basic_info)
        
        return quote_data
    except Exception as e:
        print(f"获取ETF数据失败: {e}")
        return None

def get_fund_data(code, force_update=False):
    """
    获取基金数据
    
    Args:
        code (str): 基金代码
        force_update (bool): 是否强制更新缓存
        
    Returns:
        dict: 基金数据
    """
    try:
        # 获取基金实时行情
        quote_data = get_fund_quote(code, force_update=force_update)
        
        if not quote_data:
            return None
        
        # 获取基金基本信息
        basic_info = get_fund_basic_info(code, force_update=force_update)
        
        if basic_info:
            quote_data.update(basic_info)
        
        return quote_data
    except Exception as e:
        print(f"获取基金数据失败: {e}")
        return None

def get_realtime_data(code, force_update=False):
    """
    获取实时数据（自动识别产品类型）
    
    Args:
        code (str): 产品代码
        force_update (bool): 是否强制更新缓存
        
    Returns:
        tuple: (product_type, data)
    """
    try:
        # 尝试按股票获取
        stock_data = get_stock_data(code, force_update=force_update)
        if stock_data:
            return 'stock', stock_data
        
        # 尝试按ETF获取
        etf_data = get_etf_data(code, force_update=force_update)
        if etf_data:
            return 'etf', etf_data
        
        # 尝试按基金获取
        fund_data = get_fund_data(code, force_update=force_update)
        if fund_data:
            return 'fund', fund_data
        
        # 如果都获取不到，返回None
        return None, None
    except Exception as e:
        print(f"获取实时数据失败: {e}")
        return None, None

def get_product_info(code, product_type=None, force_update=False):
    """
    获取产品信息
    
    Args:
        code (str): 产品代码
        product_type (str, optional): 产品类型 (stock/etf/fund)
        force_update (bool): 是否强制更新缓存
        
    Returns:
        tuple: (product_type, data)
    """
    try:
        if product_type:
            # 如果指定了产品类型，直接按类型获取
            if product_type == 'stock':
                data = get_stock_data(code, force_update=force_update)
                return product_type, data
            elif product_type == 'etf':
                data = get_etf_data(code, force_update=force_update)
                return product_type, data
            elif product_type == 'fund':
                data = get_fund_data(code, force_update=force_update)
                return product_type, data
            else:
                return None, None
        else:
            # 如果没有指定产品类型，自动识别
            return get_realtime_data(code, force_update=force_update)
    except Exception as e:
        print(f"获取产品信息失败: {e}")
        return None, None
