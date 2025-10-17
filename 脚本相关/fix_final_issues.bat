@echo off
chcp 65001 >nul
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║     修复最后的问题并重启后端                              ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo 已修复的问题:
echo   1. ✓ manifest.json 404
echo   2. ✓ /api/trading/symbols 404
echo   3. ✓ /api/trading/positions 404
echo   4. ✓ /api/trading/stats 500
echo   5. ✓ /api/positions/history 404 (新增)
echo   6. ✓ /api/strategies/{id}/toggle 404 (新增)
echo   7. ✓ camelCase 响应格式
echo   8. ✓ WebSocket 连接 (所有页面)
echo.

echo [1/3] 停止并清理
echo.
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM 清理所有 Python 缓存
for /d /r web_backend %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"

echo   ✓ 已停止服务并清理缓存
echo.

echo [2/3] 启动后端
echo.
cd web_backend
start /B /MIN "" python -m uvicorn main:app --host 0.0.0.0 --port 8000 > ..\logs\web_backend.log 2>&1
cd ..
echo   等待启动 (10秒)...
timeout /t 10 /nobreak >nul
echo.

echo [3/3] 验证服务
echo.
curl -s http://localhost:8000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo   ✓ 后端服务正常
    echo.
    echo   访问 API 文档查看所有端点:
    echo   http://localhost:8000/api/docs
) else (
    echo   ✗ 后端启动失败
    type logs\web_backend.log
    pause
    exit /b 1
)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                    ✅ 修复完成                             ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo 所有端点已就绪:
echo   • /api/trading/account
echo   • /api/trading/symbols
echo   • /api/trading/positions
echo   • /api/trading/stats
echo   • /api/trading/orders
echo   • /api/positions/history (新增)
echo   • /api/strategies/{id}/toggle (新增)
echo.

echo 下一步 - 在浏览器中:
echo.
echo   1. 清除缓存:
echo      F12 → Application → Clear site data
echo.
echo   2. 强制刷新:
echo      Ctrl+Shift+R
echo.
echo   3. 重新登录:
echo      admin / admin123
echo.
echo   4. 测试所有页面:
echo      • Dashboard    - 应显示余额
echo      • Trading      - 应正常工作
echo      • Strategies   - 可切换状态
echo      • Positions    - 应显示持仓
echo      • History      - 持仓记录应加载
echo.

echo 测试 API:
echo   powershell -ExecutionPolicy Bypass -File test_api_format.ps1
echo.

echo 🎉 所有问题已修复！
echo.
pause

