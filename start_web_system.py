#!/usr/bin/env python3
"""
Web系统启动脚本
一键启动React前端和FastAPI后端
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

class WebSystemStarter:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.running = False
        
    def start_backend(self):
        """启动FastAPI后端"""
        print("🚀 启动FastAPI后端...")
        
        backend_dir = Path("web_backend")
        if not backend_dir.exists():
            print("❌ 后端目录不存在，请先创建后端项目")
            return False
            
        try:
            # 安装依赖
            print("📦 安装后端依赖...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", 
                str(backend_dir / "requirements.txt")
            ], check=True)
            
            # 启动后端
            self.backend_process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", 
                "main:app", 
                "--host", "0.0.0.0", 
                "--port", "8000",
                "--reload"
            ], cwd=backend_dir)
            
            print("✅ 后端启动成功: http://localhost:8000")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 后端启动失败: {e}")
            return False
        except Exception as e:
            print(f"❌ 后端启动异常: {e}")
            return False
    
    def start_frontend(self):
        """启动React前端"""
        print("🚀 启动React前端...")
        
        frontend_dir = Path("web_frontend")
        if not frontend_dir.exists():
            print("❌ 前端目录不存在，请先创建前端项目")
            return False
            
        try:
            # 检查node_modules
            if not (frontend_dir / "node_modules").exists():
                print("📦 安装前端依赖...")
                subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
            
            # 启动前端
            self.frontend_process = subprocess.Popen([
                "npm", "start"
            ], cwd=frontend_dir)
            
            print("✅ 前端启动成功: http://localhost:3000")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 前端启动失败: {e}")
            return False
        except Exception as e:
            print(f"❌ 前端启动异常: {e}")
            return False
    
    def wait_for_services(self):
        """等待服务启动"""
        print("⏳ 等待服务启动...")
        
        # 等待后端启动
        backend_ready = False
        for i in range(30):  # 等待30秒
            try:
                import requests
                response = requests.get("http://localhost:8000/api/health", timeout=1)
                if response.status_code == 200:
                    backend_ready = True
                    break
            except:
                pass
            time.sleep(1)
        
        if not backend_ready:
            print("❌ 后端服务启动超时")
            return False
        
        # 等待前端启动
        frontend_ready = False
        for i in range(60):  # 等待60秒
            try:
                import requests
                response = requests.get("http://localhost:3000", timeout=1)
                if response.status_code == 200:
                    frontend_ready = True
                    break
            except:
                pass
            time.sleep(1)
        
        if not frontend_ready:
            print("❌ 前端服务启动超时")
            return False
        
        print("✅ 所有服务启动完成")
        return True
    
    def signal_handler(self, signum, frame):
        """信号处理器"""
        print("\n🛑 收到停止信号，正在关闭服务...")
        self.stop()
        sys.exit(0)
    
    def stop(self):
        """停止所有服务"""
        self.running = False
        
        if self.backend_process:
            print("🛑 停止后端服务...")
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
        
        if self.frontend_process:
            print("🛑 停止前端服务...")
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
        
        print("✅ 所有服务已停止")
    
    def run(self):
        """运行Web系统"""
        print("🌟 启动Lighter量化交易Web系统")
        print("=" * 50)
        
        # 注册信号处理器
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            # 启动后端
            if not self.start_backend():
                return False
            
            # 等待后端启动
            time.sleep(3)
            
            # 启动前端
            if not self.start_frontend():
                self.stop()
                return False
            
            # 等待服务启动
            if not self.wait_for_services():
                self.stop()
                return False
            
            print("\n🎉 Web系统启动成功！")
            print("📱 前端地址: http://localhost:3000")
            print("🔧 后端地址: http://localhost:8000")
            print("📚 API文档: http://localhost:8000/api/docs")
            print("\n按 Ctrl+C 停止服务")
            
            self.running = True
            
            # 保持运行
            while self.running:
                time.sleep(1)
                
                # 检查进程状态
                if self.backend_process and self.backend_process.poll() is not None:
                    print("❌ 后端进程意外退出")
                    break
                
                if self.frontend_process and self.frontend_process.poll() is not None:
                    print("❌ 前端进程意外退出")
                    break
            
        except KeyboardInterrupt:
            print("\n🛑 用户中断")
        except Exception as e:
            print(f"❌ 系统错误: {e}")
        finally:
            self.stop()
        
        return True


def main():
    """主函数"""
    starter = WebSystemStarter()
    success = starter.run()
    
    if success:
        print("✅ Web系统运行完成")
    else:
        print("❌ Web系统启动失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
