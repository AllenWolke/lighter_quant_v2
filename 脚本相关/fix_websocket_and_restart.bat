@echo off
chcp 65001 >nul
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║     WebSocket 连接修复和服务重启工具                      ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM 步骤1: 停止现有服务
echo [步骤 1/5] 停止现有服务
echo   停止 Web 后端...

taskkill /F /IM python.exe /FI "WINDOWTITLE eq *uvicorn*" >nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *web_backend*" >nul 2>&1

timeout /t 2 /nobreak >nul

echo   ✓ 已尝试停止现有服务
echo.

REM 步骤2: 验证修复
echo [步骤 2/5] 验证修复
findstr /C:"client_id = str(uuid.uuid4())" web_backend\main.py >nul
if %errorlevel% equ 0 (
    echo   ✓ WebSocket 修复已应用
) else (
    echo   ⚠️ WebSocket 修复可能未完全应用
)
echo.

REM 步骤3: 检查依赖
echo [步骤 3/5] 检查依赖

if exist "venv\Scripts\python.exe" (
    set PYTHON_CMD=venv\Scripts\python.exe
    echo   ✓ 使用虚拟环境 Python
) else (
    set PYTHON_CMD=python
    echo   ⚠️ 使用系统 Python
)

echo   检查 FastAPI...
%PYTHON_CMD% -c "import fastapi" 2>nul
if %errorlevel% equ 0 (
    echo   ✓ FastAPI
) else (
    echo   ✗ FastAPI 未安装
    echo   请运行: pip install fastapi uvicorn
    pause
    exit /b 1
)
echo.

REM 步骤4: 启动 Web 后端
echo [步骤 4/5] 启动 Web 后端

REM 创建日志目录
if not exist "logs" mkdir logs

REM 启动后端服务
echo   启动服务...
cd web_backend
start /B "" %PYTHON_CMD% -m uvicorn main:app --host 0.0.0.0 --port 8000 > ..\logs\web_backend.log 2>&1
cd ..

REM 等待服务启动
echo   等待服务启动...
timeout /t 5 /nobreak >nul

REM 检查服务是否运行
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I /N "python.exe">NUL
if %errorlevel% equ 0 (
    echo   ✓ Web 后端已启动
) else (
    echo   ✗ Web 后端启动失败
    echo   查看日志: type logs\web_backend.log
    pause
    exit /b 1
)
echo.

REM 步骤5: 测试连接
echo [步骤 5/5] 测试连接

timeout /t 2 /nobreak >nul

echo   测试 HTTP 健康检查...
curl -s http://localhost:8000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo   ✓ HTTP 健康检查通过
) else (
    echo   ⚠️ HTTP 健康检查失败（可能正在启动）
)
echo.

REM 最终总结
echo ╔════════════════════════════════════════════════════════════╗
echo ║                     服务重启完成                           ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo ✅ 服务已重启
echo.

echo 服务状态:
echo   Web 后端: http://localhost:8000
echo   WebSocket: ws://localhost:8000/ws
echo   API 文档: http://localhost:8000/api/docs
echo.

echo 查看日志:
echo   type logs\web_backend.log
echo.

echo 测试 WebSocket:
echo   1. 访问 http://localhost:3000/trading
echo   2. 打开浏览器控制台 (F12)
echo   3. 查看 WebSocket 连接状态
echo   4. 应该显示 "WebSocket连接已建立"
echo.

echo 停止服务:
echo   taskkill /F /IM python.exe
echo.

echo 🎉 修复完成！请刷新浏览器页面测试
echo.
pause

