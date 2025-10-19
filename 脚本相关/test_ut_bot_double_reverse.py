#!/usr/bin/env python3
"""
测试UT Bot策略的双倍反向订单功能
验证信号优先级和冲突处理
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, AsyncMock

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from quant_trading.strategies.ut_bot import UTBotStrategy
from quant_trading.utils.config import Config
from quant_trading.core.position_manager import Position, PositionSide

class MockPosition:
    """模拟持仓对象"""
    def __init__(self, side: str, size: float, entry_price: float):
        self.side = Mock()
        self.side.value = side
        self.side = PositionSide.LONG if side == "long" else PositionSide.SHORT
        self.size = size
        self.entry_price = entry_price

class MockEngine:
    """模拟交易引擎"""
    def __init__(self):
        self.position_manager = Mock()
        self.order_manager = Mock()
        self.data_manager = Mock()

class TestUTBotDoubleReverse:
    """测试UT Bot双倍反向订单功能"""
    
    def __init__(self):
        self.config = self._create_test_config()
        self.strategy = None
        self.test_results = []
    
    def _create_test_config(self):
        """创建测试配置"""
        config = Config.create_default()
        config.strategies = {
            'ut_bot': {
                'position_size': 2.0,
                'stop_loss': 0.02,
                'take_profit': 0.01,
                'leverage': 10.0,
                'margin_mode': 'isolated',
                'order_type': 'market',
                'limit_price_offset': 0.002,
                'price_slippage_tolerance': 0.02,
                'enable_multi_timeframe': True,
                'wait_for_kline_completion': True,
                'kline_types': [1, 5],
                'market_slippage_config': {
                    0: {"enabled": True, "tolerance": 0.01},
                    2: {"enabled": False, "tolerance": 0.02},
                    3: {"enabled": True, "tolerance": 0.03},
                },
                'market_risk_config': {
                    0: {"stop_loss_enabled": True, "stop_loss": 0.15, "take_profit_enabled": True, "take_profit": 0.25},
                    2: {"stop_loss_enabled": True, "stop_loss": 0.20, "take_profit_enabled": False, "take_profit": 0.30},
                    3: {"stop_loss_enabled": True, "stop_loss": 0.30, "take_profit_enabled": True, "take_profit": 0.50},
                }
            }
        }
        return config
    
    async def setup_strategy(self):
        """设置策略"""
        self.strategy = UTBotStrategy(
            config=self.config,
            market_id=3,  # DOGE
            key_value=0.5,
            atr_period=5,
            use_heikin_ashi=False,
            position_size=2.0,
            stop_loss=0.02,
            take_profit=0.01,
            leverage=10.0,
            margin_mode='isolated',
            order_type='market',
            limit_price_offset=0.002,
            enable_multi_timeframe=True
        )
        
        # 设置模拟引擎
        self.strategy.engine = MockEngine()
        self.strategy._get_position = Mock()
        self.strategy._create_order = AsyncMock()
        self.strategy._log_signal = Mock()
        self.strategy._check_risk_limits = Mock(return_value=True)
        
        print("策略初始化完成")
    
    async def test_scenario_1_consistent_signal(self):
        """测试场景1：上一根K线信号与持仓一致"""
        print("\n测试场景1：上一根K线信号与持仓一致")
        
        # 设置当前持仓为多仓
        self.strategy._get_position.return_value = MockPosition("long", 10.0, 0.20)
        
        # 设置上一根K线信号为买入（与多仓一致）
        self.strategy.previous_kline_signal = 1
        
        # 设置多时间周期信号
        self.strategy.tf_5m_signal = 1
        self.strategy.tf_1m_signal = 1
        
        # 执行决策
        await self.strategy._multi_timeframe_decision(0.21)
        
        # 验证结果
        self.strategy._create_order.assert_not_called()
        print("场景1通过：信号一致时保持持仓，未执行额外订单")
    
    async def test_scenario_2_inconsistent_signal_long_to_short(self):
        """测试场景2：上一根K线信号与持仓不一致（多仓→空仓）"""
        print("\n🧪 测试场景2：上一根K线信号与持仓不一致（多仓→空仓）")
        
        # 设置当前持仓为多仓
        self.strategy._get_position.return_value = MockPosition("long", 10.0, 0.20)
        
        # 设置上一根K线信号为卖出（与多仓不一致）
        self.strategy.previous_kline_signal = -1
        
        # 设置多时间周期信号
        self.strategy.tf_5m_signal = 1
        self.strategy.tf_1m_signal = 1
        
        # 执行决策
        await self.strategy._multi_timeframe_decision(0.21)
        
        # 验证结果：应该先平多仓，再开双倍空仓
        assert self.strategy._create_order.call_count >= 2, "应该执行平仓和开双倍空仓"
        print("✅ 场景2通过：信号不一致时执行双倍反向订单")
    
    async def test_scenario_3_inconsistent_signal_short_to_long(self):
        """测试场景3：上一根K线信号与持仓不一致（空仓→多仓）"""
        print("\n🧪 测试场景3：上一根K线信号与持仓不一致（空仓→多仓）")
        
        # 重置模拟
        self.strategy._create_order.reset_mock()
        
        # 设置当前持仓为空仓
        self.strategy._get_position.return_value = MockPosition("short", 10.0, 0.20)
        
        # 设置上一根K线信号为买入（与空仓不一致）
        self.strategy.previous_kline_signal = 1
        
        # 设置多时间周期信号
        self.strategy.tf_5m_signal = -1
        self.strategy.tf_1m_signal = -1
        
        # 执行决策
        await self.strategy._multi_timeframe_decision(0.21)
        
        # 验证结果：应该先平空仓，再开双倍多仓
        assert self.strategy._create_order.call_count >= 2, "应该执行平仓和开双倍多仓"
        print("✅ 场景3通过：信号不一致时执行双倍反向订单")
    
    async def test_scenario_4_priority_override(self):
        """测试场景4：双倍反向订单优先级高于多时间周期信号"""
        print("\n🧪 测试场景4：双倍反向订单优先级测试")
        
        # 重置模拟
        self.strategy._create_order.reset_mock()
        
        # 设置当前持仓为多仓
        self.strategy._get_position.return_value = MockPosition("long", 10.0, 0.20)
        
        # 设置上一根K线信号为卖出（与多仓不一致）
        self.strategy.previous_kline_signal = -1
        
        # 设置多时间周期信号为买入（与双倍反向订单冲突）
        self.strategy.tf_5m_signal = 1
        self.strategy.tf_1m_signal = 1
        
        # 执行决策
        await self.strategy._multi_timeframe_decision(0.21)
        
        # 验证结果：应该执行双倍反向订单，跳过多时间周期信号
        assert self.strategy._create_order.call_count >= 2, "应该执行双倍反向订单"
        print("✅ 场景4通过：双倍反向订单优先级高于多时间周期信号")
    
    async def test_scenario_5_no_position(self):
        """测试场景5：无持仓时跳过双倍反向订单检查"""
        print("\n🧪 测试场景5：无持仓时跳过双倍反向订单检查")
        
        # 重置模拟
        self.strategy._create_order.reset_mock()
        
        # 设置无持仓
        self.strategy._get_position.return_value = None
        
        # 设置上一根K线信号
        self.strategy.previous_kline_signal = 1
        
        # 设置多时间周期信号
        self.strategy.tf_5m_signal = 1
        self.strategy.tf_1m_signal = 1
        
        # 执行决策
        await self.strategy._multi_timeframe_decision(0.21)
        
        # 验证结果：应该执行正常的多时间周期决策
        assert self.strategy._create_order.call_count == 1, "应该执行正常开仓"
        print("✅ 场景5通过：无持仓时跳过双倍反向订单检查")
    
    async def test_scenario_6_double_position_calculation(self):
        """测试场景6：双倍仓位计算"""
        print("\n🧪 测试场景6：双倍仓位计算")
        
        # 重置模拟
        self.strategy._create_order.reset_mock()
        
        # 设置当前持仓为多仓
        self.strategy._get_position.return_value = MockPosition("long", 10.0, 0.20)
        
        # 设置上一根K线信号为买入（与多仓一致，应该开双倍多仓）
        self.strategy.previous_kline_signal = 1
        
        # 执行双倍仓位开仓
        await self.strategy._open_double_position(0.21, "long", "测试双倍仓位")
        
        # 验证订单参数
        call_args = self.strategy._create_order.call_args
        order_size = call_args[1]['size']
        expected_size = (2.0 * 2.0) / 0.21  # 双倍USD金额 / 价格
        
        assert abs(order_size - expected_size) < 0.001, f"双倍仓位计算错误: 期望{expected_size}, 实际{order_size}"
        print(f"✅ 场景6通过：双倍仓位计算正确 - 期望{expected_size:.6f}, 实际{order_size:.6f}")
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("开始测试UT Bot双倍反向订单功能")
        print("=" * 60)
        
        await self.setup_strategy()
        
        try:
            await self.test_scenario_1_consistent_signal()
            await self.test_scenario_2_inconsistent_signal_long_to_short()
            await self.test_scenario_3_inconsistent_signal_short_to_long()
            await self.test_scenario_4_priority_override()
            await self.test_scenario_5_no_position()
            await self.test_scenario_6_double_position_calculation()
            
            print("\n" + "=" * 60)
            print("所有测试通过！UT Bot双倍反向订单功能正常工作")
            print("\n功能验证总结：")
            print("✓ 上一根K线信号与持仓一致时保持持仓")
            print("✓ 上一根K线信号与持仓不一致时执行双倍反向订单")
            print("✓ 双倍反向订单优先级高于多时间周期信号")
            print("✓ 无持仓时跳过双倍反向订单检查")
            print("✓ 双倍仓位计算正确")
            print("✓ 信号冲突处理正确")
            
        except Exception as e:
            print(f"\n测试失败: {e}")
            import traceback
            traceback.print_exc()

async def main():
    """主函数"""
    tester = TestUTBotDoubleReverse()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
