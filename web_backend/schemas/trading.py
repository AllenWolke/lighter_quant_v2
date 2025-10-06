"""
交易相关的数据模式
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class TradeSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


class OrderStatus(str, Enum):
    PENDING = "pending"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class TradeCreate(BaseModel):
    """创建交易请求"""
    symbol: str = Field(..., description="交易对")
    side: TradeSide = Field(..., description="交易方向")
    order_type: OrderType = Field(..., description="订单类型")
    quantity: float = Field(..., gt=0, description="数量")
    price: Optional[float] = Field(None, gt=0, description="价格")
    stop_price: Optional[float] = Field(None, gt=0, description="止损价格")
    strategy_id: Optional[int] = Field(None, description="策略ID")


class TradeResponse(BaseModel):
    """交易响应"""
    id: int
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: float
    fee: float
    pnl: float
    status: str
    strategy_id: Optional[int]
    order_id: str
    created_at: datetime
    updated_at: datetime
    filled_at: Optional[datetime]
    remark: Optional[str]

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    """创建订单请求"""
    symbol: str = Field(..., description="交易对")
    side: TradeSide = Field(..., description="交易方向")
    order_type: OrderType = Field(..., description="订单类型")
    quantity: float = Field(..., gt=0, description="数量")
    price: Optional[float] = Field(None, gt=0, description="价格")
    stop_price: Optional[float] = Field(None, gt=0, description="止损价格")
    strategy_id: Optional[int] = Field(None, description="策略ID")


class OrderResponse(BaseModel):
    """订单响应"""
    id: int
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: Optional[float]
    stop_price: Optional[float]
    filled_quantity: float
    remaining_quantity: float
    status: str
    strategy_id: Optional[int]
    order_id: str
    created_at: datetime
    updated_at: datetime
    cancelled_at: Optional[datetime]
    remark: Optional[str]

    class Config:
        from_attributes = True


class TradingStats(BaseModel):
    """交易统计"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    total_pnl_percent: float
    max_drawdown: float
    sharpe_ratio: float
    avg_trade_pnl: float
    best_trade: float
    worst_trade: float


class AccountInfo(BaseModel):
    """账户信息"""
    balance: float
    available_balance: float
    margin_balance: float
    unrealized_pnl: float
    total_pnl: float
    margin_ratio: float
    risk_level: str


class MarketData(BaseModel):
    """市场数据"""
    symbol: str
    price: float
    change_24h: float
    change_percent_24h: float
    volume_24h: float
    high_24h: float
    low_24h: float
    timestamp: datetime
