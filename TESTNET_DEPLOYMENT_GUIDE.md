# Lighter量化交易程序测试网部署指南

## 📋 部署前准备

### 1. 系统要求
- Python 3.8+
- Windows/Linux/macOS
- 稳定的网络连接
- 至少2GB可用内存

### 2. 测试网账户准备
- 访问 [Lighter测试网](https://testnet.app.lighter.xyz/)
- 连接钱包获取测试代币（$500测试资金）
- 记录您的钱包地址和私钥

## 🚀 部署步骤

### 步骤1: 环境准备

```bash
# 1. 克隆或下载项目
cd lighter_quantification_v2

# 2. 创建虚拟环境（推荐）
python -m venv venv

# 3. 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt
```

### 步骤2: 系统初始化

```bash
# 运行系统设置脚本
python examples/system_setup.py
```

按照提示输入：
- 您的以太坊私钥
- 选择API密钥索引（建议选择1，避免与网页版冲突）
- 系统将自动生成API密钥

### 步骤3: 配置参数

#### 3.1 编辑配置文件
```bash
# 复制配置模板
cp config.yaml.example config.yaml

# 编辑配置文件
notepad config.yaml  # Windows
nano config.yaml     # Linux/macOS
```

#### 3.2 配置Lighter参数
```yaml
lighter:
  base_url: "https://testnet.zklighter.elliot.ai"  # 测试网地址
  api_key_private_key: "your_generated_api_key_here"  # 从system_setup.py获取
  account_index: 595  # 从system_setup.py获取
  api_key_index: 1    # 从system_setup.py获取
```

#### 3.3 配置风险参数（测试用）
```yaml
risk:
  max_position_size: 0.05  # 最大仓位5%（测试用较小值）
  max_daily_loss: 0.02     # 最大日亏损2%
  max_drawdown: 0.10       # 最大回撤10%
  max_orders_per_minute: 5 # 每分钟最大订单数
  max_open_orders: 10      # 最大开仓订单数
```

### 步骤4: 验证配置

```bash
# 测试配置是否正确
python -c "
from quant_trading import Config
config = Config.from_file('config.yaml')
config.validate()
print('✅ 配置验证成功')
"
```

## 🧪 测试流程

### 测试1: 基础连接测试

```bash
# 测试Lighter API连接
python examples/get_info.py
```

预期输出：
- 账户信息
- 市场数据
- 订单簿信息

### 测试2: 数据源测试

```bash
# 测试TradingView数据源
python examples/tradingview_data_example.py
```

预期输出：
- TradingView数据源初始化成功
- 获取到K线数据
- 技术指标数据

### 测试3: 策略回测

```bash
# 运行回测测试
python backtest.py --strategy ut_bot --days 7
```

预期输出：
- 回测结果摘要
- 性能指标
- 交易记录

### 测试4: 模拟交易

```bash
# 运行单个策略（模拟模式）
python main.py --strategy ut_bot --market 0 --dry-run
```

预期输出：
- 策略启动信息
- 市场数据更新
- 交易信号生成（但不执行实际交易）

## 🎯 正式运行

### 运行单个策略

```bash
# 运行UT Bot策略
python main.py --strategy ut_bot --market 0

# 运行均值回归策略
python main.py --strategy mean_reversion --market 0

# 运行所有策略
python main.py --strategy all --market 0
```

### 交互式启动

```bash
# 使用交互式启动脚本
python start_trading.py
```

按照提示：
1. 选择网络（测试网）
2. 输入API参数
3. 选择策略
4. 确认风险提示

## 📊 监控和管理

### 实时监控

程序运行时会显示：
- 策略状态
- 市场数据更新
- 交易信号
- 风险指标
- 错误信息

### 日志查看

```bash
# 查看实时日志
tail -f logs/quant_trading.log

# 查看错误日志
grep "ERROR" logs/quant_trading.log
```

### 停止程序

```bash
# 安全停止（Ctrl+C）
# 程序会自动：
# 1. 停止所有策略
# 2. 平仓所有仓位
# 3. 关闭API连接
# 4. 保存状态
```

## 🔧 故障排除

### 常见问题

#### 1. API连接失败
```
错误: API连接失败
解决: 检查网络连接和API密钥
```

#### 2. 账户余额不足
```
错误: 账户余额不足
解决: 访问测试网获取更多测试代币
```

#### 3. 市场数据获取失败
```
错误: 市场数据获取失败
解决: 检查市场ID是否正确
```

#### 4. 策略参数错误
```
错误: 策略参数错误
解决: 检查配置文件中的策略参数
```

### 调试模式

```bash
# 启用详细日志
python main.py --strategy ut_bot --market 0 --log-level DEBUG
```

## 📈 性能优化

### 1. 调整更新频率
```yaml
trading:
  tick_interval: 2.0  # 增加主循环间隔，减少API调用
```

### 2. 限制数据源
```yaml
data_sources:
  tradingview:
    enabled: false  # 如果不需要TradingView数据，可以禁用以提高性能
```

### 3. 减少策略数量
```bash
# 只运行一个策略
python main.py --strategy ut_bot --market 0
```

## 🛡️ 安全建议

### 1. 测试环境隔离
- 使用独立的测试网账户
- 不要使用主网私钥
- 定期更换测试API密钥

### 2. 风险控制
- 设置较小的仓位大小
- 启用止损和止盈
- 监控程序运行状态

### 3. 数据备份
- 定期备份配置文件
- 保存交易日志
- 记录策略参数

## 📝 测试检查清单

### 部署前检查
- [ ] Python环境正确安装
- [ ] 依赖包安装完成
- [ ] 测试网账户准备就绪
- [ ] 配置文件正确设置

### 运行前检查
- [ ] API连接测试通过
- [ ] 数据源测试通过
- [ ] 回测测试通过
- [ ] 风险参数设置合理

### 运行中检查
- [ ] 程序正常启动
- [ ] 策略正常运行
- [ ] 市场数据正常更新
- [ ] 日志记录正常

## 🎉 成功部署标志

当您看到以下输出时，说明部署成功：

```
✅ 配置验证成功
✅ Lighter数据源初始化完成
✅ TradingView数据源已启用
✅ UT Bot策略已启动
🚀 启动交易引擎...
📈 市场数据更新中...
💹 交易信号生成中...
```

## 📞 技术支持

如果遇到问题，请检查：
1. 日志文件中的错误信息
2. 网络连接状态
3. API密钥是否正确
4. 配置文件格式是否正确

## 🔄 下一步

测试成功后，您可以：
1. 调整策略参数
2. 添加更多策略
3. 优化风险控制
4. 准备主网部署

记住：测试网是学习和验证策略的好地方，请充分利用测试环境进行充分测试后再考虑主网部署！
