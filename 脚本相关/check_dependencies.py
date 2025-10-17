#!/usr/bin/env python3
"""
依赖检查工具
检查Lighter量化交易系统所需的依赖是否正确安装
"""

def check_core_dependencies():
    """检查核心依赖"""
    print("检查核心依赖...")
    
    import sys
    
    dependencies = {
        'lighter': 'Lighter交易所SDK',
        'eth_account': '以太坊账户管理',
        'pydantic': '数据验证',
        'aiohttp': '异步HTTP客户端',
        'websockets': 'WebSocket支持',
        'numpy': '数值计算',
        'pandas': '数据处理',
        'scipy': '科学计算',
        'yaml': 'YAML配置解析',
        'colorlog': '彩色日志',
        'requests': 'HTTP请求'
    }
    
    # Python 3.11+ 需要的最低版本
    py311_requirements = {
        'numpy': '1.23.0',
        'pandas': '1.5.0',
        'scipy': '1.9.0'
    }
    
    missing = []
    installed = []
    warnings = []
    
    for module, desc in dependencies.items():
        try:
            mod = __import__(module)
            version_str = getattr(mod, '__version__', 'unknown')
            installed.append(f"OK {module:15} {version_str:10} - {desc}")
            
            # 检查Python 3.11+版本兼容性
            if sys.version_info >= (3, 11) and module in py311_requirements:
                if version_str != 'unknown':
                    try:
                        from packaging import version
                        current_ver = version.parse(version_str)
                        required_ver = version.parse(py311_requirements[module])
                        if current_ver < required_ver:
                            warnings.append(
                                f"WARNING {module} 版本 {version_str} 可能不兼容Python 3.11+，"
                                f"建议 >={py311_requirements[module]}"
                            )
                    except:
                        # packaging模块未安装，跳过版本比较
                        pass
        except ImportError as e:
            missing.append(f"ERROR {module:15} - {desc} ({str(e)})")
    
    for dep in installed:
        print(dep)
    
    if warnings:
        print("\n版本兼容性警告:")
        for warning in warnings:
            print(warning)
    
    if missing:
        print("\n缺失的核心依赖:")
        for dep in missing:
            print(dep)
        return False
    
    print("\nOK 所有核心依赖已安装")
    return True

def check_optional_dependencies():
    """检查可选依赖"""
    print("\n检查可选依赖...")
    
    optional = {
        'PyQt6': 'Qt GUI框架',
        'matplotlib': '数据可视化',
        'plotly': '交互式图表',
        'talib': '技术指标库',
        'tradingview_ta': 'TradingView数据',
        'pytest': '测试框架',
        'black': '代码格式化',
        'flake8': '代码检查'
    }
    
    installed_count = 0
    for module, desc in optional.items():
        try:
            mod = __import__(module)
            version = getattr(mod, '__version__', 'unknown')
            print(f"OK {module:20} {version:10} - {desc}")
            installed_count += 1
        except ImportError:
            print(f"SKIP {module:20} {'':10} - {desc} (未安装，可选)")
    
    if installed_count > 0:
        print(f"\n已安装 {installed_count}/{len(optional)} 个可选依赖")

def check_system_dependencies():
    """检查系统依赖"""
    print("\n检查系统环境...")
    
    import sys
    import platform
    
    print(f"Python版本: {sys.version}")
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"架构: {platform.machine()}")
    
    # 检查Python版本
    py_version = sys.version_info
    if py_version < (3, 9):
        print("WARNING Python版本过低，需要3.9+")
        return False
    elif py_version >= (3, 11):
        print("OK Python版本符合要求 (3.11+ 需要更新的依赖版本)")
        print("   - numpy>=1.23.0, pandas>=1.5.0, scipy>=1.9.0")
    else:
        print("OK Python版本符合要求")
    
    return True

def check_project_files():
    """检查项目文件"""
    print("\n检查项目文件...")
    
    import os
    
    required_files = [
        'requirements.txt',
        'requirements-minimal.txt',
        'config.yaml',
        'main.py'
    ]
    
    optional_files = [
        'config_linux_testnet.yaml',
        'config_linux_mainnet.yaml',
        'config_windows_testnet.yaml'
    ]
    
    all_good = True
    for file in required_files:
        if os.path.exists(file):
            print(f"OK {file}")
        else:
            print(f"ERROR {file} - 文件不存在")
            all_good = False
    
    print("\n可选配置文件:")
    for file in optional_files:
        if os.path.exists(file):
            print(f"OK {file}")
        else:
            print(f"SKIP {file} - 文件不存在")
    
    return all_good

def test_lighter_import():
    """测试Lighter导入"""
    print("\n测试Lighter SDK...")
    
    try:
        import lighter
        print(f"OK lighter版本: {lighter.__version__ if hasattr(lighter, '__version__') else '未知'}")
        
        # 尝试导入关键类
        from lighter.signer_client import SignerClient
        print("OK SignerClient导入成功")
        
        from lighter.api.order_api import OrderApi
        print("OK OrderApi导入成功")
        
        return True
    except Exception as e:
        print(f"ERROR Lighter SDK导入失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 70)
    print("Lighter量化交易系统 - 依赖检查工具")
    print("=" * 70)
    print()
    
    results = []
    
    # 检查系统环境
    results.append(("系统环境", check_system_dependencies()))
    
    # 检查核心依赖
    results.append(("核心依赖", check_core_dependencies()))
    
    # 检查可选依赖
    check_optional_dependencies()
    
    # 测试Lighter
    results.append(("Lighter SDK", test_lighter_import()))
    
    # 检查项目文件
    results.append(("项目文件", check_project_files()))
    
    # 总结
    print("\n" + "=" * 70)
    print("检查结果总结")
    print("=" * 70)
    
    all_passed = True
    for name, passed in results:
        status = "OK" if passed else "ERROR"
        print(f"{status:10} {name}")
        if not passed:
            all_passed = False
    
    print("=" * 70)
    
    if all_passed:
        print("\nOK 所有检查通过！系统可以正常运行。")
        print("\n下一步:")
        print("1. 配置 config.yaml 文件")
        print("2. 运行 python quick_start.py 启动系统")
    else:
        print("\nERROR 部分检查未通过，请解决上述问题。")
        print("\n建议:")
        print("1. 安装缺失的核心依赖: pip install -r requirements-minimal.txt")
        print("2. 检查Python版本是否>=3.9")
        print("3. 确保在项目根目录下运行此脚本")
    
    return all_passed

if __name__ == "__main__":
    import sys
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n检查已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR 检查过程出错: {e}")
        sys.exit(1)
