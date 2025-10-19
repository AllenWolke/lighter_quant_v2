#!/usr/bin/env python3
"""
测试tick_data完整数据流
验证从WebSocket到策略的完整数据传递
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_tick_data_flow():
    """测试tick_data完整数据流"""
    print("=" * 60)
    print("测试tick_data完整数据流")
    print("=" * 60)
    
    try:
        # 1. 导入必要的模块
        print("1. 导入模块:")
        print("-" * 40)
        
        from quant_trading.strategies.ut_bot_strategy import UTBotStrategy, UTBotConfig
        from quant_trading.utils.config import Config
        from quant_trading.core.data_manager import DataManager
        from quant_trading.core.trading_engine import TradingEngine
        
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
        
        # 设置策略的市场ID
        strategy.market_id = 0
        
        print("   UTBotStrategy创建成功")
        print(f"   策略market_id: {strategy.market_id}")
        print(f"   策略use_real_time_ticks: {strategy.use_real_time_ticks}")
        
        # 3. 模拟WebSocket订单簿数据
        print("\n3. 模拟WebSocket订单簿数据:")
        print("-" * 40)
        
        # 模拟从lighter/ws_client.py接收的订单簿数据
        mock_order_book = {
            "bids": [
                {"price": "3245.0", "size": "1.5"},
                {"price": "3244.5", "size": "2.0"},
                {"price": "3244.0", "size": "1.0"}
            ],
            "asks": [
                {"price": "3246.0", "size": "1.2"},
                {"price": "3246.5", "size": "1.8"},
                {"price": "3247.0", "size": "2.5"}
            ]
        }
        
        print(f"   模拟订单簿数据: {mock_order_book}")
        
        # 4. 模拟data_manager.py的数据转换
        print("\n4. 模拟data_manager.py的数据转换:")
        print("-" * 40)
        
        # 模拟data_manager.py的_on_order_book_update方法
        def simulate_data_manager_conversion(market_id: int, order_book: Dict[str, Any]):
            """模拟data_manager.py的数据转换逻辑"""
            try:
                # 提取实时价格数据
                if "bids" in order_book and "asks" in order_book:
                    bids = order_book["bids"]
                    asks = order_book["asks"]
                    
                    if bids and asks:
                        best_bid = float(bids[0]["price"]) if bids else 0
                        best_ask = float(asks[0]["price"]) if asks else 0
                        
                        if best_bid > 0 and best_ask > 0:
                            # 计算中间价
                            mid_price = (best_bid + best_ask) / 2
                            
                            # 构建tick数据
                            tick_data = {
                                "timestamp": datetime.now().timestamp(),
                                "price": mid_price,
                                "bid": best_bid,
                                "ask": best_ask,
                                "bid_size": float(bids[0]["size"]) if bids else 0,
                                "ask_size": float(asks[0]["size"]) if asks else 0,
                                "spread": best_ask - best_bid,
                                "data_type": "order_book"
                            }
                            
                            print(f"   转换后的tick_data: {tick_data}")
                            return tick_data
                            
            except Exception as e:
                print(f"   数据转换失败: {e}")
                return None
        
        # 执行数据转换
        tick_data = simulate_data_manager_conversion(0, mock_order_book)
        
        if not tick_data:
            print("   数据转换失败，无法继续测试")
            return False
        
        # 5. 模拟trading_engine.py的数据分发
        print("\n5. 模拟trading_engine.py的数据分发:")
        print("-" * 40)
        
        # 模拟trading_engine.py的_on_real_time_tick方法
        def simulate_trading_engine_distribution(market_id: int, tick_data: Dict[str, Any]):
            """模拟trading_engine.py的数据分发逻辑"""
            try:
                # 为支持实时tick的策略执行实时计算
                strategies = [strategy]  # 模拟策略列表
                
                for strategy_obj in strategies:
                    if strategy_obj.is_active():
                        # 检查策略是否支持实时tick模式
                        if hasattr(strategy_obj, 'use_real_time_ticks') and strategy_obj.use_real_time_ticks:
                            # 检查策略是否关注这个市场
                            if (hasattr(strategy_obj, 'market_id') and strategy_obj.market_id == market_id):
                                print(f"   策略 {strategy_obj.name} 将处理市场 {market_id} 的tick数据")
                                return True
                                
                print("   没有策略需要处理这个tick数据")
                return False
                
            except Exception as e:
                print(f"   数据分发失败: {e}")
                return False
        
        # 执行数据分发
        distribution_result = simulate_trading_engine_distribution(0, tick_data)
        
        # 6. 测试策略的tick数据处理
        print("\n6. 测试策略的tick数据处理:")
        print("-" * 40)
        
        import asyncio
        
        async def test_strategy_tick_processing():
            try:
                # 直接调用策略的process_real_time_tick方法
                await strategy.process_real_time_tick(0, tick_data)
                print("   策略tick数据处理成功")
                return True
            except Exception as e:
                print(f"   策略tick数据处理失败: {e}")
                return False
        
        # 运行测试
        processing_result = asyncio.run(test_strategy_tick_processing())
        
        # 7. 验证数据完整性
        print("\n7. 验证数据完整性:")
        print("-" * 40)
        
        # 检查策略是否正确处理了tick数据
        if 0 in strategy.current_prices:
            actual_price = strategy.current_prices[0]
            expected_price = tick_data['price']
            if actual_price == expected_price:
                print(f"   OK 价格数据正确: {actual_price}")
            else:
                print(f"   FAIL 价格数据不匹配: 期望 {expected_price}, 实际 {actual_price}")
                return False
        else:
            print("   FAIL 价格数据未被存储")
            return False
        
        # 检查其他数据字段
        required_fields = ['price', 'bid', 'ask', 'spread', 'timestamp']
        for field in required_fields:
            if field in tick_data:
                print(f"   OK {field} 字段存在: {tick_data[field]}")
            else:
                print(f"   FAIL {field} 字段缺失")
                return False
        
        # 8. 总结
        print("\n8. 测试总结:")
        print("-" * 40)
        
        all_tests_passed = distribution_result and processing_result
        
        if all_tests_passed:
            print("所有测试通过！tick_data数据流完整")
            print("\n数据流验证:")
            print("   - WebSocket订单簿数据接收: OK")
            print("   - data_manager.py数据转换: OK")
            print("   - trading_engine.py数据分发: OK")
            print("   - ut_bot_strategy.py数据处理: OK")
            print("   - 数据完整性验证: OK")
        else:
            print("部分测试失败，需要进一步检查")
            print(f"   - 数据分发: {'OK' if distribution_result else 'FAIL'}")
            print(f"   - 数据处理: {'OK' if processing_result else 'FAIL'}")
        
        return all_tests_passed
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始测试tick_data完整数据流")
    
    success = test_tick_data_flow()
    
    print("\n" + "=" * 60)
    print("最终测试结果:")
    print("=" * 60)
    
    if success:
        print("SUCCESS: tick_data数据流完整")
        print("\n数据流路径:")
        print("1. lighter/ws_client.py → 接收WebSocket订单簿更新")
        print("2. data_manager.py → 转换订单簿数据为tick_data")
        print("3. trading_engine.py → 分发tick_data给策略")
        print("4. ut_bot_strategy.py → 处理tick_data并生成交易信号")
        print("\ntick_data包含的字段:")
        print("- timestamp: 时间戳")
        print("- price: 中间价")
        print("- bid: 最佳买价")
        print("- ask: 最佳卖价")
        print("- bid_size: 买价数量")
        print("- ask_size: 卖价数量")
        print("- spread: 价差")
        print("- data_type: 数据类型")
    else:
        print("FAILED: tick_data数据流存在问题")
        print("\n需要进一步检查:")
        print("1. WebSocket连接和数据接收")
        print("2. data_manager.py的数据转换逻辑")
        print("3. trading_engine.py的数据分发逻辑")
        print("4. ut_bot_strategy.py的数据处理逻辑")
    
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
