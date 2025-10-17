@echo off
chcp 65001 >nul
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║     修复 History 页面持仓历史加载问题                     ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo 🎯 修复内容:
echo   • 后端 API 返回格式添加 page 和 pageSize 字段
echo   • 匹配前端期望的数据结构
echo.

pause

echo.
echo ════════════════════════════════════════════════════════════
echo   [1/3] 停止后端服务
echo ════════════════════════════════════════════════════════════
echo.

taskkill /F /IM python.exe >nul 2>&1
echo   ✓ 已停止后端服务
timeout /t 2 /nobreak >nul
echo.

echo ════════════════════════════════════════════════════════════
echo   [2/3] 清理缓存
echo ════════════════════════════════════════════════════════════
echo.

for /d /r web_backend %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d" 2>nul
echo   ✓ 已清理 Python 缓存
echo.

echo ════════════════════════════════════════════════════════════
echo   [3/3] 启动后端服务
echo ════════════════════════════════════════════════════════════
echo.

cd web_backend
start /B /MIN "Lighter Backend" python -m uvicorn main:app --host 0.0.0.0 --port 8000
cd ..

echo   等待后端启动 (15秒)...
timeout /t 15 /nobreak >nul
echo.

echo ╔════════════════════════════════════════════════════════════╗
echo ║                    ✅ 修复完成                             ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo 🌐 测试步骤:
echo.
echo   1. 打开浏览器访问:
echo      http://localhost:3000
echo.
echo   2. 登录: admin / admin123
echo.
echo   3. 访问 History 页面
echo.
echo   4. 点击 "持仓记录" 标签
echo.
echo   5. 验证:
echo      • 无 "加载持仓历史失败" 错误
echo      • 持仓历史数据正常显示
echo      • Console (F12) 无错误
echo.

echo 🔍 手动测试 API:
echo.
echo   curl -X POST http://localhost:8000/api/auth/login ^
echo     -H "Content-Type: application/json" ^
echo     -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
echo.
echo   然后使用返回的 token:
echo.
echo   curl -X GET http://localhost:8000/api/positions/history ^
echo     -H "Authorization: Bearer YOUR_TOKEN"
echo.
echo   应该返回:
echo   {
echo     "positions": [...],
echo     "total": N,
echo     "page": 1,
echo     "pageSize": 100
echo   }
echo.

echo 📝 预期结果:
echo   • positions: 持仓数组
echo   • total: 总数量
echo   • page: 当前页码 (1)
echo   • pageSize: 每页数量 (100)
echo.

pause
