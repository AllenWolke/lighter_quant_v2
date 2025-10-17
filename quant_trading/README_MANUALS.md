# Lighter量化交易模块 - 使用手册总览

## 📚 文档导航

欢迎使用Lighter量化交易模块！本系列手册将帮助您从零开始部署和运行量化交易系统。

---

## 📖 手册列表

### 🎯 [策略快速参考](STRATEGIES_QUICK_REFERENCE.md) ⭐

**适用对象**: 所有用户

**内容涵盖**:
- ✅ 4种策略完整对比（均值回归、动量、套利、UT Bot）
- ✅ 每个策略的详细参数说明
- ✅ 快速启动命令
- ✅ 策略选择建议
- ✅ 示例代码
- ✅ 回测命令

**快速链接**: [👉 查看策略快速参考](STRATEGIES_QUICK_REFERENCE.md)

---

### 📊 [策略监控指南](STRATEGY_MONITORING_GUIDE.md) ⭐ 新增

**适用对象**: 需要监控策略运行的用户

**内容涵盖**:
- ✅ 日志查看和分析
- ✅ 交易信号识别方法
- ✅ 实时监控技巧
- ✅ 性能追踪方法
- ✅ 通知系统配置
- ✅ 常见问题排查

**适用场景**:
- 确认策略是否执行
- 查看交易信号时机
- 监控交易表现
- 排查问题

**快速链接**: [👉 查看策略监控指南](STRATEGY_MONITORING_GUIDE.md)

---

### 1. [参数配置手册](PARAMETER_CONFIG_MANUAL.md)

**适用对象**: 需要配置交易系统的用户

**内容涵盖**:
- ✅ Lighter交易所连接配置
- ✅ 交易参数设置
- ✅ 风险管理参数详解
- ✅ 策略参数配置（均值回归、动量、套利、UT Bot）
- ✅ 数据源和通知配置
- ✅ 配置示例和最佳实践

**适用场景**:
- 首次配置系统
- 调整策略参数
- 优化风险控制
- 切换测试网/主网

**快速链接**: [👉 查看参数配置手册](PARAMETER_CONFIG_MANUAL.md)

---

### 2. [部署手册](DEPLOYMENT_MANUAL.md)

**适用对象**: 负责系统安装和部署的技术人员

**内容涵盖**:
- ✅ 系统要求和环境准备
- ✅ Python环境搭建
- ✅ 依赖安装和管理
- ✅ 配置文件设置
- ✅ 测试和验证
- ✅ 生产环境部署（Linux/Windows）
- ✅ Docker容器化部署
- ✅ 系统服务配置

**适用场景**:
- 全新安装系统
- 服务器部署
- Docker容器化
- 系统升级迁移

**快速链接**: [👉 查看部署手册](DEPLOYMENT_MANUAL.md)

---

### 3. [执行手册](EXECUTION_MANUAL.md)

**适用对象**: 日常运营和监控系统的交易员

**内容涵盖**:
- ✅ 快速启动指南
- ✅ 多种启动方式
- ✅ 回测系统使用
- ✅ 策略管理和优化
- ✅ 实时监控和调试
- ✅ 风险控制和应急处理
- ✅ 故障排查
- ✅ 最佳实践

**适用场景**:
- 日常启动和停止
- 策略切换和调整
- 系统监控
- 故障处理
- 性能优化

**快速链接**: [👉 查看执行手册](EXECUTION_MANUAL.md)

---

## 🚀 快速开始流程

### 新用户推荐路径

```
1️⃣  阅读 [部署手册] 
    ↓
    安装Python环境和依赖
    ↓
2️⃣  阅读 [参数配置手册]
    ↓
    配置config.yaml文件
    ↓
3️⃣  阅读 [执行手册]
    ↓
    启动系统并监控
```

### 3分钟快速启动

如果您已经熟悉基本概念，可以直接：

```bash
# 1. 激活虚拟环境
source env/bin/activate

# 2. 复制配置文件
cp config.yaml.example config.yaml

# 3. 编辑配置（填入您的私钥）
nano config.yaml

# 4. 启动交易系统
python start_trading.py

# 详细步骤请参考执行手册
```

---

## 📋 使用场景索引

### 我想要...

#### 🆕 首次部署系统
1. 阅读 [部署手册 - 系统要求](DEPLOYMENT_MANUAL.md#系统要求)
2. 阅读 [部署手册 - 安装步骤](DEPLOYMENT_MANUAL.md#安装步骤)
3. 阅读 [参数配置手册 - 配置示例](PARAMETER_CONFIG_MANUAL.md#配置示例)
4. 阅读 [执行手册 - 快速开始](EXECUTION_MANUAL.md#快速开始)

#### 📊 配置交易策略
1. 阅读 [策略快速参考](STRATEGIES_QUICK_REFERENCE.md) ⭐ 推荐从这里开始
2. 阅读 [参数配置手册 - 策略配置](PARAMETER_CONFIG_MANUAL.md#策略配置)
3. 阅读 [执行手册 - 策略管理](EXECUTION_MANUAL.md#策略管理)
4. 阅读 [执行手册 - 回测系统](EXECUTION_MANUAL.md#回测系统)

#### 👀 监控策略执行
1. 阅读 [策略监控指南](STRATEGY_MONITORING_GUIDE.md) ⭐ 必读
2. 阅读 [执行手册 - 监控和调试](EXECUTION_MANUAL.md#监控和调试)

#### 🔌 验证连接状态
1. 阅读 [连接验证指南](../CONNECTION_VERIFICATION_GUIDE.md) ⭐ 必读
2. 运行 `python test_lighter_connection.py` 测试连接

#### ⚠️ 调整风险参数
1. 阅读 [参数配置手册 - 风险管理配置](PARAMETER_CONFIG_MANUAL.md#风险管理配置)
2. 阅读 [执行手册 - 风险控制](EXECUTION_MANUAL.md#风险控制)

#### 🐳 Docker部署
1. 阅读 [部署手册 - Docker部署](DEPLOYMENT_MANUAL.md#docker部署)

#### 🖥️ 生产服务器部署
1. 阅读 [部署手册 - 生产部署](DEPLOYMENT_MANUAL.md#生产部署)

#### 🔍 监控和调试
1. 阅读 [执行手册 - 监控和调试](EXECUTION_MANUAL.md#监控和调试)

#### 🚨 处理故障
1. 阅读 [执行手册 - 故障处理](EXECUTION_MANUAL.md#故障处理)
2. 阅读 [部署手册 - 常见问题](DEPLOYMENT_MANUAL.md#常见问题)

#### 🌐 切换到主网
1. 阅读 [参数配置手册 - Lighter配置](PARAMETER_CONFIG_MANUAL.md#lighter交易所配置)
2. 阅读 [参数配置手册 - 完整主网配置](PARAMETER_CONFIG_MANUAL.md#完整主网配置保守型)

---

## 💡 重要提示

### ⚠️ 安全警告

1. **私钥保护**: 
   - 永远不要将私钥提交到Git仓库
   - 不要在日志中打印私钥
   - 使用环境变量存储敏感信息

2. **测试先行**:
   - 新策略必须先在测试网验证
   - 主网交易使用真实资金，请谨慎操作
   - 建议使用小额资金开始

3. **风险控制**:
   - 严格设置止损止盈
   - 不要使用过高杠杆
   - 分散投资，控制单一仓位

### 📌 最佳实践

1. **配置管理**:
   - 为不同环境创建不同的配置文件
   - 定期备份配置文件
   - 使用版本控制管理配置变更

2. **监控运维**:
   - 启用日志记录
   - 设置邮件通知
   - 定期检查系统状态
   - 保持依赖包更新

3. **策略优化**:
   - 使用回测验证策略
   - 小步迭代调整参数
   - 记录和分析交易结果
   - 持续优化改进

---

## 📚 补充资源

### 项目文档

- **策略快速参考**: [策略快速参考](STRATEGIES_QUICK_REFERENCE.md) ⭐
- **策略监控指南**: [策略监控指南](STRATEGY_MONITORING_GUIDE.md) ⭐
- **连接验证指南**: [连接验证指南](../CONNECTION_VERIFICATION_GUIDE.md) ⭐
- **主README**: [../README.md](../README.md)
- **量化交易README**: [../README_QUANT_TRADING.md](../README_QUANT_TRADING.md)
- **Web系统指南**: [../WEB_SYSTEM_GUIDE.md](../WEB_SYSTEM_GUIDE.md)

### 示例代码

项目提供了丰富的示例代码，位于 `examples/` 目录：

- `simple_trading_bot.py` - 简单交易机器人
- `multi_strategy_bot.py` - 多策略机器人
- `custom_strategy.py` - 自定义策略示例
- `ut_bot_strategy_example.py` - UT Bot策略示例
- `notification_example.py` - 通知功能示例
- `tradingview_data_example.py` - TradingView数据源示例

### Lighter交易所文档

- **测试网**: https://testnet.zklighter.elliot.ai
- **主网**: https://mainnet.zklighter.elliot.ai
- **API文档**: 参考Lighter官方文档

---

## 🔄 文档更新

### 版本历史

- **v1.0.0** (2024-10) - 初始版本
  - 完整的参数配置手册
  - 详细的部署指南
  - 全面的执行手册

### 反馈和贡献

如果您发现文档中的错误或有改进建议：
1. 提交Issue到项目仓库
2. 或直接提交Pull Request
3. 联系开发团队

---

## 📞 技术支持

### 获取帮助

1. **查看文档**: 首先查阅相关手册
2. **检查日志**: 查看系统日志了解错误详情
3. **搜索问题**: 在项目Issue中搜索类似问题
4. **提交Issue**: 如果问题未解决，提交新Issue

### 常见问题快速链接

- [配置验证失败](PARAMETER_CONFIG_MANUAL.md#配置验证)
- [依赖安装问题](DEPLOYMENT_MANUAL.md#常见问题)
- [连接失败](EXECUTION_MANUAL.md#1-连接失败)
- [订单被拒绝](EXECUTION_MANUAL.md#3-订单被拒绝)

---

## 📈 学习路径

### 初级用户

**目标**: 能够部署和运行基本的交易系统

1. 完成系统部署
2. 理解基本配置参数
3. 运行示例策略
4. 使用回测系统

**推荐阅读**:
- 部署手册（完整）
- 参数配置手册（基础配置部分）
- 执行手册（快速开始部分）

### 中级用户

**目标**: 能够优化策略和管理风险

1. 深入理解各项配置参数
2. 掌握多种策略的使用
3. 进行参数优化
4. 配置监控和告警

**推荐阅读**:
- 参数配置手册（完整）
- 执行手册（策略管理、监控调试）

### 高级用户

**目标**: 能够开发自定义策略和系统扩展

1. 开发自定义交易策略
2. 集成新的数据源
3. 扩展通知功能
4. 优化系统性能

**推荐阅读**:
- 所有手册（完整）
- 源代码和API文档
- 高级示例代码

---

## ✨ 快速参考

### 常用命令

```bash
# 激活环境
source env/bin/activate  # Linux/macOS
env\Scripts\activate     # Windows

# 检查配置
python check_config.py

# 检查依赖
python check_dependencies.py

# 启动交易
python start_trading.py

# 回测
python backtest.py --strategy mean_reversion --days 30

# 查看日志
tail -f logs/quant_trading.log

# 停止服务
sudo systemctl stop quant-trading  # Linux
```

### 重要文件

```
config.yaml              # 主配置文件
logs/quant_trading.log   # 主日志文件
requirements.txt         # Python依赖
start_trading.py         # 启动脚本
backtest.py             # 回测脚本
```

### 关键配置

```yaml
# 最重要的配置项
lighter:
  api_key_private_key: "your_key"  # 您的私钥
  
risk_management:
  max_position_size: 0.05          # 仓位限制
  max_daily_loss: 0.02             # 日亏损限制
  
strategies:
  mean_reversion:
    enabled: true                   # 启用策略
```

---

**祝您交易顺利！** 🚀

如有任何问题，请参考相应的手册或联系技术支持。

---

**文档维护**: Quant Trading Team  
**最后更新**: 2024年10月  
**版本**: v1.0.0

