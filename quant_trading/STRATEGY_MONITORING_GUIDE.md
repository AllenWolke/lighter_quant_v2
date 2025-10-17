# 策略执行监控与交易确认指南

## 📋 目录

- [监控方法](#监控方法)
- [日志查看](#日志查看)
- [交易信号识别](#交易信号识别)
- [实时监控](#实时监控)
- [性能追踪](#性能追踪)
- [常见问题](#常见问题)

---

## 监控方法

### 方法一：查看日志文件 ⭐ 推荐

日志文件是最可靠的监控方式，包含所有策略执行和交易的详细信息。

**日志位置**:
```
logs/quant_trading.log
```

**查看日志**:
```bash
# Windows
type logs\quant_trading.log

# Linux/macOS
cat logs/quant_trading.log

# 实时监控（推荐）
# Windows PowerShell
Get-Content logs\quant_trading.log -Wait -Tail 50

# Linux/macOS
tail -f logs/quant_trading.log

# 只看最近50行
tail -50 logs/quant_trading.log
```

---

### 方法二：控制台输出

运行策略时，控制台会实时显示关键信息。

**启动时看到**:
```
============================================================
Lighter量化交易程序
============================================================

请配置Lighter交易所参数:
...
✅ 已添加均值回归策略
🚀 启动交易引擎...
按 Ctrl+C 停止程序
```

**运行时输出**:
```
2024-10-09 14:23:15 - TradingEngine - INFO - 启动交易引擎...
2024-10-09 14:23:16 - Strategy_MeanReversion - INFO - 初始化策略: 市场 0
2024-10-09 14:23:17 - TradingEngine - INFO - 进入主循环...
2024-10-09 14:23:20 - Strategy_MeanReversion - INFO - 交易信号: LONG, 市场 0, {...}
```

---

### 方法三：检查交易历史

通过 Lighter 交易所查看实际的交易记录。

**Web界面** (如果启用):
```
http://localhost:8000/api/orders
http://localhost:8000/api/positions
http://localhost:8000/api/trades
```

---

## 日志查看

### 日志格式

```
时间戳 - 模块名称 - 级别 - 消息内容
```

**示例**:
```
2024-10-09 14:23:15 - Strategy_MeanReversion - INFO - 交易信号: LONG, 市场 0, {'price': 1234.5, 'z_score': -2.5, 'size': 0.1}
```

### 日志级别

| 级别 | 说明 | 何时出现 |
|------|------|----------|
| DEBUG | 调试信息 | 详细的运行细节 |
| INFO | 一般信息 | 策略信号、交易执行 |
| WARNING | 警告信息 | 风险限制、异常情况 |
| ERROR | 错误信息 | 交易失败、系统错误 |

### 关键日志类型

#### 1. 策略初始化
```
2024-10-09 14:23:16 - Strategy_MeanReversion - INFO - 初始化均值回归策略: 市场 0, 回望周期 20, 阈值 2.0
2024-10-09 14:23:16 - Strategy_MeanReversion - INFO - 均值回归策略已启动
```

#### 2. 交易信号 ⭐ 重要
```
# 做多信号
2024-10-09 14:25:30 - Strategy_MeanReversion - INFO - 交易信号: LONG, 市场 0, {'price': 1234.5, 'z_score': -2.5, 'size': 0.1}

# 做空信号
2024-10-09 14:30:45 - Strategy_MeanReversion - INFO - 交易信号: SHORT, 市场 0, {'price': 1245.2, 'z_score': 2.8, 'size': 0.1}

# 平仓信号
2024-10-09 14:35:20 - Strategy_MeanReversion - INFO - 交易信号: EXIT, 市场 0, {'reason': '止盈', 'pnl_ratio': 0.015}
```

#### 3. 风险检查
```
# 通过风险检查
2024-10-09 14:25:29 - RiskManager - INFO - 风险检查通过

# 风险限制触发
2024-10-09 15:30:15 - RiskManager - WARNING - 日亏损限制触发: 3.2% > 2.0%
2024-10-09 15:30:15 - TradingEngine - WARNING - 风险检查失败，跳过本次交易
```

#### 4. 订单执行
```
# 订单创建
2024-10-09 14:25:31 - OrderManager - INFO - 创建订单: 市场 0, BUY, 数量 0.1

# 订单成交
2024-10-09 14:25:32 - OrderManager - INFO - 订单已成交: 订单ID xxx, 成交价 1234.5

# 订单失败
2024-10-09 14:26:10 - OrderManager - ERROR - 订单被拒绝: 余额不足
```

#### 5. 记录交易
```
2024-10-09 14:35:21 - Strategy_MeanReversion - INFO - 记录交易: 盈亏 15.5, 总盈亏 125.8
```

---

## 交易信号识别

### 各策略的交易信号

#### 均值回归策略 (Mean Reversion)

**做多信号** - 价格过低：
```
交易信号: LONG, 市场 0, {'price': 1234.5, 'z_score': -2.5, 'size': 0.1}
```
- `z_score < -threshold`: 价格低于均值超过阈值，预期回升

**做空信号** - 价格过高：
```
交易信号: SHORT, 市场 0, {'price': 1245.2, 'z_score': 2.8, 'size': 0.1}
```
- `z_score > threshold`: 价格高于均值超过阈值，预期回落

**平仓信号**：
```
交易信号: EXIT, 市场 0, {'reason': '止盈', 'pnl_ratio': 0.015}
交易信号: EXIT, 市场 0, {'reason': '止损', 'pnl_ratio': -0.022}
```

---

#### 动量策略 (Momentum)

**做多信号** - 正向动量：
```
交易信号: LONG, 市场 0, {'price': 1234.5, 'momentum': 0.025, 'size': 0.1}
```
- `momentum > momentum_threshold`: 短期均线上穿长期均线

**做空信号** - 负向动量：
```
交易信号: SHORT, 市场 0, {'price': 1245.2, 'momentum': -0.028, 'size': 0.1}
```
- `momentum < -momentum_threshold`: 短期均线下穿长期均线

**平仓信号**：
```
交易信号: EXIT, 市场 0, {'reason': '动量反转', 'pnl_ratio': 0.008, 'momentum': -0.015}
交易信号: EXIT, 市场 0, {'reason': '止盈', 'pnl_ratio': 0.052}
交易信号: EXIT, 市场 0, {'reason': '止损', 'pnl_ratio': -0.031}
```

---

#### UT Bot 策略

**做多信号** - 价格突破追踪止损线：
```
交易信号: LONG, 市场 0, {'price': 1234.5, 'trailing_stop': 1220.3, 'size': 0.1}
```

**做空信号** - 价格跌破追踪止损线：
```
交易信号: SHORT, 市场 0, {'price': 1245.2, 'trailing_stop': 1258.7, 'size': 0.1}
```

**平仓信号**：
```
交易信号: EXIT, 市场 0, {'reason': '多头信号平空', 'price': 1234.5, 'trailing_stop': 1220.3}
交易信号: EXIT, 市场 0, {'reason': '空头信号平多', 'price': 1245.2, 'trailing_stop': 1258.7}
```

---

#### 套利策略 (Arbitrage)

**开仓信号**：
```
交易信号: ARBITRAGE_OPEN, arbitrage_0_1, {'short_market': 0, 'long_market': 1, 'short_price': 1245.0, 'long_price': 1230.0, 'price_diff': 0.012}
```
- 在价格高的市场做空，价格低的市场做多

**平仓信号**：
```
交易信号: ARBITRAGE_CLOSE, arbitrage_0_1, {'reason': '价格收敛', 'pnl': 15.5}
交易信号: ARBITRAGE_CLOSE, arbitrage_0_1, {'reason': '止损', 'pnl': -5.2}
```

---

## 实时监控

### 使用终端实时查看日志

**Linux/macOS**:
```bash
# 打开新终端窗口
# 窗口1: 运行程序
python start_trading.py

# 窗口2: 实时监控日志
tail -f logs/quant_trading.log

# 窗口3: 只看交易信号
tail -f logs/quant_trading.log | grep "交易信号"

# 窗口4: 只看错误
tail -f logs/quant_trading.log | grep "ERROR"
```

**Windows PowerShell**:
```powershell
# 窗口1: 运行程序
python start_trading.py

# 窗口2: 实时监控日志
Get-Content logs\quant_trading.log -Wait -Tail 50

# 只看交易信号
Get-Content logs\quant_trading.log -Wait | Select-String "交易信号"
```

### 监控脚本

创建 `monitor.sh` (Linux/macOS):
```bash
#!/bin/bash

echo "=== 实时监控量化交易系统 ==="
echo ""
echo "监控日志文件: logs/quant_trading.log"
echo "按 Ctrl+C 停止监控"
echo ""
echo "----------------------------------------"

tail -f logs/quant_trading.log | while read line; do
    # 高亮显示交易信号
    if echo "$line" | grep -q "交易信号"; then
        echo -e "\033[1;32m$line\033[0m"  # 绿色
    # 高亮显示错误
    elif echo "$line" | grep -q "ERROR"; then
        echo -e "\033[1;31m$line\033[0m"  # 红色
    # 高亮显示警告
    elif echo "$line" | grep -q "WARNING"; then
        echo -e "\033[1;33m$line\033[0m"  # 黄色
    else
        echo "$line"
    fi
done
```

创建 `monitor.bat` (Windows):
```batch
@echo off
echo === 实时监控量化交易系统 ===
echo.
echo 监控日志文件: logs\quant_trading.log
echo 按 Ctrl+C 停止监控
echo.
echo ----------------------------------------
powershell -Command "Get-Content logs\quant_trading.log -Wait -Tail 50 | Select-String -Pattern '交易信号|ERROR|WARNING'"
```

---

## 性能追踪

### 查看策略统计

**在日志中查找**:
```bash
grep "记录交易" logs/quant_trading.log
```

**输出示例**:
```
2024-10-09 14:35:21 - Strategy_MeanReversion - INFO - 记录交易: 盈亏 15.5, 总盈亏 125.8
2024-10-09 15:20:45 - Strategy_MeanReversion - INFO - 记录交易: 盈亏 -8.2, 总盈亏 117.6
2024-10-09 16:05:10 - Strategy_MeanReversion - INFO - 记录交易: 盈亏 22.1, 总盈亏 139.7
```

### 统计交易次数

**Linux/macOS**:
```bash
# 统计总交易次数
grep "交易信号: LONG\|交易信号: SHORT" logs/quant_trading.log | wc -l

# 统计做多次数
grep "交易信号: LONG" logs/quant_trading.log | wc -l

# 统计做空次数
grep "交易信号: SHORT" logs/quant_trading.log | wc -l

# 统计平仓次数
grep "交易信号: EXIT" logs/quant_trading.log | wc -l
```

**Windows PowerShell**:
```powershell
# 统计总交易次数
(Select-String -Path logs\quant_trading.log -Pattern "交易信号: (LONG|SHORT)").Count

# 统计做多次数
(Select-String -Path logs\quant_trading.log -Pattern "交易信号: LONG").Count

# 统计做空次数
(Select-String -Path logs\quant_trading.log -Pattern "交易信号: SHORT").Count
```

### 查看风险事件

```bash
# 查看所有风险警告
grep "WARNING" logs/quant_trading.log

# 查看风险限制触发
grep "风险限制触发\|风险检查失败" logs/quant_trading.log
```

### 查看错误

```bash
# 查看所有错误
grep "ERROR" logs/quant_trading.log

# 查看最近的错误
grep "ERROR" logs/quant_trading.log | tail -10
```

---

## 通过 Web 界面监控

如果您启用了 Web 后端，可以通过浏览器查看：

### 启动 Web 后端

```bash
cd web_backend
python main.py
```

### 访问监控页面

```
http://localhost:8000
```

**可用端点**:
- `GET /api/account/balance` - 查看账户余额
- `GET /api/positions` - 查看当前仓位
- `GET /api/orders` - 查看订单历史
- `GET /api/trades` - 查看交易历史
- `GET /api/strategy/status` - 查看策略状态

---

## 通知系统

### 邮件通知

如果启用了邮件通知，您会收到以下类型的通知：

1. **交易执行通知**
   - 标题: "交易执行通知"
   - 内容: 包含市场ID、方向、价格、数量

2. **止损/止盈通知**
   - 标题: "止损触发" / "止盈触发"
   - 内容: 包含盈亏信息

3. **风险警告通知**
   - 标题: "风险限制触发"
   - 内容: 触发的风险类型和当前值

4. **系统错误通知**
   - 标题: "系统错误"
   - 内容: 错误详情

### 配置邮件通知

编辑 `config.yaml`:
```yaml
notifications:
  enabled: true
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    username: "your@email.com"
    password: "your_app_password"
    to_emails:
      - "your@email.com"
```

---

## 常见问题

### Q1: 为什么看不到交易信号？

**可能原因**:

1. **策略未启用**
   ```yaml
   strategies:
     mean_reversion:
       enabled: true  # 确保是 true
   ```

2. **市场数据不足**
   - 策略需要一定数量的K线数据才能工作
   - 均值回归：需要 `lookback_period` 个K线（默认20个）
   - 动量策略：需要 `long_period` 个K线（默认20个）
   
   **解决**: 等待足够的数据积累（通常需要等待 tick_interval * period 秒）

3. **信号冷却期**
   - 策略有信号冷却期限制，避免频繁交易
   - 默认冷却期：5-10分钟
   
   **查看日志**: 不会有"跳过信号"的日志，只是不产生新信号

4. **价格未达到阈值**
   - 均值回归：`|z_score| < threshold`
   - 动量策略：`|momentum| < momentum_threshold`
   
   **解决**: 调整策略参数或等待市场条件满足

### Q2: 信号产生了但没有交易？

**可能原因**:

1. **风险限制触发**
   ```
   2024-10-09 15:30:15 - RiskManager - WARNING - 日亏损限制触发: 3.2% > 2.0%
   ```
   
   **解决**: 等待风险指标恢复或调整风险参数

2. **余额不足**
   ```
   2024-10-09 14:26:10 - OrderManager - ERROR - 订单被拒绝: 余额不足
   ```
   
   **解决**: 充值账户或减小 `position_size`

3. **网络问题**
   ```
   2024-10-09 14:26:10 - OrderManager - ERROR - 连接超时
   ```
   
   **解决**: 检查网络连接

4. **API密钥问题**
   ```
   2024-10-09 14:26:10 - OrderManager - ERROR - 认证失败
   ```
   
   **解决**: 检查 API 密钥配置

### Q3: 如何确认交易已执行？

**方法1: 查看日志**
```bash
grep "订单已成交" logs/quant_trading.log
```

**方法2: 查看仓位**
- 检查 Lighter 交易所账户
- 或通过 Web API: `GET /api/positions`

**方法3: 查看订单历史**
- Lighter 交易所订单历史
- 或通过 Web API: `GET /api/orders`

### Q4: 如何查看策略表现？

**查看总盈亏**:
```bash
grep "总盈亏" logs/quant_trading.log | tail -1
```

**统计胜率**:
```bash
# 盈利交易
grep "记录交易: 盈亏" logs/quant_trading.log | grep -v "盈亏 -"

# 亏损交易
grep "记录交易: 盈亏 -" logs/quant_trading.log
```

### Q5: 交易频率太高/太低？

**太高**:
- 降低 `tick_interval`
- 增加信号阈值
- 增加信号冷却期

**太低**:
- 减小信号阈值
- 减少信号冷却期
- 检查市场波动是否足够

---

## 监控最佳实践

### 1. 开启调试模式

测试时使用 DEBUG 级别：
```yaml
log:
  level: "DEBUG"
```

或启动时指定：
```bash
python start_trading.py --log-level DEBUG
```

### 2. 使用多窗口监控

**推荐窗口布局**:
```
┌──────────────┬──────────────┐
│   主程序     │  实时日志     │
│              │              │
├──────────────┼──────────────┤
│  交易信号    │  错误监控     │
│              │              │
└──────────────┴──────────────┘
```

### 3. 定期检查

- 每小时检查一次日志
- 每天查看交易统计
- 每周分析策略表现

### 4. 设置告警

创建告警脚本 `alert.sh`:
```bash
#!/bin/bash
# 检查错误数量
error_count=$(grep "ERROR" logs/quant_trading.log | wc -l)
if [ $error_count -gt 10 ]; then
    echo "警告：发现 $error_count 个错误！" | mail -s "交易系统警告" your@email.com
fi
```

### 5. 备份日志

```bash
# 每天备份日志
tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/
```

---

## 快速参考

### 常用监控命令

```bash
# 实时监控
tail -f logs/quant_trading.log

# 只看交易信号
tail -f logs/quant_trading.log | grep "交易信号"

# 统计今天的交易
grep "$(date +%Y-%m-%d)" logs/quant_trading.log | grep "交易信号"

# 查看最近10个信号
grep "交易信号" logs/quant_trading.log | tail -10

# 查看错误
grep "ERROR" logs/quant_trading.log

# 查看风险警告
grep "WARNING.*风险" logs/quant_trading.log
```

### 日志位置

```
主日志: logs/quant_trading.log
错误日志: logs/error.log (如果单独配置)
交易记录: 在主日志中
```

---

## 相关文档

- [执行手册](EXECUTION_MANUAL.md) - 启动和运行系统
- [策略快速参考](STRATEGIES_QUICK_REFERENCE.md) - 各策略说明
- [参数配置手册](PARAMETER_CONFIG_MANUAL.md) - 配置参数

---

**文档版本**: v1.0.0  
**最后更新**: 2024年10月  
**维护者**: Quant Trading Team

