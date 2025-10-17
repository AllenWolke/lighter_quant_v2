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
                 lookback_period: int = 20, threshold: float = 2.0,
                 position_size: float = None,
                 stop_loss: float = None,
                 take_profit: float = None,
                 leverage: float = None,
                 margin_mode: str = None,
                 order_type: str = None,
                 limit_price_offset: float = None):
        """
        初始化均值回归策略
        
        Args:
            config: 配置对象
            market_id: 市场ID
            lookback_period: 回望周期
            threshold: 阈值倍数
            position_size: 仓位大小（如果为None，从config读取）
            stop_loss: 止损比例（如果为None，从config读取）
            take_profit: 止盈比例（如果为None，从config读取）
            leverage: 杠杆倍数（如果为None，从config读取）
            margin_mode: 保证金模式（如果为None，从config读取）
            order_type: 订单类型 market/limit（如果为None，从config读取）
            limit_price_offset: 限价单价格偏移百分比（如果为None，从config读取）
        """
        super().__init__("MeanReversion", config)
        
        self.market_id = market_id
        self.lookback_period = lookback_period
        self.threshold = threshold
        
        # 策略参数 - 优先使用传入的参数，否则从config读取
        mr_config = config.strategies.get('mean_reversion', {}) if hasattr(config, 'strategies') else {}
        self.position_size_usd = position_size if position_size is not None else mr_config.get('position_size', 10.0)  # 改为USD金额
        self.stop_loss = stop_loss if stop_loss is not None else mr_config.get('stop_loss', 0.02)
        self.take_profit = take_profit if take_profit is not None else mr_config.get('take_profit', 0.01)
        self.leverage = leverage if leverage is not None else mr_config.get('leverage', 1.0)
        self.margin_mode = margin_mode if margin_mode is not None else mr_config.get('margin_mode', 'cross')
        self.order_type = order_type if order_type is not None else mr_config.get('order_type', 'market')
        self.limit_price_offset = limit_price_offset if limit_price_offset is not None else mr_config.get('limit_price_offset', 0.001)
        self.price_slippage_tolerance = mr_config.get('price_slippage_tolerance', 0.01)  # 价格滑点容忍度，默认1%
        
        # ⭐ 新需求：市场级止盈止损配置
        self.market_risk_config = getattr(config, 'data_sources', {}).get('market_risk_config', {})
        market_risk = self.market_risk_config.get(self.market_id, {})
        self.market_stop_loss_enabled = market_risk.get('stop_loss_enabled', True)
        self.market_stop_loss = market_risk.get('stop_loss', self.stop_loss)
        self.market_take_profit_enabled = market_risk.get('take_profit_enabled', True)
        self.market_take_profit = market_risk.get('take_profit', self.take_profit)
        
        self.logger.info(f"市场 {self.market_id} 风险配置: 止损={'开启' if self.market_stop_loss_enabled else '关闭'}({self.market_stop_loss*100:.1f}%), 止盈={'开启' if self.market_take_profit_enabled else '关闭'}({self.market_take_profit*100:.1f}%)")
        
        self.logger.info(f"策略配置: position_size=${self.position_size_usd} USD (将根据市场价格自动计算加密货币数量)")
        self.logger.info(f"滑点容忍度: {self.price_slippage_tolerance*100:.2f}% (可在config.yaml中调整)")
    
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
            # 已有仓位，先检查市场级止盈止损
            await self._check_market_level_risk_management(current_price)
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
        # ⭐ 新增：检查是否有反向持仓（空仓），如果有则先平仓
        position = self._get_position(self.market_id)
        if position:
            from ..core.position_manager import PositionSide
            if position.side == PositionSide.SHORT:
                self.logger.warning(f"⚠️  检测到反向持仓（空仓），先平仓再开多仓")
                await self._close_position(price, z_score, "信号反向：从空仓转为多仓")
                # 等待平仓完成
                import asyncio
                await asyncio.sleep(0.5)
        
        # 将USD金额转换为实际的加密货币数量
        actual_size = self.position_size_usd / price
        self.logger.info(f"开仓计算: ${self.position_size_usd} USD ÷ ${price:.6f} = {actual_size:.6f} 加密货币")
        
        if not self._check_risk_limits(self.market_id, actual_size, price):
            return
        
        # 根据配置的订单类型决定价格
        order_price = price
        if self.order_type.lower() == "limit":
            # 限价单：买入价格略低于市场价
            order_price = price * (1 - self.limit_price_offset)
            self.logger.info(f"限价买单: 市场价=${price:.4f}, 限价=${order_price:.4f} (偏移-{self.limit_price_offset*100:.2f}%)")
        
        # 创建订单
        order = self._create_order(
            market_id=self.market_id,
            side="buy",
            order_type=self.order_type,
            size=actual_size,  # 使用计算后的实际数量
            price=order_price,
            leverage=self.leverage,
            margin_mode=self.margin_mode,
            price_slippage_tolerance=self.price_slippage_tolerance  # 使用策略配置的滑点容忍度
        )
        
        if order:
            self._log_signal("LONG", self.market_id, 
                           price=price, z_score=z_score, size=actual_size, size_usd=self.position_size_usd)
            self.last_signal_time = datetime.now()
            
    async def _open_short_position(self, price: float, z_score: float):
        """开空仓"""
        # ⭐ 新增：检查是否有反向持仓（多仓），如果有则先平仓
        position = self._get_position(self.market_id)
        if position:
            from ..core.position_manager import PositionSide
            if position.side == PositionSide.LONG:
                self.logger.warning(f"⚠️  检测到反向持仓（多仓），先平仓再开空仓")
                await self._close_position(price, z_score, "信号反向：从多仓转为空仓")
                # 等待平仓完成
                import asyncio
                await asyncio.sleep(0.5)
        
        # 将USD金额转换为实际的加密货币数量
        actual_size = self.position_size_usd / price
        self.logger.info(f"开仓计算: ${self.position_size_usd} USD ÷ ${price:.6f} = {actual_size:.6f} 加密货币")
        
        if not self._check_risk_limits(self.market_id, actual_size, price):
            return
        
        # 根据配置的订单类型决定价格
        order_price = price
        if self.order_type.lower() == "limit":
            # 限价单：卖出价格略高于市场价
            order_price = price * (1 + self.limit_price_offset)
            self.logger.info(f"限价卖单: 市场价=${price:.4f}, 限价=${order_price:.4f} (偏移+{self.limit_price_offset*100:.2f}%)")
        
        # 创建订单
        order = self._create_order(
            market_id=self.market_id,
            side="sell",
            order_type=self.order_type,
            size=actual_size,  # 使用计算后的实际数量
            price=order_price,
            leverage=self.leverage,
            margin_mode=self.margin_mode,
            price_slippage_tolerance=self.price_slippage_tolerance  # 使用策略配置的滑点容忍度
        )
        
        if order:
            self._log_signal("SHORT", self.market_id, 
                           price=price, z_score=z_score, size=actual_size, size_usd=self.position_size_usd)
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
                price=current_price,
                leverage=self.leverage,
                margin_mode=self.margin_mode
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
            "position_size_usd": self.position_size_usd,  # 修改为position_size_usd
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "signal_cooldown": self.signal_cooldown.total_seconds()
        }
