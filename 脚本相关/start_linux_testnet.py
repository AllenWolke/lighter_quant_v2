#!/usr/bin/env python3
"""
Linux测试网环境快速启动脚本
用于启动Lighter量化交易系统的Linux测试环境
"""

import os
import sys
import platform
import subprocess
import asyncio
import time
from pathlib import Path

def print_header():
    """打印系统标题"""
    print("=" * 50)
    print("   Lighter量化交易系统 - Linux测试环境")
    print("=" * 50)
    print()

def print_info(message):
    """打印信息"""
    print(f"[INFO] {message}")

def print_success(message):
    """打印成功信息"""
    print(f"[SUCCESS] {message}")

def print_error(message):
    """打印错误信息"""
    print(f"[ERROR] {message}")

def print_warning(message):
    """打印警告信息"""
    print(f"[WARNING] {message}")

def check_platform():
    """检查平台信息"""
    system = platform.system()
    print_info(f"检测到操作系统: {system}")
    
    if system == "Linux":
        return "linux"
    else:
        print_error(f"此脚本仅支持Linux系统，当前系统: {system}")
        return None

def check_python():
    """检查Python环境"""
    print_info("检查Python环境...")
    
    try:
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 9):
            print_error(f"Python版本过低: {version.major}.{version.minor}，需要3.9+")
            return False
        
        print_success(f"Python版本: {version.major}.{version.minor}.{version.micro}")
        return True
    except Exception as e:
        print_error(f"Python检查失败: {e}")
        return False

def check_virtual_env():
    """检查虚拟环境"""
    print_info("检查虚拟环境...")
    
    venv_path = Path("venv")
    if not venv_path.exists():
        print_error("未找到虚拟环境，请先创建虚拟环境")
        print_info("运行命令: python3 -m venv venv")
        return False
    
    print_success("虚拟环境检查通过")
    return True

def check_config_file():
    """检查配置文件"""
    print_info("检查配置文件...")
    
    config_file = "config_linux_testnet.yaml"
    if not Path(config_file).exists():
        print_error(f"未找到Linux测试网配置文件: {config_file}")
        print_info(f"请先复制并配置{config_file}文件")
        return False
    
    print_success("Linux测试网配置文件检查通过")
    return config_file

def check_dependencies():
    """检查依赖包"""
    print_info("检查依赖包...")
    
    try:
        import lighter
        import eth_account
        import pydantic
        import numpy
        import pandas
        print_success("关键依赖检查通过")
        return True
    except ImportError as e:
        print_warning(f"依赖缺失: {e}")
        print_info("尝试安装依赖...")
        
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                         check=True, capture_output=True)
            print_success("依赖安装完成")
            return True
        except subprocess.CalledProcessError as e:
            print_error(f"依赖安装失败: {e}")
            return False

def create_directories():
    """创建必要目录"""
    print_info("创建必要目录...")
    
    directories = ["logs", "data", "backups"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        # 设置权限
        os.chmod(directory, 0o755)
    
    print_success("目录创建完成")

def check_network():
    """检查网络连接"""
    print_info("检查网络连接...")
    
    try:
        result = subprocess.run(["ping", "-c", "3", "testnet.zklighter.elliot.ai"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print_success("测试网连接正常")
        else:
            print_warning("测试网连接异常，请检查网络设置")
    except subprocess.TimeoutExpired:
        print_warning("网络连接超时")
    except FileNotFoundError:
        print_warning("ping命令不可用，跳过网络检查")

async def test_lighter_connection(config_file):
    """测试Lighter连接"""
    print_info("测试Lighter连接...")
    
    try:
        sys.path.append('.')
        from quant_trading.utils.config import Config
        import lighter
        
        config = Config.from_file(config_file)
        configuration = lighter.Configuration()
        configuration.host = config.lighter_base_url
        api_client = lighter.ApiClient(configuration)
        
        block_api = lighter.BlockApi(api_client)
        blocks = await block_api.blocks(limit=1)
        print_success("Lighter连接测试通过")
        await api_client.close()
        return True
    except Exception as e:
        print_warning(f"Lighter连接测试失败: {e}")
        print_info("注意: 这是测试环境，连接失败不影响基本功能")
        return False

def show_menu():
    """显示启动菜单"""
    print("=" * 50)
    print("   选择启动模式:")
    print("=" * 50)
    print("1. 启动Web系统 (前端 + 后端)")
    print("2. 启动量化交易系统 (命令行)")
    print("3. 启动完整系统 (Web + 交易)")
    print("4. 启动系统服务")
    print("5. 运行回测")
    print("6. 系统监控")
    print("7. 退出")
    print("=" * 50)

def start_web_system():
    """启动Web系统"""
    print_info("启动Web系统...")
    
    # 启动后端
    print_info("启动后端服务...")
    backend_cmd = [sys.executable, "web_backend/main.py"]
    
    try:
        # 后台运行后端
        backend_process = subprocess.Popen(backend_cmd, 
                                         stdout=open("logs/backend.log", "w"),
                                         stderr=subprocess.STDOUT)
        
        with open("logs/backend.pid", "w") as f:
            f.write(str(backend_process.pid))
        
        print_success(f"后端服务启动成功 (PID: {backend_process.pid})")
    except Exception as e:
        print_error(f"后端服务启动失败: {e}")
        return False
    
    # 等待后端启动
    time.sleep(5)
    
    # 启动前端
    print_info("启动前端服务...")
    frontend_cmd = ["npm", "start"]
    frontend_dir = Path("web_frontend")
    
    try:
        # 后台运行前端
        frontend_process = subprocess.Popen(frontend_cmd, 
                                          cwd=frontend_dir,
                                          stdout=open("logs/frontend.log", "w"),
                                          stderr=subprocess.STDOUT)
        
        with open("logs/frontend.pid", "w") as f:
            f.write(str(frontend_process.pid))
        
        print_success(f"前端服务启动成功 (PID: {frontend_process.pid})")
    except Exception as e:
        print_error(f"前端服务启动失败: {e}")
        return False
    
    print_success("Web系统启动完成！")
    print("后端地址: http://localhost:8000")
    print("前端地址: http://localhost:3000")
    return True

def start_trading_system(config_file):
    """启动交易系统"""
    print_info("启动量化交易系统...")
    
    print_info("注意: 这是测试环境，将使用模拟交易模式")
    
    cmd = [sys.executable, "main.py", "--config", config_file]
    
    try:
        # 后台运行交易系统
        trading_process = subprocess.Popen(cmd, 
                                         stdout=open("logs/trading.log", "w"),
                                         stderr=subprocess.STDOUT)
        
        with open("logs/trading.pid", "w") as f:
            f.write(str(trading_process.pid))
        
        print_success(f"交易系统启动成功 (PID: {trading_process.pid})")
        print("日志文件: logs/trading.log")
        print("注意: 测试环境使用模拟交易，不会进行实际交易")
        return True
    except Exception as e:
        print_error(f"交易系统启动失败: {e}")
        return False

def start_full_system(config_file):
    """启动完整系统"""
    print_info("启动完整系统...")
    
    if start_web_system():
        time.sleep(5)
        return start_trading_system(config_file)
    return False

def start_system_service():
    """启动系统服务"""
    print_info("启动系统服务...")
    
    try:
        result = subprocess.run(["sudo", "systemctl", "start", "lighter-trading-test"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print_success("系统服务启动成功")
            
            # 显示服务状态
            status_result = subprocess.run(["systemctl", "status", "lighter-trading-test"], 
                                         capture_output=True, text=True)
            print(status_result.stdout)
        else:
            print_error(f"系统服务启动失败: {result.stderr}")
    except FileNotFoundError:
        print_error("systemctl命令不存在，请检查系统服务配置")

def run_backtest(config_file):
    """运行回测"""
    print_info("运行回测...")
    
    print("可用的回测选项:")
    print("1. 动量策略回测")
    print("2. 均值回归策略回测")
    print("3. 自定义回测")
    
    choice = input("请选择回测类型 (1-3): ")
    
    if choice == "1":
        strategy = "momentum"
    elif choice == "2":
        strategy = "mean_reversion"
    elif choice == "3":
        strategy = input("请输入策略名称: ")
    else:
        print_error("无效选择")
        return
    
    start_date = input("请输入开始日期 (YYYY-MM-DD) [默认: 2024-01-01]: ") or "2024-01-01"
    end_date = input("请输入结束日期 (YYYY-MM-DD) [默认: 2024-01-31]: ") or "2024-01-31"
    
    cmd = [sys.executable, "run_backtest.py", 
           "--strategy", strategy,
           "--start-date", start_date,
           "--end-date", end_date,
           "--config", config_file]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print_info("回测已停止")

def system_monitor():
    """系统监控"""
    print_info("启动系统监控...")
    
    if Path("monitor_mainnet.py").exists():
        subprocess.run([sys.executable, "monitor_mainnet.py"])
    else:
        print_warning("监控脚本不存在，显示基本系统信息")
        
        # 显示基本系统信息
        print("\n系统状态:")
        print(f"操作系统: {platform.system()} {platform.release()}")
        print(f"Python版本: {sys.version}")
        print(f"当前目录: {os.getcwd()}")
        
        # 检查进程状态
        print("\n进程状态:")
        pid_files = ["logs/trading.pid", "logs/backend.pid", "logs/frontend.pid"]
        for pid_file in pid_files:
            if Path(pid_file).exists():
                with open(pid_file, "r") as f:
                    pid = f.read().strip()
                try:
                    # 检查进程是否存在
                    result = subprocess.run(["ps", "-p", pid], capture_output=True)
                    if result.returncode == 0:
                        service_name = Path(pid_file).stem
                        print(f"  {service_name}: 运行中 (PID: {pid})")
                    else:
                        service_name = Path(pid_file).stem
                        print(f"  {service_name}: 已停止")
                except:
                    pass

def check_process_status():
    """检查进程状态"""
    print_info("检查系统进程状态...")
    
    pid_files = ["logs/trading.pid", "logs/backend.pid", "logs/frontend.pid"]
    running_processes = []
    
    for pid_file in pid_files:
        if Path(pid_file).exists():
            with open(pid_file, "r") as f:
                pid = f.read().strip()
            try:
                result = subprocess.run(["ps", "-p", pid], capture_output=True)
                if result.returncode == 0:
                    service_name = Path(pid_file).stem
                    running_processes.append((service_name, pid))
            except:
                pass
    
    if running_processes:
        print_success(f"发现 {len(running_processes)} 个运行中的服务:")
        for service_name, pid in running_processes:
            print(f"  - {service_name}: PID {pid}")
    else:
        print_info("没有发现运行中的服务")
    
    return running_processes

async def main():
    """主函数"""
    print_header()
    
    # 检查平台
    platform_type = check_platform()
    if not platform_type:
        return
    
    # 检查Python环境
    if not check_python():
        return
    
    # 检查虚拟环境
    if not check_virtual_env():
        return
    
    # 检查配置文件
    config_file = check_config_file()
    if not config_file:
        return
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 创建目录
    create_directories()
    
    # 检查网络
    check_network()
    
    # 测试连接
    await test_lighter_connection(config_file)
    
    print()
    print_success("所有检查完成，系统准备就绪！")
    print()
    print_info("注意: 这是测试环境，主要用于策略开发和功能测试")
    print()
    
    # 检查现有进程
    check_process_status()
    print()
    
    # 主循环
    while True:
        show_menu()
        choice = input("请输入选择 (1-7): ")
        
        try:
            if choice == "1":
                start_web_system()
            elif choice == "2":
                start_trading_system(config_file)
            elif choice == "3":
                start_full_system(config_file)
            elif choice == "4":
                start_system_service()
            elif choice == "5":
                run_backtest(config_file)
            elif choice == "6":
                system_monitor()
            elif choice == "7":
                print_info("退出系统")
                break
            else:
                print_error("无效选择，请重新输入")
        except KeyboardInterrupt:
            print_info("\n操作已取消")
        except Exception as e:
            print_error(f"执行失败: {e}")
        
        print()
        input("按回车键继续...")
        print()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_info("\n程序已退出")
    except Exception as e:
        print_error(f"程序异常退出: {e}")
