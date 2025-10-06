#!/usr/bin/env python3
"""
主网监控脚本
监控交易程序运行状态和风险指标
"""

import time
import os
import subprocess
import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from quant_trading import Config
import lighter


class MainnetMonitor:
    """主网监控器"""
    
    def __init__(self):
        self.config = None
        self.api_client = None
        self.last_balance = None
        self.start_time = datetime.now()
        
    def load_config(self):
        """加载配置"""
        try:
            self.config = Config.from_file("config_mainnet.yaml")
            return True
        except Exception as e:
            print(f"❌ 配置加载失败: {e}")
            return False
    
    async def init_api_client(self):
        """初始化API客户端"""
        try:
            self.api_client = lighter.ApiClient(
                configuration=lighter.Configuration(host=self.config.lighter_config["base_url"])
            )
            return True
        except Exception as e:
            print(f"❌ API客户端初始化失败: {e}")
            return False
    
    def check_process(self):
        """检查进程状态"""
        try:
            result = subprocess.run(['pgrep', '-f', 'start_mainnet.py'], 
                                  capture_output=True, text=True)
            return len(result.stdout.strip()) > 0
        except:
            return False
    
    def check_logs(self):
        """检查日志文件"""
        log_file = "logs/mainnet_trading.log"
        if not os.path.exists(log_file):
            return False
        
        # 检查最近5分钟是否有日志
        stat = os.stat(log_file)
        return (time.time() - stat.st_mtime) < 300
    
    def get_log_errors(self):
        """获取最近的错误日志"""
        log_file = "logs/mainnet_trading.log"
        if not os.path.exists(log_file):
            return []
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 获取最近100行的错误
            recent_lines = lines[-100:]
            errors = [line.strip() for line in recent_lines if 'ERROR' in line]
            return errors[-5:]  # 返回最近5个错误
        except:
            return []
    
    async def get_account_balance(self):
        """获取账户余额"""
        try:
            if not self.api_client:
                return None
            
            account_api = lighter.AccountApi(self.api_client)
            account = await account_api.account(
                by="index", 
                value=str(self.config.lighter_config["account_index"])
            )
            
            if account:
                return float(account.balance) if account.balance else 0.0
            return None
        except Exception as e:
            print(f"获取账户余额失败: {e}")
            return None
    
    def calculate_uptime(self):
        """计算运行时间"""
        uptime = datetime.now() - self.start_time
        hours, remainder = divmod(uptime.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
    
    def print_status(self, process_running, logs_updated, balance, errors):
        """打印状态信息"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        uptime = self.calculate_uptime()
        
        print(f"\n[{timestamp}] 主网交易监控")
        print("=" * 60)
        
        # 基本状态
        status = "✅ 正常" if (process_running and logs_updated) else "❌ 异常"
        print(f"状态: {status}")
        print(f"运行时间: {uptime}")
        
        # 进程状态
        print(f"进程运行: {'是' if process_running else '否'}")
        print(f"日志更新: {'是' if logs_updated else '否'}")
        
        # 账户信息
        if balance is not None:
            print(f"账户余额: ${balance:.2f}")
            if self.last_balance is not None:
                change = balance - self.last_balance
                if change != 0:
                    print(f"余额变化: {change:+.2f}")
            self.last_balance = balance
        else:
            print("账户余额: 无法获取")
        
        # 错误信息
        if errors:
            print(f"最近错误 ({len(errors)} 个):")
            for error in errors:
                print(f"  - {error}")
        else:
            print("错误: 无")
        
        # 风险提示
        if balance is not None and self.last_balance is not None:
            change_pct = (balance - self.last_balance) / self.last_balance * 100
            if change_pct < -5:  # 亏损超过5%
                print("⚠️  警告: 账户亏损超过5%")
            elif change_pct > 10:  # 盈利超过10%
                print("🎉 提示: 账户盈利超过10%")
        
        print("-" * 60)
    
    async def monitor_loop(self):
        """监控循环"""
        print("📊 主网交易程序监控启动")
        print("按 Ctrl+C 停止监控")
        
        while True:
            try:
                # 检查基本状态
                process_running = self.check_process()
                logs_updated = self.check_logs()
                
                # 获取账户余额
                balance = await self.get_account_balance()
                
                # 获取错误日志
                errors = self.get_log_errors()
                
                # 打印状态
                self.print_status(process_running, logs_updated, balance, errors)
                
                # 检查异常情况
                if not process_running:
                    print("⚠️  进程未运行，请检查程序状态")
                
                if not logs_updated:
                    print("⚠️  日志未更新，程序可能卡住")
                
                if errors:
                    print("⚠️  发现错误，请检查日志")
                
                # 等待下次检查
                time.sleep(60)  # 每分钟检查一次
                
            except KeyboardInterrupt:
                print("\n⏹️  监控已停止")
                break
            except Exception as e:
                print(f"\n❌ 监控错误: {e}")
                time.sleep(10)  # 出错后等待10秒再继续
    
    async def cleanup(self):
        """清理资源"""
        if self.api_client:
            await self.api_client.close()


async def main():
    """主函数"""
    monitor = MainnetMonitor()
    
    # 加载配置
    if not monitor.load_config():
        return 1
    
    # 初始化API客户端
    if not await monitor.init_api_client():
        return 1
    
    try:
        # 开始监控
        await monitor.monitor_loop()
    finally:
        # 清理资源
        await monitor.cleanup()
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 监控已停止")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 程序错误: {e}")
        sys.exit(1)
