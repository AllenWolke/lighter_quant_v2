"""
订单管理器
负责管理交易订单
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import lighter

from ..utils.config import Config
from ..utils.logger import setup_logger
from ..notifications.notification_manager import NotificationManager


class OrderType(Enum):
    """订单类型"""
    LIMIT = "limit"
    MARKET = "market"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


class OrderSide(Enum):
    """订单方向"""
    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    """订单状态"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass
class Order:
    """订单信息"""
    order_id: str
    market_id: int
    side: OrderSide
    order_type: OrderType
    size: float
    price: float
    status: OrderStatus
    filled_size: float
    filled_price: float
    timestamp: datetime
    client_order_index: int
    
    @property
    def remaining_size(self) -> float:
        """剩余数量"""
        return self.size - self.filled_size
        
    @property
    def is_filled(self) -> bool:
        """是否完全成交"""
        return self.filled_size >= self.size
        
    @property
    def is_active(self) -> bool:
        """是否活跃"""
        return self.status in [OrderStatus.PENDING, OrderStatus.SUBMITTED]


class OrderManager:
    """订单管理器"""
    
    def __init__(self, signer_client: lighter.SignerClient, config: Config, notification_manager: Optional[NotificationManager] = None):
        """
        初始化订单管理器
        
        Args:
            signer_client: lighter签名客户端
            config: 配置对象
            notification_manager: 通知管理器
        """
        self.signer_client = signer_client
        self.config = config
        self.logger = setup_logger("OrderManager", config.log_level)
        self.notification_manager = notification_manager
        
        # 订单字典 {order_id: Order}
        self.orders: Dict[str, Order] = {}
        
        # 订单历史
        self.order_history: List[Order] = []
        
        # 客户端订单索引计数器
        self.client_order_index = 0
        
    async def initialize(self):
        """初始化订单管理器"""
        self.logger.info("初始化订单管理器...")
        
        # 检查客户端
        err = self.signer_client.check_client()
        if err is not None:
            raise Exception(f"客户端检查失败: {err}")
            
        self.logger.info("订单管理器初始化完成")
        
    async def process_orders(self):
        """处理订单"""
        try:
            # 检查待处理订单
            pending_orders = [order for order in self.orders.values() if order.status == OrderStatus.PENDING]
            
            for order in pending_orders:
                await self._submit_order(order)
                
            # 检查已提交订单的状态
            submitted_orders = [order for order in self.orders.values() if order.status == OrderStatus.SUBMITTED]
            
            for order in submitted_orders:
                await self._check_order_status(order)
                
        except Exception as e:
            self.logger.error(f"处理订单失败: {e}")
            
    async def _submit_order(self, order: Order):
        """提交订单"""
        try:
            if order.order_type == OrderType.LIMIT:
                await self._submit_limit_order(order)
            elif order.order_type == OrderType.MARKET:
                await self._submit_market_order(order)
            else:
                self.logger.warning(f"不支持的订单类型: {order.order_type}")
                
        except Exception as e:
            self.logger.error(f"提交订单失败: {e}")
            order.status = OrderStatus.REJECTED
            
    async def _submit_limit_order(self, order: Order):
        """提交限价订单"""
        try:
            is_ask = order.side == OrderSide.SELL
            
            tx, tx_hash, err = await self.signer_client.create_order(
                market_index=order.market_id,
                client_order_index=order.client_order_index,
                base_amount=int(order.size * 1e18),  # 转换为wei
                price=int(order.price * 1e6),  # 转换为微单位
                is_ask=is_ask,
                order_type=lighter.SignerClient.ORDER_TYPE_LIMIT,
                time_in_force=lighter.SignerClient.ORDER_TIME_IN_FORCE_GOOD_TILL_TIME,
                reduce_only=0,
                trigger_price=0
            )
            
            if err is not None:
                self.logger.error(f"创建限价订单失败: {err}")
                order.status = OrderStatus.REJECTED
            else:
                self.logger.info(f"限价订单已提交: {order.order_id}, tx_hash: {tx_hash}")
                order.status = OrderStatus.SUBMITTED
                
        except Exception as e:
            self.logger.error(f"提交限价订单失败: {e}")
            order.status = OrderStatus.REJECTED
            
    async def _submit_market_order(self, order: Order):
        """提交市价订单"""
        try:
            is_ask = order.side == OrderSide.SELL
            
            tx = await self.signer_client.create_market_order(
                market_index=order.market_id,
                client_order_index=order.client_order_index,
                base_amount=int(order.size * 1e18),  # 转换为wei
                avg_execution_price=int(order.price * 1e6),  # 转换为微单位
                is_ask=is_ask
            )
            
            if tx:
                self.logger.info(f"市价订单已提交: {order.order_id}")
                order.status = OrderStatus.SUBMITTED
            else:
                self.logger.error(f"创建市价订单失败")
                order.status = OrderStatus.REJECTED
                
        except Exception as e:
            self.logger.error(f"提交市价订单失败: {e}")
            order.status = OrderStatus.REJECTED
            
    async def _check_order_status(self, order: Order):
        """检查订单状态"""
        try:
            # 这里应该从交易所API查询订单状态
            # 暂时使用模拟逻辑
            if order.order_type == OrderType.MARKET:
                # 市价订单通常立即成交
                order.status = OrderStatus.FILLED
                order.filled_size = order.size
                order.filled_price = order.price
                self.logger.info(f"订单已成交: {order.order_id}")
                
                # 发送交易成交通知
                if self.notification_manager:
                    await self.notification_manager.send_trade_executed(
                        symbol=f"Market_{order.market_id}",
                        side=order.side.value,
                        quantity=order.filled_size,
                        price=order.filled_price,
                        order_id=order.order_id,
                        order_type=order.order_type.value
                    )
            else:
                # 限价订单需要检查是否成交
                # 这里应该实现实际的检查逻辑
                pass
                
        except Exception as e:
            self.logger.error(f"检查订单状态失败: {e}")
            
    def create_order(self, market_id: int, side: OrderSide, order_type: OrderType,
                    size: float, price: float) -> Order:
        """
        创建订单
        
        Args:
            market_id: 市场ID
            side: 订单方向
            order_type: 订单类型
            size: 订单大小
            price: 订单价格
            
        Returns:
            订单对象
        """
        try:
            # 生成订单ID
            order_id = f"{market_id}_{self.client_order_index}_{int(datetime.now().timestamp())}"
            
            # 创建订单
            order = Order(
                order_id=order_id,
                market_id=market_id,
                side=side,
                order_type=order_type,
                size=size,
                price=price,
                status=OrderStatus.PENDING,
                filled_size=0.0,
                filled_price=0.0,
                timestamp=datetime.now(),
                client_order_index=self.client_order_index
            )
            
            # 添加到订单字典
            self.orders[order_id] = order
            
            # 添加到历史记录
            self.order_history.append(order)
            
            # 增加客户端订单索引
            self.client_order_index += 1
            
            self.logger.info(f"创建订单: {order_id}, 市场 {market_id}, {side.value}, {order_type.value}, 大小 {size}, 价格 {price}")
            
            return order
            
        except Exception as e:
            self.logger.error(f"创建订单失败: {e}")
            raise
            
    async def cancel_order(self, order_id: str) -> bool:
        """
        取消订单
        
        Args:
            order_id: 订单ID
            
        Returns:
            是否成功
        """
        try:
            if order_id not in self.orders:
                self.logger.warning(f"订单不存在: {order_id}")
                return False
                
            order = self.orders[order_id]
            
            if not order.is_active:
                self.logger.warning(f"订单不是活跃状态: {order_id}")
                return False
                
            # 调用交易所API取消订单
            tx, tx_hash, err = await self.signer_client.cancel_order(
                market_index=order.market_id,
                order_index=order.client_order_index
            )
            
            if err is not None:
                self.logger.error(f"取消订单失败: {err}")
                return False
            else:
                order.status = OrderStatus.CANCELLED
                self.logger.info(f"订单已取消: {order_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"取消订单失败: {e}")
            return False
            
    def get_order(self, order_id: str) -> Optional[Order]:
        """获取订单"""
        return self.orders.get(order_id)
        
    def get_pending_orders(self) -> List[Order]:
        """获取待处理订单"""
        return [order for order in self.orders.values() if order.status == OrderStatus.PENDING]
        
    def get_submitted_orders(self) -> List[Order]:
        """获取已提交订单"""
        return [order for order in self.orders.values() if order.status == OrderStatus.SUBMITTED]
        
    def get_active_orders(self) -> List[Order]:
        """获取活跃订单"""
        return [order for order in self.orders.values() if order.is_active]
        
    def get_orders_by_market(self, market_id: int) -> List[Order]:
        """获取指定市场的订单"""
        return [order for order in self.orders.values() if order.market_id == market_id]
        
    def get_order_summary(self) -> Dict[str, Any]:
        """获取订单摘要"""
        total_orders = len(self.orders)
        pending_orders = len(self.get_pending_orders())
        submitted_orders = len(self.get_submitted_orders())
        filled_orders = len([o for o in self.orders.values() if o.status == OrderStatus.FILLED])
        cancelled_orders = len([o for o in self.orders.values() if o.status == OrderStatus.CANCELLED])
        
        return {
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "submitted_orders": submitted_orders,
            "filled_orders": filled_orders,
            "cancelled_orders": cancelled_orders,
            "active_orders": len(self.get_active_orders())
        }
