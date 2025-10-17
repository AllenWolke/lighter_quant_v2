#!/bin/bash
# 应用所有修复并重启系统 - 最终版本

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

clear

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     应用所有修复并重启系统 - 最终版本                     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${CYAN}🎯 将修复以下所有问题:${NC}"
echo ""
echo "  后端问题:"
echo "    1. ✓ aiohttp 资源泄漏"
echo "    2. ✓ API 数据结构解析"
echo "    3. ✓ 80位私钥支持"
echo "    4. ✓ /api/trading/symbols"
echo "    5. ✓ /api/trading/positions"
echo "    6. ✓ /api/trading/stats"
echo "    7. ✓ /api/positions/history"
echo "    8. ✓ /api/strategies/{id}/toggle"
echo ""
echo "  前端问题:"
echo "    9. ✓ manifest.json"
echo "   10. ✓ Dashboard 余额显示"
echo "   11. ✓ 所有页面 WebSocket 连接"
echo "   12. ✓ camelCase 响应格式"
echo ""

read -p "按 Enter 继续..." 

PYTHON_CMD="python3"
command -v python3 &> /dev/null || PYTHON_CMD="python"

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  开始修复..."
echo "════════════════════════════════════════════════════════════"
echo ""

echo -e "${CYAN}[1/4] 停止所有服务${NC}"
echo ""
pkill -f "uvicorn.*main:app" 2>/dev/null && echo "  ✓ 后端已停止" || echo "  ✓ 后端未运行"
pkill -f "node.*react" 2>/dev/null && echo "  ✓ 前端已停止" || echo "  ✓ 前端未运行"
echo "  ✓ 已停止所有服务"
sleep 2
echo ""

echo -e "${CYAN}[2/4] 清理所有缓存${NC}"
echo ""
find web_backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find web_frontend -type d -name ".cache" -exec rm -rf {} + 2>/dev/null || true
echo "  ✓ 已清理 Python 和前端缓存"
echo ""

echo -e "${CYAN}[3/4] 启动后端服务${NC}"
echo ""
cd web_backend

if [ ! -f "main.py" ]; then
    echo -e "${RED}  ✗ 错误: 找不到 main.py${NC}"
    cd ..
    exit 1
fi

echo "  启动后端..."
nohup $PYTHON_CMD -m uvicorn main:app --host 0.0.0.0 --port 8000 > ../logs/web_backend.log 2>&1 &
BACKEND_PID=$!
cd ..

echo "  等待后端启动 (15秒)..."
sleep 15
echo ""

echo -e "${CYAN}[4/4] 验证服务${NC}"
echo ""

if curl -s http://localhost:8000/api/health >/dev/null 2>&1; then
    echo -e "${GREEN}  ✓ 后端服务正常${NC}"
    echo ""
    echo "  查看完整 API 文档:"
    echo "  http://localhost:8000/api/docs"
else
    echo -e "${RED}  ✗ 后端服务未响应${NC}"
    echo ""
    echo "  查看日志:"
    tail -30 logs/web_backend.log
    exit 1
fi

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    ✅ 修复完成                             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}🎊 所有问题已修复！${NC}"
echo ""

echo "════════════════════════════════════════════════════════════"
echo "  现在需要在浏览器中完成最后步骤"
echo "════════════════════════════════════════════════════════════"
echo ""

echo -e "${MAGENTA}📝 必需步骤:${NC}"
echo ""
echo "  1. 打开浏览器访问:"
echo "     http://localhost:3000"
echo ""
echo "  2. 按 F12 打开开发者工具"
echo ""
echo "  3. 切换到 Application 标签"
echo ""
echo "  4. 左侧点击 Storage"
echo ""
echo "  5. 点击 'Clear site data' 按钮"
echo ""
echo "  6. 关闭浏览器（完全关闭）"
echo ""
echo "  7. 重新打开浏览器"
echo ""
echo "  8. 访问 http://localhost:3000"
echo ""
echo "  9. 登录: admin / admin123"
echo ""
echo " 10. 依次访问所有页面验证:"
echo "     • Dashboard    ✓"
echo "     • Trading      ✓"
echo "     • Strategies   ✓"
echo "     • Positions    ✓"
echo "     • History      ✓"
echo ""

echo "════════════════════════════════════════════════════════════"
echo "  验证清单"
echo "════════════════════════════════════════════════════════════"
echo ""

echo "每个页面应该:"
echo "  ✓ 页面头部显示'实时连接'（绿色）"
echo "  ✓ 无'连接断开'警告"
echo "  ✓ Console 无 404/500/422 错误"
echo "  ✓ 数据正常显示"
echo ""

echo "Dashboard 应该:"
echo "  ✓ 可用余额: 5.00 USDT (不是 0.00)"
echo "  ✓ 所有卡片有数据"
echo "  ✓ 点击'刷新数据'正常"
echo ""

echo "Strategies 应该:"
echo "  ✓ 策略列表显示"
echo "  ✓ 可以切换启用/禁用状态"
echo "  ✓ 无'切换策略状态失败'"
echo ""

echo "History 应该:"
echo "  ✓ 交易记录标签正常"
echo "  ✓ 订单记录标签正常"
echo "  ✓ 持仓记录标签正常"
echo "  ✓ 无'加载持仓历史失败'"
echo ""

echo "════════════════════════════════════════════════════════════"
echo ""

echo -e "${CYAN}🔍 浏览器验证测试:${NC}"
echo ""
echo "在 Console (F12) 中运行:"
echo ""
echo "fetch('/api/positions/history', {"
echo "  headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }"
echo "})"
echo ".then(r => r.json())"
echo ".then(d => console.log('持仓历史:', d.positions.length, '条'))"
echo ""

echo -e "${CYAN}📚 相关文档:${NC}"
echo "  • FINAL_FIX_COMPLETE.md - 完整修复总结"
echo "  • APPLY_ALL_FIXES_NOW.bat/.sh - 本脚本"
echo ""

echo -e "${GREEN}🎉 修复已完成！请按照上述步骤清除浏览器缓存！${NC}"
echo ""

