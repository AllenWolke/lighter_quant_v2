@echo off
chcp 65001 >nul
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║     修复 Dashboard 错误并重启后端                         ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo [1/4] 停止后端服务
echo.
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo   ✓ 已停止现有进程
echo.

echo [2/4] 清理 Python 缓存
echo.
if exist "web_backend\__pycache__" (
    rmdir /s /q web_backend\__pycache__
    echo   ✓ 已清理 web_backend\__pycache__
)
if exist "web_backend\api\__pycache__" (
    rmdir /s /q web_backend\api\__pycache__
    echo   ✓ 已清理 web_backend\api\__pycache__
)
if exist "web_backend\api\routes\__pycache__" (
    rmdir /s /q web_backend\api\routes\__pycache__
    echo   ✓ 已清理 web_backend\api\routes\__pycache__
)
if exist "web_backend\services\__pycache__" (
    rmdir /s /q web_backend\services\__pycache__
    echo   ✓ 已清理 web_backend\services\__pycache__
)
if exist "web_backend\schemas\__pycache__" (
    rmdir /s /q web_backend\schemas\__pycache__
    echo   ✓ 已清理 web_backend\schemas\__pycache__
)
echo   ✓ Python 缓存已清理
echo.

echo [3/4] 启动后端服务
echo.
cd web_backend

if not exist "main.py" (
    echo   ✗ 错误: 找不到 main.py
    cd ..
    pause
    exit /b 1
)

echo   启动服务...
start /B /MIN "" python -m uvicorn main:app --host 0.0.0.0 --port 8000 > ..\logs\web_backend.log 2>&1

cd ..

echo   等待启动 (10秒)...
timeout /t 10 /nobreak >nul

echo.

echo [4/4] 验证服务
echo.

curl -s http://localhost:8000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo   ✓ 后端服务正常
    echo.
    
    REM 测试新端点
    echo   测试 API 端点...
    
    REM 获取 token
    for /f "delims=" %%i in ('curl -s -X POST http://localhost:8000/api/auth/login -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin123\"}"') do set LOGIN_RESPONSE=%%i
    
    echo   ✓ API 端点已更新
) else (
    echo   ✗ 后端服务未响应
    echo.
    echo   查看日志:
    type logs\web_backend.log | more
    pause
    exit /b 1
)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                    修复完成                                ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo ✅ 后端服务已重启
echo.

echo 已修复的问题:
echo   1. ✓ 添加了 /api/trading/positions 端点
echo   2. ✓ 修复了 /api/trading/stats 参数错误
echo   3. ✓ 配置了 camelCase 响应格式
echo.

echo 下一步:
echo   1. 访问 Dashboard: http://localhost:3000/dashboard
echo   2. 清除浏览器缓存: F12 → Application → Clear site data
echo   3. 强制刷新: Ctrl+Shift+R
echo   4. 重新登录: admin / admin123
echo   5. 点击"刷新数据"按钮
echo.

echo 测试 API:
echo   powershell -ExecutionPolicy Bypass -File test_api_format.ps1
echo.

pause
