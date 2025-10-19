"""
套利策略
基于价格差异的套利策略
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from datetime import datetime, timedelta

from .base_strategy import BaseStrategy
from ..utils.config import Config
from ..utils.logger import setup_logger


class ArbitrageStrategy(BaseStrategy):
    """套利策略"""
    
    def __init__(self, config: Config, market_id_1: int = 0, market_id_2: int = 1,
                 price_threshold: float = 0.01, max_position_size: float = 0.05,
                 position_size: float = None,
                 stop_loss: float = None,
                 take_profit: float = None):
        """
        初始化套利策略
        
        Args:
            config: 配置对象
            market_id_1: 第一个市场ID
            market_id_2: 第二个市场ID
            price_threshold: 价格差异阈值
            max_position_size: 最大仓位大小
            position_size: 仓位大小（如果为None，从config读取）
            stop_loss: 止损比例（如果为None，从config读取）
            take_profit: 止盈比例（如果为None，从config读取）
        """
        super().__init__("Arbitrage", config)
        
        self.market_id_1 = market_id_1
        self.market_id_2 = market_id_2
        self.price_threshold = price_threshold
        self.max_position_size = max_position_size
        
        # 策略参数 - 优先使用传入的参数，否则从config读取
        arb_config = config.strategies.get('arbitrage', {}) if hasattr(config, 'strategies') else {}
        self.position_size_usd = position_size if position_size is not None else arb_config.get('position_size', 10.0)  # 改为USD金额
        self.stop_loss = stop_loss if stop_loss is not None else arb_config.get('stop_loss', 0.005)
        self.take_profit = take_profit if take_profit is not None else arb_config.get('take_profit', 0.01)
        
        # ⭐ 需求①：K线类型配置
        self.kline_types = arb_config.get('kline_types', [1])  # 默认只对1分钟K线发出信号
        self.logger.info(f"K线类型配置: {self.kline_types}分钟 - 策略将对这些时间周期的K线发出交易信号")
        
        self.logger.info(f"策略配置: position_size=${self.position_size_usd} USD (将根据市场价格自动计算加密货币数量)")
        
        # 状态变量
        self.last_signal_time = None
        self.signal_cooldown = timedelta(minutes=2)  # 信号冷却时间
        self.arbitrage_positions = {}  # 套利仓位记录
        
    async def on_initialize(self):
        """策略初始化"""
        self.logger.info(f"初始化套利策略: 市场 {self.market_id_1} vs {self.market_id_2}, 阈值 {self.price_threshold}")
        
    async def on_start(self):
        """策略启动"""
        self.logger.info("套利策略已启动")
        
    async def on_stop(self):
        """策略停止"""
        self.logger.info("套利策略已停止")
        
    async def process_market_data(self, market_data: Dict[int, Dict[str, Any]]):
        """处理市场数据"""
        # 检查两个市场的数据是否都可用
        if (self.market_id_1 not in market_data or 
            self.market_id_2 not in market_data):
            return
            
        market_data_1 = market_data[self.market_id_1]
        market_data_2 = market_data[self.market_id_2]
        
        # 获取当前价格
        price_1 = self._get_current_price(market_data_1)
        price_2 = self._get_current_price(market_data_2)
        
        if price_1 is None or price_2 is None:
            return
            
        # 计算价格差异
        price_diff = self._calculate_price_difference(price_1, price_2)
        
        # 检查信号冷却
        if (self.last_signal_time and 
            datetime.now() - self.last_signal_time < self.signal_cooldown):
            return
            
        # 生成套利信号
        await self._generate_arbitrage_signal(price_1, price_2, price_diff)
        
    def _get_current_price(self, market_data: Dict[str, Any]) -> Optional[float]:
        """获取当前价格"""
        candlesticks = market_data.get("candlesticks", [])
        if not candlesticks:
            return None
            
        return candlesticks[-1]["close"]
        
    def _calculate_price_difference(self, price_1: float, price_2: float) -> float:
        """计算价格差异"""
        if price_2 == 0:
            return 0
            
        return (price_1 - price_2) / price_2
        
    async def _generate_arbitrage_signal(self, price_1: float, price_2: float, price_diff: float):
        """生成套利信号"""
        # 检查是否已有套利仓位
        arbitrage_id = f"{self.market_id_1}_{self.market_id_2}"
        
        if arbitrage_id in self.arbitrage_positions:
            # 已有套利仓位，检查是否需要平仓
            await self._check_arbitrage_exit(arbitrage_id, price_1, price_2, price_diff)
        else:
            # 没有套利仓位，检查是否需要开仓
            if abs(price_diff) > self.price_threshold:
                await self._open_arbitrage_position(price_1, price_2, price_diff)
                
    async def _open_arbitrage_position(self, price_1: float, price_2: float, price_diff: float):
        """开套利仓位"""
        # 确定套利方向
        if price_diff > self.price_threshold:
            # 市场1价格高，市场2价格低
            # 在市场1做空，在市场2做多
            await self._execute_arbitrage_trades(
                short_market=self.market_id_1,
                long_market=self.market_id_2,
                short_price=price_1,
                long_price=price_2,
                price_diff=price_diff
            )
        elif price_diff < -self.price_threshold:
            # 市场1价格低，市场2价格高
            # 在市场1做多，在市场2做空
            await self._execute_arbitrage_trades(
                short_market=self.market_id_2,
                long_market=self.market_id_1,
                short_price=price_2,
                long_price=price_1,
                price_diff=abs(price_diff)
            )
            
    async def _execute_arbitrage_trades(self, short_market: int, long_market: int,
                                       short_price: float, long_price: float, price_diff: float):
        """执行套利交易"""
        try:
            # 将USD金额转换为实际的加密货币数量
            short_size = self.position_size_usd / short_price
            long_size = self.position_size_usd / long_price
            self.logger.info(f"套利开仓计算:")
            self.logger.info(f"  做空市场{short_market}: ${self.position_size_usd} USD ÷ ${short_price:.6f} = {short_size:.6f} 加密货币")
            self.logger.info(f"  做多市场{long_market}: ${self.position_size_usd} USD ÷ ${long_price:.6f} = {long_size:.6f} 加密货币")
            
            # 检查风险限制
            if not (self._check_risk_limits(short_market, short_size, short_price) and
                    self._check_risk_limits(long_market, long_size, long_price)):
                return
                
            # 创建做空订单
            short_order = self._create_order(
                market_id=short_market,
                side="sell",
                order_type="market",
                size=short_size,  # 使用计算后的实际数量
                price=short_price
            )
            
            # 创建做多订单
            long_order = self._create_order(
                market_id=long_market,
                side="buy",
                order_type="market",
                size=long_size,  # 使用计算后的实际数量
                price=long_price
            )
            
            if short_order and long_order:
                # 记录套利仓位
                arbitrage_id = f"{short_market}_{long_market}"
                self.arbitrage_positions[arbitrage_id] = {
                    "short_market": short_market,
                    "long_market": long_market,
                    "short_price": short_price,
                    "long_price": long_price,
                    "short_size": short_size,  # 记录实际数量
                    "long_size": long_size,  # 记录实际数量
                    "size_usd": self.position_size_usd,  # 记录USD金额
                    "entry_time": datetime.now(),
                    "price_diff": price_diff
                }
                
                self._log_signal("ARBITRAGE_OPEN", arbitrage_id,
                               short_market=short_market, long_market=long_market,
                               short_price=short_price, long_price=long_price,
                               price_diff=price_diff, size_usd=self.position_size_usd,
                               short_size=short_size, long_size=long_size)
                
                self.last_signal_time = datetime.now()
                
        except Exception as e:
            self.logger.error(f"执行套利交易失败: {e}")
            
    async def _check_arbitrage_exit(self, arbitrage_id: str, price_1: float, price_2: float, price_diff: float):
        """检查套利平仓条件"""
        position = self.arbitrage_positions[arbitrage_id]
        
        # 计算当前价格差异
        if position["short_market"] == self.market_id_1:
            current_price_diff = (price_1 - price_2) / price_2
        else:
            current_price_diff = (price_2 - price_1) / price_1
            
        # 计算盈亏
        pnl_ratio = (position["price_diff"] - abs(current_price_diff)) / position["price_diff"]
        
        # 检查平仓条件
        should_exit = False
        exit_reason = ""
        
        if pnl_ratio <= -self.stop_loss:
            should_exit = True
            exit_reason = "止损"
        elif pnl_ratio >= self.take_profit:
            should_exit = True
            exit_reason = "止盈"
        elif abs(current_price_diff) < self.price_threshold * 0.5:
            should_exit = True
            exit_reason = "价格收敛"
            
        if should_exit:
            await self._close_arbitrage_position(arbitrage_id, price_1, price_2, exit_reason)
            
    async def _close_arbitrage_position(self, arbitrage_id: str, price_1: float, price_2: float, reason: str):
        """平套利仓位"""
        try:
            position = self.arbitrage_positions[arbitrage_id]
            
            # 平仓做空仓位
            short_close_order = self._create_order(
                market_id=position["short_market"],
                side="buy",
                order_type="market",
                size=position["size"],
                price=price_1 if position["short_market"] == self.market_id_1 else price_2
            )
            
            # 平仓做多仓位
            long_close_order = self._create_order(
                market_id=position["long_market"],
                side="sell",
                order_type="market",
                size=position["size"],
                price=price_1 if position["long_market"] == self.market_id_1 else price_2
            )
            
            if short_close_order and long_close_order:
                # 计算实际盈亏
                if position["short_market"] == self.market_id_1:
                    pnl = (position["short_price"] - price_1) + (price_2 - position["long_price"])
                else:
                    pnl = (position["short_price"] - price_2) + (price_1 - position["long_price"])
                    
                # 记录交易
                self._record_trade(pnl)
                
                # 移除套利仓位记录
                del self.arbitrage_positions[arbitrage_id]
                
                self._log_signal("ARBITRAGE_CLOSE", arbitrage_id,
                               reason=reason, pnl=pnl)
                
        except Exception as e:
            self.logger.error(f"平套利仓位失败: {e}")
            
    def get_strategy_params(self) -> Dict[str, Any]:
        """获取策略参数"""
        return {
            "market_id_1": self.market_id_1,
            "market_id_2": self.market_id_2,
            "price_threshold": self.price_threshold,
            "max_position_size": self.max_position_size,
            "position_size_usd": self.position_size_usd,  # 现在使用USD金额
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "signal_cooldown": self.signal_cooldown.total_seconds(),
            "active_arbitrage_positions": len(self.arbitrage_positions)
        }
