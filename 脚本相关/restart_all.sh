#!/bin/bash
# Lighter 量化交易系统 - 重启所有服务

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    Lighter 量化交易系统 - 重启所有服务                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 停止服务
echo -e "${CYAN}正在停止服务...${NC}"
./stop_all.sh

# 等待
echo ""
echo -e "${CYAN}等待 3 秒...${NC}"
sleep 3

# 启动服务
echo ""
echo -e "${CYAN}正在启动服务...${NC}"
echo ""
./start_all.sh
