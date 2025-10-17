"""
多市场并发策略包装器
使用asyncio+aiohttp实现多个市场的同时交易
"""

import asyncio
import aiohttp
from typing import Dict, List, Any, Set
from datetime import datetime
import logging

from .base_strategy import BaseStrategy
from ..utils.config import Config
from ..utils.logger import setup_logger


class MultiMarketStrategyWrapper:
    """
    多市场策略包装器
    
    功能:
    1. 使用asyncio并发处理多个市场
    2. 配置aiohttp连接池节约资源
    3. 实现限流保护
    4. 为同一策略类型管理多个市场实例
    """
    
    def __init__(self, strategy_class, config: Config, market_ids: List[int], **strategy_kwargs):
        """
        初始化多市场策略包装器
        
        Args:
            strategy_class: 策略类（如UTBotStrategy）
            config: 配置对象
            market_ids: 要交易的市场ID列表
            **strategy_kwargs: 传递给策略的其他参数
        """
        self.strategy_class = strategy_class
        self.config = config
        self.market_ids = market_ids
        self.strategy_kwargs = strategy_kwargs
        
        self.logger = setup_logger("MultiMarketStrategy", config.log_level)
        
        # 为每个市场创建独立的策略实例
        self.strategy_instances: Dict[int, BaseStrategy] = {}
        for market_id in market_ids:
            strategy = strategy_class(config=config, market_id=market_id, **strategy_kwargs)
            self.strategy_instances[market_id] = strategy
            self.logger.info(f"为市场 {market_id} 创建策略实例: {strategy.name}")
        
        # 并发控制
        self.max_concurrent_tasks = config.trading_config.get('max_concurrent_strategies', 10)
        self.semaphore = asyncio.Semaphore(self.max_concurrent_tasks)
        
        # 连接池配置（用于未来扩展HTTP请求）
        self.http_session: aiohttp.ClientSession = None
        self.connector_limit = 100  # 最大连接数
        self.connector_limit_per_host = 10  # 每个主机的最大连接数
        
        # 限流配置
        self.rate_limit_window = 60  # 1分钟
        self.max_requests_per_window = 60  # 每分钟最多60个请求
        self.request_timestamps: List[float] = []
        
        self.logger.info(f"多市场策略初始化完成: 管理 {len(market_ids)} 个市场")
        self.logger.info(f"最大并发任务数: {self.max_concurrent_tasks}")
        self.logger.info(f"连接池配置: 最大{self.connector_limit}连接, 每主机{self.connector_limit_per_host}连接")
        self.logger.info(f"限流配置: 每{self.rate_limit_window}秒最多{self.max_requests_per_window}请求")
    
    async def initialize(self):
        """初始化所有策略实例"""
        self.logger.info("初始化所有市场的策略实例...")
        
        # 创建aiohttp连接池
        connector = aiohttp.TCPConnector(
            limit=self.connector_limit,
            limit_per_host=self.connector_limit_per_host,
            ttl_dns_cache=300  # DNS缓存5分钟
        )
        
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        
        self.http_session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
        
        self.logger.info("aiohttp连接池已创建")
        
        # 并发初始化所有策略
        init_tasks = []
        for market_id, strategy in self.strategy_instances.items():
            task = self._initialize_strategy_with_semaphore(market_id, strategy)
            init_tasks.append(task)
        
        await asyncio.gather(*init_tasks, return_exceptions=True)
        self.logger.info(f"所有 {len(self.strategy_instances)} 个策略实例初始化完成")
    
    async def _initialize_strategy_with_semaphore(self, market_id: int, strategy: BaseStrategy):
        """使用信号量限制并发初始化"""
        async with self.semaphore:
            try:
                await strategy.on_initialize()
                self.logger.debug(f"市场 {market_id} 策略初始化成功")
            except Exception as e:
                self.logger.error(f"市场 {market_id} 策略初始化失败: {e}")
    
    async def start(self):
        """启动所有策略"""
        self.logger.info("启动所有市场的策略...")
        
        start_tasks = []
        for market_id, strategy in self.strategy_instances.items():
            task = self._start_strategy_with_semaphore(market_id, strategy)
            start_tasks.append(task)
        
        await asyncio.gather(*start_tasks, return_exceptions=True)
        self.logger.info("所有策略已启动")
    
    async def _start_strategy_with_semaphore(self, market_id: int, strategy: BaseStrategy):
        """使用信号量限制并发启动"""
        async with self.semaphore:
            try:
                await strategy.on_start()
                self.logger.debug(f"市场 {market_id} 策略启动成功")
            except Exception as e:
                self.logger.error(f"市场 {market_id} 策略启动失败: {e}")
    
    async def stop(self):
        """停止所有策略"""
        self.logger.info("停止所有市场的策略...")
        
        stop_tasks = []
        for market_id, strategy in self.strategy_instances.items():
            task = strategy.on_stop()
            stop_tasks.append(task)
        
        await asyncio.gather(*stop_tasks, return_exceptions=True)
        
        # 关闭HTTP连接池
        if self.http_session and not self.http_session.closed:
            await self.http_session.close()
            self.logger.info("aiohttp连接池已关闭")
        
        self.logger.info("所有策略已停止")
    
    async def process_market_data(self, market_data: Dict[int, Dict[str, Any]]):
        """
        并发处理所有市场的数据
        
        Args:
            market_data: 所有市场的数据字典
        """
        # 检查限流
        if not await self._check_rate_limit():
            self.logger.warning("达到限流限制，跳过本次数据处理")
            return
        
        # 为每个市场创建处理任务
        process_tasks = []
        for market_id, strategy in self.strategy_instances.items():
            if market_id in market_data:
                task = self._process_market_with_semaphore(market_id, strategy, market_data)
                process_tasks.append(task)
        
        # 并发执行所有任务
        if process_tasks:
            results = await asyncio.gather(*process_tasks, return_exceptions=True)
            
            # 统计处理结果
            success_count = sum(1 for r in results if not isinstance(r, Exception))
            error_count = sum(1 for r in results if isinstance(r, Exception))
            
            self.logger.debug(f"市场数据处理完成: {success_count}个成功, {error_count}个失败")
            
            # 记录失败的详情
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    market_id = list(self.strategy_instances.keys())[i]
                    self.logger.error(f"市场 {market_id} 数据处理失败: {result}")
    
    async def _process_market_with_semaphore(self, market_id: int, strategy: BaseStrategy, 
                                            market_data: Dict[int, Dict[str, Any]]):
        """使用信号量限制并发处理"""
        async with self.semaphore:
            try:
                await strategy.process_market_data(market_data)
            except Exception as e:
                self.logger.error(f"处理市场 {market_id} 数据时出错: {e}")
                raise
    
    async def _check_rate_limit(self) -> bool:
        """检查是否超过限流限制"""
        current_time = datetime.now().timestamp()
        
        # 清理过期的时间戳
        self.request_timestamps = [
            ts for ts in self.request_timestamps 
            if current_time - ts < self.rate_limit_window
        ]
        
        # 检查是否超限
        if len(self.request_timestamps) >= self.max_requests_per_window:
            return False
        
        # 记录当前请求
        self.request_timestamps.append(current_time)
        return True
    
    def get_all_strategies(self) -> List[BaseStrategy]:
        """获取所有策略实例（用于trading_engine集成）"""
        return list(self.strategy_instances.values())
    
    def get_managed_market_ids(self) -> Set[int]:
        """获取所有管理的市场ID"""
        return set(self.market_ids)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        active_count = sum(1 for s in self.strategy_instances.values() if s.is_active())
        
        return {
            "total_markets": len(self.market_ids),
            "active_strategies": active_count,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "rate_limit_window": self.rate_limit_window,
            "max_requests_per_window": self.max_requests_per_window,
            "current_request_count": len(self.request_timestamps)
        }

