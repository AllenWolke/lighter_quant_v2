# Lighter量化交易程序 - 测试网快速开始

## 🚀 一键部署

### 方法1: 自动部署（推荐）

```bash
# 1. 运行快速部署脚本
python quick_setup.py

# 2. 按照提示输入配置信息
# 3. 等待部署完成
```

### 方法2: 手动部署

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行系统设置
python examples/system_setup.py

# 3. 复制配置模板
cp config.yaml.example config.yaml

# 4. 编辑配置文件
notepad config.yaml  # Windows
nano config.yaml     # Linux/macOS
```

## 🧪 系统测试

```bash
# 运行完整系统测试
python test_system.py

# 或者使用简化测试
python run_testnet.py --test
```

预期输出：
```
✅ 配置加载成功
✅ Lighter连接成功
✅ 数据源初始化成功
✅ 策略初始化成功
✅ 交易引擎初始化成功
🎉 所有测试通过！系统可以正常运行。
```

## 🎯 开始交易

### 运行单个策略

```bash
# UT Bot策略（推荐）
python run_testnet.py --strategy ut_bot --market 0

# 均值回归策略
python run_testnet.py --strategy mean_reversion --market 0

# 动量策略
python run_testnet.py --strategy momentum --market 0
```

### 运行回测

```bash
# UT Bot策略回测
python backtest.py --strategy ut_bot --days 7

# 所有策略回测
python backtest.py --strategy all --days 3
```

### 交互式启动

```bash
# 使用交互式界面
python start_trading.py
```

## 📊 监控和管理

### 查看实时日志

```bash
# Windows
type logs\quant_trading.log

# Linux/macOS
tail -f logs/quant_trading.log
```

### 查看交易状态

程序运行时会显示：
- 策略状态
- 市场数据更新
- 交易信号
- 风险指标

### 停止程序

```bash
# 安全停止（Ctrl+C）
# 程序会自动：
# 1. 停止所有策略
# 2. 平仓所有仓位
# 3. 保存状态
```

## ⚙️ 配置说明

### 必需配置

```yaml
lighter:
  base_url: "https://testnet.zklighter.elliot.ai"
  api_key_private_key: "your_api_key_here"
  account_index: 595
  api_key_index: 1
```

### 风险配置（测试用）

```yaml
risk:
  max_position_size: 0.05  # 最大仓位5%
  max_daily_loss: 0.02     # 最大日亏损2%
  max_drawdown: 0.10       # 最大回撤10%
```

### 策略配置

```yaml
strategies:
  ut_bot:
    enabled: true
    market_id: 0
    key_value: 1.0      # 敏感度
    atr_period: 10      # ATR周期
    position_size: 0.05 # 仓位大小
```

## 🔧 故障排除

### 常见问题

1. **API连接失败**
   ```bash
   # 检查网络连接
   ping testnet.zklighter.elliot.ai
   
   # 验证API密钥
   python examples/get_info.py
   ```

2. **配置错误**
   ```bash
   # 验证配置文件
   python -c "from quant_trading import Config; Config.from_file('config.yaml').validate()"
   ```

3. **依赖缺失**
   ```bash
   # 重新安装依赖
   pip install -r requirements.txt
   ```

### 调试模式

```bash
# 启用详细日志
python run_testnet.py --strategy ut_bot --market 0 --log-level DEBUG
```

## 📈 性能优化

### 调整更新频率

```yaml
trading:
  tick_interval: 2.0  # 增加间隔，减少API调用
```

### 禁用不需要的数据源

```yaml
data_sources:
  tradingview:
    enabled: false  # 如果不需要TradingView数据
```

## 🛡️ 安全建议

1. **测试环境隔离**
   - 使用独立的测试网账户
   - 不要使用主网私钥
   - 定期更换测试API密钥

2. **风险控制**
   - 设置较小的仓位大小
   - 启用止损和止盈
   - 监控程序运行状态

3. **数据备份**
   - 定期备份配置文件
   - 保存交易日志
   - 记录策略参数

## 📝 检查清单

### 部署前
- [ ] Python 3.8+ 已安装
- [ ] 网络连接正常
- [ ] 测试网账户已准备
- [ ] 依赖包已安装

### 运行前
- [ ] 配置文件正确
- [ ] API密钥有效
- [ ] 系统测试通过
- [ ] 风险参数合理

### 运行中
- [ ] 程序正常启动
- [ ] 策略正常运行
- [ ] 市场数据更新
- [ ] 日志记录正常

## 🎉 成功标志

当您看到以下输出时，说明运行成功：

```
🚀 Lighter量化交易程序 - 测试网版本
✅ 配置文件加载成功
📊 启动UT Bot策略
🚀 启动交易引擎...
📈 市场数据更新中...
💹 交易信号生成中...
```

## 🔄 下一步

1. **策略优化**: 调整参数，提高性能
2. **风险控制**: 完善风险管理机制
3. **监控系统**: 添加更多监控指标
4. **主网准备**: 准备主网部署

## 📞 技术支持

如果遇到问题：
1. 查看日志文件
2. 运行系统测试
3. 检查网络连接
4. 验证配置参数

记住：测试网是学习和验证的好地方，请充分利用！
