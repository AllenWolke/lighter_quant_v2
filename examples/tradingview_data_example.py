"""
TradingView数据源使用示例
演示如何从TradingView获取市场数据
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from quant_trading import Config
from quant_trading.data_sources import TradingViewDataSource


async def main():
    """TradingView数据源示例"""
    print("TradingView数据源使用示例")
    print("=" * 40)
    
    # 创建配置
    config = Config.create_default()
    
    # 配置TradingView数据源
    tv_config = {
        "enabled": True,
        "session_id": "qs_1",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "symbol_mapping": {
            "BTC_USDT": "BTCUSDT",
            "ETH_USDT": "ETHUSDT",
            "BNB_USDT": "BNBUSDT"
        }
    }
    
    try:
        # 创建TradingView数据源
        tv_source = TradingViewDataSource(tv_config)
        await tv_source.initialize()
        
        print("✅ TradingView数据源初始化成功")
        print(f"支持的交易对: {tv_source.get_supported_symbols()}")
        print(f"支持的时间周期: {tv_source.get_supported_timeframes()}")
        print()
        
        # 获取BTC/USDT的K线数据
        print("📈 获取BTC/USDT的K线数据...")
        candlesticks = await tv_source.get_candlesticks("BTCUSDT", "1h", 10)
        
        if candlesticks:
            print(f"获取到 {len(candlesticks)} 条K线数据:")
            for i, candle in enumerate(candlesticks[-5:]):  # 显示最后5条
                print(f"  {i+1}. 时间: {candle['timestamp']}, "
                      f"开盘: {candle['open']:.2f}, "
                      f"最高: {candle['high']:.2f}, "
                      f"最低: {candle['low']:.2f}, "
                      f"收盘: {candle['close']:.2f}, "
                      f"成交量: {candle['volume']:.2f}")
        else:
            print("❌ 未能获取到K线数据")
            
        print()
        
        # 获取当前价格
        print("💰 获取BTC/USDT当前价格...")
        current_price = await tv_source.get_current_price("BTCUSDT")
        if current_price:
            print(f"当前价格: ${current_price:.2f}")
        else:
            print("❌ 未能获取当前价格")
            
        print()
        
        # 获取技术指标
        print("📊 获取技术指标...")
        indicators = await tv_source.get_technical_indicators("BTCUSDT", ["RSI", "MACD", "ATR"])
        if indicators:
            print("技术指标数据:")
            for name, value in indicators.items():
                print(f"  {name}: {value}")
        else:
            print("❌ 未能获取技术指标")
            
    except Exception as e:
        print(f"❌ 运行错误: {e}")
        
    print("\n✅ 示例完成")


if __name__ == "__main__":
    asyncio.run(main())
