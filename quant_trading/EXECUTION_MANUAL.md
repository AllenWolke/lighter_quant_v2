# Lighter量化交易模块 - 执行手册

## 📋 目录

- [快速开始](#快速开始)
- [启动方式](#启动方式)
- [交互式启动](#交互式启动)
- [命令行启动](#命令行启动)
- [回测系统](#回测系统)
- [策略管理](#策略管理)
- [监控和调试](#监控和调试)
- [风险控制](#风险控制)
- [故障处理](#故障处理)
- [最佳实践](#最佳实践)

---

## 快速开始

### 3分钟启动指南

```bash
# 1. 激活虚拟环境
source env/bin/activate  # Linux/macOS
# 或
env\Scripts\activate  # Windows

# 2. 检查配置
python check_config.py

# 3. 启动交易系统（交互式）
python start_trading.py

# 或使用配置文件启动
python start_trading.py --config config.yaml
```

### 首次运行建议

⚠️ **强烈建议**:
1. 首先在**测试网**环境测试
2. 使用**小额资金**进行实盘验证
3. 观察运行**24小时**无误后再增加资金
4. 启用**邮件通知**接收交易提醒

---

## 启动方式

### 方式一：交互式启动（推荐新手）

```bash
python start_trading.py
```

交互式启动会引导您完成：
1. 选择网络（测试网/主网）
2. 输入API私钥
3. 选择交易策略
4. 设置市场ID
5. 确认风险提示

**示例交互流程**:

```
🚀 Lighter量化交易程序
============================================================

请配置Lighter交易所参数:

1. 选择网络:
   1) 测试网 (testnet.zklighter.elliot.ai)
   2) 主网 (mainnet.zklighter.elliot.ai)
请选择 (1-2): 1

请输入API密钥私钥: 1234567890abcdef...
请输入账户索引: 0
请输入API密钥索引: 0

2. 选择交易策略:
   1) 均值回归策略
   2) 动量策略
   3) 套利策略
   4) UT Bot策略
   5) 所有策略
请选择 (1-5): 1

请输入市场ID (默认0): 0

3. 风险提示:
   ⚠️  量化交易存在风险，可能导致资金损失
   ⚠️  请确保您了解相关风险并谨慎操作
   ⚠️  建议先在测试网环境测试

是否确认继续? (y/N): y

✅ 配置已保存到 user_config.yaml
✅ 已添加均值回归策略
🚀 启动交易引擎...
按 Ctrl+C 停止程序
```

### 方式二：配置文件启动

```bash
# 使用默认配置文件
python start_trading.py --config config.yaml

# 使用自定义配置
python start_trading.py --config my_custom_config.yaml

# 指定策略
python start_trading.py --config config.yaml --strategy mean_reversion

# 指定市场
python start_trading.py --config config.yaml --market 0
```

### 方式三：直接使用main.py

```bash
# 启动完整系统
python main.py

# 使用特定配置
python main.py --config config.yaml

# 模拟运行（不实际交易）
python main.py --dry-run

# 启动特定策略
python main.py --strategy momentum --market 0
```

### 方式四：作为系统服务（生产环境）

```bash
# Linux systemd
sudo systemctl start quant-trading
sudo systemctl status quant-trading
sudo systemctl stop quant-trading

# 查看日志
sudo journalctl -u quant-trading -f

# Windows服务
sc start QuantTrading
sc query QuantTrading
sc stop QuantTrading
```

---

## 命令行参数

### 主程序参数

```bash
python start_trading.py [选项]

选项:
  -c, --config PATH       配置文件路径 (默认: config.yaml)
  -s, --strategy NAME     策略名称: mean_reversion, momentum, arbitrage, ut_bot, all
  -m, --market ID         市场ID (默认: 0)
  --dry-run              模拟运行模式，不实际交易
  --log-level LEVEL      日志级别: DEBUG, INFO, WARNING, ERROR
  --log-file PATH        日志文件路径
  -h, --help             显示帮助信息

可用策略:
  mean_reversion    均值回归策略
  momentum          动量策略
  arbitrage         套利策略
  ut_bot           UT Bot策略（ATR追踪止损）
  all              启动所有已配置的策略
```

### 使用示例

```bash
# 启动均值回归策略在市场0
python start_trading.py --strategy mean_reversion --market 0

# 启动所有策略，详细日志
python start_trading.py --strategy all --log-level DEBUG

# 模拟运行，不实际下单
python start_trading.py --dry-run --strategy momentum

# 使用自定义日志文件
python start_trading.py --log-file logs/my_trading.log

# 组合使用多个参数
python start_trading.py \
  --config config_mainnet.yaml \
  --strategy ut_bot \
  --market 0 \
  --log-level INFO \
  --log-file logs/ut_bot_mainnet.log
```

---

## 回测系统

### 基本回测

```bash
# 回测单个策略
python backtest.py --strategy mean_reversion --days 30

# 回测所有策略
python backtest.py --strategy all --days 30

# 使用自定义配置
python backtest.py --config config.yaml --strategy momentum --days 60
```

### 回测参数

```bash
python backtest.py [选项]

选项:
  -c, --config PATH       配置文件路径
  -s, --strategy NAME     策略: mean_reversion, momentum, arbitrage, all
  -d, --days NUMBER       回测天数 (默认: 30)
  -o, --output FILE       结果输出文件
  -v, --verbose          详细输出
```

### 回测输出

回测完成后会生成：
1. **控制台输出**: 性能摘要
2. **JSON文件**: 详细回测结果
3. **图表** (如果安装了matplotlib): 权益曲线、回撤图

**回测结果示例**:

```
========================================
回测结果摘要
========================================
策略: MeanReversion
回测周期: 2024-10-01 to 2024-10-31
初始资金: 10000.00
最终资金: 10523.50
========================================
收益率: 5.24%
夏普比率: 1.35
最大回撤: -3.21%
盈利交易: 45
亏损交易: 23
胜率: 66.18%
========================================
```

### 高级回测

```python
# 使用Python API进行自定义回测
from quant_trading import Config
from quant_trading.backtesting import BacktestEngine
from quant_trading.strategies import MeanReversionStrategy

# 加载配置
config = Config.from_file('config.yaml')

# 创建回测引擎
engine = BacktestEngine(config)

# 加载历史数据
engine.load_historical_data(market_id=0, data_file='data/historical.csv')

# 创建策略
strategy = MeanReversionStrategy(
    config=config,
    market_id=0,
    lookback_period=20,
    threshold=2.0
)

# 运行回测
result = await engine.run_backtest(
    strategy=strategy,
    start_date='2024-01-01',
    end_date='2024-10-31'
)

# 分析结果
result.print_summary()
result.plot_equity_curve()
result.save_to_file('backtest_result.json')
```

---

## 策略管理

### 启用/禁用策略

编辑`config.yaml`:

```yaml
strategies:
  mean_reversion:
    enabled: true    # 启用
    # ...
    
  momentum:
    enabled: false   # 禁用
    # ...
```

### 动态添加策略

```python
from quant_trading import TradingEngine, Config
from quant_trading.strategies import MomentumStrategy

# 创建引擎
config = Config.from_file('config.yaml')
engine = TradingEngine(config)

# 动态添加策略
new_strategy = MomentumStrategy(
    config=config,
    market_id=1,
    short_period=5,
    long_period=20,
    momentum_threshold=0.02
)
engine.add_strategy(new_strategy)

# 启动引擎
await engine.start()
```

### 多策略运行

```bash
# 启动所有已配置的策略
python start_trading.py --strategy all

# 或使用multi_strategy_bot示例
python examples/multi_strategy_bot.py
```

```python
# examples/multi_strategy_bot.py 内容示例
from quant_trading import TradingEngine, Config
from quant_trading.strategies import (
    MeanReversionStrategy,
    MomentumStrategy,
    UTBotStrategy
)

config = Config.from_file('config.yaml')
engine = TradingEngine(config)

# 添加多个策略
from quant_trading.strategies import (
    MeanReversionStrategy,
    MomentumStrategy,
    UTBotStrategy
)

engine.add_strategy(MeanReversionStrategy(config, market_id=0))
engine.add_strategy(MomentumStrategy(config, market_id=0))
engine.add_strategy(UTBotStrategy(config, market_id=1))

await engine.start()
```

### 策略参数优化

```python
# 参数扫描
import asyncio
from quant_trading.backtesting import BacktestEngine

async def optimize_strategy():
    config = Config.from_file('config.yaml')
    engine = BacktestEngine(config)
    
    best_params = None
    best_return = -float('inf')
    
    # 扫描参数空间
    for lookback in [10, 20, 30]:
        for threshold in [1.5, 2.0, 2.5]:
            strategy = MeanReversionStrategy(
                config=config,
                market_id=0,
                lookback_period=lookback,
                threshold=threshold
            )
            
            result = await engine.run_backtest(strategy)
            
            if result.total_return > best_return:
                best_return = result.total_return
                best_params = {
                    'lookback': lookback,
                    'threshold': threshold
                }
    
    print(f"最优参数: {best_params}")
    print(f"最优收益: {best_return:.2%}")

asyncio.run(optimize_strategy())
```

---

## 监控和调试

### 实时日志监控

```bash
# 监控主日志文件
tail -f logs/quant_trading.log

# 监控特定级别日志
tail -f logs/quant_trading.log | grep "ERROR"
tail -f logs/quant_trading.log | grep "WARNING"

# 使用多窗口监控
# 窗口1: 主程序
python start_trading.py

# 窗口2: 日志监控
tail -f logs/quant_trading.log

# 窗口3: 系统资源
htop
```

### 调试模式

```bash
# 启用DEBUG日志
python start_trading.py --log-level DEBUG

# 或修改配置文件
log:
  level: "DEBUG"
```

### 性能监控

```python
# 获取引擎状态
from quant_trading import TradingEngine, Config

config = Config.from_file('config.yaml')
engine = TradingEngine(config)

# 运行一段时间后...
status = engine.get_status()
print(f"运行状态: {status['is_running']}")
print(f"运行时长: {status['uptime']}")
print(f"活跃策略: {status['active_strategies']}")
print(f"当前仓位: {status['positions']}")
print(f"待处理订单: {status['orders']}")
```

### 风险监控

```python
# 获取风险状态
risk_status = engine.risk_manager.get_risk_status()

print(f"当前权益: {risk_status['current_equity']:.2f}")
print(f"今日盈亏: {risk_status['daily_pnl']:.2f}")
print(f"回撤: {risk_status['drawdown']:.2%}")
print(f"未成交订单: {risk_status['open_orders_count']}")
```

### Web界面监控（如已启用）

```bash
# 启动Web后端
cd web_backend
python main.py

# 访问
http://localhost:8000

# 查看实时数据
http://localhost:8000/api/account/balance
http://localhost:8000/api/positions
http://localhost:8000/api/orders
```

---

## 风险控制

### 紧急停止

```bash
# 方法1: Ctrl+C 优雅停止
# 在运行的终端按 Ctrl+C

# 方法2: 强制停止
ps aux | grep start_trading.py
kill -9 <PID>

# 方法3: 停止服务
sudo systemctl stop quant-trading

# 方法4: 使用停止脚本
./stop_all.sh
```

### 手动平仓

```python
# 使用Python脚本手动平仓
from lighter import SignerClient

client = SignerClient(
    url="https://testnet.zklighter.elliot.ai",
    private_key="your_private_key",
    account_index=0,
    api_key_index=0
)

# 取消所有订单
await client.cancel_all_orders()

# 平掉所有仓位
positions = await client.get_positions()
for position in positions:
    if position.size != 0:
        await client.create_market_order(
            market_id=position.market_id,
            side="sell" if position.side == "long" else "buy",
            size=abs(position.size)
        )
```

### 风险限制触发处理

当触发风险限制时，系统会：
1. **停止新开仓**: 阻止创建新订单
2. **发送通知**: 通过配置的通知渠道发送警告
3. **记录事件**: 在日志中详细记录
4. **等待恢复**: 等待风险指标恢复到安全范围

**手动恢复**:
```bash
# 查看风险事件
grep "风险限制触发" logs/quant_trading.log

# 调整风险参数（如需要）
nano config.yaml

# 重启系统
sudo systemctl restart quant-trading
```

---

## 故障处理

### 常见错误及解决

#### 1. 连接失败

**错误**: `Connection refused` 或 `Connection timeout`

**排查步骤**:
```bash
# 1. 检查网络
ping testnet.zklighter.elliot.ai

# 2. 检查Lighter服务状态
curl https://testnet.zklighter.elliot.ai/health

# 3. 检查配置
python check_config.py

# 4. 测试连接
python check_lighter_connection.sh
```

#### 2. 认证失败

**错误**: `Authentication failed` 或 `Invalid API key`

**解决**:
```bash
# 1. 验证私钥格式
# 确保是64位十六进制，无0x前缀
echo "your_private_key" | wc -c  # 应该是65（64+换行符）

# 2. 验证账户和密钥索引
# 确保account_index和api_key_index正确

# 3. 检查网络环境
# 测试网使用测试网私钥，主网使用主网私钥
```

#### 3. 订单被拒绝

**错误**: `Order rejected` 或 `Insufficient balance`

**排查**:
```bash
# 1. 检查账户余额
python test_account_balance.py

# 2. 检查仓位限制
# 确保不超过max_position_size

# 3. 检查市场状态
# 确保市场ID正确且市场开放

# 4. 检查订单参数
# 价格、数量必须符合市场规则
```

#### 4. 策略无交易信号

**原因**: 
- 市场数据不足
- 参数设置过于严格
- 信号冷却期未过

**解决**:
```bash
# 1. 检查日志
tail -f logs/quant_trading.log | grep "信号"

# 2. 调整策略参数
# 降低threshold、调整周期等

# 3. 等待足够的K线数据积累
# 策略通常需要20-50根K线后才开始工作
```

#### 5. 内存泄漏

**症状**: 程序运行时间越长，内存占用越高

**解决**:
```bash
# 1. 监控内存使用
while true; do
  ps aux | grep start_trading.py | grep -v grep
  sleep 60
done

# 2. 设置定时重启
# crontab
0 2 * * * /opt/quant_trading/restart.sh

# 3. 优化配置
# 减少历史数据缓存、降低tick_interval
```

### 日志分析

```bash
# 统计错误数量
grep "ERROR" logs/quant_trading.log | wc -l

# 查看最近的错误
grep "ERROR" logs/quant_trading.log | tail -20

# 统计交易次数
grep "交易信号" logs/quant_trading.log | wc -l

# 查看风险事件
grep "风险" logs/quant_trading.log

# 分析性能问题
grep "耗时" logs/quant_trading.log
```

---

## 最佳实践

### 1. 启动前检查

```bash
# 运行启动前检查脚本
cat > pre_start_check.sh << 'EOF'
#!/bin/bash

echo "=== 启动前检查 ==="

# 检查Python版本
python3 --version || { echo "❌ Python未安装"; exit 1; }

# 检查虚拟环境
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ 虚拟环境未激活"
    exit 1
fi

# 检查配置文件
if [ ! -f config.yaml ]; then
    echo "❌ 配置文件不存在"
    exit 1
fi

# 检查依赖
python check_dependencies.py || { echo "❌ 依赖检查失败"; exit 1; }

# 检查配置
python check_config.py || { echo "❌ 配置检查失败"; exit 1; }

# 检查日志目录
if [ ! -d logs ]; then
    mkdir -p logs
fi

# 检查磁盘空间
DISK_FREE=$(df -h . | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_FREE -gt 90 ]; then
    echo "⚠️  磁盘空间不足"
fi

echo "✅ 所有检查通过"
EOF

chmod +x pre_start_check.sh
./pre_start_check.sh
```

### 2. 分阶段启动策略

```yaml
# 阶段1: 仅监控（不交易）
# 观察1-3天
strategies:
  mean_reversion:
    enabled: false  # 先禁用

# 阶段2: 单策略小仓位
# 运行1周
strategies:
  mean_reversion:
    enabled: true
    position_size: 0.01  # 1%仓位

# 阶段3: 逐步增加
# 表现良好后
strategies:
  mean_reversion:
    enabled: true
    position_size: 0.05  # 5%仓位

# 阶段4: 多策略
# 稳定运行1个月后
strategies:
  mean_reversion:
    enabled: true
  momentum:
    enabled: true
```

### 3. 定期维护任务

```bash
# 创建维护脚本
cat > maintenance.sh << 'EOF'
#!/bin/bash

echo "开始维护任务..."

# 1. 备份配置
cp config.yaml backups/config_$(date +%Y%m%d).yaml

# 2. 清理旧日志（保留30天）
find logs/ -name "*.log" -mtime +30 -delete

# 3. 备份日志
tar -czf backups/logs_$(date +%Y%m%d).tar.gz logs/

# 4. 检查磁盘空间
df -h .

# 5. 更新依赖（可选）
# pip install --upgrade lighter-v2-python

# 6. 生成统计报告
python generate_report.py

echo "维护完成"
EOF

chmod +x maintenance.sh

# 设置每周执行
crontab -e
# 添加: 0 3 * * 0 /opt/quant_trading/maintenance.sh
```

### 4. 监控告警

```python
# 创建监控脚本 monitor.py
import asyncio
from quant_trading import TradingEngine, Config

async def monitor():
    config = Config.from_file('config.yaml')
    engine = TradingEngine(config)
    
    while True:
        status = engine.get_status()
        risk = engine.risk_manager.get_risk_status()
        
        # 检查异常情况
        if not status['is_running']:
            send_alert("系统未运行")
        
        if risk['drawdown'] > 0.10:
            send_alert(f"回撤过大: {risk['drawdown']:.2%}")
        
        if risk['daily_pnl'] < -1000:
            send_alert(f"日亏损: {risk['daily_pnl']:.2f}")
        
        await asyncio.sleep(300)  # 每5分钟检查一次

def send_alert(message):
    # 发送告警（邮件、短信等）
    print(f"⚠️  告警: {message}")

asyncio.run(monitor())
```

### 5. 性能优化建议

- **测试网**: `tick_interval: 1.0` - 快速测试
- **主网低频**: `tick_interval: 5.0` - 降低成本
- **主网高频**: `tick_interval: 1.0` - 需要更好的网络
- **多策略**: 限制`max_concurrent_strategies: 3-5`
- **数据缓存**: 控制历史数据保留量
- **日志轮转**: 防止日志文件过大

---

## 示例工作流

### 典型的日常操作流程

```bash
# 早上 - 检查系统状态
sudo systemctl status quant-trading
tail -50 logs/quant_trading.log

# 查看昨日表现
python generate_daily_report.py

# 中午 - 监控运行
tail -f logs/quant_trading.log | grep "交易信号"

# 晚上 - 查看统计
python show_statistics.py

# 每周 - 参数调整
# 1. 导出回测数据
python export_trades.py --days 7

# 2. 分析表现
python analyze_performance.py

# 3. 调整参数（如需要）
nano config.yaml

# 4. 重启应用新配置
sudo systemctl restart quant-trading
```

---

## 应急响应流程

### 紧急情况处理清单

**市场异常波动**:
1. 立即停止所有策略
2. 平掉所有仓位
3. 分析原因
4. 调整参数或暂停交易

**系统故障**:
1. 停止交易程序
2. 手动平仓（如有必要）
3. 检查日志
4. 修复问题
5. 测试后重新启动

**资金异常**:
1. 暂停交易
2. 检查账户余额
3. 核对交易记录
4. 联系技术支持

---

## 相关文档

- [参数配置手册](PARAMETER_CONFIG_MANUAL.md)
- [部署手册](DEPLOYMENT_MANUAL.md)
- [策略开发指南](../docs/strategy_development.md)
- [API参考文档](../docs/api_reference.md)

---

## 技术支持

如遇到问题：
1. 查看[常见问题](#故障处理)
2. 检查日志文件
3. 参考项目文档
4. 提交Issue到GitHub仓库

---

**文档版本**: v1.0.0  
**最后更新**: 2024年  
**维护者**: Quant Trading Team

