"""
数据管理器
负责获取和管理市场数据
支持多种数据源
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import lighter
from lighter.api.candlestick_api import CandlestickApi
from lighter.api.order_api import OrderApi
from lighter.api.account_api import AccountApi

from ..utils.config import Config
from ..utils.logger import setup_logger
from ..data_sources import LighterDataSource, TradingViewDataSource


class DataManager:
    """数据管理器"""
    
    def __init__(self, api_client: lighter.ApiClient, config: Config):
        """
        初始化数据管理器
        
        Args:
            api_client: lighter API客户端
            config: 配置对象
        """
        self.api_client = api_client
        self.config = config
        self.logger = setup_logger("DataManager", config.log_level)
        
        # API实例
        self.candlestick_api = CandlestickApi(api_client)
        self.order_api = OrderApi(api_client)
        self.account_api = AccountApi(api_client)
        
        # 数据源
        self.data_sources: Dict[str, Any] = {}
        self.primary_data_source = "lighter"  # 默认主数据源
        
        # 数据缓存
        self.market_data_cache: Dict[int, Dict[str, Any]] = {}
        self.order_book_cache: Dict[int, Dict[str, Any]] = {}
        self.account_cache: Optional[Dict[str, Any]] = None
        
        # 数据更新时间
        self.last_update_time: Dict[str, datetime] = {}
        
    async def initialize(self):
        """初始化数据管理器"""
        self.logger.info("初始化数据管理器...")
        
        # 初始化数据源
        await self._initialize_data_sources()
        
        # 获取初始市场数据
        await self._load_initial_data()
        
        self.logger.info("数据管理器初始化完成")
        
    async def _initialize_data_sources(self):
        """初始化数据源"""
        try:
            # 初始化Lighter数据源
            lighter_config = {
                "api_client": self.api_client
            }
            self.data_sources["lighter"] = LighterDataSource(lighter_config)
            await self.data_sources["lighter"].initialize()
            
            # 初始化TradingView数据源
            tv_config = self.config.data_sources.get("tradingview", {})
            if tv_config.get("enabled", False):
                self.data_sources["tradingview"] = TradingViewDataSource(tv_config)
                await self.data_sources["tradingview"].initialize()
                self.logger.info("TradingView数据源已启用")
            
            # 设置主数据源
            self.primary_data_source = self.config.data_sources.get("primary", "lighter")
            self.logger.info(f"主数据源设置为: {self.primary_data_source}")
            
        except Exception as e:
            self.logger.error(f"初始化数据源失败: {e}")
            raise
        
    async def _load_initial_data(self):
        """加载初始数据"""
        try:
            # 获取市场列表
            markets = await self.order_api.order_books()
            self.logger.info(f"发现 {len(markets.order_books)} 个市场")
            
            # 为每个市场初始化数据缓存
            for market in markets.order_books:
                market_id = market.market_id
                self.market_data_cache[market_id] = {
                    "market_info": market,
                    "candlesticks": [],
                    "order_book": None,
                    "trades": []
                }
                
        except Exception as e:
            self.logger.error(f"加载初始数据失败: {e}")
            raise
            
    async def get_latest_data(self) -> Dict[int, Dict[str, Any]]:
        """
        获取最新市场数据
        
        Returns:
            市场数据字典
        """
        try:
            # 更新所有市场的数据
            for market_id in self.market_data_cache.keys():
                await self._update_market_data(market_id)
                
            return self.market_data_cache
            
        except Exception as e:
            self.logger.error(f"获取最新数据失败: {e}")
            return self.market_data_cache
            
    async def get_data_from_source(self, source_name: str, symbol: str, 
                                  data_type: str = "candlesticks", **kwargs) -> Any:
        """
        从指定数据源获取数据
        
        Args:
            source_name: 数据源名称
            symbol: 交易对符号
            data_type: 数据类型 (candlesticks, current_price, order_book, trades)
            **kwargs: 其他参数
            
        Returns:
            数据
        """
        try:
            if source_name not in self.data_sources:
                self.logger.error(f"数据源 {source_name} 不存在")
                return None
                
            data_source = self.data_sources[source_name]
            
            if data_type == "candlesticks":
                return await data_source.get_candlesticks(
                    symbol, 
                    kwargs.get("timeframe", "1m"),
                    kwargs.get("limit", 100)
                )
            elif data_type == "current_price":
                return await data_source.get_current_price(symbol)
            elif data_type == "order_book":
                return await data_source.get_order_book(symbol)
            elif data_type == "trades":
                return await data_source.get_trades(symbol, kwargs.get("limit", 50))
            else:
                self.logger.error(f"不支持的数据类型: {data_type}")
                return None
                
        except Exception as e:
            self.logger.error(f"从数据源 {source_name} 获取数据失败: {e}")
            return None
            
    async def get_tradingview_data(self, symbol: str, data_type: str = "candlesticks", **kwargs) -> Any:
        """
        从TradingView获取数据
        
        Args:
            symbol: 交易对符号
            data_type: 数据类型
            **kwargs: 其他参数
            
        Returns:
            数据
        """
        return await self.get_data_from_source("tradingview", symbol, data_type, **kwargs)
        
    def get_available_data_sources(self) -> List[str]:
        """获取可用的数据源列表"""
        return list(self.data_sources.keys())
        
    def set_primary_data_source(self, source_name: str):
        """设置主数据源"""
        if source_name in self.data_sources:
            self.primary_data_source = source_name
            self.logger.info(f"主数据源已设置为: {source_name}")
        else:
            self.logger.error(f"数据源 {source_name} 不存在")
            
    async def _update_market_data(self, market_id: int):
        """更新指定市场的数据"""
        try:
            current_time = datetime.now()
            
            # 更新K线数据
            if self._should_update_data("candlesticks", market_id):
                await self._update_candlesticks(market_id)
                self.last_update_time[f"candlesticks_{market_id}"] = current_time
                
            # 更新订单簿数据
            if self._should_update_data("order_book", market_id):
                await self._update_order_book(market_id)
                self.last_update_time[f"order_book_{market_id}"] = current_time
                
            # 更新交易数据
            if self._should_update_data("trades", market_id):
                await self._update_trades(market_id)
                self.last_update_time[f"trades_{market_id}"] = current_time
                
        except Exception as e:
            self.logger.error(f"更新市场 {market_id} 数据失败: {e}")
            
    def _should_update_data(self, data_type: str, market_id: int) -> bool:
        """检查是否需要更新数据"""
        key = f"{data_type}_{market_id}"
        last_update = self.last_update_time.get(key)
        
        if last_update is None:
            return True
            
        # 根据数据类型设置更新间隔
        intervals = {
            "candlesticks": timedelta(seconds=60),  # 1分钟
            "order_book": timedelta(seconds=5),     # 5秒
            "trades": timedelta(seconds=10)         # 10秒
        }
        
        interval = intervals.get(data_type, timedelta(seconds=30))
        return datetime.now() - last_update > interval
        
    async def _update_candlesticks(self, market_id: int):
        """更新K线数据"""
        try:
            end_time = int(datetime.now().timestamp())
            start_time = end_time - 3600  # 获取最近1小时的数据
            
            candlesticks = await self.candlestick_api.candlesticks(
                market_id=market_id,
                resolution="1m",
                start_timestamp=start_time,
                end_timestamp=end_time,
                count_back=60
            )
            
            if candlesticks and candlesticks.candlesticks:
                self.market_data_cache[market_id]["candlesticks"] = [
                    {
                        "timestamp": c.timestamp,
                        "open": c.open,
                        "high": c.high,
                        "low": c.low,
                        "close": c.close,
                        "volume": c.volume
                    } for c in candlesticks.candlesticks
                ]
                
        except Exception as e:
            self.logger.error(f"更新K线数据失败 (市场 {market_id}): {e}")
            
    async def _update_order_book(self, market_id: int):
        """更新订单簿数据"""
        try:
            order_book = await self.order_api.order_book_details(market_id=market_id)
            
            if order_book:
                self.market_data_cache[market_id]["order_book"] = {
                    "bids": [(float(bid.price), float(bid.amount)) for bid in order_book.bids],
                    "asks": [(float(ask.price), float(ask.amount)) for ask in order_book.asks],
                    "timestamp": datetime.now().timestamp()
                }
                
        except Exception as e:
            self.logger.error(f"更新订单簿失败 (市场 {market_id}): {e}")
            
    async def _update_trades(self, market_id: int):
        """更新交易数据"""
        try:
            trades = await self.order_api.recent_trades(market_id=market_id, limit=100)
            
            if trades and trades.trades:
                self.market_data_cache[market_id]["trades"] = [
                    {
                        "timestamp": t.timestamp,
                        "price": float(t.price),
                        "amount": float(t.amount),
                        "side": t.side
                    } for t in trades.trades
                ]
                
        except Exception as e:
            self.logger.error(f"更新交易数据失败 (市场 {market_id}): {e}")
            
    async def get_account_data(self) -> Optional[Dict[str, Any]]:
        """获取账户数据"""
        try:
            account = await self.account_api.account(
                by="index", 
                value=str(self.config.lighter_config["account_index"])
            )
            
            if account:
                self.account_cache = {
                    "account_index": account.account_index,
                    "l1_address": account.l1_address,
                    "positions": account.positions,
                    "balance": account.balance,
                    "timestamp": datetime.now().timestamp()
                }
                
            return self.account_cache
            
        except Exception as e:
            self.logger.error(f"获取账户数据失败: {e}")
            return self.account_cache
            
    def get_market_data(self, market_id: int) -> Optional[Dict[str, Any]]:
        """获取指定市场的数据"""
        return self.market_data_cache.get(market_id)
        
    def get_candlesticks(self, market_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """获取K线数据"""
        market_data = self.get_market_data(market_id)
        if market_data and "candlesticks" in market_data:
            return market_data["candlesticks"][-limit:]
        return []
        
    def get_order_book(self, market_id: int) -> Optional[Dict[str, Any]]:
        """获取订单簿数据"""
        market_data = self.get_market_data(market_id)
        if market_data and "order_book" in market_data:
            return market_data["order_book"]
        return None
        
    def get_trades(self, market_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """获取交易数据"""
        market_data = self.get_market_data(market_id)
        if market_data and "trades" in market_data:
            return market_data["trades"][-limit:]
        return []
