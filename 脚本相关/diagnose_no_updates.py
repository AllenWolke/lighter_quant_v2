#!/usr/bin/env python3
"""
诊断日志长时间不更新的问题
"""

import os
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def check_log_file():
    """检查日志文件状态"""
    print_section("1. 日志文件状态")
    
    log_file = Path("logs/quant_trading.log")
    
    if not log_file.exists():
        print("[CRITICAL] 日志文件不存在!")
        print("  原因: 程序从未成功启动")
        print("  建议: 检查 start_trading.py 是否正常运行")
        return False, 0
    
    stat = log_file.stat()
    file_size = stat.st_size
    modified_time = datetime.fromtimestamp(stat.st_mtime)
    time_since_update = datetime.now() - modified_time
    hours = time_since_update.total_seconds() / 3600
    
    print(f"文件路径: {log_file.absolute()}")
    print(f"文件大小: {file_size / 1024:.2f} KB")
    print(f"最后修改: {modified_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"距今时间: {hours:.1f} 小时 ({time_since_update.total_seconds() / 60:.0f} 分钟)")
    
    if hours > 2:
        print(f"\n[CRITICAL] 日志超过 {hours:.1f} 小时未更新!")
        print("  这是异常情况，系统很可能:")
        print("  1. 已经崩溃")
        print("  2. 被卡住")
        print("  3. 网络连接断开")
        return False, hours
    elif hours > 0.5:
        print(f"\n[WARNING] 日志 {hours:.1f} 小时未更新")
        print("  需要进一步检查")
        return True, hours
    else:
        print(f"\n[OK] 日志正常更新")
        return True, hours

def check_process():
    """检查进程是否运行"""
    print_section("2. 进程状态")
    
    try:
        if sys.platform == 'win32':
            result = subprocess.run(['tasklist'], capture_output=True, text=True)
            python_procs = [line for line in result.stdout.split('\n') if 'python' in line.lower()]
        else:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            python_procs = [line for line in result.stdout.split('\n') 
                          if 'python' in line and ('start_trading' in line or 'main.py' in line)]
        
        if python_procs:
            print(f"[OK] 找到 {len(python_procs)} 个相关进程")
            for proc in python_procs[:3]:
                print(f"  {proc.strip()}")
            return True
        else:
            print("[CRITICAL] 未找到运行中的 Python 进程!")
            print("  原因: 程序已经停止或崩溃")
            print("  建议: 重新启动 python start_trading.py")
            return False
            
    except Exception as e:
        print(f"[ERROR] 无法检查进程: {e}")
        return None

def analyze_log_content():
    """分析日志内容"""
    print_section("3. 日志内容分析")
    
    log_file = Path("logs/quant_trading.log")
    if not log_file.exists():
        print("[SKIP] 日志文件不存在")
        return
    
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        if not lines:
            print("[CRITICAL] 日志文件为空!")
            print("  原因: 程序从未写入日志")
            return
        
        total_lines = len(lines)
        print(f"总行数: {total_lines}")
        
        # 分析最后100行
        recent = lines[-100:] if total_lines > 100 else lines
        
        # 统计日志类型
        info_count = sum(1 for l in recent if ' INFO ' in l)
        warn_count = sum(1 for l in recent if ' WARNING ' in l)
        error_count = sum(1 for l in recent if ' ERROR ' in l)
        signal_count = sum(1 for l in recent if '交易信号' in l)
        
        print(f"\n最近 {len(recent)} 行统计:")
        print(f"  INFO: {info_count}")
        print(f"  WARNING: {warn_count}")
        print(f"  ERROR: {error_count}")
        print(f"  交易信号: {signal_count}")
        
        # 查找最后一条日志
        last_line = lines[-1].strip() if lines else ""
        if last_line:
            print(f"\n最后一条日志:")
            print(f"  {last_line}")
            
            # 提取时间戳
            try:
                timestamp_str = last_line.split(' - ')[0]
                last_log_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                time_diff = datetime.now() - last_log_time
                print(f"  时间: {last_log_time.strftime('%H:%M:%S')}")
                print(f"  距今: {time_diff.total_seconds() / 60:.0f} 分钟")
            except:
                pass
        
        # 查找关键事件
        print(f"\n关键事件检查:")
        
        # 是否成功启动
        started = any("进入主循环" in line for line in lines)
        print(f"  {'[OK]' if started else '[FAIL]'} 进入主循环: {'是' if started else '否'}")
        
        # 是否有错误
        if error_count > 0:
            print(f"  [WARNING] 发现 {error_count} 个错误")
            print(f"\n  最近的错误:")
            error_lines = [l for l in recent if ' ERROR ' in l]
            for line in error_lines[-3:]:
                print(f"    {line.rstrip()}")
        
        # 是否卡在某处
        if total_lines < 50 and not started:
            print(f"\n[CRITICAL] 日志很少且未进入主循环")
            print(f"  原因: 启动过程中卡住或失败")
        
        # 显示最后10行
        print(f"\n最后 10 行日志:")
        for line in lines[-10:]:
            print(f"  {line.rstrip()}")
        
    except Exception as e:
        print(f"[ERROR] 分析日志失败: {e}")

def check_config():
    """检查配置"""
    print_section("4. 配置检查")
    
    config_file = Path("config.yaml")
    if not config_file.exists():
        print("[CRITICAL] config.yaml 不存在!")
        return
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键配置
        print("关键配置:")
        
        # tick_interval
        for line in content.split('\n'):
            if 'tick_interval' in line and ':' in line and not line.strip().startswith('#'):
                print(f"  {line.strip()}")
                try:
                    value = line.split(':')[1].split('#')[0].strip()
                    interval = float(value)
                    if interval > 60:
                        print(f"  [WARNING] tick_interval={interval}秒，可能导致日志更新慢")
                except:
                    pass
        
        # base_url
        for line in content.split('\n'):
            if 'base_url' in line and ':' in line and not line.strip().startswith('#'):
                print(f"  {line.strip()}")
        
        # 私钥配置
        for line in content.split('\n'):
            if 'api_key_private_key' in line and ':' in line:
                if 'YOUR_' in line or '""' in line:
                    print(f"  [CRITICAL] API 私钥未配置!")
                else:
                    print(f"  [OK] API 私钥已配置")
                break
        
        # 策略配置
        enabled = content.count('enabled: true')
        print(f"\n启用的策略数: {enabled}")
        if enabled == 0:
            print(f"  [WARNING] 没有启用的策略!")
        
    except Exception as e:
        print(f"[ERROR] 读取配置失败: {e}")

def check_network():
    """检查网络连接"""
    print_section("5. 网络连接检查")
    
    # 从配置读取 base_url
    base_url = None
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            for line in f:
                if 'base_url' in line and ':' in line and not line.strip().startswith('#'):
                    # 提取 URL，处理各种格式
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        url_part = parts[1].strip().strip('"').strip("'")
                        # 移除注释
                        if '#' in url_part:
                            url_part = url_part.split('#')[0].strip()
                        base_url = url_part
                        break
        
        if not base_url:
            print("[WARN] 无法从配置读取 base_url")
            return
        
        print(f"目标服务器: {base_url}")
        
        # 提取主机名
        host = base_url.replace('https://', '').replace('http://', '').split('/')[0]
        
        # 方法1: 尝试 HTTP 连接测试（更可靠）
        print(f"\n方法1: HTTP 连接测试")
        try:
            import urllib.request
            import socket
            
            # 设置超时
            socket.setdefaulttimeout(10)
            
            # 尝试连接
            try:
                req = urllib.request.Request(base_url, method='HEAD')
                with urllib.request.urlopen(req, timeout=10) as response:
                    print(f"[OK] HTTP 连接成功")
                    print(f"  状态码: {response.status}")
                    return
            except urllib.error.HTTPError as e:
                # HTTP 错误也说明连接成功
                if e.code in [200, 301, 302, 400, 401, 403, 404]:
                    print(f"[OK] HTTP 连接成功（状态码: {e.code}）")
                    print(f"  服务器可访问")
                    return
                else:
                    print(f"[WARN] HTTP 错误: {e.code}")
            except urllib.error.URLError as e:
                print(f"[FAIL] HTTP 连接失败: {e.reason}")
                print(f"  可能原因: 网络不通或服务器离线")
            except socket.timeout:
                print(f"[FAIL] HTTP 连接超时")
                print(f"  可能原因: 网络慢或服务器无响应")
            except Exception as e:
                print(f"[WARN] HTTP 测试失败: {e}")
        
        except ImportError:
            print("[WARN] urllib 不可用，跳过 HTTP 测试")
        
        # 方法2: ping 测试（作为备选）
        print(f"\n方法2: Ping 测试（参考）")
        try:
            if sys.platform == 'win32':
                result = subprocess.run(['ping', '-n', '2', host], 
                                      capture_output=True, text=True, timeout=10)
            else:
                result = subprocess.run(['ping', '-c', '2', host], 
                                      capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"[OK] Ping 成功")
            else:
                print(f"[INFO] Ping 失败")
                print(f"  注意: 某些服务器禁用 ping，这不一定表示连接有问题")
                print(f"  以 HTTP 连接测试结果为准")
        except subprocess.TimeoutExpired:
            print(f"[INFO] Ping 超时（某些服务器禁用 ping）")
        except Exception as e:
            print(f"[INFO] 无法执行 ping: {e}")
        
    except FileNotFoundError:
        print("[WARN] config.yaml 不存在")
    except Exception as e:
        print(f"[WARN] 网络检查失败: {e}")

def provide_diagnosis(log_ok, hours_since_update, process_ok):
    """提供诊断结果"""
    print_section("6. 诊断结果和建议")
    
    print("问题分析:")
    print("-" * 60)
    
    if not process_ok:
        print("\n[原因1] 程序未运行 ⭐ 最可能")
        print("  症状: 找不到 Python 进程")
        print("  原因: 程序已崩溃、被停止、或从未启动")
        print("  证据: 进程检查失败")
        print("\n  解决方案:")
        print("  1. 重新启动: python start_trading.py")
        print("  2. 观察启动过程是否有错误")
        print("  3. 确保看到 '进入主循环...'")
        
    elif hours_since_update > 2:
        print("\n[原因2] 程序卡住 ⭐ 最可能")
        print("  症状: 进程存在但日志不更新")
        print(f"  持续时间: {hours_since_update:.1f} 小时")
        print("  可能原因:")
        print("  - 网络请求卡住（最常见）")
        print("  - 死锁或无限循环")
        print("  - API 调用无响应")
        print("  - 异常未捕获导致线程卡住")
        print("\n  解决方案:")
        print("  1. 强制停止进程:")
        if sys.platform == 'win32':
            print("     任务管理器 -> 结束 python.exe 进程")
            print("     或: taskkill /F /IM python.exe")
        else:
            print("     ps aux | grep start_trading.py")
            print("     kill -9 <PID>")
        print("  2. 检查网络连接")
        print("  3. 重新启动系统")
        
    else:
        print("\n[原因3] 配置问题")
        print("  检查上述配置部分的警告")

def check_startup_logs():
    """检查启动日志"""
    print_section("7. 启动日志检查")
    
    log_file = Path("logs/quant_trading.log")
    if not log_file.exists():
        print("[SKIP] 日志文件不存在")
        return
    
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # 检查关键启动步骤
        checks = {
            "启动交易引擎": False,
            "初始化数据管理器": False,
            "发现.*个市场": False,
            "初始化订单管理器": False,
            "订单管理器初始化完成": False,
            "进入主循环": False
        }
        
        import re
        for line in lines:
            for key in checks:
                if re.search(key, line):
                    checks[key] = True
        
        print("启动步骤完成情况:")
        for step, completed in checks.items():
            status = "[OK]" if completed else "[FAIL]"
            print(f"  {status} {step}")
        
        # 分析卡在哪里
        if not checks["进入主循环"]:
            print("\n[CRITICAL] 程序未能进入主循环!")
            if not checks["发现.*个市场"]:
                print("  卡在: 获取市场数据")
                print("  原因: 网络连接问题或 API 错误")
            elif not checks["订单管理器初始化完成"]:
                print("  卡在: 初始化订单管理器")
                print("  原因: 客户端验证失败或网络问题")
            else:
                print("  卡在: 启动过程的某个环节")
        
        # 查找异常或错误
        print("\n错误检查:")
        errors = [l for l in lines if ' ERROR ' in l]
        if errors:
            print(f"  发现 {len(errors)} 个错误")
            print(f"\n  最后3个错误:")
            for err in errors[-3:]:
                print(f"    {err.rstrip()}")
        else:
            print("  [OK] 未发现错误日志")
        
        # 查找警告
        warnings = [l for l in lines if ' WARNING ' in l]
        if warnings:
            print(f"\n  发现 {len(warnings)} 个警告")
            print(f"\n  最后3个警告:")
            for warn in warnings[-3:]:
                print(f"    {warn.rstrip()}")
        
    except Exception as e:
        print(f"[ERROR] 分析启动日志失败: {e}")

def provide_solutions(hours_since_update):
    """提供解决方案"""
    print_section("8. 解决方案")
    
    print("立即执行:")
    print("-" * 60)
    
    if hours_since_update > 1:
        print("\n方案1: 重启系统 ⭐ 推荐")
        print("  步骤:")
        print("  1. 停止当前进程:")
        if sys.platform == 'win32':
            print("     - 找到运行 start_trading.py 的窗口")
            print("     - 按 Ctrl+C")
            print("     - 或在任务管理器中结束 python.exe")
        else:
            print("     - 按 Ctrl+C 停止")
            print("     - 或: ps aux | grep start_trading && kill -9 <PID>")
        
        print("\n  2. 检查配置:")
        print("     python test_lighter_connection.py")
        
        print("\n  3. 重新启动:")
        print("     python start_trading.py")
        
        print("\n  4. 监控启动过程:")
        print("     在新窗口运行:")
        if sys.platform == 'win32':
            print("     monitor_trading.bat")
        else:
            print("     bash monitor_trading.sh")
        
        print("\n  5. 验证成功:")
        print("     等待看到 '进入主循环...'")
        print("     然后运行: python check_system_simple.py")
    
    print("\n方案2: 诊断问题")
    print("  步骤:")
    print("  1. 查看完整日志:")
    if sys.platform == 'win32':
        print("     type logs\\quant_trading.log | more")
    else:
        print("     cat logs/quant_trading.log")
    
    print("\n  2. 查找错误:")
    if sys.platform == 'win32':
        print("     findstr \"ERROR\" logs\\quant_trading.log")
    else:
        print("     grep \"ERROR\" logs/quant_trading.log")
    
    print("\n  3. 测试连接:")
    print("     python test_lighter_connection.py")
    
    print("\n方案3: 启用详细日志")
    print("  修改 config.yaml:")
    print("  log:")
    print("    level: \"DEBUG\"  # 从 INFO 改为 DEBUG")
    print("\n  然后重启系统，获取更详细的日志")

def main():
    """主函数"""
    print("=" * 60)
    print("  日志长时间不更新 - 问题诊断")
    print("=" * 60)
    print()
    print("诊断工具将检查:")
    print("  1. 日志文件状态")
    print("  2. 进程运行状态")
    print("  3. 日志内容分析")
    print("  4. 配置问题")
    print("  5. 网络连接")
    print("  6. 诊断结果")
    print("  7. 启动日志分析")
    print("  8. 解决方案")
    
    # 执行检查
    log_ok, hours = check_log_file()
    process_ok = check_process()
    analyze_log_content()
    check_config()
    check_network()
    check_startup_logs()
    provide_solutions(hours)
    
    # 总结
    print_section("总结")
    
    if not log_ok and hours > 2:
        print("\n[CRITICAL] 系统异常 - 日志超过2小时未更新")
        print("\n最可能的原因:")
        if not process_ok:
            print("  1. 程序已崩溃或被停止")
            print("     → 重新启动系统")
        else:
            print("  1. 程序卡在网络请求")
            print("     → 检查网络连接")
            print("  2. 程序进入死锁")
            print("     → 强制停止并重启")
        
        print("\n立即执行:")
        print("  1. 停止进程 (Ctrl+C 或 kill)")
        print("  2. 运行: python test_lighter_connection.py")
        print("  3. 如果连接测试通过，重新启动")
    else:
        print("\n请查看上述诊断结果")
    
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n诊断已取消")
    except Exception as e:
        print(f"\n[ERROR] 诊断出错: {e}")
        import traceback
        traceback.print_exc()

