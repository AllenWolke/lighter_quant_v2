#!/bin/bash
# Linux测试网环境启动脚本
# 用于启动Lighter量化交易系统的Linux测试环境

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示标题
show_header() {
    echo "========================================"
    echo "  Lighter量化交易系统 - Linux测试环境"
    echo "========================================"
    echo
}

# 检查系统要求
check_system_requirements() {
    log_info "检查系统要求..."
    
    # 检查操作系统
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        log_error "此脚本仅支持Linux系统"
        exit 1
    fi
    
    # 检查Python版本
    if ! command -v python3 &> /dev/null; then
        log_error "未找到Python3，请先安装Python 3.9+"
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [[ $(echo "$python_version < 3.9" | bc -l) -eq 1 ]]; then
        log_error "Python版本过低 ($python_version)，需要3.9+"
        exit 1
    fi
    
    log_success "系统要求检查通过"
}

# 检查虚拟环境
check_venv() {
    log_info "检查虚拟环境..."
    
    if [ ! -f "venv/bin/activate" ]; then
        log_error "未找到虚拟环境，请先创建虚拟环境"
        log_info "运行命令: python3 -m venv venv"
        exit 1
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    log_success "虚拟环境激活成功"
}

# 检查配置文件
check_config() {
    log_info "检查配置文件..."
    
    if [ ! -f "config_linux_testnet.yaml" ]; then
        log_error "未找到测试网配置文件 config_linux_testnet.yaml"
        log_info "请先复制并配置测试网配置文件"
        exit 1
    fi
    
    # 验证配置文件格式
    python3 -c "
import yaml
try:
    with open('config_linux_testnet.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    print('配置文件格式正确')
except Exception as e:
    print(f'配置文件格式错误: {e}')
    exit(1)
" || exit 1
    
    log_success "配置文件检查通过"
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖包..."
    
    # 检查关键依赖
    python3 -c "
import sys
try:
    import lighter
    import eth_account
    import pydantic
    import numpy
    import pandas
    print('关键依赖检查通过')
except ImportError as e:
    print(f'依赖缺失: {e}')
    sys.exit(1)
" || {
        log_warning "部分依赖缺失，尝试安装..."
        pip install -r requirements.txt
        if [ $? -ne 0 ]; then
            log_error "依赖安装失败"
            exit 1
        fi
    }
    
    log_success "依赖检查通过"
}

# 创建必要目录
create_directories() {
    log_info "创建必要目录..."
    
    mkdir -p logs
    mkdir -p data
    mkdir -p backups
    
    # 设置权限
    chmod 755 logs
    chmod 755 data
    chmod 755 backups
    
    log_success "目录创建完成"
}

# 检查网络连接
check_network() {
    log_info "检查网络连接..."
    
    # 检查测试网连接
    if ping -c 3 testnet.zklighter.elliot.ai > /dev/null 2>&1; then
        log_success "测试网连接正常"
    else
        log_warning "测试网连接异常，请检查网络设置"
    fi
    
    # 检查DNS解析
    if nslookup testnet.zklighter.elliot.ai > /dev/null 2>&1; then
        log_success "DNS解析正常"
    else
        log_warning "DNS解析异常"
    fi
}

# 检查系统资源
check_resources() {
    log_info "检查系统资源..."
    
    # 检查内存
    total_mem=$(free -m | awk 'NR==2{printf "%.0f", $2}')
    if [ $total_mem -lt 4096 ]; then
        log_warning "内存不足 ($total_mem MB)，推荐8GB+"
    else
        log_success "内存充足 ($total_mem MB)"
    fi
    
    # 检查磁盘空间
    disk_usage=$(df . | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ $disk_usage -gt 80 ]; then
        log_warning "磁盘空间不足 (${disk_usage}%)"
    else
        log_success "磁盘空间充足 (${disk_usage}%)"
    fi
    
    # 检查CPU负载
    load_avg=$(uptime | awk -F'load average:' '{print $2}' | awk -F',' '{print $1}' | xargs)
    log_info "当前负载: $load_avg"
}

# 测试Lighter连接
test_lighter_connection() {
    log_info "测试Lighter连接..."
    
    python3 -c "
import asyncio
import sys
sys.path.append('.')
from quant_trading.utils.config import Config
import lighter

async def test_connection():
    try:
        config = Config.from_file('config_linux_testnet.yaml')
        configuration = lighter.Configuration()
        configuration.host = config.lighter_base_url
        api_client = lighter.ApiClient(configuration)
        
        block_api = lighter.BlockApi(api_client)
        blocks = await block_api.blocks(limit=1)
        print('Lighter连接测试成功')
        await api_client.close()
        return True
    except Exception as e:
        print(f'Lighter连接测试失败: {e}')
        return False

result = asyncio.run(test_connection())
sys.exit(0 if result else 1)
" && log_success "Lighter连接测试通过" || {
        log_warning "Lighter连接测试失败"
        log_info "注意: 这是测试环境，连接失败不影响基本功能"
    }
}

# 显示启动菜单
show_menu() {
    echo "========================================"
    echo "   选择启动模式:"
    echo "========================================"
    echo "1. 启动Web系统 (前端 + 后端)"
    echo "2. 启动量化交易系统 (命令行)"
    echo "3. 启动完整系统 (Web + 交易)"
    echo "4. 启动系统服务"
    echo "5. 运行回测"
    echo "6. 系统监控"
    echo "7. 退出"
    echo "========================================"
}

# 启动Web系统
start_web() {
    log_info "启动Web系统..."
    
    # 启动后端
    log_info "启动后端服务..."
    cd web_backend
    nohup python3 main.py > ../logs/backend.log 2>&1 &
    backend_pid=$!
    echo $backend_pid > ../logs/backend.pid
    cd ..
    
    # 等待后端启动
    sleep 5
    
    # 检查后端状态
    if ps -p $backend_pid > /dev/null; then
        log_success "后端服务启动成功 (PID: $backend_pid)"
    else
        log_error "后端服务启动失败"
        return 1
    fi
    
    # 启动前端
    log_info "启动前端服务..."
    cd web_frontend
    nohup npm start > ../logs/frontend.log 2>&1 &
    frontend_pid=$!
    echo $frontend_pid > ../logs/frontend.pid
    cd ..
    
    # 等待前端启动
    sleep 10
    
    # 检查前端状态
    if ps -p $frontend_pid > /dev/null; then
        log_success "前端服务启动成功 (PID: $frontend_pid)"
    else
        log_warning "前端服务可能启动失败，请检查日志"
    fi
    
    echo
    log_success "Web系统启动完成！"
    echo "后端地址: http://localhost:8000"
    echo "前端地址: http://localhost:3000"
    echo
}

# 启动交易系统
start_trading() {
    log_info "启动量化交易系统..."
    
    log_info "注意: 这是测试环境，将使用模拟交易模式"
    
    # 启动交易系统
    nohup python3 main.py --config config_linux_testnet.yaml > logs/trading.log 2>&1 &
    trading_pid=$!
    echo $trading_pid > logs/trading.pid
    
    sleep 3
    
    if ps -p $trading_pid > /dev/null; then
        log_success "交易系统启动成功 (PID: $trading_pid)"
        echo "日志文件: logs/trading.log"
        echo "注意: 测试环境使用模拟交易，不会进行实际交易"
    else
        log_error "交易系统启动失败"
        return 1
    fi
}

# 启动完整系统
start_full() {
    log_info "启动完整系统..."
    
    start_web
    sleep 5
    start_trading
    
    echo
    log_success "完整系统启动完成！"
}

# 启动系统服务
start_service() {
    log_info "启动系统服务..."
    
    if systemctl is-active --quiet lighter-trading-test; then
        log_warning "服务已在运行"
        systemctl status lighter-trading-test
    else
        sudo systemctl start lighter-trading-test
        if [ $? -eq 0 ]; then
            log_success "系统服务启动成功"
            systemctl status lighter-trading-test
        else
            log_error "系统服务启动失败"
        fi
    fi
}

# 运行回测
run_backtest() {
    echo
    echo "可用的回测选项:"
    echo "1. 动量策略回测"
    echo "2. 均值回归策略回测"
    echo "3. 自定义回测"
    echo
    read -p "请选择回测类型 (1-3): " backtest_choice
    
    case $backtest_choice in
        1)
            log_info "运行动量策略回测..."
            python3 run_backtest.py --strategy momentum --start-date 2024-01-01 --end-date 2024-01-31 --config config_linux_testnet.yaml
            ;;
        2)
            log_info "运行均值回归策略回测..."
            python3 run_backtest.py --strategy mean_reversion --start-date 2024-01-01 --end-date 2024-01-31 --config config_linux_testnet.yaml
            ;;
        3)
            read -p "请输入策略名称: " strategy_name
            read -p "请输入开始日期 (YYYY-MM-DD): " start_date
            read -p "请输入结束日期 (YYYY-MM-DD): " end_date
            log_info "运行自定义回测: $strategy_name"
            python3 run_backtest.py --strategy $strategy_name --start-date $start_date --end-date $end_date --config config_linux_testnet.yaml
            ;;
        *)
            log_error "无效选择"
            ;;
    esac
}

# 系统监控
system_monitor() {
    log_info "启动系统监控..."
    
    if [ -f "monitor_mainnet.py" ]; then
        python3 monitor_mainnet.py
    else
        log_warning "监控脚本不存在，显示基本系统信息"
        
        echo "========================================"
        echo "   系统状态"
        echo "========================================"
        
        # 进程状态
        echo "进程状态:"
        if [ -f "logs/trading.pid" ]; then
            trading_pid=$(cat logs/trading.pid)
            if ps -p $trading_pid > /dev/null; then
                echo "  交易系统: 运行中 (PID: $trading_pid)"
            else
                echo "  交易系统: 已停止"
            fi
        else
            echo "  交易系统: 未启动"
        fi
        
        if [ -f "logs/backend.pid" ]; then
            backend_pid=$(cat logs/backend.pid)
            if ps -p $backend_pid > /dev/null; then
                echo "  后端服务: 运行中 (PID: $backend_pid)"
            else
                echo "  后端服务: 已停止"
            fi
        else
            echo "  后端服务: 未启动"
        fi
        
        # 系统资源
        echo
        echo "系统资源:"
        echo "  内存使用: $(free -m | awk 'NR==2{printf "%.1f%%", $3*100/$2}')"
        echo "  磁盘使用: $(df -h . | tail -1 | awk '{print $5}')"
        echo "  CPU负载: $(uptime | awk -F'load average:' '{print $2}')"
        
        # 网络状态
        echo
        echo "网络状态:"
        if ping -c 1 testnet.zklighter.elliot.ai > /dev/null 2>&1; then
            echo "  Lighter连接: 正常"
        else
            echo "  Lighter连接: 异常"
        fi
        
        # 配置文件状态
        echo
        echo "配置文件状态:"
        if [ -f "config_linux_testnet.yaml" ]; then
            echo "  配置文件: 存在"
            echo "  配置类型: Linux测试网"
        else
            echo "  配置文件: 不存在"
        fi
    fi
}

# 主函数
main() {
    show_header
    
    # 执行所有检查
    check_system_requirements
    check_venv
    check_config
    check_dependencies
    create_directories
    check_network
    check_resources
    test_lighter_connection
    
    echo
    log_success "所有检查完成，系统准备就绪！"
    echo
    log_info "注意: 这是测试环境，主要用于策略开发和功能测试"
    echo
    
    # 显示菜单并处理用户选择
    while true; do
        show_menu
        read -p "请输入选择 (1-7): " choice
        
        case $choice in
            1) start_web ;;
            2) start_trading ;;
            3) start_full ;;
            4) start_service ;;
            5) run_backtest ;;
            6) system_monitor ;;
            7) 
                log_info "退出系统"
                break
                ;;
            *)
                log_error "无效选择，请重新输入"
                ;;
        esac
        
        echo
        read -p "按回车键继续..."
        echo
    done
}

# 清理函数
cleanup() {
    log_info "清理资源..."
    # 可以在这里添加清理逻辑
}

# 设置信号处理
trap cleanup EXIT

# 运行主函数
main "$@"
