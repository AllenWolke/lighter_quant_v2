# Linux主网环境部署指南

## 📋 系统要求

### 硬件要求
- **CPU**: Intel i5 或 AMD Ryzen 5 以上 (推荐 8核以上)
- **内存**: 16GB RAM 以上 (推荐 32GB)
- **存储**: 100GB SSD 以上
- **网络**: 稳定的高速互联网连接 (推荐专线)

### 软件要求
- **操作系统**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **Python**: 3.9+ (推荐 3.11)
- **Node.js**: 16+ (用于Web前端)
- **Git**: 用于代码版本控制
- **Docker**: 可选，用于容器化部署

## 🚀 部署步骤

### 第一步：系统准备

#### 1.1 更新系统
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
# 或者对于CentOS 8+
sudo dnf update -y
```

#### 1.2 安装基础软件
```bash
# Ubuntu/Debian
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip git curl wget build-essential

# CentOS/RHEL
sudo yum install -y python311 python311-devel git curl wget gcc gcc-c++ make
# 或者对于CentOS 8+
sudo dnf install -y python3.11 python3.11-devel git curl wget gcc gcc-c++ make
```

#### 1.3 安装Node.js
```bash
# 使用NodeSource仓库安装Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 验证安装
node --version
npm --version
```

### 第二步：项目部署

#### 2.1 创建专用用户
```bash
# 创建交易系统专用用户
sudo useradd -m -s /bin/bash trader
sudo usermod -aG sudo trader

# 切换到交易用户
sudo su - trader
```

#### 2.2 克隆项目
```bash
# 克隆项目
git clone <项目仓库地址>
cd lighter_quantification_v2

# 设置目录权限
chmod -R 755 .
```

#### 2.3 创建虚拟环境
```bash
# 创建Python虚拟环境
python3.11 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级pip
pip install --upgrade pip
```

### 第三步：依赖安装

#### 3.1 安装Python依赖
```bash
# 安装系统级依赖 (Ubuntu/Debian)
sudo apt install -y libssl-dev libffi-dev python3-dev build-essential

# 安装Python包
pip install -r requirements.txt

# 验证关键依赖
python -c "
import lighter
import eth_account
import pydantic
from quant_trading.core.trading_engine import TradingEngine
print('✅ 所有依赖安装成功')
"
```

#### 3.2 安装前端依赖
```bash
# 安装前端依赖
cd web_frontend
npm install
cd ..
```

### 第四步：配置参数

#### 4.1 创建主网配置
```bash
# 复制主网配置模板
cp config_mainnet.yaml.example config_mainnet.yaml
```

#### 4.2 配置主网参数
编辑 `config_mainnet.yaml` 文件：

```yaml
# 主网配置
lighter:
  base_url: "https://mainnet.zklighter.elliot.ai"
  api_key_private_key: "你的主网私钥"  # ⚠️ 请妥善保管
  api_key_index: 0
  account_index: 0

# 交易参数
trading:
  markets:
    - symbol: "ETH"
      market_id: 0
      base_asset: "ETH"
      quote_asset: "USDC"
    - symbol: "BTC"
      market_id: 1
      base_asset: "BTC"
      quote_asset: "USDC"
  
  strategies:
    momentum:
      enabled: true
      long_period: 20
      short_period: 5
      threshold: 0.02
      leverage: 3.0  # 主网建议降低杠杆
      position_size: 0.05  # 主网建议降低仓位
    
    mean_reversion:
      enabled: true
      period: 14
      threshold: 2.0
      leverage: 2.0
      position_size: 0.03

# 严格的风险管理
risk_management:
  max_position_size: 0.1  # 最大仓位10%
  max_daily_loss: 0.02   # 最大日亏损2%
  max_drawdown: 0.05     # 最大回撤5%
  stop_loss: 0.02        # 止损2%
  max_leverage: 5.0      # 最大杠杆5倍

# 通知配置
notifications:
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    username: "你的邮箱@gmail.com"
    password: "你的应用密码"
    to_email: "接收邮箱@gmail.com"
  
  # 紧急通知配置
  emergency:
    enabled: true
    max_daily_notifications: 10
    critical_events: ["stop_loss_triggered", "max_drawdown_reached", "system_error"]

# 日志配置
logging:
  level: "INFO"
  file: "/home/trader/logs/mainnet_trading.log"
  max_size: "50MB"
  backup_count: 10
  
  # 审计日志
  audit:
    enabled: true
    file: "/home/trader/logs/audit.log"
    log_trades: true
    log_errors: true

# 数据库配置
database:
  url: "sqlite:///home/trader/data/trading.db"
  backup_enabled: true
  backup_interval: "1h"
  retention_days: 30
```

#### 4.3 创建必要目录
```bash
# 创建日志目录
mkdir -p /home/trader/logs
mkdir -p /home/trader/data
mkdir -p /home/trader/backups

# 设置权限
chmod 755 /home/trader/logs
chmod 755 /home/trader/data
chmod 700 /home/trader/backups  # 备份目录更严格权限
```

### 第五步：安全配置

#### 5.1 配置防火墙
```bash
# Ubuntu/Debian (UFW)
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 8000/tcp  # Web后端端口
sudo ufw allow 3000/tcp  # Web前端端口
sudo ufw status

# CentOS/RHEL (firewalld)
sudo systemctl enable firewalld
sudo systemctl start firewalld
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --reload
```

#### 5.2 配置SSL证书 (生产环境)
```bash
# 安装certbot
sudo apt install certbot  # Ubuntu/Debian
# sudo yum install certbot  # CentOS/RHEL

# 获取SSL证书
sudo certbot certonly --standalone -d yourdomain.com
```

#### 5.3 配置系统服务
```bash
# 创建系统服务文件
sudo tee /etc/systemd/system/lighter-trading.service > /dev/null <<EOF
[Unit]
Description=Lighter Trading System
After=network.target

[Service]
Type=simple
User=trader
Group=trader
WorkingDirectory=/home/trader/lighter_quantification_v2
Environment=PATH=/home/trader/lighter_quantification_v2/venv/bin
ExecStart=/home/trader/lighter_quantification_v2/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 重新加载systemd
sudo systemctl daemon-reload
```

### 第六步：启动系统

#### 6.1 预启动检查
```bash
# 检查配置文件
python -c "
from quant_trading.utils.config import Config
try:
    config = Config.from_file('config_mainnet.yaml')
    print('✅ 配置文件正确')
    print(f'交易市场: {len(config.trading.markets)}')
    print(f'启用策略: {sum(1 for s in config.trading.strategies.values() if s.get(\"enabled\", False))}')
except Exception as e:
    print(f'❌ 配置错误: {e}')
"

# 检查网络连接
ping -c 3 mainnet.zklighter.elliot.ai

# 检查磁盘空间
df -h /home/trader
```

#### 6.2 启动Web系统
```bash
# 启动后端 (后台运行)
cd web_backend
nohup python main.py > ../logs/backend.log 2>&1 &

# 启动前端 (后台运行)
cd ../web_frontend
nohup npm start > ../logs/frontend.log 2>&1 &

# 检查进程
ps aux | grep python
ps aux | grep node
```

#### 6.3 启动交易系统
```bash
# 方式1: 直接启动
python main.py --config config_mainnet.yaml

# 方式2: 使用系统服务
sudo systemctl start lighter-trading
sudo systemctl status lighter-trading

# 方式3: 使用专用脚本
python start_mainnet.py
```

### 第七步：监控和维护

#### 7.1 实时监控
```bash
# 查看系统日志
tail -f logs/mainnet_trading.log

# 查看系统状态
python monitor_mainnet.py

# 查看资源使用
htop
# 或者
top -u trader
```

#### 7.2 自动监控脚本
```bash
# 创建监控脚本
cat > monitor_system.sh << 'EOF'
#!/bin/bash
LOG_FILE="/home/trader/logs/monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# 检查交易进程
if pgrep -f "main.py" > /dev/null; then
    echo "[$DATE] Trading system is running" >> $LOG_FILE
else
    echo "[$DATE] ERROR: Trading system is not running" >> $LOG_FILE
    # 发送告警邮件
    echo "Trading system stopped" | mail -s "CRITICAL: Trading System Down" admin@yourdomain.com
fi

# 检查Web服务
if pgrep -f "web_backend" > /dev/null; then
    echo "[$DATE] Web backend is running" >> $LOG_FILE
else
    echo "[$DATE] ERROR: Web backend is not running" >> $LOG_FILE
fi

# 检查磁盘空间
DISK_USAGE=$(df /home/trader | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "[$DATE] WARNING: Disk usage is ${DISK_USAGE}%" >> $LOG_FILE
fi

# 检查内存使用
MEM_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
if [ $MEM_USAGE -gt 90 ]; then
    echo "[$DATE] WARNING: Memory usage is ${MEM_USAGE}%" >> $LOG_FILE
fi
EOF

chmod +x monitor_system.sh

# 添加到crontab (每5分钟检查一次)
(crontab -l 2>/dev/null; echo "*/5 * * * * /home/trader/lighter_quantification_v2/monitor_system.sh") | crontab -
```

#### 7.3 备份策略
```bash
# 创建备份脚本
cat > backup_system.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/trader/backups"
DATE=$(date '+%Y%m%d_%H%M%S')

# 备份配置文件
cp config_mainnet.yaml "$BACKUP_DIR/config_$DATE.yaml"

# 备份数据库
cp data/trading.db "$BACKUP_DIR/trading_$DATE.db"

# 备份日志 (最近7天)
find logs -name "*.log" -mtime -7 -exec cp {} "$BACKUP_DIR/" \;

# 清理旧备份 (保留30天)
find "$BACKUP_DIR" -name "*.yaml" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.db" -mtime +30 -delete

echo "Backup completed: $DATE"
EOF

chmod +x backup_system.sh

# 添加到crontab (每天凌晨2点备份)
(crontab -l 2>/dev/null; echo "0 2 * * * /home/trader/lighter_quantification_v2/backup_system.sh") | crontab -
```

## 🔧 故障排除

### 常见问题

#### 1. 权限问题
```bash
# 检查文件权限
ls -la /home/trader/lighter_quantification_v2/

# 修复权限
chown -R trader:trader /home/trader/lighter_quantification_v2/
chmod -R 755 /home/trader/lighter_quantification_v2/
chmod 600 config_mainnet.yaml  # 配置文件更严格权限
```

#### 2. 网络连接问题
```bash
# 测试网络连接
curl -I https://mainnet.zklighter.elliot.ai

# 检查DNS解析
nslookup mainnet.zklighter.elliot.ai

# 检查防火墙
sudo ufw status  # Ubuntu
sudo firewall-cmd --list-all  # CentOS
```

#### 3. 服务启动失败
```bash
# 查看服务状态
sudo systemctl status lighter-trading

# 查看详细日志
sudo journalctl -u lighter-trading -f

# 重启服务
sudo systemctl restart lighter-trading
```

#### 4. 内存不足
```bash
# 检查内存使用
free -h

# 检查交换空间
swapon -s

# 创建交换文件 (如果需要)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 📊 性能优化

### 系统优化
```bash
# 优化内核参数
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

### 应用优化
```bash
# 设置环境变量
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

# 优化Python性能
export PYTHONOPTIMIZE=1
```

## ⚠️ 安全注意事项

### 主网安全
1. **私钥安全**: 
   - 使用硬件钱包存储主网私钥
   - 定期轮换API密钥
   - 不要在日志中记录私钥信息

2. **网络安全**:
   - 使用VPN或专线连接
   - 配置防火墙规则
   - 定期更新系统补丁

3. **访问控制**:
   - 限制SSH访问IP
   - 使用密钥认证
   - 定期检查访问日志

4. **数据备份**:
   - 每日自动备份
   - 异地备份重要数据
   - 测试备份恢复流程

### 监控告警
1. 设置关键指标监控
2. 配置邮件/短信告警
3. 建立应急响应流程
4. 定期进行故障演练

## 📞 技术支持

### 紧急联系
- 系统管理员: admin@yourdomain.com
- 技术支持: support@yourdomain.com
- 紧急电话: +86-xxx-xxxx-xxxx

### 维护窗口
- 每周维护: 周日 02:00-04:00 UTC
- 紧急维护: 24/7
- 计划维护: 提前24小时通知

更多详细信息请参考项目文档或联系技术支持团队。
