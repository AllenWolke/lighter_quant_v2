@echo off
chcp 65001 >nul
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║     测试真实持仓数据 - 重启后端服务                       ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo 🎯 本脚本将:
echo   1. 停止后端服务
echo   2. 清理缓存
echo   3. 重启后端服务
echo   4. 测试持仓数据端点
echo.

pause

echo.
echo ════════════════════════════════════════════════════════════
echo   [1/4] 停止后端服务
echo ════════════════════════════════════════════════════════════
echo.

taskkill /F /IM python.exe >nul 2>&1
echo   ✓ 已停止后端服务
timeout /t 2 /nobreak >nul
echo.

echo ════════════════════════════════════════════════════════════
echo   [2/4] 清理缓存
echo ════════════════════════════════════════════════════════════
echo.

for /d /r web_backend %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d" 2>nul
echo   ✓ 已清理 Python 缓存
echo.

echo ════════════════════════════════════════════════════════════
echo   [3/4] 启动后端服务
echo ════════════════════════════════════════════════════════════
echo.

cd web_backend
start /B /MIN "Lighter Backend" python -m uvicorn main:app --host 0.0.0.0 --port 8000
cd ..

echo   等待后端启动 (15秒)...
timeout /t 15 /nobreak >nul
echo.

echo ════════════════════════════════════════════════════════════
echo   [4/4] 测试持仓数据端点
echo ════════════════════════════════════════════════════════════
echo.

REM 获取 token
echo   正在登录...
for /f "delims=" %%i in ('curl -s -X POST http://localhost:8000/api/auth/login -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin123\"}" 2^>nul') do set LOGIN_RESPONSE=%%i

REM 提取 token (简化处理)
echo %LOGIN_RESPONSE% | findstr /C:"accessToken" >nul
if %errorlevel% equ 0 (
    echo   ✓ 登录成功
    echo.
    
    REM 测试 /api/trading/positions
    echo   测试 1: GET /api/trading/positions
    echo   ----------------------------------------
    curl -s -X GET http://localhost:8000/api/trading/positions ^
        -H "Authorization: Bearer %LOGIN_RESPONSE:~-50%" 2>nul | python -m json.tool
    echo.
    echo.
    
    REM 测试 /api/positions/history
    echo   测试 2: GET /api/positions/history
    echo   ----------------------------------------
    curl -s -X GET http://localhost:8000/api/positions/history ^
        -H "Authorization: Bearer %LOGIN_RESPONSE:~-50%" 2>nul | python -m json.tool
    echo.
    
) else (
    echo   ✗ 登录失败
    echo   响应: %LOGIN_RESPONSE%
)

echo.
echo ════════════════════════════════════════════════════════════
echo   完成
echo ════════════════════════════════════════════════════════════
echo.

echo 📝 说明:
echo.
echo   • 如果看到真实持仓数据，说明集成成功
echo   • 如果返回空列表 []，说明账户当前没有持仓
echo   • 如果返回模拟数据，说明 Lighter API 调用失败
echo.
echo 🔍 查看详细日志:
echo   type logs\web_backend.log
echo.
echo 🌐 在浏览器中测试:
echo   1. 访问 http://localhost:3000
echo   2. 登录: admin / admin123
echo   3. 访问 Positions 页面
echo   4. 访问 History 页面 → 持仓记录标签
echo.

pause
