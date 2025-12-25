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

# 全局变量用于存储baostock登录状态
_baostock_login_status = {
    'is_logged_in': False,
    'login_date': None  # 记录登录日期
}

def is_trading_day(date):
    """
    判断指定日期是否为交易日
    
    Args:
        date (datetime.date): 要判断的日期
    
    Returns:
        bool: True表示是交易日，False表示非交易日
    """
    try:
        # 尝试使用baostock包
        import baostock as bs
        
        # 获取当前日期
        current_date = date.today()
        
        # 检查是否已经登录并且登录日期是今天
        if not _baostock_login_status['is_logged_in'] or _baostock_login_status['login_date'] != current_date:
            # 初始化baostock连接
            lg = bs.login()
            if lg.error_code != '0':
                print(f"[日志] 登录baostock失败: {lg.error_msg}，将回退到周末判断")
                # 登录失败，回退到简单的周末判断
                result = date.weekday() < 5
                print(f"[日志] 结果来源: 周末判断，日期 {date} 是否为交易日: {result}")
                return result
            else:
                # 登录成功，更新登录状态
                _baostock_login_status['is_logged_in'] = True
                _baostock_login_status['login_date'] = current_date
                print(f"[日志] 登录baostock成功")
        else:
            print(f"[日志] 已登录baostock，无需重复登录")
        
        # 转换日期格式为字符串
        date_str = date.strftime('%Y-%m-%d')
        
        # 获取指定日期的交易日信息
        rs = bs.query_trade_dates(start_date=date_str, end_date=date_str)
        if rs.error_code != '0':
            print(f"[日志] 获取交易日信息失败: {rs.error_msg}，将回退到周末判断")
            result = date.weekday() < 5
            print(f"[日志] 结果来源: 周末判断，日期 {date} 是否为交易日: {result}")
            return result
        
        # 解析结果
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
        
        if data_list:
            # data_list[0][1] 是 is_trading_day 字段，'1' 表示是交易日，'0' 表示非交易日
            result = data_list[0][1] == '1'
            print(f"[日志] 结果来源: baostock，日期 {date} 是否为交易日: {result}")
            return result
        else:
            # 如果没有获取到数据，回退到周末判断
            print(f"[日志] 未获取到baostock数据，将回退到周末判断")
            result = date.weekday() < 5
            print(f"[日志] 结果来源: 周末判断，日期 {date} 是否为交易日: {result}")
            return result
    except ImportError:
        # 如果没有安装baostock包，使用简单的周末判断
        result = date.weekday() < 5
        print(f"[日志] 结果来源: 周末判断 (未安装baostock)，日期 {date} 是否为交易日: {result}")
        return result
