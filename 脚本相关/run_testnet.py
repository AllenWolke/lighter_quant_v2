#!/usr/bin/env python3
"""
测试网运行脚本
简化的测试网交易程序启动脚本
"""

import asyncio
import sys
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from quant_trading import TradingEngine, Config
from quant_trading.strategies import UTBotStrategy, MeanReversionStrategy, MomentumStrategy


def print_banner():
    """打印横幅"""
    print("🚀 Lighter量化交易程序 - 测试网版本")
    print("=" * 60)
    print("⚠️  这是测试网环境，请使用测试代币")
    print("=" * 60)


def load_config():
    """加载配置"""
    try:
        config = Config.from_file("config.yaml")
        config.validate()
        print("✅ 配置文件加载成功")
        return config
    except Exception as e:
        print(f"❌ 配置文件加载失败: {e}")
        print("请先运行: python quick_setup.py")
        return None


async def run_strategy(strategy_name, market_id, config):
    """运行指定策略"""
    try:
        # 创建交易引擎
        engine = TradingEngine(config)
        
        # 添加策略
        if strategy_name == "ut_bot":
            strategy = UTBotStrategy(
                config=config,
                market_id=market_id,
                key_value=1.0,
                atr_period=10,
                use_heikin_ashi=False
            )
            print("📊 启动UT Bot策略")
            print("   - 基于ATR追踪止损")
            print("   - 适合趋势跟踪")
            
        elif strategy_name == "mean_reversion":
            strategy = MeanReversionStrategy(
                config=config,
                market_id=market_id,
                lookback_period=20,
                threshold=2.0
            )
            print("📈 启动均值回归策略")
            print("   - 基于价格偏离均值")
            print("   - 适合震荡市场")
            
        elif strategy_name == "momentum":
            strategy = MomentumStrategy(
                config=config,
                market_id=market_id,
                short_period=5,
                long_period=20,
                momentum_threshold=0.02
            )
            print("⚡ 启动动量策略")
            print("   - 基于价格动量")
            print("   - 适合趋势市场")
            
        else:
            print(f"❌ 未知策略: {strategy_name}")
            return False
        
        engine.add_strategy(strategy)
        
        # 显示配置信息
        print(f"\n📋 运行配置:")
        print(f"   - 策略: {strategy_name}")
        print(f"   - 市场ID: {market_id}")
        print(f"   - 数据源: {config.data_sources.get('primary', 'lighter')}")
        print(f"   - 风险控制: 已启用")
        
        # 启动交易引擎
        print(f"\n🚀 启动交易引擎...")
        print("按 Ctrl+C 停止程序")
        print("-" * 60)
        
        await engine.start()
        
    except KeyboardInterrupt:
        print("\n⏹️  收到停止信号，正在安全关闭...")
    except Exception as e:
        print(f"\n❌ 运行错误: {e}")
        return False
    finally:
        if 'engine' in locals():
            await engine.stop()
        print("✅ 程序已安全停止")
    
    return True


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Lighter量化交易程序 - 测试网版本")
    parser.add_argument("--strategy", "-s", type=str, 
                       choices=["ut_bot", "mean_reversion", "momentum"],
                       default="ut_bot", help="要运行的策略")
    parser.add_argument("--market", "-m", type=int, default=0, 
                       help="市场ID")
    parser.add_argument("--test", "-t", action="store_true", 
                       help="运行系统测试")
    
    args = parser.parse_args()
    
    print_banner()
    
    # 运行系统测试
    if args.test:
        print("🧪 运行系统测试...")
        import subprocess
        result = subprocess.run([sys.executable, "test_system.py"], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return 0 if result.returncode == 0 else 1
    
    # 加载配置
    config = load_config()
    if not config:
        return 1
    
    # 显示风险提示
    print("\n⚠️  风险提示:")
    print("   - 这是测试网环境，使用测试代币")
    print("   - 请确保已设置合理的风险参数")
    print("   - 建议先运行回测验证策略")
    print("   - 监控程序运行状态")
    
    confirm = input("\n是否继续? (y/N): ").strip().lower()
    if confirm != 'y':
        print("已取消运行")
        return 0
    
    # 运行策略
    success = await run_strategy(args.strategy, args.market, config)
    
    return 0 if success else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 再见!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 程序错误: {e}")
        sys.exit(1)
