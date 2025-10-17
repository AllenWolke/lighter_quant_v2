#!/usr/bin/env python3
"""
实时监测日志更新
每10秒检查一次日志是否更新
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

def watch_log():
    """监控日志文件更新"""
    log_file = Path("logs/quant_trading.log")
    
    print("=" * 60)
    print("  实时监测日志更新")
    print("=" * 60)
    print()
    print(f"监控文件: {log_file.absolute()}")
    print("每10秒检查一次")
    print("按 Ctrl+C 停止监控")
    print()
    print("-" * 60)
    
    last_mtime = None
    last_size = None
    no_update_count = 0
    
    while True:
        try:
            if not log_file.exists():
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ 日志文件不存在")
                time.sleep(10)
                continue
            
            # 获取文件信息
            stat = log_file.stat()
            current_mtime = stat.st_mtime
            current_size = stat.st_size
            modified_time = datetime.fromtimestamp(current_mtime)
            
            # 检查是否更新
            if last_mtime is None:
                # 第一次检查
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 开始监控")
                print(f"  文件大小: {current_size / 1024:.2f} KB")
                print(f"  最后更新: {modified_time.strftime('%H:%M:%S')}")
                last_mtime = current_mtime
                last_size = current_size
            elif current_mtime > last_mtime or current_size != last_size:
                # 文件已更新
                size_change = current_size - last_size
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ 日志已更新")
                print(f"  新增: {size_change} 字节")
                print(f"  当前大小: {current_size / 1024:.2f} KB")
                
                # 显示新增内容
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        # 显示最后3行
                        for line in lines[-3:]:
                            print(f"    {line.rstrip()}")
                except:
                    pass
                
                last_mtime = current_mtime
                last_size = current_size
                no_update_count = 0
            else:
                # 文件未更新
                no_update_count += 1
                time_since_update = datetime.now() - modified_time
                minutes = time_since_update.total_seconds() / 60
                
                status = "○"
                if minutes > 5:
                    status = "⚠️"
                elif minutes > 10:
                    status = "✗"
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {status} 日志未更新 ({minutes:.1f} 分钟)")
                
                if no_update_count >= 6:  # 1分钟
                    print(f"  提示: 日志超过1分钟未更新，系统可能卡住")
                    print(f"  建议: 运行 python check_system_health.py 检查系统状态")
                    no_update_count = 0  # 重置计数，避免重复提示
            
            print("-" * 60)
            time.sleep(10)
            
        except KeyboardInterrupt:
            print("\n\n监控已停止")
            break
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 错误: {e}")
            time.sleep(10)

if __name__ == "__main__":
    watch_log()

