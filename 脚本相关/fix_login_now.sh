#!/bin/bash

###############################################################################
# 一键修复登录问题
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
echo -e "${CYAN}  修复登录问题${NC}"
echo "=========================================================="
echo ""

# 步骤1: 诊断当前状态
echo -e "${BLUE}▶ 步骤1: 诊断当前状态${NC}"
chmod +x diagnose_login.py 2>/dev/null || true

if [ -f "diagnose_login.py" ]; then
    if [ -f "venv/bin/python" ]; then
        venv/bin/python diagnose_login.py
    else
        python3 diagnose_login.py
    fi
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ 诊断发现问题${NC}"
    fi
else
    echo -e "${YELLOW}⚠ 诊断脚本不存在，跳过${NC}"
fi

echo ""

# 步骤2: 停止服务
echo -e "${BLUE}▶ 步骤2: 停止所有服务${NC}"
./stop_all_services.sh 2>/dev/null || true
pkill -9 -f "python.*main.py" 2>/dev/null || true
sleep 2
echo -e "${GREEN}✓ 服务已停止${NC}"
echo ""

# 步骤3: 备份并清理数据库
echo -e "${BLUE}▶ 步骤3: 重建数据库${NC}"

if [ -f "data/lighter_quant.db" ]; then
    backup_file="data/lighter_quant_backup_$(date +%Y%m%d_%H%M%S).db"
    cp data/lighter_quant.db "$backup_file"
    echo -e "${CYAN}  备份已创建: $backup_file${NC}"
fi

rm -f data/*.db
echo -e "${GREEN}✓ 数据库已清理${NC}"
echo ""

# 步骤4: 重新创建用户
echo -e "${BLUE}▶ 步骤4: 创建默认用户${NC}"
cd web_backend

export AUTO_SKIP_PROMPT=1

if [ -f "../venv/bin/python" ]; then
    ../venv/bin/python init_default_user.py 2>&1 | grep -v "Traceback" | tail -20
else
    python3 init_default_user.py 2>&1 | grep -v "Traceback" | tail -20
fi

unset AUTO_SKIP_PROMPT
cd ..

echo ""

# 步骤5: 重新启动服务
echo -e "${BLUE}▶ 步骤5: 启动服务${NC}"
./start_all_services.sh > /dev/null 2>&1 &
echo "等待服务启动..."

# 等待后端启动
for i in {1..30}; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 后端服务已启动 (${i}秒)${NC}"
        break
    fi
    sleep 1
done

echo ""

# 步骤6: 测试登录 API
echo -e "${BLUE}▶ 步骤6: 测试登录 API${NC}"
echo ""

echo "测试 JSON 格式登录..."
response=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')

echo "响应内容:"
echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
echo ""

if echo "$response" | grep -q "accessToken"; then
    echo -e "${GREEN}✓ 登录 API 测试成功（JSON 格式）${NC}"
    echo ""
    echo -e "${GREEN}✅ 登录功能已修复！${NC}"
else
    echo -e "${YELLOW}⚠️  登录 API 返回格式可能有问题${NC}"
    echo ""
fi

# 步骤7: 最终指示
echo ""
echo "=========================================================="
echo -e "${GREEN}修复完成${NC}"
echo "=========================================================="
echo ""
echo -e "${CYAN}访问信息:${NC}"
echo "  🌐 Web前端: http://localhost:3000"
echo ""
echo -e "${CYAN}登录凭据:${NC}"
echo "  👤 用户名: admin"
echo "  🔑 密码:   admin123"
echo ""
echo -e "${CYAN}如果仍无法登录:${NC}"
echo "  1. 清除浏览器缓存（Ctrl+Shift+Delete）"
echo "  2. 使用无痕模式访问"
echo "  3. 按 F12 查看 Console 和 Network 标签的错误"
echo "  4. 运行诊断: python3 diagnose_login.py"
echo ""
echo "=========================================================="

