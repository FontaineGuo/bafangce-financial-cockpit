"""
真实数据服务实现

阶段1：基础实现
- 实现股票真实数据查询（简化版本：代码、名称、价格）
- 实现ETF真实数据查询（带净值有效性验证和时间感知）
- 实现交易时间判断和缓存机制
- 提供强制刷新接口
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import logging
import re

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

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

    @staticmethod
    def get_current_trading_date() -> str:
        """获取当前交易日期"""
        from datetime import datetime as dt
        current = dt.now()

        # 简化逻辑：周末和节假日不是交易日
        if current.weekday() >= 5:  # 周六周日
            # 回到上一个工作日
            return (current - timedelta(days=current.weekday() - 5)).strftime('%Y-%m-%d')
        else:
            return current.strftime('%Y-%m-%d')

    @staticmethod
    def get_previous_trading_date(current_date: str, days_back: int = 1) -> str:
        """获取上一个交易日"""
        from datetime import datetime as dt
        date = dt.strptime(current_date, '%Y-%m-%d')
        return (date - timedelta(days=days_back)).strftime('%Y-%m-%d')

    @staticmethod
    def should_fetch_latest_data(current_time: datetime) -> bool:
        """判断是否应该获取最新数据"""
        current_hour = current_time.hour

        # 交易时间内，每小时获取一次
        if TradingTimeHelper.is_trading_hours(current_time):
            return current_hour in [8, 9, 10, 11, 12, 13, 14, 15]
        else:
            return False

    @staticmethod
    def format_date_display(date_str: str) -> str:
        """格式化日期显示"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%Y年%m月%d日')
        except ValueError:
            return date_str


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

        # 不再硬编码净值字段，改为动态解析所有日期格式的净值字段

        # LOF缓存配置
        self.lof_cache_key = "lof_all_data"  # 全局LOF数据缓存键
        self.lof_cache_ttl = 1800  # 30分钟（秒）

        # 开放式基金缓存配置
        self.open_fund_cache_key = "open_fund_all_data"  # 全局开放式基金数据缓存键
        self.open_fund_cache_ttl = 3600  # 1小时（秒）

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
        """
        获取LOF基金信息（带全局缓存机制）
        重点：避免多次API调用，一次获取全量数据服务所有查询
        """
        if not AKSHARE_AVAILABLE:
            logger.warning("Akshare不可用，无法获取真实数据")
            return None

        if not PANDAS_AVAILABLE:
            logger.warning("Pandas不可用，无法处理LOF数据")
            return None

        try:
            # 1. 获取全量LOF数据（带缓存）
            all_lof_data = self._get_all_lof_data_with_cache()

            if all_lof_data is None or all_lof_data.empty:
                logger.warning("LOF数据为空")
                return None

            # 2. 从全量数据中筛选目标代码
            found_lof = None
            for idx in range(len(all_lof_data)):
                lof_row = all_lof_data.iloc[idx]
                lof_code = str(lof_row['代码']) if pd.notna(lof_row['代码']) else None

                if lof_code == code:
                    # 将找到的LOF数据转换为字典
                    lof_dict = {}
                    for col in all_lof_data.columns:
                        value = lof_row[col]
                        if pd.notna(value):
                            lof_dict[col] = value
                        else:
                            lof_dict[col] = None

                    found_lof = lof_dict
                    logger.info(f"找到LOF基金 {code}: {lof_dict.get('名称')}")
                    break

                if found_lof:
                    break

            if not found_lof:
                logger.warning(f"LOF基金代码 {code} 未在数据中找到")
                return None

            # 3. 数据验证
            validation = self._validate_lof_data(found_lof, code)
            if not validation['valid']:
                logger.warning(f"LOF基金 {code} 数据验证失败: {validation['issues']}")
                return None

            # 4. 提取和转换数据
            lof_info = self._extract_lof_info(found_lof, code)

            return lof_info

        except Exception as e:
            logger.error(f"获取LOF基金 {code} 数据失败: {e}")
            return None

    def get_etf_fund_info(self, code: str) -> Optional[Dict]:
        """
        获取ETF基金信息（带净值有效性验证和时间感知）
        重点：获取最近一个交易日的有效净值，而不是固定字段顺序
        """
        if not AKSHARE_AVAILABLE:
            logger.warning("Akshare不可用，无法获取真实数据")
            return None

        if not PANDAS_AVAILABLE:
            logger.warning("Pandas不可用，无法处理ETF数据")
            return None

        try:
            # 1. 获取当前交易日期
            current_trading_date = self.trading_helper.get_current_trading_date()
            logger.info(f"当前交易日期: {current_trading_date}")

            # 2. 调用akshare API（无参数，获取所有ETF数据）
            all_etf_data = ak.fund_etf_fund_daily_em()

            # 3. 检查数据是否为空
            if all_etf_data.empty:
                logger.warning("ETF数据为空")
                return None

            # 4. 从全量数据中筛选对应代码
            found_etf = None
            for idx in range(len(all_etf_data)):
                etf_row = all_etf_data.iloc[idx]
                etf_code = str(etf_row['基金代码']) if pd.notna(etf_row['基金代码']) else None

                if etf_code == code:
                    # 将找到的ETF数据转换为字典
                    etf_dict = {}
                    for col in all_etf_data.columns:
                        value = etf_row[col]
                        if pd.notna(value):
                            etf_dict[col] = value
                        else:
                            etf_dict[col] = None

                    found_etf = etf_dict
                    logger.info(f"找到ETF {code}: {etf_dict.get('基金简称')}")
                    break

                if found_etf:
                    break

            if not found_etf:
                logger.warning(f"ETF代码 {code} 未在数据中找到")
                return None

            # 5. 数据有效性验证
            validation = self._validate_etf_data(found_etf, code, current_trading_date)
            if not validation['valid']:
                logger.warning(f"ETF {code} 数据验证失败: {validation['issues']}")
                return None

            # 6. 查找最新有效净值（考虑时间和交易日期）
            latest_price = self._find_latest_valid_price(found_etf, code, current_trading_date)

            if not latest_price:
                logger.error(f"ETF {code} 无法找到有效净值")
                return None

            # 7. 获取其他数据字段
            growth_rate = found_etf.get('增长率', '0.0')
            discount_rate = found_etf.get('折价率', '0.0')

            # 清理百分比数值
            growth_rate_cleaned = self._clean_percentage_value(growth_rate)
            discount_rate_cleaned = self._clean_percentage_value(discount_rate)

            # 8. 构建返回数据
            return {
                "code": found_etf.get('基金代码', code),
                "name": found_etf.get('基金简称'),
                "price": latest_price['price'],
                "type": AssetType.ETF_FUND,
                "timestamp": datetime.now(),
                "raw_data": found_etf,  # 保留原始数据用于调试
                "price_field_used": latest_price['field'],
                "price_date": latest_price['date'],
                "trading_date": current_trading_date,
                "validation": validation,

                # 补充其他字段
                "change_amount": 0.0,
                "change_percent": growth_rate_cleaned if growth_rate_cleaned is not None else 0.0,
                "volume": 0,
                "turnover": 0,
                "open_price": latest_price['price'],
                "high_price": latest_price['price'],
                "low_price": latest_price['price'],
                "prev_close": latest_price['price'],
                "turnover_rate": discount_rate_cleaned if discount_rate_cleaned is not None else 0.0,
                "circulating_market_cap": 0.0,
                "total_market_cap": 0.0,
            }

        except Exception as e:
            logger.error(f"获取ETF {code} 数据失败: {e}")
            return None

    def get_open_fund_info(self, code: str) -> Optional[Dict]:
        """
        获取开放式基金信息（带全局缓存和智能净值提取）
        重点：动态解析净值字段，支持海外基金，避免多次API调用
        """
        if not AKSHARE_AVAILABLE:
            logger.warning("Akshare不可用，无法获取真实数据")
            return None

        if not PANDAS_AVAILABLE:
            logger.warning("Pandas不可用，无法处理开放式基金数据")
            return None

        try:
            # 1. 获取当前交易日期
            current_trading_date = self.trading_helper.get_current_trading_date()
            logger.info(f"当前交易日期: {current_trading_date}")

            # 2. 获取全量开放式基金数据（带缓存）
            all_fund_data = self._get_all_open_fund_data_with_cache()

            # 检查数据有效性
            if all_fund_data is None:
                logger.warning("开放式基金全量数据为None")
                return None

            if hasattr(all_fund_data, 'empty') and all_fund_data.empty:
                logger.warning("开放式基金全量数据为空")
                return None

            # 3. 从全量数据中筛选目标代码
            found_fund = None
            try:
                # 使用DataFrame的query方法，更高效
                fund_data_rows = all_fund_data[all_fund_data['基金代码'].astype(str) == str(code)]

                if not fund_data_rows.empty:
                    # 转换为字典
                    fund_dict = fund_data_rows.iloc[0].to_dict()

                    # 处理NaN值
                    fund_dict_cleaned = {}
                    for key, value in fund_dict.items():
                        if pd.isna(value):
                            fund_dict_cleaned[key] = None
                        else:
                            fund_dict_cleaned[key] = value

                    found_fund = fund_dict_cleaned
                    fund_name = fund_dict_cleaned.get('基金简称', '')
                    logger.info(f"找到开放式基金 {code}: {fund_name}")
                else:
                    logger.warning(f"开放式基金代码 {code} 未在数据中找到")

            except Exception as e:
                logger.error(f"处理开放式基金 {code} 数据时出错: {e}")
                return None

            # 4. 数据验证
            validation = self._validate_open_fund_data(found_fund, code)
            if not validation['valid']:
                logger.warning(f"开放式基金 {code} 数据验证失败: {validation['issues']}")
                return None

            # 5. 智能净值提取（考虑时间和海外基金）
            latest_nav = self._find_latest_valid_nav_for_open_fund(found_fund, code, current_trading_date)

            if not latest_nav:
                logger.error(f"开放式基金 {code} 无法找到有效净值")
                return None

            # 6. 构建返回数据
            return self._extract_open_fund_info(found_fund, code, latest_nav, current_trading_date, validation)

        except Exception as e:
            logger.error(f"获取开放式基金 {code} 数据失败: {e}")
            return None

    def get_market_data(self, code: str, asset_type: AssetType) -> Optional[Dict]:
        """
        获取市场数据（智能决策）
        根据交易时间和缓存情况决定是否调用API
        """
        current_time = datetime.now()

        # 根据资产类型调用相应的获取方法
        if asset_type == AssetType.STOCK:
            stock_info = self.get_stock_info(code)
            if not stock_info:
                return None
            return self._build_market_data_from_stock(stock_info)

        elif asset_type == AssetType.ETF_FUND:
            etf_info = self.get_etf_fund_info(code)
            if not etf_info:
                return None
            return etf_info

        elif asset_type == AssetType.LOF_FUND:
            lof_info = self.get_lof_fund_info(code)
            if not lof_info:
                return None
            return lof_info

        elif asset_type == AssetType.OPEN_FUND:
            open_fund_info = self.get_open_fund_info(code)
            if not open_fund_info:
                return None
            return open_fund_info

        else:
            raise NotImplementedError(f"资产类型 {asset_type} 的真实数据获取待实现")

    def _build_market_data_from_stock(self, stock_info: Dict) -> Dict:
        """从股票信息构建市场数据格式"""
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
        """获取所有LOF基金列表"""
        all_lof_data = self._get_all_lof_data_with_cache()

        if all_lof_data is None or all_lof_data.empty:
            return []

        # 将DataFrame转换为字典列表
        lof_list = []
        for idx in range(len(all_lof_data)):
            lof_row = all_lof_data.iloc[idx]

            # 提取基础信息
            lof_dict = {
                'code': str(lof_row['代码']) if pd.notna(lof_row['代码']) else None,
                'name': lof_row.get('名称'),
                'type': AssetType.LOF_FUND,
                'price': float(lof_row['最新价']) if pd.notna(lof_row['最新价']) else 0.0,
                'updated_at': datetime.now()
            }

            # 添加市场数据
            lof_dict.update({
                'change_amount': float(lof_row['涨跌额']) if pd.notna(lof_row['涨跌额']) else 0.0,
                'volume': float(lof_row['成交量']) if pd.notna(lof_row['成交量']) else 0.0,
                'turnover': float(lof_row['成交额']) if pd.notna(lof_row['成交额']) else 0.0,
            })

            lof_list.append(lof_dict)

        logger.info(f"返回 {len(lof_list)} 只LOF基金")
        return lof_list

    def get_all_etf_funds(self) -> List[Dict]:
        """获取所有ETF基金列表（待实现）"""
        raise NotImplementedError("ETF基金列表获取待实现")

    def get_all_open_funds(self) -> List[Dict]:
        """获取所有开放式基金列表"""
        all_fund_data = self._get_all_open_fund_data_with_cache()

        if all_fund_data is None or all_fund_data.empty:
            return []

        # 将DataFrame转换为字典列表
        fund_list = []
        for idx in range(len(all_fund_data)):
            fund_row = all_fund_data.iloc[idx]

            # 提取基础信息
            fund_dict = {
                'code': str(fund_row['基金代码']) if pd.notna(fund_row['基金代码']) else None,
                'name': fund_row.get('基金简称'),
                'type': AssetType.OPEN_FUND,
                'updated_at': datetime.now()
            }

            # 尝试获取净值信息
            fund_code = str(fund_row['基金代码']) if pd.notna(fund_row['基金代码']) else None
            nav_fields = self._parse_nav_fields(fund_row.to_dict())

            if nav_fields and len(nav_fields) > 0:
                # 找最新的净值
                latest_nav_field = nav_fields[0] if nav_fields else None
                if latest_nav_field:
                    nav_value = fund_row.get(latest_nav_field['field'])
                    if nav_value and pd.notna(nav_value):
                        try:
                            fund_dict['price'] = float(nav_value)
                        except (ValueError, TypeError):
                            fund_dict['price'] = 0.0
                    else:
                        fund_dict['price'] = 0.0
            else:
                fund_dict['price'] = 0.0

            fund_list.append(fund_dict)

        logger.info(f"返回 {len(fund_list)} 只开放式基金")
        return fund_list

    def get_asset_info(self, code: str) -> Optional[Dict]:
        """根据代码获取资产信息（自动识别类型）"""
        # 按优先级尝试不同类型
        # 先尝试股票
        stock_info = self.get_stock_info(code)
        if stock_info:
            return stock_info

        # 再尝试ETF
        etf_info = self.get_etf_fund_info(code)
        if etf_info:
            return etf_info

        # 然后尝试LOF
        lof_info = self.get_lof_fund_info(code)
        if lof_info:
            return lof_info

        # 最后尝试开放式基金
        open_fund_info = self.get_open_fund_info(code)
        if open_fund_info:
            return open_fund_info

        return None

    def get_asset_type(self, code: str) -> Optional[AssetType]:
        """根据代码获取资产类型"""
        # 按优先级检查不同类型
        if self.get_stock_info(code):
            return AssetType.STOCK
        if self.get_etf_fund_info(code):
            return AssetType.ETF_FUND
        if self.get_lof_fund_info(code):
            return AssetType.LOF_FUND
        if self.get_open_fund_info(code):
            return AssetType.OPEN_FUND
        return None

    def get_asset_name(self, code: str) -> Optional[str]:
        """根据代码获取资产名称"""
        # 按优先级检查不同类型
        stock_info = self.get_stock_info(code)
        if stock_info:
            return stock_info.get("name")

        etf_info = self.get_etf_fund_info(code)
        if etf_info:
            return etf_info.get("name")

        lof_info = self.get_lof_fund_info(code)
        if lof_info:
            return lof_info.get("name")

        open_fund_info = self.get_open_fund_info(code)
        if open_fund_info:
            return open_fund_info.get("name")

        return None

    def force_refresh_asset(self, code: str, asset_type: AssetType) -> bool:
        """强制刷新资产数据"""
        try:
            # 清除缓存
            self.cache.delete(code)

            # 对于LOF、ETF和开放式基金，还需要清除全局数据缓存
            if asset_type in [AssetType.LOF_FUND, AssetType.ETF_FUND, AssetType.OPEN_FUND]:
                if asset_type == AssetType.LOF_FUND:
                    self.cache.delete(self.lof_cache_key)
                    logger.info(f"已清除LOF全局缓存，准备刷新数据")
                elif asset_type == AssetType.OPEN_FUND:
                    self.cache.delete(self.open_fund_cache_key)
                    logger.info(f"已清除开放式基金全局缓存，准备刷新数据")
                # ETF的全局缓存可以根据需要添加

            # 重新获取数据
            if asset_type == AssetType.STOCK:
                stock_info = self.get_stock_info(code)
                if stock_info:
                    self.cache.set(code, stock_info)
                    logger.info(f"强制刷新成功: {code}")
                    return True
            elif asset_type == AssetType.ETF_FUND:
                etf_info = self.get_etf_fund_info(code)
                if etf_info:
                    self.cache.set(code, etf_info)
                    logger.info(f"强制刷新成功: {code}")
                    return True
            elif asset_type == AssetType.LOF_FUND:
                lof_info = self.get_lof_fund_info(code)
                if lof_info:
                    self.cache.set(code, lof_info)
                    logger.info(f"强制刷新成功: {code}")
                    return True
            elif asset_type == AssetType.OPEN_FUND:
                open_fund_info = self.get_open_fund_info(code)
                if open_fund_info:
                    self.cache.set(code, open_fund_info)
                    logger.info(f"强制刷新成功: {code}")
                    return True
            else:
                logger.warning(f"资产类型 {asset_type} 强制刷新待实现")
                return False

        except Exception as e:
            logger.error(f"强制刷新失败: {code}, 错误: {e}")
            return False

    def _find_latest_valid_price(self, etf_dict: Dict, code: str, current_trading_date: str) -> Optional[Dict]:
        """
        查找最新的有效净值（考虑时间和交易日期）
        逻辑：
        1. 动态解析所有日期格式的净值字段
        2. 按日期降序排序，找到最近的有效净值
        3. 返回价格、字段名、日期和获取方法
        """
        # 1. 动态解析所有日期格式的净值字段
        nav_fields = self._parse_nav_fields(etf_dict)

        if not nav_fields:
            logger.error(f"ETF {code} 无法找到任何净值字段")
            return None

        # 2. 按日期降序排序（最近的日期在前）
        nav_fields.sort(key=lambda x: x['date'], reverse=True)
        logger.info(f"ETF {code} 找到 {len(nav_fields)} 个净值字段，按日期排序")

        # 3. 查找第一个有效的净值值
        for nav_field in nav_fields:
            field_name = nav_field['field']
            nav_value = etf_dict.get(field_name)

            if nav_value:
                try:
                    # 尝试转换为float
                    price = float(nav_value)

                    if self._is_valid_nav_value(price):
                        logger.info(f"ETF {code} 使用净值字段: {field_name} = {price}, 日期: {nav_field['date']}")

                        return {
                            'price': price,
                            'field': field_name,
                            'date': nav_field['date'],
                            'method': 'dynamic_nav_parsing'
                        }
                except (ValueError, TypeError) as e:
                    logger.warning(f"ETF {code} 净值字段 {field_name} 转换失败: {nav_value}, 错误: {e}")
                    continue

        # 4. 如果还是没有找到有效净值
        logger.error(f"ETF {code} 找到了净值字段但无有效值")
        return None

    def _get_all_lof_data_with_cache(self) -> Optional[any]:
        """
        获取全量LOF基金数据（带缓存）
        一次API调用服务所有LOF查询，避免API限流
        """
        # 1. 尝试从缓存获取
        cached_data = self.cache.get(self.lof_cache_key)
        if cached_data:
            logger.info(f"从缓存获取LOF全量数据")
            return cached_data

        # 2. 缓存未命中，调用API获取数据
        logger.info(f"缓存未命中，调用API获取LOF全量数据")

        try:
            # 调用akshare API获取所有LOF基金数据
            all_lof_data = ak.fund_lof_spot_em()

            # 检查数据是否为空
            if all_lof_data.empty:
                logger.warning("LOF基金全量数据为空")
                return None

            logger.info(f"成功获取 {len(all_lof_data)} 只LOF基金数据")

            # 3. 将数据存入缓存
            self.cache.set(self.lof_cache_key, all_lof_data, self.lof_cache_ttl)
            cache_info = self.cache.get_info()
            logger.info(f"LOF数据已缓存，当前缓存状态: {cache_info}")

            return all_lof_data

        except Exception as e:
            logger.error(f"获取LOF基金全量数据失败: {e}")
            return None

    def _validate_lof_data(self, lof_dict: Dict, code: str) -> Dict:
        """验证LOF基金数据有效性"""
        issues = []

        # 检查核心字段是否存在
        code_value = lof_dict.get('代码')
        name_value = lof_dict.get('名称')
        price_value = lof_dict.get('最新价')

        if not code_value:
            issues.append("代码为空")

        if not name_value:
            issues.append("名称为空")

        if price_value is None or price_value == '':
            issues.append("最新价为空")

        # 验证价格有效性
        if price_value is not None and price_value != '':
            try:
                price_float = float(price_value)
                if price_float <= 0:
                    issues.append(f"价格异常: {price_value}")
                if price_float > 1000:  # LOF基金一般不会超过1000
                    issues.append(f"价格可能异常: {price_value}")
            except (ValueError, TypeError):
                issues.append(f"价格格式错误: {price_value}")

        # 检查成交量（如果有）
        volume_value = lof_dict.get('成交量')
        if volume_value is not None:
            try:
                volume_float = float(volume_value)
                if volume_float < 0:
                    issues.append(f"成交量为负数: {volume_value}")
            except (ValueError, TypeError):
                # 成交量数据格式错误，不作为严重错误
                pass

        return {
            'valid': len(issues) == 0,
            'issues': issues
        }

    def _extract_lof_info(self, lof_dict: Dict, code: str) -> Dict:
        """
        从LOF基金原始数据中提取并转换信息
        返回标准化的LOF基金信息格式
        """
        # 获取原始值
        price_raw = lof_dict.get('最新价', 0)
        change_amount_raw = lof_dict.get('涨跌额', 0)
        change_percent_raw = lof_dict.get('涨跌幅', 0)
        volume_raw = lof_dict.get('成交量', 0)
        turnover_raw = lof_dict.get('成交额', 0)
        open_price_raw = lof_dict.get('开盘价', price_raw)
        high_price_raw = lof_dict.get('最高价', price_raw)
        low_price_raw = lof_dict.get('最低价', price_raw)
        prev_close_raw = lof_dict.get('昨收', price_raw)
        turnover_rate_raw = lof_dict.get('换手率', 0)

        # 清理百分比数值
        change_percent_cleaned = self._clean_percentage_value(change_percent_raw)
        turnover_rate_cleaned = self._clean_percentage_value(turnover_rate_raw)

        # 转换价格
        try:
            price = float(price_raw) if price_raw and price_raw != '' else 0.0
            change_amount = float(change_amount_raw) if change_amount_raw and change_amount_raw != '' else 0.0
            volume = float(volume_raw) if volume_raw and volume_raw != '' else 0.0
            turnover = float(turnover_raw) if turnover_raw and turnover_raw != '' else 0.0
            open_price = float(open_price_raw) if open_price_raw and open_price_raw != '' else price
            high_price = float(high_price_raw) if high_price_raw and high_price_raw != '' else price
            low_price = float(low_price_raw) if low_price_raw and low_price_raw != '' else price
            prev_close = float(prev_close_raw) if prev_close_raw and prev_close_raw != '' else price
        except (ValueError, TypeError) as e:
            logger.warning(f"LOF基金 {code} 数值转换失败: {e}")
            price = 0.0
            change_amount = 0.0
            volume = 0.0
            turnover = 0.0
            open_price = 0.0
            high_price = 0.0
            low_price = 0.0
            prev_close = 0.0

        # 构建标准化的LOF基金信息
        return {
            "code": code,
            "name": lof_dict.get('名称', ''),
            "price": price,
            "type": AssetType.LOF_FUND,
            "timestamp": datetime.now(),

            # 市场数据字段
            "change_amount": change_amount,
            "change_percent": change_percent_cleaned if change_percent_cleaned is not None else 0.0,
            "volume": int(volume) if volume > 0 else 0,
            "turnover": turnover,
            "open_price": open_price,
            "high_price": high_price,
            "low_price": low_price,
            "prev_close": prev_close,
            "turnover_rate": turnover_rate_cleaned if turnover_rate_cleaned is not None else 0.0,

            # LOF特有字段
            "circulating_market_cap": lof_dict.get('流通市值', 0.0),
            "total_market_cap": lof_dict.get('总市值', 0.0),

            # 原始数据（用于调试）
            "raw_data": lof_dict,
            "validation": {"valid": True, "issues": []}
        }

    def _get_all_open_fund_data_with_cache(self) -> Optional[any]:
        """
        获取全量开放式基金数据（带缓存）
        一次API调用服务所有开放式基金查询，避免API限流
        """
        # 1. 尝试从缓存获取
        cached_data = self.cache.get(self.open_fund_cache_key)
        if cached_data is not None:
            logger.info(f"从缓存获取开放式基金全量数据")
            # 确保返回的数据类型正确
            if cached_data is None or (hasattr(cached_data, 'empty') and cached_data.empty):
                logger.warning("缓存数据为空")
                return None
            return cached_data

        # 2. 缓存未命中，调用API获取数据
        logger.info(f"缓存未命中，调用API获取开放式基金全量数据")

        try:
            # 调用akshare API获取所有开放式基金数据
            all_fund_data = ak.fund_open_fund_daily_em()

            # 检查数据是否为空
            if all_fund_data.empty:
                logger.warning("开放式基金全量数据为空")
                return None

            logger.info(f"成功获取 {len(all_fund_data)} 只开放式基金数据")

            # 3. 将数据存入缓存
            self.cache.set(self.open_fund_cache_key, all_fund_data, self.open_fund_cache_ttl)
            cache_info = self.cache.get_info()
            logger.info(f"开放式基金数据已缓存，当前缓存状态: {cache_info}")

            return all_fund_data

        except Exception as e:
            logger.error(f"获取开放式基金全量数据失败: {e}")
            return None

    def _is_overseas_fund(self, fund_name: str) -> bool:
        """识别海外基金"""
        if not fund_name:
            return False

        overseas_keywords = [
            '海外', '美元', '港币', '美股',
            '日经', '恒生', '纳指', '标普',
            'QDII', 'H股', '美股', '港股'
        ]

        return any(keyword in fund_name for keyword in overseas_keywords)

    def _find_latest_valid_nav_for_open_fund(self, fund_dict: Dict, code: str, current_trading_date: str) -> Optional[Dict]:
        """
        查找开放式基金最新的有效净值（智能选择，支持海外基金）
        逻辑：
        1. 动态解析所有日期格式的净值字段（单位净值和累计净值）
        2. 按日期降序排序，优先选择最近的净值
        3. 支持回退到历史日期（针对海外基金）
        """
        # 1. 动态解析所有净值字段
        nav_fields = self._parse_nav_fields(fund_dict)

        if not nav_fields:
            logger.error(f"开放式基金 {code} 无法找到任何净值字段")
            return None

        # 2. 按日期降序排序（最近的日期在前）
        nav_fields.sort(key=lambda x: x['date'], reverse=True)
        logger.info(f"开放式基金 {code} 找到 {len(nav_fields)} 个净值字段，按日期排序")

        # 3. 智能查找有效净值
        fund_name = fund_dict.get('基金简称', '')
        is_overseas = self._is_overseas_fund(fund_name)

        # 优先查找"单位净值"
        unit_nav_pattern = re.compile(r'(\d{4}-\d{2}-\d{2})-单位净值$')
        accumulated_nav_pattern = re.compile(r'(\d{4}-\d{2}-\d{2})-累计净值$')

        # 提取单位净值字段和累计净值字段
        unit_nav_fields = [nav for nav in nav_fields if unit_nav_pattern.match(nav['field'])]
        accumulated_nav_fields = [nav for nav in nav_fields if accumulated_nav_pattern.match(nav['field'])]

        # 优先使用单位净值
        for nav_field in unit_nav_fields:
            field_name = nav_field['field']
            nav_value = fund_dict.get(field_name)

            if nav_value:
                try:
                    nav_float = float(nav_value)
                    if self._is_valid_nav_value(nav_float):
                        logger.info(f"开放式基金 {code} 使用单位净值字段: {field_name} = {nav_float}, 日期: {nav_field['date']}")

                        return {
                            'price': nav_float,
                            'field': field_name,
                            'date': nav_field['date'],
                            'method': 'unit_nav',
                            'nav_type': '单位净值'
                        }
                except (ValueError, TypeError) as e:
                    logger.warning(f"开放式基金 {code} 单位净值字段 {field_name} 转换失败: {nav_value}, 错误: {e}")
                    continue

        # 如果单位净值无效，尝试累计净值
        for nav_field in accumulated_nav_fields:
            field_name = nav_field['field']
            nav_value = fund_dict.get(field_name)

            if nav_value:
                try:
                    nav_float = float(nav_value)
                    if self._is_valid_nav_value(nav_float):
                        logger.info(f"开放式基金 {code} 使用累计净值字段: {field_name} = {nav_float}, 日期: {nav_field['date']}")

                        return {
                            'price': nav_float,
                            'field': field_name,
                            'date': nav_field['date'],
                            'method': 'accumulated_nav',
                            'nav_type': '累计净值'
                        }
                except (ValueError, TypeError) as e:
                    logger.warning(f"开放式基金 {code} 累计净值字段 {field_name} 转换失败: {nav_value}, 错误: {e}")
                    continue

        # 如果还是没有找到有效净值
        logger.error(f"开放式基金 {code} 无法找到有效净值")
        return None

    def _validate_open_fund_data(self, fund_dict: Dict, code: str) -> Dict:
        """验证开放式基金数据有效性"""
        issues = []

        # 检查核心字段是否存在
        code_value = fund_dict.get('基金代码')
        name_value = fund_dict.get('基金简称')

        if not code_value:
            issues.append("基金代码为空")

        if not name_value:
            issues.append("基金简称为空")

        # 检查是否有任何净值数据
        nav_fields = self._parse_nav_fields(fund_dict)

        has_any_nav = False
        for nav_field in nav_fields:
            nav_value = fund_dict.get(nav_field['field'])
            if nav_value:
                try:
                    nav_float = float(nav_value)
                    if self._is_valid_nav_value(nav_float):
                        has_any_nav = True
                        break
                except (ValueError, TypeError):
                    continue

        if not has_any_nav:
            issues.append("没有有效的净值数据")
            return {
                'valid': False,
                'issues': issues
            }

        # 检查交易状态
        purchase_status = fund_dict.get('申购状态')
        redemption_status = fund_dict.get('赎回状态')

        if purchase_status:
            logger.info(f"基金 {code} 申购状态: {purchase_status}")
        if redemption_status:
            logger.info(f"基金 {code} 赎回状态: {redemption_status}")

        return {
            'valid': len(issues) == 0,
            'issues': issues
        }

    def _extract_open_fund_info(self, fund_dict: Dict, code: str, latest_nav: Dict, current_trading_date: str, validation: Dict) -> Dict:
        """
        从开放式基金原始数据中提取并转换信息
        返回标准化的开放式基金信息格式
        """
        # 获取基础信息
        fund_name = fund_dict.get('基金简称', '')

        # 获取变动数据
        change_amount_raw = fund_dict.get('日增长值', 0)
        change_percent_raw = fund_dict.get('日增长率', 0)

        # 清理百分比数值
        change_percent_cleaned = self._clean_percentage_value(change_percent_raw)

        # 转换数值
        try:
            change_amount = float(change_amount_raw) if change_amount_raw and change_amount_raw != '' else 0.0
        except (ValueError, TypeError):
            change_amount = 0.0

        # 构建标准化的开放式基金信息
        return {
            "code": code,
            "name": fund_name,
            "price": latest_nav['price'],
            "type": AssetType.OPEN_FUND,
            "timestamp": datetime.now(),

            # 净值信息
            "unit_net_value": latest_nav['price'] if latest_nav.get('nav_type') == '单位净值' else 0.0,
            "accumulated_net_value": latest_nav['price'] if latest_nav.get('nav_type') == '累计净值' else 0.0,
            "nav_field_used": latest_nav['field'],
            "nav_date": latest_nav['date'],
            "nav_method": latest_nav['method'],

            # 变动数据
            "change_amount": change_amount,
            "change_percent": change_percent_cleaned if change_percent_cleaned is not None else 0.0,

            # 状态信息
            "purchase_status": fund_dict.get('申购状态', ''),
            "redemption_status": fund_dict.get('赎回状态', ''),
            "fee_rate": fund_dict.get('手续费', 0.0),

            # 补充市场数据字段（开放式基金通常没有实时行情）
            "volume": 0,
            "turnover": 0,
            "open_price": latest_nav['price'],
            "high_price": latest_nav['price'],
            "low_price": latest_nav['price'],
            "prev_close": latest_nav['price'],
            "turnover_rate": 0.0,
            "circulating_market_cap": 0.0,
            "total_market_cap": 0.0,

            # 额外信息
            "trading_date": current_trading_date,
            "validation": validation,

            # 原始数据（用于调试）
            "raw_data": fund_dict
        }

    def _parse_nav_fields(self, etf_dict: Dict) -> List[Dict]:
        """
        动态解析ETF字典中所有日期格式的净值字段
        返回格式: [{'field': '2026-03-08-单位净值', 'date': datetime(2026, 3, 8)}, ...]
        """
        nav_fields = []
        date_pattern = re.compile(r'^(\d{4}-\d{2}-\d{2})-.+$')  # 匹配日期开头的字段

        for field_name in etf_dict.keys():
            match = date_pattern.match(field_name)
            if match:
                date_str = match.group(1)
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    nav_fields.append({
                        'field': field_name,
                        'date': date_obj
                    })
                except ValueError:
                    # 日期格式不正确，跳过
                    continue

        return nav_fields

    def _clean_percentage_value(self, value) -> Optional[float]:
        """清理百分比数值，去除百分号并转换为float"""
        if value is None or value == '':
            return None

        try:
            # 如果是字符串，先去除空白字符
            if isinstance(value, str):
                value = value.strip()

                # 去除百分号
                if value.endswith('%'):
                    value = value.replace('%', '').strip()

            # 转换为float
            return float(value)
        except (ValueError, TypeError):
            logger.warning(f"无法转换百分比数值: {value}")
            return None

    def _is_valid_nav_value(self, value: float) -> bool:
        """验证净值是否有效"""
        # 排除零值和负值
        # 检查是否在合理范围内
        return 0.001 < value < 10000  # 一般ETF净值范围

    def _validate_etf_data(self, etf_dict: Dict, code: str, current_trading_date: str) -> Dict:
        """验证ETF数据有效性"""
        issues = []

        # 动态解析净值字段并检查是否有任何净值数据
        nav_fields = self._parse_nav_fields(etf_dict)

        has_any_nav = False
        for nav_field in nav_fields:
            nav_value = etf_dict.get(nav_field['field'])
            if nav_value:
                try:
                    nav_float = float(nav_value)
                    if self._is_valid_nav_value(nav_float):
                        has_any_nav = True
                        break
                except (ValueError, TypeError):
                    continue

        if not has_any_nav:
            issues.append("没有有效的净值数据")
            return {
                'valid': False,
                'issues': issues
            }

        # 检查增长率数据
        growth_rate = etf_dict.get('增长率')
        if growth_rate:
            growth_cleaned = self._clean_percentage_value(growth_rate)
            if growth_cleaned is not None and abs(growth_cleaned) > 50:  # 增长率超过50%可能是异常
                issues.append(f"增长率异常: {growth_rate}")

        # 检查折价率
        discount_rate = etf_dict.get('折价率')
        if discount_rate:
            discount_cleaned = self._clean_percentage_value(discount_rate)
            if discount_cleaned is not None and abs(discount_cleaned) > 20:  # 折价率超过20%可能是异常
                issues.append(f"折价率异常: {discount_rate}")

        # 检查基金简称
        fund_name = etf_dict.get('基金简称')
        if not fund_name or not pd.notna(fund_name):
            issues.append("基金简称为空")

        return {
            'valid': len(issues) == 0,
            'issues': issues
        }


# 创建真实数据服务实例
real_data_service = RealMarketDataService() if (AKSHARE_AVAILABLE and PANDAS_AVAILABLE) else None
