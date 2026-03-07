"""
真实数据服务实现

阶段1：基础实现
- 实现股票真实数据查询（简化版本：代码、名称、价格）
- 实现交易时间判断和缓存机制
- 提供强制刷新接口
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import logging

try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False

from ..models.enums import AssetType
from ..core.config import settings

logger = logging.getLogger(__name__)


class MarketDataService(ABC):
    """市场数据服务接口"""

    @abstractmethod
    def get_stock_info(self, code: str) -> Optional[Dict]:
        """获取股票信息"""
        pass

    @abstractmethod
    def get_lof_fund_info(self, code: str) -> Optional[Dict]:
        """获取LOF基金信息"""
        pass

    @abstractmethod
    def get_etf_fund_info(self, code: str) -> Optional[Dict]:
        """获取ETF基金信息"""
        pass

    @abstractmethod
    def get_open_fund_info(self, code: str) -> Optional[Dict]:
        """获取开放式基金信息"""
        pass

    @abstractmethod
    def get_market_data(self, code: str, asset_type: AssetType) -> Optional[Dict]:
        """获取市场数据"""
        pass

    @abstractmethod
    def get_all_lof_funds(self) -> List[Dict]:
        """获取所有LOF基金"""
        pass

    @abstractmethod
    def get_all_etf_funds(self) -> List[Dict]:
        """获取所有ETF基金"""
        pass

    @abstractmethod
    def get_all_open_funds(self) -> List[Dict]:
        """获取所有开放式基金"""
        pass

    @abstractmethod
    def get_asset_info(self, code: str) -> Optional[Dict]:
        """根据代码获取资产信息（自动识别类型）"""
        pass

    @abstractmethod
    def get_asset_type(self, code: str) -> Optional[AssetType]:
        """根据代码获取资产类型"""
        pass

    @abstractmethod
    def get_asset_name(self, code: str) -> Optional[str]:
        """根据代码获取资产名称"""
        pass

    @abstractmethod
    def force_refresh_asset(self, code: str, asset_type: AssetType) -> bool:
        """强制刷新资产数据"""
        pass


class TradingTimeHelper:
    """交易时间辅助类"""

    @staticmethod
    def is_trading_day(current_time: datetime) -> bool:
        """判断是否是交易日（简化实现）"""
        # 1. 周末不交易
        if current_time.weekday() >= 5:  # 周六周日
            return False

        # 2. 简化假设工作日都是交易日
        # TODO: 可以集成节假日API判断
        return True

    @staticmethod
    def is_trading_hours(current_time: datetime) -> bool:
        """判断当前时间是否在交易时间内"""
        # 1. 判断是否是交易日
        if not TradingTimeHelper.is_trading_day(current_time):
            return False

        # 2. 判断是否在交易时段内 (9:30-15:00)
        trading_start = current_time.replace(hour=9, minute=30, second=0, microsecond=0)
        trading_end = current_time.replace(hour=15, minute=0, second=0, microsecond=0)

        return trading_start <= current_time <= trading_end

    @staticmethod
    def is_data_fresh(last_update: datetime, current_time: datetime, threshold_minutes: int = 30) -> bool:
        """判断数据是否足够新鲜"""
        time_diff = current_time - last_update
        return time_diff < timedelta(minutes=threshold_minutes)


class AssetCache:
    """资产缓存服务"""

    def __init__(self):
        self.cache = {}  # 格式: {code: {data, timestamp, expiry}}
        self.default_ttl = 3600  # 默认1小时

    def get(self, code: str) -> Optional[Dict]:
        """获取缓存数据"""
        entry = self.cache.get(code)
        if not entry:
            return None

        # 检查是否过期
        if datetime.now() > entry.get('expiry', datetime.min):
            return None

        return entry.get('data')

    def set(self, code: str, data: Dict, ttl: int = None) -> None:
        """设置缓存数据"""
        ttl = ttl or self.default_ttl
        expiry = datetime.now() + timedelta(seconds=ttl)

        self.cache[code] = {
            'data': data,
            'timestamp': datetime.now(),
            'expiry': expiry
        }

    def delete(self, code: str) -> bool:
        """删除缓存数据"""
        if code in self.cache:
            del self.cache[code]
            return True
        return False

    def clear(self) -> None:
        """清空所有缓存"""
        self.cache.clear()

    def get_info(self) -> Dict:
        """获取缓存统计信息"""
        total = len(self.cache)
        valid = sum(1 for entry in self.cache.values()
                   if datetime.now() <= entry.get('expiry', datetime.min))
        expired = total - valid

        return {
            'total_entries': total,
            'valid_entries': valid,
            'expired_entries': expired
        }


class RealMarketDataService(MarketDataService):
    """真实市场数据服务实现 - 阶段1"""

    def __init__(self):
        self.cache = AssetCache()
        self.trading_helper = TradingTimeHelper()

    def get_stock_info(self, code: str) -> Optional[Dict]:
        """获取股票信息（简化版：代码、名称、价格）"""
        if not AKSHARE_AVAILABLE:
            logger.warning("Akshare不可用，无法获取真实数据")
            return None

        try:
            # 1. 调用akshare API
            stock_info = ak.stock_individual_info_em(symbol=code)

            # 2. 检查数据是否为空
            if stock_info.empty:
                logger.warning(f"股票代码 {code} 未找到数据")
                return None

            # 3. 将DataFrame转换为字典
            info_dict = dict(zip(stock_info['item'], stock_info['value']))

            # 4. 提取需要的三个字段
            return {
                "code": info_dict.get("股票代码", code),
                "name": info_dict.get("股票简称"),
                "price": float(info_dict.get("最新", 0)),
                "type": AssetType.STOCK,
                "timestamp": datetime.now()
            }

        except Exception as e:
            logger.error(f"获取股票 {code} 信息失败: {e}")
            return None

    def get_lof_fund_info(self, code: str) -> Optional[Dict]:
        """获取LOF基金信息（待实现）"""
        raise NotImplementedError("LOF基金真实数据获取待实现")

    def get_etf_fund_info(self, code: str) -> Optional[Dict]:
        """获取ETF基金信息（待实现）"""
        raise NotImplementedError("ETF基金真实数据获取待实现")

    def get_open_fund_info(self, code: str) -> Optional[Dict]:
        """获取开放式基金信息（待实现）"""
        raise NotImplementedError("开放式基金真实数据获取待实现")

    def get_market_data(self, code: str, asset_type: AssetType) -> Optional[Dict]:
        """
        获取市场数据（智能决策）
        根据交易时间和缓存情况决定是否调用API
        """
        if asset_type != AssetType.STOCK:
            raise NotImplementedError(f"资产类型 {asset_type} 的真实数据获取待实现")

        current_time = datetime.now()

        # 1. 检查缓存
        cached_data = self.cache.get(code)
        if cached_data:
            # 判断数据是否新鲜
            if self.trading_helper.is_data_fresh(
                cached_data.get('timestamp', datetime.min),
                current_time
            ):
                logger.info(f"使用缓存数据: {code}")
                return self._build_market_data(cached_data.get('data'))

        # 2. 判断是否在交易时间内
        if self.trading_helper.is_trading_hours(current_time):
            logger.info(f"交易时间需要刷新: {code}")
            return self._fetch_and_cache_data(code, asset_type)

        # 3. 判断数据是否过期
        if not cached_data or not self.trading_helper.is_data_fresh(
            cached_data.get('timestamp', datetime.min),
            current_time,
            threshold_minutes=240  # 4小时过期
        ):
            logger.info(f"数据过期需要刷新: {code}")
            return self._fetch_and_cache_data(code, asset_type)

        # 4. 使用缓存数据
        logger.info(f"使用缓存数据: {code}")
        return self._build_market_data(cached_data.get('data'))

    def _fetch_and_cache_data(self, code: str, asset_type: AssetType) -> Optional[Dict]:
        """从API获取数据并缓存"""
        # 调用get_stock_info获取真实数据
        stock_info = self.get_stock_info(code)
        if not stock_info:
            return None

        # 缓存数据
        self.cache.set(code, stock_info)

        # 构建市场数据格式
        return self._build_market_data(stock_info)

    def _build_market_data(self, stock_info: Dict) -> Dict:
        """构建标准市场数据格式"""
        price = stock_info.get("price", 0)

        return {
            "name": stock_info.get("name"),
            "code": stock_info.get("code"),
            "price": price,
            "type": stock_info.get("type"),

            # 补充其他字段（使用默认值）
            "change_amount": 0.0,
            "change_percent": 0.0,
            "volume": 0,
            "turnover": 0,
            "open_price": price,
            "high_price": price,
            "low_price": price,
            "prev_close": price,
            "turnover_rate": 0.0,
            "circulating_market_cap": 0.0,
            "total_market_cap": 0.0,
        }

    def get_all_lof_funds(self) -> List[Dict]:
        """获取所有LOF基金列表（待实现）"""
        raise NotImplementedError("LOF基金列表获取待实现")

    def get_all_etf_funds(self) -> List[Dict]:
        """获取所有ETF基金列表（待实现）"""
        raise NotImplementedError("ETF基金列表获取待实现")

    def get_all_open_funds(self) -> List[Dict]:
        """获取所有开放式基金列表（待实现）"""
        raise NotImplementedError("开放式基金列表获取待实现")

    def get_asset_info(self, code: str) -> Optional[Dict]:
        """根据代码获取资产信息（自动识别类型）"""
        # 当前只实现股票类型
        stock_info = self.get_stock_info(code)
        if stock_info:
            return stock_info
        return None

    def get_asset_type(self, code: str) -> Optional[AssetType]:
        """根据代码判断资产类型"""
        # 当前只支持股票
        stock_info = self.get_stock_info(code)
        if stock_info:
            return AssetType.STOCK
        return None

    def get_asset_name(self, code: str) -> Optional[str]:
        """根据代码获取资产名称"""
        stock_info = self.get_stock_info(code)
        return stock_info.get("name") if stock_info else None

    def force_refresh_asset(self, code: str, asset_type: AssetType) -> bool:
        """强制刷新资产数据"""
        try:
            # 清除缓存
            self.cache.delete(code)

            # 重新获取数据
            if asset_type == AssetType.STOCK:
                stock_info = self.get_stock_info(code)
                if stock_info:
                    self.cache.set(code, stock_info)
                    logger.info(f"强制刷新成功: {code}")
                    return True
            else:
                logger.warning(f"资产类型 {asset_type} 强制刷新待实现")
                return False

        except Exception as e:
            logger.error(f"强制刷新失败: {code}, 错误: {e}")
            return False


# 创建真实数据服务实例
real_data_service = RealMarketDataService() if AKSHARE_AVAILABLE else None
