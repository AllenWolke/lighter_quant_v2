"""
Lighter量化交易程序主入口
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from quant_trading import TradingEngine, Config, setup_logger
from quant_trading.strategies import MeanReversionStrategy, MomentumStrategy, ArbitrageStrategy, UTBotStrategy


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Lighter量化交易程序")
    parser.add_argument("--config", "-c", type=str, default="config.yaml", 
                       help="配置文件路径")
    parser.add_argument("--strategy", "-s", type=str, 
                       choices=["mean_reversion", "momentum", "arbitrage", "ut_bot", "all"],
                       default="all", help="要运行的策略")
    parser.add_argument("--market", "-m", type=int, default=0, 
                       help="市场ID")
    parser.add_argument("--dry-run", action="store_true", 
                       help="模拟运行模式")
    
    args = parser.parse_args()
    
    # 加载配置
    try:
        if os.path.exists(args.config):
            config = Config.from_file(args.config)
        else:
            print(f"配置文件 {args.config} 不存在，使用默认配置")
            config = Config.create_default()
            config.save_to_file(args.config)
            
        config.validate()
    except Exception as e:
        print(f"配置加载失败: {e}")
        return 1
        
    # 设置日志
    logger = setup_logger("Main", config.log_level)
    logger.info("启动Lighter量化交易程序")
    
    # 创建交易引擎
    try:
        engine = TradingEngine(config)
        
        # 添加策略
        if args.strategy in ["mean_reversion", "all"]:
            mean_reversion = MeanReversionStrategy(
                config=config,
                market_id=args.market,
                lookback_period=20,
                threshold=2.0
            )
            engine.add_strategy(mean_reversion)
            
        if args.strategy in ["momentum", "all"]:
            momentum = MomentumStrategy(
                config=config,
                market_id=args.market,
                short_period=5,
                long_period=20,
                momentum_threshold=0.02
            )
            engine.add_strategy(momentum)
            
        if args.strategy in ["arbitrage", "all"]:
            arbitrage = ArbitrageStrategy(
                config=config,
                market_id_1=0,
                market_id_2=1,
                price_threshold=0.01
            )
            engine.add_strategy(arbitrage)
            
        if args.strategy in ["ut_bot", "all"]:
            ut_bot = UTBotStrategy(
                config=config,
                market_id=args.market,
                key_value=1.0,
                atr_period=10,
                use_heikin_ashi=False
            )
            engine.add_strategy(ut_bot)
            
        # 发送启动通知
        if hasattr(engine, 'notification_manager'):
            from quant_trading.notifications import NotificationType, NotificationLevel
            await engine.notification_manager.send_notification(
                notification_type=NotificationType.SYSTEM_ERROR,
                level=NotificationLevel.INFO,
                title="交易系统启动",
                message=f"量化交易系统已启动，策略: {args.strategy}",
                data={"strategy": args.strategy, "market_id": args.market}
            )
        
        # 启动交易引擎
        logger.info("启动交易引擎...")
        await engine.start()
        
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在停止...")
    except Exception as e:
        logger.error(f"程序运行错误: {e}")
        return 1
    finally:
        if 'engine' in locals():
            await engine.stop()
            
    logger.info("程序已退出")
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
