@echo off
chcp 65001 >nul

echo 📦 安装Lighter量化交易系统前端依赖...

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

REM 清理缓存
echo 🧹 清理npm缓存...
npm cache clean --force

REM 删除node_modules和package-lock.json
if exist "node_modules" (
    echo 🗑️ 删除旧的node_modules...
    rmdir /s /q node_modules
)

if exist "package-lock.json" (
    echo 🗑️ 删除package-lock.json...
    del package-lock.json
)

REM 安装依赖
echo 📦 安装依赖包...
npm install

if %errorlevel% neq 0 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

echo ✅ 依赖安装完成

REM 检查关键依赖
echo 🔍 检查关键依赖...

echo 检查React...
npm list react
if %errorlevel% neq 0 (
    echo ❌ React安装失败
    pause
    exit /b 1
)

echo 检查Ant Design...
npm list antd
if %errorlevel% neq 0 (
    echo ❌ Ant Design安装失败
    pause
    exit /b 1
)

echo 检查React Router...
npm list react-router-dom
if %errorlevel% neq 0 (
    echo ❌ React Router安装失败
    pause
    exit /b 1
)

echo 检查TypeScript...
npm list typescript
if %errorlevel% neq 0 (
    echo ❌ TypeScript安装失败
    pause
    exit /b 1
)

echo ✅ 所有关键依赖检查通过

echo 🎉 依赖安装完成！
echo 现在可以运行 npm start 启动开发服务器
pause
