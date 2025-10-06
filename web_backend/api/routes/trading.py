"""
交易相关API路由
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from core.database import get_db
from core.security import get_current_active_user
from models.user import User
from models.trading import Trade, Order
from schemas.trading import (
    TradeResponse, OrderCreate, OrderResponse,
    TradingStats, AccountInfo, MarketData
)
from services.trading_service import TradingService

router = APIRouter()


@router.get("/account", response_model=AccountInfo)
async def get_account_info(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取账户信息"""
    try:
        trading_service = TradingService()
        account_info = await trading_service.get_account_info(current_user.id)
        return account_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取账户信息失败: {str(e)}")


@router.get("/stats", response_model=TradingStats)
async def get_trading_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    days: int = 30
):
    """获取交易统计"""
    try:
        trading_service = TradingService()
        stats = await trading_service.get_trading_stats(current_user.id, days)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取交易统计失败: {str(e)}")


@router.get("/trades", response_model=List[TradeResponse])
async def get_trades(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    symbol: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """获取交易记录"""
    try:
        query = db.query(Trade).filter(Trade.user_id == current_user.id)
        
        if symbol:
            query = query.filter(Trade.symbol == symbol)
            
        trades = query.order_by(Trade.created_at.desc()).offset(offset).limit(limit).all()
        
        return [TradeResponse.from_orm(trade) for trade in trades]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取交易记录失败: {str(e)}")


@router.get("/orders", response_model=List[OrderResponse])
async def get_orders(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    symbol: Optional[str] = None,
    order_status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """获取订单记录"""
    try:
        query = db.query(Order).filter(Order.user_id == current_user.id)
        
        if symbol:
            query = query.filter(Order.symbol == symbol)
        if order_status:
            query = query.filter(Order.status == order_status)
            
        orders = query.order_by(Order.created_at.desc()).offset(offset).limit(limit).all()
        
        return [OrderResponse.from_orm(order) for order in orders]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取订单记录失败: {str(e)}")


@router.post("/orders", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建订单"""
    try:
        trading_service = TradingService()
        order = await trading_service.create_order(current_user.id, order_data, db)
        return OrderResponse.from_orm(order)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建订单失败: {str(e)}")


@router.delete("/orders/{order_id}")
async def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """取消订单"""
    try:
        trading_service = TradingService()
        success = await trading_service.cancel_order(current_user.id, order_id, db)
        
        if not success:
            raise HTTPException(status_code=404, detail="订单不存在或无法取消")
            
        return {"message": "订单已取消"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取消订单失败: {str(e)}")


@router.get("/market-data/{symbol}", response_model=MarketData)
async def get_market_data(
    symbol: str,
    timeframe: str = "1m",
    limit: int = 200
):
    """获取市场数据"""
    try:
        trading_service = TradingService()
        market_data = await trading_service.get_market_data(symbol, timeframe, limit)
        return market_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取市场数据失败: {str(e)}")


@router.get("/klines/{symbol}")
async def get_klines(
    symbol: str,
    timeframe: str = "1m",
    limit: int = 200
):
    """获取K线数据"""
    try:
        trading_service = TradingService()
        klines = await trading_service.get_klines(symbol, timeframe, limit)
        return {"data": klines}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取K线数据失败: {str(e)}")


@router.get("/ticker/{symbol}")
async def get_ticker(symbol: str):
    """获取行情数据"""
    try:
        trading_service = TradingService()
        ticker = await trading_service.get_ticker(symbol)
        return ticker
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取行情数据失败: {str(e)}")


@router.get("/orderbook/{symbol}")
async def get_orderbook(symbol: str, limit: int = 20):
    """获取订单簿数据"""
    try:
        trading_service = TradingService()
        orderbook = await trading_service.get_orderbook(symbol, limit)
        return orderbook
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取订单簿失败: {str(e)}")


@router.post("/start-trading")
async def start_trading(
    current_user: User = Depends(get_current_active_user)
):
    """开始交易"""
    try:
        trading_service = TradingService()
        success = await trading_service.start_trading(current_user.id)
        
        if not success:
            raise HTTPException(status_code=400, detail="启动交易失败")
            
        return {"message": "交易已开始"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动交易失败: {str(e)}")


@router.post("/stop-trading")
async def stop_trading(
    current_user: User = Depends(get_current_active_user)
):
    """停止交易"""
    try:
        trading_service = TradingService()
        success = await trading_service.stop_trading(current_user.id)
        
        if not success:
            raise HTTPException(status_code=400, detail="停止交易失败")
            
        return {"message": "交易已停止"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"停止交易失败: {str(e)}")


@router.post("/emergency-stop")
async def emergency_stop(
    current_user: User = Depends(get_current_active_user)
):
    """紧急停止"""
    try:
        trading_service = TradingService()
        success = await trading_service.emergency_stop(current_user.id)
        
        if not success:
            raise HTTPException(status_code=400, detail="紧急停止失败")
            
        return {"message": "紧急停止已执行"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"紧急停止失败: {str(e)}")
