#!/usr/bin/env python3
"""
实时tick数据示例
演示如何使用修改后的系统进行实时tick交易
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from quant_trading.core.trading_engine import TradingEngine
from quant_trading.strategies.ut_bot_strategy import UTBotStrategy
from quant_trading.utils.config import Config

async def main():
    """主函数"""
    print("🚀 启动实时tick交易系统...")
    
    # 加载配置
    config = Config("config.yaml")
    
    # 创建交易引擎
    engine = TradingEngine(config)
    
    # 创建UT Bot策略（已启用实时tick模式）
    ut_bot_strategy = UTBotStrategy(
        name="UT_Bot_RealTime",
        config=config,
        ut_config={
            'key_value': 3.0,
            'atr_period': 10,
            'use_heikin_ashi': False,
            'ema_length': 200,
            'risk_per_trade': 2.5,
            'position_size_usd': 1000,
            'stop_loss': 0.02,
            'take_profit': 0.04
        }
    )
    
    # 添加策略到引擎
    engine.add_strategy(ut_bot_strategy)
    
    try:
        # 启动交易引擎
        await engine.start()
        
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断，正在停止系统...")
    except Exception as e:
        print(f"❌ 系统错误: {e}")
    finally:
        # 停止引擎
        await engine.stop()
        print("✅ 系统已安全停止")

if __name__ == "__main__":
    asyncio.run(main())
