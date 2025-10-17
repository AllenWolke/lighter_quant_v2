# Lighter量化交易模块 - 部署手册

## 📋 目录

- [系统要求](#系统要求)
- [环境准备](#环境准备)
- [安装步骤](#安装步骤)
- [配置设置](#配置设置)
- [依赖管理](#依赖管理)
- [测试验证](#测试验证)
- [生产部署](#生产部署)
- [Docker部署](#docker部署)
- [常见问题](#常见问题)

---

## 系统要求

### 硬件要求

| 组件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| CPU | 2核 | 4核+ |
| 内存 | 4GB | 8GB+ |
| 硬盘 | 10GB可用空间 | 50GB+ SSD |
| 网络 | 稳定互联网连接 | 低延迟专线 |

### 软件要求

| 软件 | 版本要求 | 说明 |
|------|----------|------|
| 操作系统 | Windows 10+/Linux/macOS | 推荐Ubuntu 20.04+ |
| Python | 3.8+ | 推荐3.10或3.11 |
| pip | 最新版本 | Python包管理器 |
| Git | 2.0+ | 版本控制（可选） |

### 支持的操作系统

✅ **Windows**
- Windows 10 (64位)
- Windows 11
- Windows Server 2019+

✅ **Linux**
- Ubuntu 20.04+
- Debian 10+
- CentOS 8+
- RHEL 8+

✅ **macOS**
- macOS 10.15+
- macOS 11+

---

## 环境准备

### 1. 安装Python

#### Windows

```bash
# 下载Python安装包
# 访问 https://www.python.org/downloads/

# 或使用Chocolatey
choco install python --version=3.11

# 验证安装
python --version
pip --version
```

#### Linux (Ubuntu/Debian)

```bash
# 更新包列表
sudo apt update

# 安装Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# 设置默认版本
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# 验证安装
python3 --version
pip3 --version
```

#### macOS

```bash
# 使用Homebrew
brew install python@3.11

# 验证安装
python3 --version
pip3 --version
```

### 2. 创建虚拟环境

```bash
# 进入项目目录
cd /path/to/lighter_quantification_v2

# 创建虚拟环境
python -m venv env

# 激活虚拟环境
# Windows
env\Scripts\activate

# Linux/macOS
source env/bin/activate

# 验证虚拟环境
which python  # Linux/macOS
where python  # Windows
```

---

## 安装步骤

### 方法一：完整安装（推荐）

```bash
# 1. 克隆或下载项目
git clone <repository_url>
cd lighter_quantification_v2

# 2. 创建并激活虚拟环境
python -m venv env
source env/bin/activate  # Linux/macOS
# 或
env\Scripts\activate  # Windows

# 3. 升级pip
python -m pip install --upgrade pip

# 4. 安装所有依赖
pip install -r requirements.txt

# 5. 安装项目包
pip install -e .

# 6. 验证安装
python -c "import quant_trading; print(quant_trading.__version__)"
```

### 方法二：最小化安装

```bash
# 仅安装核心依赖
pip install -r requirements-minimal.txt

# 根据需要安装额外功能
pip install pandas numpy  # 数据分析
pip install matplotlib seaborn  # 可视化
pip install pytest  # 测试
```

### 方法三：开发安装

```bash
# 安装开发依赖
pip install -r requirements.txt
pip install -r test-requirements.txt

# 以开发模式安装
pip install -e ".[dev]"
```

---

## 配置设置

### 1. 复制配置模板

```bash
# 复制示例配置文件
cp config.yaml.example config.yaml
```

### 2. 编辑配置文件

```bash
# 使用文本编辑器打开
nano config.yaml
# 或
vim config.yaml
# 或
code config.yaml  # VS Code
```

### 3. 配置Lighter连接

编辑`config.yaml`中的Lighter配置：

```yaml
lighter:
  # 测试网配置
  base_url: "https://testnet.zklighter.elliot.ai"
  api_key_private_key: "YOUR_PRIVATE_KEY_HERE"  # 替换为您的私钥
  account_index: 0
  api_key_index: 0
  chain_id: 302
```

⚠️ **安全提示**:
- 不要将包含真实私钥的配置文件提交到代码仓库
- 使用环境变量存储敏感信息（可选）

### 4. 环境变量配置（可选）

```bash
# Linux/macOS
export LIGHTER_PRIVATE_KEY="your_private_key_here"
export LIGHTER_BASE_URL="https://testnet.zklighter.elliot.ai"

# Windows PowerShell
$env:LIGHTER_PRIVATE_KEY="your_private_key_here"
$env:LIGHTER_BASE_URL="https://testnet.zklighter.elliot.ai"

# Windows CMD
set LIGHTER_PRIVATE_KEY=your_private_key_here
set LIGHTER_BASE_URL=https://testnet.zklighter.elliot.ai
```

### 5. 创建日志目录

```bash
# 创建日志目录
mkdir -p logs

# 设置权限（Linux/macOS）
chmod 755 logs
```

---

## 依赖管理

### 核心依赖

```txt
lighter-v2-python>=1.0.0   # Lighter交易所SDK
pyyaml>=6.0                # YAML配置文件支持
aiohttp>=3.8.0             # 异步HTTP客户端
websockets>=10.0           # WebSocket支持
numpy>=1.20.0              # 数值计算
pandas>=1.3.0              # 数据分析
```

### 可选依赖

```txt
# 数据可视化
matplotlib>=3.5.0
seaborn>=0.12.0
plotly>=5.0.0

# 通知功能
aiosmtplib>=2.0.0          # 异步邮件发送

# 测试工具
pytest>=7.0.0
pytest-asyncio>=0.18.0
pytest-cov>=3.0.0

# 开发工具
black>=22.0.0              # 代码格式化
flake8>=4.0.0              # 代码检查
mypy>=0.950                # 类型检查
```

### 检查依赖

```bash
# 使用内置检查脚本
python check_dependencies.py

# 手动检查
pip list | grep lighter
pip list | grep pyyaml
pip list | grep aiohttp
```

### 更新依赖

```bash
# 更新所有依赖到最新版本
pip install --upgrade -r requirements.txt

# 更新特定包
pip install --upgrade lighter-v2-python

# 查看过时的包
pip list --outdated
```

---

## 测试验证

### 1. 配置验证

```bash
# 检查配置文件格式
python check_config.py

# 输出示例：
# ✅ 配置文件格式正确
# ✅ Lighter配置有效
# ✅ 风险参数在合理范围内
```

### 2. 连接测试

```bash
# 测试Lighter连接
python check_lighter_connection.sh
# 或
python -c "from lighter import SignerClient; print('Connection OK')"
```

### 3. 策略测试

```bash
# 运行示例策略（不实际交易）
python examples/simple_trading_bot.py --dry-run

# 运行回测
python backtest.py --strategy mean_reversion --days 7
```

### 4. 单元测试

```bash
# 运行所有测试
pytest test/

# 运行特定测试
pytest test/test_strategies.py

# 运行测试并生成覆盖率报告
pytest --cov=quant_trading --cov-report=html test/
```

### 5. 集成测试

```bash
# 测试交易引擎启动
python -c "
from quant_trading import TradingEngine, Config
config = Config.from_file('config.yaml')
engine = TradingEngine(config)
print('Engine initialized successfully')
"
```

---

## 生产部署

### Linux服务器部署

#### 1. 创建专用用户

```bash
# 创建系统用户
sudo useradd -r -s /bin/bash -d /opt/quant_trading quant_trader

# 创建工作目录
sudo mkdir -p /opt/quant_trading
sudo chown quant_trader:quant_trader /opt/quant_trading
```

#### 2. 部署应用

```bash
# 切换到应用用户
sudo su - quant_trader

# 克隆或复制项目
cd /opt/quant_trading
git clone <repository_url> .

# 创建虚拟环境
python3 -m venv env
source env/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# 配置应用
cp config.yaml.example config.yaml
nano config.yaml  # 编辑配置

# 创建必要目录
mkdir -p logs data
```

#### 3. 配置系统服务

创建systemd服务文件 `/etc/systemd/system/quant-trading.service`:

```ini
[Unit]
Description=Lighter Quantitative Trading System
After=network.target

[Service]
Type=simple
User=quant_trader
Group=quant_trader
WorkingDirectory=/opt/quant_trading
Environment="PATH=/opt/quant_trading/env/bin"
ExecStart=/opt/quant_trading/env/bin/python start_trading.py
Restart=on-failure
RestartSec=10
StandardOutput=append:/opt/quant_trading/logs/service.log
StandardError=append:/opt/quant_trading/logs/service_error.log

[Install]
WantedBy=multi-user.target
```

#### 4. 启动服务

```bash
# 重载systemd配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start quant-trading

# 设置开机自启
sudo systemctl enable quant-trading

# 检查状态
sudo systemctl status quant-trading

# 查看日志
sudo journalctl -u quant-trading -f
```

### Windows服务部署

#### 使用NSSM (Non-Sucking Service Manager)

```powershell
# 1. 下载NSSM
# 访问 https://nssm.cc/download

# 2. 安装服务
nssm install QuantTrading "C:\Path\To\env\Scripts\python.exe" "C:\Path\To\start_trading.py"

# 3. 配置服务
nssm set QuantTrading AppDirectory "C:\Path\To\lighter_quantification_v2"
nssm set QuantTrading DisplayName "Lighter Quantitative Trading"
nssm set QuantTrading Description "Automated trading system for Lighter exchange"
nssm set QuantTrading Start SERVICE_AUTO_START

# 4. 启动服务
nssm start QuantTrading

# 5. 查看状态
nssm status QuantTrading
```

---

## Docker部署

### 1. 创建Dockerfile

在项目根目录创建`Dockerfile`:

```dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 安装项目
RUN pip install -e .

# 创建日志目录
RUN mkdir -p logs

# 暴露端口（如果需要）
# EXPOSE 8000

# 启动命令
CMD ["python", "start_trading.py"]
```

### 2. 创建docker-compose.yml

```yaml
version: '3.8'

services:
  quant-trading:
    build: .
    container_name: lighter-quant-trading
    restart: unless-stopped
    volumes:
      - ./config.yaml:/app/config.yaml:ro
      - ./logs:/app/logs
      - ./data:/app/data
    environment:
      - TZ=Asia/Shanghai
      - PYTHONUNBUFFERED=1
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 3. 构建和运行

```bash
# 构建镜像
docker-compose build

# 启动容器
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止容器
docker-compose down

# 重启容器
docker-compose restart
```

### 4. Docker管理命令

```bash
# 查看容器状态
docker-compose ps

# 进入容器
docker-compose exec quant-trading bash

# 查看实时日志
docker-compose logs -f --tail 100

# 更新并重启
docker-compose pull
docker-compose up -d

# 清理
docker-compose down -v
```

---

## 常见问题

### 1. Python版本不兼容

**问题**: `SyntaxError: invalid syntax` 或类型提示错误

**解决**:
```bash
# 检查Python版本
python --version

# 如果版本低于3.8，升级Python
# Ubuntu
sudo apt install python3.11 -y

# Windows: 重新下载安装最新版本
```

### 2. 依赖安装失败

**问题**: `ERROR: Could not build wheels for xxx`

**解决**:
```bash
# 安装编译工具
# Ubuntu/Debian
sudo apt install build-essential python3-dev -y

# CentOS/RHEL
sudo yum groupinstall "Development Tools" -y
sudo yum install python3-devel -y

# macOS
xcode-select --install

# Windows: 安装Visual Studio Build Tools
```

### 3. Lighter连接失败

**问题**: `Connection refused` 或 `Timeout`

**解决**:
```bash
# 1. 检查网络连接
ping testnet.zklighter.elliot.ai

# 2. 检查防火墙设置
# Linux
sudo ufw status
sudo ufw allow out 443/tcp

# 3. 验证私钥格式
# 确保是64位十六进制，无0x前缀
```

### 4. 权限问题

**问题**: `Permission denied` 写入日志或配置

**解决**:
```bash
# Linux/macOS
chmod 755 logs/
chmod 644 config.yaml

# Windows: 右键 -> 属性 -> 安全 -> 编辑权限
```

### 5. 模块导入错误

**问题**: `ModuleNotFoundError: No module named 'quant_trading'`

**解决**:
```bash
# 确保已安装项目包
pip install -e .

# 或添加项目路径到PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/lighter_quantification_v2"
```

### 6. 内存不足

**问题**: 系统运行缓慢或崩溃

**解决**:
```bash
# 增加系统swap（Linux）
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 或优化配置，减少并发策略数
```

### 7. 时区问题

**问题**: 时间戳不正确

**解决**:
```bash
# Linux
sudo timedatectl set-timezone Asia/Shanghai

# Docker
# 在docker-compose.yml中设置
environment:
  - TZ=Asia/Shanghai
```

---

## 部署检查清单

部署完成后，请确认以下项目：

- [ ] Python版本 >= 3.8
- [ ] 虚拟环境已创建并激活
- [ ] 所有依赖已正确安装
- [ ] 配置文件已正确设置
- [ ] Lighter私钥已配置（测试网或主网）
- [ ] 日志目录已创建且可写
- [ ] 网络连接正常，可访问Lighter API
- [ ] 配置验证通过 (`python check_config.py`)
- [ ] 连接测试通过
- [ ] 回测测试成功
- [ ] 系统服务已配置（生产环境）
- [ ] 监控和日志轮转已设置
- [ ] 备份策略已制定

---

## 监控和维护

### 日志轮转

```bash
# Linux: 配置logrotate
sudo nano /etc/logrotate.d/quant-trading
```

```conf
/opt/quant_trading/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 quant_trader quant_trader
}
```

### 性能监控

```bash
# 监控CPU和内存使用
top -p $(pgrep -f start_trading.py)

# 或使用htop
htop -p $(pgrep -f start_trading.py)

# 监控网络连接
netstat -an | grep ESTABLISHED | grep python
```

### 自动备份

```bash
# 创建备份脚本
nano /opt/quant_trading/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/backup/quant_trading"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/config_$DATE.tar.gz config.yaml
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz logs/

# 保留最近7天的备份
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

```bash
# 设置定时任务
crontab -e
# 添加: 每天凌晨2点备份
0 2 * * * /opt/quant_trading/backup.sh
```

---

## 升级和回滚

### 升级系统

```bash
# 1. 备份当前配置
cp config.yaml config.yaml.backup

# 2. 停止服务
sudo systemctl stop quant-trading

# 3. 拉取最新代码
git pull origin main

# 4. 更新依赖
source env/bin/activate
pip install --upgrade -r requirements.txt

# 5. 运行迁移脚本（如有）
python migrate.py

# 6. 启动服务
sudo systemctl start quant-trading

# 7. 验证
sudo systemctl status quant-trading
```

### 回滚

```bash
# 1. 停止服务
sudo systemctl stop quant-trading

# 2. 回滚到上一个版本
git checkout <previous_commit>

# 3. 恢复配置
cp config.yaml.backup config.yaml

# 4. 重新安装依赖
pip install -r requirements.txt

# 5. 启动服务
sudo systemctl start quant-trading
```

---

## 相关文档

- [参数配置手册](PARAMETER_CONFIG_MANUAL.md)
- [执行手册](EXECUTION_MANUAL.md)
- [故障排除指南](../docs/troubleshooting.md)

---

**文档版本**: v1.0.0  
**最后更新**: 2024年  
**维护者**: Quant Trading Team

