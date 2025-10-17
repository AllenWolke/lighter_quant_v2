#!/bin/bash
# Lighter 量化交易系统 - 一键启动所有服务
# 支持: Web 前端 + Web 后端 + 量化交易模块

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# 日志函数
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[步骤 $1]${NC} $2"; }

# 清屏
clear

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    Lighter 量化交易系统 - 一键启动所有服务                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}启动服务: Web前端 + Web后端 + 量化交易模块${NC}"
echo ""

# 检测操作系统
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS_TYPE="Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS_TYPE="macOS"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    OS_TYPE="Windows (Git Bash)"
else
    OS_TYPE="Unknown"
fi

log_info "操作系统: $OS_TYPE"

# 检测 Python 命令
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PIP_CMD="pip"
else
    log_error "未找到 Python，请先安装 Python 3.9+"
    exit 1
fi

log_info "Python: $($PYTHON_CMD --version)"

# 检测 Node.js
if command -v node &> /dev/null; then
    log_info "Node.js: $(node --version)"
else
    log_warning "未找到 Node.js，前端将无法启动"
fi

echo ""

# ============================================================================
# 步骤 1: 环境准备
# ============================================================================
log_step "1/8" "环境准备"
echo ""

# 创建必要目录
log_info "创建必要目录..."
mkdir -p logs data backups

# 检查配置文件
if [ ! -f "config.yaml" ]; then
    log_warning "配置文件不存在: config.yaml"
    log_info "将使用模拟数据运行"
else
    log_success "配置文件已存在"
fi

echo ""

# ============================================================================
# 步骤 2: 停止现有服务
# ============================================================================
log_step "2/8" "停止现有服务"
echo ""

log_info "停止 Web 后端..."
pkill -f "uvicorn.*main:app" 2>/dev/null && log_success "  ✓ Web 后端已停止" || log_info "  ✓ Web 后端未运行"

log_info "停止 Web 前端..."
pkill -f "node.*react-scripts" 2>/dev/null && log_success "  ✓ Web 前端已停止" || log_info "  ✓ Web 前端未运行"
pkill -f "npm.*start" 2>/dev/null || true

log_info "停止量化交易模块..."
pkill -f "python.*main.py.*config" 2>/dev/null && log_success "  ✓ 量化交易模块已停止" || log_info "  ✓ 量化交易模块未运行"

sleep 2

log_success "现有服务已清理"
echo ""

# ============================================================================
# 步骤 3: 检查依赖
# ============================================================================
log_step "3/8" "检查依赖"
echo ""

# 检查 Python 依赖
log_info "检查 Python 依赖..."
MISSING_PYTHON_DEPS=()

for pkg in fastapi uvicorn pydantic sqlalchemy; do
    if ! $PYTHON_CMD -c "import $pkg" 2>/dev/null; then
        MISSING_PYTHON_DEPS+=($pkg)
    fi
done

if [ ${#MISSING_PYTHON_DEPS[@]} -gt 0 ]; then
    log_warning "缺少 Python 依赖: ${MISSING_PYTHON_DEPS[*]}"
    read -p "是否安装? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "安装 Python 依赖..."
        $PIP_CMD install fastapi uvicorn[standard] pydantic pydantic-settings sqlalchemy aiosqlite -q
        log_success "Python 依赖安装完成"
    fi
else
    log_success "Python 依赖完整"
fi

# 检查 Node.js 依赖
if command -v node &> /dev/null; then
    if [ -d "web_frontend/node_modules" ]; then
        log_success "Node.js 依赖已安装"
    else
        log_warning "Node.js 依赖未安装"
        log_info "前端首次启动可能需要几分钟"
    fi
fi

echo ""

# ============================================================================
# 步骤 4: 启动 Web 后端
# ============================================================================
log_step "4/8" "启动 Web 后端"
echo ""

cd web_backend

# 验证 main.py 存在
if [ ! -f "main.py" ]; then
    log_error "找不到 main.py"
    log_error "当前目录: $(pwd)"
    cd ..
    exit 1
fi

log_success "找到 main.py"
log_info "工作目录: $(pwd)"

# 初始化默认用户
if [ -f "init_default_user.py" ]; then
    log_info "初始化默认用户..."
    export AUTO_SKIP_PROMPT=1
    $PYTHON_CMD init_default_user.py 2>/dev/null || true
    unset AUTO_SKIP_PROMPT
fi

# 启动后端
log_info "启动 Web 后端服务..."
nohup $PYTHON_CMD -m uvicorn main:app --host 0.0.0.0 --port 8000 > ../logs/web_backend.log 2>&1 &
BACKEND_PID=$!

cd ..

# 等待后端启动
log_info "等待后端启动 (5秒)..."
sleep 5

# 验证后端
if ps -p $BACKEND_PID > /dev/null 2>&1; then
    log_success "Web 后端进程运行中 (PID: $BACKEND_PID)"
    
    # 测试 HTTP 端点
    if curl -s http://localhost:8000/api/health >/dev/null 2>&1; then
        log_success "Web 后端 HTTP 端点正常"
    else
        log_warning "Web 后端 HTTP 端点未响应（可能还在初始化）"
    fi
else
    log_error "Web 后端启动失败"
    log_info "查看日志: tail -30 logs/web_backend.log"
    tail -30 logs/web_backend.log
    exit 1
fi

echo ""

# ============================================================================
# 步骤 5: 启动 Web 前端
# ============================================================================
log_step "5/8" "启动 Web 前端"
echo ""

if ! command -v node &> /dev/null; then
    log_warning "Node.js 未安装，跳过前端启动"
    SKIP_FRONTEND=true
else
    cd web_frontend
    
    # 检查 node_modules
    if [ ! -d "node_modules" ]; then
        log_warning "前端依赖未安装"
        read -p "是否安装前端依赖? 这可能需要几分钟 (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "安装前端依赖..."
            npm install
            log_success "前端依赖安装完成"
        else
            log_warning "跳过前端启动"
            cd ..
            SKIP_FRONTEND=true
        fi
    fi
    
    if [ "$SKIP_FRONTEND" != "true" ]; then
        # 创建 .env 文件
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
        log_info "等待前端启动 (30秒)..."
        sleep 30
        
        # 验证前端
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            log_success "Web 前端进程运行中 (PID: $FRONTEND_PID)"
            
            # 测试前端端口
            if curl -s http://localhost:3000 >/dev/null 2>&1; then
                log_success "Web 前端可访问"
            else
                log_warning "Web 前端可能还在编译中"
            fi
        else
            log_warning "Web 前端进程可能已退出"
            log_info "查看日志: tail -30 logs/web_frontend.log"
        fi
    else
        cd .. 2>/dev/null || true
    fi
fi

echo ""

# ============================================================================
# 步骤 6: 启动量化交易模块
# ============================================================================
log_step "6/8" "启动量化交易模块"
echo ""

if [ ! -f "config.yaml" ]; then
    log_warning "配置文件不存在，跳过量化交易模块启动"
    SKIP_QUANT=true
else
    # 检查私钥是否配置
    PRIVATE_KEY=$($PYTHON_CMD -c "import yaml; print(yaml.safe_load(open('config.yaml'))['lighter']['api_key_private_key'])" 2>/dev/null || echo "")
    
    if [ "$PRIVATE_KEY" = "YOUR_MAINNET_PRIVATE_KEY_HERE" ] || [ "$PRIVATE_KEY" = "YOUR_TESTNET_PRIVATE_KEY_HERE" ] || [ -z "$PRIVATE_KEY" ]; then
        log_warning "私钥未配置，量化交易模块将无法连接到 Lighter"
        read -p "是否仍要启动量化交易模块? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "跳过量化交易模块启动"
            SKIP_QUANT=true
        fi
    fi
fi

if [ "$SKIP_QUANT" != "true" ]; then
    log_info "启动量化交易模块..."
    
    # 检查 main.py 是否存在
    if [ ! -f "main.py" ]; then
        log_error "找不到 main.py"
        log_warning "跳过量化交易模块启动"
    else
        nohup $PYTHON_CMD main.py --config config.yaml > logs/quant_trading.log 2>&1 &
        QUANT_PID=$!
        
        # 等待启动
        sleep 3
        
        # 验证进程
        if ps -p $QUANT_PID > /dev/null 2>&1; then
            log_success "量化交易模块启动成功 (PID: $QUANT_PID)"
        else
            log_warning "量化交易模块可能启动失败"
            log_info "查看日志: tail -30 logs/quant_trading.log"
        fi
    fi
fi

echo ""

# ============================================================================
# 步骤 7: 验证所有服务
# ============================================================================
log_step "7/8" "验证服务状态"
echo ""

# 验证后端
log_info "验证 Web 后端..."
if curl -s http://localhost:8000/api/health >/dev/null 2>&1; then
    log_success "  ✓ Web 后端正常 (http://localhost:8000)"
else
    log_error "  ✗ Web 后端未响应"
fi

# 验证前端
if [ "$SKIP_FRONTEND" != "true" ]; then
    log_info "验证 Web 前端..."
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        log_success "  ✓ Web 前端正常 (http://localhost:3000)"
    else
        log_warning "  ⚠️  Web 前端可能还在编译"
    fi
fi

# 验证量化交易
if [ "$SKIP_QUANT" != "true" ] && [ ! -z "$QUANT_PID" ]; then
    log_info "验证量化交易模块..."
    if ps -p $QUANT_PID > /dev/null 2>&1; then
        log_success "  ✓ 量化交易模块运行中"
    else
        log_warning "  ⚠️  量化交易模块可能已退出"
    fi
fi

echo ""

# ============================================================================
# 步骤 8: 显示服务信息
# ============================================================================
log_step "8/8" "服务信息"
echo ""

# 显示运行的服务
echo -e "${CYAN}运行中的服务:${NC}"
echo ""

# Web 后端
if [ ! -z "$BACKEND_PID" ] && ps -p $BACKEND_PID > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓ Web 后端${NC}"
    echo "    PID: $BACKEND_PID"
    echo "    端口: 8000"
    echo "    地址: http://localhost:8000"
    echo "    文档: http://localhost:8000/api/docs"
    echo ""
fi

# Web 前端
if [ "$SKIP_FRONTEND" != "true" ] && [ ! -z "$FRONTEND_PID" ] && ps -p $FRONTEND_PID > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓ Web 前端${NC}"
    echo "    PID: $FRONTEND_PID"
    echo "    端口: 3000"
    echo "    地址: http://localhost:3000"
    echo ""
fi

# 量化交易
if [ "$SKIP_QUANT" != "true" ] && [ ! -z "$QUANT_PID" ] && ps -p $QUANT_PID > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓ 量化交易模块${NC}"
    echo "    PID: $QUANT_PID"
    echo "    配置: config.yaml"
    echo ""
fi

# ============================================================================
# 总结
# ============================================================================
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    启动完成                                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 统计启动的服务
SERVICES_STARTED=0
[ ! -z "$BACKEND_PID" ] && ps -p $BACKEND_PID > /dev/null 2>&1 && SERVICES_STARTED=$((SERVICES_STARTED + 1))
[ "$SKIP_FRONTEND" != "true" ] && [ ! -z "$FRONTEND_PID" ] && ps -p $FRONTEND_PID > /dev/null 2>&1 && SERVICES_STARTED=$((SERVICES_STARTED + 1))
[ "$SKIP_QUANT" != "true" ] && [ ! -z "$QUANT_PID" ] && ps -p $QUANT_PID > /dev/null 2>&1 && SERVICES_STARTED=$((SERVICES_STARTED + 1))

log_success "$SERVICES_STARTED 个服务已启动"
echo ""

# ============================================================================
# 使用说明
# ============================================================================
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}                        使用说明                              ${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${MAGENTA}📱 访问系统:${NC}"
echo ""
echo "  Web 界面: ${GREEN}http://localhost:3000${NC}"
echo "  API 文档: ${GREEN}http://localhost:8000/api/docs${NC}"
echo ""

echo -e "${MAGENTA}🔐 登录凭据:${NC}"
echo ""
echo "  用户名: ${CYAN}admin${NC}"
echo "  密码: ${CYAN}admin123${NC}"
echo ""

echo -e "${MAGENTA}📊 查看日志:${NC}"
echo ""
echo "  后端: ${YELLOW}tail -f logs/web_backend.log${NC}"
echo "  前端: ${YELLOW}tail -f logs/web_frontend.log${NC}"
if [ "$SKIP_QUANT" != "true" ]; then
    echo "  量化交易: ${YELLOW}tail -f logs/quant_trading.log${NC}"
fi
echo "  所有日志: ${YELLOW}tail -f logs/*.log${NC}"
echo ""

echo -e "${MAGENTA}🔍 查看进程:${NC}"
echo ""
echo "  ${YELLOW}ps aux | grep -E 'uvicorn|npm|main.py' | grep -v grep${NC}"
echo ""

echo -e "${MAGENTA}🛑 停止服务:${NC}"
echo ""
echo "  停止所有: ${YELLOW}./stop_all.sh${NC}"
echo "  或手动: ${YELLOW}pkill -f uvicorn; pkill -f npm; pkill -f 'python.*main.py'${NC}"
echo ""

echo -e "${MAGENTA}🔄 重启服务:${NC}"
echo ""
echo "  ${YELLOW}./restart_all.sh${NC}"
echo ""

echo -e "${MAGENTA}🧪 测试账户数据:${NC}"
echo ""
echo "  ${YELLOW}./diagnose_account_balance.sh${NC}"
echo ""

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# ============================================================================
# 健康检查
# ============================================================================
echo -e "${MAGENTA}🏥 健康检查:${NC}"
echo ""

sleep 2

# 后端健康检查
if curl -s http://localhost:8000/api/health >/dev/null 2>&1; then
    HEALTH_RESPONSE=$(curl -s http://localhost:8000/api/health)
    echo -e "  ${GREEN}✓ Web 后端健康${NC}"
    echo "    响应: $HEALTH_RESPONSE"
else
    echo -e "  ${YELLOW}⚠️  Web 后端未完全启动${NC}"
    echo "    等待几秒后访问: http://localhost:8000/api/health"
fi

echo ""

# 前端健康检查
if [ "$SKIP_FRONTEND" != "true" ]; then
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓ Web 前端可访问${NC}"
    else
        echo -e "  ${YELLOW}⚠️  Web 前端还在编译中（约需1-2分钟）${NC}"
        echo "    请稍后访问: http://localhost:3000"
    fi
fi

echo ""

# ============================================================================
# 最终提示
# ============================================================================
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    🎉 启动完成！                           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ "$SKIP_FRONTEND" != "true" ]; then
    echo -e "${GREEN}🚀 请访问: ${CYAN}http://localhost:3000${NC}"
else
    echo -e "${GREEN}🚀 后端已启动: ${CYAN}http://localhost:8000${NC}"
    echo -e "${YELLOW}💡 要启动前端，请运行: cd web_frontend && npm start${NC}"
fi

echo ""

# 保存 PID 到文件（方便后续管理）
cat > .service_pids << EOF
BACKEND_PID=$BACKEND_PID
FRONTEND_PID=${FRONTEND_PID:-}
QUANT_PID=${QUANT_PID:-}
EOF

log_info "服务 PID 已保存到 .service_pids"
echo ""
