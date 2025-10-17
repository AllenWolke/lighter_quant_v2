#!/usr/bin/env python3
"""
Lighter量化交易程序启动脚本 - 多市场版本
支持多时间周期确认和多市场并发交易
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from quant_trading import TradingEngine, Config
from quant_trading.strategies import UTBotStrategy, MultiMarketStrategyWrapper
from datetime import datetime

def print_banner():
    """打印程序横幅"""
    print("=" * 70)
    print("🚀 Lighter量化交易程序 - 多市场并发版本 v1.9.0")
    print("=" * 70)
    print()
    print("✨ 新功能:")
    print("  ✅ 多时间周期确认 (5分钟+1分钟)")
    print("  ✅ 多市场并发交易 (BTC, ETH, SOL等)")
    print("  ✅ asyncio+aiohttp优化")
    print("  ✅ 连接池管理和限流保护")
    print("=" * 70)
    print()

async def main():
    """主函数"""
    print_banner()
    
    # 加载配置
    if not os.path.exists('config.yaml'):
        print("❌ config.yaml 不存在，请先创建配置文件")
        return 1
    
    config = Config.from_file('config.yaml')
    print("✅ 已从 config.yaml 加载配置")
    print()
    
    # 读取UT Bot配置
    ut_config = config.strategies.get('ut_bot', {})
    
    # 检查是否启用多市场
    market_ids = ut_config.get('market_ids', [ut_config.get('market_id', 3)])
    enable_multi_timeframe = ut_config.get('enable_multi_timeframe', False)
    
    print("📋 策略配置:")
    print(f"  市场: {market_ids}")
    print(f"  多时间周期: {'✅ 已启用' if enable_multi_timeframe else '❌ 未启用'}")
    print(f"  仓位大小: ${ut_config.get('position_size', 2.0)} USD (每个市场)")
    print(f"  杠杆: {ut_config.get('leverage', 10.0)}x")
    print(f"  保证金模式: {ut_config.get('margin_mode', 'isolated')}")
    print(f"  滑点容忍度: {ut_config.get('price_slippage_tolerance', 0.02) * 100:.1f}%")
    print()
    
    # 风险确认
    total_investment = len(market_ids) * ut_config.get('position_size', 2.0)
    print("💰 资金需求估算:")
    print(f"  每个市场: ${ut_config.get('position_size', 2.0)} USD")
    print(f"  市场数量: {len(market_ids)}")
    print(f"  总投入: ${total_investment} USD")
    print(f"  保证金需求: ${total_investment / ut_config.get('leverage', 10.0):.2f} USD (使用{ut_config.get('leverage', 10.0)}x杠杆)")
    print()
    
    confirm = input("是否确认启动多市场交易？(y/N): ").strip().lower()
    if confirm != 'y':
        print("已取消启动")
        return 0
    
    print()
    print("🚀 启动交易引擎...")
    print()
    
    try:
        # 创建交易引擎
        engine = TradingEngine(config)
        
        # 如果只有一个市场，使用单市场模式
        if len(market_ids) == 1:
            print(f"📊 单市场模式: 市场 {market_ids[0]}")
            strategy = UTBotStrategy(
                config=config,
                market_id=market_ids[0],
                key_value=ut_config.get('key_value', 1.0),
                atr_period=ut_config.get('atr_period', 10),
                use_heikin_ashi=ut_config.get('use_heikin_ashi', False),
                position_size=ut_config.get('position_size', 2.0),
                stop_loss=ut_config.get('stop_loss', 0.02),
                take_profit=ut_config.get('take_profit', 0.01),
                leverage=ut_config.get('leverage', 10.0),
                margin_mode=ut_config.get('margin_mode', 'isolated'),
                order_type=ut_config.get('order_type', 'market'),
                limit_price_offset=ut_config.get('limit_price_offset', 0.002),
                enable_multi_timeframe=enable_multi_timeframe
            )
            engine.add_strategy(strategy)
        else:
            # 多市场模式
            print(f"📊 多市场并发模式: {len(market_ids)} 个市场")
            multi_market_wrapper = MultiMarketStrategyWrapper(
                strategy_class=UTBotStrategy,
                config=config,
                market_ids=market_ids,
                key_value=ut_config.get('key_value', 1.0),
                atr_period=ut_config.get('atr_period', 10),
                use_heikin_ashi=ut_config.get('use_heikin_ashi', False),
                position_size=ut_config.get('position_size', 2.0),
                stop_loss=ut_config.get('stop_loss', 0.02),
                take_profit=ut_config.get('take_profit', 0.01),
                leverage=ut_config.get('leverage', 10.0),
                margin_mode=ut_config.get('margin_mode', 'isolated'),
                order_type=ut_config.get('order_type', 'market'),
                limit_price_offset=ut_config.get('limit_price_offset', 0.002),
                enable_multi_timeframe=enable_multi_timeframe
            )
            
            # 初始化多市场包装器
            await multi_market_wrapper.initialize()
            await multi_market_wrapper.start()
            
            # 添加所有策略实例到引擎
            for strategy in multi_market_wrapper.get_all_strategies():
                engine.add_strategy(strategy)
            
            print()
            print("✅ 多市场策略已初始化")
            stats = multi_market_wrapper.get_statistics()
            print(f"  管理市场数: {stats['total_markets']}")
            print(f"  最大并发数: {stats['max_concurrent_tasks']}")
            print(f"  限流配置: {stats['max_requests_per_window']}请求/{stats['rate_limit_window']}秒")
        
        print()
        print("📊 启动交易引擎...")
        print("按 Ctrl+C 停止程序")
        print()
        
        # 启动交易引擎
        await engine.start()
        
    except KeyboardInterrupt:
        print("\n⏹️  收到停止信号，正在关闭...")
    except Exception as e:
        print(f"❌ 运行错误: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        if 'engine' in locals():
            await engine.stop()
        if 'multi_market_wrapper' in locals():
            await multi_market_wrapper.stop()
        print("✅ 交易引擎已停止")

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code or 0)
    except KeyboardInterrupt:
        print("\n👋 再见!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 程序错误: {e}")
        sys.exit(1)

