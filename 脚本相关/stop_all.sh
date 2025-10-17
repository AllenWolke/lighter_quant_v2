#!/bin/bash
# Lighter 量化交易系统 - 停止所有服务

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    Lighter 量化交易系统 - 停止所有服务                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}正在停止所有服务...${NC}"
echo ""

# 停止 Web 后端
echo -e "${CYAN}[1/3]${NC} 停止 Web 后端..."
if pkill -f "uvicorn.*main:app" 2>/dev/null; then
    echo "  ✓ Web 后端已停止"
else
    echo "  ✓ Web 后端未运行"
fi

# 停止 Web 前端
echo -e "${CYAN}[2/3]${NC} 停止 Web 前端..."
if pkill -f "node.*react-scripts" 2>/dev/null; then
    echo "  ✓ Web 前端已停止"
else
    echo "  ✓ Web 前端未运行"
fi
pkill -f "npm.*start" 2>/dev/null || true

# 停止量化交易模块
echo -e "${CYAN}[3/3]${NC} 停止量化交易模块..."
if pkill -f "python.*main.py.*config" 2>/dev/null; then
    echo "  ✓ 量化交易模块已停止"
else
    echo "  ✓ 量化交易模块未运行"
fi

# 等待进程完全停止
sleep 2

echo ""

# 检查残留进程
REMAINING=$(ps aux | grep -E 'uvicorn|node.*react|python.*main.py.*config' | grep -v grep | wc -l)

if [ $REMAINING -gt 0 ]; then
    echo -e "${YELLOW}⚠️  检测到 $REMAINING 个残留进程${NC}"
    echo ""
    ps aux | grep -E 'uvicorn|node.*react|python.*main.py.*config' | grep -v grep
    echo ""
    read -p "是否强制终止? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pkill -9 -f "uvicorn" 2>/dev/null || true
        pkill -9 -f "node.*react" 2>/dev/null || true
        pkill -9 -f "python.*main.py" 2>/dev/null || true
        echo -e "${GREEN}✓ 已强制终止所有进程${NC}"
    fi
fi

# 清理 PID 文件
rm -f .service_pids

echo ""
echo -e "${GREEN}✓ 所有服务已停止${NC}"
echo ""
echo -e "${CYAN}重新启动:${NC} ./start_all.sh"
echo ""
