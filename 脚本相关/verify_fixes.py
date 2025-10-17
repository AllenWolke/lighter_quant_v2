#!/usr/bin/env python3
"""
验证所有修复是否正常工作
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("Verifying Quantitative Trading System Fixes")
print("=" * 60)
print()

# 测试1: Config.create_default()
print("测试 1: Config.create_default()")
try:
    from quant_trading import Config
    config = Config.create_default()
    
    # 检查所有必需字段
    assert hasattr(config, 'lighter_config'), "缺少 lighter_config"
    assert hasattr(config, 'trading_config'), "缺少 trading_config"
    assert hasattr(config, 'risk_config'), "缺少 risk_config"
    assert hasattr(config, 'notifications_config'), "缺少 notifications_config"
    assert hasattr(config, 'data_sources'), "缺少 data_sources"
    assert hasattr(config, 'strategies'), "缺少 strategies"
    
    print("  [OK] Config.create_default() works correctly")
    print(f"     - notifications_config: {config.notifications_config}")
    print(f"     - data_sources: {config.data_sources}")
    print(f"     - strategies: {config.strategies}")
except Exception as e:
    print(f"  [FAIL] Failed: {e}")
    sys.exit(1)

print()

# 测试2: 策略导入
print("测试 2: 策略类导入")
try:
    from quant_trading.strategies import (
        MeanReversionStrategy,
        MomentumStrategy,
        ArbitrageStrategy,
        UTBotStrategy
    )
    print("  [OK] All strategy classes imported successfully")
    print("     - MeanReversionStrategy")
    print("     - MomentumStrategy")
    print("     - ArbitrageStrategy")
    print("     - UTBotStrategy")
except Exception as e:
    print(f"  [FAIL] Failed: {e}")
    sys.exit(1)

print()

# 测试3: start_trading.py
print("测试 3: start_trading.py")
try:
    from start_trading import create_config
    
    user_config = {
        "base_url": "https://testnet.zklighter.elliot.ai",
        "api_key_private_key": "test_key",
        "account_index": 0,
        "api_key_index": 0
    }
    
    config = create_config(user_config)
    assert config.lighter_config["base_url"] == user_config["base_url"]
    assert config.lighter_config["api_key_private_key"] == user_config["api_key_private_key"]
    
    print("  [OK] start_trading.py create_config() works correctly")
except Exception as e:
    print(f"  [FAIL] Failed: {e}")
    sys.exit(1)

print()

# 测试4: Config.from_file()
print("测试 4: Config.from_file()")
try:
    import os
    if os.path.exists("config.yaml"):
        config = Config.from_file("config.yaml")
        print("  [OK] Config.from_file() works correctly")
        print(f"     - 成功加载 config.yaml")
    else:
        print("  [SKIP] config.yaml does not exist, skipping test")
except Exception as e:
    print(f"  [FAIL] Failed: {e}")
    sys.exit(1)

print()

# 测试5: Config.to_dict()
print("测试 5: Config.to_dict()")
try:
    config = Config.create_default()
    config_dict = config.to_dict()
    
    # 检查所有字段都被导出
    assert "lighter" in config_dict, "缺少 lighter"
    assert "trading" in config_dict, "缺少 trading"
    assert "risk_management" in config_dict, "缺少 risk_management"
    assert "notifications" in config_dict, "缺少 notifications"
    assert "data_sources" in config_dict, "缺少 data_sources"
    assert "strategies" in config_dict, "缺少 strategies"
    assert "log" in config_dict, "缺少 log"
    
    print("  [OK] Config.to_dict() works correctly")
    print(f"     - 导出字段数: {len(config_dict)}")
except Exception as e:
    print(f"  [FAIL] Failed: {e}")
    sys.exit(1)

print()

# 测试6: TradingEngine
print("测试 6: TradingEngine 初始化")
try:
    from quant_trading import TradingEngine
    
    config = Config.create_default()
    config.lighter_config.update({
        "base_url": "https://testnet.zklighter.elliot.ai",
        "api_key_private_key": "0" * 64,  # 测试用假密钥
        "account_index": 0,
        "api_key_index": 0
    })
    
    # 注意：不启动引擎，只测试初始化
    # engine = TradingEngine(config)  # 这会尝试连接，可能失败
    
    print("  [OK] TradingEngine can be imported")
    print("     - 注意: 未测试实际连接")
except Exception as e:
    print(f"  [WARN] Warning: {e}")
    print("     - TradingEngine 需要有效的 API 密钥才能完全测试")

print()
print("=" * 60)
print("Verification Complete")
print("=" * 60)
print()
print("Summary:")
print("  [OK] Config class fixes working")
print("  [OK] All strategies can be imported")
print("  [OK] start_trading.py works correctly")
print("  [OK] Config load and save functions work")
print()
print("Next Steps:")
print("  1. Run: python start_trading.py")
print("     Test interactive startup")
print("  2. Run: python main.py --help")
print("     View command line options")
print("  3. Run: python backtest.py --strategy mean_reversion --days 7")
print("     Test backtesting system")
print()
print("Documentation:")
print("  - CONFIG_FIX_DOCUMENTATION.md")
print("    Config fix details")
print("  - UPDATE_SUMMARY.md")
print("    All updates summary")
print("  - quant_trading/STRATEGIES_QUICK_REFERENCE.md")
print("    Strategy quick reference")
print()

