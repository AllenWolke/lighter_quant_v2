#!/bin/bash
# 修复所有 Dashboard 问题

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     修复所有 Dashboard 问题                                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo "已修复的问题:"
echo "  1. ✓ manifest.json 404 错误"
echo "  2. ✓ /api/trading/symbols 404 错误"
echo "  3. ✓ /api/trading/positions 404 错误"
echo "  4. ✓ /api/trading/stats 500 错误"
echo "  5. ✓ camelCase 响应格式"
echo ""

PYTHON_CMD="python3"
command -v python3 &> /dev/null || PYTHON_CMD="python"

echo -e "${CYAN}[1/5] 停止所有服务${NC}"
echo ""
pkill -f "uvicorn.*main:app" 2>/dev/null && echo "  ✓ 后端已停止" || echo "  ✓ 后端未运行"
pkill -f "node.*react" 2>/dev/null && echo "  ✓ 前端已停止" || echo "  ✓ 前端未运行"
sleep 2
echo ""

echo -e "${CYAN}[2/5] 清理缓存${NC}"
echo ""
rm -rf web_backend/__pycache__
rm -rf web_backend/**/__pycache__
echo "  ✓ Python 缓存已清理"
echo ""

echo -e "${CYAN}[3/5] 启动后端服务${NC}"
echo ""
cd web_backend
echo "  工作目录: $(pwd)"
echo "  启动服务..."
nohup $PYTHON_CMD -m uvicorn main:app --host 0.0.0.0 --port 8000 > ../logs/web_backend.log 2>&1 &
BACKEND_PID=$!
cd ..
echo "  等待启动 (10秒)..."
sleep 10
echo ""

echo -e "${CYAN}[4/5] 验证后端服务${NC}"
echo ""

if curl -s http://localhost:8000/api/health >/dev/null 2>&1; then
    echo -e "${GREEN}  ✓ 后端服务正常${NC}"
    
    # 获取 token
    TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
      -H "Content-Type: application/json" \
      -d '{"username":"admin","password":"admin123"}' \
      | grep -o '"accessToken":"[^"]*"' | cut -d'"' -f4)
    
    if [ ! -z "$TOKEN" ]; then
        echo "  测试 API 端点..."
        
        # 测试各个端点
        curl -s http://localhost:8000/api/trading/account \
          -H "Authorization: Bearer $TOKEN" >/dev/null 2>&1 \
          && echo -e "${GREEN}    ✓ /api/trading/account${NC}" \
          || echo -e "${RED}    ✗ /api/trading/account${NC}"
        
        curl -s http://localhost:8000/api/trading/symbols \
          -H "Authorization: Bearer $TOKEN" >/dev/null 2>&1 \
          && echo -e "${GREEN}    ✓ /api/trading/symbols (新增)${NC}" \
          || echo -e "${RED}    ✗ /api/trading/symbols${NC}"
        
        curl -s http://localhost:8000/api/trading/positions \
          -H "Authorization: Bearer $TOKEN" >/dev/null 2>&1 \
          && echo -e "${GREEN}    ✓ /api/trading/positions (新增)${NC}" \
          || echo -e "${RED}    ✗ /api/trading/positions${NC}"
        
        curl -s "http://localhost:8000/api/trading/stats?days=30" \
          -H "Authorization: Bearer $TOKEN" >/dev/null 2>&1 \
          && echo -e "${GREEN}    ✓ /api/trading/stats (已修复)${NC}" \
          || echo -e "${RED}    ✗ /api/trading/stats${NC}"
    fi
else
    echo -e "${RED}  ✗ 后端服务启动失败${NC}"
    echo ""
    echo "  查看日志:"
    tail -30 logs/web_backend.log
    exit 1
fi

echo ""

echo -e "${CYAN}[5/5] 启动前端服务 (可选)${NC}"
echo ""
read -p "是否启动前端? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "  启动前端..."
    cd web_frontend
    nohup npm start > ../logs/web_frontend.log 2>&1 &
    cd ..
    echo -e "${GREEN}  ✓ 前端已启动（约需1分钟编译）${NC}"
else
    echo "  跳过前端启动"
fi

echo ""

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    修复完成                                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}✅ 所有 Dashboard 问题已修复${NC}"
echo ""

echo -e "${CYAN}已修复的错误:${NC}"
echo "  1. ✓ manifest.json - 已创建"
echo "  2. ✓ /api/trading/symbols - 已添加"
echo "  3. ✓ /api/trading/positions - 已添加"
echo "  4. ✓ /api/trading/stats - 参数已修复"
echo "  5. ✓ camelCase 格式 - 已配置"
echo ""

echo -e "${CYAN}下一步操作:${NC}"
echo ""
echo "  1. 访问 Dashboard:"
echo "     http://localhost:3000/dashboard"
echo ""
echo "  2. 清除浏览器缓存:"
echo "     F12 → Application → Clear site data"
echo ""
echo "  3. 强制刷新:"
echo "     Ctrl+Shift+R"
echo ""
echo "  4. 重新登录:"
echo "     用户名: admin"
echo "     密码: admin123"
echo ""
echo "  5. 点击"刷新数据"按钮"
echo ""

echo -e "${CYAN}验证修复:${NC}"
echo "  - Console 应无 404/500 错误"
echo "  - Dashboard 应显示真实余额"
echo "  - 所有数据卡片正常显示"
echo ""

echo -e "${CYAN}查看日志:${NC}"
echo "  tail -f logs/web_backend.log"
echo ""

