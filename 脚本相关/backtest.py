"""
回测脚本
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import json

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from quant_trading import Config
from quant_trading.backtesting import BacktestEngine
from quant_trading.strategies import MeanReversionStrategy, MomentumStrategy, ArbitrageStrategy


def generate_sample_data(market_id: int, days: int = 30) -> list:
    """生成示例数据"""
    import random
    import numpy as np
    
    data = []
    base_price = 100.0
    current_time = datetime.now() - timedelta(days=days)
    
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


async def run_backtest(strategy_name: str, config: Config, days: int = 30):
    """运行回测"""
    print(f"开始回测策略: {strategy_name}")
    
    # 创建回测引擎
    backtest_engine = BacktestEngine(config)
    
    # 生成示例数据
    sample_data = generate_sample_data(0, days)
    backtest_engine.load_historical_data(0, sample_data)
    
    # 创建策略
    if strategy_name == "mean_reversion":
        strategy = MeanReversionStrategy(
            config=config,
            market_id=0,
            lookback_period=20,
            threshold=2.0
        )
    elif strategy_name == "momentum":
        strategy = MomentumStrategy(
            config=config,
            market_id=0,
            short_period=5,
            long_period=20,
            momentum_threshold=0.02
        )
    elif strategy_name == "arbitrage":
        # 为套利策略生成两个市场的数据
        sample_data_2 = generate_sample_data(1, days)
        backtest_engine.load_historical_data(1, sample_data_2)
        
        strategy = ArbitrageStrategy(
            config=config,
            market_id_1=0,
            market_id_2=1,
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
    
    # 保存结果
    result_file = f"backtest_result_{strategy_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result.to_dict(), f, indent=2, ensure_ascii=False, default=str)
    
    print(f"回测结果已保存到: {result_file}")
    
    return result


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Lighter量化交易回测程序")
    parser.add_argument("--config", "-c", type=str, default="config.yaml", 
                       help="配置文件路径")
    parser.add_argument("--strategy", "-s", type=str, 
                       choices=["mean_reversion", "momentum", "arbitrage", "all"],
                       default="all", help="要回测的策略")
    parser.add_argument("--days", "-d", type=int, default=30, 
                       help="回测天数")
    
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
        
    # 运行回测
    try:
        if args.strategy == "all":
            strategies = ["mean_reversion", "momentum", "arbitrage"]
            for strategy_name in strategies:
                await run_backtest(strategy_name, config, args.days)
                print("\n" + "="*50 + "\n")
        else:
            await run_backtest(args.strategy, config, args.days)
            
    except Exception as e:
        print(f"回测运行错误: {e}")
        return 1
        
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
