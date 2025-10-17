"""
交易服务
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import asyncio
import os
import sys

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

logger = logging.getLogger(__name__)


class TradingService:
    """交易服务类"""
    
    def __init__(self):
        self.is_running = False
        self.strategies = {}
        self.positions = {}
        self.orders = {}
        self._lighter_client = None
        self._config = None
    
    async def _get_lighter_account_data(self, account_index: int = 0):
        """获取 Lighter 账户数据（每次创建新客户端，避免资源泄漏）"""
        try:
            from lighter import ApiClient, Configuration
            from lighter.api import AccountApi
            from quant_trading.utils.config import Config
            
            # 加载配置
            if self._config is None:
                config_file = os.path.join(project_root, "config.yaml")
                if os.path.exists(config_file):
                    self._config = Config.from_file(config_file)
                else:
                    logger.warning(f"配置文件不存在: {config_file}")
                    return None
            
            # 创建临时的 API 客户端（使用后自动关闭）
            configuration = Configuration(
                host=self._config.lighter_config.get("base_url", "https://mainnet.zklighter.elliot.ai")
            )
            
            async with ApiClient(configuration) as api_client:
                account_api = AccountApi(api_client)
                
                # 调用 API 获取账户信息
                account_response = await account_api.account(
                    by="index",
                    value=str(account_index)
                )
                
                return account_response
                
        except Exception as e:
            logger.error(f"获取 Lighter 账户数据失败: {e}")
            return None
    
    async def start_trading(self) -> Dict[str, Any]:
        """开始交易"""
        try:
            self.is_running = True
            logger.info("交易服务已启动")
            return {"message": "交易服务已启动", "status": "success"}
        except Exception as e:
            logger.error(f"启动交易服务失败: {e}")
            raise
    
    async def stop_trading(self) -> Dict[str, Any]:
        """停止交易"""
        try:
            self.is_running = False
            logger.info("交易服务已停止")
            return {"message": "交易服务已停止", "status": "success"}
        except Exception as e:
            logger.error(f"停止交易服务失败: {e}")
            raise
    
    async def get_account_info(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """获取账户信息"""
        try:
            # 尝试从 Lighter API 获取真实账户数据
            if self._config is None:
                # 加载配置
                config_file = os.path.join(project_root, "config.yaml")
                if os.path.exists(config_file):
                    from quant_trading.utils.config import Config
                    self._config = Config.from_file(config_file)
            
            if self._config:
                account_index = self._config.lighter_config.get("account_index", 0)
                
                # 获取账户数据
                account_response = await self._get_lighter_account_data(account_index)
                
                if account_response and account_response.code == 200:
                    # DetailedAccounts 包含一个 accounts 列表
                    if hasattr(account_response, 'accounts') and account_response.accounts:
                        # 获取第一个账户（通常查询单个账户索引时只返回一个）
                        account = account_response.accounts[0]
                        
                        # 解析真实账户数据
                        collateral = float(account.collateral) if account.collateral else 0.0
                        available_balance = float(account.available_balance) if account.available_balance else 0.0
                        total_asset_value = float(account.total_asset_value) if hasattr(account, 'total_asset_value') and account.total_asset_value else collateral
                        
                        # 计算未实现盈亏（从持仓中计算）
                        unrealized_pnl = 0.0
                        realized_pnl = 0.0
                        
                        if hasattr(account, 'positions') and account.positions:
                            for position in account.positions:
                                # 未实现盈亏
                                if hasattr(position, 'unrealized_pnl') and position.unrealized_pnl:
                                    try:
                                        unrealized_pnl += float(position.unrealized_pnl)
                                    except:
                                        pass
                                
                                # 已实现盈亏
                                if hasattr(position, 'realized_pnl') and position.realized_pnl:
                                    try:
                                        realized_pnl += float(position.realized_pnl)
                                    except:
                                        pass
                        
                        # 计算保证金率
                        margin_ratio = 0.0
                        if total_asset_value > 0:
                            used_margin = collateral - available_balance
                            margin_ratio = used_margin / total_asset_value if total_asset_value > 0 else 0.0
                        
                        # 确定风险等级
                        risk_level = "low"
                        if margin_ratio > 0.7:
                            risk_level = "high"
                        elif margin_ratio > 0.5:
                            risk_level = "medium"
                        
                        logger.info(f"从 Lighter API 获取账户信息成功 (账户索引: {account_index})")
                        logger.info(f"账户余额: collateral={collateral}, available={available_balance}, total={total_asset_value}, unrealized_pnl={unrealized_pnl}")
                        
                        return {
                            "balance": total_asset_value,
                            "available_balance": available_balance,
                            "margin_balance": collateral,
                            "unrealized_pnl": unrealized_pnl,
                            "total_pnl": realized_pnl,  # 使用已实现盈亏
                            "margin_ratio": margin_ratio,
                            "risk_level": risk_level
                        }
                    else:
                        logger.warning(f"API 返回的账户列表为空")
                else:
                    logger.warning(f"API 调用失败或返回非 200 状态: {account_response.code if account_response else 'None'}")
            
            # 如果无法获取真实数据，返回模拟数据
            logger.info("使用模拟账户数据")
            return {
                "balance": 10000.0,
                "available_balance": 9500.0,
                "margin_balance": 10000.0,
                "unrealized_pnl": 0.0,
                "total_pnl": 500.0,
                "margin_ratio": 0.05,
                "risk_level": "low"
            }
            
        except Exception as e:
            logger.error(f"获取账户信息失败: {e}")
            # 返回默认模拟数据
            return {
                "balance": 0.0,
                "available_balance": 0.0,
                "margin_balance": 0.0,
                "unrealized_pnl": 0.0,
                "total_pnl": 0.0,
                "margin_ratio": 0.0,
                "risk_level": "low"
            }
    
    async def get_trading_stats(self, days: int = 30) -> Dict[str, Any]:
        """获取交易统计"""
        # 模拟交易统计
        return {
            "total_trades": 150,
            "winning_trades": 90,
            "losing_trades": 60,
            "win_rate": 60.0,
            "total_pnl": 2500.0,
            "total_pnl_percent": 25.0,
            "max_drawdown": -500.0,
            "sharpe_ratio": 1.5,
            "avg_trade_pnl": 16.67,
            "best_trade": 200.0,
            "worst_trade": -100.0
        }
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """获取持仓列表（从 Lighter API 获取真实数据）"""
        try:
            # 尝试从 Lighter API 获取真实持仓数据
            if self._config is None:
                # 加载配置
                config_file = os.path.join(project_root, "config.yaml")
                if os.path.exists(config_file):
                    from quant_trading.utils.config import Config
                    self._config = Config.from_file(config_file)
            
            if self._config:
                account_index = self._config.lighter_config.get("account_index", 0)
                
                # 获取账户数据
                account_response = await self._get_lighter_account_data(account_index)
                
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
                                    
                                    # 只返回有持仓的数据
                                    if position_size != 0:
                                        position_data = {
                                            "id": idx + 1,
                                            "symbol": symbol_name,
                                            "side": side,
                                            "quantity": position_size,
                                            "entry_price": avg_entry_price,
                                            "current_price": avg_entry_price,  # 需要实时价格
                                            "unrealized_pnl": unrealized_pnl,
                                            "pnl_ratio": pnl_ratio,
                                            "margin": position_value,
                                            "leverage": 10.0,  # 默认杠杆
                                            "stop_loss_price": None,
                                            "take_profit_price": None,
                                            "is_active": True,
                                            "created_at": datetime.now() - timedelta(hours=2),
                                            "updated_at": datetime.now()
                                        }
                                        
                                        positions.append(position_data)
                                        
                                except Exception as e:
                                    logger.error(f"解析持仓数据失败: {e}")
                                    continue
                        
                        logger.info(f"从 Lighter API 获取持仓列表成功，共 {len(positions)} 个持仓")
                        return positions
            
            # 如果获取失败，返回空列表
            logger.warning("从 Lighter API 获取持仓失败，返回空列表")
            return []
            
        except Exception as e:
            logger.error(f"获取持仓列表失败: {e}")
            # 返回空列表而不是模拟数据
            return []
    
    async def get_orders(self, symbol: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取订单列表"""
        # 模拟订单数据
        return [
            {
                "id": 1,
                "symbol": "ETH/USDT",
                "side": "buy",
                "order_type": "limit",
                "quantity": 0.5,
                "price": 2050.0,
                "filled_quantity": 0.0,
                "remaining_quantity": 0.5,
                "status": "pending",
                "order_id": "ORD001",
                "created_at": datetime.now() - timedelta(minutes=30),
                "updated_at": datetime.now()
            }
        ]
    
    async def get_trades(self, symbol: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """获取交易历史"""
        # 模拟交易历史
        return [
            {
                "id": 1,
                "symbol": "ETH/USDT",
                "side": "buy",
                "order_type": "market",
                "quantity": 0.1,
                "price": 2000.0,
                "fee": 0.2,
                "pnl": 10.0,
                "status": "filled",
                "order_id": "ORD001",
                "created_at": datetime.now() - timedelta(hours=1),
                "updated_at": datetime.now(),
                "filled_at": datetime.now() - timedelta(hours=1)
            }
        ]
    
    async def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建订单"""
        try:
            # 模拟创建订单
            order_id = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}"
            logger.info(f"创建订单: {order_id}")
            return {
                "id": 1,
                "order_id": order_id,
                "status": "pending",
                "message": "订单创建成功"
            }
        except Exception as e:
            logger.error(f"创建订单失败: {e}")
            raise
    
    async def cancel_order(self, order_id: int) -> Dict[str, Any]:
        """取消订单"""
        try:
            logger.info(f"取消订单: {order_id}")
            return {"message": "订单取消成功"}
        except Exception as e:
            logger.error(f"取消订单失败: {e}")
            raise
    
    async def emergency_stop(self) -> Dict[str, Any]:
        """紧急停止"""
        try:
            self.is_running = False
            # 取消所有未成交订单
            logger.info("紧急停止交易")
            return {"message": "紧急停止成功"}
        except Exception as e:
            logger.error(f"紧急停止失败: {e}")
            raise
    
    async def start_background_tasks(self):
        """启动后台任务"""
        logger.info("交易服务后台任务已启动")
        try:
            while True:
                # 定期更新市场数据、检查订单状态等
                await asyncio.sleep(60)  # 每60秒执行一次
                
                if self.is_running:
                    # 这里可以添加定期执行的任务
                    # 例如：更新持仓、检查风险等
                    logger.debug("执行定期任务检查...")
                    
        except asyncio.CancelledError:
            logger.info("交易服务后台任务已取消")
        except Exception as e:
            logger.error(f"交易服务后台任务错误: {e}")
    
    async def stop(self):
        """停止交易服务"""
        logger.info("正在停止交易服务...")
        self.is_running = False
        logger.info("交易服务已停止")
