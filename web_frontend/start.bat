@echo off
chcp 65001 >nul

echo 🚀 启动Lighter量化交易系统前端...

REM 检查Node.js版本
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未安装Node.js，请先安装Node.js 16+
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version') do set node_version=%%i
echo ✅ Node.js版本: %node_version%

REM 检查npm版本
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未安装npm，请先安装npm
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('npm --version') do set npm_version=%%i
echo ✅ npm版本: %npm_version%

REM 检查是否存在node_modules
if not exist "node_modules" (
    echo 📦 安装依赖包...
    npm install
    if %errorlevel% neq 0 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
    echo ✅ 依赖安装完成
) else (
    echo ✅ 依赖已存在
)

REM 检查环境变量文件
if not exist ".env" (
    echo 📝 创建环境变量文件...
    (
        echo # API配置
        echo REACT_APP_API_URL=http://localhost:8000
        echo REACT_APP_WS_URL=ws://localhost:8000/ws
        echo.
        echo # 应用配置
        echo REACT_APP_NAME=Lighter量化交易系统
        echo REACT_APP_VERSION=1.0.0
        echo.
        echo # 开发配置
        echo GENERATE_SOURCEMAP=false
        echo REACT_APP_DEBUG=true
    ) > .env
    echo ✅ 环境变量文件创建完成
) else (
    echo ✅ 环境变量文件已存在
)

REM 启动开发服务器
echo 🌟 启动开发服务器...
echo 📱 前端地址: http://localhost:3000
echo 🔧 后端地址: http://localhost:8000
echo 📚 API文档: http://localhost:8000/api/docs
echo.
echo 按 Ctrl+C 停止服务器
echo.

npm start
