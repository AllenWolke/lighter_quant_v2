"""
数据源基类
定义所有数据源的通用接口
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime


class BaseDataSource(ABC):
    """数据源基类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化数据源
        
        Args:
            config: 数据源配置
        """
        self.config = config
        
    @abstractmethod
    async def initialize(self):
        """初始化数据源"""
        pass
        
    @abstractmethod
    async def get_candlesticks(self, symbol: str, timeframe: str, 
                              limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取K线数据
        
        Args:
            symbol: 交易对符号
            timeframe: 时间周期
            limit: 数据条数
            
        Returns:
            K线数据列表
        """
        pass
        
    @abstractmethod
    async def get_current_price(self, symbol: str) -> Optional[float]:
        """
        获取当前价格
        
        Args:
            symbol: 交易对符号
            
        Returns:
            当前价格
        """
        pass
        
    @abstractmethod
    async def get_order_book(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取订单簿数据
        
        Args:
            symbol: 交易对符号
            
        Returns:
            订单簿数据
        """
        pass
        
    @abstractmethod
    async def get_trades(self, symbol: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取交易数据
        
        Args:
            symbol: 交易对符号
            limit: 数据条数
            
        Returns:
            交易数据列表
        """
        pass
        
    def get_supported_symbols(self) -> List[str]:
        """
        获取支持的交易对列表
        
        Returns:
            交易对列表
        """
        return []
        
    def get_supported_timeframes(self) -> List[str]:
        """
        获取支持的时间周期列表
        
        Returns:
            时间周期列表
        """
        return []
