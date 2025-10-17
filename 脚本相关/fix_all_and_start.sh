#!/bin/bash

###############################################################################
# 一键修复所有问题并启动服务
###############################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

echo ""
echo "=========================================================="
echo -e "${MAGENTA}  Lighter 量化交易系统 - 一键修复并启动${NC}"
echo "=========================================================="
echo ""

# 步骤1: 停止现有服务
echo -e "${CYAN}▶ 步骤1: 停止现有服务${NC}"
if [ -f "stop_all_services.sh" ]; then
    ./stop_all_services.sh 2>/dev/null || true
    echo -e "${GREEN}✓ 服务已停止${NC}"
else
    echo -e "${YELLOW}⚠ 未找到停止脚本，跳过${NC}"
fi
echo ""

# 步骤2: 安装缺失的依赖
echo -e "${CYAN}▶ 步骤2: 安装缺失的依赖${NC}"
chmod +x install_missing_deps.sh 2>/dev/null || true

if [ -f "install_missing_deps.sh" ]; then
    ./install_missing_deps.sh
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ 依赖安装失败${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ 未找到依赖安装脚本，手动安装...${NC}"
    source venv/bin/activate
    pip install email-validator pydantic[email] bcrypt passlib -q
    deactivate
    echo -e "${GREEN}✓ 依赖已安装${NC}"
fi
echo ""

# 步骤3: 测试密码哈希
echo -e "${CYAN}▶ 步骤3: 测试密码哈希功能${NC}"
if [ -f "quick_test_hash.py" ]; then
    source venv/bin/activate
    python3 quick_test_hash.py
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ 密码哈希测试失败${NC}"
        deactivate
        exit 1
    fi
    deactivate
    echo -e "${GREEN}✓ 密码哈希功能正常${NC}"
else
    echo -e "${YELLOW}⚠ 未找到测试脚本，跳过${NC}"
fi
echo ""

# 步骤4: 清理旧数据库
echo -e "${CYAN}▶ 步骤4: 清理旧数据库${NC}"
if [ -d "data" ]; then
    rm -f data/*.db 2>/dev/null || true
    echo -e "${GREEN}✓ 旧数据库已清理${NC}"
else
    mkdir -p data
    echo -e "${GREEN}✓ 数据目录已创建${NC}"
fi
echo ""

# 步骤5: 创建必要目录
echo -e "${CYAN}▶ 步骤5: 创建必要目录${NC}"
mkdir -p logs backups
echo -e "${GREEN}✓ 目录已创建${NC}"
echo ""

# 步骤6: 启动服务
echo -e "${CYAN}▶ 步骤6: 启动服务${NC}"
if [ -f "start_all_services.sh" ]; then
    chmod +x start_all_services.sh
    ./start_all_services.sh
else
    echo -e "${RED}✗ 未找到启动脚本${NC}"
    exit 1
fi
echo ""

# 最终提示
echo "=========================================================="
echo -e "${GREEN}🎉 启动完成！${NC}"
echo "=========================================================="
echo ""
echo -e "${CYAN}访问信息:${NC}"
echo "  🌐 Web前端: http://localhost:3000"
echo "  🔌 Web后端: http://localhost:8000"
echo "  📖 API文档: http://localhost:8000/docs"
echo ""
echo -e "${CYAN}登录凭据:${NC}"
echo "  👤 用户名: admin"
echo "  🔑 密码:   admin123"
echo ""
echo -e "${YELLOW}⚠️  首次登录后请立即修改密码！${NC}"
echo ""
echo -e "${CYAN}查看日志:${NC}"
echo "  tail -f logs/backend.log"
echo "  tail -f logs/frontend.log"
echo ""
echo "=========================================================="

