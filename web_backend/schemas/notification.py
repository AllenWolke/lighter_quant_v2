"""
通知相关的数据模式
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class NotificationType(str, Enum):
    TRADE_EXECUTED = "trade_executed"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    SYSTEM_ERROR = "system_error"
    RISK_LIMIT = "risk_limit"


class NotificationLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class NotificationCreate(BaseModel):
    """创建通知请求"""
    notification_type: NotificationType = Field(..., description="通知类型")
    title: str = Field(..., min_length=1, max_length=200, description="标题")
    message: str = Field(..., min_length=1, max_length=1000, description="消息内容")
    level: NotificationLevel = Field(..., description="通知级别")
    data: Optional[Dict[str, Any]] = Field(None, description="附加数据")


class NotificationResponse(BaseModel):
    """通知响应"""
    id: int
    notification_type: str
    title: str
    message: str
    level: str
    is_read: bool
    is_sent: bool
    sent_at: Optional[datetime]
    created_at: datetime
    data: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class NotificationUpdate(BaseModel):
    """更新通知请求"""
    is_read: Optional[bool] = Field(None, description="是否已读")
    is_sent: Optional[bool] = Field(None, description="是否已发送")
