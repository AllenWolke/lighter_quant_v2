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
import lighter.exceptions

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


class MarginMode(Enum):
    """保证金模式"""
    CROSS = "cross"      # 全仓模式
    ISOLATED = "isolated"  # 逐仓模式


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
    leverage: float = 1.0  # 杠杆倍数，默认1倍（不使用杠杆）
    margin_mode: MarginMode = MarginMode.CROSS  # 保证金模式，默认全仓
    price_slippage_tolerance: float = 0.01  # 价格滑点容忍度，默认1%
    slippage_enabled: bool = True  # 是否开启滑点检测，默认开启
    
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
    
    def __init__(self, signer_client: lighter.SignerClient, config: Config, notification_manager: Optional[NotificationManager] = None, data_manager=None, position_manager=None):
        """
        初始化订单管理器
        
        Args:
            signer_client: lighter签名客户端
            config: 配置对象
            notification_manager: 通知管理器
            data_manager: 数据管理器（用于获取当前价格进行滑点检查和市场规则）
            position_manager: 持仓管理器（用于订单后持仓同步）
        """
        self.signer_client = signer_client
        self.config = config
        self.logger = setup_logger("OrderManager", config.log_level)
        self.notification_manager = notification_manager
        self.data_manager = data_manager
        self.position_manager = position_manager
        
        # 价格滑点容忍度（默认0.05%）
        self.price_slippage_tolerance = 0.0005  # 0.05%
        
        # 滑点配置现在由策略直接传入，不再使用全局配置
        
        # 市场规则缓存
        self.market_rules_cache: Dict[int, Dict[str, Any]] = {}
        
        # 市场数量精度配置 (不同市场使用不同的单位转换因子)
        # 默认: ETH/BTC等高价币使用0.0001，DOGE等低价币使用1.0
        self.market_size_unit: Dict[int, float] = {
            0: 0.0001,   # ETH - 高精度
            1: 0.00001,  # BTC - 超高精度
            2: 0.001,    # SOL - 中精度
            3: 1.0,      # DOGE - 低精度（1:1）⭐ 修复10000倍错误
            4: 1.0,      # PEPE - 低精度
            5: 0.01,     # WIF - 中低精度
            # 其他市场默认使用0.0001
        }
        
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
        
        # 加载市场规则
        await self._load_market_rules()
            
        self.logger.info("订单管理器初始化完成")
    
    async def _load_market_rules(self):
        """加载所有市场的规则"""
        try:
            if not self.data_manager:
                self.logger.warning("未配置data_manager，无法加载市场规则")
                return
            
            # 获取自定义配置
            custom_min_sizes = {}
            custom_min_quotes = {}
            if hasattr(self.config, 'data_sources') and self.config.data_sources:
                custom_min_sizes = self.config.data_sources.get('custom_min_order_size', {})
                custom_min_quotes = self.config.data_sources.get('custom_min_quote_amount', {})
            
            # 从data_manager的缓存获取市场规则
            for market_id, market_data in self.data_manager.market_data_cache.items():
                market_info = market_data.get("market_info")
                if market_info:
                    # 从API获取基础规则
                    api_min_base = float(market_info.min_base_amount) if hasattr(market_info, 'min_base_amount') else 0
                    api_min_quote = float(market_info.min_quote_amount) if hasattr(market_info, 'min_quote_amount') else 0
                    
                    # 如果有自定义配置，使用自定义值覆盖
                    custom_info = []
                    
                    if market_id in custom_min_sizes:
                        custom_min_base = float(custom_min_sizes[market_id])
                        custom_info.append(f"订单量={custom_min_base} (API: {api_min_base})")
                        min_base_amount = custom_min_base
                    else:
                        min_base_amount = api_min_base
                    
                    if market_id in custom_min_quotes:
                        custom_min_quote_val = float(custom_min_quotes[market_id])
                        custom_info.append(f"报价=${custom_min_quote_val} (API: ${api_min_quote})")
                        min_quote_amount = custom_min_quote_val
                    else:
                        min_quote_amount = api_min_quote
                    
                    if custom_info:
                        self.logger.info(f"市场 {market_id} 使用自定义规则: {', '.join(custom_info)}")
                    
                    self.market_rules_cache[market_id] = {
                        "min_base_amount": min_base_amount,
                        "min_quote_amount": min_quote_amount,
                        "symbol": market_info.symbol if hasattr(market_info, 'symbol') else f"Market_{market_id}",
                        "api_min_base_amount": api_min_base,
                        "api_min_quote_amount": api_min_quote,
                        "is_custom_size": market_id in custom_min_sizes,
                        "is_custom_quote": market_id in custom_min_quotes
                    }
                    self.logger.debug(f"加载市场 {market_id} ({self.market_rules_cache[market_id]['symbol']}) 规则: 最小订单量={min_base_amount}, 最小报价=${min_quote_amount}")
            
            self.logger.info(f"已加载 {len(self.market_rules_cache)} 个市场的规则")
        except Exception as e:
            self.logger.error(f"加载市场规则失败: {e}")
        
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
            
            # 参数转换（与市价单相同的单位）
            # Lighter使用的单位根据市场不同而不同
            
            # 获取该市场的数量单位（默认0.0001）
            size_unit = self.market_size_unit.get(order.market_id, 0.0001)
            
            base_amount_units = int(order.size / size_unit)  # 转换为Lighter的单位
            price_cents = int(order.price * 100)  # 转换为美分
            
            self.logger.info(f"单位转换: 市场{order.market_id}使用size_unit={size_unit}, {order.size} → {base_amount_units} units")
            
            self.logger.debug(f"准备提交限价订单:")
            self.logger.debug(f"  市场ID: {order.market_id}")
            self.logger.debug(f"  数量: {order.size} → {base_amount_units} units")
            self.logger.debug(f"  价格: {order.price} → {price_cents} cents")
            self.logger.debug(f"  方向: {'卖出' if is_ask else '买入'}")
            
            result = await self.signer_client.create_order(
                market_index=order.market_id,
                client_order_index=order.client_order_index,
                base_amount=base_amount_units,  # 使用Lighter单位
                price=price_cents,  # 使用美分
                is_ask=is_ask,
                order_type=lighter.SignerClient.ORDER_TYPE_LIMIT,
                time_in_force=lighter.SignerClient.ORDER_TIME_IN_FORCE_GOOD_TILL_TIME,
                reduce_only=0,
                trigger_price=0
            )
            
            # 处理返回值
            tx = None
            tx_hash = None
            err = None
            
            if result is None:
                err = "返回值为 None"
            elif isinstance(result, tuple):
                if len(result) >= 3:
                    tx, tx_hash, err = result[0], result[1], result[2]
                elif len(result) == 2:
                    tx, err = result[0], result[1]
                else:
                    tx = result[0] if len(result) > 0 else None
            else:
                tx = result
            
            if err is not None:
                self.logger.error(f"创建限价订单失败: {err}")
                order.status = OrderStatus.REJECTED
            elif tx is not None:
                log_msg = f"限价订单已提交: {order.order_id}"
                if tx_hash:
                    log_msg += f", tx_hash: {tx_hash}"
                self.logger.info(log_msg)
                order.status = OrderStatus.SUBMITTED
            else:
                self.logger.error(f"创建限价订单失败: 返回值异常")
                order.status = OrderStatus.REJECTED
                
        except Exception as e:
            self.logger.error(f"提交限价订单失败: {e}")
            order.status = OrderStatus.REJECTED
            
    async def _submit_market_order(self, order: Order):
        """提交市价订单"""
        try:
            is_ask = order.side == OrderSide.SELL
            
            # 参数转换
            # Lighter使用的单位根据市场不同而不同：
            # - 高价币(ETH): base_amount单位是0.0001（万分之一），例如1000 = 0.1 ETH
            # - 低价币(DOGE): base_amount单位是1.0（1:1），例如10 = 10 DOGE
            # price: 统一使用0.01（美分），例如170000 = $1700
            
            # 获取该市场的数量单位（默认0.0001）
            size_unit = self.market_size_unit.get(order.market_id, 0.0001)
            
            base_amount_units = int(order.size / size_unit)  # 转换为Lighter的单位
            
            # 获取滑点配置
            slippage_tolerance = getattr(order, 'price_slippage_tolerance', self.price_slippage_tolerance)
            slippage_enabled = getattr(order, 'slippage_enabled', True)
            
            # 根据滑点设置调整价格范围
            if slippage_enabled:
                # 开启滑点检测：设置最差可接受价格
                if is_ask:  # 卖出订单：价格不能低于 order.price * (1 - slippage_tolerance)
                    worst_acceptable_price = order.price * (1 - slippage_tolerance)
                else:  # 买入订单：价格不能高于 order.price * (1 + slippage_tolerance)
                    worst_acceptable_price = order.price * (1 + slippage_tolerance)
                
                price_cents = int(worst_acceptable_price * 100)  # 转换为美分
                self.logger.info(f"滑点保护: 最差可接受价格 ${worst_acceptable_price:.6f} (容忍度: {slippage_tolerance*100:.1f}%)")
            else:
                # 关闭滑点检测：使用宽松价格范围确保成交
                if is_ask:  # 卖出订单：使用很低的价格确保能卖出
                    price_cents = int(order.price * 0.5 * 100)  # 50%的价格
                else:  # 买入订单：使用很高的价格确保能买入
                    price_cents = int(order.price * 2.0 * 100)  # 200%的价格
                
                self.logger.info(f"滑点检测已关闭: 使用宽松价格范围确保成交")
            
            self.logger.info(f"单位转换: 市场{order.market_id}使用size_unit={size_unit}, {order.size} → {base_amount_units} units")
            
            # Lighter SDK的BaseAmount限制（48位整数）
            MAX_BASE_AMOUNT = 281474976710655  # 2^48 - 1
            
            self.logger.debug(f"准备提交市价订单:")
            self.logger.debug(f"  市场ID: {order.market_id}")
            self.logger.debug(f"  客户订单ID: {order.client_order_index}")
            self.logger.debug(f"  数量: {order.size} → {base_amount_units} units (Lighter单位: 0.0001)")
            self.logger.debug(f"  价格: {order.price} → {price_cents} cents (美分)")
            self.logger.debug(f"  方向: {'卖出' if is_ask else '买入'}")
            
            # 参数验证
            if base_amount_units <= 0:
                self.logger.error(f"订单数量无效: {order.size} (units: {base_amount_units})")
                order.status = OrderStatus.REJECTED
                return
            
            # 检查Lighter的BaseAmount限制
            if base_amount_units > MAX_BASE_AMOUNT:
                self.logger.error(f"订单数量超过Lighter限制:")
                self.logger.error(f"  您的订单: {base_amount_units} units")
                self.logger.error(f"  最大限制: {MAX_BASE_AMOUNT} units")
                self.logger.error(f"  超出: {(base_amount_units / MAX_BASE_AMOUNT - 1) * 100:.1f}%")
                max_size = (MAX_BASE_AMOUNT * 0.0001)
                self.logger.error(f"建议: 减小position_size到 {max_size:.6f} 或更小")
                order.status = OrderStatus.REJECTED
                return
            
            if price_cents <= 0:
                self.logger.error(f"订单价格无效: {order.price} (cents: {price_cents})")
                order.status = OrderStatus.REJECTED
                return
            
            # 市场规则检查 ⭐
            order_type_name = "市价单" if order.order_type == OrderType.MARKET else "限价单"
            self.logger.info(f"开始校验订单参数 - 市场ID: {order.market_id}, 订单类型: {order_type_name}")
            
            if order.market_id in self.market_rules_cache:
                market_rules = self.market_rules_cache[order.market_id]
                min_base = market_rules.get('min_base_amount', 0)
                min_quote = market_rules.get('min_quote_amount', 0)
                symbol = market_rules.get('symbol', f'Market_{order.market_id}')
                is_custom_size = market_rules.get('is_custom_size', False)
                is_custom_quote = market_rules.get('is_custom_quote', False)
                api_min_base = market_rules.get('api_min_base_amount', 0)
                api_min_quote = market_rules.get('api_min_quote_amount', 0)
                
                order_value = order.size * order.price
                
                # 打印当前市场规则
                self.logger.info(f"市场 {order.market_id} ({symbol}) 的订单要求:")
                self.logger.info(f"  ├─ 最小订单量: {min_base} {symbol} {'(自定义)' if is_custom_size else '(API)'}")
                if is_custom_size:
                    self.logger.info(f"  │   (API原始值: {api_min_base})")
                self.logger.info(f"  ├─ 最小报价金额: ${min_quote:.6f} USDT {'(自定义)' if is_custom_quote else '(API)'}")
                if is_custom_quote:
                    self.logger.info(f"  │   (API原始值: ${api_min_quote:.6f})")
                self.logger.info(f"  └─ 订单类型: {order_type_name}")
                
                # 打印您的订单参数
                self.logger.info(f"您的订单参数:")
                self.logger.info(f"  ├─ 订单数量: {order.size} {symbol}")
                self.logger.info(f"  ├─ 订单价格: ${order.price:.6f}")
                self.logger.info(f"  ├─ 订单价值: ${order_value:.6f} USDT")
                self.logger.info(f"  ├─ 杠杆倍数: {order.leverage}x")
                self.logger.info(f"  └─ 保证金模式: {'全仓' if order.margin_mode == MarginMode.CROSS else '逐仓'}")
                
                # 检查最小订单量
                if min_base > 0:
                    if order.size < min_base:
                        self.logger.error(f"❌ 订单量不满足市场要求，订单将被拒绝:")
                        self.logger.error(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                        self.logger.error(f"  市场: {order.market_id} ({symbol})")
                        self.logger.error(f"  订单类型: {order_type_name}")
                        self.logger.error(f"  您的订单: {order.size} {symbol}")
                        self.logger.error(f"  最小要求: {min_base} {symbol}")
                        self.logger.error(f"  差距: 需要增加 {min_base - order.size:.6f} {symbol}")
                        self.logger.error(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                        self.logger.error(f"📝 修复建议:")
                        self.logger.error(f"  修改 config.yaml:")
                        self.logger.error(f"  strategies:")
                        self.logger.error(f"    ut_bot:  # 或其他策略名")
                        self.logger.error(f"      position_size: {min_base}  # 改为最小值")
                        self.logger.error(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                        order.status = OrderStatus.REJECTED
                        return
                    else:
                        self.logger.info(f"  ✅ 订单量检查通过: {order.size} >= {min_base}")
                
                # 检查最小报价金额
                if min_quote > 0:
                    if order_value < min_quote:
                        self.logger.error(f"❌ 订单价值不满足市场要求，订单将被拒绝:")
                        self.logger.error(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                        self.logger.error(f"  市场: {order.market_id} ({symbol})")
                        self.logger.error(f"  订单类型: {order_type_name}")
                        self.logger.error(f"  您的订单价值: ${order_value:.6f} USDT")
                        self.logger.error(f"  最小要求: ${min_quote:.6f} USDT")
                        self.logger.error(f"  差距: 需要增加 ${min_quote - order_value:.6f} USDT")
                        required_size = min_quote / order.price if order.price > 0 else 0
                        self.logger.error(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                        self.logger.error(f"📝 修复建议:")
                        self.logger.error(f"  方案1 - 增加订单量:")
                        self.logger.error(f"    config.yaml:")
                        self.logger.error(f"      ut_bot:")
                        self.logger.error(f"        position_size: {required_size:.6f}  # 满足最小报价要求")
                        self.logger.error(f"  ")
                        self.logger.error(f"  方案2 - 调整自定义最小报价 (如果API值不准确):")
                        self.logger.error(f"    config.yaml:")
                        self.logger.error(f"      data_sources:")
                        self.logger.error(f"        custom_min_quote_amount:")
                        self.logger.error(f"          {order.market_id}: {order_value:.2f}  # 调整为当前订单价值")
                        self.logger.error(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                        order.status = OrderStatus.REJECTED
                        return
                    else:
                        self.logger.info(f"  ✅ 订单价值检查通过: ${order_value:.6f} >= ${min_quote:.6f}")
                
                self.logger.info(f"✅ 市场规则校验通过 - 订单参数满足市场 {order.market_id} ({symbol}) 的所有要求")
            else:
                self.logger.warning(f"⚠️  市场 {order.market_id} 规则未加载，跳过市场规则检查")
                self.logger.warning(f"  建议: 确保data_manager已初始化并加载了市场数据")
            
            # 使用订单传入的滑点配置
            slippage_tolerance = getattr(order, 'price_slippage_tolerance', self.price_slippage_tolerance)
            # 默认开启滑点检测，除非策略明确指定关闭
            slippage_enabled = getattr(order, 'slippage_enabled', True)
            
            # 检查是否开启滑点检测
            if not slippage_enabled:
                self.logger.info(f"✅ 市场 {order.market_id} 滑点检测已关闭，直接按市价成交")
                # 不return，继续执行订单提交
            else:
                self.logger.info(f"🔍 滑点检测: 市场 {order.market_id}, 容忍度 {slippage_tolerance*100:.2f}%")
                
                if self.data_manager is not None:
                    try:
                        # 获取当前市场价格
                        market_data = self.data_manager.market_data_cache.get(order.market_id, {})
                        current_price = market_data.get('last_price', 0)
                        
                        if current_price > 0:
                            if is_ask:  # 卖出订单
                                # 当前价格不能低于订单价格的(1 - 滑点容忍度)
                                min_acceptable_price = order.price * (1 - slippage_tolerance)
                                if current_price < min_acceptable_price:
                                    slippage_pct = ((order.price - current_price) / order.price) * 100
                                    self.logger.warning(f"卖出价格滑点过大，订单拒绝:")
                                    self.logger.warning(f"  订单价格: ${order.price:.4f}")
                                    self.logger.warning(f"  当前价格: ${current_price:.4f}")
                                    self.logger.warning(f"  价格滑点: {slippage_pct:.2f}%")
                                    self.logger.warning(f"  容忍限制: {slippage_tolerance * 100:.2f}%")
                                    self.logger.warning(f"  建议: 在config.yaml中增加price_slippage_tolerance")
                                    order.status = OrderStatus.REJECTED
                                    return
                                elif current_price < order.price:
                                    slippage_pct = ((order.price - current_price) / order.price) * 100
                                    self.logger.info(f"卖出价格略低于预期，但在可接受范围内:")
                                    self.logger.info(f"  订单价格: ${order.price:.4f}")
                                    self.logger.info(f"  当前价格: ${current_price:.4f}")
                                    self.logger.info(f"  价格差异: -{slippage_pct:.2f}% (可接受)")
                            else:  # 买入订单
                                # 当前价格不能超过订单价格的(1 + 滑点容忍度)
                                max_acceptable_price = order.price * (1 + slippage_tolerance)
                                if current_price > max_acceptable_price:
                                    slippage_pct = ((current_price - order.price) / order.price) * 100
                                    self.logger.warning(f"买入价格滑点过大，订单拒绝:")
                                    self.logger.warning(f"  订单价格: ${order.price:.4f}")
                                    self.logger.warning(f"  当前价格: ${current_price:.4f}")
                                    self.logger.warning(f"  价格滑点: +{slippage_pct:.2f}%")
                                    self.logger.warning(f"  容忍限制: {slippage_tolerance * 100:.2f}%")
                                    self.logger.warning(f"  建议: 在config.yaml中增加price_slippage_tolerance")
                                    order.status = OrderStatus.REJECTED
                                    return
                                elif current_price > order.price:
                                    slippage_pct = ((current_price - order.price) / order.price) * 100
                                    self.logger.info(f"买入价格略高于预期，但在可接受范围内:")
                                    self.logger.info(f"  订单价格: ${order.price:.4f}")
                                    self.logger.info(f"  当前价格: ${current_price:.4f}")
                                    self.logger.info(f"  价格差异: +{slippage_pct:.2f}% (可接受)")
                        else:
                            self.logger.warning(f"无法获取市场 {order.market_id} 的当前价格，跳过滑点检查")
                    except Exception as e:
                        self.logger.warning(f"价格滑点检查失败: {e}，继续提交订单")
                else:
                    self.logger.debug("未配置data_manager，跳过价格滑点检查")
            
            # create_market_order 可能会抛出异常（Lighter SDK内部错误）
            try:
                result = await self.signer_client.create_market_order(
                market_index=order.market_id,
                client_order_index=order.client_order_index,
                    base_amount=base_amount_units,  # 使用Lighter单位（0.0001为基础）
                    avg_execution_price=price_cents,  # 使用美分
                is_ask=is_ask
            )
                self.logger.debug(f"create_market_order 调用完成，返回值类型: {type(result)}")
            except AttributeError as ae:
                # Lighter SDK内部错误：'NoneType' object has no attribute 'code'
                self.logger.error(f"Lighter SDK内部错误: {ae}")
                self.logger.error(f"订单参数: market_id={order.market_id}, size={order.size}, price={order.price}")
                self.logger.error("可能原因:")
                self.logger.error("  1. Lighter API返回了None（服务异常）")
                self.logger.error("  2. 网络连接超时")
                self.logger.error("  3. 市场ID不存在或已关闭")
                self.logger.error("  4. 订单参数不符合市场规则")
                self.logger.error("建议: 检查市场ID是否正确，或使用较小的订单尝试")
                order.status = OrderStatus.REJECTED
                return
            except lighter.exceptions.BadRequestException as bre:
                # API明确拒绝了请求
                self.logger.error(f"订单被拒绝: {bre}")
                order.status = OrderStatus.REJECTED
                return
            except Exception as sdk_err:
                # 其他SDK错误
                self.logger.error(f"Lighter SDK调用失败: {sdk_err}")
                self.logger.error(f"错误类型: {type(sdk_err).__name__}")
                import traceback
                self.logger.error(f"堆栈追踪: {traceback.format_exc()}")
                order.status = OrderStatus.REJECTED
                return
            
            # 处理不同的返回值格式
            tx = None
            tx_hash = None
            err = None
            
            if result is None:
                self.logger.error(f"提交市价订单失败: create_market_order 返回 None，可能是网络问题或API错误")
                order.status = OrderStatus.REJECTED
                return
            
            # 安全地处理返回值
            try:
                if isinstance(result, tuple):
                    if len(result) == 3:
                        tx, tx_hash, err = result
                    elif len(result) == 2:
                        tx, err = result
                    else:
                        tx = result[0] if len(result) > 0 else None
                else:
                    # 直接返回tx对象
                    tx = result
                
                # 检查错误
                if err is not None:
                    # err可能是字符串或对象
                    error_msg = str(err) if err else "未知错误"
                    self.logger.error(f"创建市价订单失败: {error_msg}")
                    order.status = OrderStatus.REJECTED
                elif tx is not None:
                    # 检查tx是否有code属性（可能是错误对象）
                    if hasattr(tx, 'code') and hasattr(tx, 'message'):
                        # 这是一个错误响应
                        self.logger.error(f"创建市价订单失败: code={tx.code}, message={tx.message}")
                        order.status = OrderStatus.REJECTED
                    else:
                        # 成功
                        log_msg = f"市价订单已提交: {order.order_id}"
                        if tx_hash:
                            log_msg += f", tx_hash: {tx_hash}"
                        self.logger.info(log_msg)
                        order.status = OrderStatus.SUBMITTED
                        
                        # ⭐ 修复：订单提交成功后立即同步持仓
                        await self._sync_position_after_order(order)
                else:
                    self.logger.error(f"创建市价订单失败: 返回值异常，tx和err都为None")
                    order.status = OrderStatus.REJECTED
                    
            except AttributeError as ae:
                self.logger.error(f"提交市价订单失败: 访问返回值属性错误 - {ae}")
                self.logger.error(f"返回值类型: {type(result)}, 值: {result}")
                order.status = OrderStatus.REJECTED
                
            except Exception as e:
                self.logger.error(f"提交市价订单失败: {e}")
                import traceback
                self.logger.error(traceback.format_exc())
                order.status = OrderStatus.REJECTED
                
        except Exception as e:
            self.logger.error(f"提交市价订单失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            order.status = OrderStatus.REJECTED
            
    async def _check_order_status(self, order: Order):
        """检查订单状态 - 从Lighter API实际查询"""
        try:
            # 从Lighter API查询订单状态
            from lighter.api.order_api import OrderApi
            
            # 需要api_client来查询订单
            # 注意：signer_client没有查询订单的方法，需要使用api_client
            # 但OrderManager初始化时只传入了signer_client
            # 这里我们暂时使用signer_client的内部api_client
            
            # 尝试查询订单历史来确认订单状态
            # 注意：Lighter可能没有直接查询单个订单的API
            # 我们需要查询账户的订单历史
            
            self.logger.debug(f"正在查询订单状态: {order.order_id} (market={order.market_id}, client_order_index={order.client_order_index})")
            
            # 由于Lighter API的限制，我们采用保守策略：
            # 对于市价订单，等待一段时间后假设已成交或已取消
            # 但不应该立即标记为已成交
            
            # 实际上，我们需要从账户的订单历史查询
            # 但这需要api_client访问权限
            
            # 临时方案：不自动标记为FILLED，保持SUBMITTED状态
            # 让用户通过监控任务查看实际状态
            
            # TODO: 实现真正的订单状态查询
            # 需要访问 OrderApi.orders() 或类似方法
            
            self.logger.debug(f"订单 {order.order_id} 保持SUBMITTED状态，等待手动确认或API状态更新")
                
        except Exception as e:
            self.logger.error(f"检查订单状态失败: {e}")
            
    def create_order(self, market_id: int, side: OrderSide, order_type: OrderType,
                     size: float, price: float, leverage: float = 1.0,
                     margin_mode: MarginMode = MarginMode.CROSS,
                     price_slippage_tolerance: float = None,
                     slippage_enabled: bool = True) -> Order:
        """
        创建订单
        
        Args:
            market_id: 市场ID
            side: 订单方向
            order_type: 订单类型
            size: 订单大小
            price: 订单价格
            leverage: 杠杆倍数，默认1倍（不使用杠杆）
            margin_mode: 保证金模式，默认全仓（cross）
            price_slippage_tolerance: 价格滑点容忍度，默认使用策略配置
            slippage_enabled: 是否开启滑点检测，默认开启
            
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
                client_order_index=self.client_order_index,
                leverage=leverage,
                margin_mode=margin_mode,
                price_slippage_tolerance=price_slippage_tolerance or self.price_slippage_tolerance,
                slippage_enabled=slippage_enabled
            )
            
            # 添加到订单字典
            self.orders[order_id] = order
            
            # 添加到历史记录
            self.order_history.append(order)
            
            # 增加客户端订单索引
            self.client_order_index += 1
            
            # 打印订单信息（包括杠杆和保证金模式）
            margin_mode_zh = "全仓" if margin_mode == MarginMode.CROSS else "逐仓"
            self.logger.info(f"创建订单: {order_id}, 市场 {market_id}, {side.value}, {order_type.value}, 大小 {size}, 价格 {price}, 杠杆 {leverage}x, 保证金模式 {margin_mode_zh}")
            
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
            result = await self.signer_client.cancel_order(
                market_index=order.market_id,
                order_index=order.client_order_index
            )
            
            # 处理返回值
            tx = None
            tx_hash = None
            err = None
            
            if result is None:
                err = "返回值为 None"
            elif isinstance(result, tuple):
                if len(result) >= 3:
                    tx, tx_hash, err = result[0], result[1], result[2]
                elif len(result) == 2:
                    tx, err = result[0], result[1]
                else:
                    tx = result[0] if len(result) > 0 else None
            else:
                tx = result
            
            if err is not None:
                self.logger.error(f"取消订单失败: {err}")
                return False
            elif tx is not None:
                order.status = OrderStatus.CANCELLED
                log_msg = f"订单已取消: {order_id}"
                if tx_hash:
                    log_msg += f", tx_hash: {tx_hash}"
                self.logger.info(log_msg)
                return True
            else:
                self.logger.error(f"取消订单失败: 返回值异常")
                return False
                
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
    
    async def _sync_position_after_order(self, order: Order):
        """订单提交成功后同步持仓（带延迟和重试机制）"""
        try:
            if self.position_manager:
                self.logger.info(f"🔄 订单提交成功，开始同步持仓状态...")
                
                # 等待3秒让交易所处理订单
                await asyncio.sleep(3)
                
                # 尝试3次同步持仓
                for attempt in range(3):
                    try:
                        self.logger.info(f"🔄 尝试同步持仓 (第{attempt + 1}次)...")
                        await self.position_manager._load_existing_positions()
                        
                        # 检查是否成功同步到持仓
                        position = self.position_manager.get_position(order.market_id)
                        if position:
                            self.logger.info(f"✅ 持仓同步成功: 市场{order.market_id}, {position.side.value}, 数量{position.size:.6f}")
                            return  # 成功同步，退出重试循环
                        else:
                            if attempt < 2:  # 不是最后一次尝试
                                self.logger.info(f"⏳ 持仓尚未出现，等待2秒后重试...")
                                await asyncio.sleep(2)
                            else:
                                # 最后一次尝试失败
                                self.logger.warning(f"⚠️  订单提交成功但未检测到持仓: 市场{order.market_id}")
                                self.logger.warning("可能原因:")
                                self.logger.warning("  1. 订单尚未完全成交（市价单需要时间匹配）")
                                self.logger.warning("  2. 持仓API响应延迟")
                                self.logger.warning("  3. 订单数量太小，未达到最小持仓显示要求")
                                self.logger.warning("  4. 交易所内部处理延迟")
                                self.logger.info("💡 建议: 等待几分钟后手动检查持仓，或查看交易所界面确认订单状态")
                    except Exception as e:
                        self.logger.error(f"持仓同步失败 (第{attempt + 1}次): {e}")
                        if attempt < 2:
                            await asyncio.sleep(2)
            else:
                self.logger.warning("持仓管理器未设置，无法同步持仓状态")
                
        except Exception as e:
            self.logger.error(f"持仓同步失败: {e}")
            # 不抛出异常，避免影响订单流程
