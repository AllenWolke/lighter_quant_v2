#!/usr/bin/env python3
"""
测试修复后的UT Bot策略配置逻辑
验证UTBotStrategy是否能正确从config.yaml中读取配置
"""

import yaml
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_config_logic_fix():
    """测试修复后的配置逻辑"""
    print("=" * 60)
    print("测试修复后的UT Bot策略配置逻辑")
    print("=" * 60)
    
    try:
        # 1. 读取config.yaml中的配置
        print("1. 读取config.yaml中的UT Bot配置:")
        print("-" * 40)
        
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        strategies = config.get('strategies', {})
        ut_bot_config = strategies.get('ut_bot', {})
        
        print(f"   config.yaml中的atr_period: {ut_bot_config.get('atr_period')}")
        print(f"   config.yaml中的key_value: {ut_bot_config.get('key_value')}")
        print(f"   config.yaml中的ema_length: {ut_bot_config.get('ema_length')}")
        
        # 2. 测试不传递ut_config参数的情况
        print("\n2. 测试不传递ut_config参数的情况:")
        print("-" * 40)
        
        from quant_trading.strategies.ut_bot_strategy import UTBotStrategy
        from quant_trading.utils.config import Config
        
        # 创建系统配置
        system_config = Config.create_default()
        
        # 模拟从config.yaml加载配置
        if hasattr(system_config, 'strategies'):
            system_config.strategies = strategies
        else:
            system_config.strategies = strategies
        
        # 创建UTBotStrategy，不传递ut_config参数
        strategy = UTBotStrategy(
            name="UTBot_Test",
            config=system_config,
            ut_config=None  # 不传递ut_config参数
        )
        
        print("   UTBotStrategy创建成功")
        print(f"   策略中的atr_period: {strategy.ut_config.atr_period}")
        print(f"   策略中的key_value: {strategy.ut_config.key_value}")
        print(f"   策略中的ema_length: {strategy.ut_config.ema_length}")
        
        # 3. 验证配置是否正确加载
        print("\n3. 验证配置是否正确加载:")
        print("-" * 40)
        
        # 检查关键参数
        config_checks = [
            ('atr_period', strategy.ut_config.atr_period, ut_bot_config.get('atr_period')),
            ('key_value', strategy.ut_config.key_value, ut_bot_config.get('key_value')),
            ('ema_length', strategy.ut_config.ema_length, ut_bot_config.get('ema_length')),
            ('risk_per_trade', strategy.ut_config.risk_per_trade, ut_bot_config.get('risk_per_trade')),
            ('atr_multiplier', strategy.ut_config.atr_multiplier, ut_bot_config.get('atr_multiplier')),
        ]
        
        passed = 0
        total = len(config_checks)
        
        for param_name, actual_value, expected_value in config_checks:
            if actual_value == expected_value:
                print(f"   OK {param_name}: {actual_value} (与config.yaml一致)")
                passed += 1
            else:
                print(f"   FAIL {param_name}: 期望 {expected_value}, 实际 {actual_value}")
        
        print(f"\n   配置验证结果: {passed}/{total} 通过")
        
        # 4. 测试传递ut_config参数的情况（确保向后兼容）
        print("\n4. 测试传递ut_config参数的情况:")
        print("-" * 40)
        
        from quant_trading.strategies.ut_bot_strategy import UTBotConfig
        
        # 创建自定义的UTBotConfig
        custom_config = UTBotConfig(
            atr_period=5,
            key_value=2.0,
            ema_length=100
        )
        
        # 创建策略，传递自定义配置
        strategy_with_custom = UTBotStrategy(
            name="UTBot_Custom",
            config=system_config,
            ut_config=custom_config
        )
        
        print(f"   自定义配置的atr_period: {strategy_with_custom.ut_config.atr_period}")
        print(f"   自定义配置的key_value: {strategy_with_custom.ut_config.key_value}")
        print(f"   自定义配置的ema_length: {strategy_with_custom.ut_config.ema_length}")
        
        # 验证自定义配置是否生效
        if (strategy_with_custom.ut_config.atr_period == 5 and
            strategy_with_custom.ut_config.key_value == 2.0 and
            strategy_with_custom.ut_config.ema_length == 100):
            print("   OK 自定义配置正确生效")
            custom_config_ok = True
        else:
            print("   FAIL 自定义配置未生效")
            custom_config_ok = False
        
        # 5. 测试错误的调用方式（如EXECUTION_MANUAL.md中的例子）
        print("\n5. 测试错误的调用方式:")
        print("-" * 40)
        
        try:
            # 模拟错误的调用方式（只传递config参数）
            strategy_wrong = UTBotStrategy(
                name="UTBot_Wrong",
                config=system_config
                # 没有传递ut_config参数
            )
            
            print(f"   错误调用方式的atr_period: {strategy_wrong.ut_config.atr_period}")
            print(f"   错误调用方式的key_value: {strategy_wrong.ut_config.key_value}")
            
            # 检查是否从config.yaml中正确加载了配置
            if (strategy_wrong.ut_config.atr_period == ut_bot_config.get('atr_period') and
                strategy_wrong.ut_config.key_value == ut_bot_config.get('key_value')):
                print("   OK 错误调用方式也能正确从config.yaml加载配置")
                wrong_call_ok = True
            else:
                print("   FAIL 错误调用方式未能正确加载配置")
                wrong_call_ok = False
                
        except Exception as e:
            print(f"   ERROR 错误调用方式导致异常: {e}")
            wrong_call_ok = False
        
        # 6. 总结
        print("\n6. 测试总结:")
        print("-" * 40)
        
        all_tests_passed = (passed == total) and custom_config_ok and wrong_call_ok
        
        if all_tests_passed:
            print("所有测试通过！修复后的配置逻辑正确工作")
            print("\n修复效果:")
            print("   - UTBotStrategy能正确从config.yaml中读取配置")
            print("   - 传递ut_config参数时使用传入的配置（向后兼容）")
            print("   - 不传递ut_config参数时自动从config.yaml加载")
            print("   - 错误的调用方式也能正确工作")
        else:
            print("部分测试失败，需要进一步检查")
            print(f"   - 配置验证: {passed}/{total}")
            print(f"   - 自定义配置: {'OK' if custom_config_ok else 'FAIL'}")
            print(f"   - 错误调用: {'OK' if wrong_call_ok else 'FAIL'}")
        
        return all_tests_passed
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始测试修复后的UT Bot策略配置逻辑")
    
    success = test_config_logic_fix()
    
    print("\n" + "=" * 60)
    print("最终测试结果:")
    print("=" * 60)
    
    if success:
        print("SUCCESS: 修复后的配置逻辑正确工作")
        print("\n现在UTBotStrategy能够:")
        print("1. 自动从config.yaml中读取UT Bot配置")
        print("2. 支持传递ut_config参数的向后兼容方式")
        print("3. 处理错误的调用方式（如EXECUTION_MANUAL.md中的例子）")
        print("4. 确保config.yaml中的参数真正生效")
    else:
        print("FAILED: 配置逻辑修复存在问题")
        print("\n需要进一步检查:")
        print("1. _load_config_from_yaml方法的实现")
        print("2. Config对象的结构")
        print("3. 配置参数的传递逻辑")
    
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
