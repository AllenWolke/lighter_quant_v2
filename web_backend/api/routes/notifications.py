"""
通知路由
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from core.security import get_current_active_user
from models.user import User
from schemas.notification import NotificationCreate, NotificationResponse, NotificationUpdate

router = APIRouter()


@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    skip: int = Query(0, description="跳过条数"),
    limit: int = Query(100, description="限制条数"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取通知列表"""
    # 模拟通知数据
    notifications = [
        {
            "id": 1,
            "notification_type": "trade_executed",
            "title": "交易执行成功",
            "message": "ETH/USDT 买入订单已成交",
            "level": "info",
            "is_read": False,
            "is_sent": True,
            "sent_at": "2024-01-01T12:00:00",
            "created_at": "2024-01-01T12:00:00",
            "data": {"symbol": "ETH/USDT", "side": "buy", "quantity": 0.1}
        },
        {
            "id": 2,
            "notification_type": "stop_loss",
            "title": "止损触发",
            "message": "ETH/USDT 持仓触发止损",
            "level": "warning",
            "is_read": False,
            "is_sent": True,
            "sent_at": "2024-01-01T11:30:00",
            "created_at": "2024-01-01T11:30:00",
            "data": {"symbol": "ETH/USDT", "side": "long", "price": 1900.0}
        }
    ]
    return notifications[skip:skip + limit]


@router.post("/", response_model=NotificationResponse)
async def create_notification(
    notification_data: NotificationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建通知"""
    # 模拟创建通知
    notification = {
        "id": 3,
        "notification_type": notification_data.notification_type,
        "title": notification_data.title,
        "message": notification_data.message,
        "level": notification_data.level,
        "is_read": False,
        "is_sent": False,
        "sent_at": None,
        "created_at": "2024-01-01T12:00:00",
        "data": notification_data.data
    }
    return notification


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取通知详情"""
    # 模拟通知详情
    notification = {
        "id": notification_id,
        "notification_type": "trade_executed",
        "title": "交易执行成功",
        "message": "ETH/USDT 买入订单已成交",
        "level": "info",
        "is_read": False,
        "is_sent": True,
        "sent_at": "2024-01-01T12:00:00",
        "created_at": "2024-01-01T12:00:00",
        "data": {"symbol": "ETH/USDT", "side": "buy", "quantity": 0.1}
    }
    return notification


@router.put("/{notification_id}", response_model=NotificationResponse)
async def update_notification(
    notification_id: int,
    notification_data: NotificationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新通知"""
    # 模拟更新通知
    notification = {
        "id": notification_id,
        "notification_type": "trade_executed",
        "title": "交易执行成功",
        "message": "ETH/USDT 买入订单已成交",
        "level": "info",
        "is_read": notification_data.is_read if notification_data.is_read is not None else False,
        "is_sent": notification_data.is_sent if notification_data.is_sent is not None else True,
        "sent_at": "2024-01-01T12:00:00",
        "created_at": "2024-01-01T12:00:00",
        "data": {"symbol": "ETH/USDT", "side": "buy", "quantity": 0.1}
    }
    return notification


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除通知"""
    return {"message": "通知删除成功"}


@router.post("/mark-all-read")
async def mark_all_read(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """标记所有通知为已读"""
    return {"message": "所有通知已标记为已读"}
