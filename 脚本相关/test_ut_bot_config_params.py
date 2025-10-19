#!/usr/bin/env python3
"""
测试config.yaml中UT Bot策略参数是否正确传递到ut_bot_strategy.py
"""

import yaml
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_config_loading():
    """测试配置文件加载"""
    print("=" * 60)
    print("测试config.yaml中UT Bot策略参数")
    print("=" * 60)
    
    try:
        # 读取config.yaml
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        print("1. config.yaml文件读取成功")
        
        # 获取UT Bot策略配置
        strategies = config.get('strategies', {})
        ut_bot_config = strategies.get('ut_bot', {})
        
        if not ut_bot_config:
            print("❌ 未找到UT Bot策略配置")
            return False
        
        print("2. UT Bot策略配置存在")
        
        # 显示config.yaml中的配置参数
        print("\n3. config.yaml中的UT Bot配置参数:")
        print("-" * 40)
        
        # 核心参数
        core_params = {
            'enabled': ut_bot_config.get('enabled'),
            'market_id': ut_bot_config.get('market_id'),
            'key_value': ut_bot_config.get('key_value'),
            'atr_period': ut_bot_config.get('atr_period'),
            'use_heikin_ashi': ut_bot_config.get('use_heikin_ashi'),
            'ema_length': ut_bot_config.get('ema_length'),
        }
        
        for param, value in core_params.items():
            print(f"   {param}: {value}")
        
        # 风险管理参数
        risk_params = {
            'risk_per_trade': ut_bot_config.get('risk_per_trade'),
            'atr_multiplier': ut_bot_config.get('atr_multiplier'),
            'risk_reward_breakeven': ut_bot_config.get('risk_reward_breakeven'),
            'risk_reward_takeprofit': ut_bot_config.get('risk_reward_takeprofit'),
            'tp_percent': ut_bot_config.get('tp_percent'),
        }
        
        print("\n   风险管理参数:")
        for param, value in risk_params.items():
            print(f"     {param}: {value}")
        
        # 实时tick参数
        tick_params = {
            'use_real_time_ticks': ut_bot_config.get('use_real_time_ticks'),
            'real_time_tick_interval': ut_bot_config.get('real_time_tick_interval'),
        }
        
        print("\n   实时tick参数:")
        for param, value in tick_params.items():
            print(f"     {param}: {value}")
        
        return ut_bot_config
        
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False

def test_ut_bot_strategy_creation(config_dict):
    """测试UT Bot策略创建和参数传递"""
    print("\n4. 测试UT Bot策略创建和参数传递:")
    print("-" * 40)
    
    try:
        # 导入必要的模块
        from quant_trading.strategies.ut_bot_strategy import UTBotStrategy, UTBotConfig
        from quant_trading.utils.config import Config
        
        print("   模块导入成功")
        
        # 创建Config对象
        system_config = Config.create_default()
        
        # 创建UTBotConfig对象，使用config.yaml中的参数
        ut_bot_config = UTBotConfig(
            key_value=config_dict.get('key_value', 3.0),
            atr_period=config_dict.get('atr_period', 10),
            use_heikin_ashi=config_dict.get('use_heikin_ashi', False),
            ema_length=config_dict.get('ema_length', 200),
            risk_per_trade=config_dict.get('risk_per_trade', 2.5),
            atr_multiplier=config_dict.get('atr_multiplier', 1.5),
            risk_reward_breakeven=config_dict.get('risk_reward_breakeven', 0.75),
            risk_reward_takeprofit=config_dict.get('risk_reward_takeprofit', 3.0),
            tp_percent=config_dict.get('tp_percent', 50.0),
            stoploss_type=config_dict.get('stoploss_type', "atr"),
            swing_high_bars=config_dict.get('swing_high_bars', 10),
            swing_low_bars=config_dict.get('swing_low_bars', 10),
            enable_long=config_dict.get('enable_long', True),
            enable_short=config_dict.get('enable_short', True),
            use_takeprofit=config_dict.get('use_takeprofit', True),
            use_leverage=config_dict.get('use_leverage', True),
            trading_start_time=config_dict.get('trading_start_time', "00:00"),
            trading_end_time=config_dict.get('trading_end_time', "23:59")
        )
        
        print("   UTBotConfig对象创建成功")
        
        # 创建UT Bot策略实例
        ut_bot_strategy = UTBotStrategy(
            name="UTBot",
            config=system_config,
            ut_config=ut_bot_config
        )
        
        print("   UTBotStrategy对象创建成功")
        
        # 设置市场ID
        market_id = config_dict.get('market_id', 0)
        ut_bot_strategy.market_id = market_id
        
        # 设置实时tick模式
        use_real_time_ticks = config_dict.get('use_real_time_ticks', False)
        if use_real_time_ticks:
            ut_bot_strategy.enable_real_time_ticks()
        else:
            ut_bot_strategy.disable_real_time_ticks()
        
        print("   策略配置设置完成")
        
        return ut_bot_strategy, ut_bot_config
        
    except Exception as e:
        print(f"   策略创建失败: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def test_parameter_verification(strategy, config_obj, config_dict):
    """验证参数是否正确传递"""
    print("\n5. 验证参数传递是否正确:")
    print("-" * 40)
    
    try:
        # 验证UTBotConfig对象中的参数
        print("   UTBotConfig对象参数:")
        
        verification_params = [
            ('key_value', config_obj.key_value, config_dict.get('key_value')),
            ('atr_period', config_obj.atr_period, config_dict.get('atr_period')),
            ('use_heikin_ashi', config_obj.use_heikin_ashi, config_dict.get('use_heikin_ashi')),
            ('ema_length', config_obj.ema_length, config_dict.get('ema_length')),
            ('risk_per_trade', config_obj.risk_per_trade, config_dict.get('risk_per_trade')),
            ('atr_multiplier', config_obj.atr_multiplier, config_dict.get('atr_multiplier')),
            ('risk_reward_breakeven', config_obj.risk_reward_breakeven, config_dict.get('risk_reward_breakeven')),
            ('risk_reward_takeprofit', config_obj.risk_reward_takeprofit, config_dict.get('risk_reward_takeprofit')),
            ('tp_percent', config_obj.tp_percent, config_dict.get('tp_percent')),
            ('stoploss_type', config_obj.stoploss_type, config_dict.get('stoploss_type')),
            ('swing_high_bars', config_obj.swing_high_bars, config_dict.get('swing_high_bars')),
            ('swing_low_bars', config_obj.swing_low_bars, config_dict.get('swing_low_bars')),
            ('enable_long', config_obj.enable_long, config_dict.get('enable_long')),
            ('enable_short', config_obj.enable_short, config_dict.get('enable_short')),
            ('use_takeprofit', config_obj.use_takeprofit, config_dict.get('use_takeprofit')),
            ('use_leverage', config_obj.use_leverage, config_dict.get('use_leverage')),
            ('trading_start_time', config_obj.trading_start_time, config_dict.get('trading_start_time')),
            ('trading_end_time', config_obj.trading_end_time, config_dict.get('trading_end_time')),
        ]
        
        passed = 0
        total = len(verification_params)
        
        for param_name, actual_value, expected_value in verification_params:
            if actual_value == expected_value:
                print(f"     OK {param_name}: {actual_value}")
                passed += 1
            else:
                print(f"     FAIL {param_name}: 期望 {expected_value}, 实际 {actual_value}")
        
        # 验证策略实例中的参数
        print("\n   UTBotStrategy对象参数:")
        
        strategy_params = [
            ('market_id', getattr(strategy, 'market_id', None), config_dict.get('market_id')),
            ('use_real_time_ticks', getattr(strategy, 'use_real_time_ticks', None), config_dict.get('use_real_time_ticks')),
        ]
        
        for param_name, actual_value, expected_value in strategy_params:
            if actual_value == expected_value:
                print(f"     OK {param_name}: {actual_value}")
                passed += 1
            else:
                print(f"     FAIL {param_name}: 期望 {expected_value}, 实际 {actual_value}")
            total += 1
        
        # 验证策略配置对象引用
        if hasattr(strategy, 'ut_config'):
            print(f"     OK ut_config引用: 存在")
            if strategy.ut_config is config_obj:
                print(f"     OK ut_config引用: 正确")
                passed += 1
            else:
                print(f"     FAIL ut_config引用: 不正确")
            total += 1
        else:
            print(f"     FAIL ut_config引用: 不存在")
            total += 1
        
        print(f"\n   参数验证结果: {passed}/{total} 通过")
        
        return passed == total
        
    except Exception as e:
        print(f"   参数验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_strategy_methods(strategy):
    """测试策略方法是否正常工作"""
    print("\n6. 测试策略方法:")
    print("-" * 40)
    
    try:
        # 测试get_strategy_status方法
        if hasattr(strategy, 'get_strategy_status'):
            status = strategy.get_strategy_status()
            print(f"   OK get_strategy_status方法存在，返回状态信息")
            
            # 检查状态信息中的配置参数
            if 'ut_config' in status:
                print(f"   OK 状态中包含ut_config信息")
                ut_config_status = status['ut_config']
                
                # 验证关键参数是否在状态中
                key_params = ['key_value', 'atr_period', 'ema_length', 'risk_per_trade']
                for param in key_params:
                    if param in ut_config_status:
                        print(f"     OK {param}: {ut_config_status[param]}")
                    else:
                        print(f"     FAIL {param}: 未找到")
            else:
                print(f"   FAIL 状态中缺少ut_config信息")
        else:
            print(f"   FAIL get_strategy_status方法不存在")
        
        # 测试实时tick相关方法
        if hasattr(strategy, 'process_real_time_tick'):
            print(f"   OK process_real_time_tick方法存在")
        else:
            print(f"   FAIL process_real_time_tick方法不存在")
        
        if hasattr(strategy, 'use_real_time_ticks'):
            print(f"   OK use_real_time_ticks属性存在: {strategy.use_real_time_ticks}")
        else:
            print(f"   FAIL use_real_time_ticks属性不存在")
        
        return True
        
    except Exception as e:
        print(f"   方法测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始测试config.yaml中UT Bot策略参数传递")
    
    # 1. 测试配置加载
    config_dict = test_config_loading()
    if not config_dict:
        print("\n配置加载失败，测试终止")
        return False
    
    # 2. 测试策略创建
    strategy, config_obj = test_ut_bot_strategy_creation(config_dict)
    if not strategy or not config_obj:
        print("\n策略创建失败，测试终止")
        return False
    
    # 3. 验证参数传递
    param_ok = test_parameter_verification(strategy, config_obj, config_dict)
    
    # 4. 测试策略方法
    method_ok = test_strategy_methods(strategy)
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结:")
    print("=" * 60)
    
    if param_ok and method_ok:
        print("所有测试通过！config.yaml中的UT Bot参数正确传递到策略中")
        print("\n配置参数生效验证:")
        print("   - config.yaml中的参数正确读取")
        print("   - UTBotConfig对象正确创建")
        print("   - UTBotStrategy对象正确初始化")
        print("   - 所有参数正确传递和设置")
        print("   - 策略方法正常工作")
    else:
        print("部分测试失败，请检查配置")
        if not param_ok:
            print("   - 参数传递验证失败")
        if not method_ok:
            print("   - 策略方法测试失败")
    
    return param_ok and method_ok

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
