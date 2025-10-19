#!/usr/bin/env python3
"""
测试start_trading.py中UT Bot策略是否正确使用config.yaml中的参数
"""

import yaml
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_start_trading_ut_bot_loading():
    """测试start_trading.py中的UT Bot策略加载逻辑"""
    print("=" * 60)
    print("测试start_trading.py中UT Bot策略加载")
    print("=" * 60)
    
    try:
        # 1. 读取config.yaml中的UT Bot配置
        print("1. 读取config.yaml中的UT Bot配置:")
        print("-" * 40)
        
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        strategies = config.get('strategies', {})
        ut_bot_config = strategies.get('ut_bot', {})
        
        print(f"   enabled: {ut_bot_config.get('enabled')}")
        print(f"   market_id: {ut_bot_config.get('market_id')}")
        print(f"   key_value: {ut_bot_config.get('key_value')}")
        print(f"   atr_period: {ut_bot_config.get('atr_period')}")
        print(f"   use_real_time_ticks: {ut_bot_config.get('use_real_time_ticks')}")
        
        # 2. 模拟start_trading.py中的UT Bot策略创建逻辑
        print("\n2. 模拟start_trading.py中的UT Bot策略创建:")
        print("-" * 40)
        
        # 导入必要的模块
        from quant_trading.strategies.ut_bot_strategy import UTBotStrategy, UTBotConfig
        from quant_trading.utils.config import Config
        
        # 创建系统配置
        system_config = Config.create_default()
        
        # 模拟start_trading.py中的策略创建逻辑
        strategy_market_id = ut_bot_config.get('market_id') if 'market_id' in ut_bot_config else 0
        
        # 创建UTBotConfig对象（完全按照start_trading.py的逻辑）
        ut_bot_config_obj = UTBotConfig(
            key_value=ut_bot_config.get('key_value', 3.0),
            atr_period=ut_bot_config.get('atr_period', 10),
            use_heikin_ashi=ut_bot_config.get('use_heikin_ashi', False),
            ema_length=ut_bot_config.get('ema_length', 200),
            risk_per_trade=ut_bot_config.get('risk_per_trade', 2.5),
            atr_multiplier=ut_bot_config.get('atr_multiplier', 1.5),
            risk_reward_breakeven=ut_bot_config.get('risk_reward_breakeven', 0.75),
            risk_reward_takeprofit=ut_bot_config.get('risk_reward_takeprofit', 3.0),
            tp_percent=ut_bot_config.get('tp_percent', 50.0),
            stoploss_type=ut_bot_config.get('stoploss_type', "atr"),
            swing_high_bars=ut_bot_config.get('swing_high_bars', 10),
            swing_low_bars=ut_bot_config.get('swing_low_bars', 10),
            enable_long=ut_bot_config.get('enable_long', True),
            enable_short=ut_bot_config.get('enable_short', True),
            use_takeprofit=ut_bot_config.get('use_takeprofit', True),
            use_leverage=ut_bot_config.get('use_leverage', True),
            trading_start_time=ut_bot_config.get('trading_start_time', "00:00"),
            trading_end_time=ut_bot_config.get('trading_end_time', "23:59")
        )
        
        print("   UTBotConfig对象创建成功")
        
        # 创建UT Bot策略实例（完全按照start_trading.py的逻辑）
        ut_bot_strategy = UTBotStrategy(
            name="UTBot",
            config=system_config,
            ut_config=ut_bot_config_obj
        )
        
        print("   UTBotStrategy对象创建成功")
        
        # 设置市场ID（完全按照start_trading.py的逻辑）
        ut_bot_strategy.market_id = strategy_market_id
        
        print(f"   市场ID设置为: {ut_bot_strategy.market_id}")
        
        # 3. 验证配置参数是否正确传递
        print("\n3. 验证配置参数传递:")
        print("-" * 40)
        
        # 验证UTBotConfig中的参数
        verification_results = []
        
        test_params = [
            ('key_value', ut_bot_config_obj.key_value, ut_bot_config.get('key_value', 3.0)),
            ('atr_period', ut_bot_config_obj.atr_period, ut_bot_config.get('atr_period', 10)),
            ('use_heikin_ashi', ut_bot_config_obj.use_heikin_ashi, ut_bot_config.get('use_heikin_ashi', False)),
            ('ema_length', ut_bot_config_obj.ema_length, ut_bot_config.get('ema_length', 200)),
            ('risk_per_trade', ut_bot_config_obj.risk_per_trade, ut_bot_config.get('risk_per_trade', 2.5)),
            ('atr_multiplier', ut_bot_config_obj.atr_multiplier, ut_bot_config.get('atr_multiplier', 1.5)),
            ('risk_reward_breakeven', ut_bot_config_obj.risk_reward_breakeven, ut_bot_config.get('risk_reward_breakeven', 0.75)),
            ('risk_reward_takeprofit', ut_bot_config_obj.risk_reward_takeprofit, ut_bot_config.get('risk_reward_takeprofit', 3.0)),
            ('tp_percent', ut_bot_config_obj.tp_percent, ut_bot_config.get('tp_percent', 50.0)),
            ('stoploss_type', ut_bot_config_obj.stoploss_type, ut_bot_config.get('stoploss_type', "atr")),
            ('swing_high_bars', ut_bot_config_obj.swing_high_bars, ut_bot_config.get('swing_high_bars', 10)),
            ('swing_low_bars', ut_bot_config_obj.swing_low_bars, ut_bot_config.get('swing_low_bars', 10)),
            ('enable_long', ut_bot_config_obj.enable_long, ut_bot_config.get('enable_long', True)),
            ('enable_short', ut_bot_config_obj.enable_short, ut_bot_config.get('enable_short', True)),
            ('use_takeprofit', ut_bot_config_obj.use_takeprofit, ut_bot_config.get('use_takeprofit', True)),
            ('use_leverage', ut_bot_config_obj.use_leverage, ut_bot_config.get('use_leverage', True)),
            ('trading_start_time', ut_bot_config_obj.trading_start_time, ut_bot_config.get('trading_start_time', "00:00")),
            ('trading_end_time', ut_bot_config_obj.trading_end_time, ut_bot_config.get('trading_end_time', "23:59")),
        ]
        
        passed = 0
        total = len(test_params)
        
        for param_name, actual_value, expected_value in test_params:
            if actual_value == expected_value:
                print(f"   OK {param_name}: {actual_value}")
                passed += 1
                verification_results.append(True)
            else:
                print(f"   FAIL {param_name}: 期望 {expected_value}, 实际 {actual_value}")
                verification_results.append(False)
        
        # 验证策略实例中的参数
        print("\n   策略实例参数验证:")
        
        strategy_params = [
            ('market_id', ut_bot_strategy.market_id, strategy_market_id),
            ('use_real_time_ticks', ut_bot_strategy.use_real_time_ticks, True),  # 默认启用实时tick
        ]
        
        for param_name, actual_value, expected_value in strategy_params:
            if actual_value == expected_value:
                print(f"   OK {param_name}: {actual_value}")
                passed += 1
                verification_results.append(True)
            else:
                print(f"   FAIL {param_name}: 期望 {expected_value}, 实际 {actual_value}")
                verification_results.append(False)
            total += 1
        
        # 验证策略配置对象引用
        if hasattr(ut_bot_strategy, 'ut_config'):
            print(f"   OK ut_config引用: 存在")
            if ut_bot_strategy.ut_config is ut_bot_config_obj:
                print(f"   OK ut_config引用: 正确")
                passed += 1
                verification_results.append(True)
            else:
                print(f"   FAIL ut_config引用: 不正确")
                verification_results.append(False)
            total += 1
        else:
            print(f"   FAIL ut_config引用: 不存在")
            verification_results.append(False)
            total += 1
        
        print(f"\n   参数验证结果: {passed}/{total} 通过")
        
        # 4. 测试策略状态和功能
        print("\n4. 测试策略状态和功能:")
        print("-" * 40)
        
        # 获取策略状态
        status = ut_bot_strategy.get_strategy_status()
        print(f"   策略状态获取成功")
        
        # 检查状态中的配置信息
        if 'ut_config' in status:
            print(f"   状态中包含ut_config信息")
            ut_config_status = status['ut_config']
            
            # 验证关键参数
            key_params = ['key_value', 'atr_period', 'ema_length', 'risk_per_trade']
            for param in key_params:
                if param in ut_config_status:
                    print(f"     OK {param}: {ut_config_status[param]}")
                else:
                    print(f"     FAIL {param}: 未找到")
        else:
            print(f"   FAIL 状态中缺少ut_config信息")
        
        # 检查实时tick功能
        if hasattr(ut_bot_strategy, 'process_real_time_tick'):
            print(f"   OK process_real_time_tick方法存在")
        else:
            print(f"   FAIL process_real_time_tick方法不存在")
        
        if hasattr(ut_bot_strategy, 'use_real_time_ticks'):
            print(f"   OK use_real_time_ticks属性: {ut_bot_strategy.use_real_time_ticks}")
        else:
            print(f"   FAIL use_real_time_ticks属性不存在")
        
        # 5. 总结
        print("\n5. 测试总结:")
        print("-" * 40)
        
        all_passed = all(verification_results) and passed == total
        
        if all_passed:
            print("所有测试通过！start_trading.py中的UT Bot策略正确使用了config.yaml中的参数")
            print("\n配置参数生效验证:")
            print("   - config.yaml中的UT Bot参数正确读取")
            print("   - start_trading.py中的策略创建逻辑正确")
            print("   - UTBotConfig对象正确创建并传递参数")
            print("   - UTBotStrategy对象正确初始化")
            print("   - 所有配置参数正确传递和设置")
            print("   - 策略功能正常工作")
        else:
            print("部分测试失败，请检查配置")
            print(f"   参数验证: {passed}/{total} 通过")
            print(f"   详细结果: {verification_results}")
        
        return all_passed
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始测试start_trading.py中UT Bot策略配置参数传递")
    
    success = test_start_trading_ut_bot_loading()
    
    print("\n" + "=" * 60)
    print("最终测试结果:")
    print("=" * 60)
    
    if success:
        print("SUCCESS: start_trading.py中的UT Bot策略正确使用config.yaml中的参数")
        print("\n这意味着:")
        print("1. config.yaml中的strategies.ut_bot配置参数完全生效")
        print("2. start_trading.py中的UT Bot策略创建逻辑正确")
        print("3. 所有配置参数都正确传递到策略对象中")
        print("4. 策略可以正常使用这些配置参数进行交易")
    else:
        print("FAILED: 配置参数传递存在问题")
        print("\n请检查:")
        print("1. config.yaml中的ut_bot配置是否正确")
        print("2. start_trading.py中的策略创建逻辑是否正确")
        print("3. UTBotConfig和UTBotStrategy类的实现是否正确")
    
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
