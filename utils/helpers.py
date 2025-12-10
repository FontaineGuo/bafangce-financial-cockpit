# 辅助函数

def format_currency(value):
    """格式化货币显示"""
    pass

def format_date(date_obj):
    """格式化日期显示"""
    pass

def calculate_percentage(part, total):
    """计算百分比"""
    pass

def get_product_type_display(type):
    """获取产品类型的显示名称"""
    pass

def normalize_number(value):
    """将数值规范化为易读格式，保留小数点后5位
    
    Args:
        value: 需要规范化的数值，可以是科学计数法字符串或数值类型
    
    Returns:
        float: 规范化后的数值，保留小数点后5位；如果无法转换则返回None
    """
    # 处理None值
    if value is None:
        return None
    
    # 如果是字符串类型，先尝试转换为浮点数
    if isinstance(value, str):
        try:
            value = float(value)
        except ValueError:
            # 如果字符串无法转换为浮点数，返回None
            return None
    
    # 检查是否为数值类型
    if not isinstance(value, (int, float)):
        return None
    
    # 保留小数点后5位
    return round(value, 5)
