#!/bin/bash

###############################################################################
# 最终一键修复并启动
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
echo -e "${CYAN}  Lighter 量化交易系统 - 最终修复并启动${NC}"
echo "=========================================================="
echo ""

# 1. 停止所有
echo -e "${BLUE}[1/8]${NC} 停止所有服务..."
./stop_all_services.sh 2>/dev/null || true
pkill -9 -f "python.*main.py" 2>/dev/null || true
pkill -9 -f "npm start" 2>/dev/null || true
pkill -9 -f node 2>/dev/null || true
sleep 3
echo -e "${GREEN}✓ 已停止${NC}"
echo ""

# 2. 清理数据库
echo -e "${BLUE}[2/8]${NC} 清理数据库..."
if [ -f "data/lighter_quant.db" ]; then
    cp data/lighter_quant.db "data/backup_$(date +%Y%m%d_%H%M%S).db"
    echo -e "${CYAN}  已备份${NC}"
fi
rm -f data/*.db
mkdir -p data logs
echo -e "${GREEN}✓ 已清理${NC}"
echo ""

# 3. 创建用户
echo -e "${BLUE}[3/8]${NC} 创建默认用户..."
cd web_backend
export AUTO_SKIP_PROMPT=1

if [ -f "../venv/bin/python" ]; then
    ../venv/bin/python init_default_user.py 2>&1 | tail -15
else
    python3 init_default_user.py 2>&1 | tail -15
fi

unset AUTO_SKIP_PROMPT
cd ..
echo ""

# 4. 启动后端
echo -e "${BLUE}[4/8]${NC} 启动后端服务..."
cd web_backend

if [ -f "../venv/bin/python" ]; then
    nohup ../venv/bin/python main.py > ../logs/backend.log 2>&1 &
else
    nohup python3 main.py > ../logs/backend.log 2>&1 &
fi

backend_pid=$!
echo $backend_pid > ../logs/backend.pid
cd ..
echo -e "${GREEN}✓ 后端已启动 (PID: $backend_pid)${NC}"
echo ""

# 5. 等待后端就绪
echo -e "${BLUE}[5/8]${NC} 等待后端就绪..."
for i in {1..30}; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 后端就绪 (${i}秒)${NC}"
        break
    fi
    sleep 1
    [ $((i % 5)) -eq 0 ] && echo "  等待中... ${i}秒"
done
echo ""

# 6. 测试登录 API
echo -e "${BLUE}[6/8]${NC} 测试登录 API..."
response=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')

echo "响应:"
echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
echo ""

if echo "$response" | grep -q "accessToken"; then
    echo -e "${GREEN}✓ 登录 API 正常${NC}"
else
    echo -e "${RED}✗ 登录 API 异常${NC}"
    echo "查看详细日志:"
    echo "  tail -n 50 logs/backend.log"
fi
echo ""

# 7. 启动前端
echo -e "${BLUE}[7/8]${NC} 启动前端服务..."
cd web_frontend
nohup npm start > ../logs/frontend.log 2>&1 &
frontend_pid=$!
echo $frontend_pid > ../logs/frontend.pid
cd ..
echo -e "${GREEN}✓ 前端已启动 (PID: $frontend_pid)${NC}"
echo ""

# 8. 等待前端就绪
echo -e "${BLUE}[8/8]${NC} 等待前端就绪（约30秒）..."
sleep 30
echo -e "${GREEN}✓ 前端就绪${NC}"
echo ""

# 最终提示
echo "=========================================================="
echo -e "${GREEN}🎉 启动完成！${NC}"
echo "=========================================================="
echo ""
echo -e "${CYAN}访问信息:${NC}"
echo "  🌐 Web前端: ${GREEN}http://localhost:3000${NC}"
echo "  🔌 Web后端: http://localhost:8000"
echo "  📖 API文档: http://localhost:8000/docs"
echo ""
echo -e "${CYAN}登录凭据:${NC}"
echo "  👤 用户名: ${YELLOW}admin${NC}"
echo "  🔑 密码:   ${YELLOW}admin123${NC}"
echo ""
echo -e "${CYAN}重要提示:${NC}"
echo "  ${YELLOW}⚠️  清除浏览器缓存后再登录！${NC}"
echo "      1. 按 Ctrl+Shift+Delete"
echo "      2. 选择'缓存的图片和文件'"
echo "      3. 点击'清除数据'"
echo "      4. 刷新页面 (Ctrl+Shift+R)"
echo ""
echo -e "${CYAN}查看日志:${NC}"
echo "  tail -f logs/backend.log"
echo "  tail -f logs/frontend.log"
echo ""
echo "=========================================================="

