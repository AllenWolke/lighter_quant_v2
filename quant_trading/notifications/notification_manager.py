"""
通知管理器
统一管理所有通知方式
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import deque

from .base_notifier import BaseNotifier, Notification, NotificationType, NotificationLevel
from .email_notifier import EmailNotifier


class NotificationManager:
    """通知管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化通知管理器
        
        Args:
            config: 通知配置
        """
        self.config = config
        self.logger = logging.getLogger("NotificationManager")
        
        # 初始化通知器
        self.notifiers: Dict[str, BaseNotifier] = {}
        self._initialize_notifiers()
        
        # 通知队列和批处理
        self.notification_queue = deque()
        self.batch_size = config.get("batch_size", 10)
        self.batch_interval = config.get("batch_interval", 60)  # 秒
        self.last_batch_time = datetime.now()
        
        # 通知历史（用于去重和限制频率）
        self.notification_history = deque(maxlen=1000)
        self.rate_limits = config.get("rate_limits", {})
        
        # 启动批处理任务
        self._batch_task = None
        self._start_batch_processor()
        
    def _initialize_notifiers(self):
        """初始化通知器"""
        # 邮件通知器
        email_config = self.config.get("email", {})
        if email_config.get("enabled", False):
            self.notifiers["email"] = EmailNotifier(email_config)
            self.logger.info("邮件通知器已启用")
        
        # 可以在这里添加其他通知器
        # self.notifiers["sms"] = SMSNotifier(sms_config)
        # self.notifiers["webhook"] = WebhookNotifier(webhook_config)
        
        if not self.notifiers:
            self.logger.warning("没有启用的通知器")
    
    def _start_batch_processor(self):
        """启动批处理任务"""
        if self.batch_size > 1:
            self._batch_task = asyncio.create_task(self._process_batch_notifications())
    
    async def _process_batch_notifications(self):
        """处理批量通知"""
        while True:
            try:
                await asyncio.sleep(self.batch_interval)
                
                if len(self.notification_queue) >= self.batch_size or \
                   (self.notification_queue and 
                    datetime.now() - self.last_batch_time > timedelta(seconds=self.batch_interval)):
                    
                    # 获取批量通知
                    batch_notifications = []
                    for _ in range(min(self.batch_size, len(self.notification_queue))):
                        if self.notification_queue:
                            batch_notifications.append(self.notification_queue.popleft())
                    
                    if batch_notifications:
                        await self._send_batch_notifications(batch_notifications)
                        self.last_batch_time = datetime.now()
                        
            except Exception as e:
                self.logger.error(f"批处理任务错误: {e}")
    
    async def send_notification(self, 
                              notification_type: NotificationType,
                              level: NotificationLevel,
                              title: str,
                              message: str,
                              data: Optional[Dict[str, Any]] = None,
                              immediate: bool = False) -> bool:
        """
        发送通知
        
        Args:
            notification_type: 通知类型
            level: 通知级别
            title: 通知标题
            message: 通知内容
            data: 附加数据
            immediate: 是否立即发送
            
        Returns:
            是否发送成功
        """
        # 创建通知对象
        notification = Notification(
            notification_type=notification_type,
            level=level,
            title=title,
            message=message,
            data=data or {}
        )
        
        # 检查是否应该发送
        if not self._should_send_notification(notification):
            return True
        
        # 添加到历史记录
        self.notification_history.append(notification)
        
        # 立即发送或加入队列
        if immediate or self.batch_size <= 1:
            return await self._send_notification(notification)
        else:
            self.notification_queue.append(notification)
            return True
    
    async def _send_notification(self, notification: Notification) -> bool:
        """发送单个通知"""
        success_count = 0
        total_count = len(self.notifiers)
        
        for name, notifier in self.notifiers.items():
            try:
                if await notifier.send_notification(notification):
                    success_count += 1
            except Exception as e:
                self.logger.error(f"通知器 {name} 发送失败: {e}")
        
        success_rate = success_count / total_count if total_count > 0 else 0
        self.logger.info(f"通知发送完成: {success_count}/{total_count} 成功")
        
        return success_rate > 0.5  # 至少一半成功
    
    async def _send_batch_notifications(self, notifications: List[Notification]) -> bool:
        """发送批量通知"""
        success_count = 0
        total_count = len(self.notifiers)
        
        for name, notifier in self.notifiers.items():
            try:
                if await notifier.send_batch_notifications(notifications):
                    success_count += 1
            except Exception as e:
                self.logger.error(f"通知器 {name} 批量发送失败: {e}")
        
        success_rate = success_count / total_count if total_count > 0 else 0
        self.logger.info(f"批量通知发送完成: {success_count}/{total_count} 成功")
        
        return success_rate > 0.5
    
    def _should_send_notification(self, notification: Notification) -> bool:
        """检查是否应该发送通知"""
        # 检查频率限制
        if self._is_rate_limited(notification):
            return False
        
        # 检查重复通知
        if self._is_duplicate_notification(notification):
            return False
        
        return True
    
    def _is_rate_limited(self, notification: Notification) -> bool:
        """检查是否被频率限制"""
        rate_limit_config = self.rate_limits.get(notification.notification_type.value, {})
        if not rate_limit_config:
            return False
        
        # 检查时间窗口内的通知数量
        time_window = rate_limit_config.get("time_window", 300)  # 5分钟
        max_count = rate_limit_config.get("max_count", 10)
        
        cutoff_time = datetime.now() - timedelta(seconds=time_window)
        recent_notifications = [
            n for n in self.notification_history
            if n.notification_type == notification.notification_type and
               n.timestamp > cutoff_time
        ]
        
        return len(recent_notifications) >= max_count
    
    def _is_duplicate_notification(self, notification: Notification) -> bool:
        """检查是否是重复通知"""
        # 检查最近5分钟内是否有相同的通知
        cutoff_time = datetime.now() - timedelta(minutes=5)
        recent_notifications = [
            n for n in self.notification_history
            if n.notification_type == notification.notification_type and
               n.title == notification.title and
               n.timestamp > cutoff_time
        ]
        
        return len(recent_notifications) > 0
    
    # 便捷方法
    async def send_trade_executed(self, symbol: str, side: str, quantity: float, price: float, **kwargs):
        """发送交易执行通知"""
        return await self.send_notification(
            notification_type=NotificationType.TRADE_EXECUTED,
            level=NotificationLevel.INFO,
            title=f"交易执行 - {symbol}",
            message=f"{side} {quantity} {symbol} @ {price}",
            data={
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "price": price,
                **kwargs
            }
        )
    
    async def send_stop_loss_triggered(self, symbol: str, price: float, **kwargs):
        """发送止损触发通知"""
        return await self.send_notification(
            notification_type=NotificationType.STOP_LOSS_TRIGGERED,
            level=NotificationLevel.WARNING,
            title=f"止损触发 - {symbol}",
            message=f"{symbol} 价格 {price} 触发止损",
            data={
                "symbol": symbol,
                "price": price,
                **kwargs
            }
        )
    
    async def send_take_profit_triggered(self, symbol: str, price: float, **kwargs):
        """发送止盈触发通知"""
        return await self.send_notification(
            notification_type=NotificationType.TAKE_PROFIT_TRIGGERED,
            level=NotificationLevel.INFO,
            title=f"止盈触发 - {symbol}",
            message=f"{symbol} 价格 {price} 触发止盈",
            data={
                "symbol": symbol,
                "price": price,
                **kwargs
            }
        )
    
    async def send_risk_limit_exceeded(self, risk_type: str, current_value: float, limit_value: float, **kwargs):
        """发送风险限制超出通知"""
        return await self.send_notification(
            notification_type=NotificationType.RISK_LIMIT_EXCEEDED,
            level=NotificationLevel.ERROR,
            title=f"风险限制超出 - {risk_type}",
            message=f"{risk_type} 当前值 {current_value} 超出限制 {limit_value}",
            data={
                "risk_type": risk_type,
                "current_value": current_value,
                "limit_value": limit_value,
                **kwargs
            }
        )
    
    async def send_system_error(self, error_message: str, **kwargs):
        """发送系统错误通知"""
        return await self.send_notification(
            notification_type=NotificationType.SYSTEM_ERROR,
            level=NotificationLevel.CRITICAL,
            title="系统错误",
            message=error_message,
            data=kwargs
        )
    
    async def send_strategy_signal(self, strategy_name: str, signal: str, **kwargs):
        """发送策略信号通知"""
        return await self.send_notification(
            notification_type=NotificationType.STRATEGY_SIGNAL,
            level=NotificationLevel.INFO,
            title=f"策略信号 - {strategy_name}",
            message=f"{strategy_name} 产生信号: {signal}",
            data={
                "strategy_name": strategy_name,
                "signal": signal,
                **kwargs
            }
        )
    
    async def send_account_alert(self, alert_type: str, message: str, **kwargs):
        """发送账户警告通知"""
        return await self.send_notification(
            notification_type=NotificationType.ACCOUNT_ALERT,
            level=NotificationLevel.WARNING,
            title=f"账户警告 - {alert_type}",
            message=message,
            data={
                "alert_type": alert_type,
                **kwargs
            }
        )
    
    async def close(self):
        """关闭通知管理器"""
        if self._batch_task:
            self._batch_task.cancel()
            try:
                await self._batch_task
            except asyncio.CancelledError:
                pass
        
        # 发送队列中剩余的通知
        if self.notification_queue:
            await self._send_batch_notifications(list(self.notification_queue))
            self.notification_queue.clear()
        
        self.logger.info("通知管理器已关闭")
