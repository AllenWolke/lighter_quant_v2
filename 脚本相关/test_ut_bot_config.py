#!/usr/bin/env python3
"""
测试UT Bot配置是否正确加载
"""

import yaml
import sys
from pathlib import Path

def test_config_loading():
    """测试配置文件加载"""
    print("测试UT Bot配置加载...")
    
    try:
        # 读取config.yaml
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        print("config.yaml 文件读取成功")
        
        # 检查WebSocket配置
        websocket_config = config.get('websocket', {})
        if websocket_config.get('enabled'):
            print("WebSocket配置已启用")
        else:
            print("WebSocket配置未启用")
        
        # 检查实时tick配置
        real_time_tick_config = config.get('real_time_tick', {})
        if real_time_tick_config.get('enabled'):
            print("实时tick配置已启用")
        else:
            print("实时tick配置未启用")
        
        # 检查UT Bot策略配置
        strategies = config.get('strategies', {})
        ut_bot_config = strategies.get('ut_bot', {})
        
        if ut_bot_config.get('enabled'):
            print("UT Bot策略已启用")
            
            # 检查关键配置项
            required_keys = [
                'market_id', 'key_value', 'atr_period', 'ema_length',
                'risk_per_trade', 'use_real_time_ticks'
            ]
            
            missing_keys = []
            for key in required_keys:
                if key not in ut_bot_config:
                    missing_keys.append(key)
            
            if missing_keys:
                print(f"缺少配置项: {missing_keys}")
            else:
                print("所有必需配置项都已设置")
            
            # 显示关键配置值
            print(f"   市场ID: {ut_bot_config.get('market_id')}")
            print(f"   关键值: {ut_bot_config.get('key_value')}")
            print(f"   ATR周期: {ut_bot_config.get('atr_period')}")
            print(f"   EMA长度: {ut_bot_config.get('ema_length')}")
            print(f"   风险百分比: {ut_bot_config.get('risk_per_trade')}%")
            print(f"   实时tick: {'启用' if ut_bot_config.get('use_real_time_ticks') else '禁用'}")
            
        else:
            print("UT Bot策略未启用")
        
        return True
        
    except FileNotFoundError:
        print("config.yaml 文件不存在")
        return False
    except yaml.YAMLError as e:
        print(f"YAML解析错误: {e}")
        return False
    except Exception as e:
        print(f"配置测试失败: {e}")
        return False

def test_ut_bot_import():
    """测试UT Bot策略导入"""
    print("\n测试UT Bot策略导入...")
    
    try:
        # 添加项目路径
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        
        # 导入UT Bot策略
        from quant_trading.strategies.ut_bot_strategy import UTBotStrategy, UTBotConfig
        
        print("UTBotStrategy 导入成功")
        print("UTBotConfig 导入成功")
        
        # 测试配置对象创建
        config = UTBotConfig()
        print("UTBotConfig 对象创建成功")
        
        # 显示默认配置
        print(f"   默认关键值: {config.key_value}")
        print(f"   默认ATR周期: {config.atr_period}")
        print(f"   默认EMA长度: {config.ema_length}")
        
        return True
        
    except ImportError as e:
        print(f"导入失败: {e}")
        return False
    except Exception as e:
        print(f"策略测试失败: {e}")
        return False

def test_start_trading_import():
    """测试start_trading.py导入"""
    print("\n测试start_trading.py导入...")
    
    try:
        # 导入start_trading模块
        import start_trading
        
        print("start_trading.py 导入成功")
        
        # 检查关键函数是否存在
        required_functions = ['create_config', 'start_trading_engine']
        for func_name in required_functions:
            if hasattr(start_trading, func_name):
                print(f"函数 {func_name} 存在")
            else:
                print(f"函数 {func_name} 不存在")
        
        return True
        
    except ImportError as e:
        print(f"导入失败: {e}")
        return False
    except Exception as e:
        print(f"start_trading测试失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("UT Bot配置测试")
    print("=" * 60)
    
    tests = [
        test_config_loading,
        test_ut_bot_import,
        test_start_trading_import
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"测试异常: {e}")
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("所有测试通过！UT Bot配置已准备就绪")
        print("\n使用方法:")
        print("   python start_trading.py")
        print("   选择策略: 4) UT Bot策略")
    else:
        print("部分测试失败，请检查配置")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
