#!/bin/bash

###############################################################################
# 创建默认管理员用户脚本
# 用户名: admin
# 密码: admin123
###############################################################################

set -e

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

# 打印横幅
print_banner() {
    echo ""
    echo "=================================================="
    echo "  Lighter 量化交易系统 - 创建默认用户"
    echo "=================================================="
    echo ""
}

# 检查 Python
check_python() {
    log_info "检查 Python 环境..."
    
    # 优先使用虚拟环境的 Python
    if [ -f "venv/bin/python" ]; then
        PYTHON_CMD="venv/bin/python"
        log_success "使用虚拟环境 Python: $PYTHON_CMD"
        return 0
    fi
    
    # 检查 python3
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        log_success "使用系统 Python3: $PYTHON_CMD"
        return 0
    fi
    
    # 检查 python
    if command -v python &> /dev/null; then
        PYTHON_CMD="python"
        log_success "使用系统 Python: $PYTHON_CMD"
        return 0
    fi
    
    log_error "未找到 Python 命令！"
    log_error "请安装 Python 3.9+ 或激活虚拟环境"
    exit 1
}

# 检查目录
check_directory() {
    log_info "检查项目目录..."
    
    if [ ! -f "web_backend/init_default_user.py" ]; then
        log_error "未找到 web_backend/init_default_user.py"
        log_error "请确保在项目根目录执行此脚本"
        exit 1
    fi
    
    log_success "项目目录检查通过"
}

# 创建必要目录
create_directories() {
    log_info "创建必要目录..."
    mkdir -p data logs backups
    log_success "目录创建完成"
}

# 创建默认用户
create_user() {
    log_info "创建默认管理员用户..."
    
    cd web_backend
    
    # 运行创建用户脚本
    if $PYTHON_CMD init_default_user.py; then
        cd ..
        log_success "用户创建成功！"
        return 0
    else
        cd ..
        exit_code=$?
        if [ $exit_code -eq 0 ]; then
            log_warning "用户可能已存在"
            return 0
        else
            log_error "用户创建失败（退出码: $exit_code）"
            return 1
        fi
    fi
}

# 显示登录信息
show_credentials() {
    echo ""
    echo "=================================================="
    echo -e "${GREEN}✓ 默认管理员用户信息${NC}"
    echo "=================================================="
    echo -e "用户名: ${YELLOW}admin${NC}"
    echo -e "密码:   ${YELLOW}admin123${NC}"
    echo -e "邮箱:   ${YELLOW}admin@lighter-quant.local${NC}"
    echo "=================================================="
    echo ""
    echo -e "${YELLOW}⚠️  首次登录后请立即修改密码！${NC}"
    echo ""
}

# 显示下一步
show_next_steps() {
    echo "=================================================="
    echo "🌐 下一步操作"
    echo "=================================================="
    echo "1. 启动所有服务:"
    echo "   ./start_all_services.sh"
    echo ""
    echo "2. 访问 Web 界面:"
    echo "   http://localhost:3000"
    echo ""
    echo "3. 使用以下凭据登录:"
    echo "   用户名: admin"
    echo "   密码:   admin123"
    echo "=================================================="
    echo ""
}

# 主函数
main() {
    print_banner
    
    # 检查环境
    check_python
    check_directory
    
    # 创建目录
    create_directories
    
    # 创建用户
    if create_user; then
        show_credentials
        show_next_steps
        exit 0
    else
        log_error "创建用户失败！"
        echo ""
        echo "=================================================="
        echo "🆘 故障排除"
        echo "=================================================="
        echo "1. 检查 Python 版本:"
        echo "   $PYTHON_CMD --version"
        echo ""
        echo "2. 检查依赖安装:"
        echo "   $PYTHON_CMD -m pip list | grep SQLAlchemy"
        echo ""
        echo "3. 查看详细日志:"
        echo "   cd web_backend"
        echo "   $PYTHON_CMD init_default_user.py"
        echo ""
        echo "4. 重新安装依赖:"
        echo "   $PYTHON_CMD -m pip install -r requirements.txt"
        echo "=================================================="
        exit 1
    fi
}

# 运行主函数
main

