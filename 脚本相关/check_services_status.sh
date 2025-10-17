#!/bin/bash

###############################################################################
# 检查服务状态
# 诊断为什么前端仍然可以访问
###############################################################################

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo "=========================================================="
echo "  服务状态诊断"
echo "=========================================================="
echo ""

# 检查1: 检查端口监听
echo -e "${BLUE}▶ 检查端口监听${NC}"
echo ""

echo "端口 3000 (前端):"
if lsof -i :3000 > /dev/null 2>&1; then
    lsof -i :3000 | tail -n +2
    echo -e "${YELLOW}⚠️  端口 3000 仍在使用${NC}"
else
    echo -e "${GREEN}✓ 端口 3000 未使用${NC}"
fi

echo ""
echo "端口 8000 (后端):"
if lsof -i :8000 > /dev/null 2>&1; then
    lsof -i :8000 | tail -n +2
    echo -e "${YELLOW}⚠️  端口 8000 仍在使用${NC}"
else
    echo -e "${GREEN}✓ 端口 8000 未使用${NC}"
fi

echo ""

# 检查2: 检查 Node.js 进程
echo -e "${BLUE}▶ 检查 Node.js 进程${NC}"
echo ""

node_processes=$(ps aux | grep node | grep -v grep)
if [ -n "$node_processes" ]; then
    echo "$node_processes"
    echo -e "${YELLOW}⚠️  发现 Node.js 进程仍在运行${NC}"
else
    echo -e "${GREEN}✓ 没有 Node.js 进程${NC}"
fi

echo ""

# 检查3: 检查 Python 进程
echo -e "${BLUE}▶ 检查 Python 进程${NC}"
echo ""

python_processes=$(ps aux | grep python | grep -E "main.py|uvicorn" | grep -v grep)
if [ -n "$python_processes" ]; then
    echo "$python_processes"
    echo -e "${YELLOW}⚠️  发现 Python 进程仍在运行${NC}"
else
    echo -e "${GREEN}✓ 没有相关 Python 进程${NC}"
fi

echo ""

# 检查4: 检查 PID 文件
echo -e "${BLUE}▶ 检查 PID 文件${NC}"
echo ""

if [ -f "logs/frontend.pid" ]; then
    frontend_pid=$(cat logs/frontend.pid)
    echo "前端 PID 文件存在: $frontend_pid"
    if ps -p $frontend_pid > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  进程 $frontend_pid 仍在运行${NC}"
    else
        echo -e "${GREEN}✓ 进程 $frontend_pid 已停止，但 PID 文件未清理${NC}"
    fi
else
    echo -e "${GREEN}✓ 前端 PID 文件不存在${NC}"
fi

if [ -f "logs/backend.pid" ]; then
    backend_pid=$(cat logs/backend.pid)
    echo "后端 PID 文件存在: $backend_pid"
    if ps -p $backend_pid > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  进程 $backend_pid 仍在运行${NC}"
    else
        echo -e "${GREEN}✓ 进程 $backend_pid 已停止，但 PID 文件未清理${NC}"
    fi
else
    echo -e "${GREEN}✓ 后端 PID 文件不存在${NC}"
fi

echo ""

# 检查5: 检查浏览器缓存
echo -e "${BLUE}▶ 可能的原因分析${NC}"
echo ""

if lsof -i :3000 > /dev/null 2>&1; then
    echo -e "${CYAN}原因1:${NC} 前端开发服务器仍在运行"
    echo "  解决: pkill -9 -f 'npm start'"
    echo ""
fi

echo -e "${CYAN}原因2:${NC} 浏览器缓存"
echo "  React 开发服务器使用 Service Worker 和缓存"
echo "  即使服务器停止，浏览器可能显示缓存的页面"
echo "  解决:"
echo "    1. 按 Ctrl+Shift+R 强制刷新"
echo "    2. 清除浏览器缓存"
echo "    3. 使用无痕模式访问"
echo ""

if [ -d "web_frontend/build" ]; then
    echo -e "${CYAN}原因3:${NC} 构建的静态文件"
    echo "  web_frontend/build 目录存在"
    echo "  可能有其他服务器（如 Nginx）在提供这些文件"
    echo "  解决: 检查是否有 Nginx 或其他 Web 服务器在运行"
    echo ""
fi

# 检查6: 测试端口连接
echo -e "${BLUE}▶ 测试端口连接${NC}"
echo ""

echo "测试前端 (端口 3000):"
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  端口 3000 响应正常（服务仍在运行或有缓存）${NC}"
else
    echo -e "${GREEN}✓ 端口 3000 无响应（服务已停止）${NC}"
fi

echo ""
echo "测试后端 (端口 8000):"
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  端口 8000 响应正常（服务仍在运行）${NC}"
else
    echo -e "${GREEN}✓ 端口 8000 无响应（服务已停止）${NC}"
fi

echo ""

# 检查7: 推荐操作
echo "=========================================================="
echo -e "${CYAN}推荐操作:${NC}"
echo "=========================================================="
echo ""

if lsof -i :3000 > /dev/null 2>&1 || lsof -i :8000 > /dev/null 2>&1; then
    echo "发现服务仍在运行，建议执行:"
    echo ""
    echo "  # 强制停止所有相关进程"
    echo "  pkill -9 -f 'npm start'"
    echo "  pkill -9 -f 'node'"
    echo "  pkill -9 -f 'python.*main.py'"
    echo ""
    echo "  # 释放端口"
    echo "  sudo fuser -k 3000/tcp"
    echo "  sudo fuser -k 8000/tcp"
    echo ""
else
    echo "所有服务已停止，但浏览器可能显示缓存的页面"
    echo ""
    echo "  在浏览器中:"
    echo "  1. 按 Ctrl+Shift+R 强制刷新"
    echo "  2. 或清除浏览器缓存后重新访问"
    echo "  3. 或使用无痕模式测试"
    echo ""
fi

echo "=========================================================="

