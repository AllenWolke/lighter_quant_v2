"""
交易引擎
负责协调各个模块，执行交易策略
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import lighter

from ..utils.config import Config
from ..utils.logger import setup_logger
from .data_manager import DataManager
from .risk_manager import RiskManager
from .position_manager import PositionManager
from .order_manager import OrderManager
from ..strategies.base_strategy import BaseStrategy
from ..notifications.notification_manager import NotificationManager


class TradingEngine:
    """量化交易引擎"""
    
    def __init__(self, config: Config):
        """
        初始化交易引擎
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.logger = setup_logger("TradingEngine", config.log_level)
        
        # 初始化lighter客户端
        self.api_client = lighter.ApiClient(
            configuration=lighter.Configuration(host=config.lighter_config["base_url"])
        )
        
        self.signer_client = lighter.SignerClient(
            url=config.lighter_config["base_url"],
            private_key=config.lighter_config["api_key_private_key"],
            account_index=config.lighter_config["account_index"],
            api_key_index=config.lighter_config["api_key_index"]
        )
        
        # 初始化通知管理器
        notification_config = config.notifications_config if hasattr(config, 'notifications_config') else {}
        self.notification_manager = NotificationManager(notification_config)
        
        # 初始化核心模块
        self.data_manager = DataManager(self.api_client, config)
        self.risk_manager = RiskManager(config)
        self.position_manager = PositionManager(config)
        self.order_manager = OrderManager(self.signer_client, config, self.notification_manager)
        
        # 策略列表
        self.strategies: List[BaseStrategy] = []
        
        # 运行状态
        self.is_running = False
        self.start_time = None
        
    def add_strategy(self, strategy: BaseStrategy):
        """
        添加交易策略
        
        Args:
            strategy: 策略实例
        """
        strategy.set_engine(self)
        self.strategies.append(strategy)
        self.logger.info(f"添加策略: {strategy.name}")
        
    async def start(self):
        """启动交易引擎"""
        if self.is_running:
            self.logger.warning("交易引擎已在运行")
            return
            
        self.logger.info("启动交易引擎...")
        self.is_running = True
        self.start_time = datetime.now()
        
        try:
            # 初始化各个模块
            await self._initialize_modules()
            
            # 启动主循环
            await self._main_loop()
            
        except Exception as e:
            self.logger.error(f"交易引擎运行错误: {e}")
            raise
        finally:
            await self.stop()
            
    async def stop(self):
        """停止交易引擎"""
        if not self.is_running:
            return
            
        self.logger.info("停止交易引擎...")
        self.is_running = False
        
        # 停止所有策略
        for strategy in self.strategies:
            await strategy.stop()
            
        # 关闭客户端连接
        await self.api_client.close()
        await self.signer_client.close()
        
        # 关闭通知管理器
        await self.notification_manager.close()
        
        self.logger.info("交易引擎已停止")
        
    async def _initialize_modules(self):
        """初始化各个模块"""
        self.logger.info("初始化模块...")
        
        # 初始化数据管理器
        await self.data_manager.initialize()
        
        # 初始化风险管理器
        await self.risk_manager.initialize()
        
        # 初始化仓位管理器
        await self.position_manager.initialize()
        
        # 初始化订单管理器
        await self.order_manager.initialize()
        
        # 初始化所有策略
        for strategy in self.strategies:
            await strategy.initialize()
            
        self.logger.info("模块初始化完成")
        
    async def _main_loop(self):
        """主循环"""
        self.logger.info("进入主循环...")
        
        while self.is_running:
            try:
                # 获取市场数据
                market_data = await self.data_manager.get_latest_data()
                
                # 风险检查
                if not await self.risk_manager.check_risk_limits(market_data):
                    self.logger.warning("风险检查失败，跳过本次交易")
                    # 发送风险警告通知
                    await self.notification_manager.send_risk_limit_exceeded(
                        risk_type="general",
                        current_value=0,
                        limit_value=0,
                        message="风险检查失败，跳过本次交易"
                    )
                    await asyncio.sleep(1)
                    continue
                
                # 更新仓位信息
                await self.position_manager.update_positions()
                
                # 执行策略
                for strategy in self.strategies:
                    if strategy.is_active():
                        try:
                            await strategy.on_tick(market_data)
                        except Exception as e:
                            self.logger.error(f"策略 {strategy.name} 执行错误: {e}")
                
                # 处理订单
                await self.order_manager.process_orders()
                
                # 等待下次循环
                await asyncio.sleep(self.config.trading_config["tick_interval"])
                
            except Exception as e:
                self.logger.error(f"主循环错误: {e}")
                await asyncio.sleep(1)
                
    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "is_running": self.is_running,
            "start_time": self.start_time,
            "uptime": datetime.now() - self.start_time if self.start_time else None,
            "strategies_count": len(self.strategies),
            "active_strategies": sum(1 for s in self.strategies if s.is_active()),
            "positions": self.position_manager.get_all_positions(),
            "orders": self.order_manager.get_pending_orders()
        }
