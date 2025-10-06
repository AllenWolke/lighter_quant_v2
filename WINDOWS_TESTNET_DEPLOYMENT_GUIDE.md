# Windows测试环境部署指南

## 📋 系统要求

### 硬件要求
- **CPU**: Intel i5 或 AMD Ryzen 5 以上
- **内存**: 8GB RAM 以上
- **存储**: 20GB 可用空间
- **网络**: 稳定的互联网连接

### 软件要求
- **操作系统**: Windows 10/11 (64位)
- **Python**: 3.9+ (推荐 3.11)
- **Git**: 用于代码版本控制
- **浏览器**: Chrome/Firefox/Edge (用于Web界面)

## 🚀 部署步骤

### 第一步：环境准备

#### 1.1 安装Python
```bash
# 下载并安装Python 3.11
# 访问 https://www.python.org/downloads/
# 勾选 "Add Python to PATH"

# 验证安装
python --version
pip --version
```

#### 1.2 安装Git
```bash
# 下载并安装Git for Windows
# 访问 https://git-scm.com/download/win

# 验证安装
git --version
```

#### 1.3 克隆项目
```bash
# 克隆项目到本地
git clone <项目仓库地址>
cd lighter_quantification_v2
```

### 第二步：依赖安装

#### 2.1 创建虚拟环境
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows CMD
venv\Scripts\activate.bat

# Windows PowerShell
venv\Scripts\Activate.ps1
```

#### 2.2 安装依赖
```bash
# 升级pip
python -m pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt

# 验证关键依赖
python -c "import lighter; import eth_account; import pydantic; print('核心依赖安装成功')"
```

### 第三步：配置参数

#### 3.1 复制配置文件
```bash
# 复制测试网配置模板
copy config.yaml.example config.yaml
```

#### 3.2 编辑配置文件
编辑 `config.yaml` 文件：

```yaml
# 测试网配置
lighter:
  base_url: "https://testnet.zklighter.elliot.ai"
  api_key_private_key: "你的测试网私钥"
  api_key_index: 3
  account_index: 0

# 交易参数
trading:
  markets:
    - symbol: "ETH"
      market_id: 0
      base_asset: "ETH"
      quote_asset: "USDC"
  
  strategies:
    momentum:
      enabled: true
      long_period: 20
      short_period: 5
      threshold: 0.02
      leverage: 5.0
      position_size: 0.1

# 风险管理
risk_management:
  max_position_size: 0.2
  max_daily_loss: 0.05
  max_drawdown: 0.15
  stop_loss: 0.03

# 通知配置
notifications:
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    username: "你的邮箱@gmail.com"
    password: "你的应用密码"
    to_email: "接收邮箱@gmail.com"

# 日志配置
logging:
  level: "INFO"
  file: "logs/trading.log"
  max_size: "10MB"
  backup_count: 5
```

#### 3.3 获取测试网私钥
```bash
# 运行系统设置脚本获取测试私钥
python examples/system_setup.py
```

### 第四步：启动系统

#### 4.1 测试连接
```bash
# 测试Lighter连接
python -c "
import asyncio
import sys
sys.path.append('.')
from quant_trading.utils.config import Config
import lighter

async def test_connection():
    config = Config.from_file('config.yaml')
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

#### 4.2 启动Web系统
```bash
# 启动Web后端
cd web_backend
python main.py

# 新开终端窗口，启动Web前端
cd web_frontend
npm install
npm start
```

#### 4.3 启动量化交易系统
```bash
# 启动主交易程序
python main.py

# 或者启动测试网专用脚本
python run_testnet.py
```

### 第五步：使用功能

#### 5.1 Web界面使用
1. 打开浏览器访问 `http://localhost:3000`
2. 登录系统（默认用户名/密码：admin/admin）
3. 配置交易参数
4. 选择交易策略
5. 启动交易

#### 5.2 命令行使用
```bash
# 查看系统状态
python -c "
from quant_trading.utils.config import Config
config = Config.from_file('config.yaml')
print('配置加载成功')
print(f'交易市场: {config.trading.markets}')
print(f'启用策略: {[name for name, strategy in config.trading.strategies.items() if strategy.get(\"enabled\", False)]}')
"

# 手动执行策略
python examples/simple_trading_bot.py

# 运行回测
python run_backtest.py --strategy momentum --start-date 2024-01-01 --end-date 2024-01-31
```

## 🔧 故障排除

### 常见问题

#### 1. Python版本问题
```bash
# 检查Python版本
python --version

# 如果不是3.9+，请重新安装Python
```

#### 2. 依赖安装失败
```bash
# 清理pip缓存
pip cache purge

# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

#### 3. 网络连接问题
```bash
# 测试网络连接
ping testnet.zklighter.elliot.ai

# 检查防火墙设置
# 确保允许Python程序访问网络
```

#### 4. 配置文件错误
```bash
# 验证配置文件格式
python -c "
import yaml
try:
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    print('✅ 配置文件格式正确')
except Exception as e:
    print(f'❌ 配置文件错误: {e}')
"
```

## 📊 监控和维护

### 日志监控
```bash
# 查看实时日志
tail -f logs/trading.log

# 查看错误日志
grep "ERROR" logs/trading.log
```

### 性能监控
```bash
# 查看系统资源使用
# Windows任务管理器或使用PowerShell
Get-Process python | Select-Object ProcessName,CPU,WorkingSet
```

### 定期维护
- 每日检查日志文件
- 每周备份配置文件
- 每月更新依赖包
- 定期检查磁盘空间

## ⚠️ 注意事项

### Windows平台限制
1. **交易功能限制**: Windows平台不支持实际交易，只能进行数据获取和策略测试
2. **签名器限制**: Lighter签名器只支持Linux/macOS，Windows下无法执行实际交易
3. **建议用途**: 主要用于策略开发、回测和Web界面测试

### 安全建议
1. 使用测试网私钥，不要使用主网私钥
2. 定期更换API密钥
3. 不要在公共网络环境下运行
4. 定期备份重要数据

### 性能优化
1. 关闭不必要的后台程序
2. 使用SSD硬盘提升性能
3. 确保充足的内存空间
4. 定期清理日志文件

## 📞 技术支持

如遇到问题，请检查：
1. 系统要求是否满足
2. 配置文件是否正确
3. 网络连接是否正常
4. 依赖是否完整安装

更多详细信息请参考项目文档或联系技术支持。
