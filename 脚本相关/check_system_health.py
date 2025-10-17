#!/usr/bin/env python3
"""
量化交易系统健康检查脚本
实时监测系统是否正常运行
"""

import os
import sys
import time
import psutil
from datetime import datetime, timedelta
from pathlib import Path

def print_header():
    """打印标题"""
    print("=" * 60)
    print("  量化交易系统健康检查")
    print("=" * 60)
    print()

def check_process_running():
    """检查交易进程是否运行"""
    print("1. 检查进程状态")
    print("-" * 60)
    
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and any('start_trading.py' in str(cmd) or 'main.py' in str(cmd) for cmd in cmdline):
                processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    if processes:
        print(f"✓ 找到 {len(processes)} 个交易进程:")
        for proc in processes:
            try:
                cpu_percent = proc.cpu_percent(interval=1)
                memory_mb = proc.memory_info().rss / 1024 / 1024
                create_time = datetime.fromtimestamp(proc.create_time())
                uptime = datetime.now() - create_time
                
                print(f"  - PID: {proc.pid}")
                print(f"    CPU: {cpu_percent:.1f}%")
                print(f"    内存: {memory_mb:.1f} MB")
                print(f"    运行时间: {uptime}")
                print(f"    创建时间: {create_time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # 检查是否僵死
                if cpu_percent < 0.1 and uptime > timedelta(minutes=5):
                    print(f"    ⚠️  警告: CPU使用率很低，进程可能卡住")
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                print(f"  - PID: {proc.pid} (无法获取详细信息)")
        return True
    else:
        print("✗ 未找到运行中的交易进程")
        print("  提示: 可能需要启动 python start_trading.py")
        return False

def check_log_file():
    """检查日志文件"""
    print("\n2. 检查日志文件")
    print("-" * 60)
    
    log_file = Path("logs/quant_trading.log")
    
    if not log_file.exists():
        print("✗ 日志文件不存在: logs/quant_trading.log")
        print("  提示: 系统可能从未启动过")
        return False
    
    # 获取文件信息
    stat = log_file.stat()
    file_size = stat.st_size / 1024  # KB
    modified_time = datetime.fromtimestamp(stat.st_mtime)
    time_since_update = datetime.now() - modified_time
    
    print(f"✓ 日志文件存在")
    print(f"  路径: {log_file.absolute()}")
    print(f"  大小: {file_size:.2f} KB")
    print(f"  最后更新: {modified_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  距今: {time_since_update}")
    
    # 检查日志是否太久没更新
    if time_since_update > timedelta(minutes=5):
        print(f"  ⚠️  警告: 日志 {time_since_update.total_seconds()/60:.1f} 分钟没有更新")
        print(f"     可能原因:")
        print(f"     - 程序卡住或崩溃")
        print(f"     - tick_interval 设置过大")
        print(f"     - 没有交易信号产生")
    elif time_since_update < timedelta(seconds=30):
        print(f"  ✓ 日志正在更新 (最近更新: {time_since_update.total_seconds():.0f} 秒前)")
    
    # 读取最后几行
    print("\n  最后 5 行日志:")
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines[-5:]:
                print(f"    {line.rstrip()}")
    except Exception as e:
        print(f"  读取日志失败: {e}")
    
    return True

def check_config():
    """检查配置"""
    print("\n3. 检查配置文件")
    print("-" * 60)
    
    config_file = Path("config.yaml")
    
    if not config_file.exists():
        print("✗ 配置文件不存在: config.yaml")
        return False
    
    print("✓ 配置文件存在")
    
    # 读取配置
    try:
        import yaml
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 检查关键配置
        if 'trading' in config:
            tick_interval = config['trading'].get('tick_interval', 1.0)
            print(f"  tick_interval: {tick_interval} 秒")
            if tick_interval > 60:
                print(f"  ⚠️  警告: tick_interval 很大，日志更新会很慢")
        
        if 'log' in config:
            log_level = config['log'].get('level', 'INFO')
            print(f"  日志级别: {log_level}")
        
        # 检查策略配置
        if 'strategies' in config:
            enabled_strategies = []
            for strategy_name, strategy_config in config['strategies'].items():
                if isinstance(strategy_config, dict) and strategy_config.get('enabled', False):
                    enabled_strategies.append(strategy_name)
            
            if enabled_strategies:
                print(f"  启用的策略: {', '.join(enabled_strategies)}")
            else:
                print(f"  ⚠️  警告: 没有启用的策略")
        
    except Exception as e:
        print(f"  ⚠️  读取配置失败: {e}")
    
    return True

def check_system_resources():
    """检查系统资源"""
    print("\n4. 检查系统资源")
    print("-" * 60)
    
    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    print(f"  CPU 使用率: {cpu_percent}%")
    if cpu_percent > 90:
        print(f"  ⚠️  警告: CPU使用率过高")
    
    # 内存
    memory = psutil.virtual_memory()
    print(f"  内存使用率: {memory.percent}% ({memory.used / 1024**3:.1f} GB / {memory.total / 1024**3:.1f} GB)")
    if memory.percent > 90:
        print(f"  ⚠️  警告: 内存使用率过高")
    
    # 磁盘
    disk = psutil.disk_usage('.')
    print(f"  磁盘使用率: {disk.percent}% ({disk.used / 1024**3:.1f} GB / {disk.total / 1024**3:.1f} GB)")
    if disk.percent > 90:
        print(f"  ⚠️  警告: 磁盘空间不足")

def analyze_log_activity():
    """分析日志活动"""
    print("\n5. 分析日志活动")
    print("-" * 60)
    
    log_file = Path("logs/quant_trading.log")
    if not log_file.exists():
        print("✗ 日志文件不存在")
        return
    
    try:
        # 读取最后100行
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            recent_lines = lines[-100:]
        
        # 统计不同类型的日志
        info_count = sum(1 for line in recent_lines if ' INFO ' in line)
        warning_count = sum(1 for line in recent_lines if ' WARNING ' in line)
        error_count = sum(1 for line in recent_lines if ' ERROR ' in line)
        
        print(f"  最近100行日志统计:")
        print(f"    INFO: {info_count}")
        print(f"    WARNING: {warning_count}")
        print(f"    ERROR: {error_count}")
        
        # 检查是否有交易信号
        signal_count = sum(1 for line in recent_lines if '交易信号' in line)
        print(f"    交易信号: {signal_count}")
        
        if signal_count == 0:
            print(f"  ℹ️  提示: 没有发现交易信号")
            print(f"     可能原因:")
            print(f"     - 市场条件不满足策略要求")
            print(f"     - 策略参数阈值设置过高")
            print(f"     - 数据积累不足（需要20-50根K线）")
        
        # 检查最近的错误
        if error_count > 0:
            print(f"\n  最近的错误:")
            for line in recent_lines:
                if ' ERROR ' in line:
                    print(f"    {line.rstrip()}")
        
    except Exception as e:
        print(f"  分析日志失败: {e}")

def provide_recommendations():
    """提供建议"""
    print("\n6. 建议")
    print("-" * 60)
    
    log_file = Path("logs/quant_trading.log")
    if log_file.exists():
        stat = log_file.stat()
        modified_time = datetime.fromtimestamp(stat.st_mtime)
        time_since_update = datetime.now() - modified_time
        
        if time_since_update > timedelta(minutes=5):
            print("  ⚠️  日志长时间未更新，建议:")
            print("     1. 检查进程是否卡住")
            print("     2. 重启系统: Ctrl+C 停止，然后重新运行")
            print("     3. 检查网络连接")
            print("     4. 查看完整日志: tail -100 logs/quant_trading.log")
        else:
            print("  ✓ 系统看起来正常运行")
            print("     - 如果没有交易信号，这是正常的")
            print("     - 策略在等待合适的交易机会")
    
    print("\n  实时监控命令:")
    print("     Windows: monitor_trading.bat")
    print("     Linux/macOS: ./monitor_trading.sh")
    print("\n  查看信号统计:")
    print("     Windows: view_signals.bat")
    print("     Linux/macOS: ./view_signals.sh")

def main():
    """主函数"""
    print_header()
    
    # 执行检查
    process_ok = check_process_running()
    log_ok = check_log_file()
    config_ok = check_config()
    check_system_resources()
    
    if log_ok:
        analyze_log_activity()
    
    provide_recommendations()
    
    print("\n" + "=" * 60)
    if process_ok and log_ok:
        print("  总体状态: 系统正在运行")
    else:
        print("  总体状态: 发现问题，请查看上述建议")
    print("=" * 60)
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n检查已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n错误: {e}")
        sys.exit(1)

