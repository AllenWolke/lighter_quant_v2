"""
UT Bot策略示例
演示如何使用UT Bot策略进行交易
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from quant_trading import TradingEngine, Config
from quant_trading.strategies import UTBotStrategy


async def main():
    """UT Bot策略示例"""
    print("UT Bot策略交易示例")
    print("=" * 40)
    
    # 创建配置
    config = Config.create_default()
    
    # 配置Lighter参数（需要替换为实际值）
    config.lighter_config.update({
        "base_url": "https://testnet.zklighter.elliot.ai",
        "api_key_private_key": "your_api_key_private_key_here",
        "account_index": 0,
        "api_key_index": 0
    })
    
    # 启用TradingView数据源
    config.data_sources = {
        "primary": "lighter",
        "tradingview": {
            "enabled": True,
            "session_id": "qs_1",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "symbol_mapping": {
                "BTC_USDT": "BTCUSDT",
                "ETH_USDT": "ETHUSDT"
            }
        }
    }
    
    # 调整风险参数
    config.risk_config.update({
        "max_position_size": 0.05,  # 最大仓位5%
        "max_daily_loss": 0.02,     # 最大日亏损2%
        "max_drawdown": 0.10,       # 最大回撤10%
    })
    
    try:
        # 创建交易引擎
        engine = TradingEngine(config)
        
        # 添加UT Bot策略
        ut_bot_strategy = UTBotStrategy(
            config=config,
            market_id=0,
            key_value=1.0,      # 关键值，影响敏感度
            atr_period=10,      # ATR周期
            use_heikin_ashi=False  # 是否使用Heikin Ashi
        )
        engine.add_strategy(ut_bot_strategy)
        
        print("✅ UT Bot策略配置完成")
        print(f"策略参数:")
        print(f"  - 市场ID: 0")
        print(f"  - 关键值: 1.0")
        print(f"  - ATR周期: 10")
        print(f"  - 使用Heikin Ashi: False")
        print(f"  - 仓位大小: 0.05")
        print()
        
        print("🚀 启动交易引擎...")
        print("按 Ctrl+C 停止程序")
        print()
        
        # 启动交易引擎
        await engine.start()
        
    except KeyboardInterrupt:
        print("\n⏹️  收到停止信号，正在关闭...")
    except Exception as e:
        print(f"❌ 运行错误: {e}")
    finally:
        if 'engine' in locals():
            await engine.stop()
        print("✅ UT Bot策略已停止")


if __name__ == "__main__":
    asyncio.run(main())
