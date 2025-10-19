"""
UT Bot策略
基于TradingView UT Bot Alerts的ATR追踪止损策略
"""

import logging
from typing import Dict, List, Optional, Any
import numpy as np
import asyncio
from datetime import datetime, timedelta

from .base_strategy import BaseStrategy
from ..utils.config import Config
from ..utils.logger import setup_logger


class UTBotStrategy(BaseStrategy):
    """UT Bot策略 - 基于ATR追踪止损 + 多时间周期确认"""
    
    def __init__(self, config: Config, market_id: int = 0, 
                 key_value: float = 1.0, atr_period: int = 10, 
                 use_heikin_ashi: bool = False,
                 position_size: float = None,
                 stop_loss: float = None,
                 take_profit: float = None,
                 leverage: float = None,
                 margin_mode: str = None,
                 order_type: str = None,
                 limit_price_offset: float = None,
                 enable_multi_timeframe: bool = None):
        """
        初始化UT Bot策略
        
        Args:
            config: 配置对象
            market_id: 市场ID
            key_value: 关键值，影响敏感度
            atr_period: ATR周期
            use_heikin_ashi: 是否使用Heikin Ashi蜡烛图
            position_size: 仓位大小（如果为None，从config读取）
            stop_loss: 止损比例（如果为None，从config读取）
            take_profit: 止盈比例（如果为None，从config读取）
            leverage: 杠杆倍数（如果为None，从config读取）
            margin_mode: 保证金模式（如果为None，从config读取）
            order_type: 订单类型 market/limit（如果为None，从config读取）
            limit_price_offset: 限价单价格偏移百分比（如果为None，从config读取）
        """
        super().__init__("UTBot", config)
        
        self.market_id = market_id
        self.key_value = key_value
        self.atr_period = atr_period
        self.use_heikin_ashi = use_heikin_ashi
        
        # 策略参数 - 优先使用传入的参数，否则从config读取
        ut_config = config.strategies.get('ut_bot', {}) if hasattr(config, 'strategies') else {}
        self.position_size_usd = position_size if position_size is not None else ut_config.get('position_size', 10.0)  # 改为USD金额
        self.stop_loss = stop_loss if stop_loss is not None else ut_config.get('stop_loss', 0.02)
        self.take_profit = take_profit if take_profit is not None else ut_config.get('take_profit', 0.01)
        self.leverage = leverage if leverage is not None else ut_config.get('leverage', 1.0)
        self.margin_mode = margin_mode if margin_mode is not None else ut_config.get('margin_mode', 'cross')
        self.order_type = order_type if order_type is not None else ut_config.get('order_type', 'market')
        self.limit_price_offset = limit_price_offset if limit_price_offset is not None else ut_config.get('limit_price_offset', 0.001)
        self.price_slippage_tolerance = ut_config.get('price_slippage_tolerance', 0.01)  # 价格滑点容忍度，默认1%
        
        # ⭐ 新增：多时间周期确认
        self.enable_multi_timeframe = enable_multi_timeframe if enable_multi_timeframe is not None else ut_config.get('enable_multi_timeframe', False)
        
        self.logger.info(f"策略配置: position_size=${self.position_size_usd} USD (将根据市场价格自动计算加密货币数量)")
        self.logger.info(f"杠杆配置: {self.leverage}x, 保证金模式: {self.margin_mode}")
        self.logger.info(f"滑点容忍度: {self.price_slippage_tolerance*100:.2f}% (可在config.yaml中调整)")
        if self.enable_multi_timeframe:
            self.logger.info(f"✅ 已启用多时间周期确认 (5分钟+1分钟)")
        
        # 状态变量
        self.xATRTrailingStop = 0.0
        self.pos = 0  # 0: 无仓位, 1: 多头, -1: 空头
        self.last_signal_time = None
        self.signal_cooldown = 300  # 5分钟冷却时间
        
        # 历史数据缓存
        self.price_history = []
        self.atr_history = []
        
        # ⭐ 需求①：K线类型配置（需要先初始化，供后续使用）
        self.kline_types = ut_config.get('kline_types', [1])  # 默认只对1分钟K线发出信号
        self.logger.info(f"K线类型配置: {self.kline_types}分钟 - 策略将对这些时间周期的K线发出交易信号")
        
        # ⭐ 多时间周期状态（动态初始化）
        if self.enable_multi_timeframe:
            # 根据kline_types配置动态初始化多时间周期状态
            for timeframe_minutes in self.kline_types:
                if timeframe_minutes != 1:  # 1分钟使用统一的价格历史，不需要独立初始化
                    # 初始化信号状态
                    setattr(self, f'tf_{timeframe_minutes}m_signal', 0)
                    # 初始化追踪止损
                    setattr(self, f'tf_{timeframe_minutes}m_trailing_stop', 0.0)
                    # 初始化价格历史
                    setattr(self, f'tf_{timeframe_minutes}m_price_history', [])
            
            # 为1分钟时间周期初始化独立状态（多时间周期模式需要）
            self.tf_1m_signal = 0
            self.tf_1m_trailing_stop = 0.0
            self.tf_1m_price_history = []
            
            self.logger.info(f"多时间周期状态已初始化: {self.kline_types}分钟")
        
        # ⭐ 需求③：K线完成确认状态
        self.wait_for_kline_completion = ut_config.get('wait_for_kline_completion', True)  # 是否等待K线走完
        self.current_kline_signal = 0  # 当前K线的信号: 1=buy, -1=sell, 0=neutral
        self.pending_kline_signal = None  # 待确认的K线信号
        self.last_kline_timestamp = None  # 最后一根K线的时间戳
        
        # ⭐ 需求②：上一根K线信号检测状态
        self.previous_kline_signal = 0  # 上一根K线的信号: 1=buy, -1=sell, 0=neutral
        self.double_reverse_enabled = True  # 是否启用双倍反向订单功能
        
        # ⭐ 修复：延迟刷新持仓信息的标志
        self._needs_position_refresh = False
        
        if self.wait_for_kline_completion:
            kline_types_str = ", ".join(map(str, self.kline_types))
            self.logger.info(f"✅ 已启用K线完成确认模式：等待{kline_types_str}分钟K线走完后再交易")
        else:
            self.logger.info("⚡ 使用即时交易模式：检测到信号立即交易")
        
        # ⭐ 市场级止盈止损配置（仅使用策略级别的配置）
        self.market_risk_config = ut_config.get('market_risk_config', {})
        if self.market_risk_config:
            self.logger.info(f"使用config.yaml中的风险配置: {len(self.market_risk_config)} 个市场")
        else:
            self.logger.info("使用默认风险配置")
        
        market_risk = self.market_risk_config.get(self.market_id, {})
        self.market_stop_loss_enabled = market_risk.get('stop_loss_enabled', True)
        self.market_stop_loss = market_risk.get('stop_loss', self.stop_loss)
        self.market_take_profit_enabled = market_risk.get('take_profit_enabled', True)
        self.market_take_profit = market_risk.get('take_profit', self.take_profit)
        
        self.logger.info(f"市场 {self.market_id} 风险配置: 止损={'开启' if self.market_stop_loss_enabled else '关闭'}({self.market_stop_loss*100:.1f}%), 止盈={'开启' if self.market_take_profit_enabled else '关闭'}({self.market_take_profit*100:.1f}%)")
        
        # ⭐ 市场级滑点配置（优先使用config.yaml中的配置）
        config_slippage = ut_config.get('market_slippage_config', {})
        if config_slippage:
            # 使用config.yaml中的配置
            self.market_slippage_config = config_slippage
            self.logger.info(f"使用config.yaml中的滑点配置: {len(config_slippage)} 个市场")
        else:
            # 使用默认配置
            self.market_slippage_config = {
                0: {"enabled": True, "tolerance": 0.01},    # ETH: 1%滑点容忍度
                1: {"enabled": True, "tolerance": 0.005},   # BTC: 0.5%滑点容忍度
                2: {"enabled": False, "tolerance": 0.02},   # SOL: 关闭滑点检测，直接市价成交
                3: {"enabled": True, "tolerance": 0.03},    # DOGE: 3%滑点容忍度，波动较大
            }
            self.logger.info("使用默认滑点配置")
        
        # 获取当前市场的滑点配置
        current_slippage = self.market_slippage_config.get(self.market_id, {"enabled": True, "tolerance": 0.01})
        self.slippage_enabled = current_slippage["enabled"]
        self.slippage_tolerance = current_slippage["tolerance"]
        
        self.logger.info(f"市场 {self.market_id} 滑点配置: {'开启' if self.slippage_enabled else '关闭'}, 容忍度={self.slippage_tolerance*100:.2f}%")
        
    async def on_initialize(self):
        """策略初始化"""
        self.logger.info(f"初始化UT Bot策略: 市场 {self.market_id}, 关键值 {self.key_value}, ATR周期 {self.atr_period}")
        
        # ⭐ 修复：强制刷新持仓信息，避免重复开仓
        await self._refresh_position_info()
        
    async def _refresh_position_info(self):
        """⭐ 修复：刷新持仓信息，确保获取最新的真实持仓状态"""
        try:
            # 强制更新仓位管理器中的持仓信息
            if self.engine and self.engine.position_manager:
                await self.engine.position_manager.update_positions()
                
                # 检查当前市场的持仓状态
                position = self._get_position(self.market_id)
                if position:
                    self.logger.info(f"✅ 检测到现有持仓: 市场{self.market_id}, {position.side.value}, 数量{position.size:.6f}, 价格${position.entry_price:.6f}")
                else:
                    self.logger.info(f"📊 市场{self.market_id}当前无持仓")
            else:
                # 如果引擎还未初始化，标记需要延迟刷新
                self.logger.info("引擎尚未完全初始化，将在引擎启动后自动刷新持仓信息")
                self._needs_position_refresh = True
                
        except Exception as e:
            self.logger.error(f"刷新持仓信息失败: {e}")
        
    async def on_start(self):
        """策略启动"""
        self.logger.info("UT Bot策略已启动")
        
        # ⭐ 修复：如果之前标记了需要刷新持仓信息，现在执行
        if self._needs_position_refresh:
            self.logger.info("引擎已启动，现在执行延迟的持仓信息刷新")
            await self._refresh_position_info()
            self._needs_position_refresh = False
        
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
            
        # ⭐ 如果启用多时间周期，使用新的处理逻辑
        if self.enable_multi_timeframe:
            await self._process_multi_timeframe(candlesticks)
        else:
            # 原有的单时间周期逻辑
            await self._process_single_timeframe(candlesticks)
    
    async def _process_single_timeframe(self, candlesticks: List[Dict[str, Any]]):
        """⭐ 处理单时间周期数据（根据kline_types配置）"""
        # 使用统一的时间周期分析方法
        signals_analyzed = self._analyze_kline_types_signals(candlesticks, is_multi_timeframe=False)
        
        self.logger.debug(f"单时间周期分析的K线类型: {list(signals_analyzed.keys())}分钟, 信号: {signals_analyzed}")
        
        # 检查现有持仓的止盈止损条件
        if signals_analyzed:
            await self._check_market_level_risk_management(candlesticks[-1]['close'])
        
        # 根据配置的K线类型进行决策
        if signals_analyzed:
            await self._kline_types_decision(candlesticks[-1]['close'], signals_analyzed)
    
    async def _process_multi_timeframe(self, candlesticks: List[Dict[str, Any]]):
        """⭐ 处理多时间周期数据（根据kline_types配置）"""
        # 使用统一的时间周期分析方法
        signals_analyzed = self._analyze_kline_types_signals(candlesticks, is_multi_timeframe=True)
        
        self.logger.debug(f"多时间周期分析的K线类型: {list(signals_analyzed.keys())}分钟, 信号: {signals_analyzed}")
        
        # 检查现有持仓的止盈止损条件
        if signals_analyzed:
            await self._check_market_level_risk_management(candlesticks[-1]['close'])
        
        # 根据配置的K线类型进行决策
        if signals_analyzed:
            await self._kline_types_decision(candlesticks[-1]['close'], signals_analyzed)
    
    def _analyze_kline_types_signals(self, candlesticks: List[Dict[str, Any]], is_multi_timeframe: bool = True) -> Dict[int, int]:
        """⭐ 统一的时间周期信号分析方法
        
        Args:
            candlesticks: K线数据
            is_multi_timeframe: 是否为多时间周期模式
            
        Returns:
            Dict[int, int]: {时间周期(分钟): 信号值(1=buy, -1=sell, 0=neutral)}
        """
        signals_analyzed = {}
        
        for timeframe_minutes in self.kline_types:
            # 获取对应时间周期的K线数据
            if timeframe_minutes == 1:
                target_candlesticks = candlesticks  # 假设输入的就是1分钟数据
            else:
                target_candlesticks = self._resample_to_timeframe(candlesticks, f'{timeframe_minutes}m')
            
            if len(target_candlesticks) >= self.atr_period + 1:
                # 根据模式选择价格历史和追踪止损属性
                if is_multi_timeframe:
                    # 多时间周期模式：使用独立的价格历史和追踪止损
                    price_history = getattr(self, f'tf_{timeframe_minutes}m_price_history', [])
                    trailing_stop_attr = f'tf_{timeframe_minutes}m_trailing_stop'
                    
                    # 检查是否支持该时间周期
                    if not hasattr(self, trailing_stop_attr):
                        self.logger.warning(f"不支持的时间周期: {timeframe_minutes}分钟，跳过分析")
                        continue
                else:
                    # 单时间周期模式：使用统一的价格历史和追踪止损
                    price_history = self.price_history
                    trailing_stop_attr = 'xATRTrailingStop'
                
                # 分析信号
                signal = self._analyze_timeframe(target_candlesticks, price_history, trailing_stop_attr)
                signals_analyzed[timeframe_minutes] = signal
                
                # 保持向后兼容性（多时间周期模式）
                if is_multi_timeframe:
                    signal_attr = f'tf_{timeframe_minutes}m_signal'
                    if hasattr(self, signal_attr):
                        setattr(self, signal_attr, signal)
        
        return signals_analyzed
    
    def _resample_to_timeframe(self, candlesticks_1m: List[Dict], target_tf: str) -> List[Dict]:
        """将1分钟K线重采样为目标时间周期"""
        if target_tf == '5m':
            interval = 5
        elif target_tf == '15m':
            interval = 15
        else:
            return candlesticks_1m
        
        resampled = []
        for i in range(0, len(candlesticks_1m), interval):
            chunk = candlesticks_1m[i:i+interval]
            if len(chunk) >= interval:  # 只使用完整的周期
                resampled.append({
                    'open': chunk[0]['open'],
                    'high': max(c['high'] for c in chunk),
                    'low': min(c['low'] for c in chunk),
                    'close': chunk[-1]['close'],
                    'volume': sum(c.get('volume', 0) for c in chunk),
                    'timestamp': chunk[-1]['timestamp']
                })
        return resampled
    
    def _analyze_timeframe(self, candlesticks: List[Dict], price_history: List, trailing_stop_attr: str) -> int:
        """分析单个时间周期的信号
        
        Returns:
            1: buy信号, -1: sell信号, 0: 无信号
        """
        if len(candlesticks) < self.atr_period + 2:
            return 0
        
        # 获取当前价格和前一价格
        current_price = candlesticks[-1]['close']
        prev_price = candlesticks[-2]['close']
        current_timestamp = candlesticks[-1]['timestamp']
        
        # ⭐ 需求③：检查是否是新K线
        is_new_kline = (self.last_kline_timestamp is None or 
                       current_timestamp != self.last_kline_timestamp)
        
        if is_new_kline:
            # 新K线开始，确认上一根K线的最终信号
            if self.pending_kline_signal is not None:
                self.logger.info(f"🕐 K线完成确认: 上一根K线最终信号 = {['中性', '买入', '卖出'][self.pending_kline_signal]}")
                self.current_kline_signal = self.pending_kline_signal
                self.pending_kline_signal = None
            else:
                # ⭐ 修复：即使没有待确认信号，也要确认上一根K线为中性信号
                self.logger.debug(f"🕐 K线完成确认: 上一根K线无信号变化，确认为中性")
                self.current_kline_signal = 0
            
            self.last_kline_timestamp = current_timestamp
            
        # 更新价格历史
        price_history.append(current_price)
        if len(price_history) > self.atr_period + 10:
            price_history.pop(0)
            
        # 计算ATR
        if len(price_history) < self.atr_period + 1:
            return 0
        
        true_ranges = []
        for i in range(1, len(price_history)):
            high = price_history[i]
            low = price_history[i-1]
            close_prev = price_history[i-1]
            tr1 = high - low
            tr2 = abs(high - close_prev)
            tr3 = abs(low - close_prev)
            true_ranges.append(max(tr1, tr2, tr3))
        
        if len(true_ranges) < self.atr_period:
            return 0
        
        atr = np.mean(true_ranges[-self.atr_period:])
        nLoss = self.key_value * atr
        
        # 获取或初始化追踪止损
        trailing_stop = getattr(self, trailing_stop_attr, 0.0)
        
        if trailing_stop == 0:
            trailing_stop = current_price - nLoss if current_price > 0 else current_price + nLoss
        else:
            # 更新追踪止损
            if current_price > trailing_stop and prev_price > trailing_stop:
                trailing_stop = max(trailing_stop, current_price - nLoss)
            elif current_price < trailing_stop and prev_price < trailing_stop:
                trailing_stop = min(trailing_stop, current_price + nLoss)
            elif current_price > trailing_stop:
                trailing_stop = current_price - nLoss
            else:
                trailing_stop = current_price + nLoss
        
        # 保存追踪止损
        setattr(self, trailing_stop_attr, trailing_stop)
        
        # 判断信号
        if prev_price < trailing_stop and current_price > trailing_stop:
            signal = 1  # buy信号
        elif prev_price > trailing_stop and current_price < trailing_stop:
            signal = -1  # sell信号
        else:
            signal = 0  # 无信号变化
        
        # ⭐ 需求③：K线完成确认逻辑 - 对所有kline_types中的时间周期都有效
        if self.wait_for_kline_completion:
            # 检查当前时间周期是否在kline_types中
            current_timeframe_minutes = None
            if trailing_stop_attr == 'tf_1m_trailing_stop':
                current_timeframe_minutes = 1
            elif trailing_stop_attr == 'tf_5m_trailing_stop':
                current_timeframe_minutes = 5
            elif trailing_stop_attr == 'tf_15m_trailing_stop':
                current_timeframe_minutes = 15
            elif trailing_stop_attr == 'tf_30m_trailing_stop':
                current_timeframe_minutes = 30
            elif trailing_stop_attr == 'tf_60m_trailing_stop':
                current_timeframe_minutes = 60
            
            # 如果当前时间周期在kline_types中，应用K线完成确认逻辑
            if current_timeframe_minutes and current_timeframe_minutes in self.kline_types:
                # ⭐ 修复：在K线完成确认模式下，始终更新pending_kline_signal以反映当前K线的最新信号状态
                if signal != 0:
                    self.pending_kline_signal = signal
                    self.logger.debug(f"🕐 {current_timeframe_minutes}分钟K线信号更新: {['中性', '买入', '卖出'][signal]} (等待K线完成)")
                    return 0  # 返回0，等待K线完成
                else:
                    # ⭐ 修复：如果没有信号，也要更新pending_kline_signal为0（中性），确保K线完成时能正确确认
                    if self.pending_kline_signal is None:
                        self.pending_kline_signal = 0  # 初始化为中性信号
                    elif self.pending_kline_signal != 0:
                        # 如果之前有信号但现在没有，保持之前的信号状态
                        self.logger.debug(f"🕐 {current_timeframe_minutes}分钟K线信号保持: {['中性', '买入', '卖出'][self.pending_kline_signal]} (等待K线完成)")
                    
                    # ⭐ 需求②：更新上一根K线信号
                    if self.current_kline_signal != 0:
                        self.previous_kline_signal = self.current_kline_signal
                        self.logger.debug(f"📊 上一根{current_timeframe_minutes}分钟K线信号: {['中性', '买入', '卖出'][self.previous_kline_signal]}")
                    return self.current_kline_signal  # 返回已确认的信号
        
        # ⭐ 需求②：更新上一根K线信号
        if signal != 0:
            self.previous_kline_signal = signal
            self.logger.debug(f"📊 上一根K线信号: {['中性', '买入', '卖出'][self.previous_kline_signal]}")
        
        return signal
    
    async def _check_market_level_risk_management(self, current_price: float):
        """⭐ 新需求：检查市场级止盈止损条件"""
        position = self._get_position(self.market_id)
        if not position:
            return
        
        from ..core.position_manager import PositionSide
        
        # 计算当前盈亏比例
        if position.side == PositionSide.LONG:
            # 多仓：价格上涨为盈利
            pnl_ratio = (current_price - position.entry_price) / position.entry_price
        else:
            # 空仓：价格下跌为盈利
            pnl_ratio = (position.entry_price - current_price) / position.entry_price
        
        # 检查止损条件（仅在开启时检查）
        if self.market_stop_loss_enabled and pnl_ratio <= -self.market_stop_loss:
            self.logger.warning(f"🛑 市场 {self.market_id} 触发止损: 亏损 {pnl_ratio*100:.2f}% >= {self.market_stop_loss*100:.1f}%")
            await self._close_position(current_price, f"市场级止损: 亏损{pnl_ratio*100:.2f}%")
            return
        
        # 检查止盈条件（仅在开启时检查）
        if self.market_take_profit_enabled and pnl_ratio >= self.market_take_profit:
            self.logger.info(f"💰 市场 {self.market_id} 触发止盈: 盈利 {pnl_ratio*100:.2f}% >= {self.market_take_profit*100:.1f}%")
            await self._close_position(current_price, f"市场级止盈: 盈利{pnl_ratio*100:.2f}%")
            return
        
        # 记录当前盈亏状态
        stop_loss_status = f"{'开启' if self.market_stop_loss_enabled else '关闭'}({self.market_stop_loss*100:.1f}%)"
        take_profit_status = f"{'开启' if self.market_take_profit_enabled else '关闭'}({self.market_take_profit*100:.1f}%)"
        self.logger.debug(f"市场 {self.market_id} 当前盈亏: {pnl_ratio*100:.2f}% (止损: {stop_loss_status}, 止盈: {take_profit_status})")
    
    async def _kline_types_decision(self, current_price: float, signals_analyzed: Dict[int, int]):
        """⭐ 根据kline_types配置进行决策"""
        # ⭐ 修复：增强持仓检测日志
        position = self._get_position(self.market_id)
        if position:
            self.logger.info(f"📊 当前持仓状态: 市场{self.market_id}, {position.side.value}, 数量{position.size:.6f}")
        else:
            self.logger.info(f"📊 当前持仓状态: 市场{self.market_id}无持仓")
        
        # 检查信号冷却
        current_time = datetime.now().timestamp()
        if (self.last_signal_time and 
            current_time - self.last_signal_time < self.signal_cooldown):
            return
        
        # 记录分析的信号
        signal_info = []
        for timeframe, signal in signals_analyzed.items():
            signal_info.append(f"{timeframe}分钟={['中性', '买入', '卖出'][signal]}")
        self.logger.info(f"K线类型信号: {', '.join(signal_info)}")
        self.logger.info(f"上一根K线信号: {['中性', '买入', '卖出'][self.previous_kline_signal]}")
        
        # ⭐ 修复：只有在有持仓时才检查上一根K线信号的一致性
        # 如果没有持仓，应该基于当前K线信号进行决策，而不是基于历史信号
        if position and self.double_reverse_enabled and self.previous_kline_signal != 0:
            should_execute_double_reverse = await self._check_previous_kline_signal_consistency(current_price, position)
            if should_execute_double_reverse:
                self.logger.info("🔄 执行双倍反向订单，跳过其他信号处理")
                return  # 执行双倍反向订单后，跳过后续的K线类型决策
        
        # 根据配置的K线类型进行决策
        if len(self.kline_types) == 1:
            # 单时间周期决策
            await self._single_kline_type_decision(current_price, signals_analyzed, position)
        else:
            # 多时间周期决策
            await self._multiple_kline_types_decision(current_price, signals_analyzed, position)
    
    async def _single_kline_type_decision(self, current_price: float, signals_analyzed: Dict[int, int], position):
        """单时间周期决策"""
        timeframe = self.kline_types[0]
        signal = signals_analyzed.get(timeframe, 0)
        
        # ⭐ 修复：当启用K线完成确认模式时，只基于已确认的信号进行交易
        if self.wait_for_kline_completion:
            # 在K线完成确认模式下，只使用已确认的信号（current_kline_signal）
            confirmed_signal = self.current_kline_signal
            if confirmed_signal == 1:  # 买入信号
                if position and position.side.value == "long":
                    self.logger.info(f"✅ 已有多仓持仓 {position.size:.6f}，跳过重复开仓")
                else:
                    self.logger.info(f"✅ {timeframe}分钟确认买入信号 → 开多仓")
                    await self._open_long_position(current_price)
                    
            elif confirmed_signal == -1:  # 卖出信号
                if position and position.side.value == "short":
                    self.logger.info(f"✅ 已有空仓持仓 {position.size:.6f}，跳过重复开仓")
                else:
                    self.logger.info(f"✅ {timeframe}分钟确认卖出信号 → 开空仓")
                    await self._open_short_position(current_price)
            else:
                self.logger.debug(f"📊 当前无确认信号，等待K线完成确认")
        else:
            # 即时交易模式：基于实时检测的信号
            if signal == 1:  # 买入信号
                if position and position.side.value == "long":
                    self.logger.info(f"✅ 已有多仓持仓 {position.size:.6f}，跳过重复开仓")
                else:
                    self.logger.info(f"✅ {timeframe}分钟买入信号 → 开多仓")
                    await self._open_long_position(current_price)
                    
            elif signal == -1:  # 卖出信号
                if position and position.side.value == "short":
                    self.logger.info(f"✅ 已有空仓持仓 {position.size:.6f}，跳过重复开仓")
                else:
                    self.logger.info(f"✅ {timeframe}分钟卖出信号 → 开空仓")
                    await self._open_short_position(current_price)
    
    async def _multiple_kline_types_decision(self, current_price: float, signals_analyzed: Dict[int, int], position):
        """多时间周期决策（保持原有的多时间周期逻辑）"""
        # ⭐ 修复：当启用K线完成确认模式时，只基于已确认的信号进行交易
        if self.wait_for_kline_completion:
            # 在K线完成确认模式下，使用已确认的信号
            tf_1m_confirmed_signal = self.current_kline_signal  # 1分钟已确认信号
            tf_5m_confirmed_signal = getattr(self, 'tf_5m_signal', 0)  # 5分钟已确认信号
            
            # 决策规则基于已确认的信号
            if tf_5m_confirmed_signal == 1 and tf_1m_confirmed_signal == 1:
                # 规则1: 5分钟buy + 1分钟buy → 做多
                if position and position.side.value == "long":
                    self.logger.info(f"✅ 已有多仓持仓 {position.size:.6f}，跳过重复开仓")
                else:
                    self.logger.info("✅ 多时间周期确认: 5分钟buy + 1分钟buy → 基于确认信号开多仓")
                    await self._open_long_position(current_price)
                
            elif tf_5m_confirmed_signal == -1 and tf_1m_confirmed_signal == -1:
                # 规则2: 5分钟sell + 1分钟sell → 做空
                if position and position.side.value == "short":
                    self.logger.info(f"✅ 已有空仓持仓 {position.size:.6f}，跳过重复开仓")
                else:
                    self.logger.info("✅ 多时间周期确认: 5分钟sell + 1分钟sell → 基于确认信号开空仓")
                    await self._open_short_position(current_price)
        else:
            # 即时交易模式：基于实时检测的信号
            tf_1m_signal = signals_analyzed.get(1, 0)
            tf_5m_signal = signals_analyzed.get(5, 0)
            
            # 决策规则基于实时信号
            if tf_5m_signal == 1 and tf_1m_signal == 1:
                # 规则1: 5分钟buy + 1分钟buy → 做多
                if position and position.side.value == "long":
                    self.logger.info(f"✅ 已有多仓持仓 {position.size:.6f}，跳过重复开仓")
                else:
                    self.logger.info("✅ 多时间周期确认: 5分钟buy + 1分钟buy → 立即开多仓")
                    await self._open_long_position(current_price)
                
            elif tf_5m_signal == -1 and tf_1m_signal == -1:
                # 规则2: 5分钟sell + 1分钟sell → 做空
                if position and position.side.value == "short":
                    self.logger.info(f"✅ 已有空仓持仓 {position.size:.6f}，跳过重复开仓")
                else:
                    self.logger.info("✅ 多时间周期确认: 5分钟sell + 1分钟sell → 立即开空仓")
                    await self._open_short_position(current_price)
            
            elif tf_5m_signal == 1 and tf_1m_signal == -1:
                # 规则3: 5分钟buy + 1分钟sell → 平多仓（如果有），不开空仓
                if position:
                    from ..core.position_manager import PositionSide
                    if position.side == PositionSide.LONG:
                        self.logger.warning("⚠️  多时间周期冲突: 5分钟buy但1分钟sell → 平多仓，不开空仓")
                        await self._close_position(current_price, "多时间周期冲突：5m-buy + 1m-sell")
                
            elif tf_5m_signal == -1 and tf_1m_signal == 1:
                # 规则4: 5分钟sell + 1分钟buy → 平空仓（如果有），不开多仓
                if position:
                    from ..core.position_manager import PositionSide
                    if position.side == PositionSide.SHORT:
                        self.logger.warning("⚠️  多时间周期冲突: 5分钟sell但1分钟buy → 平空仓，不开多仓")
                        await self._close_position(current_price, "多时间周期冲突：5m-sell + 1m-buy")
    
    async def _multi_timeframe_decision(self, current_price: float):
        """多时间周期决策逻辑"""
        # ⭐ 修复：增强持仓检测日志
        position = self._get_position(self.market_id)
        if position:
            self.logger.info(f"📊 当前持仓状态: 市场{self.market_id}, {position.side.value}, 数量{position.size:.6f}")
        else:
            self.logger.info(f"📊 当前持仓状态: 市场{self.market_id}无持仓")
        
        # 检查信号冷却
        current_time = datetime.now().timestamp()
        if (self.last_signal_time and 
            current_time - self.last_signal_time < self.signal_cooldown):
            return
            
        self.logger.info(f"多时间周期信号: 5分钟={['中性', '买入', '卖出'][self.tf_5m_signal]}, 1分钟={['中性', '买入', '卖出'][self.tf_1m_signal]}")
        self.logger.info(f"上一根K线信号: {['中性', '买入', '卖出'][self.previous_kline_signal]}")
        
        # ⭐ 需求②：优先检查上一根K线信号与现有持仓的一致性
        # 如果上一根K线信号与持仓不一致，优先执行双倍反向订单，跳过其他信号
        if self.double_reverse_enabled and self.previous_kline_signal != 0:
            should_execute_double_reverse = await self._check_previous_kline_signal_consistency(current_price, position)
            if should_execute_double_reverse:
                self.logger.info("🔄 执行双倍反向订单，跳过其他信号处理")
                return  # 执行双倍反向订单后，跳过后续的多时间周期决策
        
        # 决策规则（仅在未执行双倍反向订单时执行）
        if self.tf_5m_signal == 1 and self.tf_1m_signal == 1:
            # 规则1: 5分钟buy + 1分钟buy → 做多
            if position and position.side.value == "long":
                # ⭐ 修复：已有多仓，跳过重复开仓
                self.logger.info(f"✅ 已有多仓持仓 {position.size:.6f}，跳过重复开仓")
            else:
                if self.wait_for_kline_completion:
                    self.logger.info("✅ 多时间周期确认: 5分钟buy + 1分钟buy → 等待K线完成确认后开多仓")
                else:
                    self.logger.info("✅ 多时间周期确认: 5分钟buy + 1分钟buy → 立即开多仓")
                await self._open_long_position(current_price)
            
        elif self.tf_5m_signal == -1 and self.tf_1m_signal == -1:
            # 规则2: 5分钟sell + 1分钟sell → 做空
            if position and position.side.value == "short":
                # ⭐ 修复：已有空仓，跳过重复开仓
                self.logger.info(f"✅ 已有空仓持仓 {position.size:.6f}，跳过重复开仓")
            else:
                if self.wait_for_kline_completion:
                    self.logger.info("✅ 多时间周期确认: 5分钟sell + 1分钟sell → 等待K线完成确认后开空仓")
                else:
                    self.logger.info("✅ 多时间周期确认: 5分钟sell + 1分钟sell → 立即开空仓")
                await self._open_short_position(current_price)
            
        elif self.tf_5m_signal == 1 and self.tf_1m_signal == -1:
            # 规则3: 5分钟buy + 1分钟sell → 平多仓（如果有），不开空仓
            if position:
                from ..core.position_manager import PositionSide
                if position.side == PositionSide.LONG:
                    self.logger.warning("⚠️  多时间周期冲突: 5分钟buy但1分钟sell → 平多仓，不开空仓")
                    await self._close_position(current_price, "多时间周期冲突：5m-buy + 1m-sell")
            
        elif self.tf_5m_signal == -1 and self.tf_1m_signal == 1:
            # 规则4: 5分钟sell + 1分钟buy → 平空仓（如果有），不开多仓
            if position:
                from ..core.position_manager import PositionSide
                if position.side == PositionSide.SHORT:
                    self.logger.warning("⚠️  多时间周期冲突: 5分钟sell但1分钟buy → 平空仓，不开多仓")
                    await self._close_position(current_price, "多时间周期冲突：5m-sell + 1m-buy")
    
    async def _check_previous_kline_signal_consistency(self, current_price: float, position):
        """⭐ 需求②：检查上一根K线信号与现有持仓的一致性
        
        Returns:
            bool: 是否需要执行双倍反向订单
        """
        if not position:
            self.logger.debug("无持仓，跳过上一根K线信号一致性检查")
            return False
        
        from ..core.position_manager import PositionSide
        
        # 判断持仓方向
        current_position_side = 1 if position.side == PositionSide.LONG else -1
        
        # 判断上一根K线信号与持仓是否一致
        is_consistent = (self.previous_kline_signal == current_position_side)
        
        if is_consistent:
            # 信号与持仓一致，保持持仓方向
            self.logger.info(f"✅ 上一根K线信号与持仓一致: {['中性', '买入', '卖出'][self.previous_kline_signal]} → 保持{['', '多仓', '空仓'][current_position_side]}")
            return False  # 不需要执行双倍反向订单
        else:
            # 信号与持仓不一致，开双倍反向订单
            self.logger.warning(f"⚠️  上一根K线信号与持仓不一致: 信号{['中性', '买入', '卖出'][self.previous_kline_signal]} vs 持仓{['', '多仓', '空仓'][current_position_side]}")
            self.logger.warning(f"🔄 执行双倍反向订单策略")
            
            if self.previous_kline_signal == 1:  # 上一根K线是买入信号
                if current_position_side == 1:
                    # 当前是多仓，上一根K线也是买入信号，开双倍多仓
                    self.logger.info("📈 上一根K线买入信号 + 当前多仓 → 开双倍多仓")
                    await self._open_double_position(current_price, "long", "上一根K线买入信号确认")
                else:
                    # 当前是空仓，但上一根K线是买入信号，平空仓并开双倍多仓
                    self.logger.info("📈 上一根K线买入信号 + 当前空仓 → 平空仓并开双倍多仓")
                    await self._close_position(current_price, "信号反向：从空仓转为多仓")
                    await asyncio.sleep(0.5)  # 等待平仓完成
                    await self._open_double_position(current_price, "long", "上一根K线买入信号确认")
                    
            elif self.previous_kline_signal == -1:  # 上一根K线是卖出信号
                if current_position_side == -1:
                    # 当前是空仓，上一根K线也是卖出信号，开双倍空仓
                    self.logger.info("📉 上一根K线卖出信号 + 当前空仓 → 开双倍空仓")
                    await self._open_double_position(current_price, "short", "上一根K线卖出信号确认")
                else:
                    # 当前是多仓，但上一根K线是卖出信号，平多仓并开双倍空仓
                    self.logger.info("📉 上一根K线卖出信号 + 当前多仓 → 平多仓并开双倍空仓")
                    await self._close_position(current_price, "信号反向：从多仓转为空仓")
                    await asyncio.sleep(0.5)  # 等待平仓完成
                    await self._open_double_position(current_price, "short", "上一根K线卖出信号确认")
            
            return True  # 已执行双倍反向订单
    
    async def _open_double_position(self, price: float, side: str, reason: str):
        """⭐ 需求②：开双倍仓位"""
        # 计算双倍仓位大小
        double_size_usd = self.position_size_usd * 2.0
        actual_size = double_size_usd / price
        
        self.logger.info(f"🔄 开双倍仓位: ${double_size_usd} USD ÷ ${price:.6f} = {actual_size:.6f} 加密货币")
        self.logger.info(f"原因: {reason}")
        
        if not self._check_risk_limits(self.market_id, actual_size, price):
            self.logger.warning("⚠️  双倍仓位超过风险限制，取消开仓")
            return
        
        # 根据配置的订单类型决定价格
        order_price = price
        if self.order_type.lower() == "limit":
            if side == "long":
                # 限价买单：买入价格略低于市场价
                order_price = price * (1 - self.limit_price_offset)
                self.logger.info(f"限价双倍买单: 市场价=${price:.4f}, 限价=${order_price:.4f}")
            else:
                # 限价卖单：卖出价格略高于市场价
                order_price = price * (1 + self.limit_price_offset)
                self.logger.info(f"限价双倍卖单: 市场价=${price:.4f}, 限价=${order_price:.4f}")
        
        order = self._create_order(
            market_id=self.market_id,
            side=side,
            order_type=self.order_type,
            size=actual_size,
            price=order_price,
            leverage=self.leverage,
            margin_mode=self.margin_mode,
            price_slippage_tolerance=self.slippage_tolerance,
            slippage_enabled=self.slippage_enabled
        )
        
        if order:
            self._log_signal(f"DOUBLE_{side.upper()}", self.market_id, 
                           price=price, size=actual_size, size_usd=double_size_usd, reason=reason)
            self.last_signal_time = datetime.now().timestamp()
        
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
        # ⭐ 修复：检查是否已有同向持仓，避免重复开仓
        self.logger.info(f"🔍 检查市场{self.market_id}的持仓状态...")
        position = self._get_position(self.market_id)
        
        if position:
            from ..core.position_manager import PositionSide
            self.logger.info(f"📊 检测到现有持仓: {position.side.value}, 数量{position.size:.6f}, 入场价${position.entry_price:.6f}")
            
            if position.side == PositionSide.SHORT:
                self.logger.warning(f"⚠️  检测到反向持仓（空仓），先平仓再开多仓")
                await self._close_position(price, "信号反向：从空仓转为多仓")
                # 等待平仓完成
                import asyncio
                await asyncio.sleep(0.5)
            elif position.side == PositionSide.LONG:
                # ⭐ 修复：已有多仓，跳过重复开仓
                self.logger.warning(f"🚫 已有多仓持仓 {position.size:.6f}，跳过重复开仓（避免重复持仓）")
                return
        else:
            self.logger.info(f"📊 市场{self.market_id}当前无持仓，可以开多仓")
        
        # 将USD金额转换为实际的加密货币数量
        actual_size = self.position_size_usd / price
        self.logger.info(f"开仓计算: ${self.position_size_usd} USD ÷ ${price:.6f} = {actual_size:.6f} 加密货币")
        
        if not self._check_risk_limits(self.market_id, actual_size, price):
            return
            
        # 根据配置的订单类型决定价格
        order_price = price
        if self.order_type.lower() == "limit":
            # 限价单：买入价格略低于市场价（更容易成交）
            order_price = price * (1 - self.limit_price_offset)
            self.logger.info(f"限价买单: 市场价=${price:.4f}, 限价=${order_price:.4f} (偏移-{self.limit_price_offset*100:.2f}%)")
        
        order = self._create_order(
            market_id=self.market_id,
            side="buy",
            order_type=self.order_type,
            size=actual_size,  # 使用计算后的实际数量
            price=order_price,
            leverage=self.leverage,
            margin_mode=self.margin_mode,
            price_slippage_tolerance=self.slippage_tolerance,  # 使用市场特定的滑点容忍度
            slippage_enabled=self.slippage_enabled  # 使用市场特定的滑点开关
        )
        
        if order:
            self._log_signal("LONG", self.market_id, 
                           price=price, trailing_stop=self.xATRTrailingStop, size=actual_size, size_usd=self.position_size_usd)
            self.last_signal_time = datetime.now().timestamp()
            
    async def _open_short_position(self, price: float):
        """开空仓"""
        # ⭐ 修复：检查是否已有同向持仓，避免重复开仓
        self.logger.info(f"🔍 检查市场{self.market_id}的持仓状态...")
        position = self._get_position(self.market_id)
        
        if position:
            from ..core.position_manager import PositionSide
            self.logger.info(f"📊 检测到现有持仓: {position.side.value}, 数量{position.size:.6f}, 入场价${position.entry_price:.6f}")
            
            if position.side == PositionSide.LONG:
                self.logger.warning(f"⚠️  检测到反向持仓（多仓），先平仓再开空仓")
                await self._close_position(price, "信号反向：从多仓转为空仓")
                # 等待平仓完成
                import asyncio
                await asyncio.sleep(0.5)
            elif position.side == PositionSide.SHORT:
                # ⭐ 修复：已有空仓，跳过重复开仓
                self.logger.warning(f"🚫 已有空仓持仓 {position.size:.6f}，跳过重复开仓（避免重复持仓）")
                return
        else:
            self.logger.info(f"📊 市场{self.market_id}当前无持仓，可以开空仓")
        
        # 将USD金额转换为实际的加密货币数量
        actual_size = self.position_size_usd / price
        self.logger.info(f"开仓计算: ${self.position_size_usd} USD ÷ ${price:.6f} = {actual_size:.6f} 加密货币")
        
        if not self._check_risk_limits(self.market_id, actual_size, price):
            return
            
        # 根据配置的订单类型决定价格
        order_price = price
        if self.order_type.lower() == "limit":
            # 限价单：卖出价格略高于市场价（更容易成交）
            order_price = price * (1 + self.limit_price_offset)
            self.logger.info(f"限价卖单: 市场价=${price:.4f}, 限价=${order_price:.4f} (偏移+{self.limit_price_offset*100:.2f}%)")
        
        order = self._create_order(
            market_id=self.market_id,
            side="sell",
            order_type=self.order_type,
            size=actual_size,  # 使用计算后的实际数量
            price=order_price,
            leverage=self.leverage,
            margin_mode=self.margin_mode,
            price_slippage_tolerance=self.slippage_tolerance,  # 使用市场特定的滑点容忍度
            slippage_enabled=self.slippage_enabled  # 使用市场特定的滑点开关
        )
        
        if order:
            self._log_signal("SHORT", self.market_id, 
                           price=price, trailing_stop=self.xATRTrailingStop, size=actual_size, size_usd=self.position_size_usd)
            self.last_signal_time = datetime.now().timestamp()
            
    async def _close_position(self, price: float, reason: str):
        """平仓"""
        position = self._get_position(self.market_id)
        if not position:
            return
            
        from ..core.position_manager import PositionSide
        
        # 平仓通常使用市价单以确保快速执行
        close_order_type = "market"
        order_price = price
        
        # 如果配置使用限价单，平仓也可以用限价
        if self.order_type.lower() == "limit":
            if position.side == PositionSide.LONG:
                # 平多仓（卖出）：限价略高于市场价
                order_price = price * (1 + self.limit_price_offset)
            else:
                # 平空仓（买入）：限价略低于市场价
                order_price = price * (1 - self.limit_price_offset)
            close_order_type = "limit"
            self.logger.info(f"限价平仓: 市场价=${price:.4f}, 限价=${order_price:.4f}")
        
        order = self._create_order(
            market_id=self.market_id,
            side="sell" if position.side == PositionSide.LONG else "buy",
            order_type=close_order_type,
            size=position.size,
            price=order_price,
            leverage=self.leverage,
            margin_mode=self.margin_mode,
            price_slippage_tolerance=self.slippage_tolerance,  # 使用市场特定的滑点容忍度
            slippage_enabled=self.slippage_enabled  # 使用市场特定的滑点开关
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
            "position_size_usd": self.position_size_usd,  # 修改为position_size_usd
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "signal_cooldown": self.signal_cooldown,
            "current_trailing_stop": self.xATRTrailingStop,
            "current_position": self.pos
        }
