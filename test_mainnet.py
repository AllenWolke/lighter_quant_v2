#!/usr/bin/env python3
"""
主网系统测试脚本
验证主网配置、连接和风险参数
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from quant_trading import Config
import lighter


class MainnetTester:
    """主网测试器"""
    
    def __init__(self):
        self.test_results = {}
        self.config = None
        self.api_client = None
    
    def load_config(self):
        """加载配置"""
        print("🔍 测试配置加载...")
        
        try:
            if not os.path.exists("config_mainnet.yaml"):
                print("❌ 主网配置文件不存在")
                return False
            
            self.config = Config.from_file("config_mainnet.yaml")
            self.config.validate()
            print("✅ 配置文件加载成功")
            return True
        except Exception as e:
            print(f"❌ 配置加载失败: {e}")
            return False
    
    async def test_mainnet_connection(self):
        """测试主网连接"""
        print("🔍 测试主网连接...")
        
        try:
            # 创建API客户端
            self.api_client = lighter.ApiClient(
                configuration=lighter.Configuration(host=self.config.lighter_config["base_url"])
            )
            
            # 测试账户API
            account_api = lighter.AccountApi(self.api_client)
            account = await account_api.account(
                by="index", 
                value=str(self.config.lighter_config["account_index"])
            )
            
            if account:
                print(f"✅ 主网连接成功")
                print(f"   账户索引: {account.account_index}")
                print(f"   地址: {account.l1_address}")
                print(f"   余额: {account.balance}")
                self.test_results["mainnet_connection"] = True
                return True
            else:
                print("❌ 主网连接失败，无法获取账户信息")
                self.test_results["mainnet_connection"] = False
                return False
                
        except Exception as e:
            print(f"❌ 主网连接测试失败: {e}")
            self.test_results["mainnet_connection"] = False
            return False
    
    def test_risk_parameters(self):
        """测试风险参数"""
        print("🔍 测试风险参数...")
        
        try:
            risk_config = self.config.risk_config
            warnings = []
            errors = []
            
            # 检查最大仓位
            max_position = risk_config.get("max_position_size", 0)
            if max_position > 0.05:
                warnings.append(f"最大仓位 {max_position*100:.1f}% 超过建议值 5%")
            elif max_position < 0.01:
                warnings.append(f"最大仓位 {max_position*100:.1f}% 过小，可能影响收益")
            
            # 检查最大日亏损
            max_daily_loss = risk_config.get("max_daily_loss", 0)
            if max_daily_loss > 0.02:
                warnings.append(f"最大日亏损 {max_daily_loss*100:.1f}% 超过建议值 2%")
            elif max_daily_loss < 0.005:
                warnings.append(f"最大日亏损 {max_daily_loss*100:.1f}% 过小，可能过于保守")
            
            # 检查最大回撤
            max_drawdown = risk_config.get("max_drawdown", 0)
            if max_drawdown > 0.1:
                warnings.append(f"最大回撤 {max_drawdown*100:.1f}% 超过建议值 10%")
            elif max_drawdown < 0.02:
                warnings.append(f"最大回撤 {max_drawdown*100:.1f}% 过小，可能过于保守")
            
            # 检查最大杠杆
            max_leverage = risk_config.get("max_leverage", 0)
            if max_leverage > 10:
                warnings.append(f"最大杠杆 {max_leverage:.1f} 超过建议值 10")
            elif max_leverage < 1:
                warnings.append(f"最大杠杆 {max_leverage:.1f} 过低")
            
            # 检查订单限制
            max_orders_per_minute = risk_config.get("max_orders_per_minute", 0)
            if max_orders_per_minute > 10:
                warnings.append(f"每分钟最大订单数 {max_orders_per_minute} 过多")
            
            max_open_orders = risk_config.get("max_open_orders", 0)
            if max_open_orders > 20:
                warnings.append(f"最大开仓订单数 {max_open_orders} 过多")
            
            # 打印结果
            if warnings:
                print("⚠️  风险参数警告:")
                for warning in warnings:
                    print(f"   - {warning}")
            else:
                print("✅ 风险参数检查通过")
            
            if errors:
                print("❌ 风险参数错误:")
                for error in errors:
                    print(f"   - {error}")
                self.test_results["risk_parameters"] = False
                return False
            else:
                self.test_results["risk_parameters"] = True
                return True
                
        except Exception as e:
            print(f"❌ 风险参数测试失败: {e}")
            self.test_results["risk_parameters"] = False
            return False
    
    def test_strategy_config(self):
        """测试策略配置"""
        print("🔍 测试策略配置...")
        
        try:
            strategies_config = self.config.strategies
            enabled_strategies = []
            
            for strategy_name, strategy_config in strategies_config.items():
                if strategy_config.get("enabled", False):
                    enabled_strategies.append(strategy_name)
            
            if not enabled_strategies:
                print("⚠️  没有启用的策略")
                self.test_results["strategy_config"] = False
                return False
            
            print(f"✅ 启用的策略: {', '.join(enabled_strategies)}")
            
            # 检查UT Bot策略配置
            if "ut_bot" in enabled_strategies:
                ut_bot_config = strategies_config["ut_bot"]
                key_value = ut_bot_config.get("key_value", 1.0)
                atr_period = ut_bot_config.get("atr_period", 10)
                position_size = ut_bot_config.get("position_size", 0.1)
                
                print(f"   UT Bot配置:")
                print(f"   - 关键值: {key_value}")
                print(f"   - ATR周期: {atr_period}")
                print(f"   - 仓位大小: {position_size*100:.1f}%")
                
                if key_value > 1.5:
                    print("   ⚠️  关键值过高，可能过于敏感")
                if atr_period < 10:
                    print("   ⚠️  ATR周期过短，可能不够稳定")
                if position_size > 0.05:
                    print("   ⚠️  仓位大小过大，风险较高")
            
            self.test_results["strategy_config"] = True
            return True
            
        except Exception as e:
            print(f"❌ 策略配置测试失败: {e}")
            self.test_results["strategy_config"] = False
            return False
    
    async def test_market_data(self):
        """测试市场数据获取"""
        print("🔍 测试市场数据获取...")
        
        try:
            if not self.api_client:
                print("❌ API客户端未初始化")
                return False
            
            # 测试订单API
            order_api = lighter.OrderApi(self.api_client)
            markets = await order_api.order_books()
            
            if markets and markets.order_books:
                print(f"✅ 市场数据获取成功，发现 {len(markets.order_books)} 个市场")
                
                # 显示前3个市场信息
                for i, market in enumerate(markets.order_books[:3]):
                    print(f"   市场 {i+1}: ID={market.market_id}")
                
                self.test_results["market_data"] = True
                return True
            else:
                print("❌ 市场数据获取失败")
                self.test_results["market_data"] = False
                return False
                
        except Exception as e:
            print(f"❌ 市场数据测试失败: {e}")
            self.test_results["market_data"] = False
            return False
    
    def test_logging_config(self):
        """测试日志配置"""
        print("🔍 测试日志配置...")
        
        try:
            log_config = self.config.log_config
            log_file = log_config.get("file", "logs/mainnet_trading.log")
            
            # 检查日志目录
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
                print(f"✅ 创建日志目录: {log_dir}")
            
            # 检查日志文件权限
            try:
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"# 主网测试日志 - {datetime.now()}\n")
                print(f"✅ 日志文件可写: {log_file}")
            except Exception as e:
                print(f"❌ 日志文件写入失败: {e}")
                return False
            
            self.test_results["logging_config"] = True
            return True
            
        except Exception as e:
            print(f"❌ 日志配置测试失败: {e}")
            self.test_results["logging_config"] = False
            return False
    
    def print_test_summary(self):
        """打印测试总结"""
        print("\n" + "="*60)
        print("主网测试总结")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result is True)
        failed_tests = sum(1 for result in self.test_results.values() if result is False)
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        print()
        
        for test_name, result in self.test_results.items():
            if result is True:
                print(f"✅ {test_name}")
            else:
                print(f"❌ {test_name}")
        
        print()
        if failed_tests == 0:
            print("🎉 所有测试通过！主网系统可以正常运行。")
            print("\n下一步:")
            print("1. 运行: python start_mainnet.py")
            print("2. 监控: python monitor_mainnet.py")
        else:
            print("❌ 部分测试失败，请修复问题后再运行主网程序。")
        
        return failed_tests == 0
    
    async def cleanup(self):
        """清理资源"""
        if self.api_client:
            await self.api_client.close()


async def main():
    """主函数"""
    print("🧪 Lighter量化交易系统 - 主网测试")
    print("=" * 60)
    print("⚠️  这是主网测试，请确保配置正确！")
    print("=" * 60)
    
    tester = MainnetTester()
    
    # 运行测试
    tests = [
        ("配置加载", tester.load_config),
        ("主网连接", tester.test_mainnet_connection),
        ("风险参数", tester.test_risk_parameters),
        ("策略配置", tester.test_strategy_config),
        ("市场数据", tester.test_market_data),
        ("日志配置", tester.test_logging_config),
    ]
    
    for test_name, test_func in tests:
        print(f"\n🔍 测试: {test_name}")
        print("-" * 40)
        try:
            if asyncio.iscoroutinefunction(test_func):
                await test_func()
            else:
                test_func()
        except Exception as e:
            print(f"❌ 测试 {test_name} 发生异常: {e}")
            tester.test_results[test_name.lower().replace(" ", "_")] = False
    
    # 打印总结
    success = tester.print_test_summary()
    
    # 清理资源
    await tester.cleanup()
    
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
