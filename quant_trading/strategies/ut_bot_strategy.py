"""
UT Bot策略
基于UT Bot Alerts指标的量化交易策略
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
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
    
    # 实时tick配置
    real_time_tick_interval: float = 0.1  # 实时tick处理间隔（秒）
    
    # 订单配置
    position_size_usd: float = 1000.0  # 仓位大小(USD)
    leverage: float = 1.0              # 杠杆倍数
    margin_mode: str = "cross"         # 保证金模式: cross (全仓) 或 isolated (逐仓)
    order_type: str = "market"         # 订单类型: market (市价单) 或 limit (限价单)
    limit_price_offset: float = 0.001  # 限价单价格偏移 (0.1%)
    price_slippage_tolerance: float = 0.01  # 价格滑点容忍度 (1%)
    
    # 多市场配置
    market_ids: Optional[List[int]] = None       # 支持的市场ID列表
    
    # 时间周期确认配置
    enable_multi_timeframe: bool = False  # 启用多时间周期确认（调整为单周期）
    kline_types: List[int] = field(default_factory=lambda: [1])  # tick周期列表，1代表根据1tick的图来确认交易信号
    
    # 市场特定配置
    market_slippage_config: Optional[Dict[int, Dict[str, Any]]] = None  # 各市场滑点配置
    market_risk_config: Optional[Dict[int, Dict[str, Any]]] = None      # 各市场止盈止损配置


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
        
        # 策略配置 - 优先使用传入的ut_config，否则从config.yaml中读取
        if ut_config is not None:
            self.ut_config = ut_config
        else:
            # 从config.yaml中读取UT Bot配置
            self.ut_config = self._load_config_from_yaml()
        
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
        
        # 实时tick支持
        self.enable_real_time_ticks()  # 启用实时tick模式
        self.logger.info("✅ UT Bot策略已启用实时tick模式")
        
        # 实时价格数据
        self.current_prices: Dict[int, float] = {}
        self.last_price_updates: Dict[int, datetime] = {}
        
        # 多市场支持
        self.active_markets = self.ut_config.market_ids if self.ut_config.market_ids else [0]  # 默认市场0
        self.logger.info(f"UT Bot策略支持的市场: {self.active_markets}")
    
    def _load_config_from_yaml(self) -> UTBotConfig:
        """
        从config.yaml中加载UT Bot配置
        
        Returns:
            UTBotConfig: 从配置文件加载的配置对象
        """
        try:
            # 尝试从系统配置中获取UT Bot配置
            if hasattr(self.config, 'strategies') and 'ut_bot' in self.config.strategies:
                ut_bot_config_dict = self.config.strategies['ut_bot']
                
                # 创建UTBotConfig对象，使用配置文件中的值
                return UTBotConfig(
                    # UT Bot Alerts核心参数
                    key_value=ut_bot_config_dict.get('key_value', 3.0),
                    atr_period=ut_bot_config_dict.get('atr_period', 1),
                    use_heikin_ashi=ut_bot_config_dict.get('use_heikin_ashi', False),
                    ema_length=ut_bot_config_dict.get('ema_length', 200),
                    
                    # 风险管理参数
                    risk_per_trade=ut_bot_config_dict.get('risk_per_trade', 2.5),
                    atr_multiplier=ut_bot_config_dict.get('atr_multiplier', 1.5),
                    risk_reward_breakeven=ut_bot_config_dict.get('risk_reward_breakeven', 0.75),
                    risk_reward_takeprofit=ut_bot_config_dict.get('risk_reward_takeprofit', 3.0),
                    tp_percent=ut_bot_config_dict.get('tp_percent', 50.0),
                    
                    # 止损类型
                    stoploss_type=ut_bot_config_dict.get('stoploss_type', "atr"),
                    swing_high_bars=ut_bot_config_dict.get('swing_high_bars', 10),
                    swing_low_bars=ut_bot_config_dict.get('swing_low_bars', 10),
                    
                    # 仓位管理
                    enable_long=ut_bot_config_dict.get('enable_long', True),
                    enable_short=ut_bot_config_dict.get('enable_short', True),
                    use_takeprofit=ut_bot_config_dict.get('use_takeprofit', True),
                    use_leverage=ut_bot_config_dict.get('use_leverage', True),
                    
                    # 时间过滤
                    trading_start_time=ut_bot_config_dict.get('trading_start_time', "00:00"),
                    trading_end_time=ut_bot_config_dict.get('trading_end_time', "23:59"),
                    
                    # 实时tick配置
                    real_time_tick_interval=ut_bot_config_dict.get('real_time_tick_interval', 0.1),
                    
                    # 订单配置
                    position_size_usd=ut_bot_config_dict.get('position_size_usd', 1000.0),
                    leverage=ut_bot_config_dict.get('leverage', 1.0),
                    margin_mode=ut_bot_config_dict.get('margin_mode', "cross"),
                    order_type=ut_bot_config_dict.get('order_type', "market"),
                    limit_price_offset=ut_bot_config_dict.get('limit_price_offset', 0.001),
                    price_slippage_tolerance=ut_bot_config_dict.get('price_slippage_tolerance', 0.01),
                    
                    # 多市场配置
                    market_ids=ut_bot_config_dict.get('market_ids', None),
                    
                    # 时间周期确认配置
                    enable_multi_timeframe=ut_bot_config_dict.get('enable_multi_timeframe', False),
                    kline_types=ut_bot_config_dict.get('kline_types', [1]),
                    
                    # 市场特定配置
                    market_slippage_config=ut_bot_config_dict.get('market_slippage_config', None),
                    market_risk_config=ut_bot_config_dict.get('market_risk_config', None)
                )
            else:
                # 如果配置文件中没有找到UT Bot配置，使用默认值
                self.logger.warning("未找到config.yaml中的ut_bot配置，使用默认配置")
                return UTBotConfig()
                
        except Exception as e:
            self.logger.error(f"从config.yaml加载UT Bot配置失败: {e}")
            return UTBotConfig()
        
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
        处理市场数据 - 抽象方法实现
        注意：UT Bot策略使用实时tick模式，不处理K线数据
        """
        # UT Bot策略使用实时tick模式，不处理K线数据
        # 这避免了历史数据对交易信号的干扰
        self.logger.debug("UT Bot策略使用实时tick模式，跳过K线数据处理")
        pass
    
    async def process_real_time_tick(self, market_id: int, tick_data: Dict[str, Any]):
        """
        处理实时tick数据 - 类似Pine Script的calc_on_every_tick
        
        Args:
            market_id: 市场ID
            tick_data: tick数据，包含price, bid, ask, spread等
        """
        try:
            # 检查是否是支持的市场
            if market_id not in self.active_markets:
                return  # 跳过不支持的市场
            
            # 验证输入参数
            if not tick_data or not isinstance(tick_data, dict):
                self.logger.warning(f"无效的tick_data参数 (市场 {market_id}): {tick_data}")
                return
            
            if 'price' not in tick_data:
                self.logger.warning(f"tick_data缺少price字段 (市场 {market_id}): {tick_data}")
                return
            
            # 更新实时价格
            current_price = tick_data.get('price', 0)
            if current_price > 0:
                self.current_prices[market_id] = current_price
                self.last_price_updates[market_id] = datetime.now()
                
                # 构建简化的市场数据结构
                simplified_market_data = {
                    market_id: {
                        'last_price': current_price,
                        'last_tick': tick_data,
                        'timestamp': tick_data.get('timestamp', datetime.now().timestamp())
                    }
                }
                
                # 更新历史数据
                self._update_market_data_history(market_id, {
                    'timestamp': tick_data.get('timestamp', datetime.now().timestamp()),
                    'open': current_price,
                    'high': current_price,
                    'low': current_price,
                    'close': current_price,
                    'volume': 0
                })
                
                # 实时计算技术指标
                await self._calculate_real_time_indicators(market_id)
                
                # 实时生成交易信号
                await self._generate_real_time_signals(market_id, current_price)
                
                self.logger.debug(f"实时tick处理完成 (市场 {market_id}): 价格 {current_price}")
                
        except Exception as e:
            self.logger.error(f"实时tick处理失败 (市场 {market_id}): {e}")
    
    async def _calculate_real_time_indicators(self, market_id: int):
        """实时计算技术指标"""
        try:
            if market_id not in self.market_data_history:
                return
                
            data = self.market_data_history[market_id]
            if len(data) < max(self.ut_config.atr_period, self.ut_config.ema_length):
                return
            
            df = pd.DataFrame(data)
            
            # 计算ATR
            self.atrs[market_id] = self._calculate_atr(df, self.ut_config.atr_period)
            
            # 计算EMA
            self.emas[market_id] = self._calculate_ema(df, self.ut_config.ema_length)
            
            # 计算UT Bot Alerts指标
            self._calculate_ut_bot_indicators(market_id, df)
            
        except Exception as e:
            self.logger.error(f"实时指标计算失败 (市场 {market_id}): {e}")
    
    async def _generate_real_time_signals(self, market_id: int, current_price: float):
        """实时生成交易信号"""
        try:
            if market_id not in self.atr_trailing_stops:
                return
            
            # 检查是否在指定的tick周期内
            if not self._should_process_signal(market_id):
                return
                
            xATRTrailingStop = self.atr_trailing_stops[market_id]
            ema = self.emas.get(market_id, current_price)
            
            # 趋势判断
            bullish = current_price > ema
            bearish = current_price < ema
            
            # UT Bot信号判断
            if current_price > xATRTrailingStop and bullish:
                signal = SignalType.BUY
                self.logger.info(f"🔵 实时买入信号 (市场 {market_id}): 价格 {current_price} > 追踪止损 {xATRTrailingStop}")
            elif current_price < xATRTrailingStop and bearish:
                signal = SignalType.SELL
                self.logger.info(f"🔴 实时卖出信号 (市场 {market_id}): 价格 {current_price} < 追踪止损 {xATRTrailingStop}")
            else:
                signal = SignalType.NONE
            
            # 执行交易信号
            if signal != SignalType.NONE:
                await self._execute_signal(market_id, signal, current_price)
                
        except Exception as e:
            self.logger.error(f"实时信号生成失败 (市场 {market_id}): {e}")
    
    def _should_process_signal(self, market_id: int) -> bool:
        """检查是否应该处理交易信号（基于tick周期）"""
        try:
            # 获取配置的tick周期
            kline_types = getattr(self.ut_config, 'kline_types', [1])
            if not kline_types:
                return True  # 如果没有配置，默认每个tick都处理
            
            # 获取当前时间戳
            current_time = datetime.now().timestamp()
            
            # 检查是否在指定的tick周期内
            # 这里简化处理：根据tick周期间隔来决定是否处理信号
            tick_interval = getattr(self.ut_config, 'real_time_tick_interval', 0.1)
            
            # 初始化每个市场的tick计数器
            if not hasattr(self, '_tick_counters'):
                self._tick_counters = {}
            
            if market_id not in self._tick_counters:
                self._tick_counters[market_id] = 0
            
            self._tick_counters[market_id] += 1
            
            # 检查是否达到指定的tick周期
            # 如果tick计数能被任何配置的周期整除，则处理信号
            for tick_period in kline_types:
                if self._tick_counters[market_id] % tick_period == 0:
                    self.logger.debug(f"市场 {market_id} 达到tick周期 {tick_period}，处理信号")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"检查tick周期失败 (市场 {market_id}): {e}")
            return True  # 出错时默认处理
    
    async def _execute_signal(self, market_id: int, signal: SignalType, current_price: float):
        """
        执行交易信号 - 对应Pine Script的交易逻辑
        
        Args:
            market_id: 市场ID
            signal: 信号类型
            current_price: 当前价格
        """
        try:
            # 首先进行风险检查
            if not await self._check_risk_limits(market_id):
                self.logger.warning(f"市场 {market_id} 风险检查未通过，跳过交易信号")
                return
            
            self.signals_generated += 1
            self._log_signal(signal.value, market_id)
            
            # 更新仓位状态
            if hasattr(self, 'engine') and self.engine:
                await self.engine.position_manager.update_positions()
            
            # 获取当前仓位
            position = self._get_position(market_id)
            
            # 根据信号执行相应操作 - 对应Pine Script的交易逻辑
            if signal == SignalType.BUY and self.ut_config.enable_long:
                # 对应Pine Script: if not bought and buy and long_positions and bullish
                await self._handle_buy_signal(market_id)
                
            elif signal == SignalType.SELL and self.ut_config.enable_short:
                # 对应Pine Script: if not sold and sell and short_positions and bearish
                await self._handle_sell_signal(market_id)
                
            elif signal == SignalType.CLOSE_BUY and position and position.size > 0:
                # 对应Pine Script: if bought and sell and strategy.openprofit>0
                await self._handle_close_long_signal(market_id)
                
            elif signal == SignalType.CLOSE_SELL and position and position.size < 0:
                # 对应Pine Script: if sold and buy and strategy.openprofit>0
                await self._handle_close_short_signal(market_id)
                
        except Exception as e:
            self.logger.error(f"执行交易信号失败 (市场 {market_id}, 信号 {signal.value}): {e}")
    
    def _update_market_data_history(self, market_id: int, tick_data: Dict[str, Any]):
        """更新市场数据历史"""
        if market_id not in self.market_data_history:
            self.market_data_history[market_id] = []
            
        self.market_data_history[market_id].append(tick_data)
        
        # 保持历史数据长度（保留最近1000个数据点）
        if len(self.market_data_history[market_id]) > 1000:
            self.market_data_history[market_id] = self.market_data_history[market_id][-1000:]
                
                       
        
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
        
        # 获取当前价格用于滑点控制
        market_data = self.engine.data_manager.get_market_data(market_id)
        current_price = market_data.get('last_price', 0) if market_data else 0
        
        # 获取有效的滑点容忍度
        slippage_tolerance = self._get_effective_slippage_tolerance(market_id)
        
        # 创建订单（添加滑点控制）
        order = self._create_order(
            market_id=market_id,
            side="buy",
            order_type=self.ut_config.order_type,
            size=size,
            price=current_price,  # 使用当前价格进行滑点控制
            leverage=self.ut_config.leverage,
            margin_mode=self.ut_config.margin_mode,
            price_slippage_tolerance=slippage_tolerance,
            slippage_enabled=True
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
        
        # 获取当前价格用于滑点控制
        market_data = self.engine.data_manager.get_market_data(market_id)
        current_price = market_data.get('last_price', 0) if market_data else 0
        
        # 获取有效的滑点容忍度
        slippage_tolerance = self._get_effective_slippage_tolerance(market_id)
        
        # 创建订单（添加滑点控制）
        order = self._create_order(
            market_id=market_id,
            side="sell",
            order_type=self.ut_config.order_type,
            size=size,
            price=current_price,  # 使用当前价格进行滑点控制
            leverage=self.ut_config.leverage,
            margin_mode=self.ut_config.margin_mode,
            price_slippage_tolerance=slippage_tolerance,
            slippage_enabled=True
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
        # 使用data_manager获取当前价格
        market_data = self.engine.data_manager.get_market_data(market_id)
        if not market_data:
            return 0.0
            
        current_price = market_data.get('last_price', 0)
        if current_price <= 0:
            return 0.0
        
        # 优先使用position_size_usd配置
        if hasattr(self.ut_config, 'position_size_usd') and self.ut_config.position_size_usd > 0:
            # 直接使用USD金额计算仓位大小
            position_size = self.ut_config.position_size_usd / current_price
            self.logger.debug(f"使用position_size_usd配置: ${self.ut_config.position_size_usd} / ${current_price} = {position_size:.6f}")
        else:
            # 回退到基于风险百分比的计算方式
            risk_status = self.engine.risk_manager.get_risk_status()
            account_balance = risk_status.get('current_equity', 10000.0)
            
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
            self.logger.debug(f"使用风险百分比计算: ${risk_amount} / (${stop_distance:.4f} * ${current_price}) = {position_size:.6f}")
        
        # 注意：杠杆在订单创建时应用，这里不重复应用
        # 杠杆倍数会在_create_order方法中处理
        
        # 获取市场特定的滑点配置
        slippage_config = self._get_market_slippage_config(market_id)
        if slippage_config and slippage_config.get('enabled', True):
            # 滑点配置可能会影响仓位大小，这里可以根据需要调整
            pass
            
        return position_size
    
    def _get_market_slippage_config(self, market_id: int) -> Optional[Dict[str, Any]]:
        """获取市场特定的滑点配置"""
        if not hasattr(self.ut_config, 'market_slippage_config') or not self.ut_config.market_slippage_config:
            return None
        
        return self.ut_config.market_slippage_config.get(market_id)
    
    def _get_market_risk_config(self, market_id: int) -> Optional[Dict[str, Any]]:
        """获取市场特定的风险配置"""
        if not hasattr(self.ut_config, 'market_risk_config') or not self.ut_config.market_risk_config:
            return None
        
        return self.ut_config.market_risk_config.get(market_id)
    
    def _get_effective_slippage_tolerance(self, market_id: int) -> float:
        """获取有效的滑点容忍度"""
        # 首先检查市场特定配置
        market_slippage_config = self._get_market_slippage_config(market_id)
        if market_slippage_config and market_slippage_config.get('enabled', True):
            return market_slippage_config.get('tolerance', self.ut_config.price_slippage_tolerance)
        
        # 回退到全局配置
        return self.ut_config.price_slippage_tolerance
    
    def _get_effective_stop_loss(self, market_id: int) -> float:
        """获取有效的止损百分比"""
        # 首先检查市场特定配置
        market_risk_config = self._get_market_risk_config(market_id)
        if market_risk_config and market_risk_config.get('stop_loss_enabled', True):
            return market_risk_config.get('stop_loss', 0.15)  # 默认15%
        
        # 回退到全局配置（这里可以根据需要添加全局止损配置）
        return 0.15  # 默认15%
    
    def _get_effective_take_profit(self, market_id: int) -> float:
        """获取有效的止盈百分比"""
        # 首先检查市场特定配置
        market_risk_config = self._get_market_risk_config(market_id)
        if market_risk_config and market_risk_config.get('take_profit_enabled', True):
            return market_risk_config.get('take_profit', 0.25)  # 默认25%
        
        # 回退到全局配置（这里可以根据需要添加全局止盈配置）
        return 0.25  # 默认25%
        
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
        
    async def _check_risk_limits(self, market_id: int) -> bool:
        """检查风险限制"""
        try:
            # 获取当前价格
            market_data = self.engine.data_manager.get_market_data(market_id)
            if not market_data:
                return False
                
            current_price = market_data.get('last_price', 0)
            if current_price <= 0:
                return False
                
            # 计算仓位大小
            size = self._calculate_position_size(market_id, "buy")
            if size <= 0:
                return False
                
            # 检查仓位大小限制
            if not self.engine.risk_manager.check_position_size(market_id, size, current_price):
                self.logger.warning(f"市场 {market_id} 仓位大小超过风险限制")
                return False
                
            # 检查杠杆限制
            leverage = 1.0 if not self.ut_config.use_leverage else 2.0
            if not self.engine.risk_manager.check_leverage(leverage):
                self.logger.warning(f"市场 {market_id} 杠杆倍数超过风险限制")
                return False
                
            # 检查日亏损限制
            risk_status = self.engine.risk_manager.get_risk_status()
            daily_loss_ratio = abs(risk_status['daily_pnl']) / max(risk_status['current_equity'], 1)
            if not self.engine.risk_manager.check_daily_loss(daily_loss_ratio):
                self.logger.warning(f"市场 {market_id} 日亏损超过风险限制")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"风险检查失败: {e}")
            return False
