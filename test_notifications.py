#!/usr/bin/env python3
"""
通知功能测试脚本
测试邮件通知功能
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from quant_trading import Config
from quant_trading.notifications import NotificationManager, NotificationType, NotificationLevel


async def test_notification_system():
    """测试通知系统"""
    print("🧪 测试通知系统")
    print("=" * 50)
    
    # 加载配置
    try:
        config = Config.from_file("config.yaml")
        print("✅ 配置加载成功")
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False
    
    # 检查邮件配置
    email_config = config.notifications_config.get("email", {})
    if not email_config.get("enabled", False):
        print("❌ 邮件通知未启用")
        return False
    
    if not email_config.get("username") or not email_config.get("password"):
        print("❌ 邮件配置不完整，请配置用户名和密码")
        return False
    
    if not email_config.get("to_emails"):
        print("❌ 接收邮箱未配置")
        return False
    
    print("✅ 邮件配置检查通过")
    
    # 创建通知管理器
    notification_manager = NotificationManager(config.notifications_config)
    
    # 测试各种通知类型
    tests = [
        {
            "name": "交易执行通知",
            "func": lambda: notification_manager.send_trade_executed(
                symbol="BTC_USDT",
                side="buy",
                quantity=0.1,
                price=50000.0,
                order_id="test_001"
            )
        },
        {
            "name": "止损触发通知",
            "func": lambda: notification_manager.send_stop_loss_triggered(
                symbol="BTC_USDT",
                price=48000.0,
                order_id="test_002"
            )
        },
        {
            "name": "止盈触发通知",
            "func": lambda: notification_manager.send_take_profit_triggered(
                symbol="BTC_USDT",
                price=52000.0,
                order_id="test_003"
            )
        },
        {
            "name": "风险限制通知",
            "func": lambda: notification_manager.send_risk_limit_exceeded(
                risk_type="max_position_size",
                current_value=0.15,
                limit_value=0.10,
                message="仓位大小超出限制"
            )
        },
        {
            "name": "系统错误通知",
            "func": lambda: notification_manager.send_system_error(
                error_message="API连接超时",
                component="data_manager"
            )
        },
        {
            "name": "策略信号通知",
            "func": lambda: notification_manager.send_strategy_signal(
                strategy_name="UT Bot",
                signal="BUY",
                symbol="BTC_USDT",
                confidence=0.85
            )
        },
        {
            "name": "账户警告通知",
            "func": lambda: notification_manager.send_account_alert(
                alert_type="low_balance",
                message="账户余额不足",
                current_balance=100.0,
                min_balance=500.0
            )
        }
    ]
    
    # 执行测试
    success_count = 0
    for test in tests:
        print(f"\n🔍 测试: {test['name']}")
        try:
            result = await test["func"]()
            if result:
                print(f"✅ {test['name']} 测试成功")
                success_count += 1
            else:
                print(f"❌ {test['name']} 测试失败")
        except Exception as e:
            print(f"❌ {test['name']} 测试异常: {e}")
    
    # 测试批量通知
    print(f"\n🔍 测试: 批量通知")
    try:
        notifications = []
        for i in range(3):
            notifications.append({
                "notification_type": NotificationType.TRADE_EXECUTED,
                "level": NotificationLevel.INFO,
                "title": f"批量测试通知 {i+1}",
                "message": f"这是第 {i+1} 个测试通知",
                "data": {"test_id": i+1}
            })
        
        result = await notification_manager.send_batch_notifications(notifications)
        if result:
            print("✅ 批量通知测试成功")
            success_count += 1
        else:
            print("❌ 批量通知测试失败")
    except Exception as e:
        print(f"❌ 批量通知测试异常: {e}")
    
    # 关闭通知管理器
    await notification_manager.close()
    
    # 打印测试结果
    print(f"\n{'='*50}")
    print(f"测试完成: {success_count}/{len(tests)+1} 成功")
    
    if success_count == len(tests) + 1:
        print("🎉 所有通知测试通过！")
        return True
    else:
        print("⚠️  部分通知测试失败，请检查配置")
        return False


async def test_email_configuration():
    """测试邮件配置"""
    print("\n📧 测试邮件配置")
    print("-" * 30)
    
    # 获取用户输入
    smtp_server = input("SMTP服务器 (默认: smtp.gmail.com): ").strip() or "smtp.gmail.com"
    smtp_port = input("SMTP端口 (默认: 587): ").strip() or "587"
    username = input("邮箱用户名: ").strip()
    password = input("邮箱密码或应用密码: ").strip()
    from_email = input("发送者邮箱: ").strip() or username
    to_email = input("接收者邮箱: ").strip()
    
    if not username or not password or not to_email:
        print("❌ 必要信息不完整")
        return False
    
    # 创建测试配置
    test_config = {
        "enabled": True,
        "batch_size": 1,
        "batch_interval": 1,
        "email": {
            "enabled": True,
            "smtp_server": smtp_server,
            "smtp_port": int(smtp_port),
            "username": username,
            "password": password,
            "from_email": from_email,
            "to_emails": [to_email],
            "min_level": "info"
        }
    }
    
    # 创建通知管理器
    notification_manager = NotificationManager(test_config)
    
    # 发送测试邮件
    try:
        result = await notification_manager.send_notification(
            notification_type=NotificationType.SYSTEM_ERROR,
            level=NotificationLevel.INFO,
            title="邮件配置测试",
            message="这是一封测试邮件，如果您收到此邮件，说明配置正确。",
            data={"test": True, "timestamp": "now"}
        )
        
        if result:
            print("✅ 测试邮件发送成功，请检查您的邮箱")
            return True
        else:
            print("❌ 测试邮件发送失败")
            return False
            
    except Exception as e:
        print(f"❌ 邮件发送异常: {e}")
        return False
    finally:
        await notification_manager.close()


async def main():
    """主函数"""
    print("🚀 通知功能测试")
    print("=" * 60)
    
    # 选择测试模式
    print("请选择测试模式:")
    print("1. 使用配置文件测试")
    print("2. 交互式配置测试")
    
    choice = input("请输入选择 (1/2): ").strip()
    
    if choice == "1":
        success = await test_notification_system()
    elif choice == "2":
        success = await test_email_configuration()
    else:
        print("❌ 无效选择")
        return 1
    
    if success:
        print("\n🎉 通知功能测试完成！")
        print("\n下一步:")
        print("1. 在 config.yaml 中配置您的邮箱信息")
        print("2. 运行交易程序测试通知功能")
        print("3. 监控邮箱接收通知")
    else:
        print("\n❌ 通知功能测试失败，请检查配置")
    
    return 0 if success else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 测试过程中发生错误: {e}")
        sys.exit(1)
