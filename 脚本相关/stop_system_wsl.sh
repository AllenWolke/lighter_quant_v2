#!/bin/bash
# WSL Ubuntu 量化交易系统停止脚本

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    Lighter 量化交易系统 - 停止服务                        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}正在停止所有服务...${NC}"
echo ""

# 停止 Web 后端
echo -e "${GREEN}[1/3]${NC} 停止 Web 后端..."
pkill -f "uvicorn.*main:app" 2>/dev/null && echo "  ✓ Web 后端已停止" || echo "  ✓ Web 后端未运行"

# 停止 Web 前端
echo -e "${GREEN}[2/3]${NC} 停止 Web 前端..."
pkill -f "node.*react-scripts" 2>/dev/null && echo "  ✓ Web 前端已停止" || echo "  ✓ Web 前端未运行"
pkill -f "npm.*start" 2>/dev/null || true

# 停止量化交易程序
echo -e "${GREEN}[3/3]${NC} 停止量化交易程序..."
pkill -f "python.*main.py.*config" 2>/dev/null && echo "  ✓ 量化交易程序已停止" || echo "  ✓ 量化交易程序未运行"

# 等待进程完全停止
sleep 2

echo ""
echo -e "${GREEN}✓ 所有服务已停止${NC}"
echo ""

# 检查是否还有残留进程
REMAINING=$(ps aux | grep -E 'uvicorn|node.*react|python.*main.py' | grep -v grep | wc -l)

if [ $REMAINING -gt 0 ]; then
    echo -e "${YELLOW}⚠️  检测到 $REMAINING 个残留进程${NC}"
    echo ""
    read -p "是否强制终止所有相关进程? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pkill -9 -f "uvicorn" 2>/dev/null || true
        pkill -9 -f "node.*react" 2>/dev/null || true
        pkill -9 -f "python.*main.py" 2>/dev/null || true
        echo -e "${GREEN}✓ 已强制终止所有进程${NC}"
    fi
fi

echo ""
echo -e "${BLUE}服务已停止，如需重启请运行:${NC}"
echo "  ./start_system_wsl.sh"
echo ""

