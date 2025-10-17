#!/bin/bash
# Lighter量化交易系统 - 完整启动脚本
# 自动创建目录、检查环境、启动所有服务

set -e  # 遇到错误立即退出

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
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
echo "=========================================="
echo "  Lighter量化交易系统 - 服务启动"
echo "=========================================="
echo ""

# 1. 检查是否在项目根目录
if [ ! -f "main.py" ]; then
    log_error "请在项目根目录下运行此脚本"
    exit 1
fi

log_info "当前目录: $(pwd)"

# 2. 检查并激活虚拟环境
if [ -f "venv/bin/activate" ]; then
    log_info "激活虚拟环境..."
    source venv/bin/activate
    log_info "✅ 虚拟环境已激活"
else
    log_warning "未找到虚拟环境，使用系统Python"
fi

# 3. 创建必要目录
log_info "创建必要目录..."
mkdir -p logs/{backend,frontend,trading,system}
mkdir -p data/{db,cache,temp}
mkdir -p backups/{config,data,logs}

# 设置权限
chmod 755 logs data
chmod 700 backups

log_info "✅ 目录创建完成"

# 4. 检查配置文件
log_info "检查配置文件..."
if [ ! -f "config.yaml" ] && [ ! -f "config_linux_mainnet.yaml" ]; then
    log_error "未找到配置文件"
    log_info "请复制配置文件: cp config_linux_mainnet.yaml config.yaml"
    exit 1
fi

CONFIG_FILE="config.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    CONFIG_FILE="config_linux_mainnet.yaml"
fi

log_info "✅ 使用配置文件: $CONFIG_FILE"

# 5. 停止已运行的服务
log_info "检查并停止已运行的服务..."

if [ -f "logs/backend.pid" ]; then
    backend_pid=$(cat logs/backend.pid)
    if ps -p $backend_pid > /dev/null 2>&1; then
        log_warning "停止已运行的后端服务 (PID: $backend_pid)"
        kill $backend_pid
        sleep 2
    fi
fi

if [ -f "logs/frontend.pid" ]; then
    frontend_pid=$(cat logs/frontend.pid)
    if ps -p $frontend_pid > /dev/null 2>&1; then
        log_warning "停止已运行的前端服务 (PID: $frontend_pid)"
        kill $frontend_pid
        sleep 2
    fi
fi

if [ -f "logs/trading.pid" ]; then
    trading_pid=$(cat logs/trading.pid)
    if ps -p $trading_pid > /dev/null 2>&1; then
        log_warning "停止已运行的交易系统 (PID: $trading_pid)"
        kill $trading_pid
        sleep 2
    fi
fi

# 6. 检查并安装 Web 后端依赖
log_info "检查 Web 后端依赖..."

# 检查关键依赖是否已安装
if [ -f "venv/bin/python" ]; then
    PYTHON_CMD="venv/bin/python"
else
    PYTHON_CMD="python3"
fi

# 检查 fastapi 是否已安装
if ! $PYTHON_CMD -c "import fastapi" 2>/dev/null; then
    log_warning "检测到缺少 Web 后端依赖，正在安装..."
    
    # 激活虚拟环境并安装依赖
    if [ -f "venv/bin/activate" ]; then
        echo -e "${BLUE}[INFO]${NC} 安装 Web 后端核心依赖（可能需要1-2分钟）..."
        
        # 使用子 shell 来避免函数作用域问题
        (
            source venv/bin/activate
            pip install fastapi>=0.104.0 \
                        uvicorn[standard]>=0.24.0 \
                        pydantic[email]>=2.5.0 \
                        pydantic-settings>=2.1.0 \
                        email-validator>=2.0.0 \
                        sqlalchemy>=2.0.0 \
                        passlib[bcrypt]>=1.7.4 \
                        python-jose[cryptography]>=3.3.0 \
                        python-multipart>=0.0.6 \
                        aiosqlite>=0.19.0 \
                        websockets>=12.0 \
                        httpx>=0.25.0 \
                        aiohttp>=3.9.0 \
                        python-dotenv>=1.0.0 \
                        pyyaml>=6.0 \
                        loguru>=0.7.0 \
                        -q
        )
        
        # 验证安装
        if $PYTHON_CMD -c "import fastapi" 2>/dev/null; then
            log_success "Web 后端依赖安装成功"
        else
            log_error "Web 后端依赖安装失败"
            exit 1
        fi
    else
        log_error "无法激活虚拟环境"
        exit 1
    fi
else
    log_success "Web 后端依赖已安装"
fi

# 7. 初始化数据库和默认用户
log_info "初始化数据库..."
cd web_backend

if [ ! -f "main.py" ]; then
    log_error "未找到 web_backend/main.py"
    cd ..
    exit 1
fi

# 创建默认管理员用户（如果不存在）
if [ -f "init_default_user.py" ]; then
    # 优先使用虚拟环境的python，否则使用python3
    # 设置环境变量以跳过交互式提示
    export AUTO_SKIP_PROMPT=1
    if [ -f "../venv/bin/python" ]; then
        ../venv/bin/python init_default_user.py 2>/dev/null || true
    else
        python3 init_default_user.py 2>/dev/null || true
    fi
    unset AUTO_SKIP_PROMPT
fi

# 启动Web后端
log_info "启动Web后端..."
# 优先使用虚拟环境的python
if [ -f "../venv/bin/python" ]; then
    nohup ../venv/bin/python main.py > ../logs/backend.log 2>&1 &
else
    nohup python3 main.py > ../logs/backend.log 2>&1 &
fi
backend_pid=$!
echo $backend_pid > ../logs/backend.pid

# 验证后端启动
sleep 3
if ps -p $backend_pid > /dev/null; then
    log_info "✅ 后端服务已启动 (PID: $backend_pid)"
else
    log_error "后端服务启动失败，查看日志: logs/backend.log"
    cd ..
    exit 1
fi

cd ..

# 7. 启动Web前端
log_info "启动Web前端..."
cd web_frontend

if [ ! -f "package.json" ]; then
    log_warning "未找到 web_frontend/package.json，跳过前端启动"
    cd ..
else
    # 检查node_modules
    if [ ! -d "node_modules" ]; then
        log_warning "未找到 node_modules，正在安装依赖..."
        npm install
    fi
    
    nohup npm start > ../logs/frontend.log 2>&1 &
    frontend_pid=$!
    echo $frontend_pid > ../logs/frontend.pid
    
    # 验证前端启动
    sleep 5
    if ps -p $frontend_pid > /dev/null; then
        log_info "✅ 前端服务已启动 (PID: $frontend_pid)"
    else
        log_error "前端服务启动失败，查看日志: logs/frontend.log"
    fi
    
    cd ..
fi

# 8. 启动交易系统
log_info "启动交易系统..."

nohup python main.py --config $CONFIG_FILE > logs/trading.log 2>&1 &
trading_pid=$!
echo $trading_pid > logs/trading.pid

# 验证交易系统启动
sleep 3
if ps -p $trading_pid > /dev/null; then
    log_info "✅ 交易系统已启动 (PID: $trading_pid)"
else
    log_error "交易系统启动失败，查看日志: logs/trading.log"
    exit 1
fi

# 9. 显示启动总结
echo ""
echo "=========================================="
echo "系统启动完成"
echo "=========================================="
echo ""
echo "运行中的服务:"
[ ! -z "$backend_pid" ] && echo "  后端服务:   PID $backend_pid (端口 8000)"
[ ! -z "$frontend_pid" ] && echo "  前端服务:   PID $frontend_pid (端口 3000)"
[ ! -z "$trading_pid" ] && echo "  交易系统:   PID $trading_pid"
echo ""
echo "访问地址:"
echo "  Web前端: http://localhost:3000"
echo "  Web后端: http://localhost:8000"
echo "  API文档: http://localhost:8000/docs"
echo ""
echo "日志文件:"
echo "  后端日志: logs/backend.log"
echo "  前端日志: logs/frontend.log"
echo "  交易日志: logs/trading.log"
echo ""
echo "查看实时日志:"
echo "  tail -f logs/backend.log"
echo "  tail -f logs/frontend.log"
echo "  tail -f logs/trading.log"
echo ""
echo "停止服务:"
echo "  ./stop_all_services.sh"
echo "=========================================="
