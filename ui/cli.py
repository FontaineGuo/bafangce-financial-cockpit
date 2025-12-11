# 命令行式持仓添加模块
import sys
import os

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.holdings_manager import add_holding
from core.data_fetcher import get_stock_data, get_fund_data
from models.holding import Holding
from core.database import create_tables

def print_menu():
    """打印菜单"""
    print("=" * 50)
    print("        持仓添加模块")
    print("=" * 50)
    print("1. 添加股票持仓")
    print("2. 添加基金持仓")
    print("0. 退出")
    print("=" * 50)

def get_product_info(product_type, product_code):
    """
    获取产品信息
    
    Args:
        product_type (str): 产品类型 (stock/fund)
        product_code (str): 产品代码
    
    Returns:
        dict: 产品信息
    """
    if product_type == "stock":
        return get_stock_data(product_code)
    elif product_type == "fund":
        return get_fund_data(product_code)
    else:
        return None

def add_holding_cli(product_type):
    """
    添加持仓的命令行界面
    
    Args:
        product_type (str): 产品类型 (stock/fund)
    """
    product_type_name = "股票" if product_type == "stock" else "基金"
    
    print(f"\n=== 添加{product_type_name}持仓 ===")
    
    # 获取产品代码
    while True:
        product_code = input(f"请输入{product_type_name}代码: ").strip()
        if not product_code:
            print("错误: 代码不能为空!")
            continue
        
        # 获取产品信息
        print(f"正在获取{product_type_name}信息...")
        product_info = get_product_info(product_type, product_code)
        
        if product_info:
            # 显示产品信息
            if product_type == "stock":
                print(f"\n{product_type_name}信息:")
                print(f"代码: {product_info['stock_code']}")
                print(f"名称: {product_info['stock_name']}")
                print(f"当前价格: {product_info['current_price']}")
                product_name = product_info['stock_name']
                current_price = product_info['current_price']
            else:
                print(f"\n{product_type_name}信息:")
                print(f"代码: {product_info['fund_code']}")
                print(f"名称: {product_info['fund_name']}")
                print(f"当前价格: {product_info['net_value']}")
                product_name = product_info['fund_name']
                current_price = product_info['net_value']
            
            break
        else:
            print(f"错误: 无法获取{product_type_name}信息，请检查代码是否正确!")
    
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

def main():
    """主函数"""
    # 确保数据库表已创建
    create_tables()
    
    while True:
        print_menu()
        choice = input("请选择操作: ").strip()
        
        if choice == "1":
            add_holding_cli("stock")
        elif choice == "2":
            add_holding_cli("fund")
        elif choice == "0":
            print("感谢使用持仓添加模块，再见！")
            break
        else:
            print("错误: 无效的选择，请重新输入！")
        
        # 操作完成后暂停
        input("\n按回车键继续...")

if __name__ == "__main__":
    main()