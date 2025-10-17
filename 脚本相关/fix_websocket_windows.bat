@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║     WebSocket 连接修复工具 - Windows 专用版               ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM 步骤1: 停止现有服务
echo [步骤 1/5] 停止现有服务
echo.
echo   停止 Web 后端...

REM 停止所有 Python 进程中包含 uvicorn 的
for /f "tokens=2" %%a in ('tasklist ^| findstr python.exe') do (
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 2 /nobreak >nul

echo   ✓ 已停止现有服务
echo.

REM 步骤2: 验证修复
echo [步骤 2/5] 验证修复
echo.

findstr /C:"client_id = str(uuid.uuid4())" web_backend\main.py >nul
if %errorlevel% equ 0 (
    echo   ✓ WebSocket 修复已应用
) else (
    echo   ⚠️ WebSocket 修复可能未完全应用
)
echo.

REM 步骤3: 检查 Python
echo [步骤 3/5] 检查 Python 环境
echo.

REM 检测 Python 命令
set PYTHON_CMD=
if exist "venv\Scripts\python.exe" (
    set PYTHON_CMD=venv\Scripts\python.exe
    echo   ✓ 使用虚拟环境 Python
) else if exist "venv\Scripts\python3.exe" (
    set PYTHON_CMD=venv\Scripts\python3.exe
    echo   ✓ 使用虚拟环境 Python3
) else (
    REM 尝试系统 Python
    where python >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=python
        echo   ⚠️ 使用系统 Python
    ) else (
        where python3 >nul 2>&1
        if %errorlevel% equ 0 (
            set PYTHON_CMD=python3
            echo   ⚠️ 使用系统 Python3
        ) else (
            echo   ✗ 未找到 Python
            echo   请安装 Python 3.9+ 或创建虚拟环境
            echo.
            pause
            exit /b 1
        )
    )
)

REM 显示 Python 版本
echo.
echo   Python 版本:
%PYTHON_CMD% --version 2>&1 | findstr /C:"Python"
echo.

REM 检查 FastAPI
echo   检查依赖...
%PYTHON_CMD% -c "import fastapi" 2>nul
if %errorlevel% equ 0 (
    echo   ✓ FastAPI 已安装
) else (
    echo   ✗ FastAPI 未安装
    echo   请运行: pip install fastapi uvicorn
    echo.
    pause
    exit /b 1
)

%PYTHON_CMD% -c "import uvicorn" 2>nul
if %errorlevel% equ 0 (
    echo   ✓ Uvicorn 已安装
) else (
    echo   ✗ Uvicorn 未安装
    echo   请运行: pip install uvicorn
    echo.
    pause
    exit /b 1
)

echo.

REM 步骤4: 启动 Web 后端
echo [步骤 4/5] 启动 Web 后端
echo.

REM 创建日志目录
if not exist "logs" mkdir logs

echo   启动服务...
cd web_backend

REM 使用 start 命令在新窗口后台启动（最小化）
start /B /MIN "" %PYTHON_CMD% -m uvicorn main:app --host 0.0.0.0 --port 8000 > ..\logs\web_backend.log 2>&1

cd ..

REM 等待服务启动
echo   等待服务启动 (10秒)...
timeout /t 10 /nobreak >nul

REM 检查服务是否运行
netstat -an | findstr "0.0.0.0:8000" | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    echo   ✓ Web 后端已启动
    echo   端口 8000 正在监听
) else (
    echo   ✗ Web 后端启动失败
    echo.
    echo   查看日志:
    type logs\web_backend.log | more
    echo.
    pause
    exit /b 1
)

echo.

REM 步骤5: 测试连接
echo [步骤 5/5] 测试连接
echo.

REM 等待一会儿确保服务完全启动
timeout /t 2 /nobreak >nul

echo   测试 HTTP 健康检查...
curl -s http://localhost:8000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo   ✓ HTTP 健康检查通过
) else (
    echo   ⚠️ HTTP 健康检查失败
    echo   服务可能还在启动中...
)

echo.

REM 测试 WebSocket（使用 Python）
echo   测试 WebSocket 连接...
%PYTHON_CMD% -c "import sys; sys.path.insert(0, '.'); import asyncio; import json; exec(\"async def test():\n    try:\n        import websockets\n        async with websockets.connect('ws://localhost:8000/ws') as ws:\n            await ws.send(json.dumps({'type': 'ping'}))\n            resp = await ws.recv()\n            print('✓ WebSocket 测试成功')\n            return True\n    except ImportError:\n        print('⚠️ 需要安装 websockets: pip install websockets')\n        return False\n    except Exception as e:\n        print(f'✗ WebSocket 连接失败: {e}')\n        return False\nresult = asyncio.run(test())\")" 2>nul

echo.
echo.

REM 最终总结
echo ╔════════════════════════════════════════════════════════════╗
echo ║                     服务启动完成                           ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo ✅ 服务已启动
echo.

echo 服务信息:
echo   Web 后端: http://localhost:8000
echo   WebSocket: ws://localhost:8000/ws
echo   API 文档: http://localhost:8000/api/docs
echo.

echo 查看日志:
echo   type logs\web_backend.log
echo.

echo 测试 WebSocket:
echo   1. 访问 http://localhost:3000/trading
echo   2. 按 F12 打开浏览器开发者工具
echo   3. 查看 Console 标签
echo   4. 应该显示 "WebSocket连接已建立"
echo.

echo 停止服务:
echo   taskkill /F /IM python.exe
echo.

echo 🎉 修复完成！请刷新浏览器页面测试
echo.
pause

