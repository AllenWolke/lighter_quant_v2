# 量化交易策略快速参考

## 可用策略列表

本系统提供以下4种内置交易策略：

### 1. 均值回归策略 (Mean Reversion)

**策略代码**: `mean_reversion`  
**适用场景**: 震荡市场、区间交易  
**核心原理**: 价格偏离均值后会回归

**关键参数**:
```yaml
strategies:
  mean_reversion:
    enabled: true
    market_id: 0
    lookback_period: 20      # 回望周期（K线数量）
    threshold: 2.0           # Z分数阈值（标准差倍数）
    position_size: 0.1       # 仓位大小（占总资金比例）
    stop_loss: 0.02          # 止损比例（2%）
    take_profit: 0.01        # 止盈比例（1%）
```

**使用方法**:
```bash
# 命令行启动
python start_trading.py --strategy mean_reversion

# 交互式启动时选择: 1
```

---

### 2. 动量策略 (Momentum)

**策略代码**: `momentum`  
**适用场景**: 趋势市场、单边行情  
**核心原理**: 跟随价格动量方向

**关键参数**:
```yaml
strategies:
  momentum:
    enabled: true
    market_id: 0
    short_period: 5          # 短期均线周期
    long_period: 20          # 长期均线周期
    momentum_threshold: 0.02 # 动量阈值（2%）
    position_size: 0.1
    stop_loss: 0.03
    take_profit: 0.05
```

**使用方法**:
```bash
# 命令行启动
python start_trading.py --strategy momentum

# 交互式启动时选择: 2
```

---

### 3. 套利策略 (Arbitrage)

**策略代码**: `arbitrage`  
**适用场景**: 相关性强的交易对、跨市场套利  
**核心原理**: 捕捉不同市场间的价格差异

**关键参数**:
```yaml
strategies:
  arbitrage:
    enabled: true
    market_id_1: 0           # 市场1的ID
    market_id_2: 1           # 市场2的ID
    price_threshold: 0.01    # 价格差异阈值（1%）
    position_size: 0.02      # 仓位大小（建议较小）
    stop_loss: 0.005
    take_profit: 0.01
```

**使用方法**:
```bash
# 命令行启动
python start_trading.py --strategy arbitrage

# 交互式启动时选择: 3
```

---

### 4. UT Bot策略 (UT Bot / ATR追踪止损)

**策略代码**: `ut_bot`  
**适用场景**: 趋势跟踪、波动率交易  
**核心原理**: 基于ATR的动态追踪止损系统

**关键参数**:
```yaml
strategies:
  ut_bot:
    enabled: true
    market_id: 0
    key_value: 1.0           # 敏感度系数（越大越不敏感）
    atr_period: 10           # ATR计算周期
    use_heikin_ashi: false   # 是否使用Heikin Ashi蜡烛图
    position_size: 0.1
    stop_loss: 0.02
    take_profit: 0.01
```

**使用方法**:
```bash
# 命令行启动
python start_trading.py --strategy ut_bot

# 交互式启动时选择: 4
```

**特点**:
- 动态追踪止损，适应市场波动
- 基于TradingView UT Bot Alerts指标
- 支持Heikin Ashi平滑价格

---

## 多策略组合

### 启动所有策略

**使用方法**:
```bash
# 命令行启动
python start_trading.py --strategy all

# 交互式启动时选择: 5
```

### 自定义策略组合

编辑 `config.yaml`，启用需要的策略：

```yaml
strategies:
  mean_reversion:
    enabled: true    # ✅ 启用
  
  momentum:
    enabled: true    # ✅ 启用
  
  arbitrage:
    enabled: false   # ❌ 禁用
  
  ut_bot:
    enabled: true    # ✅ 启用
```

---

## 策略选择建议

### 测试网环境

建议先测试单一策略，观察表现后再组合：

```yaml
# 阶段1: 测试均值回归（1周）
mean_reversion:
  enabled: true
  position_size: 0.05  # 小仓位

# 阶段2: 测试动量（1周）
momentum:
  enabled: true
  position_size: 0.05

# 阶段3: 组合测试（2周）
mean_reversion:
  enabled: true
momentum:
  enabled: true
ut_bot:
  enabled: true
```

### 主网环境

**保守型**（推荐新手）:
```yaml
strategies:
  mean_reversion:
    enabled: true
    position_size: 0.03  # 3%仓位
```

**稳健型**:
```yaml
strategies:
  mean_reversion:
    enabled: true
    position_size: 0.05
  
  momentum:
    enabled: true
    position_size: 0.05
```

**积极型**（有经验用户）:
```yaml
strategies:
  mean_reversion:
    enabled: true
    position_size: 0.05
  
  momentum:
    enabled: true
    position_size: 0.05
  
  ut_bot:
    enabled: true
    position_size: 0.05
  
  arbitrage:
    enabled: true
    position_size: 0.02
```

---

## 策略对比

| 策略 | 市场类型 | 交易频率 | 风险级别 | 适合新手 |
|------|----------|----------|----------|----------|
| 均值回归 | 震荡 | 中等 | 中 | ✅ 是 |
| 动量 | 趋势 | 中等 | 中 | ✅ 是 |
| 套利 | 相关市场 | 高 | 低 | ⚠️ 需要理解 |
| UT Bot | 趋势 | 低 | 中-高 | ⚠️ 需要理解 |

---

## 快速启动命令

```bash
# 均值回归策略
python start_trading.py --strategy mean_reversion --market 0

# 动量策略
python start_trading.py --strategy momentum --market 0

# 套利策略
python start_trading.py --strategy arbitrage --market 0

# UT Bot策略
python start_trading.py --strategy ut_bot --market 0

# 所有策略
python start_trading.py --strategy all

# 模拟运行（不实际交易）
python start_trading.py --strategy mean_reversion --dry-run
```

---

## 回测命令

```bash
# 回测均值回归策略（30天）
python backtest.py --strategy mean_reversion --days 30

# 回测动量策略（60天）
python backtest.py --strategy momentum --days 60

# 回测套利策略（30天）
python backtest.py --strategy arbitrage --days 30

# 回测UT Bot策略（30天）
python backtest.py --strategy ut_bot --days 30

# 回测所有策略
python backtest.py --strategy all --days 30
```

---

## 策略示例代码

### 示例1: 使用均值回归策略

```python
from quant_trading import TradingEngine, Config
from quant_trading.strategies import MeanReversionStrategy

config = Config.from_file('config.yaml')
engine = TradingEngine(config)

strategy = MeanReversionStrategy(
    config=config,
    market_id=0,
    lookback_period=20,
    threshold=2.0
)

engine.add_strategy(strategy)
await engine.start()
```

### 示例2: 使用UT Bot策略

```python
from quant_trading import TradingEngine, Config
from quant_trading.strategies import UTBotStrategy

config = Config.from_file('config.yaml')
engine = TradingEngine(config)

strategy = UTBotStrategy(
    config=config,
    market_id=0,
    key_value=1.5,
    atr_period=14,
    use_heikin_ashi=False
)

engine.add_strategy(strategy)
await engine.start()
```

### 示例3: 多策略组合

```python
from quant_trading import TradingEngine, Config
from quant_trading.strategies import (
    MeanReversionStrategy,
    MomentumStrategy,
    UTBotStrategy
)

config = Config.from_file('config.yaml')
engine = TradingEngine(config)

# 添加多个策略
engine.add_strategy(MeanReversionStrategy(config, market_id=0))
engine.add_strategy(MomentumStrategy(config, market_id=0))
engine.add_strategy(UTBotStrategy(config, market_id=0))

await engine.start()
```

---

## 策略文件位置

```
quant_trading/strategies/
├── base_strategy.py         # 策略基类
├── mean_reversion.py        # 均值回归策略
├── momentum.py              # 动量策略
├── arbitrage.py             # 套利策略
└── ut_bot.py               # UT Bot策略
```

---

## 相关示例

项目提供了以下示例代码（位于 `examples/` 目录）：

- `simple_trading_bot.py` - 简单交易机器人示例
- `multi_strategy_bot.py` - 多策略机器人示例
- `ut_bot_strategy_example.py` - UT Bot策略详细示例
- `custom_strategy.py` - 自定义策略开发示例

---

## 更多信息

- [参数配置手册](PARAMETER_CONFIG_MANUAL.md#策略配置)
- [执行手册](EXECUTION_MANUAL.md#策略管理)
- [手册总览](README_MANUALS.md)

---

**文档版本**: v1.0.0  
**最后更新**: 2024年10月  
**维护者**: Quant Trading Team

