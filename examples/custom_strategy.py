"""
自定义策略示例
演示如何创建自定义交易策略
"""

import asyncio
import sys
from pathlib import Path
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from quant_trading import TradingEngine, Config
from quant_trading.strategies.base_strategy import BaseStrategy


class RSIStrategy(BaseStrategy):
    """RSI策略示例"""
    
    def __init__(self, config: Config, market_id: int = 0, 
                 rsi_period: int = 14, oversold: float = 30, overbought: float = 70):
        """
        初始化RSI策略
        
        Args:
            config: 配置对象
            market_id: 市场ID
            rsi_period: RSI周期
            oversold: 超卖阈值
            overbought: 超买阈值
        """
        super().__init__("RSI", config)
        
        self.market_id = market_id
        self.rsi_period = rsi_period
        self.oversold = oversold
        self.overbought = overbought
        
        # 策略参数
        self.position_size = 0.1
        self.stop_loss = 0.02
        self.take_profit = 0.01
        
        # 状态变量
        self.last_signal_time = None
        self.signal_cooldown = 300  # 5分钟冷却时间
        
    async def on_initialize(self):
        """策略初始化"""
        self.logger.info(f"初始化RSI策略: 市场 {self.market_id}, 周期 {self.rsi_period}")
        
    async def on_start(self):
        """策略启动"""
        self.logger.info("RSI策略已启动")
        
    async def on_stop(self):
        """策略停止"""
        self.logger.info("RSI策略已停止")
        
    async def process_market_data(self, market_data: Dict[int, Dict[str, Any]]):
        """处理市场数据"""
        if self.market_id not in market_data:
            return
            
        market_data_info = market_data[self.market_id]
        candlesticks = market_data_info.get("candlesticks", [])
        
        if len(candlesticks) < self.rsi_period + 1:
            return
            
        # 获取当前价格
        current_price = self._get_current_price(candlesticks)
        if current_price is None:
            return
            
        # 计算RSI
        rsi = self._calculate_rsi(candlesticks)
        if rsi is None:
            return
            
        # 检查信号冷却
        current_time = datetime.now().timestamp()
        if (self.last_signal_time and 
            current_time - self.last_signal_time < self.signal_cooldown):
            return
            
        # 生成交易信号
        await self._generate_signal(current_price, rsi)
        
    def _get_current_price(self, candlesticks: List[Dict[str, Any]]) -> Optional[float]:
        """获取当前价格"""
        if not candlesticks:
            return None
        return candlesticks[-1]["close"]
        
    def _calculate_rsi(self, candlesticks: List[Dict[str, Any]]) -> Optional[float]:
        """计算RSI指标"""
        if len(candlesticks) < self.rsi_period + 1:
            return None
            
        prices = [c["close"] for c in candlesticks[-self.rsi_period-1:]]
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gain = np.mean(gains)
        avg_loss = np.mean(losses)
        
        if avg_loss == 0:
            return 100
            
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
        
    async def _generate_signal(self, current_price: float, rsi: float):
        """生成交易信号"""
        # 检查是否已有仓位
        position = self._get_position(self.market_id)
        
        if position:
            # 已有仓位，检查是否需要平仓
            await self._check_exit_conditions(position, current_price, rsi)
        else:
            # 没有仓位，检查是否需要开仓
            if rsi < self.oversold:
                # RSI超卖，做多
                await self._open_long_position(current_price, rsi)
            elif rsi > self.overbought:
                # RSI超买，做空
                await self._open_short_position(current_price, rsi)
                
    async def _open_long_position(self, price: float, rsi: float):
        """开多仓"""
        if not self._check_risk_limits(self.market_id, self.position_size, price):
            return
            
        order = self._create_order(
            market_id=self.market_id,
            side="buy",
            order_type="market",
            size=self.position_size,
            price=price
        )
        
        if order:
            self._log_signal("LONG", self.market_id, 
                           price=price, rsi=rsi, size=self.position_size)
            self.last_signal_time = datetime.now().timestamp()
            
    async def _open_short_position(self, price: float, rsi: float):
        """开空仓"""
        if not self._check_risk_limits(self.market_id, self.position_size, price):
            return
            
        order = self._create_order(
            market_id=self.market_id,
            side="sell",
            order_type="market",
            size=self.position_size,
            price=price
        )
        
        if order:
            self._log_signal("SHORT", self.market_id, 
                           price=price, rsi=rsi, size=self.position_size)
            self.last_signal_time = datetime.now().timestamp()
            
    async def _check_exit_conditions(self, position, current_price: float, rsi: float):
        """检查平仓条件"""
        from quant_trading.core.position_manager import PositionSide
        
        entry_price = position.entry_price
        pnl_ratio = 0.0
        
        if position.side == PositionSide.LONG:
            pnl_ratio = (current_price - entry_price) / entry_price
        else:
            pnl_ratio = (entry_price - current_price) / entry_price
            
        # 检查止损和止盈
        should_exit = False
        exit_reason = ""
        
        if pnl_ratio <= -self.stop_loss:
            should_exit = True
            exit_reason = "止损"
        elif pnl_ratio >= self.take_profit:
            should_exit = True
            exit_reason = "止盈"
        elif self._is_rsi_reversal(position.side, rsi):
            should_exit = True
            exit_reason = "RSI反转"
            
        if should_exit:
            order = self._create_order(
                market_id=self.market_id,
                side="sell" if position.side == PositionSide.LONG else "buy",
                order_type="market",
                size=position.size,
                price=current_price
            )
            
            if order:
                self._log_signal("EXIT", self.market_id, 
                               reason=exit_reason, pnl_ratio=pnl_ratio, rsi=rsi)
                self.last_signal_time = datetime.now().timestamp()
                
    def _is_rsi_reversal(self, position_side, rsi: float) -> bool:
        """检查RSI是否反转"""
        if position_side == PositionSide.LONG:
            return rsi > 50  # 多头仓位，RSI回到50以上
        else:
            return rsi < 50  # 空头仓位，RSI回到50以下


async def main():
    """自定义策略示例主函数"""
    print("启动自定义RSI策略交易机器人...")
    
    # 创建配置
    config = Config.create_default()
    
    # 配置Lighter参数
    config.lighter_config.update({
        "base_url": "https://testnet.zklighter.elliot.ai",
        "api_key_private_key": "your_api_key_private_key_here",
        "account_index": 0,
        "api_key_index": 0
    })
    
    try:
        # 创建交易引擎
        engine = TradingEngine(config)
        
        # 添加自定义RSI策略
        rsi_strategy = RSIStrategy(
            config=config,
            market_id=0,
            rsi_period=14,
            oversold=30,
            overbought=70
        )
        engine.add_strategy(rsi_strategy)
        
        print("自定义策略交易机器人配置完成")
        print("策略: RSI策略")
        print("参数: 周期14, 超卖30, 超买70")
        
        # 启动交易引擎
        print("启动交易引擎...")
        await engine.start()
        
    except KeyboardInterrupt:
        print("\n收到停止信号，正在关闭...")
    except Exception as e:
        print(f"运行错误: {e}")
    finally:
        if 'engine' in locals():
            await engine.stop()
        print("自定义策略交易机器人已停止")


if __name__ == "__main__":
    asyncio.run(main())
