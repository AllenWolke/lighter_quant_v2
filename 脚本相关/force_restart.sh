#!/bin/bash

###############################################################################
# 强制重启所有服务
# 终止挂起进程 → (可选)清理数据库 → 重新启动
# 
# 使用方法:
#   ./force_restart.sh              # 保留数据库（默认）
#   ./force_restart.sh --clean-db   # 清理数据库
###############################################################################

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# 解析命令行参数
CLEAN_DB=false
if [ "$1" == "--clean-db" ] || [ "$1" == "-c" ]; then
    CLEAN_DB=true
fi

echo ""
echo "=========================================================="
echo -e "${CYAN}  Lighter 量化交易系统 - 强制重启${NC}"
if [ "$CLEAN_DB" == "true" ]; then
    echo -e "${YELLOW}  ⚠️  数据库清理模式（将删除所有用户数据）${NC}"
else
    echo -e "${GREEN}  ✓ 保留数据模式（保留所有用户数据）${NC}"
fi
echo "=========================================================="
echo ""

# 步骤1: 终止所有挂起的进程
echo -e "${BLUE}▶ 步骤1: 终止挂起的进程${NC}"

# 查找挂起的进程
hanging_pids=$(ps aux | grep -E "init_default_user|python.*main.py" | grep -v grep | awk '{print $2}')

if [ -z "$hanging_pids" ]; then
    echo -e "${GREEN}✓ 没有发现挂起的进程${NC}"
else
    echo "发现以下挂起的进程:"
    ps aux | grep -E "init_default_user|python.*main.py" | grep -v grep
    echo ""
    for pid in $hanging_pids; do
        kill -9 $pid 2>/dev/null && echo -e "${GREEN}✓ 已终止进程 $pid${NC}"
    done
fi

# 额外清理
pkill -9 -f "init_default_user" 2>/dev/null || true
pkill -9 -f "python.*main.py" 2>/dev/null || true
pkill -9 -f "npm start" 2>/dev/null || true

echo -e "${GREEN}✓ 进程清理完成${NC}"
echo ""

# 步骤2: 等待进程完全退出
echo -e "${BLUE}▶ 步骤2: 等待进程退出${NC}"
sleep 3
echo -e "${GREEN}✓ 等待完成${NC}"
echo ""

# 步骤3: 停止所有服务
echo -e "${BLUE}▶ 步骤3: 停止所有服务${NC}"
if [ -f "stop_all_services.sh" ]; then
    ./stop_all_services.sh 2>/dev/null || true
    echo -e "${GREEN}✓ 服务已停止${NC}"
else
    echo -e "${YELLOW}⚠ 未找到停止脚本，跳过${NC}"
fi
echo ""

# 步骤4: 处理数据库
echo -e "${BLUE}▶ 步骤4: 处理数据库${NC}"

if [ "$CLEAN_DB" == "true" ]; then
    # 清理模式：删除数据库
    echo -e "${YELLOW}⚠️  清理数据库模式${NC}"
    
    # 备份数据库（如果存在）
    if [ -f "data/lighter_quant.db" ]; then
        backup_name="data/lighter_quant_backup_$(date +%Y%m%d_%H%M%S).db"
        cp data/lighter_quant.db "$backup_name" 2>/dev/null || true
        echo -e "${CYAN}  备份已创建: $backup_name${NC}"
    fi
    
    # 删除数据库
    rm -f data/*.db 2>/dev/null || true
    echo -e "${GREEN}✓ 数据库已清理${NC}"
    echo "   启动时会创建全新的用户"
else
    # 保留模式：不删除数据库
    echo -e "${GREEN}✓ 保留数据库模式${NC}"
    echo "   用户数据将被保留"
    
    # 确保数据目录存在
    mkdir -p data
fi

echo ""

# 步骤5: 清理 PID 文件
echo -e "${BLUE}▶ 步骤5: 清理 PID 文件${NC}"
rm -f logs/*.pid 2>/dev/null || true
echo -e "${GREEN}✓ PID 文件已清理${NC}"
echo ""

# 步骤6: 释放端口
echo -e "${BLUE}▶ 步骤6: 释放端口${NC}"
if command -v fuser &> /dev/null; then
    fuser -k 3000/tcp 2>/dev/null || true
    fuser -k 8000/tcp 2>/dev/null || true
    echo -e "${GREEN}✓ 端口已释放${NC}"
else
    echo -e "${YELLOW}⚠ fuser 命令不可用，跳过端口释放${NC}"
fi
echo ""

# 步骤7: 等待端口释放
echo -e "${BLUE}▶ 步骤7: 等待端口释放${NC}"
sleep 2
echo -e "${GREEN}✓ 等待完成${NC}"
echo ""

# 步骤8: 手动创建默认用户（确保用户存在）
echo -e "${BLUE}▶ 步骤8: 创建默认管理员用户${NC}"
if [ -f "web_backend/init_default_user.py" ]; then
    cd web_backend
    export AUTO_SKIP_PROMPT=1
    if [ -f "../venv/bin/python" ]; then
        ../venv/bin/python init_default_user.py 2>&1 | grep -E "创建成功|已存在|✓|✗"
    else
        python3 init_default_user.py 2>&1 | grep -E "创建成功|已存在|✓|✗"
    fi
    unset AUTO_SKIP_PROMPT
    cd ..
    echo -e "${GREEN}✓ 用户初始化完成${NC}"
else
    echo -e "${YELLOW}⚠ 未找到用户初始化脚本${NC}"
fi
echo ""

# 步骤9: 启动服务
echo -e "${BLUE}▶ 步骤9: 启动服务${NC}"
if [ -f "start_all_services.sh" ]; then
    chmod +x start_all_services.sh
    ./start_all_services.sh
else
    echo -e "${RED}✗ 未找到启动脚本${NC}"
    exit 1
fi

# 最终提示
echo ""
echo "=========================================================="
echo -e "${GREEN}🎉 强制重启完成！${NC}"
echo "=========================================================="
echo ""

if [ "$CLEAN_DB" == "true" ]; then
    echo -e "${YELLOW}⚠️  数据库已清理，使用默认凭据${NC}"
    echo ""
    echo -e "${CYAN}登录凭据:${NC}"
    echo "  👤 用户名: admin"
    echo "  🔑 密码:   admin123"
    echo ""
    echo -e "${YELLOW}⚠️  首次登录后请立即修改密码！${NC}"
else
    echo -e "${GREEN}✓ 数据库已保留，使用您之前的凭据登录${NC}"
    echo ""
    echo -e "${CYAN}提示:${NC}"
    echo "  如果是首次部署，默认凭据为:"
    echo "  👤 用户名: admin"
    echo "  🔑 密码:   admin123"
fi

echo ""
echo -e "${CYAN}访问信息:${NC}"
echo "  🌐 Web前端: http://localhost:3000"
echo "  🔌 Web后端: http://localhost:8000"
echo "  📖 API文档: http://localhost:8000/docs"
echo ""
echo -e "${CYAN}查看日志:${NC}"
echo "  tail -f logs/backend.log"
echo "  tail -f logs/frontend.log"
echo ""
echo -e "${CYAN}使用说明:${NC}"
echo "  保留数据重启: ${GREEN}./force_restart.sh${NC}"
echo "  清理数据重启: ${YELLOW}./force_restart.sh --clean-db${NC}"
echo ""
echo "=========================================================="

