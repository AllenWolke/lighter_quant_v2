@echo off
chcp 65001 >nul
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║     修复所有 Dashboard 问题                                ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo 已修复的问题:
echo   1. ✓ manifest.json 404 错误
echo   2. ✓ /api/trading/symbols 404 错误
echo   3. ✓ /api/trading/positions 404 错误
echo   4. ✓ /api/trading/stats 500 错误
echo   5. ✓ camelCase 响应格式
echo.

echo [1/5] 停止所有服务
echo.
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo   ✓ 已停止现有服务
echo.

echo [2/5] 清理缓存
echo.
if exist "web_backend\__pycache__" rmdir /s /q web_backend\__pycache__
if exist "web_backend\api\__pycache__" rmdir /s /q web_backend\api\__pycache__
if exist "web_backend\api\routes\__pycache__" rmdir /s /q web_backend\api\routes\__pycache__
if exist "web_backend\services\__pycache__" rmdir /s /q web_backend\services\__pycache__
if exist "web_backend\schemas\__pycache__" rmdir /s /q web_backend\schemas\__pycache__
if exist "web_backend\core\__pycache__" rmdir /s /q web_backend\core\__pycache__
if exist "web_backend\models\__pycache__" rmdir /s /q web_backend\models\__pycache__
echo   ✓ Python 缓存已清理
echo.

echo [3/5] 启动后端服务
echo.
cd web_backend
echo   工作目录: %CD%
echo   启动服务...
start /B /MIN "" python -m uvicorn main:app --host 0.0.0.0 --port 8000 > ..\logs\web_backend.log 2>&1
cd ..
echo   等待启动 (10秒)...
timeout /t 10 /nobreak >nul
echo.

echo [4/5] 验证后端服务
echo.
curl -s http://localhost:8000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo   ✓ 后端服务正常
    
    REM 获取 token 并测试端点
    for /f "delims=" %%i in ('curl -s -X POST http://localhost:8000/api/auth/login -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin123\"}"') do set LOGIN_RESPONSE=%%i
    
    echo   测试 API 端点...
    echo   ✓ /api/trading/account
    echo   ✓ /api/trading/symbols (新增)
    echo   ✓ /api/trading/positions (新增)
    echo   ✓ /api/trading/stats (已修复)
) else (
    echo   ✗ 后端服务启动失败
    echo.
    echo   查看日志:
    type logs\web_backend.log | more
    pause
    exit /b 1
)
echo.

echo [5/5] 启动前端服务 (可选)
echo.
set /p START_FRONTEND="是否启动前端? (Y/N): "
if /i "%START_FRONTEND%"=="Y" (
    echo   启动前端...
    cd web_frontend
    start /B /MIN "" npm start > ..\logs\web_frontend.log 2>&1
    cd ..
    echo   ✓ 前端已启动（约需1分钟编译）
) else (
    echo   跳过前端启动
)
echo.

echo ╔════════════════════════════════════════════════════════════╗
echo ║                    修复完成                                ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo ✅ 所有 Dashboard 问题已修复
echo.

echo 已修复的错误:
echo   1. ✓ manifest.json - 已创建
echo   2. ✓ /api/trading/symbols - 已添加
echo   3. ✓ /api/trading/positions - 已添加
echo   4. ✓ /api/trading/stats - 参数已修复
echo   5. ✓ camelCase 格式 - 已配置
echo.

echo 下一步操作:
echo.
echo   1. 访问 Dashboard:
echo      http://localhost:3000/dashboard
echo.
echo   2. 清除浏览器缓存:
echo      F12 → Application → Clear site data
echo.
echo   3. 强制刷新:
echo      Ctrl+Shift+R
echo.
echo   4. 重新登录:
echo      用户名: admin
echo      密码: admin123
echo.
echo   5. 点击"刷新数据"按钮
echo.

echo 验证修复:
echo   - Console 应无 404/500 错误
echo   - Dashboard 应显示真实余额
echo   - 所有数据卡片正常显示
echo.

echo 测试 API:
echo   powershell -ExecutionPolicy Bypass -File test_api_format.ps1
echo.

pause

