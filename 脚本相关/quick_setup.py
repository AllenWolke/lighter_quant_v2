#!/usr/bin/env python3
"""
快速部署脚本
自动化测试网部署流程
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

def print_step(step, description):
    """打印步骤信息"""
    print(f"\n{'='*60}")
    print(f"步骤 {step}: {description}")
    print('='*60)

def run_command(command, description=""):
    """运行命令"""
    print(f"执行: {command}")
    if description:
        print(f"说明: {description}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令执行失败: {e}")
        if e.stderr:
            print(f"错误信息: {e.stderr}")
        return False

def check_python_version():
    """检查Python版本"""
    print_step(1, "检查Python环境")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python版本过低，需要Python 3.8+")
        print(f"当前版本: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python版本检查通过: {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """安装依赖"""
    print_step(2, "安装项目依赖")
    
    if not run_command("pip install -r requirements.txt", "安装Python依赖包"):
        return False
    
    print("✅ 依赖安装完成")
    return True

def create_directories():
    """创建必要目录"""
    print_step(3, "创建必要目录")
    
    directories = ["logs", "data", "backtest_results"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ 创建目录: {directory}")
    
    return True

def setup_config():
    """设置配置文件"""
    print_step(4, "配置系统参数")
    
    print("请配置以下参数：")
    print()
    
    # 获取用户输入
    base_url = input("Lighter API地址 (默认: https://testnet.zklighter.elliot.ai): ").strip()
    if not base_url:
        base_url = "https://testnet.zklighter.elliot.ai"
    
    print("\n请运行以下命令获取API密钥：")
    print("python examples/system_setup.py")
    print()
    
    api_key = input("API密钥私钥: ").strip()
    if not api_key:
        print("❌ API密钥不能为空")
        return False
    
    account_index = input("账户索引: ").strip()
    if not account_index:
        print("❌ 账户索引不能为空")
        return False
    
    api_key_index = input("API密钥索引: ").strip()
    if not api_key_index:
        print("❌ API密钥索引不能为空")
        return False
    
    # 创建配置文件
    config_content = f"""# Lighter量化交易程序配置文件

# Lighter交易所配置
lighter:
  base_url: "{base_url}"
  api_key_private_key: "{api_key}"
  account_index: {account_index}
  api_key_index: {api_key_index}

# 交易配置
trading:
  tick_interval: 1.0
  max_concurrent_strategies: 5

# 风险管理配置
risk:
  max_position_size: 0.05
  max_daily_loss: 0.02
  max_drawdown: 0.10
  max_leverage: 10.0
  max_orders_per_minute: 5
  max_open_orders: 10

# 日志配置
log:
  level: "INFO"
  file: "logs/quant_trading.log"

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

# 策略配置
strategies:
  mean_reversion:
    enabled: true
    market_id: 0
    lookback_period: 20
    threshold: 2.0
    position_size: 0.05
    stop_loss: 0.02
    take_profit: 0.01
    
  momentum:
    enabled: true
    market_id: 0
    short_period: 5
    long_period: 20
    momentum_threshold: 0.02
    position_size: 0.05
    stop_loss: 0.03
    take_profit: 0.05
    
  arbitrage:
    enabled: true
    market_id_1: 0
    market_id_2: 1
    price_threshold: 0.01
    position_size: 0.02
    stop_loss: 0.005
    take_profit: 0.01
    
  ut_bot:
    enabled: true
    market_id: 0
    key_value: 1.0
    atr_period: 10
    use_heikin_ashi: false
    position_size: 0.05
    stop_loss: 0.02
    take_profit: 0.01
"""
    
    with open("config.yaml", "w", encoding="utf-8") as f:
        f.write(config_content)
    
    print("✅ 配置文件创建完成")
    return True

def test_connection():
    """测试连接"""
    print_step(5, "测试系统连接")
    
    print("测试Lighter API连接...")
    if not run_command("python examples/get_info.py", "测试API连接"):
        print("❌ API连接测试失败")
        return False
    
    print("✅ API连接测试通过")
    return True

def run_backtest():
    """运行回测测试"""
    print_step(6, "运行回测测试")
    
    print("运行UT Bot策略回测...")
    if not run_command("python backtest.py --strategy ut_bot --days 3", "回测测试"):
        print("❌ 回测测试失败")
        return False
    
    print("✅ 回测测试通过")
    return True

def show_usage():
    """显示使用说明"""
    print_step(7, "部署完成")
    
    print("🎉 部署成功！")
    print()
    print("使用方法：")
    print("1. 运行单个策略:")
    print("   python main.py --strategy ut_bot --market 0")
    print()
    print("2. 运行所有策略:")
    print("   python main.py --strategy all --market 0")
    print()
    print("3. 交互式启动:")
    print("   python start_trading.py")
    print()
    print("4. 运行回测:")
    print("   python backtest.py --strategy ut_bot --days 7")
    print()
    print("5. 查看日志:")
    print("   tail -f logs/quant_trading.log")
    print()
    print("⚠️  重要提醒:")
    print("- 这是测试网环境，请使用测试代币")
    print("- 建议先运行回测验证策略")
    print("- 监控程序运行状态")
    print("- 设置合理的风险参数")

def main():
    """主函数"""
    print("🚀 Lighter量化交易程序快速部署")
    print("=" * 60)
    
    # 检查Python版本
    if not check_python_version():
        return 1
    
    # 安装依赖
    if not install_dependencies():
        return 1
    
    # 创建目录
    if not create_directories():
        return 1
    
    # 设置配置
    if not setup_config():
        return 1
    
    # 测试连接
    if not test_connection():
        return 1
    
    # 运行回测
    if not run_backtest():
        return 1
    
    # 显示使用说明
    show_usage()
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  部署被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 部署过程中发生错误: {e}")
        sys.exit(1)
