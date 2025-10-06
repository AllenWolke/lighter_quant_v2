#!/usr/bin/env python3
"""
Lighter量化交易程序启动脚本
提供交互式配置和启动功能
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from quant_trading import TradingEngine, Config
from quant_trading.strategies import MeanReversionStrategy, MomentumStrategy, ArbitrageStrategy


def print_banner():
    """打印程序横幅"""
    print("=" * 60)
    print("🚀 Lighter量化交易程序")
    print("=" * 60)
    print()


def get_user_config():
    """获取用户配置"""
    print("请配置Lighter交易所参数:")
    print()
    
    # 选择网络
    print("1. 选择网络:")
    print("   1) 测试网 (testnet.zklighter.elliot.ai)")
    print("   2) 主网 (mainnet.zklighter.elliot.ai)")
    
    while True:
        choice = input("请选择 (1-2): ").strip()
        if choice == "1":
            base_url = "https://testnet.zklighter.elliot.ai"
            break
        elif choice == "2":
            base_url = "https://mainnet.zklighter.elliot.ai"
            break
        else:
            print("无效选择，请重新输入")
    
    print()
    
    # 获取API参数
    api_key_private_key = input("请输入API密钥私钥: ").strip()
    if not api_key_private_key:
        print("❌ API密钥私钥不能为空")
        return None
        
    try:
        account_index = int(input("请输入账户索引: ").strip())
    except ValueError:
        print("❌ 账户索引必须是数字")
        return None
        
    try:
        api_key_index = int(input("请输入API密钥索引: ").strip())
    except ValueError:
        print("❌ API密钥索引必须是数字")
        return None
    
    print()
    
    # 选择策略
    print("2. 选择交易策略:")
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
    
    # 选择市场
    try:
        market_id = int(input("请输入市场ID (默认0): ").strip() or "0")
    except ValueError:
        market_id = 0
    
    print()
    
    # 风险确认
    print("3. 风险提示:")
    print("   ⚠️  量化交易存在风险，可能导致资金损失")
    print("   ⚠️  请确保您了解相关风险并谨慎操作")
    print("   ⚠️  建议先在测试网环境测试")
    print()
    
    confirm = input("是否确认继续? (y/N): ").strip().lower()
    if confirm != 'y':
        print("已取消启动")
        return None
    
    return {
        "base_url": base_url,
        "api_key_private_key": api_key_private_key,
        "account_index": account_index,
        "api_key_index": api_key_index,
        "strategy_choice": strategy_choice,
        "market_id": market_id
    }


def create_config(user_config):
    """创建配置对象"""
    config = Config.create_default()
    
    # 更新Lighter配置
    config.lighter_config.update({
        "base_url": user_config["base_url"],
        "api_key_private_key": user_config["api_key_private_key"],
        "account_index": user_config["account_index"],
        "api_key_index": user_config["api_key_index"]
    })
    
    # 调整风险参数（保守设置）
    config.risk_config.update({
        "max_position_size": 0.05,  # 最大仓位5%
        "max_daily_loss": 0.02,     # 最大日亏损2%
        "max_drawdown": 0.10,       # 最大回撤10%
        "max_orders_per_minute": 5, # 每分钟最大订单数
        "max_open_orders": 10,      # 最大开仓订单数
    })
    
    return config


async def start_trading_engine(config, user_config):
    """启动交易引擎"""
    try:
        # 创建交易引擎
        engine = TradingEngine(config)
        
        # 添加策略
        strategy_choice = user_config["strategy_choice"]
        market_id = user_config["market_id"]
        
        if strategy_choice in ["1", "4"]:  # 均值回归或所有策略
            mean_reversion = MeanReversionStrategy(
                config=config,
                market_id=market_id,
                lookback_period=20,
                threshold=2.0
            )
            engine.add_strategy(mean_reversion)
            print("✅ 已添加均值回归策略")
        
        if strategy_choice in ["2", "4"]:  # 动量或所有策略
            momentum = MomentumStrategy(
                config=config,
                market_id=market_id,
                short_period=5,
                long_period=20,
                momentum_threshold=0.02
            )
            engine.add_strategy(momentum)
            print("✅ 已添加动量策略")
        
        if strategy_choice in ["3", "4"]:  # 套利或所有策略
            arbitrage = ArbitrageStrategy(
                config=config,
                market_id_1=market_id,
                market_id_2=market_id + 1,
                price_threshold=0.01
            )
            engine.add_strategy(arbitrage)
            print("✅ 已添加套利策略")
        
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
        raise
    finally:
        if 'engine' in locals():
            await engine.stop()
        print("✅ 交易引擎已停止")


async def main():
    """主函数"""
    print_banner()
    
    # 获取用户配置
    user_config = get_user_config()
    if not user_config:
        return 1
    
    # 创建配置
    config = create_config(user_config)
    
    # 保存配置到文件
    config.save_to_file("user_config.yaml")
    print("✅ 配置已保存到 user_config.yaml")
    print()
    
    # 启动交易引擎
    await start_trading_engine(config, user_config)
    
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
