#!/bin/bash

###############################################################################
# 安装 Web 后端依赖脚本
# 解决 ModuleNotFoundError 问题
###############################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# 打印横幅
print_banner() {
    echo ""
    echo "===================================================="
    echo "  安装 Web 后端依赖"
    echo "===================================================="
    echo ""
}

# 检查虚拟环境
check_venv() {
    log_info "检查虚拟环境..."
    
    if [ ! -d "venv" ]; then
        log_warning "虚拟环境不存在，正在创建..."
        python3 -m venv venv
        log_success "虚拟环境创建完成"
    else
        log_success "虚拟环境已存在"
    fi
}

# 激活虚拟环境
activate_venv() {
    log_info "激活虚拟环境..."
    
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        log_success "虚拟环境已激活"
    else
        log_error "无法找到虚拟环境激活脚本"
        exit 1
    fi
}

# 升级 pip
upgrade_pip() {
    log_info "升级 pip..."
    python3 -m pip install --upgrade pip -q
    log_success "pip 已升级"
}

# 安装核心依赖
install_core_deps() {
    log_info "安装核心依赖（可能需要几分钟）..."
    
    echo ""
    echo "${CYAN}正在安装:${NC}"
    echo "  - fastapi"
    echo "  - uvicorn"
    echo "  - pydantic (含 email 支持)"
    echo "  - pydantic-settings"
    echo "  - email-validator"
    echo "  - sqlalchemy"
    echo "  - passlib"
    echo "  - python-jose"
    echo "  - python-multipart"
    echo ""
    
    pip install fastapi>=0.104.0 \
                uvicorn[standard]>=0.24.0 \
                pydantic[email]>=2.5.0 \
                pydantic-settings>=2.1.0 \
                email-validator>=2.0.0 \
                sqlalchemy>=2.0.0 \
                passlib[bcrypt]>=1.7.4 \
                python-jose[cryptography]>=3.3.0 \
                python-multipart>=0.0.6 \
                -q
    
    log_success "核心依赖安装完成"
}

# 安装完整 Web 后端依赖
install_full_deps() {
    log_info "安装完整 Web 后端依赖..."
    
    if [ -f "web_backend/requirements.txt" ]; then
        pip install -r web_backend/requirements.txt -q
        log_success "完整依赖安装完成"
    else
        log_warning "未找到 web_backend/requirements.txt"
        log_info "仅安装核心依赖"
    fi
}

# 验证安装
verify_installation() {
    log_info "验证安装..."
    echo ""
    
    # 检查关键包
    packages=("fastapi" "uvicorn" "pydantic" "pydantic_settings" "sqlalchemy" "passlib")
    all_installed=true
    
    for package in "${packages[@]}"; do
        if python3 -c "import $package" 2>/dev/null; then
            echo -e "${GREEN}✓${NC} $package"
        else
            echo -e "${RED}✗${NC} $package"
            all_installed=false
        fi
    done
    
    echo ""
    
    if [ "$all_installed" = true ]; then
        log_success "所有依赖验证通过"
        return 0
    else
        log_error "部分依赖验证失败"
        return 1
    fi
}

# 显示已安装的包
show_installed() {
    log_info "已安装的关键包:"
    echo ""
    
    pip list | grep -E "fastapi|uvicorn|pydantic|sqlalchemy|passlib|jose|aiohttp|websockets" || true
    
    echo ""
}

# 退出虚拟环境
deactivate_venv() {
    log_info "退出虚拟环境..."
    deactivate
    log_success "已退出虚拟环境"
}

# 显示下一步
show_next_steps() {
    echo ""
    echo "===================================================="
    echo -e "${GREEN}✅ 依赖安装完成！${NC}"
    echo "===================================================="
    echo ""
    echo -e "${CYAN}📝 下一步:${NC}"
    echo "1. 启动所有服务:"
    echo "   ./start_all_services.sh"
    echo ""
    echo "2. 或使用一键重启:"
    echo "   ./restart_all_services.sh"
    echo ""
    echo "3. 查看日志:"
    echo "   tail -f logs/backend.log"
    echo "===================================================="
    echo ""
}

# 错误处理
handle_error() {
    echo ""
    log_error "安装过程中发生错误！"
    echo ""
    echo "===================================================="
    echo "🆘 故障排除建议:"
    echo "===================================================="
    echo "1. 检查网络连接"
    echo "2. 检查磁盘空间: df -h"
    echo "3. 检查 Python 版本: python3 --version"
    echo "4. 手动安装:"
    echo "   source venv/bin/activate"
    echo "   pip install fastapi uvicorn pydantic pydantic-settings"
    echo "   deactivate"
    echo "5. 重新创建虚拟环境:"
    echo "   rm -rf venv"
    echo "   python3 -m venv venv"
    echo "   ./install_web_backend_deps.sh"
    echo "===================================================="
    exit 1
}

# 设置错误陷阱
trap handle_error ERR

# 主函数
main() {
    # 检查是否在项目根目录
    if [ ! -f "web_backend/requirements.txt" ] && [ ! -d "web_backend" ]; then
        log_error "请在项目根目录执行此脚本！"
        exit 1
    fi
    
    print_banner
    
    # 执行安装流程
    check_venv
    activate_venv
    upgrade_pip
    install_core_deps
    install_full_deps
    
    echo ""
    verify_installation
    show_installed
    deactivate_venv
    show_next_steps
}

# 运行主函数
main

