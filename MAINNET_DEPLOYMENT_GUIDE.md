# Lighter量化交易程序主网部署指南

## ⚠️ 重要警告

**主网部署涉及真实资金，请务必谨慎操作！**

- 确保您完全理解量化交易的风险
- 建议先在测试网充分测试
- 从小资金开始，逐步增加
- 设置严格的风险控制参数
- 定期监控程序运行状态

## 📋 主网部署前准备

### 1. 系统要求
- Python 3.8+
- 稳定的网络连接（推荐VPS）
- 至少4GB可用内存
- 24/7运行环境（推荐云服务器）

### 2. 主网账户准备
- 访问 [Lighter主网](https://app.lighter.xyz/)
- 完成KYC认证
- 充值真实资金到账户
- 创建API密钥（建议创建专用API密钥）

### 3. 资金准备
- 建议初始资金：$1000-$10000
- 确保有足够的资金承受最大回撤
- 预留应急资金

## 🚀 主网部署步骤

### 步骤1: 环境准备

```bash
# 1. 创建生产环境目录
mkdir lighter_quant_mainnet
cd lighter_quant_mainnet

# 2. 复制项目文件
cp -r /path/to/lighter_quantification_v2/* .

# 3. 创建虚拟环境
python -m venv venv

# 4. 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 5. 安装依赖
pip install -r requirements.txt
```

### 步骤2: 主网配置

#### 2.1 创建主网配置文件
```bash
# 复制配置模板
cp config.yaml.example config_mainnet.yaml
```

#### 2.2 编辑主网配置
```yaml
# Lighter主网配置
lighter:
  base_url: "https://mainnet.zklighter.elliot.ai"  # 主网地址
  api_key_private_key: "your_mainnet_api_key_here"  # 主网API密钥
  account_index: 0  # 主网账户索引
  api_key_index: 0  # 主网API密钥索引

# 交易配置（主网优化）
trading:
  tick_interval: 2.0  # 增加间隔，减少API调用
  max_concurrent_strategies: 3  # 减少并发策略数

# 风险管理配置（主网严格设置）
risk:
  max_position_size: 0.02  # 最大仓位2%（主网保守设置）
  max_daily_loss: 0.01     # 最大日亏损1%
  max_drawdown: 0.05       # 最大回撤5%
  max_leverage: 5.0        # 最大杠杆5倍
  max_orders_per_minute: 3 # 每分钟最大订单数
  max_open_orders: 5       # 最大开仓订单数

# 日志配置（主网详细日志）
log:
  level: "INFO"
  file: "logs/mainnet_trading.log"

# 数据源配置
data_sources:
  primary: "lighter"
  tradingview:
    enabled: true
    session_id: "qs_1"
    user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    symbol_mapping:
      "BTC_USDT": "BTCUSDT"
      "ETH_USDT": "ETHUSDT"

# 策略配置（主网保守设置）
strategies:
  ut_bot:
    enabled: true
    market_id: 0
    key_value: 0.8      # 降低敏感度
    atr_period: 14      # 增加ATR周期
    use_heikin_ashi: false
    position_size: 0.01  # 减小仓位
    stop_loss: 0.015    # 严格止损
    take_profit: 0.008  # 保守止盈
    
  mean_reversion:
    enabled: false      # 主网暂时禁用
    market_id: 0
    lookback_period: 30
    threshold: 2.5
    position_size: 0.01
    stop_loss: 0.015
    take_profit: 0.008
```

### 步骤3: 安全配置

#### 3.1 创建安全脚本
```bash
# 创建安全启动脚本
cat > start_mainnet.py << 'EOF'
#!/usr/bin/env python3
"""
主网安全启动脚本
包含多重安全检查
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from quant_trading import TradingEngine, Config

def safety_checks():
    """安全检查"""
    print("🔒 执行安全检查...")
    
    # 检查配置文件
    if not os.path.exists("config_mainnet.yaml"):
        print("❌ 主网配置文件不存在")
        return False
    
    # 检查API密钥
    config = Config.from_file("config_mainnet.yaml")
    if not config.lighter_config.get("api_key_private_key"):
        print("❌ API密钥未配置")
        return False
    
    # 检查是否为测试网
    if "testnet" in config.lighter_config.get("base_url", ""):
        print("❌ 检测到测试网配置，主网部署被阻止")
        return False
    
    # 检查风险参数
    risk_config = config.risk_config
    if risk_config.get("max_position_size", 0) > 0.05:
        print("⚠️  警告：仓位大小过大，建议小于5%")
        confirm = input("是否继续? (y/N): ").strip().lower()
        if confirm != 'y':
            return False
    
    print("✅ 安全检查通过")
    return True

async def main():
    """主函数"""
    print("🚀 Lighter量化交易程序 - 主网版本")
    print("=" * 60)
    print("⚠️  警告：这是主网环境，涉及真实资金！")
    print("=" * 60)
    
    # 执行安全检查
    if not safety_checks():
        print("❌ 安全检查失败，程序退出")
        return 1
    
    # 最终确认
    print("\n⚠️  最终确认：")
    print("   - 这是主网环境")
    print("   - 将使用真实资金进行交易")
    print("   - 请确保已充分测试")
    print("   - 请确保已设置风险控制")
    
    confirm = input("\n确认继续? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("已取消启动")
        return 0
    
    try:
        # 加载配置
        config = Config.from_file("config_mainnet.yaml")
        
        # 创建交易引擎
        engine = TradingEngine(config)
        
        # 添加策略（只添加UT Bot策略）
        from quant_trading.strategies import UTBotStrategy
        
        ut_bot = UTBotStrategy(
            config=config,
            market_id=0,
            key_value=0.8,
            atr_period=14,
            use_heikin_ashi=False
        )
        engine.add_strategy(ut_bot)
        
        print("🚀 启动主网交易引擎...")
        print("按 Ctrl+C 安全停止")
        print("-" * 60)
        
        # 启动交易引擎
        await engine.start()
        
    except KeyboardInterrupt:
        print("\n⏹️  收到停止信号，正在安全关闭...")
    except Exception as e:
        print(f"\n❌ 运行错误: {e}")
        return 1
    finally:
        if 'engine' in locals():
            await engine.stop()
        print("✅ 程序已安全停止")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 再见!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 程序错误: {e}")
        sys.exit(1)
EOF

chmod +x start_mainnet.py
```

#### 3.2 创建监控脚本
```bash
# 创建监控脚本
cat > monitor_mainnet.py << 'EOF'
#!/usr/bin/env python3
"""
主网监控脚本
监控交易程序运行状态
"""

import time
import os
import subprocess
from datetime import datetime

def check_process():
    """检查进程状态"""
    try:
        result = subprocess.run(['pgrep', '-f', 'start_mainnet.py'], 
                              capture_output=True, text=True)
        return len(result.stdout.strip()) > 0
    except:
        return False

def check_logs():
    """检查日志文件"""
    log_file = "logs/mainnet_trading.log"
    if not os.path.exists(log_file):
        return False
    
    # 检查最近5分钟是否有日志
    stat = os.stat(log_file)
    return (time.time() - stat.st_mtime) < 300

def main():
    """主函数"""
    print("📊 主网交易程序监控")
    print("=" * 40)
    
    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        process_running = check_process()
        logs_updated = check_logs()
        
        status = "✅ 正常" if (process_running and logs_updated) else "❌ 异常"
        
        print(f"[{timestamp}] 状态: {status}")
        print(f"  进程运行: {'是' if process_running else '否'}")
        print(f"  日志更新: {'是' if logs_updated else '否'}")
        
        if not process_running:
            print("⚠️  进程未运行，请检查程序状态")
        
        if not logs_updated:
            print("⚠️  日志未更新，程序可能卡住")
        
        print("-" * 40)
        time.sleep(60)  # 每分钟检查一次

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n监控已停止")
EOF

chmod +x monitor_mainnet.py
```

### 步骤4: 系统测试

#### 4.1 创建主网测试脚本
```bash
# 创建主网测试脚本
cat > test_mainnet.py << 'EOF'
#!/usr/bin/env python3
"""
主网系统测试
验证主网配置和连接
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from quant_trading import Config
import lighter

async def test_mainnet_connection():
    """测试主网连接"""
    print("🔍 测试主网连接...")
    
    try:
        # 加载配置
        config = Config.from_file("config_mainnet.yaml")
        
        # 创建API客户端
        api_client = lighter.ApiClient(
            configuration=lighter.Configuration(host=config.lighter_config["base_url"])
        )
        
        # 测试账户API
        account_api = lighter.AccountApi(api_client)
        account = await account_api.account(
            by="index", 
            value=str(config.lighter_config["account_index"])
        )
        
        if account:
            print(f"✅ 主网连接成功")
            print(f"   账户索引: {account.account_index}")
            print(f"   地址: {account.l1_address}")
            return True
        else:
            print("❌ 主网连接失败")
            return False
            
    except Exception as e:
        print(f"❌ 主网连接测试失败: {e}")
        return False
    finally:
        if 'api_client' in locals():
            await api_client.close()

async def test_risk_parameters():
    """测试风险参数"""
    print("🔍 测试风险参数...")
    
    try:
        config = Config.from_file("config_mainnet.yaml")
        risk_config = config.risk_config
        
        # 检查风险参数
        if risk_config.get("max_position_size", 0) > 0.05:
            print("⚠️  警告：最大仓位超过5%")
            return False
        
        if risk_config.get("max_daily_loss", 0) > 0.02:
            print("⚠️  警告：最大日亏损超过2%")
            return False
        
        if risk_config.get("max_drawdown", 0) > 0.1:
            print("⚠️  警告：最大回撤超过10%")
            return False
        
        print("✅ 风险参数检查通过")
        return True
        
    except Exception as e:
        print(f"❌ 风险参数测试失败: {e}")
        return False

async def main():
    """主函数"""
    print("🧪 主网系统测试")
    print("=" * 40)
    
    # 测试连接
    connection_ok = await test_mainnet_connection()
    
    # 测试风险参数
    risk_ok = await test_risk_parameters()
    
    print("\n" + "=" * 40)
    if connection_ok and risk_ok:
        print("🎉 主网测试通过，可以开始交易！")
        return 0
    else:
        print("❌ 主网测试失败，请检查配置")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except Exception as e:
        print(f"❌ 测试错误: {e}")
        sys.exit(1)
EOF

chmod +x test_mainnet.py
```

### 步骤5: 部署和启动

#### 5.1 运行主网测试
```bash
# 运行主网测试
python test_mainnet.py
```

#### 5.2 启动主网交易
```bash
# 启动主网交易程序
python start_mainnet.py
```

#### 5.3 启动监控
```bash
# 在另一个终端启动监控
python monitor_mainnet.py
```

## 📊 主网监控和管理

### 实时监控

#### 1. 日志监控
```bash
# 查看实时日志
tail -f logs/mainnet_trading.log

# 查看错误日志
grep "ERROR" logs/mainnet_trading.log

# 查看交易日志
grep "交易信号" logs/mainnet_trading.log
```

#### 2. 系统监控
```bash
# 检查进程状态
ps aux | grep start_mainnet.py

# 检查内存使用
top -p $(pgrep -f start_mainnet.py)

# 检查网络连接
netstat -an | grep 443
```

#### 3. 交易监控
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
    print(f'账户余额: {account.balance}')
    await api_client.close()

asyncio.run(check_balance())
"
```

### 风险管理

#### 1. 每日检查清单
- [ ] 程序正常运行
- [ ] 日志无错误
- [ ] 账户余额正常
- [ ] 风险指标在范围内
- [ ] 网络连接稳定

#### 2. 紧急停止
```bash
# 紧急停止程序
pkill -f start_mainnet.py

# 或者发送SIGINT信号
kill -INT $(pgrep -f start_mainnet.py)
```

#### 3. 数据备份
```bash
# 备份配置文件
cp config_mainnet.yaml config_mainnet_backup_$(date +%Y%m%d).yaml

# 备份日志文件
tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/

# 备份交易数据
cp -r data/ data_backup_$(date +%Y%m%d)/
```

## 🔧 主网优化建议

### 1. 性能优化

#### 服务器配置
- 推荐使用云服务器（AWS、阿里云等）
- 至少2核4GB内存
- SSD硬盘
- 稳定的网络连接

#### 程序优化
```yaml
# 优化配置
trading:
  tick_interval: 3.0  # 增加更新间隔
  max_concurrent_strategies: 2  # 减少并发策略

# 禁用不需要的功能
data_sources:
  tradingview:
    enabled: false  # 如果不需要TradingView数据
```

### 2. 安全优化

#### 网络安全
- 使用VPN或专用网络
- 设置防火墙规则
- 定期更新系统

#### 程序安全
- 定期备份配置和日志
- 监控异常活动
- 设置多重验证

### 3. 风险控制

#### 资金管理
- 不要投入超过承受能力的资金
- 设置严格的止损和止盈
- 定期提取利润

#### 策略管理
- 只运行经过充分测试的策略
- 定期评估策略表现
- 及时调整参数

## 📈 主网运行检查清单

### 部署前检查
- [ ] 测试网充分测试
- [ ] 主网配置正确
- [ ] 风险参数合理
- [ ] 资金准备充足
- [ ] 监控系统就绪

### 启动前检查
- [ ] 主网连接测试通过
- [ ] 风险参数检查通过
- [ ] 策略参数合理
- [ ] 监控脚本运行
- [ ] 备份系统就绪

### 运行中检查
- [ ] 程序正常运行
- [ ] 日志记录正常
- [ ] 交易执行正常
- [ ] 风险控制有效
- [ ] 监控报警正常

## ⚠️ 主网注意事项

### 1. 资金安全
- 定期检查账户余额
- 设置资金使用限制
- 保留应急资金

### 2. 风险控制
- 严格执行止损
- 监控最大回撤
- 控制仓位大小

### 3. 系统维护
- 定期更新程序
- 监控系统性能
- 备份重要数据

### 4. 合规要求
- 遵守当地法规
- 记录交易活动
- 按时报税

## 🆘 应急处理

### 1. 程序崩溃
```bash
# 检查错误日志
tail -n 100 logs/mainnet_trading.log

# 重启程序
python start_mainnet.py
```

### 2. 网络中断
```bash
# 检查网络连接
ping mainnet.zklighter.elliot.ai

# 等待网络恢复后重启
```

### 3. 异常交易
```bash
# 立即停止程序
pkill -f start_mainnet.py

# 检查交易记录
grep "交易" logs/mainnet_trading.log
```

## 📞 技术支持

### 1. 日志分析
- 查看错误日志
- 分析交易记录
- 检查系统状态

### 2. 问题排查
- 网络连接问题
- API调用问题
- 策略执行问题

### 3. 性能优化
- 系统性能调优
- 策略参数优化
- 风险控制优化

记住：主网部署涉及真实资金，请务必谨慎操作，充分测试，严格风控！
