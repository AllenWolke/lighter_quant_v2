#!/usr/bin/env python3
"""
通知功能示例
演示如何使用通知功能
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from quant_trading import Config
from quant_trading.notifications import NotificationManager, NotificationType, NotificationLevel


async def basic_notification_example():
    """基础通知示例"""
    print("📧 基础通知示例")
    print("=" * 40)
    
    # 加载配置
    config = Config.from_file("config.yaml")
    
    # 创建通知管理器
    notification_manager = NotificationManager(config.notifications_config)
    
    # 发送简单通知
    await notification_manager.send_notification(
        notification_type=NotificationType.SYSTEM_ERROR,
        level=NotificationLevel.INFO,
        title="系统启动",
        message="量化交易系统已成功启动",
        data={"version": "1.0.0", "timestamp": "2024-01-01 12:00:00"}
    )
    
    print("✅ 基础通知发送完成")
    
    # 关闭通知管理器
    await notification_manager.close()


async def trading_notification_example():
    """交易通知示例"""
    print("\n💰 交易通知示例")
    print("=" * 40)
    
    # 加载配置
    config = Config.from_file("config.yaml")
    
    # 创建通知管理器
    notification_manager = NotificationManager(config.notifications_config)
    
    # 模拟交易场景
    scenarios = [
        {
            "name": "买入订单",
            "func": lambda: notification_manager.send_trade_executed(
                symbol="BTC_USDT",
                side="buy",
                quantity=0.1,
                price=50000.0,
                order_id="BTC_001",
                strategy="UT Bot"
            )
        },
        {
            "name": "卖出订单",
            "func": lambda: notification_manager.send_trade_executed(
                symbol="ETH_USDT",
                side="sell",
                quantity=1.0,
                price=3000.0,
                order_id="ETH_001",
                strategy="Mean Reversion"
            )
        },
        {
            "name": "止损触发",
            "func": lambda: notification_manager.send_stop_loss_triggered(
                symbol="BTC_USDT",
                price=48000.0,
                order_id="BTC_001",
                loss_amount=200.0
            )
        },
        {
            "name": "止盈触发",
            "func": lambda: notification_manager.send_take_profit_triggered(
                symbol="ETH_USDT",
                price=3200.0,
                order_id="ETH_001",
                profit_amount=200.0
            )
        }
    ]
    
    # 发送交易通知
    for scenario in scenarios:
        print(f"发送 {scenario['name']} 通知...")
        await scenario["func"]()
        await asyncio.sleep(1)  # 避免发送过快
    
    print("✅ 交易通知发送完成")
    
    # 关闭通知管理器
    await notification_manager.close()


async def risk_notification_example():
    """风险通知示例"""
    print("\n⚠️ 风险通知示例")
    print("=" * 40)
    
    # 加载配置
    config = Config.from_file("config.yaml")
    
    # 创建通知管理器
    notification_manager = NotificationManager(config.notifications_config)
    
    # 模拟风险场景
    risk_scenarios = [
        {
            "name": "仓位过大",
            "func": lambda: notification_manager.send_risk_limit_exceeded(
                risk_type="max_position_size",
                current_value=0.15,
                limit_value=0.10,
                message="当前仓位15%超过限制10%"
            )
        },
        {
            "name": "日亏损过大",
            "func": lambda: notification_manager.send_risk_limit_exceeded(
                risk_type="max_daily_loss",
                current_value=0.05,
                limit_value=0.02,
                message="今日亏损5%超过限制2%"
            )
        },
        {
            "name": "回撤过大",
            "func": lambda: notification_manager.send_risk_limit_exceeded(
                risk_type="max_drawdown",
                current_value=0.12,
                limit_value=0.10,
                message="当前回撤12%超过限制10%"
            )
        }
    ]
    
    # 发送风险通知
    for scenario in risk_scenarios:
        print(f"发送 {scenario['name']} 通知...")
        await scenario["func"]()
        await asyncio.sleep(1)
    
    print("✅ 风险通知发送完成")
    
    # 关闭通知管理器
    await notification_manager.close()


async def strategy_notification_example():
    """策略通知示例"""
    print("\n📊 策略通知示例")
    print("=" * 40)
    
    # 加载配置
    config = Config.from_file("config.yaml")
    
    # 创建通知管理器
    notification_manager = NotificationManager(config.notifications_config)
    
    # 模拟策略场景
    strategy_scenarios = [
        {
            "name": "UT Bot买入信号",
            "func": lambda: notification_manager.send_strategy_signal(
                strategy_name="UT Bot",
                signal="BUY",
                symbol="BTC_USDT",
                confidence=0.85,
                price=50000.0,
                reason="价格突破ATR追踪止损线"
            )
        },
        {
            "name": "均值回归卖出信号",
            "func": lambda: notification_manager.send_strategy_signal(
                strategy_name="Mean Reversion",
                signal="SELL",
                symbol="ETH_USDT",
                confidence=0.75,
                price=3100.0,
                reason="价格偏离均值超过阈值"
            )
        },
        {
            "name": "动量策略平仓信号",
            "func": lambda: notification_manager.send_strategy_signal(
                strategy_name="Momentum",
                signal="CLOSE",
                symbol="BTC_USDT",
                confidence=0.90,
                price=52000.0,
                reason="动量指标反转"
            )
        }
    ]
    
    # 发送策略通知
    for scenario in strategy_scenarios:
        print(f"发送 {scenario['name']} 通知...")
        await scenario["func"]()
        await asyncio.sleep(1)
    
    print("✅ 策略通知发送完成")
    
    # 关闭通知管理器
    await notification_manager.close()


async def batch_notification_example():
    """批量通知示例"""
    print("\n📦 批量通知示例")
    print("=" * 40)
    
    # 加载配置
    config = Config.from_file("config.yaml")
    
    # 创建通知管理器
    notification_manager = NotificationManager(config.notifications_config)
    
    # 创建批量通知
    notifications = []
    
    # 添加多个通知
    for i in range(5):
        notifications.append({
            "notification_type": NotificationType.TRADE_EXECUTED,
            "level": NotificationLevel.INFO,
            "title": f"批量交易通知 {i+1}",
            "message": f"这是第 {i+1} 个批量交易通知",
            "data": {
                "symbol": f"TOKEN_{i+1}",
                "side": "buy" if i % 2 == 0 else "sell",
                "quantity": 0.1 * (i + 1),
                "price": 1000.0 + i * 100
            }
        })
    
    # 发送批量通知
    print("发送批量通知...")
    result = await notification_manager.send_batch_notifications(notifications)
    
    if result:
        print("✅ 批量通知发送成功")
    else:
        print("❌ 批量通知发送失败")
    
    # 关闭通知管理器
    await notification_manager.close()


async def main():
    """主函数"""
    print("🚀 通知功能示例")
    print("=" * 60)
    
    # 检查配置
    try:
        config = Config.from_file("config.yaml")
        if not config.notifications_config.get("email", {}).get("enabled", False):
            print("❌ 邮件通知未启用，请先配置邮件设置")
            return 1
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return 1
    
    # 运行示例
    examples = [
        ("基础通知", basic_notification_example),
        ("交易通知", trading_notification_example),
        ("风险通知", risk_notification_example),
        ("策略通知", strategy_notification_example),
        ("批量通知", batch_notification_example)
    ]
    
    for name, example_func in examples:
        try:
            print(f"\n{'='*60}")
            print(f"运行示例: {name}")
            print('='*60)
            await example_func()
            print(f"✅ {name} 示例完成")
        except Exception as e:
            print(f"❌ {name} 示例失败: {e}")
    
    print(f"\n{'='*60}")
    print("🎉 所有通知示例运行完成！")
    print("\n请检查您的邮箱查看通知邮件。")
    print("\n配置说明:")
    print("1. 在 config.yaml 中配置邮件设置")
    print("2. 设置接收邮箱地址")
    print("3. 配置SMTP服务器信息")
    print("4. 运行交易程序自动发送通知")
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  示例被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 示例运行错误: {e}")
        sys.exit(1)
