#!/bin/bash
# Lighter量化交易系统 - 停止所有服务

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo "=========================================="
echo "  Lighter量化交易系统 - 停止服务"
echo "=========================================="
echo ""

# 停止后端服务
if [ -f "logs/backend.pid" ]; then
    backend_pid=$(cat logs/backend.pid)
    if ps -p $backend_pid > /dev/null 2>&1; then
        log_info "停止后端服务 (PID: $backend_pid)..."
        kill $backend_pid
        sleep 2
        
        # 强制杀死（如果还在运行）
        if ps -p $backend_pid > /dev/null 2>&1; then
            kill -9 $backend_pid
        fi
        
        echo "✅ 后端服务已停止"
    else
        echo "⚪ 后端服务未运行"
    fi
    rm -f logs/backend.pid
else
    echo "⚪ 未找到后端PID文件"
fi

# 停止前端服务
if [ -f "logs/frontend.pid" ]; then
    frontend_pid=$(cat logs/frontend.pid)
    if ps -p $frontend_pid > /dev/null 2>&1; then
        log_info "停止前端服务 (PID: $frontend_pid)..."
        kill $frontend_pid
        sleep 2
        
        if ps -p $frontend_pid > /dev/null 2>&1; then
            kill -9 $frontend_pid
        fi
        
        echo "✅ 前端服务已停止"
    else
        echo "⚪ 前端服务未运行"
    fi
    rm -f logs/frontend.pid
else
    echo "⚪ 未找到前端PID文件"
fi

# 停止交易系统
if [ -f "logs/trading.pid" ]; then
    trading_pid=$(cat logs/trading.pid)
    if ps -p $trading_pid > /dev/null 2>&1; then
        log_info "停止交易系统 (PID: $trading_pid)..."
        kill $trading_pid
        sleep 2
        
        if ps -p $trading_pid > /dev/null 2>&1; then
            kill -9 $trading_pid
        fi
        
        echo "✅ 交易系统已停止"
    else
        echo "⚪ 交易系统未运行"
    fi
    rm -f logs/trading.pid
else
    echo "⚪ 未找到交易系统PID文件"
fi

# 清理残留进程
log_info "清理残留进程..."
pkill -f "python.*main.py" 2>/dev/null || true
pkill -f "npm start" 2>/dev/null || true

echo ""
echo "=========================================="
echo "所有服务已停止"
echo "=========================================="
