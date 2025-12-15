# 资产配置监控模块

from models.holding import Holding
from typing import List, Dict, Tuple
from config import constants

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
        categories = current_allocation.get('categories', {})
        
        for category, config in self.strategy.items():
            target_ratio = config['target_ratio']
            max_deviation = config['max_deviation']
            
            # 获取当前比例，如果该类别没有持仓则为0
            current_ratio = categories.get(category, {}).get('ratio', 0.0)
            
            # 计算偏离值
            deviation = abs(current_ratio - target_ratio)
            
            # 检查是否超过最大允许偏离值
            if deviation > max_deviation:
                # 确定是超配还是低配
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
    
    def generate_report(self, holdings: List[Holding]) -> Dict[str, any]:
        """
        生成资产配置报告
        
        Args:
            holdings (List[Holding]): 持仓列表
        
        Returns:
            Dict[str, any]: 资产配置报告
                格式: {
                    'current_allocation': Dict[str, Dict],  # 当前资产配置
                    'strategy': Dict[str, Dict],            # 配置策略
                    'warnings': List[Dict],                 # 偏离预警
                    'total_holding_count': int              # 总持仓数量
                }
        """
        current_allocation = self.calculate_current_allocation(holdings)
        warnings = self.check_deviation(current_allocation)
        
        return {
            'current_allocation': current_allocation,
            'strategy': self.strategy,
            'warnings': warnings,
            'total_holding_count': len(holdings)
        }
    
    def get_allocation_suggestions(self, warnings: List[Dict]) -> List[Dict]:
        """
        根据偏离情况生成调整建议
        
        Args:
            warnings (List[Dict]): 偏离预警列表
        
        Returns:
            List[Dict]: 调整建议列表
                格式: [
                    {
                        'category': str,   # 资产类别
                        'status': str,     # 'over' or 'under'
                        'suggestion': str  # 调整建议
                    },
                    ...
                ]
        """
        suggestions = []
        
        for warning in warnings:
            category = warning['category']
            status = warning['status']
            target_ratio = warning['target_ratio']
            current_ratio = warning['current_ratio']
            
            if status == 'over':
                # 超配建议
                suggestion = f"{category}类资产当前比例({current_ratio:.2%})超过目标比例({target_ratio:.2%})，建议适当减持"
            else:
                # 低配建议
                suggestion = f"{category}类资产当前比例({current_ratio:.2%})低于目标比例({target_ratio:.2%})，建议适当增持"
            
            suggestions.append({
                'category': category,
                'status': status,
                'suggestion': suggestion
            })
        
        return suggestions

# 辅助函数
def print_allocation_report(report: Dict[str, any]):
    """
    打印资产配置报告
    
    Args:
        report (Dict[str, any]): 资产配置报告
    """
    print("\n=== 资产配置报告 ===")
    
    # 打印总览
    total_value = report['current_allocation']['total_value']
    total_holding_count = report['total_holding_count']
    print(f"总市值: {total_value:.2f} 元")
    print(f"总持仓数量: {total_holding_count}")
    
    # 合并打印当前配置和目标配置
    print("\n当前资产配置与目标配置对比:")
    print(f"{'类别':<18}{'当前市值':>10}{'当前占比':>10}{'持仓数量':>12}{'目标比例':>12}{'最大偏离':>12}")
    print("-" * 86)
    
    categories = report['current_allocation']['categories']
    strategy = report['strategy']
    
    # 获取所有类别（确保包含当前配置和目标策略中的所有类别）
    all_categories = sorted(set(categories.keys()).union(set(strategy.keys())))
    
    for category in all_categories:
        # 获取当前配置数据
        if category in categories:
            current_data = categories[category]
            value = current_data['value']
            current_ratio = current_data['ratio']
            count = current_data['holding_count']
        else:
            value = 0.0
            current_ratio = 0.0
            count = 0
        
        # 获取目标配置数据
        if category in strategy:
            target_data = strategy[category]
            target_ratio = target_data['target_ratio']
            max_deviation = target_data['max_deviation']
        else:
            target_ratio = 0.0
            max_deviation = 0.0
        
        print(f"{category:<18}{value:>10.2f}{current_ratio:>10.2%}{count:>12}{target_ratio:>12.2%}{max_deviation:>12.2%}")
    
    # 打印偏离预警
    warnings = report['warnings']
    if warnings:
        print("\n=== 配置偏离预警 ===")
        print(f"{'类别':<15}{'当前比例':>10}{'目标比例':>10}{'偏离值':>10}{'状态':>8}")
        print("-" * 63)
        
        for warning in warnings:
            category = warning['category']
            current_ratio = warning['current_ratio']
            target_ratio = warning['target_ratio']
            deviation = warning['deviation']
            status = '超配' if warning['status'] == 'over' else '低配'
            
            # 超配用红色，低配用黄色
            if warning['status'] == 'over':
                print(f"{category:<15}{current_ratio:>10.2%}{target_ratio:>10.2%}{deviation:>10.2%}{status:>8} \033[91m⚠\033[0m")
            else:
                print(f"{category:<15}{current_ratio:>10.2%}{target_ratio:>10.2%}{deviation:>10.2%}{status:>8} \033[93m⚠\033[0m")
        
        # 打印调整建议
        suggestions = AssetAllocationMonitor().get_allocation_suggestions(warnings)
        print("\n=== 调整建议 ===")
        for suggestion in suggestions:
            print(f"- {suggestion['suggestion']}")
    else:
        print("\n✅ 资产配置符合目标比例，无需调整")
    
    print("\n" + "=" * 50)
