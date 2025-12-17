#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PortfolioManager 单元测试
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.portfolio import PortfolioManager
from backend.models.holding import Holding

class TestPortfolioManager(unittest.TestCase):
    """PortfolioManager类的单元测试"""
    
    def setUp(self):
        """测试前置设置"""
        self.portfolio_manager = PortfolioManager()
        
    def tearDown(self):
        """测试后置清理"""
        pass
    
    @patch('backend.core.portfolio.db_get_all_holdings')
    def test_get_all_holdings(self, mock_db_get_all):
        """测试获取所有持仓"""
        # 模拟数据库返回
        mock_db_get_all.return_value = [
            (1, '000001', '平安银行', 'stock', 'china_stock_etf', 100, 10.0, 11.0, '2023-01-01'),
            (2, '000002', '万科A', 'stock', 'china_stock_etf', 50, 20.0, 22.0, '2023-01-02')
        ]
        
        holdings = self.portfolio_manager.get_all_holdings()
        
        # 验证结果
        self.assertEqual(len(holdings), 2)
        self.assertIsInstance(holdings[0], Holding)
        self.assertEqual(holdings[0].product_code, '000001')
        self.assertEqual(holdings[1].product_code, '000002')
    
    @patch('backend.core.portfolio.get_realtime_data')
    @patch('backend.core.portfolio.db_add_holding')
    def test_add_holding(self, mock_db_add, mock_get_realtime):
        """测试添加持仓"""
        # 模拟实时数据返回
        mock_get_realtime.return_value = ('stock', {'current_price': 11.0})
        
        # 模拟数据库添加返回
        mock_db_add.return_value = 1
        
        # 测试数据
        holding_data = {
            'product_code': '000001',
            'product_name': '平安银行',
            'product_type': 'stock',
            'quantity': 100,
            'purchase_price': 10.0
        }
        
        success, result = self.portfolio_manager.add_holding(holding_data)
        
        # 验证结果
        self.assertTrue(success)
        self.assertEqual(result['message'], '持仓添加成功')
        self.assertEqual(result['holding_id'], 1)
        self.assertEqual(result['category'], '其他')
    
    @patch('backend.core.portfolio.db_update_holding')
    @patch('backend.core.portfolio.db_get_all_holdings')
    def test_update_holding(self, mock_db_get_all, mock_db_update):
        """测试更新持仓"""
        # 模拟数据库返回
        mock_db_get_all.return_value = [
            (1, '000001', '平安银行', 'stock', 'china_stock_etf', 100, 10.0, 11.0, '2023-01-01')
        ]
        
        # 模拟数据库更新返回
        mock_db_update.return_value = True
        
        # 测试数据
        update_data = {
            'quantity': 200,
            'purchase_price': 10.5
        }
        
        success, result = self.portfolio_manager.update_holding(1, update_data)
        
        # 验证结果
        self.assertTrue(success)
        self.assertEqual(result['message'], '持仓更新成功')
    
    @patch('backend.core.portfolio.db_delete_holding')
    def test_delete_holding(self, mock_db_delete):
        """测试删除持仓"""
        # 模拟数据库删除返回
        mock_db_delete.return_value = True
        
        success, message = self.portfolio_manager.delete_holding(1)
        
        # 验证结果
        self.assertTrue(success)
        self.assertEqual(message, '持仓删除成功')
    
    @patch('backend.core.portfolio.db_get_all_holdings')
    def test_calculate_asset_allocation(self, mock_db_get_all):
        """测试计算资产配置"""
        # 模拟数据库返回
        mock_db_get_all.return_value = [
            (1, '000001', '平安银行', 'stock', 'china_stock_etf', 100, 10.0, 11.0, '2023-01-01'),
            (2, '000002', '万科A', 'stock', 'china_stock_etf', 50, 20.0, 22.0, '2023-01-02')
        ]
        
        allocation = self.portfolio_manager.calculate_asset_allocation()
        
        # 验证结果
        self.assertEqual(allocation['total_value'], 2200.0)  # 100*11 + 50*22 = 1100 + 1100 = 2200
        self.assertIn('china_stock_etf', allocation['categories'])
        self.assertEqual(allocation['categories']['china_stock_etf']['market_value'], 2200.0)
    
    @patch('backend.core.portfolio.db_get_all_holdings')
    def test_search_holdings(self, mock_db_get_all):
        """测试搜索持仓"""
        # 模拟数据库返回
        mock_db_get_all.return_value = [
            (1, '000001', '平安银行', 'stock', 'china_stock_etf', 100, 10.0, 11.0, '2023-01-01'),
            (2, '000002', '万科A', 'stock', 'china_stock_etf', 50, 20.0, 22.0, '2023-01-02')
        ]
        
        # 搜索"平安"
        results = self.portfolio_manager.search_holdings('平安')
        
        # 验证结果
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].product_name, '平安银行')

if __name__ == '__main__':
    unittest.main()
