#!/usr/bin/env python3
"""
GUI启动脚本
启动量化交易系统的可视化界面
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 检查依赖
def check_dependencies():
    """检查必要的依赖"""
    missing_deps = []
    
    try:
        import PyQt6
    except ImportError:
        missing_deps.append("PyQt6")
        
    try:
        import matplotlib
    except ImportError:
        missing_deps.append("matplotlib")
        
    try:
        import pandas
    except ImportError:
        missing_deps.append("pandas")
        
    try:
        import numpy
    except ImportError:
        missing_deps.append("numpy")
        
    if missing_deps:
        print("❌ 缺少必要的依赖包:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\n请运行以下命令安装依赖:")
        print("pip install -r requirements.txt")
        return False
        
    return True

def main():
    """主函数"""
    print("🚀 启动Lighter量化交易系统GUI")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
        
    # 检查配置文件
    config_file = Path("config.yaml")
    if not config_file.exists():
        print("❌ 配置文件不存在: config.yaml")
        print("请先运行: python quick_setup.py")
        sys.exit(1)
        
    try:
        # 导入GUI模块
        from gui.main_window import MainWindow
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        
        # 创建应用
        app = QApplication(sys.argv)
        app.setApplicationName("Lighter量化交易系统")
        app.setApplicationVersion("1.0.0")
        
        # 设置应用样式
        app.setStyle('Fusion')
        
        # 应用深色主题
        try:
            import qdarkstyle
            app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt6())
        except ImportError:
            print("ℹ️  深色主题未安装，使用默认主题")
            print("   安装命令: pip install qdarkstyle")
        
        # 创建主窗口
        window = MainWindow()
        window.show()
        
        print("✅ GUI界面启动成功")
        print("📊 功能特性:")
        print("   - 交易对选择")
        print("   - 策略配置")
        print("   - 实时K线图")
        print("   - 持仓监控")
        print("   - 风险控制")
        print("   - 邮件通知")
        
        # 运行应用
        sys.exit(app.exec())
        
    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
        print("请确保所有依赖已正确安装")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

