"""
UT Bot策略
基于UT Bot Alerts指标的量化交易策略
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from .base_strategy import BaseStrategy
from ..utils.config import Config
from ..utils.logger import setup_logger


class SignalType(Enum):
    """信号类型"""
    BUY = "buy"
    SELL = "sell"
    CLOSE_BUY = "close_buy"
    CLOSE_SELL = "close_sell"
    NONE = "none"


@dataclass
class UTBotConfig:
    """UT Bot策略配置"""
    # UT Bot Alerts参数
    key_value: float = 3.0  # 关键值，控制止损距离
    atr_period: int = 1     # ATR周期
    use_heikin_ashi: bool = False  # 是否使用Heikin Ashi蜡烛图
    
    # 趋势过滤参数
    ema_length: int = 200   # EMA长度
    
    # 风险管理参数
    risk_per_trade: float = 2.5  # 每笔交易风险百分比
    atr_multiplier: float = 1.5  # ATR止损倍数
    risk_reward_breakeven: float = 0.75  # 保本盈亏比
    risk_reward_takeprofit: float = 3.0  # 止盈盈亏比
    tp_percent: float = 50.0  # 第一批止盈百分比
    
    # 止损类型
    stoploss_type: str = "atr"  # "atr" 或 "swing"
    swing_high_bars: int = 10   # 摆动高点周期
    swing_low_bars: int = 10    # 摆动低点周期
    
    # 仓位管理
    enable_long: bool = True    # 允许做多
    enable_short: bool = True   # 允许做空
    use_takeprofit: bool = True # 使用止盈
    use_leverage: bool = True   # 使用杠杆
    
    # 时间过滤
    trading_start_time: str = "00:00"  # 交易开始时间
    trading_end_time: str = "23:59"    # 交易结束时间


class UTBotStrategy(BaseStrategy):
    """UT Bot策略"""
    
    def __init__(self, name: str, config: Config, ut_config: UTBotConfig = None):
        """
        初始化UT Bot策略
        
        Args:
            name: 策略名称
            config: 系统配置
            ut_config: UT Bot策略配置
        """
        super().__init__(name, config)
        
        # 策略配置
        self.ut_config = ut_config or UTBotConfig()
        
        # 策略状态
        self.market_data_history = {}  # 市场数据历史
        self.positions = {}  # 当前仓位
        self.stop_losses = {}  # 止损价格
        self.take_profits = {}  # 止盈价格
        self.breakevens = {}  # 保本价格
        
        # 指标缓存
        self.atr_trailing_stops = {}  # ATR动态止损线
        self.emas = {}  # EMA值
        self.atrs = {}  # ATR值
        
        # 交易统计
        self.signals_generated = 0
        self.trades_executed = 0
        
    async def on_initialize(self):
        """策略初始化"""
        self.logger.info("初始化UT Bot策略")
        self.logger.info(f"策略配置: {self.ut_config}")
        
    async def on_start(self):
        """策略启动"""
        self.logger.info("启动UT Bot策略")
        
    async def on_stop(self):
        """策略停止"""
        self.logger.info("停止UT Bot策略")
        
    async def process_market_data(self, market_data: Dict[int, Dict[str, Any]]):
        """
        处理市场数据
        
        Args:
            market_data: 市场数据字典，key为market_id，value为市场数据
        """
        for market_id, data in market_data.items():
            try:
                await self._process_single_market(market_id, data)
            except Exception as e:
                self.logger.error(f"处理市场 {market_id} 数据失败: {e}")
                
    async def _process_single_market(self, market_id: int, data: Dict[str, Any]):
        """处理单个市场的数据"""
        # 更新市场数据历史
        self._update_market_data_history(market_id, data)
        
        # 检查是否有足够的历史数据
        if len(self.market_data_history.get(market_id, [])) < max(self.ut_config.ema_length, 20):
            return
            
        # 计算技术指标
        self._calculate_indicators(market_id)
        
        # 生成交易信号
        signal = self._generate_signal(market_id)
        
        # 执行交易逻辑
        if signal != SignalType.NONE:
            await self._execute_trading_logic(market_id, signal)
            
    def _update_market_data_history(self, market_id: int, data: Dict[str, Any]):
        """更新市场数据历史"""
        if market_id not in self.market_data_history:
            self.market_data_history[market_id] = []
            
        # 添加新的数据点
        self.market_data_history[market_id].append({
            'timestamp': datetime.now(),
            'open': float(data.get('open', 0)),
            'high': float(data.get('high', 0)),
            'low': float(data.get('low', 0)),
            'close': float(data.get('close', 0)),
            'volume': float(data.get('volume', 0))
        })
        
        # 保持历史数据长度（保留最近1000个数据点）
        if len(self.market_data_history[market_id]) > 1000:
            self.market_data_history[market_id] = self.market_data_history[market_id][-1000:]
            
    def _calculate_indicators(self, market_id: int):
        """计算技术指标"""
        if market_id not in self.market_data_history:
            return
            
        data = self.market_data_history[market_id]
        df = pd.DataFrame(data)
        
        # 计算ATR
        self.atrs[market_id] = self._calculate_atr(df, self.ut_config.atr_period)
        
        # 计算EMA
        self.emas[market_id] = self._calculate_ema(df, self.ut_config.ema_length)
        
        # 计算UT Bot Alerts指标
        self._calculate_ut_bot_indicators(market_id, df)
        
    def _calculate_atr(self, df: pd.DataFrame, period: int) -> float:
        """计算ATR"""
        if len(df) < period + 1:
            return 0.0
            
        high = df['high'].values
        low = df['low'].values
        close = df['close'].values
        
        # 计算真实波幅
        tr1 = high[1:] - low[1:]
        tr2 = np.abs(high[1:] - close[:-1])
        tr3 = np.abs(low[1:] - close[:-1])
        
        true_range = np.maximum(tr1, np.maximum(tr2, tr3))
        
        # 计算ATR
        atr = np.mean(true_range[-period:])
        return atr
        
    def _calculate_ema(self, df: pd.DataFrame, period: int) -> float:
        """计算EMA"""
        if len(df) < period:
            return df['close'].iloc[-1]
            
        close = df['close'].values
        alpha = 2.0 / (period + 1)
        ema = close[0]
        
        for price in close[1:]:
            ema = alpha * price + (1 - alpha) * ema
            
        return ema
        
    def _calculate_ut_bot_indicators(self, market_id: int, df: pd.DataFrame):
        """计算UT Bot Alerts指标"""
        if market_id not in self.atrs or self.atrs[market_id] == 0:
            return
            
        # 获取当前价格
        current_close = df['close'].iloc[-1]
        atr = self.atrs[market_id]
        key_value = self.ut_config.key_value
        
        # 计算止损距离
        n_loss = key_value * atr
        
        # 计算ATR动态止损线
        if market_id not in self.atr_trailing_stops:
            self.atr_trailing_stops[market_id] = current_close
            
        prev_trailing_stop = self.atr_trailing_stops[market_id]
        
        # UT Bot Alerts逻辑
        if current_close > prev_trailing_stop:
            if prev_trailing_stop > 0:
                self.atr_trailing_stops[market_id] = max(prev_trailing_stop, current_close - n_loss)
            else:
                self.atr_trailing_stops[market_id] = current_close - n_loss
        else:
            if prev_trailing_stop > 0 and current_close < prev_trailing_stop:
                self.atr_trailing_stops[market_id] = min(prev_trailing_stop, current_close + n_loss)
            else:
                self.atr_trailing_stops[market_id] = current_close + n_loss
                
    def _generate_signal(self, market_id: int) -> SignalType:
        """生成交易信号"""
        if market_id not in self.market_data_history:
            return SignalType.NONE
            
        data = self.market_data_history[market_id]
        current_close = data[-1]['close']
        current_high = data[-1]['high']
        current_low = data[-1]['low']
        
        # 检查是否有足够的指标数据
        if (market_id not in self.atr_trailing_stops or 
            market_id not in self.emas or 
            market_id not in self.atrs):
            return SignalType.NONE
            
        atr_trailing_stop = self.atr_trailing_stops[market_id]
        ema = self.emas[market_id]
        
        # 趋势判断
        is_bullish = current_close > ema
        is_bearish = current_close < ema
        
        # 检查是否有前一个数据点
        if len(data) < 2:
            return SignalType.NONE
            
        prev_close = data[-2]['close']
        prev_high = data[-2]['high']
        prev_low = data[-2]['low']
        
        # 计算EMA_UT（1周期EMA）
        ema_ut = current_close  # 简化为当前价格
        
        # 计算交叉信号
        above_crossover = prev_close <= atr_trailing_stop and current_close > atr_trailing_stop
        below_crossover = prev_close >= atr_trailing_stop and current_close < atr_trailing_stop
        
        # 生成信号
        if current_close > atr_trailing_stop and above_crossover and is_bullish:
            return SignalType.BUY
        elif current_close < atr_trailing_stop and below_crossover and is_bearish:
            return SignalType.SELL
        elif current_close < atr_trailing_stop and below_crossover and is_bullish:
            return SignalType.CLOSE_BUY
        elif current_close > atr_trailing_stop and above_crossover and is_bearish:
            return SignalType.CLOSE_SELL
            
        return SignalType.NONE
        
    async def _execute_trading_logic(self, market_id: int, signal: SignalType):
        """执行交易逻辑"""
        self.signals_generated += 1
        self._log_signal(signal.value, market_id)
        
        # 获取当前仓位
        position = self._get_position(market_id)
        
        # 根据信号执行相应操作
        if signal == SignalType.BUY and self.ut_config.enable_long:
            await self._handle_buy_signal(market_id)
        elif signal == SignalType.SELL and self.ut_config.enable_short:
            await self._handle_sell_signal(market_id)
        elif signal == SignalType.CLOSE_BUY and position and position.side.value == "long":
            await self._handle_close_long_signal(market_id)
        elif signal == SignalType.CLOSE_SELL and position and position.side.value == "short":
            await self._handle_close_short_signal(market_id)
            
    async def _handle_buy_signal(self, market_id: int):
        """处理买入信号"""
        # 检查是否已有仓位
        position = self._get_position(market_id)
        if position and position.size > 0:
            return
            
        # 计算仓位大小
        size = self._calculate_position_size(market_id, "buy")
        if size <= 0:
            return
            
        # 计算止损和止盈价格
        stop_loss, take_profit, breakeven = self._calculate_stop_and_target(market_id, "buy")
        
        # 创建订单
        order = self._create_order(
            market_id=market_id,
            side="buy",
            order_type="market",
            size=size,
            price=0,  # 市价单
            leverage=1.0 if not self.ut_config.use_leverage else 2.0
        )
        
        if order:
            # 记录止损和止盈价格
            self.stop_losses[market_id] = stop_loss
            if self.ut_config.use_takeprofit:
                self.take_profits[market_id] = take_profit
            self.breakevens[market_id] = breakeven
            
            self.trades_executed += 1
            self.logger.info(f"执行买入订单: 市场{market_id}, 数量{size}, 止损{stop_loss}, 止盈{take_profit}")
            
    async def _handle_sell_signal(self, market_id: int):
        """处理卖出信号"""
        # 检查是否已有仓位
        position = self._get_position(market_id)
        if position and position.size < 0:
            return
            
        # 计算仓位大小
        size = self._calculate_position_size(market_id, "sell")
        if size <= 0:
            return
            
        # 计算止损和止盈价格
        stop_loss, take_profit, breakeven = self._calculate_stop_and_target(market_id, "sell")
        
        # 创建订单
        order = self._create_order(
            market_id=market_id,
            side="sell",
            order_type="market",
            size=size,
            price=0,  # 市价单
            leverage=1.0 if not self.ut_config.use_leverage else 2.0
        )
        
        if order:
            # 记录止损和止盈价格
            self.stop_losses[market_id] = stop_loss
            if self.ut_config.use_takeprofit:
                self.take_profits[market_id] = take_profit
            self.breakevens[market_id] = breakeven
            
            self.trades_executed += 1
            self.logger.info(f"执行卖出订单: 市场{market_id}, 数量{size}, 止损{stop_loss}, 止盈{take_profit}")
            
    async def _handle_close_long_signal(self, market_id: int):
        """处理平多信号"""
        position = self._get_position(market_id)
        if not position or position.size <= 0:
            return
            
        # 检查是否有盈利
        if position.unrealized_pnl <= 0:
            return
            
        # 平仓
        order = self._create_order(
            market_id=market_id,
            side="sell",
            order_type="market",
            size=position.size,
            price=0
        )
        
        if order:
            self.logger.info(f"平多仓位: 市场{market_id}")
            
    async def _handle_close_short_signal(self, market_id: int):
        """处理平空信号"""
        position = self._get_position(market_id)
        if not position or position.size >= 0:
            return
            
        # 检查是否有盈利
        if position.unrealized_pnl <= 0:
            return
            
        # 平仓
        order = self._create_order(
            market_id=market_id,
            side="buy",
            order_type="market",
            size=abs(position.size),
            price=0
        )
        
        if order:
            self.logger.info(f"平空仓位: 市场{market_id}")
            
    def _calculate_position_size(self, market_id: int, side: str) -> float:
        """计算仓位大小"""
        if market_id not in self.market_data_history:
            return 0.0
            
        current_price = self.market_data_history[market_id][-1]['close']
        
        # 获取账户资金
        if not self.engine:
            return 0.0
            
        account_balance = 10000.0  # 假设账户余额，实际应从引擎获取
        
        # 计算风险金额
        risk_amount = account_balance * (self.ut_config.risk_per_trade / 100)
        
        # 计算止损距离
        stop_loss = self._calculate_stop_loss_price(market_id, side)
        if stop_loss is None:
            return 0.0
            
        if side == "buy":
            stop_distance = (current_price - stop_loss) / current_price
        else:
            stop_distance = (stop_loss - current_price) / current_price
            
        if stop_distance <= 0:
            return 0.0
            
        # 计算仓位大小
        position_size = risk_amount / (stop_distance * current_price)
        
        # 检查杠杆限制
        if not self.ut_config.use_leverage:
            max_size = account_balance / current_price
            position_size = min(position_size, max_size)
            
        return position_size
        
    def _calculate_stop_loss_price(self, market_id: int, side: str) -> Optional[float]:
        """计算止损价格"""
        if market_id not in self.market_data_history:
            return None
            
        current_price = self.market_data_history[market_id][-1]['close']
        
        if self.ut_config.stoploss_type == "atr":
            # ATR止损
            if market_id not in self.atrs or self.atrs[market_id] == 0:
                return None
                
            atr = self.atrs[market_id]
            multiplier = self.ut_config.atr_multiplier
            
            if side == "buy":
                return current_price - (atr * multiplier)
            else:
                return current_price + (atr * multiplier)
                
        elif self.ut_config.stoploss_type == "swing":
            # 摆动高低点止损
            data = self.market_data_history[market_id]
            high_bars = self.ut_config.swing_high_bars
            low_bars = self.ut_config.swing_low_bars
            
            if len(data) < max(high_bars, low_bars):
                return None
                
            recent_highs = [d['high'] for d in data[-high_bars:]]
            recent_lows = [d['low'] for d in data[-low_bars:]]
            
            if side == "buy":
                return min(recent_lows)
            else:
                return max(recent_highs)
                
        return None
        
    def _calculate_stop_and_target(self, market_id: int, side: str) -> Tuple[float, Optional[float], float]:
        """计算止损、止盈和保本价格"""
        current_price = self.market_data_history[market_id][-1]['close']
        stop_loss = self._calculate_stop_loss_price(market_id, side)
        
        if stop_loss is None:
            return current_price, None, current_price
            
        # 计算风险距离
        if side == "buy":
            risk_distance = current_price - stop_loss
            breakeven = current_price + risk_distance * self.ut_config.risk_reward_breakeven
            take_profit = current_price + risk_distance * self.ut_config.risk_reward_takeprofit
        else:
            risk_distance = stop_loss - current_price
            breakeven = current_price - risk_distance * self.ut_config.risk_reward_breakeven
            take_profit = current_price - risk_distance * self.ut_config.risk_reward_takeprofit
            
        return stop_loss, take_profit, breakeven
        
    def get_strategy_status(self) -> Dict[str, Any]:
        """获取策略状态"""
        base_status = self.get_status()
        base_status.update({
            "ut_config": self.ut_config.__dict__,
            "signals_generated": self.signals_generated,
            "trades_executed": self.trades_executed,
            "active_markets": list(self.market_data_history.keys()),
            "current_positions": len(self.positions),
            "stop_losses": self.stop_losses,
            "take_profits": self.take_profits
        })
        return base_status
