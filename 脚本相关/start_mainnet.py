#!/usr/bin/env python3
"""
主网安全启动脚本
包含多重安全检查和风险控制
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from quant_trading import TradingEngine, Config
from quant_trading.strategies import UTBotStrategy


def print_banner():
    """打印横幅"""
    print("🚀 Lighter量化交易程序 - 主网版本")
    print("=" * 60)
    print("⚠️  警告：这是主网环境，涉及真实资金！")
    print("⚠️  请确保您已充分测试并理解相关风险！")
    print("=" * 60)


def safety_checks():
    """执行安全检查"""
    print("🔒 执行安全检查...")
    
    # 检查配置文件
    if not os.path.exists("config_mainnet.yaml"):
        print("❌ 主网配置文件不存在")
        print("   请先创建 config_mainnet.yaml 文件")
        return False
    
    # 加载配置
    try:
        config = Config.from_file("config_mainnet.yaml")
        config.validate()
        print("✅ 配置文件验证通过")
    except Exception as e:
        print(f"❌ 配置文件验证失败: {e}")
        return False
    
    # 检查API密钥
    if not config.lighter_config.get("api_key_private_key"):
        print("❌ API密钥未配置")
        print("   请在 config_mainnet.yaml 中配置 api_key_private_key")
        return False
    
    # 检查是否为测试网
    if "testnet" in config.lighter_config.get("base_url", ""):
        print("❌ 检测到测试网配置，主网部署被阻止")
        print("   请将 base_url 改为 https://mainnet.zklighter.elliot.ai")
        return False
    
    # 检查风险参数
    risk_config = config.risk_config
    warnings = []
    
    if risk_config.get("max_position_size", 0) > 0.05:
        warnings.append("最大仓位超过5%")
    
    if risk_config.get("max_daily_loss", 0) > 0.02:
        warnings.append("最大日亏损超过2%")
    
    if risk_config.get("max_drawdown", 0) > 0.1:
        warnings.append("最大回撤超过10%")
    
    if risk_config.get("max_leverage", 0) > 10:
        warnings.append("最大杠杆超过10倍")
    
    if warnings:
        print("⚠️  风险参数警告:")
        for warning in warnings:
            print(f"   - {warning}")
        
        confirm = input("\n是否继续? (y/N): ").strip().lower()
        if confirm != 'y':
            print("已取消启动")
            return False
    
    print("✅ 安全检查通过")
    return True


def final_confirmation():
    """最终确认"""
    print("\n" + "="*60)
    print("⚠️  最终确认：")
    print("   - 这是主网环境，将使用真实资金进行交易")
    print("   - 请确保您已充分测试策略")
    print("   - 请确保您已设置合理的风险控制参数")
    print("   - 请确保您已准备好承受可能的资金损失")
    print("   - 建议从小资金开始，逐步增加")
    print("="*60)
    
    print("\n请输入 'MAINNET' 确认继续:")
    confirm = input("确认: ").strip()
    
    if confirm != 'MAINNET':
        print("确认失败，程序退出")
        return False
    
    return True


async def run_mainnet_trading():
    """运行主网交易"""
    try:
        # 加载配置
        config = Config.from_file("config_mainnet.yaml")
        
        # 创建交易引擎
        engine = TradingEngine(config)
        
        # 只添加UT Bot策略（主网保守策略）
        ut_bot = UTBotStrategy(
            config=config,
            market_id=0,
            key_value=0.8,      # 降低敏感度
            atr_period=14,      # 增加稳定性
            use_heikin_ashi=False
        )
        engine.add_strategy(ut_bot)
        
        print(f"\n📊 策略配置:")
        print(f"   - 策略: UT Bot")
        print(f"   - 市场ID: 0")
        print(f"   - 关键值: 0.8")
        print(f"   - ATR周期: 14")
        print(f"   - 仓位大小: {config.risk_config['max_position_size']*100:.1f}%")
        
        print(f"\n🛡️ 风险控制:")
        print(f"   - 最大仓位: {config.risk_config['max_position_size']*100:.1f}%")
        print(f"   - 最大日亏损: {config.risk_config['max_daily_loss']*100:.1f}%")
        print(f"   - 最大回撤: {config.risk_config['max_drawdown']*100:.1f}%")
        print(f"   - 最大杠杆: {config.risk_config['max_leverage']:.1f}倍")
        
        print(f"\n🚀 启动主网交易引擎...")
        print(f"   启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   日志文件: logs/mainnet_trading.log")
        print("   按 Ctrl+C 安全停止")
        print("-" * 60)
        
        # 启动交易引擎
        await engine.start()
        
    except KeyboardInterrupt:
        print("\n⏹️  收到停止信号，正在安全关闭...")
        print("   正在平仓所有仓位...")
        print("   正在保存状态...")
    except Exception as e:
        print(f"\n❌ 运行错误: {e}")
        print("   请检查日志文件: logs/mainnet_trading.log")
        return False
    finally:
        if 'engine' in locals():
            await engine.stop()
        print("✅ 程序已安全停止")
        print(f"   停止时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return True


async def main():
    """主函数"""
    print_banner()
    
    # 执行安全检查
    if not safety_checks():
        return 1
    
    # 最终确认
    if not final_confirmation():
        return 0
    
    # 运行主网交易
    success = await run_mainnet_trading()
    
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
