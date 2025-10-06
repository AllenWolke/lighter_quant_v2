"""
WebSocket管理器
"""

from typing import Dict, List, Set, Any, Callable
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class WebSocketManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, Any] = {}
        self.subscriptions: Dict[str, Set[str]] = {}
        self.message_handlers: List[Callable] = []
    
    async def connect(self, websocket: Any, client_id: str):
        """建立WebSocket连接"""
        try:
            await websocket.accept()
            self.active_connections[client_id] = websocket
            logger.info(f"WebSocket连接已建立: {client_id}")
        except Exception as e:
            logger.error(f"建立WebSocket连接失败: {e}")
            raise
    
    async def disconnect(self, client_id: str):
        """断开WebSocket连接"""
        try:
            if client_id in self.active_connections:
                del self.active_connections[client_id]
            if client_id in self.subscriptions:
                del self.subscriptions[client_id]
            logger.info(f"WebSocket连接已断开: {client_id}")
        except Exception as e:
            logger.error(f"断开WebSocket连接失败: {e}")
    
    async def send_message(self, client_id: str, message: Dict[str, Any]):
        """发送消息给指定客户端"""
        try:
            if client_id in self.active_connections:
                websocket = self.active_connections[client_id]
                await websocket.send_text(json.dumps(message))
                logger.debug(f"消息已发送给客户端 {client_id}: {message}")
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
    
    async def broadcast_message(self, message: Dict[str, Any]):
        """广播消息给所有客户端"""
        try:
            for client_id, websocket in self.active_connections.items():
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"广播消息给客户端 {client_id} 失败: {e}")
            logger.debug(f"消息已广播: {message}")
        except Exception as e:
            logger.error(f"广播消息失败: {e}")
    
    async def subscribe(self, client_id: str, channel: str):
        """订阅频道"""
        try:
            if client_id not in self.subscriptions:
                self.subscriptions[client_id] = set()
            self.subscriptions[client_id].add(channel)
            logger.info(f"客户端 {client_id} 订阅频道: {channel}")
        except Exception as e:
            logger.error(f"订阅频道失败: {e}")
    
    async def unsubscribe(self, client_id: str, channel: str):
        """取消订阅频道"""
        try:
            if client_id in self.subscriptions and channel in self.subscriptions[client_id]:
                self.subscriptions[client_id].remove(channel)
                logger.info(f"客户端 {client_id} 取消订阅频道: {channel}")
        except Exception as e:
            logger.error(f"取消订阅频道失败: {e}")
    
    async def handle_message(self, client_id: str, message: str):
        """处理接收到的消息"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "subscribe":
                channel = data.get("channel")
                if channel:
                    await self.subscribe(client_id, channel)
            
            elif message_type == "unsubscribe":
                channel = data.get("channel")
                if channel:
                    await self.unsubscribe(client_id, channel)
            
            elif message_type == "ping":
                await self.send_message(client_id, {"type": "pong", "timestamp": datetime.now().isoformat()})
            
            # 调用注册的消息处理器
            for handler in self.message_handlers:
                try:
                    await handler(client_id, data)
                except Exception as e:
                    logger.error(f"消息处理器执行失败: {e}")
                    
        except json.JSONDecodeError:
            logger.error(f"无效的JSON消息: {message}")
        except Exception as e:
            logger.error(f"处理消息失败: {e}")
    
    def add_message_handler(self, handler: Callable):
        """添加消息处理器"""
        self.message_handlers.append(handler)
    
    def remove_message_handler(self, handler: Callable):
        """移除消息处理器"""
        if handler in self.message_handlers:
            self.message_handlers.remove(handler)
    
    async def get_connection_count(self) -> int:
        """获取连接数量"""
        return len(self.active_connections)
    
    async def get_subscriptions(self, client_id: str) -> Set[str]:
        """获取客户端的订阅列表"""
        return self.subscriptions.get(client_id, set())
