# Lighter量化交易程序

基于Lighter交易所API的量化交易系统，支持多种交易策略、风险管理和回测功能。

## 功能特性

- 🚀 **多种交易策略**: 均值回归、动量、套利、UT Bot等策略
- 🛡️ **风险管理**: 仓位控制、止损止盈、风险监控
- 📊 **多数据源支持**: Lighter交易所、TradingView等数据源
- 🔄 **回测系统**: 历史数据回测和性能分析
- ⚙️ **配置管理**: 灵活的配置系统和参数调整
- 📝 **日志监控**: 完整的日志记录和监控

## 项目结构

```
quant_trading/
├── core/                    # 核心模块
│   ├── trading_engine.py   # 交易引擎
│   ├── data_manager.py     # 数据管理器
│   ├── risk_manager.py     # 风险管理器
│   ├── position_manager.py # 仓位管理器
│   └── order_manager.py    # 订单管理器
├── strategies/              # 交易策略
│   ├── base_strategy.py    # 策略基类
│   ├── mean_reversion.py   # 均值回归策略
│   ├── momentum.py         # 动量策略
│   ├── arbitrage.py        # 套利策略
│   └── ut_bot.py          # UT Bot策略
├── data_sources/           # 数据源模块
│   ├── base_data_source.py # 数据源基类
│   ├── lighter_data_source.py # Lighter数据源
│   └── tradingview_data_source.py # TradingView数据源
├── backtesting/            # 回测模块
│   ├── backtest_engine.py  # 回测引擎
│   └── backtest_result.py  # 回测结果
├── utils/                  # 工具模块
│   ├── config.py          # 配置管理
│   ├── logger.py          # 日志管理
│   ├── data_utils.py      # 数据处理工具
│   └── math_utils.py      # 数学工具
└── __init__.py
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置设置

1. 复制配置文件模板：
```bash
cp config.yaml.example config.yaml
```

2. 编辑 `config.yaml` 文件，配置Lighter交易所参数：
```yaml
lighter:
  base_url: "https://testnet.zklighter.elliot.ai"  # 或主网地址
  api_key_private_key: "your_api_key_private_key"
  account_index: 0
  api_key_index: 0
```

## 使用方法

### 1. 实盘交易

运行主程序：
```bash
python main.py --strategy mean_reversion --market 0
```

参数说明：
- `--strategy`: 策略类型 (mean_reversion, momentum, arbitrage, ut_bot, all)
- `--market`: 市场ID
- `--config`: 配置文件路径
- `--dry-run`: 模拟运行模式

### 2. 回测

运行回测程序：
```bash
python backtest.py --strategy mean_reversion --days 30
```

参数说明：
- `--strategy`: 策略类型
- `--days`: 回测天数
- `--config`: 配置文件路径

## 策略说明

### 均值回归策略 (Mean Reversion)
- 基于价格偏离均值的策略
- 当价格偏离均值超过阈值时开仓
- 适合震荡市场

### 动量策略 (Momentum)
- 基于价格动量的策略
- 跟随趋势方向开仓
- 适合趋势市场

### 套利策略 (Arbitrage)
- 基于不同市场间价格差异的策略
- 同时在两个市场进行相反操作
- 适合价格差异较大的市场

### UT Bot策略 (UT Bot)
- 基于TradingView UT Bot Alerts的策略
- 使用ATR追踪止损机制
- 支持Heikin Ashi蜡烛图
- 适合趋势跟踪交易

## 风险管理

系统内置多种风险管理功能：

- **仓位控制**: 限制单个仓位的最大比例
- **日亏损限制**: 控制每日最大亏损
- **回撤控制**: 限制最大回撤幅度
- **订单频率限制**: 防止过度交易
- **杠杆控制**: 限制最大杠杆倍数

## 配置参数

### 交易配置
```yaml
trading:
  tick_interval: 1.0  # 主循环间隔（秒）
  max_concurrent_strategies: 5  # 最大并发策略数
```

### 风险配置
```yaml
risk:
  max_position_size: 0.1  # 最大仓位比例
  max_daily_loss: 0.05    # 最大日亏损比例
  max_drawdown: 0.15      # 最大回撤比例
  max_leverage: 10.0      # 最大杠杆倍数
```

### 数据源配置
```yaml
data_sources:
  primary: "lighter"  # 主数据源: lighter, tradingview
  tradingview:
    enabled: true  # 是否启用TradingView数据源
    session_id: "qs_1"
    user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    symbol_mapping:  # 交易对映射
      "BTC_USDT": "BTCUSDT"
      "ETH_USDT": "ETHUSDT"
```

### 策略配置
```yaml
strategies:
  mean_reversion:
    enabled: true
    market_id: 0
    lookback_period: 20
    threshold: 2.0
    position_size: 0.1
    stop_loss: 0.02
    take_profit: 0.01
    
  ut_bot:
    enabled: true
    market_id: 0
    key_value: 1.0
    atr_period: 10
    use_heikin_ashi: false
    position_size: 0.1
    stop_loss: 0.02
    take_profit: 0.01
```

## 日志监控

系统提供完整的日志记录功能：

- **控制台输出**: 实时显示交易状态
- **文件记录**: 保存详细日志到文件
- **日志级别**: 支持DEBUG、INFO、WARNING、ERROR级别

## 回测功能

回测系统支持：

- **历史数据回测**: 使用历史数据测试策略
- **性能指标**: 计算收益率、夏普比率、最大回撤等
- **可视化**: 生成权益曲线和回撤图表
- **交易分析**: 详细的交易记录和分析

## 注意事项

1. **测试环境**: 建议先在测试网环境测试
2. **风险控制**: 合理设置风险参数，避免过度风险
3. **资金管理**: 不要投入超过承受能力的资金
4. **策略监控**: 定期检查策略表现，及时调整参数
5. **网络稳定**: 确保网络连接稳定，避免断线影响交易

## 开发扩展

### 添加新策略

1. 继承 `BaseStrategy` 类
2. 实现必要的方法：
   - `on_initialize()`
   - `on_start()`
   - `on_stop()`
   - `process_market_data()`

示例：
```python
class MyStrategy(BaseStrategy):
    def __init__(self, config: Config):
        super().__init__("MyStrategy", config)
    
    async def on_initialize(self):
        # 初始化逻辑
        pass
    
    async def process_market_data(self, market_data):
        # 策略逻辑
        pass
```

### 添加新指标

在 `utils/data_utils.py` 中添加新的技术指标计算方法。

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交Issue或联系开发团队。
