"""
通知基类
定义所有通知方式的通用接口
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class NotificationType(Enum):
    """通知类型"""
    TRADE_EXECUTED = "trade_executed"      # 交易执行
    TRADE_FILLED = "trade_filled"          # 交易成交
    STOP_LOSS_TRIGGERED = "stop_loss"      # 止损触发
    TAKE_PROFIT_TRIGGERED = "take_profit"  # 止盈触发
    RISK_LIMIT_EXCEEDED = "risk_limit"     # 风险限制
    SYSTEM_ERROR = "system_error"          # 系统错误
    STRATEGY_SIGNAL = "strategy_signal"    # 策略信号
    ACCOUNT_ALERT = "account_alert"        # 账户警告


class NotificationLevel(Enum):
    """通知级别"""
    INFO = "info"        # 信息
    WARNING = "warning"  # 警告
    ERROR = "error"      # 错误
    CRITICAL = "critical" # 严重


class Notification:
    """通知消息"""
    
    def __init__(self, 
                 notification_type: NotificationType,
                 level: NotificationLevel,
                 title: str,
                 message: str,
                 data: Optional[Dict[str, Any]] = None):
        """
        初始化通知消息
        
        Args:
            notification_type: 通知类型
            level: 通知级别
            title: 通知标题
            message: 通知内容
            data: 附加数据
        """
        self.notification_type = notification_type
        self.level = level
        self.title = title
        self.message = message
        self.data = data or {}
        self.timestamp = datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "type": self.notification_type.value,
            "level": self.level.value,
            "title": self.title,
            "message": self.message,
            "data": self.data,
            "timestamp": self.timestamp.isoformat()
        }
        
    def __str__(self):
        return f"[{self.level.value.upper()}] {self.title}: {self.message}"


class BaseNotifier(ABC):
    """通知基类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化通知器
        
        Args:
            config: 通知配置
        """
        self.config = config
        self.enabled = config.get("enabled", True)
        
    @abstractmethod
    async def send_notification(self, notification: Notification) -> bool:
        """
        发送通知
        
        Args:
            notification: 通知消息
            
        Returns:
            是否发送成功
        """
        pass
        
    @abstractmethod
    async def send_batch_notifications(self, notifications: List[Notification]) -> bool:
        """
        批量发送通知
        
        Args:
            notifications: 通知消息列表
            
        Returns:
            是否发送成功
        """
        pass
        
    def is_enabled(self) -> bool:
        """检查是否启用"""
        return self.enabled
        
    def should_send(self, notification: Notification) -> bool:
        """
        检查是否应该发送通知
        
        Args:
            notification: 通知消息
            
        Returns:
            是否应该发送
        """
        if not self.enabled:
            return False
            
        # 检查通知级别过滤
        min_level = self.config.get("min_level", "info")
        level_priority = {
            "info": 1,
            "warning": 2, 
            "error": 3,
            "critical": 4
        }
        
        if level_priority.get(notification.level.value, 0) < level_priority.get(min_level, 1):
            return False
            
        # 检查通知类型过滤
        allowed_types = self.config.get("allowed_types", [])
        if allowed_types and notification.notification_type.value not in allowed_types:
            return False
            
        return True
