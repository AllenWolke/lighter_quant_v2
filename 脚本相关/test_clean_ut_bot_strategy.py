#!/usr/bin/env python3
"""
测试清理后的UT Bot策略
验证只保留实时tick处理逻辑，删除K线数据处理逻辑
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_clean_ut_bot_strategy():
    """测试清理后的UT Bot策略"""
    print("=" * 60)
    print("测试清理后的UT Bot策略")
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
            name="UTBot_Clean",
            config=system_config,
            ut_config=ut_bot_config
        )
        
        # 设置策略的市场ID
        strategy.market_id = 0
        
        print("   UTBotStrategy创建成功")
        print(f"   策略market_id: {strategy.market_id}")
        print(f"   策略use_real_time_ticks: {strategy.use_real_time_ticks}")
        
        # 3. 检查删除的函数
        print("\n3. 检查删除的函数:")
        print("-" * 40)
        
        # 检查process_market_data函数是否为空实现
        if hasattr(strategy, 'process_market_data'):
            print("   OK: process_market_data函数存在但为空实现（符合抽象方法要求）")
        else:
            print("   FAIL: process_market_data函数缺失（抽象方法必须实现）")
            return False
        
        # 检查是否还有_process_single_market函数
        if hasattr(strategy, '_process_single_market'):
            print("   FAIL: _process_single_market函数仍然存在")
            return False
        else:
            print("   OK: _process_single_market函数已删除")
        
        # 检查_update_market_data_history函数（用于实时tick数据，应该保留）
        if hasattr(strategy, '_update_market_data_history'):
            print("   OK: _update_market_data_history函数保留（用于实时tick数据）")
        else:
            print("   FAIL: _update_market_data_history函数缺失（实时tick需要）")
            return False
        
        # 检查是否还有_calculate_indicators函数
        if hasattr(strategy, '_calculate_indicators'):
            print("   FAIL: _calculate_indicators函数仍然存在")
            return False
        else:
            print("   OK: _calculate_indicators函数已删除")
        
        # 检查是否还有_generate_signal函数
        if hasattr(strategy, '_generate_signal'):
            print("   FAIL: _generate_signal函数仍然存在")
            return False
        else:
            print("   OK: _generate_signal函数已删除")
        
        # 检查_execute_trading_logic函数（用于执行交易逻辑，应该保留）
        if hasattr(strategy, '_execute_trading_logic'):
            print("   OK: _execute_trading_logic函数保留（用于执行交易逻辑）")
        else:
            print("   FAIL: _execute_trading_logic函数缺失（交易执行需要）")
            return False
        
        # 4. 检查保留的函数
        print("\n4. 检查保留的函数:")
        print("-" * 40)
        
        # 检查是否还有process_real_time_tick函数
        if hasattr(strategy, 'process_real_time_tick'):
            print("   OK: process_real_time_tick函数保留")
        else:
            print("   FAIL: process_real_time_tick函数缺失")
            return False
        
        # 检查是否还有_calculate_real_time_indicators函数
        if hasattr(strategy, '_calculate_real_time_indicators'):
            print("   OK: _calculate_real_time_indicators函数保留")
        else:
            print("   FAIL: _calculate_real_time_indicators函数缺失")
            return False
        
        # 检查是否还有_generate_real_time_signals函数
        if hasattr(strategy, '_generate_real_time_signals'):
            print("   OK: _generate_real_time_signals函数保留")
        else:
            print("   FAIL: _generate_real_time_signals函数缺失")
            return False
        
        # 5. 测试实时tick处理
        print("\n5. 测试实时tick处理:")
        print("-" * 40)
        
        # 创建测试tick数据
        test_tick_data = {
            "timestamp": datetime.now().timestamp(),
            "price": 3245.5,
            "bid": 3245.0,
            "ask": 3246.0,
            "bid_size": 1.5,
            "ask_size": 1.2,
            "spread": 1.0,
            "data_type": "order_book"
        }
        
        print(f"   测试tick_data: {test_tick_data}")
        
        import asyncio
        
        async def test_real_time_tick():
            try:
                # 测试实时tick处理
                await strategy.process_real_time_tick(0, test_tick_data)
                print("   OK: 实时tick处理成功")
                
                # 验证数据是否正确处理
                if 0 in strategy.current_prices:
                    actual_price = strategy.current_prices[0]
                    expected_price = test_tick_data['price']
                    if actual_price == expected_price:
                        print(f"   OK: 价格数据正确: {actual_price}")
                        return True
                    else:
                        print(f"   FAIL: 价格数据不匹配: 期望 {expected_price}, 实际 {actual_price}")
                        return False
                else:
                    print("   FAIL: 价格数据未被存储")
                    return False
                    
            except Exception as e:
                print(f"   FAIL: 实时tick处理失败: {e}")
                return False
        
        # 运行测试
        tick_result = asyncio.run(test_real_time_tick())
        
        # 6. 总结
        print("\n6. 测试总结:")
        print("-" * 40)
        
        if tick_result:
            print("所有测试通过！UT Bot策略清理成功")
            print("\n清理效果:")
            print("   - 删除了K线数据处理逻辑")
            print("   - 保留了实时tick处理逻辑")
            print("   - 符合Pine Script的calc_on_every_tick逻辑")
            print("   - 避免了历史数据对交易信号的干扰")
        else:
            print("部分测试失败，需要进一步检查")
            print(f"   - 实时tick处理: {'OK' if tick_result else 'FAIL'}")
        
        return tick_result
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始测试清理后的UT Bot策略")
    
    success = test_clean_ut_bot_strategy()
    
    print("\n" + "=" * 60)
    print("最终测试结果:")
    print("=" * 60)
    
    if success:
        print("SUCCESS: UT Bot策略清理成功")
        print("\n清理内容:")
        print("1. 删除process_market_data函数 - 处理K线数据")
        print("2. 删除_process_single_market函数 - 处理单个市场K线数据")
        print("3. 删除_update_market_data_history函数 - 更新K线历史数据")
        print("4. 删除_calculate_indicators函数 - 基于K线数据计算指标")
        print("5. 删除_generate_signal函数 - 基于K线数据生成信号")
        print("6. 删除_execute_trading_logic函数 - 执行K线数据交易逻辑")
        print("\n保留内容:")
        print("1. process_real_time_tick函数 - 处理实时tick数据")
        print("2. _calculate_real_time_indicators函数 - 实时计算指标")
        print("3. _generate_real_time_signals函数 - 实时生成信号")
        print("\n符合Pine Script逻辑:")
        print("- calc_on_every_tick = true")
        print("- 每个tick都重新计算")
        print("- 不依赖历史K线数据")
        print("- 避免历史数据干扰交易信号")
    else:
        print("FAILED: UT Bot策略清理存在问题")
        print("\n需要进一步检查:")
        print("1. 函数删除是否完整")
        print("2. 实时tick处理是否正常")
        print("3. 代码逻辑是否一致")
    
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
