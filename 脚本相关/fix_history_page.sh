#!/bin/bash
# 修复 History 页面持仓历史加载问题

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

clear

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     修复 History 页面持仓历史加载问题                     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${CYAN}🎯 修复内容:${NC}"
echo "  • 后端 API 返回格式添加 page 和 pageSize 字段"
echo "  • 匹配前端期望的数据结构"
echo ""

read -p "按 Enter 继续..." 

PYTHON_CMD="python3"
command -v python3 &> /dev/null || PYTHON_CMD="python"

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  [1/3] 停止后端服务"
echo "════════════════════════════════════════════════════════════"
echo ""

pkill -f "uvicorn.*main:app" 2>/dev/null && echo -e "${GREEN}  ✓ 已停止后端服务${NC}" || echo "  ✓ 后端未运行"
sleep 2
echo ""

echo "════════════════════════════════════════════════════════════"
echo "  [2/3] 清理缓存"
echo "════════════════════════════════════════════════════════════"
echo ""

find web_backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
echo -e "${GREEN}  ✓ 已清理 Python 缓存${NC}"
echo ""

echo "════════════════════════════════════════════════════════════"
echo "  [3/3] 启动后端服务"
echo "════════════════════════════════════════════════════════════"
echo ""

cd web_backend
nohup $PYTHON_CMD -m uvicorn main:app --host 0.0.0.0 --port 8000 > ../logs/web_backend.log 2>&1 &
BACKEND_PID=$!
cd ..

echo "  等待后端启动 (15秒)..."
sleep 15
echo ""

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    ✅ 修复完成                             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${CYAN}🌐 测试步骤:${NC}"
echo ""
echo "  1. 打开浏览器访问:"
echo "     http://localhost:3000"
echo ""
echo "  2. 登录: admin / admin123"
echo ""
echo "  3. 访问 History 页面"
echo ""
echo "  4. 点击 '持仓记录' 标签"
echo ""
echo "  5. 验证:"
echo "     • 无 '加载持仓历史失败' 错误"
echo "     • 持仓历史数据正常显示"
echo "     • Console (F12) 无错误"
echo ""

echo -e "${YELLOW}🔍 手动测试 API:${NC}"
echo ""
echo "  # 1. 登录获取 token"
echo "  TOKEN=\$(curl -s -X POST http://localhost:8000/api/auth/login \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"username\":\"admin\",\"password\":\"admin123\"}' \\"
echo "    | grep -o '\"accessToken\":\"[^\"]*' | cut -d'\"' -f4)"
echo ""
echo "  # 2. 测试持仓历史端点"
echo "  curl -X GET http://localhost:8000/api/positions/history \\"
echo "    -H \"Authorization: Bearer \$TOKEN\" | python3 -m json.tool"
echo ""

echo -e "${GREEN}📝 预期结果:${NC}"
echo "  {"
echo "    \"positions\": [...],"
echo "    \"total\": N,"
echo "    \"page\": 1,"
echo "    \"pageSize\": 100"
echo "  }"
echo ""

echo -e "${CYAN}🔍 查看日志:${NC}"
echo "  tail -f logs/web_backend.log"
echo ""

