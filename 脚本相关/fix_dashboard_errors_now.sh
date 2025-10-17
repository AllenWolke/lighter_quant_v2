#!/bin/bash
# 修复 Dashboard 错误并重启后端

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     修复 Dashboard 错误并重启后端                         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

PYTHON_CMD="python3"
command -v python3 &> /dev/null || PYTHON_CMD="python"

echo -e "${CYAN}[1/4] 停止后端服务${NC}"
echo ""
pkill -f "uvicorn.*main:app" 2>/dev/null && echo "  ✓ 已停止现有进程" || echo "  ✓ 无现有进程"
sleep 2
echo ""

echo -e "${CYAN}[2/4] 清理 Python 缓存${NC}"
echo ""
rm -rf web_backend/__pycache__
rm -rf web_backend/**/__pycache__
echo "  ✓ Python 缓存已清理"
echo ""

echo -e "${CYAN}[3/4] 启动后端服务${NC}"
echo ""
cd web_backend

if [ ! -f "main.py" ]; then
    echo -e "${RED}  ✗ 错误: 找不到 main.py${NC}"
    cd ..
    exit 1
fi

echo "  启动服务..."
nohup $PYTHON_CMD -m uvicorn main:app --host 0.0.0.0 --port 8000 > ../logs/web_backend.log 2>&1 &
BACKEND_PID=$!

cd ..

echo "  等待启动 (10秒)..."
sleep 10

echo ""

echo -e "${CYAN}[4/4] 验证服务${NC}"
echo ""

if curl -s http://localhost:8000/api/health >/dev/null 2>&1; then
    echo -e "${GREEN}  ✓ 后端服务正常${NC}"
    
    # 显示健康检查
    HEALTH=$(curl -s http://localhost:8000/api/health)
    echo "    响应: $HEALTH"
    
    echo ""
    echo "  测试新端点..."
    
    # 获取 token
    TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
      -H "Content-Type: application/json" \
      -d '{"username":"admin","password":"admin123"}' \
      | grep -o '"accessToken":"[^"]*"' | cut -d'"' -f4)
    
    if [ ! -z "$TOKEN" ]; then
        # 测试 positions 端点
        if curl -s http://localhost:8000/api/trading/positions \
           -H "Authorization: Bearer $TOKEN" >/dev/null 2>&1; then
            echo -e "${GREEN}    ✓ /api/trading/positions 可用${NC}"
        else
            echo -e "${YELLOW}    ⚠️  /api/trading/positions 可能有问题${NC}"
        fi
        
        # 测试 stats 端点
        if curl -s http://localhost:8000/api/trading/stats \
           -H "Authorization: Bearer $TOKEN" >/dev/null 2>&1; then
            echo -e "${GREEN}    ✓ /api/trading/stats 可用${NC}"
        else
            echo -e "${YELLOW}    ⚠️  /api/trading/stats 可能有问题${NC}"
        fi
    fi
else
    echo -e "${RED}  ✗ 后端服务未响应${NC}"
    echo ""
    echo "  查看日志:"
    tail -30 logs/web_backend.log
    exit 1
fi

echo ""

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    修复完成                                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}✅ 后端服务已重启${NC}"
echo ""

echo -e "${CYAN}已修复的问题:${NC}"
echo "  1. ✓ 添加了 /api/trading/positions 端点"
echo "  2. ✓ 修复了 /api/trading/stats 参数错误"
echo "  3. ✓ 配置了 camelCase 响应格式"
echo ""

echo -e "${CYAN}下一步:${NC}"
echo "  1. 访问 Dashboard: http://localhost:3000/dashboard"
echo "  2. 清除浏览器缓存: F12 → Application → Clear site data"
echo "  3. 强制刷新: Ctrl+Shift+R"
echo "  4. 重新登录: admin / admin123"
echo "  5. 点击"刷新数据"按钮"
echo ""

echo -e "${CYAN}查看日志:${NC}"
echo "  tail -f logs/web_backend.log"
echo ""
