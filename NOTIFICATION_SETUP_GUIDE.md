# 通知功能配置指南

## 📧 通知功能概述

通知功能模块为量化交易系统提供实时消息推送服务，支持在以下情况下发送通知：

- ✅ 交易执行完成
- ⚠️ 止损价格触发
- 🎯 止盈价格触发
- 🚨 风险限制超出
- ❌ 系统错误发生
- 📊 策略信号生成
- 💰 账户状态变化

## 🔧 配置步骤

### 步骤1: 邮件服务配置

#### 1.1 Gmail配置（推荐）

1. **启用两步验证**
   - 访问 [Google账户设置](https://myaccount.google.com/)
   - 启用两步验证

2. **生成应用密码**
   - 访问 [应用密码页面](https://myaccount.google.com/apppasswords)
   - 选择"邮件"和"其他设备"
   - 生成16位应用密码

3. **配置参数**
   ```yaml
   email:
     enabled: true
     smtp_server: "smtp.gmail.com"
     smtp_port: 587
     username: "your_email@gmail.com"
     password: "your_16_digit_app_password"
     from_email: "your_email@gmail.com"
     to_emails: ["recipient1@gmail.com", "recipient2@gmail.com"]
   ```

#### 1.2 其他邮件服务配置

**Outlook/Hotmail:**
```yaml
email:
  smtp_server: "smtp-mail.outlook.com"
  smtp_port: 587
```

**QQ邮箱:**
```yaml
email:
  smtp_server: "smtp.qq.com"
  smtp_port: 587
```

**163邮箱:**
```yaml
email:
  smtp_server: "smtp.163.com"
  smtp_port: 25
```

### 步骤2: 通知参数配置

#### 2.1 基础配置
```yaml
notifications:
  enabled: true
  batch_size: 5          # 批量发送大小
  batch_interval: 60     # 批量发送间隔（秒）
```

#### 2.2 频率限制配置
```yaml
rate_limits:
  trade_executed:        # 交易执行通知
    time_window: 300     # 时间窗口（秒）
    max_count: 20        # 最大数量
  stop_loss:             # 止损通知
    time_window: 300
    max_count: 10
  take_profit:           # 止盈通知
    time_window: 300
    max_count: 10
  system_error:          # 系统错误通知
    time_window: 60
    max_count: 5
  risk_limit:            # 风险限制通知
    time_window: 60
    max_count: 2
```

#### 2.3 邮件过滤配置
```yaml
email:
  min_level: "info"      # 最小通知级别: info, warning, error, critical
  allowed_types: []      # 允许的通知类型，空表示全部
```

## 🧪 测试通知功能

### 方法1: 使用测试脚本
```bash
# 运行通知测试
python test_notifications.py

# 选择测试模式
# 1. 使用配置文件测试
# 2. 交互式配置测试
```

### 方法2: 运行示例
```bash
# 运行通知示例
python examples/notification_example.py
```

### 方法3: 手动测试
```python
from quant_trading import Config
from quant_trading.notifications import NotificationManager

# 加载配置
config = Config.from_file("config.yaml")

# 创建通知管理器
notification_manager = NotificationManager(config.notifications_config)

# 发送测试通知
await notification_manager.send_notification(
    notification_type=NotificationType.SYSTEM_ERROR,
    level=NotificationLevel.INFO,
    title="测试通知",
    message="这是一封测试邮件"
)

# 关闭通知管理器
await notification_manager.close()
```

## 📊 通知类型说明

### 1. 交易执行通知
```python
await notification_manager.send_trade_executed(
    symbol="BTC_USDT",
    side="buy",
    quantity=0.1,
    price=50000.0,
    order_id="BTC_001"
)
```

### 2. 止损触发通知
```python
await notification_manager.send_stop_loss_triggered(
    symbol="BTC_USDT",
    price=48000.0,
    order_id="BTC_001"
)
```

### 3. 止盈触发通知
```python
await notification_manager.send_take_profit_triggered(
    symbol="BTC_USDT",
    price=52000.0,
    order_id="BTC_001"
)
```

### 4. 风险限制通知
```python
await notification_manager.send_risk_limit_exceeded(
    risk_type="max_position_size",
    current_value=0.15,
    limit_value=0.10,
    message="仓位大小超出限制"
)
```

### 5. 系统错误通知
```python
await notification_manager.send_system_error(
    error_message="API连接超时",
    component="data_manager"
)
```

### 6. 策略信号通知
```python
await notification_manager.send_strategy_signal(
    strategy_name="UT Bot",
    signal="BUY",
    symbol="BTC_USDT",
    confidence=0.85
)
```

### 7. 账户警告通知
```python
await notification_manager.send_account_alert(
    alert_type="low_balance",
    message="账户余额不足",
    current_balance=100.0
)
```

## 🎨 邮件模板

### HTML邮件模板
通知系统支持美观的HTML邮件模板，包含：
- 响应式设计
- 颜色编码的通知级别
- 详细的数据表格
- 专业的邮件头部和尾部

### 文本邮件模板
同时提供纯文本版本，确保所有邮件客户端都能正常显示。

## ⚙️ 高级配置

### 1. 自定义邮件模板
```python
# 在EmailNotifier中自定义模板
def _create_custom_html_content(self, notification):
    # 自定义HTML模板
    pass
```

### 2. 多邮箱配置
```yaml
email:
  to_emails:
    - "trader1@example.com"
    - "trader2@example.com"
    - "manager@example.com"
```

### 3. 条件通知
```yaml
email:
  min_level: "warning"  # 只发送警告级别以上的通知
  allowed_types:
    - "trade_executed"
    - "stop_loss"
    - "system_error"
```

## 🔍 故障排除

### 常见问题

#### 1. 邮件发送失败
```
错误: SMTP发送失败
解决: 检查邮箱用户名、密码和SMTP设置
```

#### 2. 认证失败
```
错误: 认证失败
解决: 使用应用密码而不是账户密码
```

#### 3. 连接超时
```
错误: 连接超时
解决: 检查网络连接和防火墙设置
```

#### 4. 邮件被标记为垃圾邮件
```
解决: 将发送邮箱添加到白名单
```

### 调试方法

#### 1. 启用详细日志
```yaml
log:
  level: "DEBUG"
```

#### 2. 检查配置
```python
# 验证邮件配置
config = Config.from_file("config.yaml")
email_config = config.notifications_config.get("email", {})
print(f"SMTP服务器: {email_config.get('smtp_server')}")
print(f"端口: {email_config.get('smtp_port')}")
print(f"用户名: {email_config.get('username')}")
```

#### 3. 测试连接
```python
import smtplib
import ssl

# 测试SMTP连接
context = ssl.create_default_context()
with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls(context=context)
    server.login("your_email@gmail.com", "your_app_password")
    print("连接成功")
```

## 📈 性能优化

### 1. 批量发送
```yaml
notifications:
  batch_size: 10      # 增加批量大小
  batch_interval: 30  # 减少发送间隔
```

### 2. 频率限制
```yaml
rate_limits:
  trade_executed:
    time_window: 600   # 增加时间窗口
    max_count: 50      # 增加最大数量
```

### 3. 过滤设置
```yaml
email:
  min_level: "warning"  # 提高最小级别
  allowed_types:        # 限制通知类型
    - "stop_loss"
    - "system_error"
```

## 🛡️ 安全建议

### 1. 密码安全
- 使用应用密码而不是账户密码
- 定期更换应用密码
- 不要在代码中硬编码密码

### 2. 邮箱安全
- 使用专用的交易监控邮箱
- 启用两步验证
- 定期检查邮箱安全设置

### 3. 网络安全
- 使用安全的网络连接
- 避免在公共WiFi下发送敏感信息
- 考虑使用VPN

## 📞 技术支持

如果遇到问题，请：

1. 查看日志文件
2. 运行测试脚本
3. 检查网络连接
4. 验证邮箱配置
5. 联系技术支持

## 🎉 完成配置

配置完成后，您将收到以下类型的通知：

- 📧 交易执行确认
- ⚠️ 风险警告提醒
- 🎯 止盈止损通知
- ❌ 系统错误报警
- 📊 策略信号推送
- 💰 账户状态更新

现在您的量化交易系统具备了完整的通知功能！
