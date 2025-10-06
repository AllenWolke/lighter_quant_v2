"""
风险管理器
负责风险控制和资金管理
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

from ..utils.config import Config
from ..utils.logger import setup_logger


@dataclass
class RiskLimits:
    """风险限制配置"""
    max_position_size: float = 0.1  # 最大仓位比例
    max_daily_loss: float = 0.05    # 最大日亏损比例
    max_drawdown: float = 0.15      # 最大回撤比例
    max_leverage: float = 10.0      # 最大杠杆
    max_orders_per_minute: int = 10 # 每分钟最大订单数
    max_open_orders: int = 20       # 最大开仓订单数


class RiskManager:
    """风险管理器"""
    
    def __init__(self, config: Config):
        """
        初始化风险管理器
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.logger = setup_logger("RiskManager", config.log_level)
        
        # 风险限制
        self.risk_limits = RiskLimits(
            max_position_size=config.risk_config.get("max_position_size", 0.1),
            max_daily_loss=config.risk_config.get("max_daily_loss", 0.05),
            max_drawdown=config.risk_config.get("max_drawdown", 0.15),
            max_leverage=config.risk_config.get("max_leverage", 10.0),
            max_orders_per_minute=config.risk_config.get("max_orders_per_minute", 10),
            max_open_orders=config.risk_config.get("max_open_orders", 20)
        )
        
        # 风险状态
        self.daily_pnl = 0.0
        self.max_equity = 0.0
        self.current_equity = 0.0
        self.order_count_minute = 0
        self.last_order_time = None
        self.open_orders_count = 0
        
        # 风险事件记录
        self.risk_events: List[Dict[str, Any]] = []
        
    async def initialize(self):
        """初始化风险管理器"""
        self.logger.info("初始化风险管理器...")
        
        # 重置日统计
        self._reset_daily_stats()
        
        self.logger.info("风险管理器初始化完成")
        
    def _reset_daily_stats(self):
        """重置日统计"""
        self.daily_pnl = 0.0
        self.max_equity = 0.0
        self.current_equity = 0.0
        self.order_count_minute = 0
        self.last_order_time = None
        
    async def check_risk_limits(self, market_data: Dict[int, Dict[str, Any]]) -> bool:
        """
        检查风险限制
        
        Args:
            market_data: 市场数据
            
        Returns:
            是否通过风险检查
        """
        try:
            # 更新当前权益
            await self._update_equity()
            
            # 检查各种风险限制
            checks = [
                self._check_daily_loss_limit(),
                self._check_drawdown_limit(),
                self._check_order_frequency_limit(),
                self._check_open_orders_limit()
            ]
            
            # 如果任何检查失败，记录风险事件
            for check_name, passed in checks:
                if not passed:
                    self._record_risk_event(check_name, "风险限制触发")
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.error(f"风险检查失败: {e}")
            return False
            
    def _check_daily_loss_limit(self) -> tuple[str, bool]:
        """检查日亏损限制"""
        if self.current_equity <= 0:
            return "daily_loss", True
            
        daily_loss_ratio = abs(self.daily_pnl) / self.current_equity
        passed = daily_loss_ratio <= self.risk_limits.max_daily_loss
        
        if not passed:
            self.logger.warning(f"日亏损限制触发: {daily_loss_ratio:.2%} > {self.risk_limits.max_daily_loss:.2%}")
            
        return "daily_loss", passed
        
    def _check_drawdown_limit(self) -> tuple[str, bool]:
        """检查回撤限制"""
        if self.max_equity <= 0:
            return "drawdown", True
            
        drawdown_ratio = (self.max_equity - self.current_equity) / self.max_equity
        passed = drawdown_ratio <= self.risk_limits.max_drawdown
        
        if not passed:
            self.logger.warning(f"回撤限制触发: {drawdown_ratio:.2%} > {self.risk_limits.max_drawdown:.2%}")
            
        return "drawdown", passed
        
    def _check_order_frequency_limit(self) -> tuple[str, bool]:
        """检查订单频率限制"""
        current_time = datetime.now()
        
        # 重置分钟计数器
        if (self.last_order_time is None or 
            current_time - self.last_order_time > timedelta(minutes=1)):
            self.order_count_minute = 0
            
        passed = self.order_count_minute < self.risk_limits.max_orders_per_minute
        
        if not passed:
            self.logger.warning(f"订单频率限制触发: {self.order_count_minute} > {self.risk_limits.max_orders_per_minute}")
            
        return "order_frequency", passed
        
    def _check_open_orders_limit(self) -> tuple[str, bool]:
        """检查开仓订单限制"""
        passed = self.open_orders_count < self.risk_limits.max_open_orders
        
        if not passed:
            self.logger.warning(f"开仓订单限制触发: {self.open_orders_count} > {self.risk_limits.max_open_orders}")
            
        return "open_orders", passed
        
    async def _update_equity(self):
        """更新权益信息"""
        # 这里应该从账户数据中获取实际权益
        # 暂时使用模拟数据
        if self.current_equity == 0:
            self.current_equity = 10000.0  # 初始资金
            self.max_equity = self.current_equity
            
        # 更新最大权益
        if self.current_equity > self.max_equity:
            self.max_equity = self.current_equity
            
    def check_position_size(self, market_id: int, size: float, price: float) -> bool:
        """
        检查仓位大小
        
        Args:
            market_id: 市场ID
            size: 仓位大小
            price: 价格
            
        Returns:
            是否通过检查
        """
        if self.current_equity <= 0:
            return False
            
        position_value = size * price
        position_ratio = position_value / self.current_equity
        
        passed = position_ratio <= self.risk_limits.max_position_size
        
        if not passed:
            self.logger.warning(f"仓位大小限制触发: {position_ratio:.2%} > {self.risk_limits.max_position_size:.2%}")
            
        return passed
        
    def check_daily_loss(self, daily_loss_ratio: float) -> bool:
        """
        检查日亏损限制
        
        Args:
            daily_loss_ratio: 日亏损比例
            
        Returns:
            是否通过检查
        """
        passed = abs(daily_loss_ratio) <= self.risk_limits.max_daily_loss
        
        if not passed:
            self.logger.warning(f"日亏损限制触发: {daily_loss_ratio:.2%} > {self.risk_limits.max_daily_loss:.2%}")
            
        return passed
        
    def check_drawdown(self, drawdown_ratio: float) -> bool:
        """
        检查回撤限制
        
        Args:
            drawdown_ratio: 回撤比例
            
        Returns:
            是否通过检查
        """
        passed = drawdown_ratio <= self.risk_limits.max_drawdown
        
        if not passed:
            self.logger.warning(f"回撤限制触发: {drawdown_ratio:.2%} > {self.risk_limits.max_drawdown:.2%}")
            
        return passed
        
    def check_leverage(self, leverage: float) -> bool:
        """
        检查杠杆限制
        
        Args:
            leverage: 杠杆倍数
            
        Returns:
            是否通过检查
        """
        passed = leverage <= self.risk_limits.max_leverage
        
        if not passed:
            self.logger.warning(f"杠杆限制触发: {leverage} > {self.risk_limits.max_leverage}")
            
        return passed
        
    def record_order(self):
        """记录订单"""
        current_time = datetime.now()
        
        # 更新分钟计数器
        if (self.last_order_time is None or 
            current_time - self.last_order_time > timedelta(minutes=1)):
            self.order_count_minute = 1
        else:
            self.order_count_minute += 1
            
        self.last_order_time = current_time
        self.open_orders_count += 1
        
    def record_order_filled(self):
        """记录订单成交"""
        self.open_orders_count = max(0, self.open_orders_count - 1)
        
    def update_pnl(self, pnl: float):
        """
        更新盈亏
        
        Args:
            pnl: 盈亏金额
        """
        self.daily_pnl += pnl
        self.current_equity += pnl
        
        # 更新最大权益
        if self.current_equity > self.max_equity:
            self.max_equity = self.current_equity
            
    def _record_risk_event(self, event_type: str, description: str):
        """记录风险事件"""
        event = {
            "timestamp": datetime.now(),
            "type": event_type,
            "description": description,
            "daily_pnl": self.daily_pnl,
            "current_equity": self.current_equity,
            "max_equity": self.max_equity
        }
        
        self.risk_events.append(event)
        self.logger.warning(f"风险事件: {event_type} - {description}")
        
    def get_risk_status(self) -> Dict[str, Any]:
        """获取风险状态"""
        return {
            "daily_pnl": self.daily_pnl,
            "current_equity": self.current_equity,
            "max_equity": self.max_equity,
            "drawdown": (self.max_equity - self.current_equity) / self.max_equity if self.max_equity > 0 else 0,
            "order_count_minute": self.order_count_minute,
            "open_orders_count": self.open_orders_count,
            "risk_events_count": len(self.risk_events),
            "risk_limits": {
                "max_position_size": self.risk_limits.max_position_size,
                "max_daily_loss": self.risk_limits.max_daily_loss,
                "max_drawdown": self.risk_limits.max_drawdown,
                "max_leverage": self.risk_limits.max_leverage,
                "max_orders_per_minute": self.risk_limits.max_orders_per_minute,
                "max_open_orders": self.risk_limits.max_open_orders
            }
        }
