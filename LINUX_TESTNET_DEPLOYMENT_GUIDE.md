# Linux测试环境部署指南

## 📋 系统要求

### 硬件要求
- **CPU**: Intel i3 或 AMD Ryzen 3 以上
- **内存**: 4GB RAM 以上 (推荐 8GB)
- **存储**: 20GB 可用空间
- **网络**: 稳定的互联网连接

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

#### 2.1 创建专用用户 (可选但推荐)
```bash
# 创建测试环境专用用户
sudo useradd -m -s /bin/bash trader-test
sudo usermod -aG sudo trader-test

# 切换到测试用户
sudo su - trader-test
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

#### 4.1 创建测试网配置
```bash
# 复制测试网配置模板
cp config_windows_testnet.yaml config_linux_testnet.yaml
```

#### 4.2 配置测试网参数
编辑 `config_linux_testnet.yaml` 文件：

```yaml
# Linux测试网配置
lighter:
  # 测试网地址
  base_url: "https://testnet.zklighter.elliot.ai"
  # 测试网私钥 (从system_setup.py获取)
  api_key_private_key: "1234567812345678123456781234567812345678123456781234567812345678"
  # API密钥索引
  api_key_index: 3
  # 账户索引
  account_index: 0
  # 链ID (测试网: 300, 主网: 304)
  chain_id: 300

# 交易配置
trading:
  # 交易市场配置
  markets:
    - symbol: "ETH"
      market_id: 0
      base_asset: "ETH"
      quote_asset: "USDC"
      min_order_size: 0.001
      max_order_size: 100.0
      tick_size: 0.01

  # 交易策略配置
  strategies:
    # 动量策略
    momentum:
      enabled: true
      long_period: 20
      short_period: 5
      threshold: 0.02
      leverage: 5.0
      position_size: 0.1
      max_orders: 10
      order_timeout: 300
    
    # 均值回归策略
    mean_reversion:
      enabled: false
      period: 14
      threshold: 2.0
      leverage: 3.0
      position_size: 0.05
      max_orders: 5
      order_timeout: 300

# 风险管理配置
risk_management:
  # 最大仓位大小 (占总资金的百分比)
  max_position_size: 0.2
  # 最大日亏损限制
  max_daily_loss: 0.05
  # 最大回撤限制
  max_drawdown: 0.15
  # 止损百分比
  stop_loss: 0.03
  # 最大杠杆倍数
  max_leverage: 10.0

# 数据源配置
data_sources:
  # Lighter数据源
  lighter:
    enabled: true
    websocket_url: "wss://testnet.zklighter.elliot.ai/ws"
    update_interval: 1
    max_retries: 5
    retry_delay: 5

# 通知配置
notifications:
  # 邮件通知
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    use_tls: true
    username: "your_email@gmail.com"
    password: "your_app_password"
    to_email: "recipient@gmail.com"
    
    # 通知类型
    notify_on:
      - trade_executed
      - stop_loss_triggered
      - daily_summary
      - system_error

# 日志配置
logging:
  level: "INFO"
  file: "logs/linux_testnet_trading.log"
  max_size: "10MB"
  backup_count: 5
  console: true

# Web界面配置
web:
  # 后端配置
  backend:
    host: "0.0.0.0"
    port: 8000
    debug: true
    reload: true
  
  # 前端配置
  frontend:
    host: "0.0.0.0"
    port: 3000
    api_url: "http://localhost:8000"

# 测试配置
testing:
  # 模拟交易模式
  paper_trading: true
  # 模拟资金
  paper_balance: 10000.0
  # 测试数据源
  use_mock_data: false
  # 回测模式
  backtest_mode: false

# Linux特定配置
linux:
  # 用户配置
  user: "trader-test"
  group: "trader-test"
  # 目录权限
  permissions:
    config_dir: "644"
    log_dir: "755"
    data_dir: "755"
  # 进程管理
  process_management: "manual"
```

#### 4.3 获取测试网私钥
```bash
# 运行系统设置脚本获取测试私钥
python examples/system_setup.py
```

#### 4.4 创建必要目录
```bash
# 创建日志目录
mkdir -p logs
mkdir -p data
mkdir -p backups

# 设置权限
chmod 755 logs
chmod 755 data
chmod 755 backups
```

### 第五步：安全配置

#### 5.1 配置防火墙 (可选)
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

#### 5.2 配置系统服务 (可选)
```bash
# 创建系统服务文件
sudo tee /etc/systemd/system/lighter-trading-test.service > /dev/null <<EOF
[Unit]
Description=Lighter Trading System (Test Environment)
After=network.target

[Service]
Type=simple
User=trader-test
Group=trader-test
WorkingDirectory=/home/trader-test/lighter_quantification_v2
Environment=PATH=/home/trader-test/lighter_quantification_v2/venv/bin
ExecStart=/home/trader-test/lighter_quantification_v2/venv/bin/python main.py --config config_linux_testnet.yaml
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
    config = Config.from_file('config_linux_testnet.yaml')
    print('✅ 配置文件正确')
    print(f'交易市场: {len(config.trading.markets)}')
    print(f'启用策略: {sum(1 for s in config.trading.strategies.values() if s.get(\"enabled\", False))}')
except Exception as e:
    print(f'❌ 配置错误: {e}')
"

# 检查网络连接
ping -c 3 testnet.zklighter.elliot.ai

# 检查磁盘空间
df -h .
```

#### 6.2 测试连接
```bash
# 测试Lighter连接
python -c "
import asyncio
import sys
sys.path.append('.')
from quant_trading.utils.config import Config
import lighter

async def test_connection():
    config = Config.from_file('config_linux_testnet.yaml')
    configuration = lighter.Configuration()
    configuration.host = config.lighter_base_url
    api_client = lighter.ApiClient(configuration)
    
    try:
        # 测试API连接
        block_api = lighter.BlockApi(api_client)
        blocks = await block_api.blocks(limit=1)
        print('✅ Lighter连接成功')
        await api_client.close()
        return True
    except Exception as e:
        print(f'❌ 连接失败: {e}')
        await api_client.close()
        return False

asyncio.run(test_connection())
"
```

#### 6.3 启动Web系统
```bash
# 启动后端 (后台运行)
cd web_backend
nohup python main.py > ../logs/backend.log 2>&1 &
backend_pid=$!
echo $backend_pid > ../logs/backend.pid
cd ..

# 启动前端 (后台运行)
cd web_frontend
nohup npm start > ../logs/frontend.log 2>&1 &
frontend_pid=$!
echo $frontend_pid > ../logs/frontend.pid
cd ..

# 检查进程
ps aux | grep python
ps aux | grep node
```

#### 6.4 启动交易系统
```bash
# 方式1: 直接启动
python main.py --config config_linux_testnet.yaml

# 方式2: 后台运行
nohup python main.py --config config_linux_testnet.yaml > logs/trading.log 2>&1 &
trading_pid=$!
echo $trading_pid > logs/trading.pid

# 方式3: 使用系统服务
sudo systemctl start lighter-trading-test
sudo systemctl status lighter-trading-test
```

### 第七步：使用功能

#### 7.1 Web界面使用
1. 打开浏览器访问 `http://localhost:3000` 或 `http://your-server-ip:3000`
2. 登录系统 (默认用户名/密码：admin/admin)
3. 配置交易参数
4. 选择交易策略
5. 启动交易

#### 7.2 命令行使用
```bash
# 查看系统状态
python -c "
from quant_trading.utils.config import Config
config = Config.from_file('config_linux_testnet.yaml')
print('配置加载成功')
print(f'交易市场: {config.trading.markets}')
print(f'启用策略: {[name for name, strategy in config.trading.strategies.items() if strategy.get(\"enabled\", False)]}')
"

# 手动执行策略
python examples/simple_trading_bot.py

# 运行回测
python run_backtest.py --strategy momentum --start-date 2024-01-01 --end-date 2024-01-31 --config config_linux_testnet.yaml
```

#### 7.3 监控和维护
```bash
# 查看系统日志
tail -f logs/linux_testnet_trading.log

# 查看Web后端日志
tail -f logs/backend.log

# 查看Web前端日志
tail -f logs/frontend.log

# 查看系统状态
python monitor_mainnet.py  # 使用主网监控脚本
```

## 🔧 故障排除

### 常见问题

#### 1. 权限问题
```bash
# 检查文件权限
ls -la config_linux_testnet.yaml

# 修复权限
chmod 644 config_linux_testnet.yaml
chmod 755 logs
chmod 755 data
```

#### 2. 网络连接问题
```bash
# 测试网络连接
curl -I https://testnet.zklighter.elliot.ai

# 检查DNS解析
nslookup testnet.zklighter.elliot.ai

# 检查防火墙
sudo ufw status  # Ubuntu
sudo firewall-cmd --list-all  # CentOS
```

#### 3. 服务启动失败
```bash
# 查看服务状态
sudo systemctl status lighter-trading-test

# 查看详细日志
sudo journalctl -u lighter-trading-test -f

# 重启服务
sudo systemctl restart lighter-trading-test
```

#### 4. 依赖问题
```bash
# 重新安装依赖
pip install -r requirements.txt --force-reinstall

# 清理pip缓存
pip cache purge
```

#### 5. 端口冲突
```bash
# 检查端口占用
netstat -tlnp | grep :8000
netstat -tlnp | grep :3000

# 杀死占用进程
sudo kill -9 <PID>
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

## 🔒 安全注意事项

### 测试环境安全
1. **私钥安全**: 使用测试网私钥，不要使用主网私钥
2. **网络安全**: 配置防火墙，限制访问端口
3. **访问控制**: 限制SSH访问IP
4. **数据备份**: 定期备份配置文件

### 开发建议
1. 使用版本控制管理代码
2. 定期更新依赖包
3. 编写单元测试
4. 使用代码质量工具

## 📞 技术支持

### 文档资源
- [Windows测试环境部署指南](WINDOWS_TESTNET_DEPLOYMENT_GUIDE.md)
- [Linux主网环境部署指南](LINUX_MAINNET_DEPLOYMENT_GUIDE.md)
- [配置文件示例](config_windows_testnet.yaml)
- [启动脚本](start_linux_mainnet.sh)

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
