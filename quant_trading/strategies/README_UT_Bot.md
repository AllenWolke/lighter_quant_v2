# UT Bot策略

基于UT Bot Alerts指标的量化交易策略，从TradingView Pine Script翻译而来。

## 策略概述

UT Bot策略是一个趋势跟踪策略，使用UT Bot Alerts指标作为主要交易信号源，结合200周期EMA进行趋势过滤，通过ATR动态止损和盈亏比管理来实现风险控制。

## 核心特性

### 1. UT Bot Alerts指标
- **动态止损线**: 基于ATR的自适应止损机制
- **趋势跟踪**: 价格突破止损线时产生交易信号
- **自适应调整**: 止损线根据价格波动自动调整

### 2. 趋势过滤
- **200周期EMA**: 确保只在趋势方向交易
- **多头过滤**: 只在价格高于EMA时做多
- **空头过滤**: 只在价格低于EMA时做空

### 3. 风险管理
- **ATR止损**: 基于平均真实波幅的止损设置
- **摆动止损**: 基于摆动高低点的止损设置
- **盈亏比管理**: 1:3的风险回报比
- **分批止盈**: 50%仓位在第一个止盈点平仓

### 4. 资金管理
- **风险控制**: 每笔交易风险2.5%
- **仓位计算**: 基于风险金额和止损距离动态计算
- **杠杆支持**: 可配置杠杆倍数

## 策略参数

### UT Bot Alerts参数
```yaml
key_value: 3.0          # 关键值，控制止损距离倍数
atr_period: 1           # ATR计算周期
use_heikin_ashi: false  # 是否使用Heikin Ashi蜡烛图
```

### 趋势过滤参数
```yaml
ema_length: 200         # EMA长度，用于趋势过滤
```

### 风险管理参数
```yaml
risk_per_trade: 2.5     # 每笔交易风险百分比
atr_multiplier: 1.5     # ATR止损倍数
risk_reward_breakeven: 0.75  # 保本盈亏比
risk_reward_takeprofit: 3.0  # 止盈盈亏比
tp_percent: 50.0        # 第一批止盈百分比
```

### 止损类型
```yaml
stoploss_type: "atr"    # "atr" 或 "swing"
swing_high_bars: 10     # 摆动高点周期
swing_low_bars: 10      # 摆动低点周期
```

## 使用方法

### 1. 基本使用
```python
from quant_trading.strategies.ut_bot_strategy import UTBotStrategy, UTBotConfig
from quant_trading.utils.config import Config

# 创建配置
config = Config()
ut_config = UTBotConfig()

# 创建策略
strategy = UTBotStrategy("UT_Bot_Strategy", config, ut_config)

# 初始化和启动
await strategy.initialize()
await strategy.start()

# 处理市场数据
await strategy.process_market_data(market_data)
```

### 2. 自定义配置
```python
# 自定义UT Bot配置
ut_config = UTBotConfig(
    key_value=2.5,           # 更保守的关键值
    atr_period=2,            # 更长的ATR周期
    ema_length=100,          # 更短的EMA周期
    risk_per_trade=1.5,      # 更小的风险比例
    atr_multiplier=2.0,      # 更大的ATR倍数
    stoploss_type="swing"    # 使用摆动止损
)

strategy = UTBotStrategy("Custom_UT_Bot", config, ut_config)
```

### 3. 运行示例
```bash
# 运行策略示例
python quant_trading/strategies/ut_bot_example.py
```

## 交易信号

### 买入信号
- 价格突破ATR动态止损线上方
- 价格高于200周期EMA（多头趋势）
- 发生向上交叉

### 卖出信号
- 价格跌破ATR动态止损线下方
- 价格低于200周期EMA（空头趋势）
- 发生向下交叉

### 平仓信号
- 盈利时出现反向信号
- 达到止损价格
- 达到止盈价格

## 风险控制

### 1. 止损机制
- **ATR止损**: 基于ATR的固定倍数止损
- **摆动止损**: 基于最近摆动高低点止损
- **保本移动**: 达到保本点后移动止损到成本价

### 2. 仓位管理
- **风险控制**: 每笔交易最大风险2.5%
- **仓位计算**: 基于风险金额和止损距离
- **杠杆限制**: 可配置最大杠杆倍数

### 3. 时间过滤
- **交易时段**: 可限制在特定时间段交易
- **日期范围**: 可设置策略运行时间范围

## 性能优化

### 1. 指标计算优化
- 使用numpy进行向量化计算
- 缓存计算结果避免重复计算
- 限制历史数据长度

### 2. 内存管理
- 限制市场数据历史长度（1000个数据点）
- 定期清理过期数据
- 使用高效的数据结构

### 3. 并发处理
- 异步处理市场数据
- 并行处理多个市场
- 非阻塞订单执行

## 监控和调试

### 1. 日志记录
```python
# 启用详细日志
strategy.logger.setLevel(logging.DEBUG)

# 查看策略状态
status = strategy.get_strategy_status()
print(f"信号数量: {status['signals_generated']}")
print(f"交易数量: {status['trades_executed']}")
```

### 2. 性能指标
- 信号生成频率
- 交易执行成功率
- 平均持仓时间
- 最大回撤

### 3. 风险监控
- 实时仓位监控
- 止损止盈状态
- 风险暴露度

## 注意事项

1. **数据质量**: 确保市场数据的准确性和及时性
2. **参数调优**: 根据市场特点调整策略参数
3. **风险控制**: 严格执行风险控制规则
4. **回测验证**: 在实盘前进行充分的回测验证
5. **监控告警**: 设置适当的监控和告警机制

## 扩展功能

### 1. 多市场支持
- 支持同时交易多个市场
- 独立的风险控制
- 统一的信号管理

### 2. 策略组合
- 可与其他策略组合使用
- 权重分配和信号融合
- 风险分散

### 3. 机器学习集成
- 参数自动优化
- 信号质量评估
- 市场状态识别

## 版本历史

- **v1.0.0**: 初始版本，实现基本UT Bot策略功能
- 支持ATR和摆动止损
- 支持多空双向交易
- 集成风险管理系统
