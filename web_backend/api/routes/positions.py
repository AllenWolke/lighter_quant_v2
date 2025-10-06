"""
持仓路由
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from core.security import get_current_active_user
from models.user import User
from schemas.position import PositionCreate, PositionResponse, PositionUpdate

router = APIRouter()


@router.get("/", response_model=List[PositionResponse])
async def get_positions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取持仓列表"""
    # 模拟持仓数据
    positions = [
        {
            "id": 1,
            "symbol": "ETH/USDT",
            "side": "long",
            "quantity": 1.0,
            "entry_price": 2000.0,
            "current_price": 2100.0,
            "unrealized_pnl": 100.0,
            "pnl_ratio": 5.0,
            "margin": 200.0,
            "leverage": 10.0,
            "stop_loss_price": 1900.0,
            "take_profit_price": 2200.0,
            "is_active": True,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }
    ]
    return positions


@router.post("/", response_model=PositionResponse)
async def create_position(
    position_data: PositionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建持仓"""
    # 模拟创建持仓
    position = {
        "id": 2,
        "symbol": position_data.symbol,
        "side": position_data.side,
        "quantity": position_data.quantity,
        "entry_price": position_data.entry_price,
        "current_price": position_data.entry_price,
        "unrealized_pnl": 0.0,
        "pnl_ratio": 0.0,
        "margin": position_data.entry_price * position_data.quantity / position_data.leverage,
        "leverage": position_data.leverage,
        "stop_loss_price": position_data.stop_loss_price,
        "take_profit_price": position_data.take_profit_price,
        "is_active": True,
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00"
    }
    return position


@router.get("/{position_id}", response_model=PositionResponse)
async def get_position(
    position_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取持仓详情"""
    # 模拟持仓详情
    position = {
        "id": position_id,
        "symbol": "ETH/USDT",
        "side": "long",
        "quantity": 1.0,
        "entry_price": 2000.0,
        "current_price": 2100.0,
        "unrealized_pnl": 100.0,
        "pnl_ratio": 5.0,
        "margin": 200.0,
        "leverage": 10.0,
        "stop_loss_price": 1900.0,
        "take_profit_price": 2200.0,
        "is_active": True,
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00"
    }
    return position


@router.put("/{position_id}", response_model=PositionResponse)
async def update_position(
    position_id: int,
    position_data: PositionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新持仓"""
    # 模拟更新持仓
    position = {
        "id": position_id,
        "symbol": "ETH/USDT",
        "side": "long",
        "quantity": 1.0,
        "entry_price": 2000.0,
        "current_price": 2100.0,
        "unrealized_pnl": 100.0,
        "pnl_ratio": 5.0,
        "margin": 200.0,
        "leverage": 10.0,
        "stop_loss_price": position_data.stop_loss_price or 1900.0,
        "take_profit_price": position_data.take_profit_price or 2200.0,
        "is_active": position_data.is_active if position_data.is_active is not None else True,
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00"
    }
    return position


@router.delete("/{position_id}")
async def close_position(
    position_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """平仓"""
    return {"message": "持仓平仓成功"}
