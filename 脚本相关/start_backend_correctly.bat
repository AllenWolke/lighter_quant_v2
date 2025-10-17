@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║     启动 Web 后端服务 - 正确方式                          ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM 获取脚本所在目录并切换
cd /d "%~dp0"

echo [1/6] 检查环境
echo.

REM 检查 Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ 错误: 未找到 Python
    echo 请先安装 Python 3.9+
    pause
    exit /b 1
)

python --version
echo ✓ Python 已安装
echo.

REM 创建必要目录
echo [2/6] 创建目录
if not exist "logs" mkdir logs
if not exist "data" mkdir data
echo ✓ 目录已创建
echo.

REM 切换到 web_backend 目录
echo [3/6] 切换到 web_backend 目录
cd web_backend

if not exist "main.py" (
    echo ✗ 错误: 找不到 main.py
    echo 当前目录: %CD%
    echo 请确保脚本在项目根目录运行
    pause
    exit /b 1
)

echo ✓ 找到 main.py
echo   路径: %CD%\main.py
echo.

REM 验证 Python 环境
echo [4/6] 验证 Python 环境
python -c "import main; print('✓ main 模块可以导入'); print('✓ app 对象存在:', hasattr(main, 'app'))" 2>nul
if %errorlevel% neq 0 (
    echo ✗ Python 环境验证失败
    echo.
    echo 可能的原因:
    echo   1. 缺少依赖包
    echo   2. main.py 中有错误
    echo.
    echo 请运行以下命令检查:
    echo   cd web_backend
    echo   python main.py
    echo.
    pause
    exit /b 1
)

echo ✓ Python 环境验证成功
echo.

REM 停止现有进程
echo [5/6] 停止现有进程
for /f "tokens=2" %%a in ('tasklist ^| findstr python.exe') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 /nobreak >nul
echo ✓ 已清理现有进程
echo.

REM 启动服务
echo [6/6] 启动后端服务
echo.
echo 启动信息:
echo   端口: 8000
echo   日志: ..\logs\web_backend.log
echo   工作目录: %CD%
echo.

REM 在新窗口启动服务（方便看到输出）
start "Lighter Web Backend" /MIN python -m uvicorn main:app --host 0.0.0.0 --port 8000

REM 等待启动
echo 等待服务启动...
timeout /t 5 /nobreak >nul

REM 测试服务
echo.
echo 测试服务连接...
curl -s http://localhost:8000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo.
    echo ╔════════════════════════════════════════════════════════════╗
    echo ║                ✓ 后端服务启动成功！                        ║
    echo ╚════════════════════════════════════════════════════════════╝
    echo.
    echo 访问地址:
    echo   API: http://localhost:8000
    echo   文档: http://localhost:8000/api/docs
    echo   健康检查: http://localhost:8000/api/health
    echo.
    echo 查看日志:
    echo   type ..\logs\web_backend.log
    echo.
    echo 停止服务:
    echo   taskkill /F /IM python.exe
    echo.
) else (
    echo.
    echo ⚠️  服务启动可能失败
    echo.
    echo 请检查:
    echo   1. 端口 8000 是否被占用
    echo   2. 查看后端窗口的错误信息
    echo   3. 查看日志: type ..\logs\web_backend.log
    echo.
)

echo 提示: 后端服务在独立窗口运行
echo       关闭该窗口将停止服务
echo.
pause

