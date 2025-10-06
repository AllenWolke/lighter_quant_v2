"""
持仓相关的数据模式
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PositionCreate(BaseModel):
    """创建持仓请求"""
    symbol: str = Field(..., description="交易对")
    side: str = Field(..., description="持仓方向")
    quantity: float = Field(..., gt=0, description="数量")
    entry_price: float = Field(..., gt=0, description="入场价格")
    leverage: float = Field(..., gt=0, description="杠杆倍数")
    stop_loss_price: Optional[float] = Field(None, gt=0, description="止损价格")
    take_profit_price: Optional[float] = Field(None, gt=0, description="止盈价格")


class PositionResponse(BaseModel):
    """持仓响应"""
    id: int
    symbol: str
    side: str
    quantity: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    pnl_ratio: float
    margin: float
    leverage: float
    stop_loss_price: Optional[float]
    take_profit_price: Optional[float]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PositionUpdate(BaseModel):
    """更新持仓请求"""
    stop_loss_price: Optional[float] = Field(None, gt=0, description="止损价格")
    take_profit_price: Optional[float] = Field(None, gt=0, description="止盈价格")
    is_active: Optional[bool] = Field(None, description="是否激活")
