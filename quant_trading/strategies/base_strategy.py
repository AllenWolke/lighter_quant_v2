"""
策略基类
定义所有交易策略的通用接口
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..utils.config import Config
from ..utils.logger import setup_logger


class BaseStrategy(ABC):
    """策略基类"""
    
    def __init__(self, name: str, config: Config):
        """
        初始化策略
        
        Args:
            name: 策略名称
            config: 配置对象
        """
        self.name = name
        self.config = config
        self.logger = setup_logger(f"Strategy_{name}", config.log_level)
        
        # 策略状态
        self.is_active_flag = True
        self.engine = None
        
        # 策略统计
        self.trades_count = 0
        self.total_pnl = 0.0
        self.start_time = None
        
    def set_engine(self, engine):
        """设置交易引擎"""
        self.engine = engine
        
    async def initialize(self):
        """初始化策略"""
        self.logger.info(f"初始化策略: {self.name}")
        self.start_time = datetime.now()
        await self.on_initialize()
        
    async def start(self):
        """启动策略"""
        self.logger.info(f"启动策略: {self.name}")
        self.is_active_flag = True
        await self.on_start()
        
    async def stop(self):
        """停止策略"""
        self.logger.info(f"停止策略: {self.name}")
        self.is_active_flag = False
        await self.on_stop()
        
    def is_active(self) -> bool:
        """检查策略是否活跃"""
        return self.is_active_flag
        
    async def on_tick(self, market_data: Dict[int, Dict[str, Any]]):
        """
        市场数据更新时的回调
        
        Args:
            market_data: 市场数据
        """
        if not self.is_active():
            return
            
        try:
            await self.process_market_data(market_data)
        except Exception as e:
            self.logger.error(f"策略处理市场数据失败: {e}")
            
    @abstractmethod
    async def on_initialize(self):
        """策略初始化时的回调"""
        pass
        
    @abstractmethod
    async def on_start(self):
        """策略启动时的回调"""
        pass
        
    @abstractmethod
    async def on_stop(self):
        """策略停止时的回调"""
        pass
        
    @abstractmethod
    async def process_market_data(self, market_data: Dict[int, Dict[str, Any]]):
        """
        处理市场数据
        
        Args:
            market_data: 市场数据
        """
        pass
        
    def get_status(self) -> Dict[str, Any]:
        """获取策略状态"""
        return {
            "name": self.name,
            "is_active": self.is_active(),
            "start_time": self.start_time,
            "uptime": datetime.now() - self.start_time if self.start_time else None,
            "trades_count": self.trades_count,
            "total_pnl": self.total_pnl
        }
        
    def _record_trade(self, pnl: float):
        """记录交易"""
        self.trades_count += 1
        self.total_pnl += pnl
        self.logger.info(f"记录交易: 盈亏 {pnl}, 总盈亏 {self.total_pnl}")
        
    def _log_signal(self, signal_type: str, market_id: int, **kwargs):
        """记录交易信号"""
        self.logger.info(f"交易信号: {signal_type}, 市场 {market_id}, {kwargs}")
        
    def _check_risk_limits(self, market_id: int, size: float, price: float) -> bool:
        """检查风险限制"""
        if not self.engine:
            return False
            
        return self.engine.risk_manager.check_position_size(market_id, size, price)
        
    def _create_order(self, market_id: int, side: str, order_type: str, 
                     size: float, price: float, leverage: float = 1.0,
                     margin_mode: str = "cross", price_slippage_tolerance: float = None):
        """
        创建订单
        
        Args:
            market_id: 市场ID
            side: 订单方向 ("buy" 或 "sell")
            order_type: 订单类型 ("market" 或 "limit")
            size: 订单大小
            price: 订单价格
            leverage: 杠杆倍数，默认1倍（不使用杠杆）
            margin_mode: 保证金模式 ("cross" 全仓 或 "isolated" 逐仓)，默认全仓
            price_slippage_tolerance: 价格滑点容忍度（可选，策略可自定义）
        """
        if not self.engine:
            return None
            
        from ..core.order_manager import OrderSide, OrderType, MarginMode
        
        order_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
        order_type_enum = OrderType.MARKET if order_type.lower() == "market" else OrderType.LIMIT
        margin_mode_enum = MarginMode.CROSS if margin_mode.lower() == "cross" else MarginMode.ISOLATED
        
        return self.engine.order_manager.create_order(
            market_id=market_id,
            side=order_side,
            order_type=order_type_enum,
            size=size,
            price=price,
            leverage=leverage,
            margin_mode=margin_mode_enum,
            price_slippage_tolerance=price_slippage_tolerance
        )
        
    def _get_position(self, market_id: int):
        """获取仓位"""
        if not self.engine:
            return None
            
        return self.engine.position_manager.get_position(market_id)
        
    def _get_market_data(self, market_id: int):
        """获取市场数据"""
        if not self.engine:
            return None
            
        return self.engine.data_manager.get_market_data(market_id)
