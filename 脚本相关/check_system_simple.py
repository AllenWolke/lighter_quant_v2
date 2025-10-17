#!/usr/bin/env python3
"""
量化交易系统简单健康检查
不需要额外依赖
"""

import os
import sys
import subprocess
from datetime import datetime
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
    
    try:
        if sys.platform == 'win32':
            # Windows
            result = subprocess.run(['tasklist'], capture_output=True, text=True)
            output = result.stdout
            python_processes = [line for line in output.split('\n') if 'python' in line.lower()]
            
            if python_processes:
                print(f"[OK] Found {len(python_processes)} Python processes")
                print("  (Cannot determine if trading process, please check windows)")
                return True
            else:
                print("[FAIL] No Python processes found")
                return False
        else:
            # Linux/macOS
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            output = result.stdout
            trading_processes = [line for line in output.split('\n') 
                               if 'start_trading.py' in line or 'main.py' in line]
            
            if trading_processes:
                print(f"[OK] Found {len(trading_processes)} trading processes")
                for proc in trading_processes[:3]:
                    print(f"  {proc.strip()}")
                return True
            else:
                print("[FAIL] No trading processes found")
                return False
    except Exception as e:
        print(f"[WARN] Cannot check processes: {e}")
        return None

def check_log_file():
    """检查日志文件"""
    print("\n2. 检查日志文件")
    print("-" * 60)
    
    log_file = Path("logs/quant_trading.log")
    
    if not log_file.exists():
        print("[FAIL] Log file not found: logs/quant_trading.log")
        print("  Hint: System may never started")
        return False
    
    # 获取文件信息
    stat = log_file.stat()
    file_size = stat.st_size / 1024  # KB
    modified_time = datetime.fromtimestamp(stat.st_mtime)
    time_since_update = datetime.now() - modified_time
    minutes_since_update = time_since_update.total_seconds() / 60
    
    print(f"[OK] Log file exists")
    print(f"  路径: {log_file.absolute()}")
    print(f"  大小: {file_size:.2f} KB")
    print(f"  最后更新: {modified_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  距今: {minutes_since_update:.1f} 分钟")
    
    # 检查日志是否太久没更新
    if minutes_since_update > 10:
        print(f"  [CRITICAL] Log not updated for >10 minutes")
        print(f"     System may be crashed or stuck")
    elif minutes_since_update > 5:
        print(f"  [WARN] Log not updated for >5 minutes")
        print(f"     Possible reasons:")
        print(f"     - Program stuck")
        print(f"     - tick_interval too large")
        print(f"     - No trading activity (normal)")
    elif minutes_since_update < 0.5:
        print(f"  [OK] Log is actively updating")
    else:
        print(f"  [OK] Log is normal (waiting)")
    
    # 读取最后几行
    print("\n  Last 5 lines:")
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            for line in lines[-5:]:
                print(f"    {line.rstrip()}")
    except Exception as e:
        print(f"  Read log failed: {e}")
    
    return minutes_since_update < 10

def check_config():
    """检查配置"""
    print("\n3. 检查配置文件")
    print("-" * 60)
    
    config_file = Path("config.yaml")
    
    if not config_file.exists():
        print("[FAIL] Config file not found: config.yaml")
        return False
    
    print("[OK] Config file exists")
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 简单检查关键配置
        if 'tick_interval' in content:
            # 提取 tick_interval 值
            for line in content.split('\n'):
                if 'tick_interval' in line and ':' in line:
                    value = line.split(':')[1].strip()
                    print(f"  tick_interval: {value}")
                    try:
                        interval = float(value)
                        if interval > 60:
                            print(f"  [WARN] tick_interval is large, log updates slow")
                    except:
                        pass
        
        # 检查策略配置
        enabled_count = content.count('enabled: true')
        if enabled_count > 0:
            print(f"  Enabled strategies: {enabled_count}")
        else:
            print(f"  [WARN] No strategies may be enabled")
        
    except Exception as e:
        print(f"  [WARN] Read config failed: {e}")
    
    return True

def analyze_log_activity():
    """分析日志活动"""
    print("\n4. 分析日志活动")
    print("-" * 60)
    
    log_file = Path("logs/quant_trading.log")
    if not log_file.exists():
        print("[FAIL] Log file not found")
        return
    
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            recent_lines = lines[-100:] if len(lines) > 100 else lines
        
        # 统计不同类型的日志
        info_count = sum(1 for line in recent_lines if ' INFO ' in line)
        warning_count = sum(1 for line in recent_lines if ' WARNING ' in line)
        error_count = sum(1 for line in recent_lines if ' ERROR ' in line)
        signal_count = sum(1 for line in recent_lines if '交易信号' in line or 'SIGNAL' in line)
        
        print(f"  最近 {len(recent_lines)} 行日志统计:")
        print(f"    INFO: {info_count}")
        print(f"    WARNING: {warning_count}")
        print(f"    ERROR: {error_count}")
        print(f"    交易信号: {signal_count}")
        
        if signal_count == 0:
            print(f"\n  [INFO] No trading signals found")
            print(f"     This is NORMAL - strategy is waiting for opportunities")
        else:
            print(f"\n  [OK] Found {signal_count} trading signals")
        
        # 显示最近的错误
        if error_count > 0:
            print(f"\n  Recent errors (last 3):")
            error_lines = [line for line in recent_lines if ' ERROR ' in line]
            for line in error_lines[-3:]:
                print(f"    {line.rstrip()}")
        
    except Exception as e:
        print(f"  Analyze log failed: {e}")

def provide_recommendations(log_ok, process_ok):
    """提供建议"""
    print("\n5. 建议")
    print("-" * 60)
    
    if not process_ok:
        print("  [WARN] No running process detected")
        print("     Recommendation: Start system")
        print("     Command: python start_trading.py")
    elif not log_ok:
        print("  [WARN] Log not updated for long time")
        print("     Recommendations:")
        print("     1. Restart system (Ctrl+C then rerun)")
        print("     2. Check for errors in log")
        print("     3. Check network connection")
    else:
        print("  [OK] System looks normal")
        print("     If no trading signals, this is NORMAL")
        print("     Strategy is waiting for opportunities")
    
    print("\n  Monitoring commands:")
    if sys.platform == 'win32':
        print("     Real-time monitor: monitor_trading.bat")
        print("     View signals: view_signals.bat")
    else:
        print("     Real-time monitor: ./monitor_trading.sh")
        print("     View signals: ./view_signals.sh")
    
    print("\n  Watch log updates:")
    print("     python watch_log_updates.py")

def main():
    """主函数"""
    print_header()
    
    # 执行检查
    process_ok = check_process_running()
    log_ok = check_log_file()
    config_ok = check_config()
    analyze_log_activity()
    provide_recommendations(log_ok, process_ok is not False)
    
    print("\n" + "=" * 60)
    if process_ok and log_ok:
        print("  Overall Status: [OK] System is running")
    elif log_ok:
        print("  Overall Status: [OK] System may be normal (log updating)")
    else:
        print("  Overall Status: [WARN] Issues found, see recommendations")
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
        import traceback
        traceback.print_exc()
        sys.exit(1)

