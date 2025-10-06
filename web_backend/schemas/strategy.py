"""
策略相关的数据模式
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class StrategyCreate(BaseModel):
    """创建策略请求"""
    name: str = Field(..., min_length=1, max_length=100, description="策略名称")
    strategy_type: str = Field(..., description="策略类型")
    description: Optional[str] = Field(None, max_length=500, description="策略描述")
    parameters: Optional[Dict[str, Any]] = Field(None, description="策略参数")


class StrategyResponse(BaseModel):
    """策略响应"""
    id: int
    name: str
    strategy_type: str
    description: Optional[str]
    is_active: bool
    is_enabled: bool
    created_at: datetime
    updated_at: datetime
    last_run_at: Optional[datetime]
    total_trades: int
    winning_trades: int
    total_pnl: float

    class Config:
        from_attributes = True


class StrategyParameter(BaseModel):
    """策略参数"""
    id: int
    strategy_id: int
    parameter_name: str
    parameter_value: str
    parameter_type: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StrategyUpdate(BaseModel):
    """更新策略请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="策略名称")
    description: Optional[str] = Field(None, max_length=500, description="策略描述")
    is_active: Optional[bool] = Field(None, description="是否激活")
    is_enabled: Optional[bool] = Field(None, description="是否启用")
    parameters: Optional[Dict[str, Any]] = Field(None, description="策略参数")
