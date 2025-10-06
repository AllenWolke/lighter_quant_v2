"""
动量策略
基于价格动量的策略
"""

import logging
from typing import Dict, List, Optional, Any
import numpy as np
from datetime import datetime, timedelta

from .base_strategy import BaseStrategy
from ..utils.config import Config
from ..utils.logger import setup_logger
from ..core.position_manager import PositionSide


class MomentumStrategy(BaseStrategy):
    """动量策略"""
    
    def __init__(self, config: Config, market_id: int = 0,
                 short_period: int = 5, long_period: int = 20, 
                 momentum_threshold: float = 0.02):
        """
        初始化动量策略
        
        Args:
            config: 配置对象
            market_id: 市场ID
            short_period: 短期周期
            long_period: 长期周期
            momentum_threshold: 动量阈值
        """
        super().__init__("Momentum", config)
        
        self.market_id = market_id
        self.short_period = short_period
        self.long_period = long_period
        self.momentum_threshold = momentum_threshold
        
        # 策略参数
        self.position_size = 0.1  # 仓位大小
        self.stop_loss = 0.03     # 止损比例
        self.take_profit = 0.05   # 止盈比例
        
        # 状态变量
        self.last_signal_time = None
        self.signal_cooldown = timedelta(minutes=10)  # 信号冷却时间
        
    async def on_initialize(self):
        """策略初始化"""
        self.logger.info(f"初始化动量策略: 市场 {self.market_id}, 短期 {self.short_period}, 长期 {self.long_period}")
        
    async def on_start(self):
        """策略启动"""
        self.logger.info("动量策略已启动")
        
    async def on_stop(self):
        """策略停止"""
        self.logger.info("动量策略已停止")
        
    async def process_market_data(self, market_data: Dict[int, Dict[str, Any]]):
        """处理市场数据"""
        if self.market_id not in market_data:
            return
            
        market_data_info = market_data[self.market_id]
        candlesticks = market_data_info.get("candlesticks", [])
        
        if len(candlesticks) < self.long_period:
            return
            
        # 获取当前价格
        current_price = self._get_current_price(candlesticks)
        if current_price is None:
            return
            
        # 计算动量指标
        momentum = self._calculate_momentum(candlesticks)
        if momentum is None:
            return
            
        # 检查信号冷却
        if (self.last_signal_time and 
            datetime.now() - self.last_signal_time < self.signal_cooldown):
            return
            
        # 生成交易信号
        await self._generate_signal(current_price, momentum)
        
    def _get_current_price(self, candlesticks: List[Dict[str, Any]]) -> Optional[float]:
        """获取当前价格"""
        if not candlesticks:
            return None
            
        latest_candle = candlesticks[-1]
        if not isinstance(latest_candle, dict) or "close" not in latest_candle:
            return None
            
        price = latest_candle["close"]
        if not isinstance(price, (int, float)) or price <= 0:
            return None
            
        return price
        
    def _calculate_momentum(self, candlesticks: List[Dict[str, Any]]) -> Optional[float]:
        """计算动量指标"""
        if len(candlesticks) < self.long_period:
            return None
            
        prices = [c["close"] for c in candlesticks[-self.long_period:]]
        
        # 检查价格数据有效性
        if not prices or any(p <= 0 for p in prices):
            return None
        
        # 计算短期和长期移动平均
        short_ma = np.mean(prices[-self.short_period:])
        long_ma = np.mean(prices)
        
        # 防止除零错误
        if long_ma == 0:
            return None
        
        # 计算动量
        momentum = (short_ma - long_ma) / long_ma
        
        return momentum
        
    async def _generate_signal(self, current_price: float, momentum: float):
        """生成交易信号"""
        # 检查是否已有仓位
        position = self._get_position(self.market_id)
        
        if position:
            # 已有仓位，检查是否需要平仓
            await self._check_exit_conditions(position, current_price, momentum)
        else:
            # 没有仓位，检查是否需要开仓
            if momentum > self.momentum_threshold:
                # 正动量，做多
                await self._open_long_position(current_price, momentum)
            elif momentum < -self.momentum_threshold:
                # 负动量，做空
                await self._open_short_position(current_price, momentum)
                
    async def _open_long_position(self, price: float, momentum: float):
        """开多仓"""
        if not self._check_risk_limits(self.market_id, self.position_size, price):
            return
            
        # 创建订单
        order = self._create_order(
            market_id=self.market_id,
            side="buy",
            order_type="market",
            size=self.position_size,
            price=price
        )
        
        if order:
            self._log_signal("LONG", self.market_id, 
                           price=price, momentum=momentum, size=self.position_size)
            self.last_signal_time = datetime.now()
            
    async def _open_short_position(self, price: float, momentum: float):
        """开空仓"""
        if not self._check_risk_limits(self.market_id, self.position_size, price):
            return
            
        # 创建订单
        order = self._create_order(
            market_id=self.market_id,
            side="sell",
            order_type="market",
            size=self.position_size,
            price=price
        )
        
        if order:
            self._log_signal("SHORT", self.market_id, 
                           price=price, momentum=momentum, size=self.position_size)
            self.last_signal_time = datetime.now()
            
    async def _check_exit_conditions(self, position, current_price: float, momentum: float):
        """检查平仓条件"""
        entry_price = position.entry_price
        pnl_ratio = 0.0
        
        if position.side == PositionSide.LONG:
            pnl_ratio = (current_price - entry_price) / entry_price
        else:
            pnl_ratio = (entry_price - current_price) / entry_price
            
        # 检查止损和止盈
        should_exit = False
        exit_reason = ""
        
        if pnl_ratio <= -self.stop_loss:
            should_exit = True
            exit_reason = "止损"
        elif pnl_ratio >= self.take_profit:
            should_exit = True
            exit_reason = "止盈"
        elif self._is_momentum_reversal(position.side, momentum):
            should_exit = True
            exit_reason = "动量反转"
            
        if should_exit:
            # 平仓
            order = self._create_order(
                market_id=self.market_id,
                side="sell" if position.side == PositionSide.LONG else "buy",
                order_type="market",
                size=position.size,
                price=current_price
            )
            
            if order:
                self._log_signal("EXIT", self.market_id, 
                               reason=exit_reason, pnl_ratio=pnl_ratio, momentum=momentum)
                self.last_signal_time = datetime.now()
                
    def _is_momentum_reversal(self, position_side, momentum: float) -> bool:
        """检查动量是否反转"""
        if position_side == PositionSide.LONG:
            return momentum < -self.momentum_threshold * 0.5
        else:
            return momentum > self.momentum_threshold * 0.5
            
    def get_strategy_params(self) -> Dict[str, Any]:
        """获取策略参数"""
        return {
            "market_id": self.market_id,
            "short_period": self.short_period,
            "long_period": self.long_period,
            "momentum_threshold": self.momentum_threshold,
            "position_size": self.position_size,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "signal_cooldown": self.signal_cooldown.total_seconds()
        }
