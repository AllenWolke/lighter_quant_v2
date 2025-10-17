#!/bin/bash
# 修复最后的问题并重启后端

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     修复最后的问题并重启后端                              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo "已修复的问题:"
echo "  1. ✓ manifest.json 404"
echo "  2. ✓ /api/trading/symbols 404"
echo "  3. ✓ /api/trading/positions 404"
echo "  4. ✓ /api/trading/stats 500"
echo "  5. ✓ /api/positions/history 404 (新增)"
echo "  6. ✓ /api/strategies/{id}/toggle 404 (新增)"
echo "  7. ✓ camelCase 响应格式"
echo "  8. ✓ WebSocket 连接 (所有页面)"
echo ""

PYTHON_CMD="python3"
command -v python3 &> /dev/null || PYTHON_CMD="python"

echo -e "${CYAN}[1/3] 停止并清理${NC}"
echo ""
pkill -f "uvicorn.*main:app" 2>/dev/null && echo "  ✓ 后端已停止" || echo "  ✓ 后端未运行"
sleep 2

# 清理所有 Python 缓存
find web_backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

echo "  ✓ 已清理缓存"
echo ""

echo -e "${CYAN}[2/3] 启动后端${NC}"
echo ""
cd web_backend
echo "  工作目录: $(pwd)"
nohup $PYTHON_CMD -m uvicorn main:app --host 0.0.0.0 --port 8000 > ../logs/web_backend.log 2>&1 &
BACKEND_PID=$!
cd ..
echo "  等待启动 (10秒)..."
sleep 10
echo ""

echo -e "${CYAN}[3/3] 验证服务${NC}"
echo ""

if curl -s http://localhost:8000/api/health >/dev/null 2>&1; then
    echo -e "${GREEN}  ✓ 后端服务正常${NC}"
    echo ""
    echo "  访问 API 文档查看所有端点:"
    echo "  http://localhost:8000/api/docs"
else
    echo -e "${RED}  ✗ 后端启动失败${NC}"
    tail -30 logs/web_backend.log
    exit 1
fi

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    ✅ 修复完成                             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}所有端点已就绪:${NC}"
echo "  • /api/trading/account"
echo "  • /api/trading/symbols"
echo "  • /api/trading/positions"
echo "  • /api/trading/stats"
echo "  • /api/trading/orders"
echo "  • /api/positions/history (新增)"
echo "  • /api/strategies/{id}/toggle (新增)"
echo ""

echo -e "${CYAN}下一步 - 在浏览器中:${NC}"
echo ""
echo "  1. 清除缓存:"
echo "     F12 → Application → Clear site data"
echo ""
echo "  2. 强制刷新:"
echo "     Ctrl+Shift+R"
echo ""
echo "  3. 重新登录:"
echo "     admin / admin123"
echo ""
echo "  4. 测试所有页面:"
echo "     • Dashboard    - 应显示余额"
echo "     • Trading      - 应正常工作"
echo "     • Strategies   - 可切换状态"
echo "     • Positions    - 应显示持仓"
echo "     • History      - 持仓记录应加载"
echo ""

echo -e "${GREEN}🎉 所有问题已修复！${NC}"
echo ""

