#!/usr/bin/env python3
"""
系统测试脚本
验证量化交易系统的各个组件
"""

import asyncio
import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from quant_trading import Config, TradingEngine
from quant_trading.strategies import UTBotStrategy, MeanReversionStrategy
from quant_trading.data_sources import LighterDataSource, TradingViewDataSource


class SystemTester:
    """系统测试器"""
    
    def __init__(self):
        self.test_results = {}
        self.config = None
        
    def load_config(self):
        """加载配置"""
        try:
            self.config = Config.from_file("config.yaml")
            self.config.validate()
            self.test_results["config"] = True
            print("✅ 配置加载成功")
            return True
        except Exception as e:
            self.test_results["config"] = False
            print(f"❌ 配置加载失败: {e}")
            return False
    
    async def test_lighter_connection(self):
        """测试Lighter连接"""
        try:
            import lighter
            
            # 创建API客户端
            api_client = lighter.ApiClient(
                configuration=lighter.Configuration(host=self.config.lighter_config["base_url"])
            )
            
            # 测试账户API
            account_api = lighter.AccountApi(api_client)
            account = await account_api.account(
                by="index", 
                value=str(self.config.lighter_config["account_index"])
            )
            
            if account:
                print(f"✅ Lighter连接成功，账户索引: {account.account_index}")
                self.test_results["lighter_connection"] = True
            else:
                print("❌ Lighter连接失败，无法获取账户信息")
                self.test_results["lighter_connection"] = False
                
            await api_client.close()
            return self.test_results["lighter_connection"]
            
        except Exception as e:
            print(f"❌ Lighter连接测试失败: {e}")
            self.test_results["lighter_connection"] = False
            return False
    
    async def test_data_sources(self):
        """测试数据源"""
        try:
            # 测试Lighter数据源
            import lighter
            api_client = lighter.ApiClient(
                configuration=lighter.Configuration(host=self.config.lighter_config["base_url"])
            )
            
            lighter_config = {"api_client": api_client}
            lighter_source = LighterDataSource(lighter_config)
            await lighter_source.initialize()
            
            print("✅ Lighter数据源初始化成功")
            self.test_results["lighter_data_source"] = True
            
            # 测试TradingView数据源
            tv_config = self.config.data_sources.get("tradingview", {})
            if tv_config.get("enabled", False):
                tv_source = TradingViewDataSource(tv_config)
                await tv_source.initialize()
                print("✅ TradingView数据源初始化成功")
                self.test_results["tradingview_data_source"] = True
            else:
                print("ℹ️  TradingView数据源未启用")
                self.test_results["tradingview_data_source"] = None
            
            await api_client.close()
            return True
            
        except Exception as e:
            print(f"❌ 数据源测试失败: {e}")
            self.test_results["data_sources"] = False
            return False
    
    async def test_strategies(self):
        """测试策略"""
        try:
            # 测试UT Bot策略
            ut_bot = UTBotStrategy(
                config=self.config,
                market_id=0,
                key_value=1.0,
                atr_period=10
            )
            await ut_bot.initialize()
            print("✅ UT Bot策略初始化成功")
            self.test_results["ut_bot_strategy"] = True
            
            # 测试均值回归策略
            mean_reversion = MeanReversionStrategy(
                config=self.config,
                market_id=0,
                lookback_period=20,
                threshold=2.0
            )
            await mean_reversion.initialize()
            print("✅ 均值回归策略初始化成功")
            self.test_results["mean_reversion_strategy"] = True
            
            return True
            
        except Exception as e:
            print(f"❌ 策略测试失败: {e}")
            self.test_results["strategies"] = False
            return False
    
    async def test_trading_engine(self):
        """测试交易引擎"""
        try:
            import lighter
            
            # 创建API客户端
            api_client = lighter.ApiClient(
                configuration=lighter.Configuration(host=self.config.lighter_config["base_url"])
            )
            
            # 创建交易引擎
            engine = TradingEngine(self.config)
            
            # 添加策略
            ut_bot = UTBotStrategy(
                config=self.config,
                market_id=0,
                key_value=1.0,
                atr_period=10
            )
            engine.add_strategy(ut_bot)
            
            # 初始化引擎（不启动）
            await engine.initialize()
            print("✅ 交易引擎初始化成功")
            
            # 获取状态
            status = engine.get_status()
            print(f"   策略数量: {status['strategies_count']}")
            print(f"   活跃策略: {status['active_strategies']}")
            
            await engine.stop()
            await api_client.close()
            
            self.test_results["trading_engine"] = True
            return True
            
        except Exception as e:
            print(f"❌ 交易引擎测试失败: {e}")
            self.test_results["trading_engine"] = False
            return False
    
    async def test_market_data(self):
        """测试市场数据获取"""
        try:
            import lighter
            
            # 创建API客户端
            api_client = lighter.ApiClient(
                configuration=lighter.Configuration(host=self.config.lighter_config["base_url"])
            )
            
            # 测试订单API
            order_api = lighter.OrderApi(api_client)
            markets = await order_api.order_books()
            
            if markets and markets.order_books:
                print(f"✅ 市场数据获取成功，发现 {len(markets.order_books)} 个市场")
                for market in markets.order_books[:3]:  # 显示前3个市场
                    print(f"   市场 {market.market_id}: {market}")
                self.test_results["market_data"] = True
            else:
                print("❌ 市场数据获取失败")
                self.test_results["market_data"] = False
            
            await api_client.close()
            return self.test_results["market_data"]
            
        except Exception as e:
            print(f"❌ 市场数据测试失败: {e}")
            self.test_results["market_data"] = False
            return False
    
    def print_test_summary(self):
        """打印测试总结"""
        print("\n" + "="*60)
        print("测试总结")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result is True)
        failed_tests = sum(1 for result in self.test_results.values() if result is False)
        skipped_tests = sum(1 for result in self.test_results.values() if result is None)
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        print(f"跳过: {skipped_tests}")
        print()
        
        for test_name, result in self.test_results.items():
            if result is True:
                print(f"✅ {test_name}")
            elif result is False:
                print(f"❌ {test_name}")
            else:
                print(f"ℹ️  {test_name} (跳过)")
        
        print()
        if failed_tests == 0:
            print("🎉 所有测试通过！系统可以正常运行。")
        else:
            print("⚠️  部分测试失败，请检查配置和网络连接。")
        
        return failed_tests == 0


async def main():
    """主函数"""
    print("🧪 Lighter量化交易系统测试")
    print("="*60)
    
    tester = SystemTester()
    
    # 加载配置
    if not tester.load_config():
        return 1
    
    # 运行测试
    tests = [
        ("Lighter连接", tester.test_lighter_connection),
        ("数据源", tester.test_data_sources),
        ("策略", tester.test_strategies),
        ("交易引擎", tester.test_trading_engine),
        ("市场数据", tester.test_market_data),
    ]
    
    for test_name, test_func in tests:
        print(f"\n🔍 测试: {test_name}")
        print("-" * 40)
        try:
            await test_func()
        except Exception as e:
            print(f"❌ 测试 {test_name} 发生异常: {e}")
            tester.test_results[test_name.lower().replace(" ", "_")] = False
    
    # 打印总结
    success = tester.print_test_summary()
    
    if success:
        print("\n🚀 系统测试完成，可以开始交易！")
        print("\n运行命令:")
        print("python main.py --strategy ut_bot --market 0")
    else:
        print("\n🔧 请修复失败的测试后再运行交易程序。")
    
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
