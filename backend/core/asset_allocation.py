# 资产配置监控模块

import sys
import os

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.models.holding import Holding
from typing import List, Dict, Tuple
from backend.config import constants

class AssetAllocationMonitor:
    """
    资产配置监控类
    用于监控投资组合的资产配置比例，检测是否偏离设定的目标比例
    """
    
    def __init__(self, strategy=None):
        """
        初始化资产配置监控器
        
        Args:
            strategy (dict, optional): 资产配置策略，包含目标比例和偏离上下限
                格式: {
                    'category1': {'target_ratio': 0.3, 'max_deviation': 0.05},
                    'category2': {'target_ratio': 0.5, 'max_deviation': 0.05},
                    ...
                }
        """
        if strategy:
            self.strategy = strategy
        else:
            # 默认使用全天候策略
            self.strategy = constants.DEFAULT_ASSET_ALLOCATION_STRATEGY
    
    def calculate_current_allocation(self, holdings: List[Holding]) -> Dict[str, Dict]:
        """
        计算当前资产配置情况
        
        Args:
            holdings (List[Holding]): 持仓列表
        
        Returns:
            Dict[str, Dict]: 当前资产配置情况
                格式: {
                    'total_value': float,  # 总市值
                    'categories': {
                        'category1': {
                            'value': float,     # 类别市值
                            'ratio': float,     # 类别占比
                            'holding_count': int # 该类别持仓数量
                        },
                        ...
                    }
                }
        """
        categories = {}
        total_value = 0.0
        
        # 计算每个类别的市值
        for holding in holdings:
            category = holding.category or 'unclassified'
            value = holding.current_total
            
            if category not in categories:
                categories[category] = {
                    'value': 0.0,
                    'ratio': 0.0,
                    'holding_count': 0
                }
            
            categories[category]['value'] += value
            categories[category]['holding_count'] += 1
            total_value += value
        
        # 计算每个类别的占比
        if total_value > 0:
            for category in categories:
                categories[category]['ratio'] = categories[category]['value'] / total_value
        
        return {
            'total_value': total_value,
            'categories': categories
        }
    
    def check_deviation(self, current_allocation: Dict[str, Dict]) -> List[Dict]:
        """
        检查资产配置是否偏离目标比例
        
        Args:
            current_allocation (Dict[str, Dict]): 当前资产配置情况
        
        Returns:
            List[Dict]: 偏离预警列表
                格式: [
                    {
                        'category': str,       # 资产类别
                        'target_ratio': float, # 目标比例
                        'current_ratio': float, # 当前比例
                        'deviation': float,    # 偏离值
                        'max_deviation': float, # 最大允许偏离值
                        'status': str          # 'over' or 'under'
                    },
                    ...
                ]
        """
        warnings = []
        
        for category, config in self.strategy.items():
            target_ratio = config['target_ratio']
            max_deviation = config['max_deviation']
            
            current_ratio = current_allocation['categories'].get(category, {}).get('ratio', 0.0)
            deviation = abs(current_ratio - target_ratio)
            
            if deviation > max_deviation:
                status = 'over' if current_ratio > target_ratio else 'under'
                
                warnings.append({
                    'category': category,
                    'target_ratio': target_ratio,
                    'current_ratio': current_ratio,
                    'deviation': deviation,
                    'max_deviation': max_deviation,
                    'status': status
                })
        
        return warnings
    
    def generate_rebalance_suggestions(self, current_allocation: Dict[str, Dict]) -> List[Dict]:
        """
        生成再平衡建议
        
        Args:
            current_allocation (Dict[str, Dict]): 当前资产配置情况
        
        Returns:
            List[Dict]: 再平衡建议列表
                格式: [
                    {
                        'category': str,          # 资产类别
                        'target_ratio': float,    # 目标比例
                        'current_ratio': float,   # 当前比例
                        'target_value': float,    # 目标市值
                        'current_value': float,   # 当前市值
                        'adjust_amount': float,   # 需要调整的金额
                        'adjust_direction': str   # 'increase' or 'decrease'
                    },
                    ...
                ]
        """
        suggestions = []
        total_value = current_allocation['total_value']
        
        for category, config in self.strategy.items():
            target_ratio = config['target_ratio']
            target_value = total_value * target_ratio
            current_value = current_allocation['categories'].get(category, {}).get('value', 0.0)
            
            adjust_amount = target_value - current_value
            if abs(adjust_amount) > 0:
                adjust_direction = 'increase' if adjust_amount > 0 else 'decrease'
                
                suggestions.append({
                    'category': category,
                    'target_ratio': target_ratio,
                    'current_ratio': current_value / total_value if total_value > 0 else 0,
                    'target_value': target_value,
                    'current_value': current_value,
                    'adjust_amount': abs(adjust_amount),
                    'adjust_direction': adjust_direction
                })
        
        return suggestions
    
    def calculate_allocation_score(self, current_allocation: Dict[str, Dict]) -> float:
        """
        计算资产配置分数（0-100分）
        
        Args:
            current_allocation (Dict[str, Dict]): 当前资产配置情况
        
        Returns:
            float: 资产配置分数
        """
        warnings = self.check_deviation(current_allocation)
        
        if not warnings:
            return 100.0
        
        # 计算每个偏离的严重性
        total_penalty = 0.0
        max_penalty = 0.0
        
        for warning in warnings:
            # 偏离程度比例
            deviation_ratio = warning['deviation'] / warning['max_deviation']
            
            # 计算惩罚分数（最高10分）
            penalty = min(deviation_ratio * 10, 10)
            
            total_penalty += penalty
            max_penalty += 10
        
        # 计算最终分数
        score = max(0.0, 100.0 - (total_penalty / max_penalty * 100.0))
        
        return score
