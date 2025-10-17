#!/bin/bash
# WebSocket 修复和重启脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     WebSocket 连接修复和服务重启工具                      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 步骤1: 停止现有服务
echo -e "${CYAN}[步骤 1/5] 停止现有服务${NC}"

# 停止 web 后端
echo -e "  停止 Web 后端..."
pkill -f "uvicorn.*main:app" || true
pkill -f "python.*web_backend" || true

# 等待进程完全停止
sleep 2

# 验证是否已停止
if pgrep -f "uvicorn.*main:app" > /dev/null; then
    echo -e "${RED}✗ Web 后端仍在运行，强制终止${NC}"
    pkill -9 -f "uvicorn.*main:app" || true
else
    echo -e "${GREEN}✓ Web 后端已停止${NC}"
fi

echo ""

# 步骤2: 检查修复文件
echo -e "${CYAN}[步骤 2/5] 验证修复${NC}"

# 检查 main.py 是否包含修复
if grep -q "client_id = str(uuid.uuid4())" web_backend/main.py; then
    echo -e "${GREEN}✓ WebSocket 修复已应用${NC}"
else
    echo -e "${YELLOW}⚠️ WebSocket 修复可能未完全应用${NC}"
fi

echo ""

# 步骤3: 检查依赖
echo -e "${CYAN}[步骤 3/5] 检查依赖${NC}"

# 智能检测 Python 命令（支持 Windows/Linux/WSL）
if [ -f "venv/bin/python" ]; then
    PYTHON_CMD="venv/bin/python"
    echo -e "${GREEN}✓ 使用虚拟环境 Python (Linux)${NC}"
elif [ -f "venv/Scripts/python.exe" ]; then
    PYTHON_CMD="venv/Scripts/python.exe"
    echo -e "${GREEN}✓ 使用虚拟环境 Python (Windows)${NC}"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo -e "${YELLOW}⚠️ 使用系统 Python3${NC}"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo -e "${YELLOW}⚠️ 使用系统 Python${NC}"
else
    echo -e "${RED}✗ 未找到 Python${NC}"
    echo -e "${RED}请安装 Python 3.9+ 或创建虚拟环境${NC}"
    exit 1
fi

# 检查必要的包
echo -e "  检查 FastAPI..."
$PYTHON_CMD -c "import fastapi" 2>/dev/null && echo -e "${GREEN}  ✓ FastAPI${NC}" || echo -e "${RED}  ✗ FastAPI${NC}"

echo -e "  检查 WebSockets..."
$PYTHON_CMD -c "import websockets" 2>/dev/null && echo -e "${GREEN}  ✓ WebSockets${NC}" || echo -e "${YELLOW}  ⚠️ WebSockets（可选）${NC}"

echo ""

# 步骤4: 启动 Web 后端
echo -e "${CYAN}[步骤 4/5] 启动 Web 后端${NC}"

cd web_backend

# 创建日志目录
mkdir -p ../logs

# 启动后端服务
echo -e "  启动服务..."

# 检测操作系统并使用相应的启动方式
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    # Windows (Git Bash/MSYS)
    echo -e "  检测到 Windows 环境"
    start "" $PYTHON_CMD -m uvicorn main:app --host 0.0.0.0 --port 8000 > ../logs/web_backend.log 2>&1
    BACKEND_PID="Windows"
    sleep 3
else
    # Linux/macOS
    echo -e "  检测到 Linux/macOS 环境"
    if command -v nohup &> /dev/null; then
        nohup $PYTHON_CMD -m uvicorn main:app --host 0.0.0.0 --port 8000 > ../logs/web_backend.log 2>&1 &
        BACKEND_PID=$!
    else
        # 如果没有 nohup，直接后台运行
        $PYTHON_CMD -m uvicorn main:app --host 0.0.0.0 --port 8000 > ../logs/web_backend.log 2>&1 &
        BACKEND_PID=$!
    fi
fi

# 等待服务启动
echo -e "  等待服务启动..."
sleep 5

# 检查服务是否运行
if [[ "$BACKEND_PID" == "Windows" ]]; then
    # Windows: 检查端口
    if netstat -an 2>/dev/null | grep -q ":8000.*LISTENING" || \
       ss -tuln 2>/dev/null | grep -q ":8000"; then
        echo -e "${GREEN}✓ Web 后端已启动${NC}"
    else
        echo -e "${RED}✗ Web 后端启动失败${NC}"
        echo -e "${YELLOW}查看日志: cat ../logs/web_backend.log | tail -20${NC}"
        cd ..
        exit 1
    fi
elif ps -p $BACKEND_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Web 后端已启动 (PID: $BACKEND_PID)${NC}"
else
    echo -e "${RED}✗ Web 后端启动失败${NC}"
    echo -e "${YELLOW}查看日志: tail -20 ../logs/web_backend.log${NC}"
    cd ..
    exit 1
fi

cd ..

echo ""

# 步骤5: 测试 WebSocket 连接
echo -e "${CYAN}[步骤 5/5] 测试 WebSocket 连接${NC}"

sleep 2

# 测试 HTTP 健康检查
echo -e "  测试 HTTP 健康检查..."
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ HTTP 健康检查通过${NC}"
else
    echo -e "${YELLOW}⚠️ HTTP 健康检查失败（可能正在启动）${NC}"
fi

# 测试 WebSocket（使用 Python）
echo -e "  测试 WebSocket 连接..."
$PYTHON_CMD << 'PYTHON_EOF'
import asyncio
import websockets
import json
import sys

async def test_websocket():
    try:
        async with websockets.connect('ws://localhost:8000/ws') as websocket:
            # 发送 ping
            await websocket.send(json.dumps({"type": "ping"}))
            
            # 接收 pong
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            message = json.loads(response)
            
            if message.get('type') == 'pong':
                print("✓ WebSocket 测试成功")
                return True
            else:
                print(f"⚠️ 收到意外响应: {message}")
                return False
                
    except asyncio.TimeoutError:
        print("✗ WebSocket 连接超时")
        return False
    except Exception as e:
        print(f"✗ WebSocket 测试失败: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_websocket())
    sys.exit(0 if result else 1)
PYTHON_EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ WebSocket 连接测试通过${NC}"
else
    echo -e "${YELLOW}⚠️ WebSocket 连接测试失败（需要 websockets 包）${NC}"
    echo -e "${CYAN}  安装: pip install websockets${NC}"
fi

echo ""

# 最终总结
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                     服务重启完成                           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}✅ 服务已重启${NC}"
echo ""

echo -e "${CYAN}服务状态:${NC}"
echo -e "  Web 后端: ${GREEN}http://localhost:8000${NC}"
echo -e "  WebSocket: ${GREEN}ws://localhost:8000/ws${NC}"
echo -e "  API 文档: ${GREEN}http://localhost:8000/api/docs${NC}"
echo ""

echo -e "${CYAN}查看日志:${NC}"
echo -e "  ${YELLOW}tail -f logs/web_backend.log${NC}"
echo ""

echo -e "${CYAN}测试 WebSocket:${NC}"
echo -e "  1. 访问 ${GREEN}http://localhost:3000/trading${NC}"
echo -e "  2. 查看浏览器控制台的 WebSocket 连接状态"
echo -e "  3. 应该显示 ${GREEN}\"WebSocket连接已建立\"${NC}"
echo ""

echo -e "${CYAN}停止服务:${NC}"
echo -e "  ${YELLOW}pkill -f \"uvicorn.*main:app\"${NC}"
echo ""

echo -e "${GREEN}🎉 修复完成！请刷新浏览器页面测试${NC}"

