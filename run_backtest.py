#!/usr/bin/env python3
"""
回测程序启动脚本
提供交互式回测功能
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from quant_trading import Config
from quant_trading.backtesting import BacktestEngine
from quant_trading.strategies import MeanReversionStrategy, MomentumStrategy, ArbitrageStrategy


def print_banner():
    """打印程序横幅"""
    print("=" * 60)
    print("📊 Lighter量化交易回测程序")
    print("=" * 60)
    print()


def get_backtest_config():
    """获取回测配置"""
    print("请配置回测参数:")
    print()
    
    # 选择策略
    print("1. 选择回测策略:")
    print("   1) 均值回归策略")
    print("   2) 动量策略")
    print("   3) 套利策略")
    print("   4) 所有策略")
    
    while True:
        choice = input("请选择 (1-4): ").strip()
        if choice in ["1", "2", "3", "4"]:
            strategy_choice = choice
            break
        else:
            print("无效选择，请重新输入")
    
    print()
    
    # 选择回测天数
    try:
        days = int(input("请输入回测天数 (默认30天): ").strip() or "30")
        if days <= 0:
            print("❌ 回测天数必须大于0")
            return None
    except ValueError:
        print("❌ 回测天数必须是数字")
        return None
    
    print()
    
    # 选择市场
    try:
        market_id = int(input("请输入市场ID (默认0): ").strip() or "0")
    except ValueError:
        market_id = 0
    
    print()
    
    return {
        "strategy_choice": strategy_choice,
        "days": days,
        "market_id": market_id
    }


def generate_sample_data(market_id: int, days: int) -> list:
    """生成示例数据"""
    import random
    import numpy as np
    
    data = []
    base_price = 100.0
    current_time = datetime.now() - timedelta(days=days)
    
    print(f"📈 生成市场 {market_id} 的 {days} 天示例数据...")
    
    for i in range(days * 24 * 60):  # 每分钟一个数据点
        # 随机游走
        change = random.gauss(0, 0.001)
        base_price *= (1 + change)
        
        # 生成OHLCV数据
        high = base_price * (1 + abs(random.gauss(0, 0.005)))
        low = base_price * (1 - abs(random.gauss(0, 0.005)))
        open_price = base_price * (1 + random.gauss(0, 0.002))
        close_price = base_price
        volume = random.uniform(1000, 10000)
        
        data.append({
            "timestamp": int(current_time.timestamp()),
            "open": open_price,
            "high": high,
            "low": low,
            "close": close_price,
            "volume": volume
        })
        
        current_time += timedelta(minutes=1)
        
    return data


async def run_single_backtest(strategy_name: str, config: Config, days: int, market_id: int):
    """运行单个策略回测"""
    print(f"\n🔄 开始回测策略: {strategy_name}")
    
    # 创建回测引擎
    backtest_engine = BacktestEngine(config)
    
    # 生成示例数据
    sample_data = generate_sample_data(market_id, days)
    backtest_engine.load_historical_data(market_id, sample_data)
    
    # 为套利策略生成第二个市场的数据
    if strategy_name == "arbitrage":
        sample_data_2 = generate_sample_data(market_id + 1, days)
        backtest_engine.load_historical_data(market_id + 1, sample_data_2)
    
    # 创建策略
    if strategy_name == "mean_reversion":
        strategy = MeanReversionStrategy(
            config=config,
            market_id=market_id,
            lookback_period=20,
            threshold=2.0
        )
    elif strategy_name == "momentum":
        strategy = MomentumStrategy(
            config=config,
            market_id=market_id,
            short_period=5,
            long_period=20,
            momentum_threshold=0.02
        )
    elif strategy_name == "arbitrage":
        strategy = ArbitrageStrategy(
            config=config,
            market_id_1=market_id,
            market_id_2=market_id + 1,
            price_threshold=0.01
        )
    else:
        raise ValueError(f"未知策略: {strategy_name}")
    
    # 设置回测时间
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # 运行回测
    result = await backtest_engine.run_backtest(strategy, start_date, end_date)
    
    # 打印结果
    result.print_summary()
    
    return result


async def main():
    """主函数"""
    print_banner()
    
    # 获取回测配置
    backtest_config = get_backtest_config()
    if not backtest_config:
        return 1
    
    # 创建配置
    config = Config.create_default()
    
    # 调整风险参数（回测用）
    config.risk_config.update({
        "max_position_size": 0.1,
        "max_daily_loss": 0.1,
        "max_drawdown": 0.3,
    })
    
    try:
        strategy_choice = backtest_config["strategy_choice"]
        days = backtest_config["days"]
        market_id = backtest_config["market_id"]
        
        if strategy_choice == "4":  # 所有策略
            strategies = ["mean_reversion", "momentum", "arbitrage"]
            results = []
            
            for strategy_name in strategies:
                result = await run_single_backtest(strategy_name, config, days, market_id)
                results.append(result)
                print("\n" + "="*50 + "\n")
            
            # 打印总结
            print("📊 回测总结:")
            print("-" * 40)
            for i, result in enumerate(results):
                print(f"{i+1}. {result.strategy_name}: 总收益 {result.total_return:.2%}, 夏普比率 {result.sharpe_ratio:.2f}")
                
        else:
            # 单个策略
            strategy_map = {
                "1": "mean_reversion",
                "2": "momentum", 
                "3": "arbitrage"
            }
            strategy_name = strategy_map[strategy_choice]
            await run_single_backtest(strategy_name, config, days, market_id)
        
        print("\n✅ 回测完成!")
        
    except Exception as e:
        print(f"❌ 回测运行错误: {e}")
        return 1
        
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 再见!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 程序错误: {e}")
        sys.exit(1)
