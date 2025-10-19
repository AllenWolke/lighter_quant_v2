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
                 momentum_threshold: float = 0.02,
                 position_size: float = None,
                 stop_loss: float = None,
                 take_profit: float = None):
        """
        初始化动量策略
        
        Args:
            config: 配置对象
            market_id: 市场ID
            short_period: 短期周期
            long_period: 长期周期
            momentum_threshold: 动量阈值
            position_size: 仓位大小（如果为None，从config读取）
            stop_loss: 止损比例（如果为None，从config读取）
            take_profit: 止盈比例（如果为None，从config读取）
        """
        super().__init__("Momentum", config)
        
        self.market_id = market_id
        self.short_period = short_period
        self.long_period = long_period
        self.momentum_threshold = momentum_threshold
        
        # 策略参数 - 优先使用传入的参数，否则从config读取
        mom_config = config.strategies.get('momentum', {}) if hasattr(config, 'strategies') else {}
        self.position_size_usd = position_size if position_size is not None else mom_config.get('position_size', 10.0)  # 改为USD金额
        self.stop_loss = stop_loss if stop_loss is not None else mom_config.get('stop_loss', 0.03)
        self.take_profit = take_profit if take_profit is not None else mom_config.get('take_profit', 0.05)
        self.price_slippage_tolerance = mom_config.get('price_slippage_tolerance', 0.01)  # 价格滑点容忍度，默认1%
        
        # ⭐ 市场级止盈止损配置（仅使用策略级别的配置）
        self.market_risk_config = mom_config.get('market_risk_config', {})
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
        config_slippage = mom_config.get('market_slippage_config', {})
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
        
        # ⭐ 需求①：K线类型配置
        self.kline_types = mom_config.get('kline_types', [1])  # 默认只对1分钟K线发出信号
        self.logger.info(f"K线类型配置: {self.kline_types}分钟 - 策略将对这些时间周期的K线发出交易信号")
        
        self.logger.info(f"策略配置: position_size=${self.position_size_usd} USD (将根据市场价格自动计算加密货币数量)")
        self.logger.info(f"市场 {self.market_id} 滑点配置: {'开启' if self.slippage_enabled else '关闭'}, 容忍度={self.slippage_tolerance*100:.2f}%")
    
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
            # 已有仓位，先检查市场级止盈止损
            await self._check_market_level_risk_management(current_price)
            # 再检查策略级别的平仓条件
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
        # ⭐ 新增：检查是否有反向持仓（空仓），如果有则先平仓
        position = self._get_position(self.market_id)
        if position:
            from ..core.position_manager import PositionSide
            if position.side == PositionSide.SHORT:
                self.logger.warning(f"⚠️  检测到反向持仓（空仓），先平仓再开多仓")
                await self._close_position(price, momentum, "信号反向：从空仓转为多仓")
                # 等待平仓完成
                import asyncio
                await asyncio.sleep(0.5)
        
        # 将USD金额转换为实际的加密货币数量
        actual_size = self.position_size_usd / price
        self.logger.info(f"开仓计算: ${self.position_size_usd} USD ÷ ${price:.6f} = {actual_size:.6f} 加密货币")
        
        if not self._check_risk_limits(self.market_id, actual_size, price):
            return
            
        # 创建订单
        order = self._create_order(
            market_id=self.market_id,
            side="buy",
            order_type="market",
            size=actual_size,  # 使用计算后的实际数量
            price=price,
            price_slippage_tolerance=self.slippage_tolerance,  # 使用市场特定的滑点容忍度
            slippage_enabled=self.slippage_enabled  # 使用市场特定的滑点开关
        )
        
        if order:
            self._log_signal("LONG", self.market_id, 
                           price=price, momentum=momentum, size=actual_size, size_usd=self.position_size_usd)
            self.last_signal_time = datetime.now()
            
    async def _open_short_position(self, price: float, momentum: float):
        """开空仓"""
        # ⭐ 新增：检查是否有反向持仓（多仓），如果有则先平仓
        position = self._get_position(self.market_id)
        if position:
            from ..core.position_manager import PositionSide
            if position.side == PositionSide.LONG:
                self.logger.warning(f"⚠️  检测到反向持仓（多仓），先平仓再开空仓")
                await self._close_position(price, momentum, "信号反向：从多仓转为空仓")
                # 等待平仓完成
                import asyncio
                await asyncio.sleep(0.5)
        
        # 将USD金额转换为实际的加密货币数量
        actual_size = self.position_size_usd / price
        self.logger.info(f"开仓计算: ${self.position_size_usd} USD ÷ ${price:.6f} = {actual_size:.6f} 加密货币")
        
        if not self._check_risk_limits(self.market_id, actual_size, price):
            return
            
        # 创建订单
        order = self._create_order(
            market_id=self.market_id,
            side="sell",
            order_type="market",
            size=actual_size,  # 使用计算后的实际数量
            price=price,
            price_slippage_tolerance=self.slippage_tolerance,  # 使用市场特定的滑点容忍度
            slippage_enabled=self.slippage_enabled  # 使用市场特定的滑点开关
        )
        
        if order:
            self._log_signal("SHORT", self.market_id, 
                           price=price, momentum=momentum, size=actual_size, size_usd=self.position_size_usd)
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
                price=current_price,
                price_slippage_tolerance=self.slippage_tolerance,  # 使用市场特定的滑点容忍度
                slippage_enabled=self.slippage_enabled  # 使用市场特定的滑点开关
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
            "position_size_usd": self.position_size_usd,  # 修改为position_size_usd
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "signal_cooldown": self.signal_cooldown.total_seconds()
        }
