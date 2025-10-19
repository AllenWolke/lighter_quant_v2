"""
UT Bot策略使用示例
演示如何使用UT Bot策略进行量化交易
"""

import asyncio
import yaml
from typing import Dict, Any
from datetime import datetime

from .ut_bot_strategy import UTBotStrategy, UTBotConfig
from ..utils.config import Config


async def run_ut_bot_strategy():
    """运行UT Bot策略示例"""
    
    # 加载配置
    with open('quant_trading/strategies/ut_bot_config.yaml', 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)
    
    # 创建系统配置
    config = Config()
    
    # 创建UT Bot策略配置
    ut_config = UTBotConfig(
        key_value=config_data['ut_bot_config']['key_value'],
        atr_period=config_data['ut_bot_config']['atr_period'],
        use_heikin_ashi=config_data['ut_bot_config']['use_heikin_ashi'],
        ema_length=config_data['ut_bot_config']['ema_length'],
        risk_per_trade=config_data['ut_bot_config']['risk_per_trade'],
        atr_multiplier=config_data['ut_bot_config']['atr_multiplier'],
        risk_reward_breakeven=config_data['ut_bot_config']['risk_reward_breakeven'],
        risk_reward_takeprofit=config_data['ut_bot_config']['risk_reward_takeprofit'],
        tp_percent=config_data['ut_bot_config']['tp_percent'],
        stoploss_type=config_data['ut_bot_config']['stoploss_type'],
        swing_high_bars=config_data['ut_bot_config']['swing_high_bars'],
        swing_low_bars=config_data['ut_bot_config']['swing_low_bars'],
        enable_long=config_data['ut_bot_config']['enable_long'],
        enable_short=config_data['ut_bot_config']['enable_short'],
        use_takeprofit=config_data['ut_bot_config']['use_takeprofit'],
        use_leverage=config_data['ut_bot_config']['use_leverage'],
        trading_start_time=config_data['ut_bot_config']['trading_start_time'],
        trading_end_time=config_data['ut_bot_config']['trading_end_time']
    )
    
    # 创建策略实例
    strategy = UTBotStrategy("UT_Bot_Strategy", config, ut_config)
    
    # 初始化策略
    await strategy.initialize()
    
    # 启动策略
    await strategy.start()
    
    print("UT Bot策略已启动")
    print(f"策略配置: {ut_config}")
    
    # 模拟市场数据
    await simulate_market_data(strategy)
    
    # 停止策略
    await strategy.stop()
    
    # 显示策略状态
    status = strategy.get_strategy_status()
    print(f"\n策略最终状态:")
    print(f"信号生成数量: {status['signals_generated']}")
    print(f"交易执行数量: {status['trades_executed']}")
    print(f"总盈亏: {status['total_pnl']}")


async def simulate_market_data(strategy: UTBotStrategy):
    """模拟市场数据"""
    import random
    
    # 模拟BTCUSDT市场数据
    market_id = 1
    base_price = 50000.0
    
    print("\n开始模拟市场数据...")
    
    for i in range(100):  # 模拟100个数据点
        # 生成模拟价格数据
        price_change = random.uniform(-0.02, 0.02)  # ±2%的价格变化
        base_price *= (1 + price_change)
        
        # 生成OHLC数据
        open_price = base_price * random.uniform(0.998, 1.002)
        high_price = max(open_price, base_price) * random.uniform(1.0, 1.01)
        low_price = min(open_price, base_price) * random.uniform(0.99, 1.0)
        close_price = base_price
        volume = random.uniform(1000, 5000)
        
        market_data = {
            market_id: {
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': volume,
                'timestamp': datetime.now()
            }
        }
        
        # 处理市场数据
        await strategy.process_market_data(market_data)
        
        # 每10个数据点显示一次状态
        if (i + 1) % 10 == 0:
            status = strategy.get_strategy_status()
            print(f"数据点 {i+1}: 价格={close_price:.2f}, 信号数={status['signals_generated']}, 交易数={status['trades_executed']}")
        
        # 模拟实时数据间隔
        await asyncio.sleep(0.1)


def print_strategy_info():
    """打印策略信息"""
    print("=" * 60)
    print("UT Bot策略 - 量化交易系统")
    print("=" * 60)
    print("策略特点:")
    print("1. 基于UT Bot Alerts指标的动态止损")
    print("2. 200周期EMA趋势过滤")
    print("3. ATR自适应风险管理")
    print("4. 盈亏比优化和分批止盈")
    print("5. 支持多空双向交易")
    print("=" * 60)
    print("核心参数:")
    print("- 关键值(Key Value): 3.0")
    print("- ATR周期: 1")
    print("- EMA长度: 200")
    print("- 风险比例: 2.5%")
    print("- 盈亏比: 1:3")
    print("=" * 60)


if __name__ == "__main__":
    print_strategy_info()
    asyncio.run(run_ut_bot_strategy())
