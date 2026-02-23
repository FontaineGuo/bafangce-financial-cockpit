"""
Mock数据服务 - 用于替代akshare API调用

注：本系统不设置独立的BOND资产类型。债券通过基金持有。
示例中的"华夏纯债债券A"是开放式债券基金（OPEN_FUND类型），
而非独立的债券资产。
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random

from ..models.enums import AssetType, StrategyCategory


class MockDataService:
    """Mock数据服务"""

    # Mock资产数据
    MOCK_ASSETS = {
        # 股票
        "000001": {
            "code": "000001",
            "name": "平安银行",
            "type": AssetType.STOCK,
            "price": 12.35,
            "change_amount": 0.15,
            "change_percent": 1.23,
        },
        "000002": {
            "code": "000002",
            "name": "万科A",
            "type": AssetType.STOCK,
            "price": 8.56,
            "change_amount": -0.08,
            "change_percent": -0.93,
        },
        # LOF基金
        "501018": {
            "code": "501018",
            "name": "南方原油LOF",
            "type": AssetType.LOF_FUND,
            "price": 1.314,
            "change_amount": 0.046,
            "change_percent": 3.63,
            "volume": 2926603.0,
            "turnover": 385592522.0,
        },
        "161226": {
            "code": "161226",
            "name": "国投白银",
            "type": AssetType.LOF_FUND,
            "price": 0.856,
            "change_amount": 0.023,
            "change_percent": 2.76,
        },
        # ETF基金
        "510300": {
            "code": "510300",
            "name": "沪深300ETF",
            "type": AssetType.ETF_FUND,
            "price": 4.125,
            "change_amount": 0.035,
            "change_percent": 0.85,
        },
        "513880": {
            "code": "513880",
            "name": "华安日经225ETF",
            "type": AssetType.ETF_FUND,
            "price": 1.8002,
            "change_amount": 0.0597,
            "change_percent": 3.43,
        },
        "159981": {
            "code": "159981",
            "name": "能源化工ETF",
            "type": AssetType.ETF_FUND,
            "price": 1.025,
            "change_amount": 0.018,
            "change_percent": 1.79,
        },
        "518880": {
            "code": "518880",
            "name": "华安黄金ETF",
            "type": AssetType.ETF_FUND,
            "price": 5.256,
            "change_amount": 0.089,
            "change_percent": 1.72,
        },
        "159985": {
            "code": "159985",
            "name": "豆粕ETF",
            "type": AssetType.ETF_FUND,
            "price": 1.985,
            "change_amount": 0.032,
            "change_percent": 1.64,
        },
        # 开放式基金
        "021539": {
            "code": "021539",
            "name": "中证红利",
            "type": AssetType.OPEN_FUND,
            "price": 1.0234,
            "change_amount": 0.0012,
            "change_percent": 0.12,
            "unit_net_value": 1.0234,
            "accumulated_net_value": 1.0234,
        },
        "007280": {
            "code": "007280",
            "name": "招商中证白酒",
            "type": AssetType.OPEN_FUND,
            "price": 1.2456,
            "change_amount": -0.0089,
            "change_percent": -0.71,
        },
        # 债券基金（通过基金持有债券）
        "007021": {
            "code": "007021",
            "name": "华夏纯债债券A",
            "type": AssetType.OPEN_FUND,
            "price": 1.1056,
            "change_amount": 0.0003,
            "change_percent": 0.03,
            "unit_net_value": 1.1056,
            "accumulated_net_value": 1.4856,
        },
    }

    @classmethod
    def get_stock_info(cls, code: str) -> Optional[Dict]:
        """获取股票信息"""
        if code in cls.MOCK_ASSETS:
            return cls.MOCK_ASSETS[code].copy()
        return None

    @classmethod
    def get_lof_fund_info(cls, code: str) -> Optional[Dict]:
        """获取LOF基金信息"""
        if code in cls.MOCK_ASSETS:
            asset = cls.MOCK_ASSETS[code]
            if asset["type"] == AssetType.LOF_FUND:
                return asset.copy()
        return None

    @classmethod
    def get_etf_fund_info(cls, code: str) -> Optional[Dict]:
        """获取ETF基金信息"""
        if code in cls.MOCK_ASSETS:
            asset = cls.MOCK_ASSETS[code]
            if asset["type"] == AssetType.ETF_FUND:
                return asset.copy()
        return None

    @classmethod
    def get_open_fund_info(cls, code: str) -> Optional[Dict]:
        """获取开放式基金信息"""
        if code in cls.MOCK_ASSETS:
            asset = cls.MOCK_ASSETS[code]
            if asset["type"] == AssetType.OPEN_FUND:
                return asset.copy()
        return None

    @classmethod
    def get_market_data(cls, code: str, asset_type: AssetType) -> Optional[Dict]:
        """
        获取市场数据

        返回的数据包含资产名称，以便在创建资产时如果未提供名称可以自动填充
        """
        asset = cls.MOCK_ASSETS.get(code)
        if asset and asset["type"] == asset_type:
            base_price = asset["price"]
            # 模拟价格波动
            price_change = random.uniform(-0.01, 0.01) * base_price
            new_price = base_price + price_change

            return {
                "name": asset.get("name"),  # 包含资产名称
                "price": round(new_price, 4),
                "change_amount": round(price_change, 4),
                "change_percent": round((price_change / base_price) * 100, 2),
                "volume": asset.get("volume"),
                "turnover": asset.get("turnover"),
                "open_price": round(new_price * random.uniform(0.98, 1.0), 4),
                "high_price": round(new_price * random.uniform(1.0, 1.02), 4),
                "low_price": round(new_price * random.uniform(0.98, 1.0), 4),
                "prev_close": round(base_price, 4),
                "turnover_rate": random.uniform(0.1, 10),
                "circulating_market_cap": random.uniform(100000000, 10000000000),
                "total_market_cap": random.uniform(100000000, 10000000000),
                "unit_net_value": asset.get("unit_net_value"),
                "accumulated_net_value": asset.get("accumulated_net_value"),
                "discount_rate": random.uniform(-5, 5),
            }
        return None

    @classmethod
    def get_all_lof_funds(cls) -> List[Dict]:
        """获取所有LOF基金"""
        return [
            {**data, "updated_at": datetime.now()}
            for code, data in cls.MOCK_ASSETS.items()
            if data["type"] == AssetType.LOF_FUND
        ]

    @classmethod
    def get_all_etf_funds(cls) -> List[Dict]:
        """获取所有ETF基金"""
        return [
            {**data, "updated_at": datetime.now()}
            for code, data in cls.MOCK_ASSETS.items()
            if data["type"] == AssetType.ETF_FUND
        ]

    @classmethod
    def get_all_open_funds(cls) -> List[Dict]:
        """获取所有开放式基金"""
        return [
            {**data, "updated_at": datetime.now()}
            for code, data in cls.MOCK_ASSETS.items()
            if data["type"] == AssetType.OPEN_FUND
        ]

    @classmethod
    def get_asset_info(cls, code: str) -> Optional[Dict]:
        """根据代码获取资产信息（自动识别类型）"""
        for asset_data in cls.MOCK_ASSETS.values():
            if asset_data["code"] == code:
                return asset_data.copy()
        return None

    @classmethod
    def get_asset_type(cls, code: str) -> Optional[AssetType]:
        """根据代码获取资产类型"""
        asset = cls.MOCK_ASSETS.get(code)
        return asset["type"] if asset else None

    @classmethod
    def get_asset_name(cls, code: str) -> Optional[str]:
        """根据代码获取资产名称"""
        asset = cls.MOCK_ASSETS.get(code)
        return asset["name"] if asset else None


mock_data_service = MockDataService()
