#!/bin/bash
# WSL Ubuntu 量化交易系统重启脚本

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    Lighter 量化交易系统 - 重启服务                        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 停止服务
echo -e "${GREEN}正在停止服务...${NC}"
./stop_system_wsl.sh

# 等待
echo ""
echo -e "${GREEN}等待 3 秒...${NC}"
sleep 3

# 启动服务
echo ""
echo -e "${GREEN}正在启动服务...${NC}"
echo ""
./start_system_wsl.sh

