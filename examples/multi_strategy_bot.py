"""
多策略交易机器人示例
同时运行多个交易策略
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from quant_trading import TradingEngine, Config
from quant_trading.strategies import MeanReversionStrategy, MomentumStrategy, ArbitrageStrategy


async def main():
    """多策略交易机器人主函数"""
    print("启动多策略交易机器人...")
    
    # 创建配置
    config = Config.create_default()
    
    # 配置Lighter参数
    config.lighter_config.update({
        "base_url": "https://testnet.zklighter.elliot.ai",
        "api_key_private_key": "your_api_key_private_key_here",
        "account_index": 0,
        "api_key_index": 0
    })
    
    # 调整风险参数
    config.risk_config.update({
        "max_position_size": 0.03,  # 每个策略最大仓位3%
        "max_daily_loss": 0.03,     # 最大日亏损3%
        "max_drawdown": 0.12,       # 最大回撤12%
        "max_open_orders": 30,      # 增加最大开仓订单数
    })
    
    try:
        # 创建交易引擎
        engine = TradingEngine(config)
        
        # 添加多个策略
        strategies = [
            MeanReversionStrategy(
                config=config,
                market_id=0,
                lookback_period=20,
                threshold=2.0
            ),
            MomentumStrategy(
                config=config,
                market_id=0,
                short_period=5,
                long_period=20,
                momentum_threshold=0.02
            ),
            ArbitrageStrategy(
                config=config,
                market_id_1=0,
                market_id_2=1,
                price_threshold=0.01
            )
        ]
        
        for strategy in strategies:
            engine.add_strategy(strategy)
            print(f"添加策略: {strategy.name}")
        
        print("多策略交易机器人配置完成")
        print(f"策略数量: {len(strategies)}")
        print("风险控制: 已启用")
        
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
        print("多策略交易机器人已停止")


if __name__ == "__main__":
    asyncio.run(main())
