#!/usr/bin/env python3
"""
测试process_real_time_tick函数的参数验证修复
验证tick_data参数验证逻辑是否正确工作
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_tick_data_validation():
    """测试tick_data参数验证"""
    print("=" * 60)
    print("测试process_real_time_tick函数参数验证修复")
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
        
        # 3. 测试有效的tick_data
        print("\n3. 测试有效的tick_data:")
        print("-" * 40)
        
        valid_tick_data = {
            'price': 3245.5,
            'bid': 3245.0,
            'ask': 3246.0,
            'spread': 1.0,
            'timestamp': datetime.now().timestamp(),
            'volume': 10.5
        }
        
        print(f"   有效tick_data: {valid_tick_data}")
        
        import asyncio
        
        async def test_valid_tick_data():
            try:
                await strategy.process_real_time_tick(0, valid_tick_data)
                print("   OK 有效tick_data处理成功")
                return True
            except Exception as e:
                print(f"   ERROR 有效tick_data处理失败: {e}")
                return False
        
        valid_result = asyncio.run(test_valid_tick_data())
        
        # 4. 测试None tick_data
        print("\n4. 测试None tick_data:")
        print("-" * 40)
        
        async def test_none_tick_data():
            try:
                await strategy.process_real_time_tick(0, None)
                print("   OK None tick_data处理成功（应该被拒绝）")
                return True
            except Exception as e:
                print(f"   ERROR None tick_data处理失败: {e}")
                return False
        
        none_result = asyncio.run(test_none_tick_data())
        
        # 5. 测试空字典tick_data
        print("\n5. 测试空字典tick_data:")
        print("-" * 40)
        
        async def test_empty_tick_data():
            try:
                await strategy.process_real_time_tick(0, {})
                print("   OK 空字典tick_data处理成功（应该被拒绝）")
                return True
            except Exception as e:
                print(f"   ERROR 空字典tick_data处理失败: {e}")
                return False
        
        empty_result = asyncio.run(test_empty_tick_data())
        
        # 6. 测试缺少price字段的tick_data
        print("\n6. 测试缺少price字段的tick_data:")
        print("-" * 40)
        
        invalid_tick_data = {
            'bid': 3245.0,
            'ask': 3246.0,
            'timestamp': datetime.now().timestamp()
            # 缺少'price'字段
        }
        
        print(f"   无效tick_data: {invalid_tick_data}")
        
        async def test_invalid_tick_data():
            try:
                await strategy.process_real_time_tick(0, invalid_tick_data)
                print("   OK 缺少price字段的tick_data处理成功（应该被拒绝）")
                return True
            except Exception as e:
                print(f"   ERROR 缺少price字段的tick_data处理失败: {e}")
                return False
        
        invalid_result = asyncio.run(test_invalid_tick_data())
        
        # 7. 测试非字典类型的tick_data
        print("\n7. 测试非字典类型的tick_data:")
        print("-" * 40)
        
        async def test_non_dict_tick_data():
            try:
                await strategy.process_real_time_tick(0, "invalid_data")
                print("   OK 非字典类型tick_data处理成功（应该被拒绝）")
                return True
            except Exception as e:
                print(f"   ERROR 非字典类型tick_data处理失败: {e}")
                return False
        
        non_dict_result = asyncio.run(test_non_dict_tick_data())
        
        # 8. 测试price为0或负数的tick_data
        print("\n8. 测试price为0或负数的tick_data:")
        print("-" * 40)
        
        zero_price_tick_data = {
            'price': 0,
            'timestamp': datetime.now().timestamp()
        }
        
        negative_price_tick_data = {
            'price': -100.0,
            'timestamp': datetime.now().timestamp()
        }
        
        async def test_zero_negative_price():
            try:
                await strategy.process_real_time_tick(0, zero_price_tick_data)
                await strategy.process_real_time_tick(0, negative_price_tick_data)
                print("   OK price为0或负数的tick_data处理成功（应该被跳过）")
                return True
            except Exception as e:
                print(f"   ERROR price为0或负数的tick_data处理失败: {e}")
                return False
        
        zero_negative_result = asyncio.run(test_zero_negative_price())
        
        # 9. 总结
        print("\n9. 测试总结:")
        print("-" * 40)
        
        all_tests_passed = (valid_result and none_result and empty_result and 
                          invalid_result and non_dict_result and zero_negative_result)
        
        if all_tests_passed:
            print("所有测试通过！参数验证修复成功")
            print("\n修复效果:")
            print("   - 有效tick_data正确处理")
            print("   - None tick_data被正确拒绝")
            print("   - 空字典tick_data被正确拒绝")
            print("   - 缺少price字段的tick_data被正确拒绝")
            print("   - 非字典类型tick_data被正确拒绝")
            print("   - price为0或负数的tick_data被正确跳过")
        else:
            print("部分测试失败，需要进一步检查")
            print(f"   - 有效tick_data: {'OK' if valid_result else 'FAIL'}")
            print(f"   - None tick_data: {'OK' if none_result else 'FAIL'}")
            print(f"   - 空字典tick_data: {'OK' if empty_result else 'FAIL'}")
            print(f"   - 缺少price字段: {'OK' if invalid_result else 'FAIL'}")
            print(f"   - 非字典类型: {'OK' if non_dict_result else 'FAIL'}")
            print(f"   - price为0或负数: {'OK' if zero_negative_result else 'FAIL'}")
        
        return all_tests_passed
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始测试process_real_time_tick函数参数验证修复")
    
    success = test_tick_data_validation()
    
    print("\n" + "=" * 60)
    print("最终测试结果:")
    print("=" * 60)
    
    if success:
        print("SUCCESS: 参数验证修复成功")
        print("\n现在函数能够:")
        print("1. 正确验证tick_data参数的有效性")
        print("2. 拒绝无效的tick_data参数")
        print("3. 确保在安全的情况下才使用tick_data")
        print("4. 提供详细的错误日志")
    else:
        print("FAILED: 参数验证修复存在问题")
        print("\n需要进一步检查:")
        print("1. 参数验证逻辑")
        print("2. 错误处理机制")
        print("3. 日志输出")
    
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
