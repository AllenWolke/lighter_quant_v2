#!/bin/bash
# 测试真实持仓数据 - 重启后端服务

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

clear

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     测试真实持仓数据 - 重启后端服务                       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${CYAN}🎯 本脚本将:${NC}"
echo "  1. 停止后端服务"
echo "  2. 清理缓存"
echo "  3. 重启后端服务"
echo "  4. 测试持仓数据端点"
echo ""

read -p "按 Enter 继续..." 

PYTHON_CMD="python3"
command -v python3 &> /dev/null || PYTHON_CMD="python"

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  [1/4] 停止后端服务"
echo "════════════════════════════════════════════════════════════"
echo ""

pkill -f "uvicorn.*main:app" 2>/dev/null && echo -e "${GREEN}  ✓ 已停止后端服务${NC}" || echo "  ✓ 后端未运行"
sleep 2
echo ""

echo "════════════════════════════════════════════════════════════"
echo "  [2/4] 清理缓存"
echo "════════════════════════════════════════════════════════════"
echo ""

find web_backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
echo -e "${GREEN}  ✓ 已清理 Python 缓存${NC}"
echo ""

echo "════════════════════════════════════════════════════════════"
echo "  [3/4] 启动后端服务"
echo "════════════════════════════════════════════════════════════"
echo ""

cd web_backend
nohup $PYTHON_CMD -m uvicorn main:app --host 0.0.0.0 --port 8000 > ../logs/web_backend.log 2>&1 &
BACKEND_PID=$!
cd ..

echo "  等待后端启动 (15秒)..."
sleep 15
echo ""

echo "════════════════════════════════════════════════════════════"
echo "  [4/4] 测试持仓数据端点"
echo "════════════════════════════════════════════════════════════"
echo ""

# 获取 token
echo "  正在登录..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin123"}')

if echo "$LOGIN_RESPONSE" | grep -q "accessToken"; then
    echo -e "${GREEN}  ✓ 登录成功${NC}"
    echo ""
    
    # 提取 token
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"accessToken":"[^"]*' | cut -d'"' -f4)
    
    # 测试 /api/trading/positions
    echo -e "${CYAN}  测试 1: GET /api/trading/positions${NC}"
    echo "  ----------------------------------------"
    curl -s -X GET http://localhost:8000/api/trading/positions \
        -H "Authorization: Bearer $TOKEN" | python3 -m json.tool 2>/dev/null || echo "  (解析失败，查看原始响应)"
    echo ""
    echo ""
    
    # 测试 /api/positions/history
    echo -e "${CYAN}  测试 2: GET /api/positions/history${NC}"
    echo "  ----------------------------------------"
    curl -s -X GET http://localhost:8000/api/positions/history \
        -H "Authorization: Bearer $TOKEN" | python3 -m json.tool 2>/dev/null || echo "  (解析失败，查看原始响应)"
    echo ""
    
else
    echo -e "${RED}  ✗ 登录失败${NC}"
    echo "  响应: $LOGIN_RESPONSE"
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  完成"
echo "════════════════════════════════════════════════════════════"
echo ""

echo -e "${YELLOW}📝 说明:${NC}"
echo ""
echo "  • 如果看到真实持仓数据，说明集成成功"
echo "  • 如果返回空列表 []，说明账户当前没有持仓"
echo "  • 如果返回模拟数据，说明 Lighter API 调用失败"
echo ""
echo -e "${CYAN}🔍 查看详细日志:${NC}"
echo "  tail -f logs/web_backend.log"
echo ""
echo -e "${CYAN}🌐 在浏览器中测试:${NC}"
echo "  1. 访问 http://localhost:3000"
echo "  2. 登录: admin / admin123"
echo "  3. 访问 Positions 页面"
echo "  4. 访问 History 页面 → 持仓记录标签"
echo ""
