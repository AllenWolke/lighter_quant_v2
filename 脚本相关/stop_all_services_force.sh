#!/bin/bash

###############################################################################
# 强制停止所有服务
# 比 stop_all_services.sh 更彻底
###############################################################################

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "=========================================="
echo "  强制停止所有服务"
echo "=========================================="
echo ""

# 步骤1: 使用标准停止脚本
echo -e "${BLUE}[INFO]${NC} 步骤1: 执行标准停止脚本..."
if [ -f "stop_all_services.sh" ]; then
    ./stop_all_services.sh 2>/dev/null || true
else
    echo -e "${YELLOW}[WARNING]${NC} 未找到标准停止脚本"
fi
echo ""

# 步骤2: 强制终止所有相关进程
echo -e "${BLUE}[INFO]${NC} 步骤2: 强制终止所有进程..."

# 前端进程
echo "  终止前端进程..."
pkill -9 -f "npm start" 2>/dev/null || true
pkill -9 -f "react-scripts" 2>/dev/null || true
pkill -9 -f "node.*react" 2>/dev/null || true
pkill -9 -f "webpack-dev-server" 2>/dev/null || true

# 后端进程
echo "  终止后端进程..."
pkill -9 -f "python.*main.py" 2>/dev/null || true
pkill -9 -f "uvicorn" 2>/dev/null || true
pkill -9 -f "web_backend" 2>/dev/null || true

# 交易系统进程
echo "  终止交易系统进程..."
pkill -9 -f "quant_trading" 2>/dev/null || true

# 其他可能的进程
echo "  清理其他进程..."
pkill -9 -f "init_default_user" 2>/dev/null || true

echo -e "${GREEN}✓ 进程终止完成${NC}"
echo ""

# 步骤3: 等待进程退出
echo -e "${BLUE}[INFO]${NC} 步骤3: 等待进程退出..."
sleep 3
echo -e "${GREEN}✓ 等待完成${NC}"
echo ""

# 步骤4: 释放端口
echo -e "${BLUE}[INFO]${NC} 步骤4: 释放端口..."

if command -v fuser &> /dev/null; then
    # 使用 fuser 释放端口
    sudo fuser -k 3000/tcp 2>/dev/null || true
    sudo fuser -k 8000/tcp 2>/dev/null || true
    echo -e "${GREEN}✓ 端口已释放${NC}"
else
    echo -e "${YELLOW}[WARNING]${NC} fuser 命令不可用"
    
    # 备用方法：查找并杀死占用端口的进程
    if command -v lsof &> /dev/null; then
        port_3000_pid=$(lsof -t -i:3000 2>/dev/null)
        port_8000_pid=$(lsof -t -i:8000 2>/dev/null)
        
        [ -n "$port_3000_pid" ] && kill -9 $port_3000_pid 2>/dev/null
        [ -n "$port_8000_pid" ] && kill -9 $port_8000_pid 2>/dev/null
        
        echo -e "${GREEN}✓ 端口已释放${NC}"
    else
        echo -e "${YELLOW}[WARNING]${NC} 无法自动释放端口，请手动检查"
    fi
fi
echo ""

# 步骤5: 清理 PID 文件
echo -e "${BLUE}[INFO]${NC} 步骤5: 清理 PID 文件..."
rm -f logs/*.pid 2>/dev/null || true
echo -e "${GREEN}✓ PID 文件已清理${NC}"
echo ""

# 步骤6: 验证停止结果
echo -e "${BLUE}[INFO]${NC} 步骤6: 验证停止结果..."
echo ""

# 检查进程
node_count=$(ps aux | grep -E "node|npm" | grep -v grep | wc -l)
python_count=$(ps aux | grep python | grep main.py | grep -v grep | wc -l)

if [ $node_count -eq 0 ]; then
    echo -e "${GREEN}✓ 前端进程: 已停止${NC}"
else
    echo -e "${YELLOW}⚠️  前端进程: 仍有 $node_count 个进程运行${NC}"
    ps aux | grep -E "node|npm" | grep -v grep
fi

if [ $python_count -eq 0 ]; then
    echo -e "${GREEN}✓ 后端进程: 已停止${NC}"
else
    echo -e "${YELLOW}⚠️  后端进程: 仍有 $python_count 个进程运行${NC}"
    ps aux | grep python | grep main.py | grep -v grep
fi

# 检查端口
echo ""
port_3000_status=$(lsof -i :3000 2>/dev/null | wc -l)
port_8000_status=$(lsof -i :8000 2>/dev/null | wc -l)

if [ $port_3000_status -eq 0 ]; then
    echo -e "${GREEN}✓ 端口 3000: 已释放${NC}"
else
    echo -e "${YELLOW}⚠️  端口 3000: 仍被占用${NC}"
    lsof -i :3000 2>/dev/null
fi

if [ $port_8000_status -eq 0 ]; then
    echo -e "${GREEN}✓ 端口 8000: 已释放${NC}"
else
    echo -e "${YELLOW}⚠️  端口 8000: 仍被占用${NC}"
    lsof -i :8000 2>/dev/null
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✅ 强制停止完成${NC}"
echo "=========================================="
echo ""

# 检查是否还有进程或端口占用
if [ $node_count -eq 0 ] && [ $python_count -eq 0 ] && [ $port_3000_status -eq 0 ] && [ $port_8000_status -eq 0 ]; then
    echo -e "${GREEN}🎉 所有服务已完全停止${NC}"
    echo ""
    echo "如果浏览器仍显示页面，请:"
    echo "  1. 按 Ctrl+Shift+R 强制刷新"
    echo "  2. 或清除浏览器缓存"
    echo "  3. 或使用无痕模式访问"
else
    echo -e "${YELLOW}⚠️  部分服务可能仍在运行${NC}"
    echo ""
    echo "建议执行:"
    echo "  sudo fuser -k 3000/tcp"
    echo "  sudo fuser -k 8000/tcp"
    echo "  pkill -9 -f node"
    echo "  pkill -9 -f python"
fi

echo ""
echo "=========================================="

