#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML表格导出工具
用于将持仓数据导出为HTML格式的表格文件
"""

import datetime
import os


class HtmlExporter:
    """
    HTML表格导出类
    用于将持仓数据导出为美观的HTML表格
    """
    
    def __init__(self):
        """初始化HTML导出器"""
        self.css_style = """        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                text-align: center;
                color: #333;
                margin-bottom: 30px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 30px;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 12px;
                text-align: right;
            }
            th {
                background-color: #f2f2f2;
                font-weight: bold;
                color: #333;
                text-align: center;
            }
            th:first-child, td:first-child {
                text-align: center;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            tr:hover {
                background-color: #f5f5f5;
            }
            .profit {
                color: #2ecc71;
                font-weight: bold;
            }
            .loss {
                color: #e74c3c;
                font-weight: bold;
            }
            .summary {
                background-color: #e8f4f8;
                font-weight: bold;
            }
            .stats {
                background-color: #f0f4c3;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
            }
            .stats p {
                margin: 5px 0;
                font-size: 14px;
            }
            .footer {
                text-align: center;
                color: #666;
                font-size: 12px;
                margin-top: 30px;
            }
        </style>"""
    
    def generate_html_table(self, holdings, total_cost, total_current, total_profit, total_profit_rate, 
                          stock_count, etf_count, fund_count):
        """
        生成HTML表格内容
        
        Args:
            holdings (list): 持仓数据列表
            total_cost (float): 总成本
            total_current (float): 总市值
            total_profit (float): 总盈亏
            total_profit_rate (float): 总盈利率
            stock_count (int): 股票数量
            etf_count (int): ETF数量
            fund_count (int): 基金数量
            
        Returns:
            str: 完整的HTML内容
        """
        # 构建HTML头部
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>持仓报表</title>
{self.css_style}
</head>
<body>
    <div class="container">
        <h1>持仓报表</h1>
        
        <div class="stats">
            <p>统计信息：</p>
            <p>总持仓数量: {len(holdings)}  股票: {stock_count}  ETF: {etf_count}  基金: {fund_count}</p>
            <p>总成本: {total_cost:.2f}  总市值: {total_current:.2f}  总盈亏: {total_profit:.2f}  总盈利率: {total_profit_rate:.2f}%</p>
            <p>生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>类型</th>
                    <th>代码</th>
                    <th>名称</th>
                    <th>份额</th>
                    <th>成本价</th>
                    <th>当前价</th>
                    <th>成本总额</th>
                    <th>当前总额</th>
                    <th>盈亏额</th>
                    <th>盈亏率</th>
                </tr>
            </thead>
            <tbody>"""
        
        # 添加数据行
        for holding in holdings:
            # 确定产品类型
            if holding.product_type == "stock":
                product_type_str = "股票"
            elif holding.product_type == "etf":
                product_type_str = "ETF"
            else:
                product_type_str = "基金"
            
            # 安全处理可能的None值
            safe_id = holding.id or 0
            safe_code = holding.product_code or ""
            safe_name = holding.product_name or ""
            safe_quantity = holding.quantity if holding.quantity is not None else 0.0
            safe_purchase_price = holding.purchase_price if holding.purchase_price is not None else 0.0
            safe_current_price = holding.current_price if holding.current_price is not None else 0.0
            safe_cost_total = holding.cost_total if holding.cost_total is not None else 0.0
            safe_current_total = holding.current_total if holding.current_total is not None else 0.0
            safe_profit_total = holding.profit_total if holding.profit_total is not None else 0.0
            profit_rate = holding.profit_rate * 100 if holding.profit_rate is not None else 0.0
            
            # 确定盈亏类
            profit_class = "profit" if safe_profit_total >= 0 else "loss"
            
            # 添加行
            html_content += f"""
                <tr>
                    <td>{safe_id}</td>
                    <td>{product_type_str}</td>
                    <td>{safe_code}</td>
                    <td>{safe_name}</td>
                    <td>{safe_quantity:.2f}</td>
                    <td>{safe_purchase_price:.4f}</td>
                    <td>{safe_current_price:.4f}</td>
                    <td>{safe_cost_total:.2f}</td>
                    <td>{safe_current_total:.2f}</td>
                    <td class="{profit_class}">{safe_profit_total:.2f}</td>
                    <td class="{profit_class}">{profit_rate:.2f}%</td>
                </tr>"""
        
        # 添加总计行
        total_profit_class = "profit" if total_profit >= 0 else "loss"
        html_content += f"""
                <tr class="summary">
                    <td>总计</td>
                    <td colspan="6"></td>
                    <td>{total_cost:.2f}</td>
                    <td>{total_current:.2f}</td>
                    <td class="{total_profit_class}">{total_profit:.2f}</td>
                    <td class="{total_profit_class}">{total_profit_rate:.2f}%</td>
                </tr>
            </tbody>
        </table>
        
        <div class="footer">
            <p>持仓报表 - 自动生成</p>
        </div>
    </div>
</body>
</html>"""
        
        return html_content
    
    def export_to_file(self, html_content, output_dir=None, filename=None):
        """
        将HTML内容导出到文件
        
        Args:
            html_content (str): HTML内容
            output_dir (str, optional): 输出目录，默认为当前目录
            filename (str, optional): 文件名，默认为自动生成
            
        Returns:
            str: 导出的文件路径
        """
        if output_dir is None:
            output_dir = os.getcwd()
        
        if filename is None:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"holdings_report_{timestamp}.html"
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 完整文件路径
        file_path = os.path.join(output_dir, filename)
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return file_path
    
    def export_holdings(self, holdings, total_cost, total_current, total_profit, total_profit_rate, 
                      stock_count, etf_count, fund_count, output_dir=None, filename=None):
        """
        导出持仓数据为HTML文件
        
        Args:
            holdings (list): 持仓数据列表
            total_cost (float): 总成本
            total_current (float): 总市值
            total_profit (float): 总盈亏
            total_profit_rate (float): 总盈利率
            stock_count (int): 股票数量
            etf_count (int): ETF数量
            fund_count (int): 基金数量
            output_dir (str, optional): 输出目录
            filename (str, optional): 文件名
            
        Returns:
            str: 导出的文件路径
        """
        # 生成HTML内容
        html_content = self.generate_html_table(
            holdings, total_cost, total_current, total_profit, total_profit_rate,
            stock_count, etf_count, fund_count
        )
        
        # 导出到文件
        return self.export_to_file(html_content, output_dir, filename)
    
    def generate_asset_allocation_html(self, report):
        """
        生成资产配置报告的HTML内容
        
        Args:
            report (dict): 资产配置报告数据
            
        Returns:
            str: 完整的资产配置报告HTML内容
        """
        # 构建HTML头部
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>资产配置报告</title>
{self.css_style}
</head>
<body>
    <div class="container">
        <h1>资产配置报告</h1>
        
        <div class="stats">
            <p>统计信息：</p>
            <p>总市值: {report['current_allocation']['total_value']:.2f} 元</p>
            <p>总持仓数量: {report['total_holding_count']}</p>
            <p>生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <h2>当前资产配置与目标配置对比</h2>
        <table>
            <thead>
                <tr>
                    <th>类别</th>
                    <th>当前市值</th>
                    <th>当前占比</th>
                    <th>持仓数量</th>
                    <th>目标比例</th>
                    <th>最大偏离</th>
                </tr>
            </thead>
            <tbody>"""
        
        # 获取所有类别
        categories = report['current_allocation']['categories']
        strategy = report['strategy']
        all_categories = sorted(set(categories.keys()).union(set(strategy.keys())))
        
        # 添加数据行
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
            
            html_content += f"""
                <tr>
                    <td>{category}</td>
                    <td>{value:.2f}</td>
                    <td>{current_ratio:.2%}</td>
                    <td>{count}</td>
                    <td>{target_ratio:.2%}</td>
                    <td>{max_deviation:.2%}</td>
                </tr>"""
        
        html_content += f"""
            </tbody>
        </table>"""
        
        # 添加偏离预警（如果有的话）
        warnings = report['warnings']
        if warnings:
            html_content += f"""
        <h2>配置偏离预警</h2>
        <table>
            <thead>
                <tr>
                    <th>类别</th>
                    <th>当前比例</th>
                    <th>目标比例</th>
                    <th>偏离值</th>
                    <th>状态</th>
                </tr>
            </thead>
            <tbody>"""
            
            for warning in warnings:
                category = warning['category']
                current_ratio = warning['current_ratio']
                target_ratio = warning['target_ratio']
                deviation = warning['deviation']
                status = '超配' if warning['status'] == 'over' else '低配'
                
                # 超配用红色，低配用黄色
                status_class = 'loss' if warning['status'] == 'over' else 'profit'
                
                html_content += f"""
                <tr>
                    <td>{category}</td>
                    <td>{current_ratio:.2%}</td>
                    <td>{target_ratio:.2%}</td>
                    <td>{deviation:.2%}</td>
                    <td class="{status_class}">{status} ⚠</td>
                </tr>"""
            
            html_content += f"""
            </tbody>
        </table>"""
        
            # 添加调整建议
            html_content += f"""
        <h2>调整建议</h2>
        <ul>"""
            
            # 生成调整建议
            from core.asset_allocation import AssetAllocationMonitor
            suggestions = AssetAllocationMonitor().get_allocation_suggestions(warnings)
            for suggestion in suggestions:
                html_content += f"""
            <li>{suggestion['suggestion']}</li>"""
            
            html_content += f"""
        </ul>"""
        else:
            html_content += f"""
        <div class="stats">
            <p>✅ 资产配置符合目标比例，无需调整</p>
        </div>"""
        
        html_content += f"""
        <div class="footer">
            <p>资产配置报告 - 自动生成</p>
        </div>
    </div>
</body>
</html>"""
        
        return html_content
    
    def export_asset_allocation(self, report, output_dir=None, filename=None):
        """
        导出资产配置报告为HTML文件
        
        Args:
            report (dict): 资产配置报告数据
            output_dir (str, optional): 输出目录
            filename (str, optional): 文件名
            
        Returns:
            str: 导出的文件路径
        """
        # 生成HTML内容
        html_content = self.generate_asset_allocation_html(report)
        
        # 导出到文件
        if filename is None:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"asset_allocation_report_{timestamp}.html"
        
        return self.export_to_file(html_content, output_dir, filename)
