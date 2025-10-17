# Lighter量化交易模块 - 参数配置手册

## 📋 目录

- [概述](#概述)
- [配置文件结构](#配置文件结构)
- [Lighter交易所配置](#lighter交易所配置)
- [交易配置](#交易配置)
- [风险管理配置](#风险管理配置)
- [数据源配置](#数据源配置)
- [通知配置](#通知配置)
- [策略配置](#策略配置)
- [日志配置](#日志配置)
- [配置示例](#配置示例)

---

## 概述

本手册详细说明Lighter量化交易模块的所有配置参数。配置文件采用YAML格式，包含交易所连接、策略参数、风险控制等核心配置。

### 配置文件位置

- **主配置文件**: `config.yaml`
- **示例配置**: `config.yaml.example`
- **测试网配置**: `config_linux_testnet.yaml` / `config_windows_testnet.yaml`
- **主网配置**: `config_mainnet.yaml` / `config_linux_mainnet.yaml`

---

## 配置文件结构

```yaml
lighter:              # Lighter交易所配置
trading:              # 交易配置
risk_management:      # 风险管理配置
data_sources:         # 数据源配置
notifications:        # 通知配置
strategies:           # 策略配置
log:                  # 日志配置
```

---

## Lighter交易所配置

### 基础参数

```yaml
lighter:
  base_url: "https://testnet.zklighter.elliot.ai"  # 交易所API地址
  api_key_private_key: "YOUR_PRIVATE_KEY_HERE"     # API密钥私钥
  account_index: 0                                  # 账户索引
  api_key_index: 0                                  # API密钥索引
  chain_id: 304                                     # 链ID（测试网：302，主网：304）
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `base_url` | string | ✅ | 交易所API基础URL |
| `api_key_private_key` | string | ✅ | 64位十六进制私钥（无0x前缀） |
| `account_index` | integer | ✅ | 账户索引，默认为0 |
| `api_key_index` | integer | ✅ | API密钥索引，默认为0 |
| `chain_id` | integer | ⚠️ | 区块链ID，测试网302，主网304 |

### 环境选择

#### 测试网配置
```yaml
lighter:
  base_url: "https://testnet.zklighter.elliot.ai"
  chain_id: 302
```

#### 主网配置
```yaml
lighter:
  base_url: "https://mainnet.zklighter.elliot.ai"
  chain_id: 304
```

⚠️ **重要提示**: 主网配置需要真实资金，请谨慎使用！

---

## 交易配置

```yaml
trading:
  tick_interval: 1.0              # 主循环执行间隔（秒）
  max_concurrent_strategies: 5    # 最大并发策略数量
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `tick_interval` | float | 1.0 | 策略执行周期，单位秒 |
| `max_concurrent_strategies` | integer | 5 | 同时运行的最大策略数 |

### 推荐配置

| 场景 | tick_interval | 说明 |
|------|---------------|------|
| 高频交易 | 0.5 - 1.0 | 需要更好的网络和性能 |
| 中频交易 | 1.0 - 3.0 | 平衡性能和成本 |
| 低频交易 | 3.0 - 10.0 | 适合趋势跟踪策略 |
| 主网交易 | ≥ 3.0 | 避免API限流 |

---

## 风险管理配置

```yaml
risk_management:
  max_position_size: 0.1         # 最大仓位比例（10%）
  max_daily_loss: 0.05           # 最大日亏损比例（5%）
  max_drawdown: 0.15             # 最大回撤比例（15%）
  max_leverage: 10.0             # 最大杠杆倍数
  max_orders_per_minute: 10      # 每分钟最大订单数
  max_open_orders: 20            # 最大未成交订单数
  stop_loss_percent: 0.02        # 全局止损百分比（2%）
  take_profit_percent: 0.05      # 全局止盈百分比（5%）
```

### 参数详解

| 参数 | 类型 | 范围 | 说明 |
|------|------|------|------|
| `max_position_size` | float | 0.01-1.0 | 单个仓位占总资金比例 |
| `max_daily_loss` | float | 0.01-0.5 | 单日最大亏损占总资金比例 |
| `max_drawdown` | float | 0.05-0.5 | 最大回撤占峰值资金比例 |
| `max_leverage` | float | 1.0-100.0 | 最大杠杆倍数 |
| `max_orders_per_minute` | integer | 1-100 | 每分钟最大下单次数 |
| `max_open_orders` | integer | 1-100 | 同时存在的最大未成交订单 |
| `stop_loss_percent` | float | 0.01-0.5 | 全局止损触发百分比 |
| `take_profit_percent` | float | 0.01-1.0 | 全局止盈触发百分比 |

### 风险等级推荐

#### 保守型（推荐主网使用）
```yaml
risk_management:
  max_position_size: 0.05        # 5%仓位
  max_daily_loss: 0.02           # 2%日亏损
  max_drawdown: 0.10             # 10%回撤
  max_leverage: 3.0              # 3倍杠杆
  max_orders_per_minute: 5
  max_open_orders: 10
```

#### 稳健型
```yaml
risk_management:
  max_position_size: 0.10        # 10%仓位
  max_daily_loss: 0.05           # 5%日亏损
  max_drawdown: 0.15             # 15%回撤
  max_leverage: 5.0              # 5倍杠杆
  max_orders_per_minute: 10
  max_open_orders: 20
```

#### 激进型（仅测试网）
```yaml
risk_management:
  max_position_size: 0.20        # 20%仓位
  max_daily_loss: 0.10           # 10%日亏损
  max_drawdown: 0.30             # 30%回撤
  max_leverage: 10.0             # 10倍杠杆
  max_orders_per_minute: 20
  max_open_orders: 50
```

---

## 数据源配置

```yaml
data_sources:
  primary: "lighter"              # 主数据源：lighter, tradingview
  
  # TradingView数据源配置（可选）
  tradingview:
    enabled: true                 # 是否启用
    session_id: "qs_1"           # 会话ID
    user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    symbol_mapping:               # 交易对映射
      "BTC_USDT": "BTCUSDT"
      "ETH_USDT": "ETHUSDT"
      "SOL_USDT": "SOLUSDT"
```

### 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| `primary` | string | 主数据源选择：lighter或tradingview |
| `tradingview.enabled` | boolean | 是否启用TradingView数据源 |
| `tradingview.session_id` | string | TradingView会话标识 |
| `tradingview.user_agent` | string | HTTP请求User-Agent |
| `tradingview.symbol_mapping` | dict | Lighter到TradingView的交易对映射 |

---

## 通知配置

```yaml
notifications:
  enabled: true                   # 是否启用通知
  batch_size: 5                   # 批量发送大小
  batch_interval: 60              # 批量发送间隔（秒）
  
  # 频率限制
  rate_limits:
    trade_executed:               # 交易执行通知
      time_window: 300            # 时间窗口（秒）
      max_count: 20               # 最大次数
    stop_loss:                    # 止损通知
      time_window: 300
      max_count: 10
    take_profit:                  # 止盈通知
      time_window: 300
      max_count: 10
    system_error:                 # 系统错误通知
      time_window: 60
      max_count: 5
  
  # 邮件通知配置
  email:
    enabled: true                 # 是否启用邮件通知
    smtp_server: "smtp.gmail.com" # SMTP服务器
    smtp_port: 587                # SMTP端口
    username: "your@email.com"    # 邮箱账号
    password: "your_password"     # 邮箱密码或应用密码
    from_email: "your@email.com"  # 发件人邮箱
    to_emails:                    # 收件人列表
      - "recipient1@email.com"
      - "recipient2@email.com"
    min_level: "info"             # 最小通知级别：debug, info, warning, error
    allowed_types: []             # 允许的通知类型，空表示全部
```

### 通知类型

- `trade_executed`: 交易成功执行
- `stop_loss`: 止损触发
- `take_profit`: 止盈触发
- `position_opened`: 开仓
- `position_closed`: 平仓
- `risk_limit_exceeded`: 风险限制触发
- `system_error`: 系统错误
- `strategy_started`: 策略启动
- `strategy_stopped`: 策略停止

### 常用SMTP服务器配置

#### Gmail
```yaml
email:
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
  username: "your@gmail.com"
  password: "your_app_password"  # 需要使用应用专用密码
```

#### Outlook/Hotmail
```yaml
email:
  smtp_server: "smtp-mail.outlook.com"
  smtp_port: 587
  username: "your@outlook.com"
  password: "your_password"
```

#### QQ邮箱
```yaml
email:
  smtp_server: "smtp.qq.com"
  smtp_port: 587
  username: "your@qq.com"
  password: "your_auth_code"  # 需要使用授权码
```

---

## 策略配置

### 均值回归策略 (Mean Reversion)

```yaml
strategies:
  mean_reversion:
    enabled: true                # 是否启用
    market_id: 0                 # 市场ID
    lookback_period: 20          # 回望周期
    threshold: 2.0               # Z分数阈值
    position_size: 0.1           # 仓位大小
    stop_loss: 0.02              # 止损比例
    take_profit: 0.01            # 止盈比例
```

**参数说明**:
- `lookback_period`: 计算均值和标准差的K线数量，建议20-50
- `threshold`: Z分数阈值，价格偏离均值的标准差倍数，建议1.5-3.0
- `position_size`: 单次开仓占账户总资金的比例
- `stop_loss`: 止损百分比，相对于开仓价格
- `take_profit`: 止盈百分比，相对于开仓价格

**适用场景**: 震荡市场、区间交易

---

### 动量策略 (Momentum)

```yaml
strategies:
  momentum:
    enabled: true                # 是否启用
    market_id: 0                 # 市场ID
    short_period: 5              # 短期均线周期
    long_period: 20              # 长期均线周期
    momentum_threshold: 0.02     # 动量阈值
    position_size: 0.1           # 仓位大小
    stop_loss: 0.03              # 止损比例
    take_profit: 0.05            # 止盈比例
```

**参数说明**:
- `short_period`: 短期移动平均周期，建议5-10
- `long_period`: 长期移动平均周期，建议20-50
- `momentum_threshold`: 动量阈值，短期均线与长期均线的差异比例
- 其他参数同均值回归策略

**适用场景**: 趋势市场、单边行情

---

### 套利策略 (Arbitrage)

```yaml
strategies:
  arbitrage:
    enabled: true                # 是否启用
    market_id_1: 0               # 市场1 ID
    market_id_2: 1               # 市场2 ID
    price_threshold: 0.01        # 价格差异阈值
    position_size: 0.02          # 仓位大小
    stop_loss: 0.005             # 止损比例
    take_profit: 0.01            # 止盈比例
```

**参数说明**:
- `market_id_1`, `market_id_2`: 两个相关市场的ID
- `price_threshold`: 触发套利的价格差异百分比
- `position_size`: 建议较小，因为同时在两个市场开仓
- 其他参数同均值回归策略

**适用场景**: 相关性强的交易对、跨市场套利

---

### UT Bot策略 (ATR追踪止损)

```yaml
strategies:
  ut_bot:
    enabled: true                # 是否启用
    market_id: 0                 # 市场ID
    key_value: 1.0               # 敏感度参数
    atr_period: 10               # ATR周期
    use_heikin_ashi: false       # 是否使用Heikin Ashi蜡烛图
    position_size: 0.1           # 仓位大小
    stop_loss: 0.02              # 止损比例
    take_profit: 0.01            # 止盈比例
```

**参数说明**:
- `key_value`: 敏感度系数，数值越大越不敏感，建议1.0-3.0
- `atr_period`: ATR计算周期，建议10-20
- `use_heikin_ashi`: 是否使用平滑的Heikin Ashi蜡烛图
- 其他参数同均值回归策略

**适用场景**: 趋势跟踪、波动率交易

---

## 日志配置

```yaml
log:
  level: "INFO"                  # 日志级别
  file: "logs/quant_trading.log" # 日志文件路径
```

### 日志级别

| 级别 | 说明 | 使用场景 |
|------|------|----------|
| `DEBUG` | 详细调试信息 | 开发调试、问题排查 |
| `INFO` | 一般信息 | 正常运行监控 |
| `WARNING` | 警告信息 | 潜在问题提示 |
| `ERROR` | 错误信息 | 错误记录 |

**推荐配置**:
- 开发/测试: `DEBUG`
- 生产环境: `INFO`
- 仅关注问题: `WARNING`

---

## 配置示例

### 完整测试网配置

```yaml
# 测试网完整配置示例
lighter:
  base_url: "https://testnet.zklighter.elliot.ai"
  api_key_private_key: "your_64_char_hex_private_key"
  account_index: 0
  api_key_index: 0
  chain_id: 302

trading:
  tick_interval: 1.0
  max_concurrent_strategies: 3

risk_management:
  max_position_size: 0.10
  max_daily_loss: 0.05
  max_drawdown: 0.15
  max_leverage: 5.0
  max_orders_per_minute: 10
  max_open_orders: 20
  stop_loss_percent: 0.02
  take_profit_percent: 0.05

log:
  level: "INFO"
  file: "logs/quant_trading.log"

data_sources:
  primary: "lighter"

notifications:
  enabled: true
  email:
    enabled: false  # 测试时可以关闭

strategies:
  mean_reversion:
    enabled: true
    market_id: 0
    lookback_period: 20
    threshold: 2.0
    position_size: 0.1
    stop_loss: 0.02
    take_profit: 0.01
```

### 完整主网配置（保守型）

```yaml
# 主网保守型配置示例
lighter:
  base_url: "https://mainnet.zklighter.elliot.ai"
  api_key_private_key: "your_64_char_hex_private_key"
  account_index: 0
  api_key_index: 0
  chain_id: 304

trading:
  tick_interval: 3.0  # 主网使用较长间隔避免限流
  max_concurrent_strategies: 2

risk_management:
  max_position_size: 0.05   # 保守仓位
  max_daily_loss: 0.02      # 严格止损
  max_drawdown: 0.10        # 控制回撤
  max_leverage: 3.0         # 低杠杆
  max_orders_per_minute: 5  # 降低频率
  max_open_orders: 10
  stop_loss_percent: 0.02
  take_profit_percent: 0.05

log:
  level: "INFO"
  file: "logs/quant_trading_mainnet.log"

data_sources:
  primary: "lighter"

notifications:
  enabled: true
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    username: "your@gmail.com"
    password: "your_app_password"
    from_email: "your@gmail.com"
    to_emails:
      - "your@gmail.com"
    min_level: "info"

strategies:
  ut_bot:
    enabled: true
    market_id: 0
    key_value: 1.5
    atr_period: 14
    use_heikin_ashi: false
    position_size: 0.05
    stop_loss: 0.02
    take_profit: 0.03
```

---

## 配置验证

### 使用配置检查工具

```bash
# 检查配置文件有效性
python check_config.py

# 检查依赖项
python check_dependencies.py
```

### 手动验证清单

- [ ] Lighter私钥格式正确（64位十六进制，无0x前缀）
- [ ] 网络地址与chain_id匹配
- [ ] 风险参数在合理范围内
- [ ] 日志目录存在且可写
- [ ] 邮件配置正确（如启用）
- [ ] 策略参数符合市场特性

---

## 常见配置问题

### 1. 私钥格式错误

**错误**: `Invalid private key format`

**解决**: 确保私钥是64位十六进制字符串，不包含`0x`前缀

```yaml
# ❌ 错误
api_key_private_key: "0x1234..."

# ✅ 正确
api_key_private_key: "1234567890abcdef..."
```

### 2. 网络不匹配

**错误**: `Chain ID mismatch`

**解决**: 确保base_url和chain_id匹配
- 测试网: `chain_id: 302`
- 主网: `chain_id: 304`

### 3. 风险参数过大

**警告**: `Risk parameters too aggressive`

**解决**: 调整风险参数至推荐范围内，特别是主网环境

### 4. 邮件发送失败

**错误**: `SMTP authentication failed`

**解决**:
- Gmail: 使用应用专用密码，而非账户密码
- QQ邮箱: 使用授权码
- 检查SMTP服务器和端口配置

---

## 最佳实践

1. **分环境配置**: 测试网和主网使用不同的配置文件
2. **版本控制**: 使用git管理配置文件，但排除包含私钥的文件
3. **敏感信息**: 不要将私钥提交到代码仓库
4. **备份配置**: 定期备份配置文件
5. **渐进调整**: 参数调整应小步迭代，观察效果后再继续
6. **监控日志**: 配置更改后密切监控日志输出
7. **回测验证**: 新策略参数先在回测系统中验证

---

## 相关文档

- [部署手册](DEPLOYMENT_MANUAL.md)
- [执行手册](EXECUTION_MANUAL.md)
- [策略开发指南](../docs/strategy_development.md)

---

**文档版本**: v1.0.0  
**最后更新**: 2024年  
**维护者**: Quant Trading Team

