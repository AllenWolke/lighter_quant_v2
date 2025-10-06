"""
Lighter交易所数据源
从Lighter交易所API获取市场数据
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import lighter
from lighter.api.candlestick_api import CandlestickApi
from lighter.api.order_api import OrderApi

from .base_data_source import BaseDataSource


class LighterDataSource(BaseDataSource):
    """Lighter交易所数据源"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化Lighter数据源
        
        Args:
            config: 配置字典，包含api_client等
        """
        super().__init__(config)
        self.api_client = config.get("api_client")
        self.logger = logging.getLogger("LighterDataSource")
        
        # API实例
        self.candlestick_api = CandlestickApi(self.api_client)
        self.order_api = OrderApi(self.api_client)
        
        # 市场ID到交易对符号的映射
        self.market_symbol_map: Dict[int, str] = {}
        
    async def initialize(self):
        """初始化数据源"""
        self.logger.info("初始化Lighter数据源...")
        
        try:
            # 获取市场列表
            markets = await self.order_api.order_books()
            
            # 建立市场ID到交易对符号的映射
            for market in markets.order_books:
                # 这里需要根据实际的市场信息构建交易对符号
                # 假设市场有base_token和quote_token字段
                symbol = f"{market.base_token}_{market.quote_token}" if hasattr(market, 'base_token') else f"MARKET_{market.market_id}"
                self.market_symbol_map[market.market_id] = symbol
                
            self.logger.info(f"Lighter数据源初始化完成，发现 {len(self.market_symbol_map)} 个市场")
            
        except Exception as e:
            self.logger.error(f"Lighter数据源初始化失败: {e}")
            raise
            
    async def get_candlesticks(self, symbol: str, timeframe: str, 
                              limit: int = 100) -> List[Dict[str, Any]]:
        """获取K线数据"""
        try:
            # 根据交易对符号找到市场ID
            market_id = self._get_market_id_by_symbol(symbol)
            if market_id is None:
                self.logger.warning(f"未找到交易对 {symbol} 对应的市场ID")
                return []
                
            # 获取K线数据
            end_time = int(datetime.now().timestamp())
            start_time = end_time - 3600  # 获取最近1小时的数据
            
            candlesticks = await self.candlestick_api.candlesticks(
                market_id=market_id,
                resolution=timeframe,
                start_timestamp=start_time,
                end_timestamp=end_time,
                count_back=limit
            )
            
            if candlesticks and candlesticks.candlesticks:
                return [
                    {
                        "timestamp": c.timestamp,
                        "open": float(c.open),
                        "high": float(c.high),
                        "low": float(c.low),
                        "close": float(c.close),
                        "volume": float(c.volume)
                    } for c in candlesticks.candlesticks
                ]
                
            return []
            
        except Exception as e:
            self.logger.error(f"获取K线数据失败 ({symbol}): {e}")
            return []
            
    async def get_current_price(self, symbol: str) -> Optional[float]:
        """获取当前价格"""
        try:
            # 获取最新的K线数据
            candlesticks = await self.get_candlesticks(symbol, "1m", 1)
            if candlesticks:
                return candlesticks[-1]["close"]
            return None
            
        except Exception as e:
            self.logger.error(f"获取当前价格失败 ({symbol}): {e}")
            return None
            
    async def get_order_book(self, symbol: str) -> Optional[Dict[str, Any]]:
        """获取订单簿数据"""
        try:
            market_id = self._get_market_id_by_symbol(symbol)
            if market_id is None:
                return None
                
            order_book = await self.order_api.order_book_details(market_id=market_id)
            
            if order_book:
                return {
                    "bids": [(float(bid.price), float(bid.amount)) for bid in order_book.bids],
                    "asks": [(float(ask.price), float(ask.amount)) for ask in order_book.asks],
                    "timestamp": datetime.now().timestamp()
                }
                
            return None
            
        except Exception as e:
            self.logger.error(f"获取订单簿失败 ({symbol}): {e}")
            return None
            
    async def get_trades(self, symbol: str, limit: int = 50) -> List[Dict[str, Any]]:
        """获取交易数据"""
        try:
            market_id = self._get_market_id_by_symbol(symbol)
            if market_id is None:
                return []
                
            trades = await self.order_api.recent_trades(market_id=market_id, limit=limit)
            
            if trades and trades.trades:
                return [
                    {
                        "timestamp": t.timestamp,
                        "price": float(t.price),
                        "amount": float(t.amount),
                        "side": t.side
                    } for t in trades.trades
                ]
                
            return []
            
        except Exception as e:
            self.logger.error(f"获取交易数据失败 ({symbol}): {e}")
            return []
            
    def get_supported_symbols(self) -> List[str]:
        """获取支持的交易对列表"""
        return list(self.market_symbol_map.values())
        
    def get_supported_timeframes(self) -> List[str]:
        """获取支持的时间周期列表"""
        return ["1m", "5m", "15m", "1h", "4h", "1d"]
        
    def _get_market_id_by_symbol(self, symbol: str) -> Optional[int]:
        """根据交易对符号获取市场ID"""
        for market_id, market_symbol in self.market_symbol_map.items():
            if market_symbol == symbol:
                return market_id
        return None
