"""
简单交易机器人示例
演示如何使用量化交易框架
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from quant_trading import TradingEngine, Config
from quant_trading.strategies import MeanReversionStrategy


async def main():
    """简单交易机器人主函数"""
    print("启动简单交易机器人...")
    
    # 创建配置
    config = Config.create_default()
    
    # 配置Lighter参数（需要替换为实际值）
    config.lighter_config.update({
        "base_url": "https://testnet.zklighter.elliot.ai",
        "api_key_private_key": "your_api_key_private_key_here",
        "account_index": 0,
        "api_key_index": 0
    })
    
    # 调整风险参数（降低风险）
    config.risk_config.update({
        "max_position_size": 0.05,  # 最大仓位5%
        "max_daily_loss": 0.02,     # 最大日亏损2%
        "max_drawdown": 0.10,       # 最大回撤10%
    })
    
    try:
        # 创建交易引擎
        engine = TradingEngine(config)
        
        # 添加均值回归策略
        strategy = MeanReversionStrategy(
            config=config,
            market_id=0,
            lookback_period=20,
            threshold=2.0
        )
        engine.add_strategy(strategy)
        
        print("交易机器人配置完成")
        print("策略: 均值回归")
        print("市场: 0")
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
        print("交易机器人已停止")


if __name__ == "__main__":
    asyncio.run(main())
