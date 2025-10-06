# Lighter量化交易程序 - 主网快速开始

## ⚠️ 重要警告

**主网部署涉及真实资金，请务必谨慎操作！**

- 确保您完全理解量化交易的风险
- 建议先在测试网充分测试
- 从小资金开始，逐步增加
- 设置严格的风险控制参数
- 定期监控程序运行状态

## 🚀 主网部署流程

### 步骤1: 环境准备

```bash
# 1. 确保测试网测试完成
python test_system.py

# 2. 创建主网目录
mkdir lighter_quant_mainnet
cd lighter_quant_mainnet

# 3. 复制项目文件
cp -r /path/to/lighter_quantification_v2/* .

# 4. 安装依赖
pip install -r requirements.txt
```

### 步骤2: 主网配置

#### 2.1 获取主网API密钥
1. 访问 [Lighter主网](https://app.lighter.xyz/)
2. 完成KYC认证
3. 充值资金到账户
4. 创建API密钥（建议创建专用API密钥）

#### 2.2 配置主网参数
```bash
# 编辑主网配置文件
notepad config_mainnet.yaml  # Windows
nano config_mainnet.yaml     # Linux/macOS
```

配置以下参数：
```yaml
lighter:
  base_url: "https://mainnet.zklighter.elliot.ai"
  api_key_private_key: "your_mainnet_api_key_here"
  account_index: 0
  api_key_index: 0
```

### 步骤3: 系统测试

```bash
# 运行主网系统测试
python test_mainnet.py
```

预期输出：
```
✅ 配置加载成功
✅ 主网连接成功
✅ 风险参数检查通过
✅ 策略配置正确
✅ 市场数据获取成功
🎉 所有测试通过！主网系统可以正常运行。
```

### 步骤4: 启动主网交易

```bash
# 启动主网交易程序
python start_mainnet.py
```

按照提示：
1. 确认安全检查通过
2. 输入 'MAINNET' 确认继续
3. 程序将自动启动交易

### 步骤5: 监控程序

```bash
# 在另一个终端启动监控
python monitor_mainnet.py
```

监控内容：
- 程序运行状态
- 账户余额变化
- 错误日志
- 风险指标

## 📊 主网配置说明

### 风险控制配置（主网严格设置）

```yaml
risk:
  max_position_size: 0.02  # 最大仓位2%
  max_daily_loss: 0.01     # 最大日亏损1%
  max_drawdown: 0.05       # 最大回撤5%
  max_leverage: 5.0        # 最大杠杆5倍
  max_orders_per_minute: 3 # 每分钟最大订单数
  max_open_orders: 5       # 最大开仓订单数
```

### 策略配置（主网保守设置）

```yaml
strategies:
  ut_bot:
    enabled: true
    market_id: 0
    key_value: 0.8      # 降低敏感度
    atr_period: 14      # 增加稳定性
    position_size: 0.01 # 保守仓位
    stop_loss: 0.015    # 严格止损
    take_profit: 0.008  # 保守止盈
```

## 🛡️ 安全建议

### 1. 资金管理
- 不要投入超过承受能力的资金
- 建议初始资金：$1000-$10000
- 设置严格的止损和止盈
- 定期提取利润

### 2. 风险控制
- 严格执行风险参数
- 监控最大回撤
- 控制仓位大小
- 避免过度杠杆

### 3. 系统监控
- 24/7监控程序运行
- 定期检查日志
- 监控账户余额
- 及时处理异常

## 📈 监控和管理

### 实时监控

#### 1. 程序状态监控
```bash
# 检查进程状态
ps aux | grep start_mainnet.py

# 查看实时日志
tail -f logs/mainnet_trading.log

# 查看错误日志
grep "ERROR" logs/mainnet_trading.log
```

#### 2. 账户监控
```bash
# 查看账户余额
python -c "
import asyncio
import lighter
from quant_trading import Config

async def check_balance():
    config = Config.from_file('config_mainnet.yaml')
    api_client = lighter.ApiClient(
        configuration=lighter.Configuration(host=config.lighter_config['base_url'])
    )
    account_api = lighter.AccountApi(api_client)
    account = await account_api.account(
        by='index', 
        value=str(config.lighter_config['account_index'])
    )
    print(f'账户余额: ${account.balance}')
    await api_client.close()

asyncio.run(check_balance())
"
```

#### 3. 风险监控
- 监控最大回撤
- 检查仓位大小
- 验证止损设置
- 跟踪交易频率

### 紧急处理

#### 1. 紧急停止
```bash
# 立即停止程序
pkill -f start_mainnet.py

# 或者发送SIGINT信号
kill -INT $(pgrep -f start_mainnet.py)
```

#### 2. 数据备份
```bash
# 备份配置文件
cp config_mainnet.yaml config_mainnet_backup_$(date +%Y%m%d).yaml

# 备份日志文件
tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/

# 备份交易数据
cp -r data/ data_backup_$(date +%Y%m%d)/
```

## 🔧 故障排除

### 常见问题

#### 1. 连接问题
```bash
# 检查网络连接
ping mainnet.zklighter.elliot.ai

# 检查API密钥
python test_mainnet.py
```

#### 2. 配置问题
```bash
# 验证配置文件
python -c "from quant_trading import Config; Config.from_file('config_mainnet.yaml').validate()"
```

#### 3. 权限问题
```bash
# 检查文件权限
ls -la config_mainnet.yaml
ls -la logs/

# 修复权限
chmod 600 config_mainnet.yaml
chmod 755 logs/
```

### 调试模式

```bash
# 启用详细日志
export LOG_LEVEL=DEBUG
python start_mainnet.py
```

## 📝 主网检查清单

### 部署前检查
- [ ] 测试网充分测试
- [ ] 主网配置正确
- [ ] API密钥有效
- [ ] 资金准备充足
- [ ] 风险参数合理

### 启动前检查
- [ ] 主网连接测试通过
- [ ] 风险参数检查通过
- [ ] 策略配置正确
- [ ] 监控系统就绪
- [ ] 备份系统就绪

### 运行中检查
- [ ] 程序正常运行
- [ ] 日志记录正常
- [ ] 交易执行正常
- [ ] 风险控制有效
- [ ] 监控报警正常

## 🎯 最佳实践

### 1. 渐进式部署
- 从小资金开始
- 逐步增加仓位
- 持续监控表现
- 及时调整参数

### 2. 风险控制
- 设置严格止损
- 控制最大回撤
- 限制仓位大小
- 避免过度交易

### 3. 系统维护
- 定期更新程序
- 监控系统性能
- 备份重要数据
- 及时处理异常

### 4. 合规要求
- 遵守当地法规
- 记录交易活动
- 按时报税
- 保持透明度

## 🆘 应急联系

### 技术支持
- 查看日志文件
- 运行诊断脚本
- 检查网络连接
- 验证配置参数

### 紧急情况
- 立即停止程序
- 检查账户状态
- 联系技术支持
- 记录问题详情

## 📞 后续支持

### 1. 性能优化
- 策略参数调优
- 风险控制优化
- 系统性能优化
- 监控系统完善

### 2. 功能扩展
- 添加新策略
- 集成更多数据源
- 增强监控功能
- 优化用户体验

### 3. 风险管控
- 完善风险模型
- 增强监控指标
- 优化止损机制
- 提高系统稳定性

记住：主网部署涉及真实资金，请务必谨慎操作，充分测试，严格风控！

## 🎉 成功部署标志

当您看到以下输出时，说明主网部署成功：

```
🚀 Lighter量化交易程序 - 主网版本
✅ 安全检查通过
📊 策略配置: UT Bot
🛡️ 风险控制: 已启用
🚀 启动主网交易引擎...
📈 市场数据更新中...
💹 交易信号生成中...
```

恭喜您成功部署了主网量化交易系统！
