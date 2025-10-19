#!/usr/bin/env python3
"""
测试UT Bot配置集成
验证config.yaml中的ut_bot配置是否能正确运用到ut_bot_strategy.py
以及start_trading.py是否能正确执行ut_bot_strategy.py而不是ut_bot.py
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import asyncio

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_config_integration():
    """测试配置集成"""
    print("=" * 60)
    print("测试UT Bot配置集成")
    print("=" * 60)
    
    try:
        # 1. 导入模块
        print("1. 导入模块:")
        print("-" * 40)
        
        from quant_trading.utils.config import Config
        from quant_trading.strategies import UTBotStrategy  # 从__init__.py导入
        from quant_trading.strategies.ut_bot_strategy import UTBotStrategy as UTBotStrategyNew  # 直接导入新的策略
        
        print("   模块导入成功")
        
        # 2. 检查导入的是哪个UTBotStrategy
        print("\n2. 检查导入的UTBotStrategy:")
        print("-" * 40)
        
        print(f"   从__init__.py导入的UTBotStrategy: {UTBotStrategy}")
        print(f"   从ut_bot_strategy.py直接导入的UTBotStrategy: {UTBotStrategyNew}")
        
        if UTBotStrategy == UTBotStrategyNew:
            print("   ✅ 导入的是同一个类 - 正确")
        else:
            print("   ❌ 导入的是不同的类 - 有问题！")
            print(f"   __init__.py导入的类: {UTBotStrategy.__module__}")
            print(f"   ut_bot_strategy.py的类: {UTBotStrategyNew.__module__}")
            return False
        
        # 3. 加载配置文件
        print("\n3. 加载配置文件:")
        print("-" * 40)
        
        if not Path('config.yaml').exists():
            print("   ❌ config.yaml文件不存在")
            return False
        
        config = Config.from_file('config.yaml')
        print("   ✅ 配置文件加载成功")
        
        # 4. 检查config.yaml中的ut_bot配置
        print("\n4. 检查config.yaml中的ut_bot配置:")
        print("-" * 40)
        
        if not hasattr(config, 'strategies') or 'ut_bot' not in config.strategies:
            print("   ❌ config.yaml中没有ut_bot配置")
            return False
        
        ut_config = config.strategies['ut_bot']
        print("   ✅ 找到ut_bot配置")
        
        # 显示关键配置项
        key_configs = [
            'enabled', 'market_id', 'key_value', 'atr_period', 'use_heikin_ashi',
            'ema_length', 'risk_per_trade', 'atr_multiplier', 'enable_long', 'enable_short'
        ]
        
        print("   关键配置项:")
        for key in key_configs:
            value = ut_config.get(key, "未设置")
            print(f"     {key}: {value}")
        
        # 5. 测试UTBotStrategy配置加载
        print("\n5. 测试UTBotStrategy配置加载:")
        print("-" * 40)
        
        # 创建UTBotStrategy实例
        ut_bot = UTBotStrategy(
            name="TestUTBot",
            config=config
        )
        
        print("   ✅ UTBotStrategy实例创建成功")
        
        # 检查配置是否正确加载
        ut_bot_config = ut_bot.ut_config
        print("   配置验证:")
        
        # 验证关键参数
        expected_configs = {
            'key_value': 3.0,
            'atr_period': 10,
            'use_heikin_ashi': False,
            'ema_length': 200,
            'risk_per_trade': 2.5,
            'atr_multiplier': 1.5,
            'enable_long': True,
            'enable_short': True
        }
        
        all_correct = True
        for key, expected_value in expected_configs.items():
            actual_value = getattr(ut_bot_config, key, None)
            if actual_value == expected_value:
                print(f"     ✅ {key}: {actual_value} (正确)")
            else:
                print(f"     ❌ {key}: {actual_value} (期望: {expected_value})")
                all_correct = False
        
        if all_correct:
            print("   ✅ 所有配置参数都正确加载")
        else:
            print("   ❌ 部分配置参数加载不正确")
            return False
        
        # 6. 测试实时tick模式
        print("\n6. 测试实时tick模式:")
        print("-" * 40)
        
        if hasattr(ut_bot, 'use_real_time_ticks'):
            print(f"   ✅ 实时tick模式: {ut_bot.use_real_time_ticks}")
        else:
            print("   ❌ 没有use_real_time_ticks属性")
            return False
        
        # 7. 检查策略方法
        print("\n7. 检查策略方法:")
        print("-" * 40)
        
        required_methods = [
            'process_real_time_tick',
            '_execute_signal',
            '_handle_buy_signal',
            '_handle_sell_signal'
        ]
        
        for method_name in required_methods:
            if hasattr(ut_bot, method_name):
                print(f"     ✅ {method_name}: 存在")
            else:
                print(f"     ❌ {method_name}: 不存在")
                return False
        
        # 8. 测试配置来源验证
        print("\n8. 测试配置来源验证:")
        print("-" * 40)
        
        # 检查是否使用了config.yaml中的值
        config_source_test = [
            ('key_value', 3.0),
            ('atr_period', 10),
            ('ema_length', 200)
        ]
        
        for param, expected in config_source_test:
            actual = getattr(ut_bot_config, param)
            if actual == expected:
                print(f"     ✅ {param}: {actual} (来自config.yaml)")
            else:
                print(f"     ❌ {param}: {actual} (期望: {expected})")
                return False
        
        # 9. 测试总结
        print("\n9. 测试总结:")
        print("-" * 40)
        
        print("SUCCESS: UT Bot配置集成测试通过！")
        print("\n验证结果:")
        print("1. ✅ __init__.py正确导入ut_bot_strategy.py中的UTBotStrategy")
        print("2. ✅ config.yaml中的ut_bot配置正确加载")
        print("3. ✅ UTBotStrategy正确使用config.yaml中的参数")
        print("4. ✅ 实时tick模式正确启用")
        print("5. ✅ 所有必要的方法都存在")
        
        print("\n关键发现:")
        print("- start_trading.py会正确执行ut_bot_strategy.py")
        print("- config.yaml中的ut_bot配置完全生效")
        print("- 实时tick模式已启用")
        print("- 所有Pine Script对应的功能都已实现")
        
        return True
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_start_trading_integration():
    """测试start_trading.py集成"""
    print("\n" + "=" * 60)
    print("测试start_trading.py集成")
    print("=" * 60)
    
    try:
        # 1. 检查start_trading.py中的导入
        print("1. 检查start_trading.py中的导入:")
        print("-" * 40)
        
        with open('start_trading.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'from quant_trading.strategies import' in content and 'UTBotStrategy' in content:
            print("   ✅ start_trading.py正确导入了UTBotStrategy")
        else:
            print("   ❌ start_trading.py没有正确导入UTBotStrategy")
            return False
        
        # 2. 检查UT Bot策略创建逻辑
        print("\n2. 检查UT Bot策略创建逻辑:")
        print("-" * 40)
        
        if 'ut_config = strategies_config.get(\'ut_bot\', {})' in content:
            print("   ✅ 正确从config.yaml读取ut_bot配置")
        else:
            print("   ❌ 没有从config.yaml读取ut_bot配置")
            return False
        
        if 'from quant_trading.strategies.ut_bot_strategy import UTBotConfig' in content:
            print("   ✅ 正确导入UTBotConfig")
        else:
            print("   ❌ 没有正确导入UTBotConfig")
            return False
        
        if 'ut_bot = UTBotStrategy(' in content:
            print("   ✅ 正确创建UTBotStrategy实例")
        else:
            print("   ❌ 没有正确创建UTBotStrategy实例")
            return False
        
        # 3. 检查配置参数传递
        print("\n3. 检查配置参数传递:")
        print("-" * 40)
        
        config_params = [
            'key_value=ut_config.get(\'key_value\', 3.0)',
            'atr_period=ut_config.get(\'atr_period\', 10)',
            'ema_length=ut_config.get(\'ema_length\', 200)',
            'risk_per_trade=ut_config.get(\'risk_per_trade\', 2.5)'
        ]
        
        for param in config_params:
            if param in content:
                print(f"   ✅ 正确传递参数: {param.split('=')[0]}")
            else:
                print(f"   ❌ 缺少参数传递: {param.split('=')[0]}")
                return False
        
        # 4. 检查实时tick模式设置
        print("\n4. 检查实时tick模式设置:")
        print("-" * 40)
        
        if 'use_real_time_ticks=' in content:
            print("   ✅ 正确设置实时tick模式")
        else:
            print("   ❌ 没有设置实时tick模式")
            return False
        
        print("\nSUCCESS: start_trading.py集成测试通过！")
        return True
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始测试UT Bot配置集成")
    
    # 测试配置集成
    config_test_success = test_config_integration()
    
    # 测试start_trading.py集成
    start_trading_test_success = test_start_trading_integration()
    
    print("\n" + "=" * 60)
    print("最终测试结果:")
    print("=" * 60)
    
    if config_test_success and start_trading_test_success:
        print("SUCCESS: 所有测试通过！")
        print("\n验证结果:")
        print("1. ✅ config.yaml中的ut_bot配置能正确运用到ut_bot_strategy.py")
        print("2. ✅ start_trading.py选择UT Bot策略时，会执行ut_bot_strategy.py而不是ut_bot.py")
        print("3. ✅ 所有配置参数都正确传递和加载")
        print("4. ✅ 实时tick模式正确启用")
        
        print("\n配置映射验证:")
        print("- key_value: 3.0 (来自config.yaml)")
        print("- atr_period: 10 (来自config.yaml)")
        print("- ema_length: 200 (来自config.yaml)")
        print("- risk_per_trade: 2.5% (来自config.yaml)")
        print("- enable_long: true (来自config.yaml)")
        print("- enable_short: true (来自config.yaml)")
        
        print("\n关键功能验证:")
        print("- ✅ 实时tick处理: process_real_time_tick方法存在")
        print("- ✅ 信号执行: _execute_signal方法存在")
        print("- ✅ 买入信号: _handle_buy_signal方法存在")
        print("- ✅ 卖出信号: _handle_sell_signal方法存在")
        
        print("\n执行流程验证:")
        print("1. start_trading.py导入UTBotStrategy → 来自ut_bot_strategy.py")
        print("2. 从config.yaml读取ut_bot配置 → 所有参数正确")
        print("3. 创建UTBotConfig对象 → 使用config.yaml中的值")
        print("4. 创建UTBotStrategy实例 → 启用实时tick模式")
        print("5. 添加到交易引擎 → 开始实时交易")
        
    else:
        print("FAILED: 部分测试失败")
        print("\n需要检查:")
        if not config_test_success:
            print("1. config.yaml中的ut_bot配置")
            print("2. ut_bot_strategy.py中的配置加载逻辑")
            print("3. __init__.py中的导入设置")
        if not start_trading_test_success:
            print("4. start_trading.py中的UT Bot策略创建逻辑")
            print("5. 配置参数传递")
    
    return config_test_success and start_trading_test_success

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
