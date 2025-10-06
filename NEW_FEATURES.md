# 新增功能说明

## 🆕 新增功能

### 1. 多数据源支持

#### 数据源架构
- **数据源基类** (`BaseDataSource`): 定义所有数据源的通用接口
- **Lighter数据源** (`LighterDataSource`): 从Lighter交易所API获取数据
- **TradingView数据源** (`TradingViewDataSource`): 从TradingView获取数据

#### 主要特性
- 支持多个数据源同时使用
- 可配置主数据源
- 统一的数据接口
- 自动故障转移

#### 使用方法
```python
# 从指定数据源获取数据
data = await data_manager.get_data_from_source("tradingview", "BTCUSDT", "candlesticks")

# 从TradingView获取数据
tv_data = await data_manager.get_tradingview_data("BTCUSDT", "candlesticks")
```

### 2. UT Bot策略

#### 策略特点
- 基于TradingView UT Bot Alerts实现
- 使用ATR（平均真实波幅）追踪止损
- 支持Heikin Ashi蜡烛图
- 自适应追踪止损机制

#### 核心算法
1. **ATR计算**: 计算平均真实波幅
2. **追踪止损**: 基于ATR的动态止损线
3. **信号生成**: 价格突破追踪止损线时产生交易信号
4. **仓位管理**: 自动开仓和平仓

#### 参数配置
```yaml
ut_bot:
  enabled: true
  market_id: 0
  key_value: 1.0      # 关键值，影响敏感度
  atr_period: 10      # ATR计算周期
  use_heikin_ashi: false  # 是否使用Heikin Ashi
  position_size: 0.1
  stop_loss: 0.02
  take_profit: 0.01
```

### 3. 增强的数据管理器

#### 新功能
- 多数据源支持
- 数据源切换
- 统一数据接口
- 故障处理

#### 新增方法
```python
# 获取可用数据源
sources = data_manager.get_available_data_sources()

# 设置主数据源
data_manager.set_primary_data_source("tradingview")

# 从指定数据源获取数据
data = await data_manager.get_data_from_source("tradingview", "BTCUSDT", "candlesticks")
```

## 📁 新增文件

### 数据源模块
- `quant_trading/data_sources/__init__.py`
- `quant_trading/data_sources/base_data_source.py`
- `quant_trading/data_sources/lighter_data_source.py`
- `quant_trading/data_sources/tradingview_data_source.py`

### 策略模块
- `quant_trading/strategies/ut_bot.py`

### 示例文件
- `examples/tradingview_data_example.py`
- `examples/ut_bot_strategy_example.py`

## 🔧 配置更新

### 新增配置项
```yaml
# 数据源配置
data_sources:
  primary: "lighter"  # 主数据源
  tradingview:
    enabled: true
    session_id: "qs_1"
    user_agent: "Mozilla/5.0..."
    symbol_mapping:
      "BTC_USDT": "BTCUSDT"

# UT Bot策略配置
strategies:
  ut_bot:
    enabled: true
    market_id: 0
    key_value: 1.0
    atr_period: 10
    use_heikin_ashi: false
```

## 🚀 使用方法

### 1. 运行UT Bot策略
```bash
python main.py --strategy ut_bot --market 0
```

### 2. 使用TradingView数据源
```python
# 在策略中使用TradingView数据
tv_data = await self.engine.data_manager.get_tradingview_data("BTCUSDT", "candlesticks")
```

### 3. 运行示例
```bash
# TradingView数据源示例
python examples/tradingview_data_example.py

# UT Bot策略示例
python examples/ut_bot_strategy_example.py
```

## 📊 技术指标支持

### TradingView数据源支持的技术指标
- RSI (相对强弱指数)
- MACD (移动平均收敛散度)
- ATR (平均真实波幅)
- 更多指标可扩展

### 使用方法
```python
# 获取技术指标
indicators = await tv_source.get_technical_indicators("BTCUSDT", ["RSI", "MACD", "ATR"])
```

## 🔄 数据源切换

### 自动切换
系统支持在主数据源不可用时自动切换到备用数据源。

### 手动切换
```python
# 切换到TradingView数据源
data_manager.set_primary_data_source("tradingview")

# 切换回Lighter数据源
data_manager.set_primary_data_source("lighter")
```

## ⚠️ 注意事项

### TradingView数据源
1. 需要网络连接访问TradingView
2. 数据获取可能受到限制
3. 建议作为辅助数据源使用

### UT Bot策略
1. 需要足够的历史数据计算ATR
2. 参数调整影响策略敏感度
3. 建议先在回测中验证

### 性能考虑
1. 多数据源会增加网络请求
2. 建议合理设置数据更新频率
3. 监控数据源可用性

## 🔮 未来扩展

### 计划中的功能
1. 更多数据源支持（Binance、Coinbase等）
2. 实时WebSocket数据流
3. 数据源健康检查
4. 数据质量监控
5. 更多技术指标

### 扩展接口
```python
# 添加自定义数据源
class MyDataSource(BaseDataSource):
    async def get_candlesticks(self, symbol, timeframe, limit):
        # 实现自定义数据获取逻辑
        pass
```

## 📈 性能优化

### 数据缓存
- 智能数据缓存机制
- 减少重复请求
- 提高响应速度

### 异步处理
- 异步数据获取
- 并发处理多个数据源
- 非阻塞操作

### 错误处理
- 完善的异常处理
- 自动重试机制
- 故障恢复

这些新功能大大增强了量化交易系统的灵活性和可扩展性，为策略开发提供了更多的数据源选择和更丰富的技术指标支持。
