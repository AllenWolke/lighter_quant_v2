#!/bin/bash
# WSL Ubuntu Web 后端启动脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    启动 Web 后端服务 - WSL Ubuntu                         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 检测 Python 命令
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}✗ 未找到 Python${NC}"
    exit 1
fi

echo -e "${GREEN}[1/6] 检查环境${NC}"
echo ""
echo "Python 命令: $PYTHON_CMD"
$PYTHON_CMD --version
echo ""

# 创建必要目录
echo -e "${GREEN}[2/6] 创建目录${NC}"
mkdir -p logs data backups
echo "✓ 目录已创建"
echo ""

# 停止现有进程
echo -e "${GREEN}[3/6] 停止现有进程${NC}"
pkill -f "uvicorn.*main:app" 2>/dev/null && echo "✓ 已停止现有后端进程" || echo "✓ 无现有进程"
sleep 2
echo ""

# 切换到 web_backend 目录
echo -e "${GREEN}[4/6] 切换到 web_backend 目录${NC}"
cd web_backend

# 验证 main.py 存在
if [ ! -f "main.py" ]; then
    echo -e "${RED}✗ 错误: 找不到 main.py${NC}"
    echo "当前目录: $(pwd)"
    echo "请确保脚本在项目根目录运行"
    exit 1
fi

echo "✓ 找到 main.py"
echo "  路径: $(pwd)/main.py"
echo ""

# 验证 Python 环境
echo -e "${GREEN}[5/6] 验证 Python 环境${NC}"

# 测试导入
if $PYTHON_CMD -c "import main; print('✓ main 模块可以导入'); print('✓ app 对象存在:', hasattr(main, 'app'))" 2>/dev/null; then
    echo "✓ Python 环境验证成功"
else
    echo -e "${RED}✗ Python 环境验证失败${NC}"
    echo ""
    echo "可能的原因:"
    echo "  1. 缺少依赖包"
    echo "  2. main.py 中有错误"
    echo ""
    echo "请运行以下命令检查:"
    echo "  cd web_backend"
    echo "  python3 -c 'import main'"
    echo ""
    exit 1
fi

# 初始化默认用户
if [ -f "init_default_user.py" ]; then
    echo ""
    echo "初始化默认用户..."
    export AUTO_SKIP_PROMPT=1
    $PYTHON_CMD init_default_user.py 2>/dev/null || true
    unset AUTO_SKIP_PROMPT
fi

echo ""

# 启动服务
echo -e "${GREEN}[6/6] 启动后端服务${NC}"
echo ""
echo "启动信息:"
echo "  工作目录: $(pwd)"
echo "  启动命令: $PYTHON_CMD -m uvicorn main:app --host 0.0.0.0 --port 8000"
echo "  日志文件: ../logs/web_backend.log"
echo ""

# 使用 nohup 后台启动
nohup $PYTHON_CMD -m uvicorn main:app --host 0.0.0.0 --port 8000 > ../logs/web_backend.log 2>&1 &
BACKEND_PID=$!

cd ..

# 等待启动
echo "等待服务启动..."
sleep 5

# 检查服务状态
echo ""
echo "检查服务状态..."

if ps -p $BACKEND_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 进程运行中 (PID: $BACKEND_PID)${NC}"
else
    echo -e "${RED}✗ 进程可能已退出${NC}"
    echo ""
    echo "查看日志:"
    tail -20 logs/web_backend.log
    exit 1
fi

# 测试 HTTP 端点
if curl -s http://localhost:8000/api/health >/dev/null 2>&1; then
    echo -e "${GREEN}✓ HTTP 端点响应正常${NC}"
    
    # 显示健康检查响应
    HEALTH=$(curl -s http://localhost:8000/api/health)
    echo "  响应: $HEALTH"
else
    echo -e "${YELLOW}⚠️  HTTP 端点未响应（可能还在启动）${NC}"
    echo ""
    echo "等待 5 秒后重试..."
    sleep 5
    
    if curl -s http://localhost:8000/api/health >/dev/null 2>&1; then
        echo -e "${GREEN}✓ HTTP 端点现在正常${NC}"
    else
        echo -e "${RED}✗ HTTP 端点仍未响应${NC}"
        echo ""
        echo "查看日志:"
        tail -30 logs/web_backend.log
        exit 1
    fi
fi

echo ""

# 成功总结
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                  后端服务启动成功                          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}✓ Web 后端已启动${NC}"
echo ""

echo -e "${CYAN}服务信息:${NC}"
echo "  进程 ID: $BACKEND_PID"
echo "  端口: 8000"
echo "  API 地址: http://localhost:8000"
echo "  API 文档: http://localhost:8000/api/docs"
echo "  健康检查: http://localhost:8000/api/health"
echo ""

echo -e "${CYAN}查看日志:${NC}"
echo "  实时: tail -f logs/web_backend.log"
echo "  最后50行: tail -50 logs/web_backend.log"
echo "  账户相关: tail -f logs/web_backend.log | grep -i 账户"
echo ""

echo -e "${CYAN}停止服务:${NC}"
echo "  pkill -f \"uvicorn.*main:app\""
echo "  或: kill $BACKEND_PID"
echo ""

echo -e "${CYAN}测试账户数据:${NC}"
echo "  ./diagnose_account_balance.sh"
echo ""

echo -e "${GREEN}🎉 启动完成！${NC}"
echo ""
