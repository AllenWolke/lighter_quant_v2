#!/bin/bash
# WSL Ubuntu 量化交易系统启动脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# 日志函数
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP $1]${NC} $2"; }

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    Lighter 量化交易系统 - WSL Ubuntu 启动脚本             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 检测 Python 命令
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    log_error "未找到 Python，请先安装 Python 3.9+"
    exit 1
fi

log_info "使用 Python 命令: $PYTHON_CMD"
$PYTHON_CMD --version
echo ""

# ============================================================================
# 步骤 1: 环境检查
# ============================================================================
log_step "1/7" "环境检查"
echo ""

# 检查必要的命令
REQUIRED_COMMANDS=("curl" "node" "npm")
MISSING_COMMANDS=()

for cmd in "${REQUIRED_COMMANDS[@]}"; do
    if ! command -v $cmd &> /dev/null; then
        MISSING_COMMANDS+=($cmd)
        log_warning "$cmd 未安装"
    else
        log_info "✓ $cmd 已安装"
    fi
done

if [ ${#MISSING_COMMANDS[@]} -gt 0 ]; then
    log_warning "缺少以下命令: ${MISSING_COMMANDS[*]}"
    echo ""
    read -p "是否自动安装缺少的包? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "安装缺少的包..."
        sudo apt-get update
        for cmd in "${MISSING_COMMANDS[@]}"; do
            case $cmd in
                node|npm)
                    if ! command -v node &> /dev/null; then
                        sudo apt-get install -y nodejs npm
                    fi
                    ;;
                *)
                    sudo apt-get install -y $cmd
                    ;;
            esac
        done
        log_success "依赖安装完成"
    fi
fi

echo ""

# ============================================================================
# 步骤 2: 创建必要目录
# ============================================================================
log_step "2/7" "创建必要目录"
echo ""

mkdir -p logs data backups

log_success "目录创建完成"
echo ""

# ============================================================================
# 步骤 3: 检查配置文件
# ============================================================================
log_step "3/7" "检查配置文件"
echo ""

if [ ! -f "config.yaml" ]; then
    log_warning "配置文件不存在"
    log_info "请先配置 config.yaml"
    echo ""
    echo "示例配置:"
    echo "  lighter:"
    echo "    base_url: \"https://mainnet.zklighter.elliot.ai\""
    echo "    api_key_private_key: \"0x您的私钥\""
    echo "    account_index: 0"
    echo ""
    read -p "是否继续使用默认配置? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "退出脚本，请先配置 config.yaml"
        exit 0
    fi
else
    log_success "配置文件已存在"
fi

echo ""

# ============================================================================
# 步骤 4: 停止现有服务
# ============================================================================
log_step "4/7" "停止现有服务"
echo ""

# 停止后端
log_info "停止 Web 后端..."
pkill -f "uvicorn.*main:app" 2>/dev/null || true
pkill -f "python.*web_backend" 2>/dev/null || true

# 停止前端
log_info "停止 Web 前端..."
pkill -f "node.*react-scripts" 2>/dev/null || true
pkill -f "npm.*start" 2>/dev/null || true

# 停止量化交易程序
log_info "停止量化交易程序..."
pkill -f "python.*main.py.*config" 2>/dev/null || true

sleep 2

log_success "现有服务已停止"
echo ""

# ============================================================================
# 步骤 5: 启动 Web 后端
# ============================================================================
log_step "5/7" "启动 Web 后端"
echo ""

cd web_backend

# 检查依赖
log_info "检查 Python 依赖..."
if ! $PYTHON_CMD -c "import fastapi, uvicorn" 2>/dev/null; then
    log_warning "缺少后端依赖，正在安装..."
    $PYTHON_CMD -m pip install -q fastapi uvicorn[standard] pydantic pydantic-settings sqlalchemy aiosqlite
fi

# 初始化默认用户
if [ -f "init_default_user.py" ]; then
    log_info "初始化默认用户..."
    export AUTO_SKIP_PROMPT=1
    $PYTHON_CMD init_default_user.py 2>/dev/null || true
    unset AUTO_SKIP_PROMPT
fi

# 检查 main.py 是否存在
if [ ! -f "main.py" ]; then
    log_error "找不到 main.py，当前目录: $(pwd)"
    log_error "请确保在 web_backend 目录中"
    cd ..
    exit 1
fi

# 启动后端
log_info "启动 Web 后端服务..."
log_info "工作目录: $(pwd)"
nohup $PYTHON_CMD -m uvicorn main:app --host 0.0.0.0 --port 8000 > ../logs/web_backend.log 2>&1 &
BACKEND_PID=$!

cd ..

# 等待后端启动
log_info "等待后端启动..."
sleep 5

# 检查后端状态
if curl -s http://localhost:8000/api/health >/dev/null 2>&1; then
    log_success "Web 后端启动成功 (PID: $BACKEND_PID)"
else
    log_warning "Web 后端可能未完全启动，请检查日志"
fi

echo ""

# ============================================================================
# 步骤 6: 启动 Web 前端
# ============================================================================
log_step "6/7" "启动 Web 前端"
echo ""

cd web_frontend

# 检查 node_modules
if [ ! -d "node_modules" ]; then
    log_warning "前端依赖未安装"
    read -p "是否安装前端依赖? 这可能需要几分钟 (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "安装前端依赖..."
        npm install
    else
        log_warning "跳过前端启动"
        cd ..
        echo ""
        # 跳到步骤7
        log_step "7/7" "启动量化交易程序"
        echo ""
        
        read -p "是否启动量化交易程序? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "启动量化交易程序..."
            nohup $PYTHON_CMD main.py --config config.yaml > logs/quant_trading.log 2>&1 &
            QUANT_PID=$!
            sleep 3
            
            if ps -p $QUANT_PID > /dev/null 2>&1; then
                log_success "量化交易程序启动成功 (PID: $QUANT_PID)"
            else
                log_warning "量化交易程序可能未成功启动"
            fi
        fi
        
        # 跳到总结
        echo ""
        echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${BLUE}║                    系统启动完成                            ║${NC}"
        echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        
        log_success "后端服务已启动"
        echo ""
        
        echo -e "${CYAN}服务信息:${NC}"
        echo "  Web 后端: http://localhost:8000"
        echo "  API 文档: http://localhost:8000/api/docs"
        echo ""
        
        echo -e "${CYAN}查看日志:${NC}"
        echo "  后端: tail -f logs/web_backend.log"
        if [ ! -z "$QUANT_PID" ]; then
            echo "  量化交易: tail -f logs/quant_trading.log"
        fi
        echo ""
        
        echo -e "${CYAN}停止服务:${NC}"
        echo "  ./stop_system_wsl.sh"
        echo ""
        
        echo -e "${YELLOW}提示: 前端未启动，如需启动前端请运行:${NC}"
        echo "  cd web_frontend && npm start"
        echo ""
        
        exit 0
    fi
fi

# 检查环境变量
if [ ! -f ".env" ]; then
    log_info "创建环境变量文件..."
    cat > .env << EOF
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws
EOF
fi

# 启动前端
log_info "启动 Web 前端..."
nohup npm start > ../logs/web_frontend.log 2>&1 &
FRONTEND_PID=$!

cd ..

# 等待前端启动
log_info "等待前端启动 (约30秒)..."
sleep 30

# 检查前端状态
if curl -s http://localhost:3000 >/dev/null 2>&1; then
    log_success "Web 前端启动成功 (PID: $FRONTEND_PID)"
else
    log_warning "Web 前端可能未完全启动，请检查日志"
fi

echo ""

# ============================================================================
# 步骤 7: 启动量化交易程序（可选）
# ============================================================================
log_step "7/7" "启动量化交易程序"
echo ""

read -p "是否启动量化交易程序? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "启动量化交易程序..."
    
    # 检查配置
    if [ -f "config.yaml" ]; then
        nohup $PYTHON_CMD main.py --config config.yaml > logs/quant_trading.log 2>&1 &
        QUANT_PID=$!
        
        sleep 3
        
        if ps -p $QUANT_PID > /dev/null 2>&1; then
            log_success "量化交易程序启动成功 (PID: $QUANT_PID)"
        else
            log_warning "量化交易程序可能未成功启动，请检查日志"
        fi
    else
        log_warning "配置文件不存在，跳过量化交易程序启动"
    fi
else
    log_info "跳过量化交易程序启动"
fi

echo ""

# ============================================================================
# 总结
# ============================================================================
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    系统启动完成                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

log_success "所有服务已启动"
echo ""

echo -e "${CYAN}服务信息:${NC}"
echo "  Web 后端: http://localhost:8000"
echo "  Web 前端: http://localhost:3000"
echo "  API 文档: http://localhost:8000/api/docs"
echo ""

echo -e "${CYAN}访问方式:${NC}"
echo "  1. WSL 内访问: http://localhost:3000"
echo "  2. Windows 浏览器访问: http://localhost:3000"
echo ""

echo -e "${CYAN}默认登录凭据:${NC}"
echo "  用户名: admin"
echo "  密码: admin123"
echo ""

echo -e "${CYAN}查看日志:${NC}"
echo "  后端: tail -f logs/web_backend.log"
echo "  前端: tail -f logs/web_frontend.log"
if [ ! -z "$QUANT_PID" ]; then
    echo "  量化交易: tail -f logs/quant_trading.log"
fi
echo ""

echo -e "${CYAN}查看进程:${NC}"
echo "  ps aux | grep -E 'uvicorn|npm|main.py'"
echo ""

echo -e "${CYAN}停止服务:${NC}"
echo "  ./stop_system_wsl.sh"
echo "  或手动: pkill -f uvicorn; pkill -f npm"
echo ""

echo -e "${GREEN}🎉 启动完成！请访问 http://localhost:3000${NC}"
echo ""

