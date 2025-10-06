"""
数据路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from core.security import get_current_active_user
from models.user import User
from schemas.trading import MarketData
from services.data_service import DataService

router = APIRouter()


@router.get("/market-data/{symbol}", response_model=MarketData)
async def get_market_data(
    symbol: str,
    current_user: User = Depends(get_current_active_user),
    data_service: DataService = Depends()
):
    """获取市场数据"""
    try:
        market_data = await data_service.get_market_data(symbol)
        return market_data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取市场数据失败: {str(e)}"
        )


@router.get("/klines/{symbol}")
async def get_klines(
    symbol: str,
    timeframe: str = Query("1m", description="时间周期"),
    limit: int = Query(200, description="数据条数"),
    current_user: User = Depends(get_current_active_user),
    data_service: DataService = Depends()
):
    """获取K线数据"""
    try:
        klines = await data_service.get_klines(symbol, timeframe, limit)
        return {"data": klines}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取K线数据失败: {str(e)}"
        )


@router.get("/ticker/{symbol}")
async def get_ticker(
    symbol: str,
    current_user: User = Depends(get_current_active_user),
    data_service: DataService = Depends()
):
    """获取行情数据"""
    try:
        ticker = await data_service.get_ticker(symbol)
        return ticker
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取行情数据失败: {str(e)}"
        )


@router.get("/orderbook/{symbol}")
async def get_orderbook(
    symbol: str,
    limit: int = Query(20, description="深度条数"),
    current_user: User = Depends(get_current_active_user),
    data_service: DataService = Depends()
):
    """获取订单簿"""
    try:
        orderbook = await data_service.get_orderbook(symbol, limit)
        return orderbook
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取订单簿失败: {str(e)}"
        )


@router.get("/symbols")
async def get_symbols(
    current_user: User = Depends(get_current_active_user),
    data_service: DataService = Depends()
):
    """获取交易对列表"""
    try:
        symbols = await data_service.get_symbols()
        return {"symbols": symbols}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取交易对列表失败: {str(e)}"
        )
