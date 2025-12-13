# 命令行式持仓添加模块
import sys
import os

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.holdings_manager import add_holding, get_all_holdings, update_holding, delete_holding
from core.data_fetcher import get_stock_data, get_fund_data, get_etf_data, fetch_and_store_etf_data, fetch_and_store_fund_data
from models.holding import Holding
from core.database import create_tables
from utils import HtmlExporter

def print_menu():
    """
    打印主菜单
    """
    print("\n" + "=" * 50)
    print("          持仓管理模块")
    print("=" * 50)
    print("1. 添加持仓（自动判断股票/基金）")
    print("2. 查看所有持仓")
    print("3. 更新持仓")
    print("4. 删除持仓")
    print("5. 强制同步持仓数据")
    print("0. 退出")
    print("=" * 50)

def safe_get_field(data_dict, key, default="null"):
    """
    安全获取字典中的字段值，将None转换为指定的默认值
    
    Args:
        data_dict (dict): 数据字典
        key (str): 要获取的键名
        default (str): 默认值，默认为"null"
    
    Returns:
        str: 字段值或默认值
    """
    return data_dict.get(key) if data_dict.get(key) is not None else default

def get_product_info(product_code, max_attempts=3):
    """
    自适应获取产品信息（自动判断是股票、ETF还是基金）
    
    Args:
        product_code (str): 产品代码
        max_attempts (int): 最大尝试次数
    
    Returns:
        tuple: (product_type, product_info) 产品类型和产品信息
    """
    attempt = 0
    
    # 先尝试作为股票查询（更快）
    print(f"\n尝试获取产品信息: {product_code}")
    print(f"第 {attempt + 1} 次尝试: 作为股票查询...")
    
    try:
        # 检查是否为股票代码格式（6位数字）
        if not (product_code.isdigit() and len(product_code) == 6):
            raise ValueError("股票代码应为6位数字")
        
        stock_info = get_stock_data(product_code)
        if stock_info and stock_info.get('stock_name'):
            print(f"✅ 成功获取股票信息: {stock_info['stock_name']}")
            return ("stock", stock_info)
    except Exception as e:
        print(f"❌ 股票查询失败: {e}")
    
    attempt += 1
    
    # 如果股票查询失败，尝试作为ETF查询
    if attempt < max_attempts:
        print(f"第 {attempt + 1} 次尝试: 作为ETF查询...")
        
        try:
            # 检查是否为ETF代码格式（通常为6位数字）
            if not (product_code.isdigit() and len(product_code) == 6):
                raise ValueError("ETF代码应为6位数字")
            
            etf_info = get_etf_data(product_code)
            if etf_info and etf_info.get('etf_name'):
                print(f"✅ 成功获取ETF信息: {etf_info['etf_name']}")
                return ("etf", etf_info)
        except Exception as e:
            print(f"❌ ETF查询失败: {e}")
    
    attempt += 1
    
    # 如果ETF查询失败，且还有尝试次数，尝试作为基金查询
    if attempt < max_attempts:
        print(f"第 {attempt + 1} 次尝试: 作为基金查询...")
        
        try:
            # 检查是否为基金代码格式（通常为6位数字）
            if not (product_code.isdigit() and len(product_code) == 6):
                raise ValueError("基金代码应为6位数字")
            
            # 先检查数据库中是否已有该基金数据
            from core.database import get_fund_by_code
            fund_info = get_fund_by_code(product_code)
            
            if fund_info and fund_info.get('fund_name'):
                print(f"✅ 从数据库获取基金信息: {fund_info['fund_name']}")
                return ("fund", fund_info)
            
            # 如果数据库中没有，再尝试获取新数据（会下载所有基金）
            print("⚠️  数据库中没有该基金数据，正在获取最新数据...")
            print("ℹ️  提示：首次获取基金数据需要下载所有市售基金，可能需要较长时间")
            
            fund_info = get_fund_data(product_code)
            if fund_info and fund_info.get('fund_name'):
                print(f"✅ 成功获取基金信息: {fund_info['fund_name']}")
                return ("fund", fund_info)
        except Exception as e:
            print(f"❌ 基金查询失败: {e}")
    
    print(f"❌ 无法获取产品信息: {product_code}")
    return (None, None)

def add_holding_cli():
    """
    添加持仓的命令行界面（自适应判断产品类型）
    """
    print("\n=== 添加持仓 ===")
    print("ℹ️  系统将自动判断输入的产品代码是股票还是基金")
    print("ℹ️  股票代码应为6位数字，基金代码通常为6位数字")
    
    # 获取产品代码
    while True:
        product_code = input("请输入产品代码: ").strip()
        if not product_code:
            print("错误: 代码不能为空!")
            continue
        
        # 自适应获取产品信息
        product_type, product_info = get_product_info(product_code)
        
        if product_info:
            # 设置产品类型名称
            if product_type == "stock":
                product_type_name = "股票"
            elif product_type == "etf":
                product_type_name = "ETF"
            else:
                product_type_name = "基金"
            
            # 显示产品信息
            print(f"\n{product_type_name}信息:")
            if product_type == "stock":
                print(f"代码: {safe_get_field(product_info, 'stock_code')}")
                print(f"名称: {safe_get_field(product_info, 'stock_name')}")
                print(f"当前价格: {safe_get_field(product_info, 'current_price')}")
                product_name = product_info.get('stock_name') or "unknown"
                current_price = product_info.get('current_price') or 0.0
            elif product_type == "etf":
                print(f"代码: {safe_get_field(product_info, 'etf_code')}")
                print(f"名称: {safe_get_field(product_info, 'etf_name')}")
                print(f"当前价格: {safe_get_field(product_info, 'net_value')}")
                product_name = product_info.get('etf_name') or "unknown"
                current_price = product_info.get('net_value') or 0.0
            else:
                print(f"代码: {safe_get_field(product_info, 'fund_code')}")
                print(f"名称: {safe_get_field(product_info, 'fund_name')}")
                print(f"当前价格: {safe_get_field(product_info, 'net_value')}")
                product_name = product_info.get('fund_name') or "unknown"
                current_price = product_info.get('net_value') or 0.0
            
            break
        else:
            print(f"错误: 无法获取产品信息，请检查代码是否正确!")
    
    # 获取持仓份额
    while True:
        try:
            quantity = float(input(f"请输入持仓份额: "))
            if quantity <= 0:
                print("错误: 持仓份额必须大于0!")
                continue
            break
        except ValueError:
            print("错误: 请输入有效的数字!")
    
    # 获取持仓成本
    while True:
        try:
            purchase_price = float(input(f"请输入持仓成本: "))
            if purchase_price < 0:
                print("错误: 持仓成本不能小于0!")
                continue
            break
        except ValueError:
            print("错误: 请输入有效的数字!")
    
    # 确认信息
    print("\n=== 持仓信息确认 ===")
    print(f"产品类型: {product_type_name}")
    print(f"产品代码: {product_code}")
    print(f"产品名称: {product_name}")
    print(f"持仓份额: {quantity}")
    print(f"持仓成本: {purchase_price}")
    print(f"当前价格: {current_price}")
    
    confirm = input("\n确认添加此持仓吗？(y/n): ").strip().lower()
    if confirm != 'y':
        print("操作已取消!")
        return
    
    # 创建Holding对象
    holding = Holding(
        product_code=product_code,
        product_name=product_name,
        product_type=product_type,
        quantity=quantity,
        purchase_price=purchase_price,
        current_price=current_price
    )
    
    # 添加持仓
    try:
        holding_id = add_holding(holding)
        print(f"\n✅ 持仓添加成功！持仓ID: {holding_id}")
    except Exception as e:
        print(f"\n❌ 持仓添加失败: {e}")

def supports_color():
    """检查终端是否支持ANSI颜色"""
    import sys
    import os
    
    # 检查是否在Windows系统上
    if sys.platform == 'win32':
        # Windows 10+ 支持ANSI颜色
        return (os.environ.get('ANSICON') is not None or
                os.environ.get('WT_SESSION') is not None or  # Windows Terminal
                os.environ.get('ConEmuANSI') == 'ON' or  # ConEmu
                os.environ.get('TERM') == 'xterm')
    else:
        # Unix-like系统检查TERM环境变量
        return (os.environ.get('TERM') or '').endswith(('color', 'ansi'))

def colorize(text, color='default'):
    """给文本添加颜色"""
    if not supports_color():
        return text
        
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'reset': '\033[0m',
        'default': ''
    }
    return f"{colors.get(color, '')}{text}{colors['reset']}"

def update_holding_cli():
    """更新持仓的命令行界面"""
    print(f"\n{colorize('=== 更新持仓 ===', 'blue')}")
    
    try:
        # 获取所有持仓
        holdings = get_all_holdings()
        
        if not holdings:
            print(f"{colorize('暂无持仓记录！', 'yellow')}")
            return
        
        # 显示当前持仓列表（简化版）
        print(f"\n{colorize('当前持仓列表:', 'blue')}")
        print(f"{'ID':^5} {'类型':^6} {'代码':^12} {'名称':^18} {'份额':^12} {'成本价':^12}")
        print("-" * 80)
        
        for holding in holdings:
            if holding.product_type == "stock":
                product_type_str = "股票"
            elif holding.product_type == "etf":
                product_type_str = "ETF"
            else:
                product_type_str = "基金"
            # 安全处理可能为None的字段
            safe_id = holding.id or "null"
            safe_code = holding.product_code or "null"
            safe_name = holding.product_name or "null"
            safe_quantity = holding.quantity if holding.quantity is not None else 0.0
            safe_purchase_price = holding.purchase_price if holding.purchase_price is not None else 0.0
            print(f"{safe_id:^5} {colorize(product_type_str, 'yellow'):^6} {safe_code:^12} {safe_name:^18} {safe_quantity:^12.2f} {safe_purchase_price:^12.2f}")
        
        print("-" * 80)
        
        # 获取要更新的持仓ID
        while True:
            try:
                holding_id = int(input(f"{colorize('请输入要更新的持仓ID: ', 'blue')}"))
                # 查找该ID对应的持仓
                target_holding = None
                for holding in holdings:
                    if holding.id == holding_id:
                        target_holding = holding
                        break
                
                if target_holding:
                    break
                else:
                    print(f"{colorize(f'错误: 找不到ID为{holding_id}的持仓！', 'red')}")
            except ValueError:
                print(f"{colorize('错误: 请输入有效的数字ID！', 'red')}")
        
        # 显示当前持仓详情
        print(f"\n{colorize('当前持仓详情:', 'blue')}")
        if target_holding.product_type == "stock":
            product_type_name = "股票"
        elif target_holding.product_type == "etf":
            product_type_name = "ETF"
        else:
            product_type_name = "基金"
        # 安全处理可能为None的字段
        safe_id = target_holding.id or "null"
        safe_code = target_holding.product_code or "null"
        safe_name = target_holding.product_name or "null"
        safe_quantity = target_holding.quantity if target_holding.quantity is not None else 0.0
        safe_purchase_price = target_holding.purchase_price if target_holding.purchase_price is not None else 0.0
        print(f"ID: {safe_id}")
        print(f"类型: {product_type_name}")
        print(f"代码: {safe_code}")
        print(f"名称: {safe_name}")
        print(f"当前份额: {safe_quantity}")
        print(f"当前成本价: {safe_purchase_price}")
        
        # 获取新的份额
        while True:
            new_quantity = input(f"\n{colorize('请输入新的份额 (直接回车保持不变): ', 'blue')}").strip()
            if not new_quantity:
                new_quantity = target_holding.quantity
                break
            try:
                new_quantity = float(new_quantity)
                if new_quantity <= 0:
                    print(f"{colorize('错误: 份额必须大于0！', 'red')}")
                    continue
                break
            except ValueError:
                print(f"{colorize('错误: 请输入有效的数字！', 'red')}")
        
        # 获取新的成本价
        while True:
            new_purchase_price = input(f"{colorize('请输入新的成本价 (直接回车保持不变): ', 'blue')}").strip()
            if not new_purchase_price:
                new_purchase_price = target_holding.purchase_price
                break
            try:
                new_purchase_price = float(new_purchase_price)
                if new_purchase_price < 0:
                    print(f"{colorize('错误: 成本价不能小于0！', 'red')}")
                    continue
                break
            except ValueError:
                print(f"{colorize('错误: 请输入有效的数字！', 'red')}")
        
        # 确认更新
        print(f"\n{colorize('更新确认:', 'blue')}")
        # 安全处理可能为None的字段
        safe_id = target_holding.id or "null"
        safe_code = target_holding.product_code or "null"
        safe_name = target_holding.product_name or "null"
        safe_quantity = target_holding.quantity if target_holding.quantity is not None else 0.0
        safe_purchase_price = target_holding.purchase_price if target_holding.purchase_price is not None else 0.0
        safe_new_quantity = new_quantity if new_quantity is not None else 0.0
        safe_new_purchase_price = new_purchase_price if new_purchase_price is not None else 0.0
        print(f"ID: {safe_id}")
        print(f"类型: {product_type_name}")
        print(f"代码: {safe_code}")
        print(f"名称: {safe_name}")
        print(f"原份额: {safe_quantity} → 新份额: {safe_new_quantity}")
        print(f"原成本价: {safe_purchase_price} → 新成本价: {safe_new_purchase_price}")
        
        confirm = input(f"\n{colorize('确认更新此持仓吗？(y/n): ', 'blue')}").strip().lower()
        if confirm != 'y':
            print(f"{colorize('操作已取消！', 'yellow')}")
            return
        
        # 创建更新后的持仓对象
        updated_holding = Holding(
            id=target_holding.id,
            product_code=target_holding.product_code,
            product_name=target_holding.product_name,
            product_type=target_holding.product_type,
            quantity=new_quantity,
            purchase_price=new_purchase_price,
            current_price=target_holding.current_price
        )
        
        # 更新持仓
        success = update_holding(holding_id, updated_holding)
        
        if success:
            print(f"\n{colorize('✅ 持仓更新成功！', 'green')}")
        else:
            print(f"\n{colorize('❌ 持仓更新失败！', 'red')}")
            
    except Exception as e:
        print(f"\n{colorize('❌ 更新持仓失败:', 'red')} {e}")

def delete_holding_cli():
    """删除持仓的命令行界面"""
    print(f"\n{colorize('=== 删除持仓 ===', 'blue')}")
    
    try:
        # 获取所有持仓
        holdings = get_all_holdings()
        
        if not holdings:
            print(f"{colorize('暂无持仓记录！', 'yellow')}")
            return
        
        # 显示当前持仓列表（简化版）
        print(f"\n{colorize('当前持仓列表:', 'blue')}")
        print(f"{'ID':^5} {'类型':^6} {'代码':^12} {'名称':^18} {'份额':^12} {'成本价':^12}")
        print("=" * 80)
        
        for holding in holdings:
            product_type_str = "股票" if holding.product_type == "stock" else "基金"
            # 安全处理可能为None的字段
            safe_id = holding.id or "null"
            safe_code = holding.product_code or "null"
            safe_name = holding.product_name or "null"
            safe_quantity = holding.quantity if holding.quantity is not None else 0.0
            safe_purchase_price = holding.purchase_price if holding.purchase_price is not None else 0.0
            print(f"{safe_id:^5} {colorize(product_type_str, 'yellow'):^6} {safe_code:^12} {safe_name:^18} {safe_quantity:^12.2f} {safe_purchase_price:^12.2f}")
        
        print("=" * 80)
        
        # 获取要删除的持仓ID
        while True:
            try:
                holding_id = int(input(f"{colorize('请输入要删除的持仓ID: ', 'blue')}"))
                # 查找该ID对应的持仓
                target_holding = None
                for holding in holdings:
                    if holding.id == holding_id:
                        target_holding = holding
                        break
                
                if target_holding:
                    break
                else:
                    print(f"{colorize(f'错误: 找不到ID为{holding_id}的持仓！', 'red')}")
            except ValueError:
                print(f"{colorize('错误: 请输入有效的数字ID！', 'red')}")
        
        # 显示要删除的持仓详情
        print(f"\n{colorize('要删除的持仓详情:', 'red')}")
        product_type_name = "股票" if target_holding.product_type == "stock" else "基金"
        # 安全处理可能为None的字段
        safe_id = target_holding.id or "null"
        safe_code = target_holding.product_code or "null"
        safe_name = target_holding.product_name or "null"
        safe_quantity = target_holding.quantity if target_holding.quantity is not None else 0.0
        safe_purchase_price = target_holding.purchase_price if target_holding.purchase_price is not None else 0.0
        print(f"ID: {safe_id}")
        print(f"类型: {product_type_name}")
        print(f"代码: {safe_code}")
        print(f"名称: {safe_name}")
        print(f"份额: {safe_quantity}")
        print(f"成本价: {safe_purchase_price}")
        
        # 确认删除
        confirm = input(f"\n{colorize('⚠️  确认要删除此持仓吗？此操作不可恢复！(y/n): ', 'red')}").strip().lower()
        if confirm != 'y':
            print(f"{colorize('操作已取消！', 'yellow')}")
            return
        
        # 删除持仓
        success = delete_holding(holding_id)
        
        if success:
            print(f"\n{colorize('✅ 持仓删除成功！', 'green')}")
        else:
            print(f"\n{colorize('❌ 持仓删除失败！', 'red')}")
            
    except Exception as e:
        print(f"\n{colorize('❌ 删除持仓失败:', 'red')} {e}")

def view_holdings_cli():
    """查看所有持仓的命令行界面"""
    print(f"\n{colorize('=== 查看所有持仓 ===', 'blue')}")
    
    try:
        # 获取所有持仓
        holdings = get_all_holdings()
        
        if not holdings:
            print(f"{colorize('暂无持仓记录！', 'yellow')}")
            return
        
        # 计算总计数据
        total_cost = 0
        total_current = 0
        total_profit = 0
        
        # 转换所有持仓为Holding对象并计算总计
        holding_objects = []
        for holding in holdings:
            if isinstance(holding, tuple):
                # 安全处理数据库返回的元组，确保没有None值
                holding = Holding.from_dict({
                    'id': holding[0] or 0,
                    'product_code': holding[1] or "null",
                    'product_name': holding[2] or "null",
                    'product_type': holding[3] or "null",
                    'quantity': holding[4] or 0.0,
                    'purchase_price': holding[5] or 0.0,
                    'current_price': holding[6] or 0.0,
                    'update_time': holding[7]
                })
            holding_objects.append(holding)
            # 确保计算时使用安全值
            safe_cost_total = holding.cost_total if holding.cost_total is not None else 0.0
            safe_current_total = holding.current_total if holding.current_total is not None else 0.0
            safe_profit_total = holding.profit_total if holding.profit_total is not None else 0.0
            total_cost += safe_cost_total
            total_current += safe_current_total
            total_profit += safe_profit_total
        
        # 计算总盈利率
        total_profit_rate = (total_profit / total_cost * 100) if total_cost > 0 else 0
        
        # 打印持仓列表
        # 定义表格宽度
        col_widths = [5, 6, 12, 18, 12, 14, 14, 14, 14, 14, 11]
        
        # 打印顶部边框
        border_line = "+" + "+" .join(["-" * (width + 2) for width in col_widths]) + "+"
        print(f"\n{border_line}")
        
        # 打印标题行
        headers = ["ID", "类型", "代码", "名称", "份额", "成本价", "当前价", "成本总额", "当前总额", "盈亏额", "盈亏率"]
        header_line = "|"
        for i, header in enumerate(headers):
            header_line += f" {header:^{col_widths[i]}} |"
        print(header_line)
        
        # 打印标题分隔线
        separator_line = "+" + "+" .join(["=" * (width + 2) for width in col_widths]) + "+"
        print(separator_line)
        
        for holding in holding_objects:
            # 计算显示数据
            cost_total = holding.cost_total
            current_total = holding.current_total
            profit_total = holding.profit_total
            profit_rate = holding.profit_rate * 100 if holding.profit_rate is not None else 0
            if holding.product_type == "stock":
                product_type_str = "股票"
            elif holding.product_type == "etf":
                product_type_str = "ETF"
            else:
                product_type_str = "基金"
            
            # 确定盈亏颜色
            profit_color = 'green' if profit_total >= 0 else 'red'
            
            # 格式化数字字符串（居中对齐），安全处理可能的None值
            safe_quantity = holding.quantity if holding.quantity is not None else 0.0
            safe_purchase_price = holding.purchase_price if holding.purchase_price is not None else 0.0
            safe_current_price = holding.current_price if holding.current_price is not None else 0.0
            safe_cost_total = cost_total if cost_total is not None else 0.0
            safe_current_total = current_total if current_total is not None else 0.0
            safe_profit_total = profit_total if profit_total is not None else 0.0
            
            quantity_str = f"{safe_quantity:^12.2f}"
            purchase_price_str = f"{safe_purchase_price:^14.4f}"
            current_price_str = f"{safe_current_price:^14.4f}"
            cost_total_str = f"{safe_cost_total:^14.2f}"
            current_total_str = f"{safe_current_total:^14.2f}"
            profit_total_str = f"{safe_profit_total:^14.2f}"
            # 先组合数字和百分比符号，再居中对齐
            profit_rate_str = f"{profit_rate:.2f}%"  # 不在这里对齐
            profit_rate_str = f"{profit_rate_str:^11}"  # 单独进行居中对齐，确保百分比符号紧跟数字
            
            # 打印一行记录
            data_line = "|"
            # ID
            data_line += f" {holding.id:<{col_widths[0]}} |"
            # 类型
            data_line += f" {colorize(product_type_str, 'yellow'):^{col_widths[1]}} |"
            # 代码
            data_line += f" {holding.product_code:^{col_widths[2]}} |"
            # 名称
            data_line += f" {holding.product_name:^{col_widths[3]}} |"
            # 份额
            data_line += f" {quantity_str.strip():^{col_widths[4]}} |"
            # 成本价
            data_line += f" {purchase_price_str.strip():^{col_widths[5]}} |"
            # 当前价
            data_line += f" {current_price_str.strip():^{col_widths[6]}} |"
            # 成本总额
            data_line += f" {cost_total_str.strip():^{col_widths[7]}} |"
            # 当前总额
            data_line += f" {current_total_str.strip():^{col_widths[8]}} |"
            # 盈亏额
            data_line += f" {colorize(profit_total_str.strip(), profit_color):^{col_widths[9]}} |"
            # 盈亏率
            data_line += f" {colorize(profit_rate_str.strip(), profit_color):^{col_widths[10]}} |"
            print(data_line)
        
        # 打印数据和总计之间的分隔线
        print(separator_line)
        
        # 打印总计行
        total_profit_color = 'green' if total_profit >= 0 else 'red'
        # 格式化总盈亏率，先组合数字和百分比符号
        total_profit_rate_str = f"{total_profit_rate:.2f}%"
        total_profit_rate_str = f"{total_profit_rate_str:^{col_widths[10]}}"  # 单独进行居中对齐，确保百分比符号紧跟数字
        
        total_line = "|"
        total_line += f" {'总计':<{col_widths[0]}} |"
        total_line += f" {'':^{col_widths[1]}} |"
        total_line += f" {'':^{col_widths[2]}} |"
        total_line += f" {'':^{col_widths[3]}} |"
        total_line += f" {'':^{col_widths[4]}} |"
        total_line += f" {'':^{col_widths[5]}} |"
        total_line += f" {'':^{col_widths[6]}} |"
        total_line += f" {colorize(f'{total_cost:.2f}', 'blue'):^{col_widths[7]}} |"
        total_line += f" {colorize(f'{total_current:.2f}', 'blue'):^{col_widths[8]}} |"
        total_line += f" {colorize(f'{total_profit:.2f}', total_profit_color):^{col_widths[9]}} |"
        total_line += f" {colorize(total_profit_rate_str, total_profit_color):^{col_widths[10]}} |"
        print(total_line)
        
        # 打印底部边框
        print(border_line)
        
        # 统计信息
        stock_count = sum(1 for h in holding_objects if h.product_type == 'stock')
        etf_count = sum(1 for h in holding_objects if h.product_type == 'etf')
        fund_count = sum(1 for h in holding_objects if h.product_type == 'fund')
        print(f"\n{colorize('统计信息:', 'blue')}")
        print(f"  总持仓数量: {len(holding_objects)}  股票: {stock_count}  ETF: {etf_count}  基金: {fund_count}")
        print(f"  总成本: {total_cost:.2f}  总市值: {total_current:.2f}  总盈亏: {total_profit:.2f}  总盈利率: {total_profit_rate:.2f}%")
        
        # 询问是否导出为HTML文件
        export_choice = input(f"\n{colorize('是否将持仓数据导出为HTML表格文件？(y/n): ', 'blue')}").strip().lower()
        if export_choice == 'y':
            try:
                exporter = HtmlExporter()
                # 导出到当前目录
                html_file = exporter.export_holdings(
                    holding_objects, total_cost, total_current, total_profit, total_profit_rate,
                    stock_count, etf_count, fund_count
                )
                print(f"\n{colorize('✅ HTML表格已成功导出！', 'green')}")
                print(f"   文件路径: {html_file}")
                print(f"   您可以用浏览器打开此文件查看详细的持仓报表")
            except Exception as e:
                print(f"\n{colorize('❌ HTML导出失败:', 'red')} {e}")
        
    except Exception as e:
        print(f"\n{colorize('❌ 获取持仓失败:', 'red')} {e}")


def force_sync_holdings_cli():
    """
    强制同步持仓数据的命令行界面
    """
    print(f"\n{colorize('=== 强制同步持仓数据 ===', 'blue')}")
    
    try:
        # 获取所有持仓
        holdings = get_all_holdings()
        
        if not holdings:
            print(f"{colorize('暂无持仓记录！', 'yellow')}")
            return
        
        # 统计不同类型的持仓
        stock_codes = []
        etf_codes = set()
        fund_codes = set()
        
        for holding in holdings:
            if isinstance(holding, tuple):
                # 数据库返回的元组格式
                product_type = holding[3] or ""
                product_code = holding[1] or ""
            else:
                # Holding对象格式
                product_type = holding.product_type or ""
                product_code = holding.product_code or ""
            
            if product_type == "stock":
                stock_codes.append(product_code)
            elif product_type == "etf":
                etf_codes.add(product_code)
            elif product_type == "fund":
                fund_codes.add(product_code)
        
        print(f"\n{colorize('持仓统计:', 'blue')}")
        print(f"  股票: {len(stock_codes)} 只")
        print(f"  ETF: {len(etf_codes)} 只")
        print(f"  基金: {len(fund_codes)} 只")
        print(f"  总计: {len(holdings)} 个持仓")
        
        # 确认是否继续
        confirm = input(f"\n{colorize('确认要强制同步所有持仓数据吗？(y/n): ', 'yellow')}").strip().lower()
        if confirm != 'y':
            print(f"\n{colorize('操作已取消！', 'yellow')}")
            return
        
        print(f"\n{colorize('开始同步数据...', 'green')}")
        
        # 同步ETF数据（一次获取所有）
        if etf_codes:
            print(f"\n{colorize('1. 同步ETF数据:', 'blue')}")
            # 随便选一个ETF代码触发获取所有ETF数据
            sample_etf = next(iter(etf_codes))
            print(f"   获取所有ETF数据...")
            fetch_and_store_etf_data(sample_etf)
            print(f"   ETF数据同步完成！")
        
        # 同步基金数据（一次获取所有）
        if fund_codes:
            print(f"\n{colorize('2. 同步基金数据:', 'blue')}")
            # 随便选一个基金代码触发获取所有基金数据
            sample_fund = next(iter(fund_codes))
            print(f"   获取所有基金数据...")
            fetch_and_store_fund_data(sample_fund)
            print(f"   基金数据同步完成！")
        
        # 同步股票数据（逐个获取）
        if stock_codes:
            print(f"\n{colorize('3. 同步股票数据:', 'blue')}")
            for i, stock_code in enumerate(stock_codes, 1):
                print(f"   {i}/{len(stock_codes)}: 同步股票 {stock_code}...")
                get_stock_data(stock_code, force_update=True)
            print(f"   股票数据同步完成！")
        
        # 更新持仓的当前价格
        print(f"\n{colorize('4. 更新持仓数据:', 'blue')}")
        updated_count = 0
        
        for holding in holdings:
            if isinstance(holding, tuple):
                # 转换为Holding对象
                holding_id = holding[0]
                product_code = holding[1]
                product_type = holding[3]
            else:
                holding_id = holding.id
                product_code = holding.product_code
                product_type = holding.product_type
            
            print(f"   更新持仓ID {holding_id} ({product_code})...")
            
            # 获取最新的产品数据
            if product_type == "stock":
                product_info = get_stock_data(product_code)
                if product_info:
                    new_price = product_info.get('current_price')
                    if new_price is not None:
                        # 更新持仓的当前价格
                        updated_holding = Holding.from_dict({
                            'id': holding_id,
                            'product_code': product_code,
                            'product_name': product_info.get('stock_name') or holding[2] or holding.product_name,
                            'product_type': product_type,
                            'quantity': holding[4] if isinstance(holding, tuple) else holding.quantity,
                            'purchase_price': holding[5] if isinstance(holding, tuple) else holding.purchase_price,
                            'current_price': new_price
                        })
                        update_holding(holding_id, updated_holding)
                        updated_count += 1
            
            elif product_type == "etf":
                from core.database import get_etf_by_code
                etf_info = get_etf_by_code(product_code)
                if etf_info:
                    new_price = etf_info.get('net_value')
                    if new_price is not None:
                        # 更新持仓的当前价格
                        updated_holding = Holding.from_dict({
                            'id': holding_id,
                            'product_code': product_code,
                            'product_name': etf_info.get('etf_name') or holding[2] or holding.product_name,
                            'product_type': product_type,
                            'quantity': holding[4] if isinstance(holding, tuple) else holding.quantity,
                            'purchase_price': holding[5] if isinstance(holding, tuple) else holding.purchase_price,
                            'current_price': new_price
                        })
                        update_holding(holding_id, updated_holding)
                        updated_count += 1
            
            elif product_type == "fund":
                from core.database import get_fund_by_code
                fund_info = get_fund_by_code(product_code)
                if fund_info:
                    new_price = fund_info.get('net_value')
                    if new_price is not None:
                        # 更新持仓的当前价格
                        updated_holding = Holding.from_dict({
                            'id': holding_id,
                            'product_code': product_code,
                            'product_name': fund_info.get('fund_name') or holding[2] or holding.product_name,
                            'product_type': product_type,
                            'quantity': holding[4] if isinstance(holding, tuple) else holding.quantity,
                            'purchase_price': holding[5] if isinstance(holding, tuple) else holding.purchase_price,
                            'current_price': new_price
                        })
                        update_holding(holding_id, updated_holding)
                        updated_count += 1
        
        print(f"\n{colorize('数据同步完成！', 'green')}")
        print(f"   成功更新 {updated_count}/{len(holdings)} 个持仓")
        
    except Exception as e:
        print(f"\n{colorize('❌ 同步数据失败:', 'red')} {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    # 确保数据库表已创建
    create_tables()
    
    while True:
        print_menu()
        choice = input("请选择操作: ").strip()
        
        if choice == "1":
            add_holding_cli()
        elif choice == "2":
            view_holdings_cli()
        elif choice == "3":
            update_holding_cli()
        elif choice == "4":
            delete_holding_cli()
        elif choice == "5":
            force_sync_holdings_cli()
        elif choice == "0":
            print("感谢使用持仓管理模块，再见！")
            break
        else:
            print("错误: 无效的选择，请重新输入！")
        
        # 操作完成后暂停
        input("\n按回车键继续...")

if __name__ == "__main__":
    main()