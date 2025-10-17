"""
仓位管理器
负责管理交易仓位
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from ..utils.config import Config
from ..utils.logger import setup_logger


class PositionSide(Enum):
    """仓位方向"""
    LONG = "long"
    SHORT = "short"


@dataclass
class Position:
    """仓位信息"""
    market_id: int
    side: PositionSide
    size: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float
    leverage: float
    margin: float
    timestamp: datetime
    
    @property
    def market_value(self) -> float:
        """市值"""
        return self.size * self.current_price
        
    @property
    def margin_ratio(self) -> float:
        """保证金比例"""
        if self.market_value <= 0:
            return 0
        return self.margin / self.market_value


class PositionManager:
    """仓位管理器"""
    
    def __init__(self, config: Config):
        """
        初始化仓位管理器
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.logger = setup_logger("PositionManager", config.log_level)
        
        # 仓位字典 {market_id: Position}
        self.positions: Dict[int, Position] = {}
        
        # 仓位历史
        self.position_history: List[Position] = []
        
        # API客户端引用（稍后设置）
        self.api_client = None
        self.signer_client = None
    
    def set_api_clients(self, api_client, signer_client):
        """设置API客户端引用"""
        self.api_client = api_client
        self.signer_client = signer_client
        self.logger.info("API客户端已设置")
        
    async def initialize(self):
        """初始化仓位管理器"""
        self.logger.info("初始化仓位管理器...")
        
        # 从交易所加载现有仓位
        await self._load_existing_positions()
        
        self.logger.info("仓位管理器初始化完成")
        
    async def _load_existing_positions(self):
        """加载现有仓位"""
        try:
            self.logger.info("正在从交易所加载现有仓位...")
            
            if not self.api_client or not self.signer_client:
                self.logger.warning("API客户端未设置，无法获取真实持仓信息")
                self.positions.clear()
                return
            
            # 从Lighter API获取账户信息
            from lighter.api.account_api import AccountApi
            account_api = AccountApi(self.api_client)
            
            # 获取账户详情
            account_info = await account_api.account(by="index", value="0")
            
            if account_info and hasattr(account_info, 'accounts'):
                loaded_positions = 0
                
                for account in account_info.accounts:
                    # 检查是否有持仓信息
                    if hasattr(account, 'positions') and account.positions:
                        for position_data in account.positions:
                            try:
                                # 解析持仓数据
                                market_id = getattr(position_data, 'market_id', None)
                                if market_id is None:
                                    continue
                                    
                                side_str = getattr(position_data, 'side', '')
                                if side_str == 'long':
                                    side = PositionSide.LONG
                                elif side_str == 'short':
                                    side = PositionSide.SHORT
                                else:
                                    continue
                                
                                size = float(getattr(position_data, 'size', 0))
                                if size <= 0:
                                    continue
                                
                                entry_price = float(getattr(position_data, 'entry_price', 0))
                                current_price = float(getattr(position_data, 'current_price', entry_price))
                                leverage = float(getattr(position_data, 'leverage', 1.0))
                                margin = float(getattr(position_data, 'margin', 0))
                                
                                # 计算盈亏
                                if side == PositionSide.LONG:
                                    unrealized_pnl = (current_price - entry_price) * size
                                else:
                                    unrealized_pnl = (entry_price - current_price) * size
                                
                                # 创建Position对象
                                position = Position(
                                    market_id=market_id,
                                    side=side,
                                    size=size,
                                    entry_price=entry_price,
                                    current_price=current_price,
                                    unrealized_pnl=unrealized_pnl,
                                    realized_pnl=0.0,
                                    leverage=leverage,
                                    margin=margin,
                                    timestamp=datetime.now()
                                )
                                
                                self.positions[market_id] = position
                                loaded_positions += 1
                                
                                self.logger.info(f"✅ 加载持仓: 市场{market_id}, {side.value}, 数量{size:.6f}, 价格${entry_price:.6f}")
                                
                            except Exception as e:
                                self.logger.error(f"解析持仓数据失败: {e}")
                                continue
                
                if loaded_positions > 0:
                    self.logger.info(f"成功加载 {loaded_positions} 个持仓")
                else:
                    self.logger.info("未发现任何持仓")
            else:
                self.logger.info("账户信息为空或格式不正确")
                self.positions.clear()
                
        except Exception as e:
            self.logger.error(f"加载现有仓位失败: {e}")
            # 即使失败也清空缓存，避免使用过期的仓位信息
            self.positions.clear()
            self.logger.warning("已清空本地仓位缓存，避免使用过期信息")
            
    async def update_positions(self):
        """更新仓位信息"""
        try:
            # 定期从交易所同步持仓信息（每100次调用同步一次）
            if not hasattr(self, '_update_counter'):
                self._update_counter = 0
            
            self._update_counter += 1
            if self._update_counter % 100 == 0:  # 每100次更新时同步一次
                self.logger.info("执行定期持仓同步...")
                await self._load_existing_positions()
            
            # 更新所有仓位的当前价格和未实现盈亏
            for market_id, position in self.positions.items():
                await self._update_position_price(position)
                
        except Exception as e:
            self.logger.error(f"更新仓位失败: {e}")
            
    async def _update_position_price(self, position: Position):
        """更新仓位价格"""
        try:
            # 这里应该从市场数据获取当前价格
            # 暂时使用模拟数据
            current_price = position.current_price * (1 + (datetime.now().second % 10 - 5) * 0.001)
            position.current_price = current_price
            
            # 计算未实现盈亏
            if position.side == PositionSide.LONG:
                position.unrealized_pnl = (current_price - position.entry_price) * position.size
            else:
                position.unrealized_pnl = (position.entry_price - current_price) * position.size
                
        except Exception as e:
            self.logger.error(f"更新仓位价格失败: {e}")
            
    def open_position(self, market_id: int, side: PositionSide, size: float, 
                     price: float, leverage: float = 1.0) -> Optional[Position]:
        """
        开仓
        
        Args:
            market_id: 市场ID
            side: 仓位方向
            size: 仓位大小
            price: 开仓价格
            leverage: 杠杆倍数
            
        Returns:
            仓位对象
        """
        try:
            # 检查是否已有该市场的仓位
            if market_id in self.positions:
                self.logger.warning(f"市场 {market_id} 已有仓位，无法开新仓")
                return None
                
            # 计算保证金
            margin = (size * price) / leverage
            
            # 创建仓位
            position = Position(
                market_id=market_id,
                side=side,
                size=size,
                entry_price=price,
                current_price=price,
                unrealized_pnl=0.0,
                realized_pnl=0.0,
                leverage=leverage,
                margin=margin,
                timestamp=datetime.now()
            )
            
            # 添加到仓位字典
            self.positions[market_id] = position
            
            # 添加到历史记录
            self.position_history.append(position)
            
            self.logger.info(f"开仓成功: 市场 {market_id}, 方向 {side.value}, 大小 {size}, 价格 {price}")
            
            return position
            
        except Exception as e:
            self.logger.error(f"开仓失败: {e}")
            return None
            
    def close_position(self, market_id: int, price: float) -> Optional[float]:
        """
        平仓
        
        Args:
            market_id: 市场ID
            price: 平仓价格
            
        Returns:
            实现盈亏
        """
        try:
            if market_id not in self.positions:
                self.logger.warning(f"市场 {market_id} 没有仓位")
                return None
                
            position = self.positions[market_id]
            
            # 计算实现盈亏
            if position.side == PositionSide.LONG:
                realized_pnl = (price - position.entry_price) * position.size
            else:
                realized_pnl = (position.entry_price - price) * position.size
                
            # 更新实现盈亏
            position.realized_pnl += realized_pnl
            
            # 从仓位字典中移除
            del self.positions[market_id]
            
            self.logger.info(f"平仓成功: 市场 {market_id}, 实现盈亏 {realized_pnl}")
            
            return realized_pnl
            
        except Exception as e:
            self.logger.error(f"平仓失败: {e}")
            return None
            
    def update_position_size(self, market_id: int, new_size: float, price: float) -> bool:
        """
        更新仓位大小
        
        Args:
            market_id: 市场ID
            new_size: 新仓位大小
            price: 当前价格
            
        Returns:
            是否成功
        """
        try:
            if market_id not in self.positions:
                self.logger.warning(f"市场 {market_id} 没有仓位")
                return False
                
            position = self.positions[market_id]
            old_size = position.size
            
            # 计算部分平仓的盈亏
            if new_size < old_size:
                partial_size = old_size - new_size
                if position.side == PositionSide.LONG:
                    partial_pnl = (price - position.entry_price) * partial_size
                else:
                    partial_pnl = (position.entry_price - price) * partial_size
                    
                position.realized_pnl += partial_pnl
                
            # 更新仓位大小
            position.size = new_size
            position.margin = (new_size * price) / position.leverage
            
            self.logger.info(f"更新仓位大小: 市场 {market_id}, {old_size} -> {new_size}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"更新仓位大小失败: {e}")
            return False
            
    def get_position(self, market_id: int) -> Optional[Position]:
        """获取指定市场的仓位"""
        return self.positions.get(market_id)
        
    def get_all_positions(self) -> Dict[int, Position]:
        """获取所有仓位"""
        return self.positions.copy()
        
    def get_positions_by_side(self, side: PositionSide) -> List[Position]:
        """获取指定方向的仓位"""
        return [pos for pos in self.positions.values() if pos.side == side]
        
    def get_total_unrealized_pnl(self) -> float:
        """获取总未实现盈亏"""
        return sum(pos.unrealized_pnl for pos in self.positions.values())
        
    def get_total_realized_pnl(self) -> float:
        """获取总实现盈亏"""
        return sum(pos.realized_pnl for pos in self.position_history)
        
    def get_total_margin(self) -> float:
        """获取总保证金"""
        return sum(pos.margin for pos in self.positions.values())
        
    def get_position_summary(self) -> Dict[str, Any]:
        """获取仓位摘要"""
        total_positions = len(self.positions)
        long_positions = len(self.get_positions_by_side(PositionSide.LONG))
        short_positions = len(self.get_positions_by_side(PositionSide.SHORT))
        
        return {
            "total_positions": total_positions,
            "long_positions": long_positions,
            "short_positions": short_positions,
            "total_unrealized_pnl": self.get_total_unrealized_pnl(),
            "total_realized_pnl": self.get_total_realized_pnl(),
            "total_margin": self.get_total_margin(),
            "positions": [
                {
                    "market_id": pos.market_id,
                    "side": pos.side.value,
                    "size": pos.size,
                    "entry_price": pos.entry_price,
                    "current_price": pos.current_price,
                    "unrealized_pnl": pos.unrealized_pnl,
                    "realized_pnl": pos.realized_pnl,
                    "leverage": pos.leverage,
                    "margin": pos.margin
                } for pos in self.positions.values()
            ]
        }
