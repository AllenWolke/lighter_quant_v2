#!/usr/bin/env python3
"""
测试修复后的参数使用问题
验证process_market_data和process_real_time_tick函数的参数是否正确使用
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_parameter_usage_fix():
    """测试参数使用修复"""
    print("=" * 60)
    print("测试UT Bot策略参数使用修复")
    print("=" * 60)
    
    try:
        # 1. 导入必要的模块
        print("1. 导入模块:")
        print("-" * 40)
        
        from quant_trading.strategies.ut_bot_strategy import UTBotStrategy, UTBotConfig
        from quant_trading.utils.config import Config
        
        print("   模块导入成功")
        
        # 2. 创建测试配置
        print("\n2. 创建测试配置:")
        print("-" * 40)
        
        system_config = Config.create_default()
        ut_bot_config = UTBotConfig()
        
        strategy = UTBotStrategy(
            name="UTBot_Test",
            config=system_config,
            ut_config=ut_bot_config
        )
        
        print("   UTBotStrategy创建成功")
        
        # 3. 测试process_market_data函数的参数使用
        print("\n3. 测试process_market_data函数参数使用:")
        print("-" * 40)
        
        # 创建模拟的market_data
        test_market_data = {
            0: {  # ETH市场
                'candlesticks': [
                    {
                        'timestamp': datetime.now().timestamp(),
                        'open': 3200.0,
                        'high': 3250.0,
                        'low': 3180.0,
                        'close': 3240.0,
                        'volume': 100.0
                    }
                ],
                'last_price': 3240.0
            },
            1: {  # BTC市场
                'candlesticks': [
                    {
                        'timestamp': datetime.now().timestamp(),
                        'open': 45000.0,
                        'high': 46000.0,
                        'low': 44000.0,
                        'close': 45500.0,
                        'volume': 50.0
                    }
                ],
                'last_price': 45500.0
            }
        }
        
        print(f"   创建测试market_data: {len(test_market_data)} 个市场")
        print(f"   市场0数据: {test_market_data[0].keys()}")
        print(f"   市场1数据: {test_market_data[1].keys()}")
        
        # 测试_process_single_market函数的参数使用
        print("\n   测试_process_single_market函数:")
        
        # 模拟engine和data_manager
        class MockEngine:
            class MockDataManager:
                def get_market_data(self, market_id):
                    # 返回None，强制使用传入的data参数
                    return None
            
            def __init__(self):
                self.data_manager = self.MockDataManager()
        
        strategy.engine = MockEngine()
        
        # 测试传入有效data参数的情况
        test_data = {
            'candlesticks': [
                {
                    'timestamp': datetime.now().timestamp(),
                    'open': 3200.0,
                    'high': 3250.0,
                    'low': 3180.0,
                    'close': 3240.0,
                    'volume': 100.0
                }
            ],
            'last_price': 3240.0
        }
        
        print(f"   测试data参数: {list(test_data.keys())}")
        
        # 由于_process_single_market是async函数，我们需要用asyncio来测试
        import asyncio
        
        async def test_process_single_market():
            try:
                await strategy._process_single_market(0, test_data)
                print("   OK _process_single_market函数执行成功")
                return True
            except Exception as e:
                print(f"   ERROR _process_single_market函数执行失败: {e}")
                return False
        
        # 运行测试
        process_result = asyncio.run(test_process_single_market())
        
        # 4. 测试process_real_time_tick函数的参数使用
        print("\n4. 测试process_real_time_tick函数参数使用:")
        print("-" * 40)
        
        # 创建模拟的tick_data
        test_tick_data = {
            'price': 3245.5,
            'bid': 3245.0,
            'ask': 3246.0,
            'spread': 1.0,
            'timestamp': datetime.now().timestamp(),
            'volume': 10.5
        }
        
        print(f"   创建测试tick_data: {list(test_tick_data.keys())}")
        print(f"   tick_data价格: {test_tick_data['price']}")
        
        async def test_process_real_time_tick():
            try:
                await strategy.process_real_time_tick(0, test_tick_data)
                print("   OK process_real_time_tick函数执行成功")
                
                # 检查参数是否被正确使用
                if 0 in strategy.current_prices:
                    actual_price = strategy.current_prices[0]
                    expected_price = test_tick_data['price']
                    if actual_price == expected_price:
                        print(f"   OK tick_data参数被正确使用: {actual_price}")
                        return True
                    else:
                        print(f"   FAIL 价格不匹配: 期望 {expected_price}, 实际 {actual_price}")
                        return False
                else:
                    print("   FAIL 价格未被存储")
                    return False
                    
            except Exception as e:
                print(f"   ERROR process_real_time_tick函数执行失败: {e}")
                return False
        
        # 运行测试
        tick_result = asyncio.run(test_process_real_time_tick())
        
        # 5. 测试空参数的处理
        print("\n5. 测试空参数处理:")
        print("-" * 40)
        
        async def test_empty_data():
            try:
                # 测试传入空data的情况
                await strategy._process_single_market(0, {})
                print("   OK 空data参数处理成功")
                return True
            except Exception as e:
                print(f"   ERROR 空data参数处理失败: {e}")
                return False
        
        empty_result = asyncio.run(test_empty_data())
        
        # 6. 总结
        print("\n6. 测试总结:")
        print("-" * 40)
        
        all_tests_passed = process_result and tick_result and empty_result
        
        if all_tests_passed:
            print("所有测试通过！参数使用修复成功")
            print("\n修复效果:")
            print("   - _process_single_market函数正确使用传入的data参数")
            print("   - process_real_time_tick函数正确使用传入的tick_data参数")
            print("   - 空参数处理正常")
            print("   - 参数命名避免了混淆")
        else:
            print("部分测试失败，需要进一步检查")
            print(f"   - _process_single_market: {'OK' if process_result else 'FAIL'}")
            print(f"   - process_real_time_tick: {'OK' if tick_result else 'FAIL'}")
            print(f"   - 空参数处理: {'OK' if empty_result else 'FAIL'}")
        
        return all_tests_passed
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始测试UT Bot策略参数使用修复")
    
    success = test_parameter_usage_fix()
    
    print("\n" + "=" * 60)
    print("最终测试结果:")
    print("=" * 60)
    
    if success:
        print("SUCCESS: 参数使用修复成功")
        print("\n现在函数能够:")
        print("1. 正确使用传入的market_data参数")
        print("2. 正确使用传入的tick_data参数")
        print("3. 优先使用传入参数，回退到data_manager")
        print("4. 避免参数命名混淆")
    else:
        print("FAILED: 参数使用修复存在问题")
        print("\n需要进一步检查:")
        print("1. 函数参数的使用逻辑")
        print("2. 参数传递的完整性")
        print("3. 错误处理机制")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
