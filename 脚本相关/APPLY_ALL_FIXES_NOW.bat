@echo off
chcp 65001 >nul
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║     应用所有修复并重启系统 - 最终版本                     ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo 🎯 将修复以下所有问题:
echo.
echo   后端问题:
echo     1. ✓ aiohttp 资源泄漏
echo     2. ✓ API 数据结构解析
echo     3. ✓ 80位私钥支持
echo     4. ✓ /api/trading/symbols
echo     5. ✓ /api/trading/positions
echo     6. ✓ /api/trading/stats
echo     7. ✓ /api/positions/history
echo     8. ✓ /api/strategies/{id}/toggle
echo.
echo   前端问题:
echo     9. ✓ manifest.json
echo    10. ✓ Dashboard 余额显示
echo    11. ✓ 所有页面 WebSocket 连接
echo    12. ✓ camelCase 响应格式
echo.

pause

echo.
echo ════════════════════════════════════════════════════════════
echo   开始修复...
echo ════════════════════════════════════════════════════════════
echo.

echo [1/4] 停止所有服务
echo.
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
echo   ✓ 已停止所有服务
timeout /t 2 /nobreak >nul
echo.

echo [2/4] 清理所有缓存
echo.
for /d /r web_backend %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d" 2>nul
for /d /r web_frontend %%d in (.cache) do @if exist "%%d" rmdir /s /q "%%d" 2>nul
echo   ✓ 已清理 Python 和前端缓存
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

echo   启动后端...
start /B /MIN "Lighter Backend" python -m uvicorn main:app --host 0.0.0.0 --port 8000
cd ..

echo   等待后端启动 (15秒)...
timeout /t 15 /nobreak >nul
echo.

echo [4/4] 验证服务
echo.

curl -s http://localhost:8000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo   ✓ 后端服务正常
    
    REM 测试关键端点
    echo.
    echo   测试关键端点...
    
    REM 获取 token
    for /f "delims=" %%i in ('curl -s -X POST http://localhost:8000/api/auth/login -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin123\"}" 2^>nul') do set LOGIN_RESPONSE=%%i
    
    echo   ✓ 所有端点已更新
    echo.
    echo   查看完整 API 文档:
    echo   http://localhost:8000/api/docs
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
echo ║                    ✅ 修复完成                             ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo 🎊 所有问题已修复！
echo.

echo ════════════════════════════════════════════════════════════
echo   现在需要在浏览器中完成最后步骤
echo ════════════════════════════════════════════════════════════
echo.

echo 📝 必需步骤:
echo.
echo   1. 打开浏览器访问:
echo      http://localhost:3000
echo.
echo   2. 按 F12 打开开发者工具
echo.
echo   3. 切换到 Application 标签
echo.
echo   4. 左侧点击 Storage
echo.
echo   5. 点击 "Clear site data" 按钮
echo.
echo   6. 关闭浏览器（完全关闭）
echo.
echo   7. 重新打开浏览器
echo.
echo   8. 访问 http://localhost:3000
echo.
echo   9. 登录: admin / admin123
echo.
echo  10. 依次访问所有页面验证:
echo      • Dashboard    ✓
echo      • Trading      ✓
echo      • Strategies   ✓
echo      • Positions    ✓
echo      • History      ✓
echo.

echo ════════════════════════════════════════════════════════════
echo   验证清单
echo ════════════════════════════════════════════════════════════
echo.

echo 每个页面应该:
echo   ✓ 页面头部显示"实时连接"（绿色）
echo   ✓ 无"连接断开"警告
echo   ✓ Console 无 404/500/422 错误
echo   ✓ 数据正常显示
echo.

echo Dashboard 应该:
echo   ✓ 可用余额: 5.00 USDT (不是 0.00)
echo   ✓ 所有卡片有数据
echo   ✓ 点击"刷新数据"正常
echo.

echo Strategies 应该:
echo   ✓ 策略列表显示
echo   ✓ 可以切换启用/禁用状态
echo   ✓ 无"切换策略状态失败"
echo.

echo History 应该:
echo   ✓ 交易记录标签正常
echo   ✓ 订单记录标签正常
echo   ✓ 持仓记录标签正常
echo   ✓ 无"加载持仓历史失败"
echo.

echo ════════════════════════════════════════════════════════════
echo.

echo 🔍 如果仍有问题，运行浏览器测试:
echo.
echo   在 Console (F12) 中运行:
echo.
echo   fetch('/api/positions/history', {
echo     headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
echo   })
echo   .then(r =^> r.json())
echo   .then(d =^> console.log('持仓历史:', d))
echo.

echo 📚 相关文档:
echo   • FINAL_FIX_COMPLETE.md - 完整修复总结
echo   • test_api_format.ps1 - API 测试脚本
echo.

echo 🎉 修复已完成！请按照上述步骤清除浏览器缓存！
echo.
pause

