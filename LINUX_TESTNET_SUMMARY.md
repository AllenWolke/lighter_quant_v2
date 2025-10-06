# Linux测试环境部署和使用流程总结

## 📋 概述

本文档提供了Lighter量化交易系统在Linux测试环境的完整部署、配置、启动和使用流程。测试环境主要用于策略开发、功能测试和系统验证。

## 🎯 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web前端       │    │   Web后端       │    │   量化交易模块   │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (Python)      │
│   Port: 3000    │    │   Port: 8000    │    │   (模拟交易)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Lighter测试网   │
                    │  (API/WebSocket)│
                    └─────────────────┘
```

## 🚀 快速部署流程

### 第一步：环境准备 (5分钟)

```bash
# 1. 更新系统
sudo apt update && sudo apt upgrade -y

# 2. 安装基础软件
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip git curl wget build-essential

# 3. 安装Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 4. 验证安装
python3 --version
node --version
npm --version
```

### 第二步：项目部署 (5分钟)

```bash
# 1. 创建专用用户 (可选)
sudo useradd -m -s /bin/bash trader-test
sudo usermod -aG sudo trader-test
sudo su - trader-test

# 2. 克隆项目
git clone <项目仓库地址>
cd lighter_quantification_v2

# 3. 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate

# 4. 安装依赖
pip install --upgrade pip
pip install -r requirements.txt
```

### 第三步：配置参数 (3分钟)

```bash
# 1. 复制配置文件
cp config_linux_testnet.yaml config.yaml

# 2. 编辑配置文件
nano config.yaml

# 3. 创建必要目录
mkdir -p logs data backups
chmod 755 logs data backups
```

### 第四步：启动系统 (2分钟)

```bash
# 方式1: 使用启动脚本
chmod +x start_linux_testnet.sh
./start_linux_testnet.sh

# 方式2: 使用Python启动脚本
python start_linux_testnet.py

# 方式3: 使用跨平台启动脚本
python quick_start.py
```

## 📝 详细配置说明

### 核心配置文件: `config_linux_testnet.yaml`

#### Lighter交易所配置
```yaml
lighter:
  base_url: "https://testnet.zklighter.elliot.ai"
  api_key_private_key: "1234567812345678123456781234567812345678123456781234567812345678"
  api_key_index: 3
  account_index: 0
  chain_id: 300
```

#### 交易策略配置
```yaml
trading:
  strategies:
    momentum:
      enabled: true
      long_period: 20
      short_period: 5
      threshold: 0.02
      leverage: 5.0
      position_size: 0.1
```

#### 风险管理配置
```yaml
risk_management:
  max_position_size: 0.2
  max_daily_loss: 0.05
  max_drawdown: 0.15
  stop_loss: 0.03
  max_leverage: 10.0
```

#### 测试环境配置
```yaml
testing:
  paper_trading: true
  paper_balance: 10000.0
  use_mock_data: false
  backtest_mode: false
```

## 🔧 启动方式对比

| 启动方式 | 优点 | 缺点 | 适用场景 |
|---------|------|------|----------|
| Shell脚本 | 快速、自动化 | 仅Linux | 生产环境 |
| Python脚本 | 跨平台、统一 | 需要Python | 开发测试 |
| 手动启动 | 完全控制 | 步骤繁琐 | 调试开发 |
| 系统服务 | 开机自启 | 配置复杂 | 长期运行 |

## 📊 使用功能

### Web界面使用

#### 1. 访问系统
```bash
# 本地访问
http://localhost:3000

# 远程访问
http://your-server-ip:3000
```

#### 2. 登录系统
- 默认用户名: `admin`
- 默认密码: `admin`

#### 3. 主要功能
- **交易面板**: 配置交易参数，选择策略
- **市场数据**: 查看实时价格和K线图
- **持仓管理**: 监控当前持仓和盈亏
- **订单管理**: 查看历史订单和执行状态
- **策略配置**: 调整策略参数和风险设置

### 命令行使用

#### 1. 系统状态检查
```bash
# 检查配置文件
python -c "
from quant_trading.utils.config import Config
config = Config.from_file('config_linux_testnet.yaml')
print('配置加载成功')
print(f'交易市场: {len(config.trading.markets)}')
print(f'启用策略: {sum(1 for s in config.trading.strategies.values() if s.get(\"enabled\", False))}')
"

# 检查进程状态
ps aux | grep python
ps aux | grep node
```

#### 2. 运行回测
```bash
# 动量策略回测
python run_backtest.py --strategy momentum --start-date 2024-01-01 --end-date 2024-01-31

# 均值回归策略回测
python run_backtest.py --strategy mean_reversion --start-date 2024-01-01 --end-date 2024-01-31

# 自定义回测
python run_backtest.py --strategy custom_strategy --start-date 2024-01-01 --end-date 2024-01-31
```

#### 3. 手动执行策略
```bash
# 运行简单交易机器人
python examples/simple_trading_bot.py

# 运行多策略机器人
python examples/multi_strategy_bot.py

# 运行自定义策略
python examples/custom_strategy.py
```

#### 4. 系统监控
```bash
# 查看实时日志
tail -f logs/linux_testnet_trading.log

# 查看错误日志
grep "ERROR" logs/linux_testnet_trading.log

# 查看特定策略日志
grep "momentum" logs/linux_testnet_trading.log

# 系统监控
python monitor_mainnet.py
```

## 🔍 监控和维护

### 日志监控

#### 日志文件位置
```bash
logs/
├── linux_testnet_trading.log  # 主交易日志
├── backend.log               # Web后端日志
├── frontend.log              # Web前端日志
├── backend.pid               # 后端进程ID
└── frontend.pid              # 前端进程ID
```

#### 日志查看命令
```bash
# 实时查看主日志
tail -f logs/linux_testnet_trading.log

# 查看错误日志
grep "ERROR" logs/linux_testnet_trading.log

# 查看警告日志
grep "WARNING" logs/linux_testnet_trading.log

# 查看交易日志
grep "TRADE" logs/linux_testnet_trading.log
```

### 性能监控

#### 系统资源监控
```bash
# 查看内存使用
free -h

# 查看磁盘使用
df -h

# 查看CPU负载
top
htop

# 查看网络连接
netstat -tlnp
```

#### 进程监控
```bash
# 查看Python进程
ps aux | grep python

# 查看Node.js进程
ps aux | grep node

# 查看特定进程
ps -p $(cat logs/trading.pid)
```

### 自动监控脚本

#### 创建监控脚本
```bash
cat > monitor_testnet.sh << 'EOF'
#!/bin/bash
LOG_FILE="logs/monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# 检查交易进程
if pgrep -f "main.py" > /dev/null; then
    echo "[$DATE] Trading system is running" >> $LOG_FILE
else
    echo "[$DATE] ERROR: Trading system is not running" >> $LOG_FILE
fi

# 检查Web服务
if pgrep -f "web_backend" > /dev/null; then
    echo "[$DATE] Web backend is running" >> $LOG_FILE
else
    echo "[$DATE] ERROR: Web backend is not running" >> $LOG_FILE
fi

# 检查磁盘空间
DISK_USAGE=$(df . | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "[$DATE] WARNING: Disk usage is ${DISK_USAGE}%" >> $LOG_FILE
fi
EOF

chmod +x monitor_testnet.sh
```

#### 设置定时监控
```bash
# 添加到crontab (每5分钟检查一次)
(crontab -l 2>/dev/null; echo "*/5 * * * * /path/to/monitor_testnet.sh") | crontab -
```

## 🔧 故障排除

### 常见问题及解决方案

#### 1. 端口冲突
```bash
# 检查端口占用
netstat -tlnp | grep :8000
netstat -tlnp | grep :3000

# 杀死占用进程
sudo kill -9 <PID>

# 或者修改配置文件中的端口
```

#### 2. 权限问题
```bash
# 检查文件权限
ls -la config_linux_testnet.yaml

# 修复权限
chmod 644 config_linux_testnet.yaml
chmod 755 logs data backups
```

#### 3. 依赖问题
```bash
# 重新安装依赖
pip install -r requirements.txt --force-reinstall

# 清理pip缓存
pip cache purge

# 检查依赖版本
pip list | grep -E "(lighter|eth-account|pydantic)"
```

#### 4. 网络连接问题
```bash
# 测试网络连接
ping -c 3 testnet.zklighter.elliot.ai

# 检查DNS解析
nslookup testnet.zklighter.elliot.ai

# 检查防火墙
sudo ufw status
sudo firewall-cmd --list-all
```

#### 5. 服务启动失败
```bash
# 查看详细日志
tail -f logs/trading.log
tail -f logs/backend.log
tail -f logs/frontend.log

# 检查系统服务
sudo systemctl status lighter-trading-test
sudo journalctl -u lighter-trading-test -f
```

## 📈 性能优化

### 系统级优化

#### 内核参数优化
```bash
# 添加优化参数
sudo tee -a /etc/sysctl.conf > /dev/null <<EOF
# 网络优化
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216

# 文件系统优化
fs.file-max = 65536
vm.swappiness = 10
EOF

# 应用配置
sudo sysctl -p
```

#### 环境变量优化
```bash
# 设置环境变量
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1
export PYTHONOPTIMIZE=1

# 添加到 ~/.bashrc
echo 'export PYTHONUNBUFFERED=1' >> ~/.bashrc
echo 'export PYTHONDONTWRITEBYTECODE=1' >> ~/.bashrc
echo 'export PYTHONOPTIMIZE=1' >> ~/.bashrc
```

### 应用级优化

#### 配置文件优化
```yaml
performance:
  data_update_interval: 1
  strategy_execution_interval: 5
  max_concurrent_tasks: 10
  memory_limit: 2048
  cpu_limit: 80
```

#### 日志优化
```yaml
logging:
  level: "INFO"  # 生产环境可设为WARNING
  max_size: "10MB"
  backup_count: 5
  console: false  # 生产环境关闭控制台输出
```

## 🔒 安全注意事项

### 测试环境安全

#### 1. 网络安全
```bash
# 配置防火墙
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 8000/tcp
sudo ufw allow 3000/tcp

# 限制访问IP (可选)
sudo ufw allow from 192.168.1.0/24 to any port 8000
```

#### 2. 文件权限
```bash
# 设置配置文件权限
chmod 644 config_linux_testnet.yaml

# 设置日志目录权限
chmod 755 logs

# 设置数据目录权限
chmod 755 data
```

#### 3. 用户权限
```bash
# 使用专用用户运行
sudo useradd -m -s /bin/bash trader-test
sudo usermod -aG sudo trader-test

# 设置sudo权限
sudo visudo
# 添加: trader-test ALL=(ALL) NOPASSWD: /bin/systemctl restart lighter-trading-test
```

### 数据安全

#### 1. 配置文件备份
```bash
# 创建备份脚本
cat > backup_config.sh << 'EOF'
#!/bin/bash
DATE=$(date '+%Y%m%d_%H%M%S')
cp config_linux_testnet.yaml "backups/config_${DATE}.yaml"
find backups -name "config_*.yaml" -mtime +30 -delete
EOF

chmod +x backup_config.sh

# 添加到crontab (每日备份)
(crontab -l 2>/dev/null; echo "0 2 * * * /path/to/backup_config.sh") | crontab -
```

#### 2. 日志轮转
```bash
# 配置logrotate
sudo tee /etc/logrotate.d/lighter-testnet > /dev/null <<EOF
/path/to/lighter_quantification_v2/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 trader-test trader-test
}
EOF
```

## 📞 技术支持

### 文档资源
- [Linux测试网部署指南](LINUX_TESTNET_DEPLOYMENT_GUIDE.md)
- [Linux主网部署指南](LINUX_MAINNET_DEPLOYMENT_GUIDE.md)
- [配置文件示例](config_linux_testnet.yaml)
- [启动脚本](start_linux_testnet.sh)

### 联系方式
- 技术支持: support@yourdomain.com
- 紧急联系: +86-xxx-xxxx-xxxx
- 文档更新: 请参考项目README

### 社区支持
- GitHub Issues: 报告问题和功能请求
- 技术论坛: 技术讨论和经验分享
- 定期更新: 关注项目更新和公告

---

**注意**: 本指南适用于Linux测试环境部署。测试环境主要用于策略开发、回测和功能验证，不建议用于实际交易。如需实际交易，请使用Linux主网环境部署指南。

## 🎯 快速参考

### 常用命令
```bash
# 启动系统
./start_linux_testnet.sh

# 查看日志
tail -f logs/linux_testnet_trading.log

# 运行回测
python run_backtest.py --strategy momentum --start-date 2024-01-01 --end-date 2024-01-31

# 系统监控
python monitor_mainnet.py

# 停止服务
pkill -f "main.py"
pkill -f "web_backend"
pkill -f "npm start"
```

### 配置文件位置
- 主配置: `config_linux_testnet.yaml`
- 日志目录: `logs/`
- 数据目录: `data/`
- 备份目录: `backups/`

### 访问地址
- Web前端: `http://localhost:3000`
- Web后端: `http://localhost:8000`
- API文档: `http://localhost:8000/docs`
