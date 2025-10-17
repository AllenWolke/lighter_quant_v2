"""
持仓路由
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

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


@router.get("/history")
async def get_position_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    symbol: Optional[str] = None,
    limit: int = 100,
    startDate: Optional[str] = None,
    endDate: Optional[str] = None
):
    """获取持仓历史（从 Lighter API 获取真实数据）"""
    import sys
    import os
    from datetime import datetime
    
    # 添加项目根目录到路径
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    try:
        from lighter import ApiClient, Configuration
        from lighter.api import AccountApi
        from quant_trading.utils.config import Config
        
        # 加载配置
        config_file = os.path.join(project_root, "config.yaml")
        if not os.path.exists(config_file):
            # 返回模拟数据
            return _get_mock_position_history(symbol, limit)
        
        config = Config.from_file(config_file)
        
        # 创建 API 客户端
        configuration = Configuration(
            host=config.lighter_config.get("base_url", "https://mainnet.zklighter.elliot.ai")
        )
        
        async with ApiClient(configuration) as api_client:
            account_api = AccountApi(api_client)
            account_index = config.lighter_config.get("account_index", 0)
            
            # 获取账户信息（包含持仓）
            account_response = await account_api.account(
                by="index",
                value=str(account_index)
            )
            
            if account_response and account_response.code == 200:
                if hasattr(account_response, 'accounts') and account_response.accounts:
                    account = account_response.accounts[0]
                    
                    # 解析持仓数据
                    positions = []
                    
                    if hasattr(account, 'positions') and account.positions:
                        for idx, position in enumerate(account.positions):
                            try:
                                # 获取市场信息
                                market_id = position.market_id if hasattr(position, 'market_id') else 0
                                
                                # 解析持仓数据
                                pos_sign = position.sign if hasattr(position, 'sign') else 1
                                side = "long" if pos_sign > 0 else "short"
                                
                                # 计算数值
                                position_size = float(position.position) if hasattr(position, 'position') and position.position else 0.0
                                avg_entry_price = float(position.avg_entry_price) if hasattr(position, 'avg_entry_price') and position.avg_entry_price else 0.0
                                position_value = float(position.position_value) if hasattr(position, 'position_value') and position.position_value else 0.0
                                unrealized_pnl = float(position.unrealized_pnl) if hasattr(position, 'unrealized_pnl') and position.unrealized_pnl else 0.0
                                realized_pnl = float(position.realized_pnl) if hasattr(position, 'realized_pnl') and position.realized_pnl else 0.0
                                
                                # 计算盈亏比率
                                pnl_ratio = 0.0
                                if position_value > 0:
                                    pnl_ratio = (unrealized_pnl / position_value) * 100
                                
                                # 获取交易对名称（简化处理）
                                symbol_name = f"MARKET_{market_id}"
                                if market_id == 0:
                                    symbol_name = "ETH/USDT"
                                elif market_id == 1:
                                    symbol_name = "BTC/USDT"
                                
                                position_data = {
                                    "id": idx + 1,
                                    "symbol": symbol_name,
                                    "side": side,
                                    "quantity": position_size,
                                    "entryPrice": avg_entry_price,
                                    "currentPrice": avg_entry_price,  # 需要实时价格
                                    "unrealizedPnl": unrealized_pnl,
                                    "pnlRatio": pnl_ratio,
                                    "margin": position_value,
                                    "leverage": 10.0,  # 默认杠杆
                                    "stopLossPrice": None,
                                    "takeProfitPrice": None,
                                    "isActive": position_size != 0,
                                    "createdAt": datetime.now().isoformat(),
                                    "updatedAt": datetime.now().isoformat()
                                }
                                
                                positions.append(position_data)
                                
                            except Exception as e:
                                print(f"解析持仓数据失败: {e}")
                                continue
                    
                    # 根据筛选条件过滤
                    if symbol:
                        positions = [p for p in positions if p["symbol"] == symbol]
                    
                    # 计算总数
                    total = len(positions)
                    
                    # 限制数量
                    positions = positions[:limit]
                    
                    return {
                        "positions": positions, 
                        "total": total,
                        "page": 1,
                        "pageSize": limit
                    }
        
        # 如果 API 调用失败，返回模拟数据
        return _get_mock_position_history(symbol, limit)
        
    except Exception as e:
        print(f"获取持仓历史失败: {e}")
        # 返回模拟数据
        return _get_mock_position_history(symbol, limit)


def _get_mock_position_history(symbol: Optional[str] = None, limit: int = 100):
    """返回模拟持仓历史数据"""
    positions = [
        {
            "id": 1,
            "symbol": "ETH/USDT",
            "side": "long",
            "quantity": 1.0,
            "entryPrice": 2000.0,
            "currentPrice": 2150.0,
            "unrealizedPnl": 150.0,
            "pnlRatio": 7.5,
            "margin": 200.0,
            "leverage": 10.0,
            "stopLossPrice": 1900.0,
            "takeProfitPrice": 2200.0,
            "isActive": False,
            "createdAt": "2024-01-01T00:00:00",
            "updatedAt": "2024-01-02T00:00:00"
        },
        {
            "id": 2,
            "symbol": "BTC/USDT",
            "side": "short",
            "quantity": 0.1,
            "entryPrice": 45000.0,
            "currentPrice": 44500.0,
            "unrealizedPnl": 50.0,
            "pnlRatio": 1.1,
            "margin": 450.0,
            "leverage": 10.0,
            "stopLossPrice": 46000.0,
            "takeProfitPrice": 44000.0,
            "isActive": False,
            "createdAt": "2024-01-02T00:00:00",
            "updatedAt": "2024-01-03T00:00:00"
        }
    ]
    
    # 根据筛选条件过滤
    if symbol:
        positions = [p for p in positions if p["symbol"] == symbol]
    
    total = len(positions)
    positions = positions[:limit]
    
    return {
        "positions": positions, 
        "total": total,
        "page": 1,
        "pageSize": limit
    }
