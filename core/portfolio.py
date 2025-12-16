# 持仓管理模块 - 封装核心业务逻辑
import sys
import os
import datetime

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.holdings_manager import (
    get_all_holdings as db_get_all_holdings,
    add_holding as db_add_holding,
    update_holding as db_update_holding,
    delete_holding as db_delete_holding
)
from core.data_fetcher import (
    get_stock_data,
    get_etf_data,
    get_fund_data,
    get_realtime_data
)
from models.holding import Holding
from utils.helpers import normalize_number

class PortfolioManager:
    """
    投资组合管理器 - 封装所有持仓管理和计算逻辑
    """
    
    def __init__(self, user_id=None):
        """
        初始化投资组合管理器
        
        Args:
            user_id (str/int, optional): 用户ID，用于多用户场景的数据隔离
        """
        self.user_id = user_id
    
    def get_all_holdings(self):
        """
        获取所有持仓
        
        Returns:
            list: Holding对象列表
        """
        try:
            holdings = db_get_all_holdings()
            # 转换为Holding对象（如果是元组格式）
            holding_objects = []
            for holding in holdings:
                if isinstance(holding, tuple):
                    # 数据库返回的元组格式
                    holding_obj = Holding.from_dict({
                        'id': holding[0],
                        'product_code': holding[1],
                        'product_name': holding[2],
                        'product_type': holding[3],
                        'category': holding[4],
                        'quantity': holding[5],
                        'purchase_price': holding[6],
                        'current_price': holding[7],
                        'purchase_date': holding[8] if len(holding) > 8 else None
                    })
                    holding_objects.append(holding_obj)
                else:
                    holding_objects.append(holding)
            return holding_objects
        except Exception as e:
            print(f"获取持仓失败: {e}")
            return []
    
    def add_holding(self, holding_data):
        """
        添加新持仓
        
        Args:
            holding_data (dict): 持仓数据字典
                - product_code: 产品代码
                - product_name: 产品名称
                - product_type: 产品类型 (stock/etf/fund)
                - quantity: 持仓数量
                - purchase_price: 购买价格
                - current_price: 当前价格 (可选)
                - purchase_date: 购买日期 (可选)
                - category: 资产类别 (可选，自动分配)
        
        Returns:
            tuple: (success, result)
        """
        try:
            # 如果没有提供当前价格，尝试获取
            if 'current_price' not in holding_data or not holding_data['current_price']:
                product_type, product_info = get_realtime_data(holding_data['product_code'])
                if product_info:
                    if product_type == 'stock':
                        holding_data['current_price'] = product_info.get('current_price')
                    elif product_type in ['etf', 'fund']:
                        holding_data['current_price'] = product_info.get('net_value')
            
            # 如果没有提供资产类别，使用默认类别
            if 'category' not in holding_data or not holding_data['category']:
                holding_data['category'] = '其他'  # 提供默认类别
            
            # 创建Holding对象
            holding = Holding.from_dict(holding_data)
            
            # 添加到数据库
            holding_id = db_add_holding(holding)
            
            return True, {
                'message': '持仓添加成功',
                'holding_id': holding_id,
                'category': holding.category
            }
        except Exception as e:
            print(f"添加持仓失败: {e}")
            return False, {
                'message': '持仓添加失败',
                'error': str(e)
            }
    
    def update_holding(self, holding_id, update_data):
        """
        更新持仓信息
        
        Args:
            holding_id (int): 持仓ID
            update_data (dict): 更新的数据
                - quantity: 持仓数量 (可选)
                - purchase_price: 购买价格 (可选)
                - current_price: 当前价格 (可选)
                - product_name: 产品名称 (可选)
                - category: 资产类别 (可选)
        
        Returns:
            tuple: (success, result)
        """
        try:
            # 获取当前持仓
            holdings = self.get_all_holdings()
            current_holding = next((h for h in holdings if h.id == holding_id), None)
            
            if not current_holding:
                return False, {'message': '持仓不存在'}
            
            # 构建更新后的持仓数据
            updated_data = current_holding.to_dict()
            updated_data.update(update_data)
            
            # 创建更新后的Holding对象
            updated_holding = Holding.from_dict(updated_data)
            
            # 更新到数据库
            success = db_update_holding(holding_id, updated_holding)
            
            if success:
                return True, {'message': '持仓更新成功'}
            else:
                return False, {'message': '持仓更新失败'}
        except Exception as e:
            print(f"更新持仓失败: {e}")
            return False, {
                'message': '持仓更新失败',
                'error': str(e)
            }
    
    def delete_holding(self, holding_id):
        """
        删除持仓
        
        Args:
            holding_id (int): 持仓ID
            
        Returns:
            tuple: (success, message)
        """
        try:
            success = db_delete_holding(holding_id)
            if success:
                return True, '持仓删除成功'
            else:
                return False, '持仓删除失败'
        except Exception as e:
            print(f"删除持仓失败: {e}")
            return False, f'删除持仓失败: {e}'
    
    def update_holding_prices(self, force_update=False):
        """
        更新所有持仓的当前价格
        
        Args:
            force_update (bool): 是否强制更新
            
        Returns:
            dict: 更新结果统计
        """
        try:
            holdings = self.get_all_holdings()
            updated_count = 0
            failed_count = 0
            
            for holding in holdings:
                try:
                    # 获取最新价格
                    if holding.product_type == 'stock':
                        product_info = get_stock_data(holding.product_code, force_update=force_update)
                        if product_info:
                            new_price = product_info.get('current_price')
                    elif holding.product_type == 'etf':
                        product_info = get_etf_data(holding.product_code, force_update=force_update)
                        if product_info:
                            new_price = product_info.get('net_value')
                    elif holding.product_type == 'fund':
                        product_info = get_fund_data(holding.product_code, force_update=force_update)
                        if product_info:
                            new_price = product_info.get('net_value')
                    else:
                        new_price = None
                    
                    # 更新价格
                    if new_price is not None:
                        self.update_holding(holding.id, {'current_price': new_price})
                        updated_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    print(f"更新持仓 {holding.id} 价格失败: {e}")
                    failed_count += 1
            
            return {
                'total_holdings': len(holdings),
                'updated_count': updated_count,
                'failed_count': failed_count
            }
        except Exception as e:
            print(f"更新持仓价格失败: {e}")
            return {
                'total_holdings': 0,
                'updated_count': 0,
                'failed_count': 0,
                'error': str(e)
            }
    
    def calculate_portfolio_stats(self):
        """
        计算投资组合统计信息
        
        Returns:
            dict: 统计信息
        """
        try:
            holdings = self.get_all_holdings()
            
            if not holdings:
                return {
                    'total_cost': 0,
                    'total_current': 0,
                    'total_profit': 0,
                    'total_profit_rate': 0,
                    'stock_count': 0,
                    'etf_count': 0,
                    'fund_count': 0,
                    'total_holdings': 0
                }
            
            total_cost = 0
            total_current = 0
            stock_count = 0
            etf_count = 0
            fund_count = 0
            
            for holding in holdings:
                # 计算成本总额
                cost = normalize_number(holding.quantity) * normalize_number(holding.purchase_price)
                total_cost += cost
                
                # 计算当前总额
                current = normalize_number(holding.quantity) * normalize_number(holding.current_price)
                total_current += current
                
                # 统计产品类型
                if holding.product_type == 'stock':
                    stock_count += 1
                elif holding.product_type == 'etf':
                    etf_count += 1
                elif holding.product_type == 'fund':
                    fund_count += 1
            
            # 计算总盈亏和总盈利率
            total_profit = total_current - total_cost
            total_profit_rate = (total_profit / total_cost * 100) if total_cost > 0 else 0
            
            return {
                'total_cost': total_cost,
                'total_current': total_current,
                'total_profit': total_profit,
                'total_profit_rate': total_profit_rate,
                'stock_count': stock_count,
                'etf_count': etf_count,
                'fund_count': fund_count,
                'total_holdings': len(holdings)
            }
        except Exception as e:
            print(f"计算投资组合统计信息失败: {e}")
            return {}
    
    def calculate_asset_allocation(self):
        """
        计算资产配置
        
        Returns:
            dict: 资产配置信息
        """
        try:
            holdings = self.get_all_holdings()
            
            if not holdings:
                return {'total_value': 0, 'categories': {}}
            
            # 按类别分组计算市值
            category_values = {}
            total_value = 0
            
            for holding in holdings:
                # 确保类别存在
                if not holding.category:
                    # 如果没有类别，使用默认类别
                    category = '其他'
                    # 更新持仓类别
                    self.update_holding(holding.id, {'category': category})
                    holding.category = category
                
                # 计算市值
                market_value = normalize_number(holding.quantity) * normalize_number(holding.current_price)
                
                # 累加到对应类别
                if holding.category in category_values:
                    category_values[holding.category]['market_value'] += market_value
                    category_values[holding.category]['count'] += 1
                else:
                    category_values[holding.category] = {
                        'market_value': market_value,
                        'count': 1
                    }
                
                total_value += market_value
            
            # 计算每个类别的占比
            for category, data in category_values.items():
                data['percentage'] = (data['market_value'] / total_value * 100) if total_value > 0 else 0
            
            return {
                'total_value': total_value,
                'categories': category_values
            }
        except Exception as e:
            print(f"计算资产配置失败: {e}")
            return {'total_value': 0, 'categories': {}}
    
    def get_holding_details(self, holding_id):
        """
        获取单个持仓的详细信息
        
        Args:
            holding_id (int): 持仓ID
            
        Returns:
            dict: 持仓详细信息
        """
        try:
            holdings = self.get_all_holdings()
            holding = next((h for h in holdings if h.id == holding_id), None)
            
            if not holding:
                return None
            
            # 计算详细信息
            cost = normalize_number(holding.quantity) * normalize_number(holding.purchase_price)
            current = normalize_number(holding.quantity) * normalize_number(holding.current_price)
            profit = current - cost
            profit_rate = (profit / cost * 100) if cost > 0 else 0
            
            return {
                'id': holding.id,
                'product_code': holding.product_code,
                'product_name': holding.product_name,
                'product_type': holding.product_type,
                'category': holding.category,
                'quantity': holding.quantity,
                'purchase_price': holding.purchase_price,
                'current_price': holding.current_price,
                'cost_value': cost,
                'current_value': current,
                'profit': profit,
                'profit_rate': profit_rate
            }
        except Exception as e:
            print(f"获取持仓详细信息失败: {e}")
            return None
    
    def batch_update_categories(self, force_update=False):
        """
        批量更新所有持仓的资产类别
        
        Args:
            force_update (bool): 是否强制更新
            
        Returns:
            dict: 更新结果统计
        """
        try:
            holdings = self.get_all_holdings()
            updated_count = 0
            unchanged_count = 0
            
            for holding in holdings:
                if not holding.category or force_update:
                    # 设置默认类别
                    self.update_holding(holding.id, {'category': '其他'})
                    updated_count += 1
                else:
                    unchanged_count += 1
            
            return {
                'total_holdings': len(holdings),
                'updated_count': updated_count,
                'unchanged_count': unchanged_count
            }
        except Exception as e:
            print(f"批量更新资产类别失败: {e}")
            return {
                'total_holdings': 0,
                'updated_count': 0,
                'unchanged_count': 0,
                'error': str(e)
            }
    
    def search_holdings(self, keyword):
        """
        搜索持仓
        
        Args:
            keyword (str): 搜索关键词
            
        Returns:
            list: 匹配的持仓列表
        """
        try:
            holdings = self.get_all_holdings()
            keyword_lower = keyword.lower()
            
            matched_holdings = []
            for holding in holdings:
                if (
                    keyword_lower in holding.product_code.lower() or
                    keyword_lower in holding.product_name.lower() or
                    keyword_lower in holding.product_type.lower() or
                    (holding.category and keyword_lower in holding.category.lower())
                ):
                    matched_holdings.append(holding)
            
            return matched_holdings
        except Exception as e:
            print(f"搜索持仓失败: {e}")
            return []

# 全局投资组合管理器实例
# 用于向后兼容，单用户场景可以直接使用
portfolio_manager = PortfolioManager()

# 向后兼容的函数
def get_all_holdings():
    """获取所有持仓（向后兼容）"""
    return portfolio_manager.get_all_holdings()

def add_holding(holding_data):
    """添加持仓（向后兼容）"""
    return portfolio_manager.add_holding(holding_data)

def update_holding(holding_id, update_data):
    """更新持仓（向后兼容）"""
    return portfolio_manager.update_holding(holding_id, update_data)

def delete_holding(holding_id):
    """删除持仓（向后兼容）"""
    return portfolio_manager.delete_holding(holding_id)

def calculate_portfolio_stats():
    """计算投资组合统计信息（向后兼容）"""
    return portfolio_manager.calculate_portfolio_stats()

def calculate_asset_allocation():
    """计算资产配置（向后兼容）"""
    return portfolio_manager.calculate_asset_allocation()
