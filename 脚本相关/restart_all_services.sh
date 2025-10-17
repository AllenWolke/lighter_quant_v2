#!/bin/bash

###############################################################################
# Lighter量化交易系统 - 完整重启脚本
# 包含：停止服务、清理进程、检查依赖、启动服务
###############################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
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

log_step() {
    echo -e "${MAGENTA}▶${NC} ${CYAN}$1${NC}"
}

# 打印横幅
print_banner() {
    echo ""
    echo "===================================================="
    echo "  Lighter 量化交易系统 - 完整重启"
    echo "===================================================="
    echo ""
}

# 步骤1: 停止所有服务
stop_services() {
    log_step "步骤1: 停止所有服务"
    echo ""
    
    if [ -f "stop_all_services.sh" ]; then
        ./stop_all_services.sh
    else
        log_warning "未找到 stop_all_services.sh，手动停止进程..."
        
        # 手动停止进程
        if [ -f "logs/backend.pid" ]; then
            backend_pid=$(cat logs/backend.pid)
            if ps -p $backend_pid > /dev/null 2>&1; then
                kill $backend_pid 2>/dev/null || true
                sleep 1
                kill -9 $backend_pid 2>/dev/null || true
            fi
            rm -f logs/backend.pid
        fi
        
        if [ -f "logs/frontend.pid" ]; then
            frontend_pid=$(cat logs/frontend.pid)
            if ps -p $frontend_pid > /dev/null 2>&1; then
                kill $frontend_pid 2>/dev/null || true
                sleep 1
                kill -9 $frontend_pid 2>/dev/null || true
            fi
            rm -f logs/frontend.pid
        fi
        
        if [ -f "logs/trading.pid" ]; then
            trading_pid=$(cat logs/trading.pid)
            if ps -p $trading_pid > /dev/null 2>&1; then
                kill $trading_pid 2>/dev/null || true
                sleep 1
                kill -9 $trading_pid 2>/dev/null || true
            fi
            rm -f logs/trading.pid
        fi
    fi
    
    log_success "服务已停止"
    echo ""
}

# 步骤2: 等待并清理
wait_and_clean() {
    log_step "步骤2: 等待并清理残留进程"
    echo ""
    
    log_info "等待5秒..."
    sleep 5
    
    log_info "清理残留进程..."
    pkill -f "python.*main.py" 2>/dev/null || true
    pkill -f "npm start" 2>/dev/null || true
    pkill -f "node.*react" 2>/dev/null || true
    
    log_success "清理完成"
    echo ""
}

# 步骤3: 检查端口占用
check_ports() {
    log_step "步骤3: 检查端口占用"
    echo ""
    
    # 检查端口 3000
    if lsof -i :3000 > /dev/null 2>&1; then
        log_warning "端口 3000 被占用，尝试释放..."
        fuser -k 3000/tcp 2>/dev/null || true
        sleep 1
    else
        log_success "端口 3000 可用"
    fi
    
    # 检查端口 8000
    if lsof -i :8000 > /dev/null 2>&1; then
        log_warning "端口 8000 被占用，尝试释放..."
        fuser -k 8000/tcp 2>/dev/null || true
        sleep 1
    else
        log_success "端口 8000 可用"
    fi
    
    echo ""
}

# 步骤4: 检查并安装依赖
check_dependencies() {
    log_step "步骤4: 检查并安装依赖"
    echo ""
    
    # 检查虚拟环境
    if [ ! -d "venv" ]; then
        log_error "虚拟环境不存在！"
        log_info "创建虚拟环境..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 检查 pydantic-settings
    log_info "检查 pydantic-settings..."
    if python3 -c "import pydantic_settings" 2>/dev/null; then
        log_success "pydantic-settings 已安装"
    else
        log_warning "pydantic-settings 未安装，正在安装..."
        pip install pydantic-settings>=2.1.0 -q
        log_success "pydantic-settings 安装完成"
    fi
    
    # 检查其他 Web 后端依赖
    log_info "检查 Web 后端依赖..."
    if [ -f "web_backend/requirements.txt" ]; then
        missing_packages=0
        
        # 检查关键包
        for package in fastapi uvicorn sqlalchemy pydantic-settings; do
            if ! pip show $package > /dev/null 2>&1; then
                missing_packages=$((missing_packages + 1))
            fi
        done
        
        if [ $missing_packages -gt 0 ]; then
            log_warning "发现 $missing_packages 个缺失的包，正在安装..."
            pip install -r web_backend/requirements.txt -q
            log_success "依赖安装完成"
        else
            log_success "所有依赖已安装"
        fi
    fi
    
    # 退出虚拟环境
    deactivate
    
    echo ""
}

# 步骤5: 启动所有服务
start_services() {
    log_step "步骤5: 启动所有服务"
    echo ""
    
    if [ -f "start_all_services.sh" ]; then
        ./start_all_services.sh
    else
        log_error "未找到 start_all_services.sh！"
        log_info "请手动启动服务"
        exit 1
    fi
}

# 步骤6: 验证服务
verify_services() {
    log_step "步骤6: 验证服务状态"
    echo ""
    
    log_info "等待10秒让服务完全启动..."
    sleep 10
    
    # 检查后端
    if curl -s http://localhost:8000/health > /dev/null 2>&1 || \
       curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1 || \
       lsof -i :8000 > /dev/null 2>&1; then
        log_success "✓ 后端服务运行正常 (端口: 8000)"
    else
        log_warning "⚠ 后端服务可能未正常启动，请检查日志"
    fi
    
    # 检查前端
    if curl -s http://localhost:3000 > /dev/null 2>&1 || \
       lsof -i :3000 > /dev/null 2>&1; then
        log_success "✓ 前端服务运行正常 (端口: 3000)"
    else
        log_warning "⚠ 前端服务可能未正常启动，请检查日志"
    fi
    
    echo ""
}

# 显示访问信息
show_info() {
    echo ""
    echo "===================================================="
    echo -e "${GREEN}🎉 重启完成！${NC}"
    echo "===================================================="
    echo ""
    echo -e "${CYAN}📊 服务信息:${NC}"
    echo "  - Web前端: http://localhost:3000"
    echo "  - Web后端: http://localhost:8000"
    echo "  - API文档: http://localhost:8000/docs"
    echo ""
    echo -e "${CYAN}🔐 默认登录:${NC}"
    echo "  - 用户名: admin"
    echo "  - 密码: admin123"
    echo -e "  ${YELLOW}⚠️  首次登录后请立即修改密码！${NC}"
    echo ""
    echo -e "${CYAN}📝 日志文件:${NC}"
    echo "  - 后端: logs/backend.log"
    echo "  - 前端: logs/frontend.log"
    echo ""
    echo -e "${CYAN}🔍 查看日志:${NC}"
    echo "  tail -f logs/backend.log"
    echo "  tail -f logs/frontend.log"
    echo ""
    echo -e "${CYAN}🛑 停止服务:${NC}"
    echo "  ./stop_all_services.sh"
    echo "===================================================="
    echo ""
}

# 错误处理
handle_error() {
    echo ""
    log_error "重启过程中发生错误！"
    echo ""
    echo "===================================================="
    echo "🆘 故障排除建议:"
    echo "===================================================="
    echo "1. 查看日志:"
    echo "   tail -n 50 logs/backend.log"
    echo "   tail -n 50 logs/frontend.log"
    echo ""
    echo "2. 手动停止所有进程:"
    echo "   pkill -9 -f 'python.*main.py'"
    echo "   pkill -9 -f 'npm start'"
    echo ""
    echo "3. 检查端口占用:"
    echo "   lsof -i :3000"
    echo "   lsof -i :8000"
    echo ""
    echo "4. 重新安装依赖:"
    echo "   source venv/bin/activate"
    echo "   pip install -r web_backend/requirements.txt"
    echo "   deactivate"
    echo ""
    echo "5. 再次尝试重启:"
    echo "   ./restart_all_services.sh"
    echo "===================================================="
    exit 1
}

# 设置错误陷阱
trap handle_error ERR

# 主函数
main() {
    # 检查是否在项目根目录
    if [ ! -f "start_all_services.sh" ] && [ ! -f "stop_all_services.sh" ]; then
        log_error "请在项目根目录执行此脚本！"
        exit 1
    fi
    
    print_banner
    
    # 执行重启流程
    stop_services
    wait_and_clean
    check_ports
    check_dependencies
    start_services
    verify_services
    show_info
}

# 运行主函数
main

