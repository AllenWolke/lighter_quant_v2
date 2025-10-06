"""
策略路由
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from core.security import get_current_active_user
from models.user import User
from schemas.strategy import StrategyCreate, StrategyResponse, StrategyUpdate

router = APIRouter()


@router.get("/", response_model=List[StrategyResponse])
async def get_strategies(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取策略列表"""
    # 模拟策略数据
    strategies = [
        {
            "id": 1,
            "name": "UT Bot策略",
            "strategy_type": "ut_bot",
            "description": "基于UT Bot的交易策略",
            "is_active": True,
            "is_enabled": True,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
            "last_run_at": "2024-01-01T12:00:00",
            "total_trades": 50,
            "winning_trades": 30,
            "total_pnl": 1000.0
        }
    ]
    return strategies


@router.post("/", response_model=StrategyResponse)
async def create_strategy(
    strategy_data: StrategyCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建策略"""
    # 模拟创建策略
    strategy = {
        "id": 2,
        "name": strategy_data.name,
        "strategy_type": strategy_data.strategy_type,
        "description": strategy_data.description,
        "is_active": False,
        "is_enabled": True,
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
        "last_run_at": None,
        "total_trades": 0,
        "winning_trades": 0,
        "total_pnl": 0.0
    }
    return strategy


@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取策略详情"""
    # 模拟策略详情
    strategy = {
        "id": strategy_id,
        "name": "UT Bot策略",
        "strategy_type": "ut_bot",
        "description": "基于UT Bot的交易策略",
        "is_active": True,
        "is_enabled": True,
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
        "last_run_at": "2024-01-01T12:00:00",
        "total_trades": 50,
        "winning_trades": 30,
        "total_pnl": 1000.0
    }
    return strategy


@router.put("/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(
    strategy_id: int,
    strategy_data: StrategyUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新策略"""
    # 模拟更新策略
    strategy = {
        "id": strategy_id,
        "name": strategy_data.name or "UT Bot策略",
        "strategy_type": "ut_bot",
        "description": strategy_data.description or "基于UT Bot的交易策略",
        "is_active": strategy_data.is_active if strategy_data.is_active is not None else True,
        "is_enabled": strategy_data.is_enabled if strategy_data.is_enabled is not None else True,
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
        "last_run_at": "2024-01-01T12:00:00",
        "total_trades": 50,
        "winning_trades": 30,
        "total_pnl": 1000.0
    }
    return strategy


@router.delete("/{strategy_id}")
async def delete_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除策略"""
    return {"message": "策略删除成功"}


@router.post("/{strategy_id}/start")
async def start_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """启动策略"""
    return {"message": "策略启动成功"}


@router.post("/{strategy_id}/stop")
async def stop_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """停止策略"""
    return {"message": "策略停止成功"}
