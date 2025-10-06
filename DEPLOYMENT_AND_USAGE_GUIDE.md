# Lighter量化交易系统部署和使用指南

## 📋 概述

本指南提供了Lighter量化交易系统在Windows测试环境和Linux主网生产环境的完整部署、配置、启动和使用流程。

## 🎯 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web前端       │    │   Web后端       │    │   量化交易模块   │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (Python)      │
│   Port: 3000    │    │   Port: 8000    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Lighter交易所   │
                    │  (API/WebSocket)│
                    └─────────────────┘
```

## 🖥️ Windows测试环境部署

### 系统要求
- **操作系统**: Windows 10/11 (64位)
- **Python**: 3.9+ (推荐 3.11)
- **内存**: 8GB RAM 以上
- **存储**: 20GB 可用空间
- **网络**: 稳定的互联网连接

### 部署步骤

#### 1. 环境准备
```bash
# 安装Python 3.11
# 访问 https://www.python.org/downloads/
# 勾选 "Add Python to PATH"

# 验证安装
python --version
pip --version
```

#### 2. 项目部署
```bash
# 克隆项目
git clone <项目仓库地址>
cd lighter_quantification_v2

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate.bat

# 安装依赖
pip install -r requirements.txt
```

#### 3. 配置参数
```bash
# 复制配置文件
copy config_windows_testnet.yaml config.yaml

# 编辑配置文件 (使用文本编辑器)
notepad config.yaml
```

**关键配置项**:
```yaml
lighter:
  base_url: "https://testnet.zklighter.elliot.ai"
  api_key_private_key: "你的测试网私钥"
  api_key_index: 3
  account_index: 0

trading:
  strategies:
    momentum:
      enabled: true
      leverage: 5.0
      position_size: 0.1

risk_management:
  max_position_size: 0.2
  max_daily_loss: 0.05
  max_drawdown: 0.15
```

#### 4. 启动系统

**方式1: 使用启动脚本**
```bash
# 运行Windows启动脚本
start_windows_testnet.bat
```

**方式2: 使用Python启动脚本**
```bash
# 运行跨平台启动脚本
python quick_start.py
```

**方式3: 手动启动**
```bash
# 启动Web后端
cd web_backend
python main.py

# 新开终端，启动Web前端
cd web_frontend
npm install
npm start

# 新开终端，启动交易系统
python main.py
```

#### 5. 使用功能

**Web界面使用**:
1. 打开浏览器访问 `http://localhost:3000`
2. 登录系统 (默认: admin/admin)
3. 配置交易参数
4. 选择交易策略
5. 启动交易

**命令行使用**:
```bash
# 运行回测
python run_backtest.py --strategy momentum --start-date 2024-01-01 --end-date 2024-01-31

# 运行简单交易机器人
python examples/simple_trading_bot.py
```

### Windows平台限制
⚠️ **重要提醒**:
- Windows平台不支持实际交易
- 仅用于策略开发、回测和Web界面测试
- Lighter签名器只支持Linux/macOS

## 🐧 Linux主网环境部署

### 系统要求
- **操作系统**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **Python**: 3.9+ (推荐 3.11)
- **内存**: 16GB RAM 以上 (推荐 32GB)
- **存储**: 100GB SSD 以上
- **网络**: 稳定的高速互联网连接

### 部署步骤

#### 1. 系统准备
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3.11-dev git curl wget build-essential

# CentOS/RHEL
sudo yum update -y
sudo yum install -y python311 python311-devel git curl wget gcc gcc-c++ make
```

#### 2. 创建专用用户
```bash
# 创建交易系统专用用户
sudo useradd -m -s /bin/bash trader
sudo usermod -aG sudo trader
sudo su - trader
```

#### 3. 项目部署
```bash
# 克隆项目
git clone <项目仓库地址>
cd lighter_quantification_v2

# 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 4. 配置参数
```bash
# 复制主网配置
cp config_linux_mainnet.yaml config.yaml

# 编辑配置文件
nano config.yaml
```

**关键配置项**:
```yaml
lighter:
  base_url: "https://mainnet.zklighter.elliot.ai"
  api_key_private_key: "你的主网私钥"  # ⚠️ 请妥善保管
  api_key_index: 0
  account_index: 0

trading:
  strategies:
    momentum:
      enabled: true
      leverage: 3.0      # 主网建议降低杠杆
      position_size: 0.05 # 主网建议降低仓位

risk_management:
  max_position_size: 0.1  # 更保守的仓位限制
  max_daily_loss: 0.02   # 2%日亏损限制
  max_drawdown: 0.05     # 5%最大回撤
  stop_loss: 0.02        # 2%止损
```

#### 5. 安全配置
```bash
# 配置防火墙
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 8000/tcp
sudo ufw allow 3000/tcp

# 设置文件权限
chmod 600 config.yaml
chmod 755 logs
chmod 700 backups
```

#### 6. 启动系统

**方式1: 使用启动脚本**
```bash
# 运行Linux启动脚本
./start_linux_mainnet.sh
```

**方式2: 使用Python启动脚本**
```bash
# 运行跨平台启动脚本
python quick_start.py
```

**方式3: 系统服务启动**
```bash
# 创建系统服务
sudo systemctl start lighter-trading
sudo systemctl enable lighter-trading

# 查看服务状态
sudo systemctl status lighter-trading
```

**方式4: 手动启动**
```bash
# 启动Web后端 (后台运行)
nohup python3 main.py --config config.yaml > logs/trading.log 2>&1 &

# 启动Web前端 (后台运行)
cd web_frontend
nohup npm start > ../logs/frontend.log 2>&1 &
```

#### 7. 使用功能

**Web界面使用**:
1. 打开浏览器访问 `http://your-server:3000`
2. 登录系统
3. 配置交易参数
4. 选择交易策略
5. 启动交易

**命令行使用**:
```bash
# 查看系统状态
python monitor_mainnet.py

# 运行回测
python run_backtest.py --strategy momentum --start-date 2024-01-01 --end-date 2024-01-31

# 手动执行策略
python examples/simple_trading_bot.py
```

## 🔧 配置文件说明

### 通用配置项

#### 交易配置
```yaml
trading:
  markets:              # 交易市场
    - symbol: "ETH"     # 交易对符号
      market_id: 0      # 市场ID
      base_asset: "ETH" # 基础资产
      quote_asset: "USDC" # 计价资产
  
  strategies:           # 交易策略
    momentum:           # 策略名称
      enabled: true     # 是否启用
      leverage: 3.0     # 杠杆倍数
      position_size: 0.05 # 仓位大小
```

#### 风险管理配置
```yaml
risk_management:
  max_position_size: 0.1  # 最大仓位大小
  max_daily_loss: 0.02   # 最大日亏损
  max_drawdown: 0.05     # 最大回撤
  stop_loss: 0.02        # 止损百分比
  max_leverage: 5.0      # 最大杠杆
```

#### 通知配置
```yaml
notifications:
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    username: "your_email@gmail.com"
    password: "your_app_password"
    to_email: "recipient@gmail.com"
```

### 平台特定配置

#### Windows测试环境
```yaml
# Windows特定配置
windows:
  encoding: "utf-8"
  path_separator: "\\"
  temp_dir: "C:\\temp\\lighter_trading"

# 测试配置
testing:
  paper_trading: true      # 模拟交易
  paper_balance: 10000.0   # 模拟资金
  use_mock_data: false     # 使用模拟数据
```

#### Linux主网环境
```yaml
# Linux特定配置
linux:
  user: "trader"
  group: "trader"
  systemd_service: true
  service_name: "lighter-trading"

# 生产配置
production:
  mode: "production"
  monitoring: true
  alerting: true
  auto_recovery: true
```

## 🚀 启动方式对比

| 启动方式 | Windows测试 | Linux主网 | 优点 | 缺点 |
|---------|------------|-----------|------|------|
| 启动脚本 | ✅ | ✅ | 简单易用，自动化检查 | 平台特定 |
| Python脚本 | ✅ | ✅ | 跨平台，统一界面 | 需要Python环境 |
| 手动启动 | ✅ | ✅ | 完全控制，调试方便 | 步骤繁琐 |
| 系统服务 | ❌ | ✅ | 开机自启，进程管理 | 配置复杂 |

## 📊 监控和维护

### 日志监控
```bash
# 查看实时日志
tail -f logs/trading.log

# 查看错误日志
grep "ERROR" logs/trading.log

# 查看特定策略日志
grep "momentum" logs/trading.log
```

### 性能监控
```bash
# Linux系统监控
htop
top -u trader

# Windows系统监控
# 使用任务管理器或PowerShell
Get-Process python | Select-Object ProcessName,CPU,WorkingSet
```

### 自动监控脚本
```bash
# 创建监控脚本 (Linux)
cat > monitor_system.sh << 'EOF'
#!/bin/bash
# 检查进程状态
if pgrep -f "main.py" > /dev/null; then
    echo "交易系统运行正常"
else
    echo "交易系统已停止"
    # 发送告警
fi
EOF

chmod +x monitor_system.sh

# 添加到crontab
(crontab -l 2>/dev/null; echo "*/5 * * * * /path/to/monitor_system.sh") | crontab -
```

## 🔒 安全注意事项

### 私钥安全
1. **测试网**: 使用测试私钥，定期更换
2. **主网**: 使用硬件钱包，定期轮换API密钥
3. **存储**: 加密存储，不在日志中记录
4. **备份**: 安全备份，异地存储

### 网络安全
1. **防火墙**: 配置适当的防火墙规则
2. **VPN**: 使用VPN或专线连接
3. **SSL**: 生产环境使用HTTPS
4. **访问控制**: 限制SSH访问IP

### 系统安全
1. **用户权限**: 使用专用用户运行
2. **文件权限**: 设置适当的文件权限
3. **系统更新**: 定期更新系统补丁
4. **监控**: 设置安全监控和告警

## 🆘 故障排除

### 常见问题

#### 1. 连接问题
```bash
# 测试网络连接
ping testnet.zklighter.elliot.ai  # 测试网
ping mainnet.zklighter.elliot.ai  # 主网

# 检查DNS解析
nslookup testnet.zklighter.elliot.ai
```

#### 2. 依赖问题
```bash
# 重新安装依赖
pip install -r requirements.txt --force-reinstall

# 清理pip缓存
pip cache purge
```

#### 3. 配置问题
```bash
# 验证配置文件
python -c "
import yaml
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
print('配置文件格式正确')
"
```

#### 4. 权限问题
```bash
# Linux权限修复
chown -R trader:trader /home/trader/lighter_quantification_v2/
chmod -R 755 /home/trader/lighter_quantification_v2/
chmod 600 config.yaml
```

## 📞 技术支持

### 文档资源
- [Windows测试环境部署指南](WINDOWS_TESTNET_DEPLOYMENT_GUIDE.md)
- [Linux主网环境部署指南](LINUX_MAINNET_DEPLOYMENT_GUIDE.md)
- [配置文件示例](config_windows_testnet.yaml)
- [启动脚本](start_windows_testnet.bat)

### 联系方式
- 技术支持: support@yourdomain.com
- 紧急联系: +86-xxx-xxxx-xxxx
- 文档更新: 请参考项目README

### 社区支持
- GitHub Issues: 报告问题和功能请求
- 技术论坛: 技术讨论和经验分享
- 定期更新: 关注项目更新和公告

---

**注意**: 本指南提供了完整的部署和使用流程，但实际部署时请根据具体环境进行调整。生产环境部署前请务必进行充分的测试和验证。
