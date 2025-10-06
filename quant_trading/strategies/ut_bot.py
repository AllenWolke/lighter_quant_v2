"""
UT Bot策略
基于TradingView UT Bot Alerts的ATR追踪止损策略
"""

import logging
from typing import Dict, List, Optional, Any
import numpy as np
from datetime import datetime, timedelta

from .base_strategy import BaseStrategy
from ..utils.config import Config
from ..utils.logger import setup_logger


class UTBotStrategy(BaseStrategy):
    """UT Bot策略 - 基于ATR追踪止损"""
    
    def __init__(self, config: Config, market_id: int = 0, 
                 key_value: float = 1.0, atr_period: int = 10, 
                 use_heikin_ashi: bool = False):
        """
        初始化UT Bot策略
        
        Args:
            config: 配置对象
            market_id: 市场ID
            key_value: 关键值，影响敏感度
            atr_period: ATR周期
            use_heikin_ashi: 是否使用Heikin Ashi蜡烛图
        """
        super().__init__("UTBot", config)
        
        self.market_id = market_id
        self.key_value = key_value
        self.atr_period = atr_period
        self.use_heikin_ashi = use_heikin_ashi
        
        # 策略参数
        self.position_size = 0.1
        self.stop_loss = 0.02
        self.take_profit = 0.01
        
        # 状态变量
        self.xATRTrailingStop = 0.0
        self.pos = 0  # 0: 无仓位, 1: 多头, -1: 空头
        self.last_signal_time = None
        self.signal_cooldown = 300  # 5分钟冷却时间
        
        # 历史数据缓存
        self.price_history = []
        self.atr_history = []
        
    async def on_initialize(self):
        """策略初始化"""
        self.logger.info(f"初始化UT Bot策略: 市场 {self.market_id}, 关键值 {self.key_value}, ATR周期 {self.atr_period}")
        
    async def on_start(self):
        """策略启动"""
        self.logger.info("UT Bot策略已启动")
        
    async def on_stop(self):
        """策略停止"""
        self.logger.info("UT Bot策略已停止")
        
    async def process_market_data(self, market_data: Dict[int, Dict[str, Any]]):
        """处理市场数据"""
        if self.market_id not in market_data:
            return
            
        market_data_info = market_data[self.market_id]
        candlesticks = market_data_info.get("candlesticks", [])
        
        if len(candlesticks) < self.atr_period + 1:
            return
            
        # 获取当前价格
        current_price = self._get_current_price(candlesticks)
        if current_price is None:
            return
            
        # 更新价格历史
        self.price_history.append(current_price)
        if len(self.price_history) > self.atr_period + 10:
            self.price_history.pop(0)
            
        # 计算ATR
        atr = self._calculate_atr()
        if atr is None:
            return
            
        # 计算追踪止损
        self._update_trailing_stop(current_price, atr)
        
        # 检查信号冷却
        current_time = datetime.now().timestamp()
        if (self.last_signal_time and 
            current_time - self.last_signal_time < self.signal_cooldown):
            return
            
        # 生成交易信号
        await self._generate_signal(current_price)
        
    def _get_current_price(self, candlesticks: List[Dict[str, Any]]) -> Optional[float]:
        """获取当前价格"""
        if not candlesticks:
            return None
            
        if self.use_heikin_ashi:
            # 使用Heikin Ashi价格
            return self._calculate_heikin_ashi_close(candlesticks[-1])
        else:
            # 使用普通收盘价
            return candlesticks[-1]["close"]
            
    def _calculate_heikin_ashi_close(self, candle: Dict[str, Any]) -> float:
        """计算Heikin Ashi收盘价"""
        # 简化的Heikin Ashi计算
        # 实际应用中需要更复杂的计算
        return (candle["open"] + candle["high"] + candle["low"] + candle["close"]) / 4
        
    def _calculate_atr(self) -> Optional[float]:
        """计算ATR"""
        if len(self.price_history) < self.atr_period + 1:
            return None
            
        # 计算真实波幅
        true_ranges = []
        for i in range(1, len(self.price_history)):
            high = self.price_history[i]
            low = self.price_history[i-1]
            close_prev = self.price_history[i-1]
            
            tr1 = high - low
            tr2 = abs(high - close_prev)
            tr3 = abs(low - close_prev)
            
            true_ranges.append(max(tr1, tr2, tr3))
            
        if len(true_ranges) < self.atr_period:
            return None
            
        # 计算ATR
        atr = np.mean(true_ranges[-self.atr_period:])
        self.atr_history.append(atr)
        
        return atr
        
    def _update_trailing_stop(self, current_price: float, atr: float):
        """更新追踪止损"""
        nLoss = self.key_value * atr
        
        if self.xATRTrailingStop == 0:
            # 初始化追踪止损
            self.xATRTrailingStop = current_price - nLoss if current_price > 0 else current_price + nLoss
        else:
            # 更新追踪止损
            if (current_price > self.xATRTrailingStop and 
                self.price_history[-2] > self.xATRTrailingStop):
                # 价格在止损线上方且继续上涨
                self.xATRTrailingStop = max(self.xATRTrailingStop, current_price - nLoss)
            elif (current_price < self.xATRTrailingStop and 
                  self.price_history[-2] < self.xATRTrailingStop):
                # 价格在止损线下方且继续下跌
                self.xATRTrailingStop = min(self.xATRTrailingStop, current_price + nLoss)
            elif current_price > self.xATRTrailingStop:
                # 价格从下方突破止损线
                self.xATRTrailingStop = current_price - nLoss
            else:
                # 价格从上方跌破止损线
                self.xATRTrailingStop = current_price + nLoss
                
    async def _generate_signal(self, current_price: float):
        """生成交易信号"""
        # 更新仓位状态
        prev_pos = self.pos
        
        if (self.price_history[-2] < self.xATRTrailingStop and 
            current_price > self.xATRTrailingStop):
            self.pos = 1  # 多头信号
        elif (self.price_history[-2] > self.xATRTrailingStop and 
              current_price < self.xATRTrailingStop):
            self.pos = -1  # 空头信号
        else:
            self.pos = prev_pos
            
        # 检查是否需要开仓或平仓
        if self.pos != prev_pos:
            await self._handle_position_change(current_price, prev_pos, self.pos)
            
    async def _handle_position_change(self, current_price: float, prev_pos: int, new_pos: int):
        """处理仓位变化"""
        # 检查是否已有仓位
        position = self._get_position(self.market_id)
        
        if new_pos == 1 and prev_pos != 1:
            # 多头信号
            if position and position.side.value == "short":
                # 平空仓
                await self._close_position(current_price, "多头信号平空")
            # 开多仓
            await self._open_long_position(current_price)
            
        elif new_pos == -1 and prev_pos != -1:
            # 空头信号
            if position and position.side.value == "long":
                # 平多仓
                await self._close_position(current_price, "空头信号平多")
            # 开空仓
            await self._open_short_position(current_price)
            
    async def _open_long_position(self, price: float):
        """开多仓"""
        if not self._check_risk_limits(self.market_id, self.position_size, price):
            return
            
        order = self._create_order(
            market_id=self.market_id,
            side="buy",
            order_type="market",
            size=self.position_size,
            price=price
        )
        
        if order:
            self._log_signal("LONG", self.market_id, 
                           price=price, trailing_stop=self.xATRTrailingStop, size=self.position_size)
            self.last_signal_time = datetime.now().timestamp()
            
    async def _open_short_position(self, price: float):
        """开空仓"""
        if not self._check_risk_limits(self.market_id, self.position_size, price):
            return
            
        order = self._create_order(
            market_id=self.market_id,
            side="sell",
            order_type="market",
            size=self.position_size,
            price=price
        )
        
        if order:
            self._log_signal("SHORT", self.market_id, 
                           price=price, trailing_stop=self.xATRTrailingStop, size=self.position_size)
            self.last_signal_time = datetime.now().timestamp()
            
    async def _close_position(self, price: float, reason: str):
        """平仓"""
        position = self._get_position(self.market_id)
        if not position:
            return
            
        from ..core.position_manager import PositionSide
        
        order = self._create_order(
            market_id=self.market_id,
            side="sell" if position.side == PositionSide.LONG else "buy",
            order_type="market",
            size=position.size,
            price=price
        )
        
        if order:
            self._log_signal("EXIT", self.market_id, 
                           reason=reason, price=price, trailing_stop=self.xATRTrailingStop)
            self.last_signal_time = datetime.now().timestamp()
            
    def get_strategy_params(self) -> Dict[str, Any]:
        """获取策略参数"""
        return {
            "market_id": self.market_id,
            "key_value": self.key_value,
            "atr_period": self.atr_period,
            "use_heikin_ashi": self.use_heikin_ashi,
            "position_size": self.position_size,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "signal_cooldown": self.signal_cooldown,
            "current_trailing_stop": self.xATRTrailingStop,
            "current_position": self.pos
        }
