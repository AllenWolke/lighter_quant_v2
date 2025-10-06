"""
均值回归策略
基于价格偏离均值的策略
"""

import logging
from typing import Dict, List, Optional, Any
import numpy as np
from datetime import datetime, timedelta

from .base_strategy import BaseStrategy
from ..utils.config import Config
from ..utils.logger import setup_logger


class MeanReversionStrategy(BaseStrategy):
    """均值回归策略"""
    
    def __init__(self, config: Config, market_id: int = 0, 
                 lookback_period: int = 20, threshold: float = 2.0):
        """
        初始化均值回归策略
        
        Args:
            config: 配置对象
            market_id: 市场ID
            lookback_period: 回望周期
            threshold: 阈值倍数
        """
        super().__init__("MeanReversion", config)
        
        self.market_id = market_id
        self.lookback_period = lookback_period
        self.threshold = threshold
        
        # 策略参数
        self.position_size = 0.1  # 仓位大小
        self.stop_loss = 0.02     # 止损比例
        self.take_profit = 0.01   # 止盈比例
        
        # 状态变量
        self.last_signal_time = None
        self.signal_cooldown = timedelta(minutes=5)  # 信号冷却时间
        
    async def on_initialize(self):
        """策略初始化"""
        self.logger.info(f"初始化均值回归策略: 市场 {self.market_id}, 回望周期 {self.lookback_period}, 阈值 {self.threshold}")
        
    async def on_start(self):
        """策略启动"""
        self.logger.info("均值回归策略已启动")
        
    async def on_stop(self):
        """策略停止"""
        self.logger.info("均值回归策略已停止")
        
    async def process_market_data(self, market_data: Dict[int, Dict[str, Any]]):
        """处理市场数据"""
        if self.market_id not in market_data:
            return
            
        market_data_info = market_data[self.market_id]
        candlesticks = market_data_info.get("candlesticks", [])
        
        if len(candlesticks) < self.lookback_period:
            return
            
        # 获取当前价格
        current_price = self._get_current_price(candlesticks)
        if current_price is None:
            return
            
        # 计算均值和标准差
        prices = [c["close"] for c in candlesticks[-self.lookback_period:]]
        mean_price = np.mean(prices)
        std_price = np.std(prices)
        
        if std_price == 0:
            return
            
        # 计算Z分数
        z_score = (current_price - mean_price) / std_price
        
        # 检查信号冷却
        if (self.last_signal_time and 
            datetime.now() - self.last_signal_time < self.signal_cooldown):
            return
            
        # 生成交易信号
        await self._generate_signal(current_price, z_score, mean_price)
        
    def _get_current_price(self, candlesticks: List[Dict[str, Any]]) -> Optional[float]:
        """获取当前价格"""
        if not candlesticks:
            return None
            
        # 使用最新K线的收盘价
        return candlesticks[-1]["close"]
        
    async def _generate_signal(self, current_price: float, z_score: float, mean_price: float):
        """生成交易信号"""
        # 检查是否已有仓位
        position = self._get_position(self.market_id)
        
        if position:
            # 已有仓位，检查是否需要平仓
            await self._check_exit_conditions(position, current_price)
        else:
            # 没有仓位，检查是否需要开仓
            if z_score > self.threshold:
                # 价格过高，做空
                await self._open_short_position(current_price, z_score)
            elif z_score < -self.threshold:
                # 价格过低，做多
                await self._open_long_position(current_price, z_score)
                
    async def _open_long_position(self, price: float, z_score: float):
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
                           price=price, z_score=z_score, size=self.position_size)
            self.last_signal_time = datetime.now()
            
    async def _open_short_position(self, price: float, z_score: float):
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
                           price=price, z_score=z_score, size=self.position_size)
            self.last_signal_time = datetime.now()
            
    async def _check_exit_conditions(self, position, current_price: float):
        """检查平仓条件"""
        from ..core.position_manager import PositionSide
        
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
                               reason=exit_reason, pnl_ratio=pnl_ratio)
                self.last_signal_time = datetime.now()
                
    def get_strategy_params(self) -> Dict[str, Any]:
        """获取策略参数"""
        return {
            "market_id": self.market_id,
            "lookback_period": self.lookback_period,
            "threshold": self.threshold,
            "position_size": self.position_size,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "signal_cooldown": self.signal_cooldown.total_seconds()
        }
