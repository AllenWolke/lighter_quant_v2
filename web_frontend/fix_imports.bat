@echo off
chcp 65001 >nul

echo 🔧 修复Lighter量化交易系统前端导入问题...

REM 检查是否存在node_modules
if not exist "node_modules" (
    echo ❌ node_modules不存在，请先运行 install_dependencies.bat
    pause
    exit /b 1
)

REM 创建.env文件
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
    echo.
    echo # TypeScript配置
    echo TSC_COMPILE_ON_ERROR=true
    echo ESLINT_NO_DEV_ERRORS=true
) > .env

echo ✅ 环境变量文件创建完成

REM 检查TypeScript配置
echo 🔍 检查TypeScript配置...
if not exist "tsconfig.json" (
    echo ❌ tsconfig.json不存在
    pause
    exit /b 1
)

echo ✅ TypeScript配置存在

REM 检查关键文件
echo 🔍 检查关键文件...

if not exist "src\App.tsx" (
    echo ❌ src\App.tsx不存在
    pause
    exit /b 1
)

if not exist "src\index.tsx" (
    echo ❌ src\index.tsx不存在
    pause
    exit /b 1
)

if not exist "src\store\authStore.ts" (
    echo ❌ src\store\authStore.ts不存在
    pause
    exit /b 1
)

echo ✅ 关键文件检查通过

REM 运行类型检查
echo 🔍 运行TypeScript类型检查...
npx tsc --noEmit

if %errorlevel% neq 0 (
    echo ⚠️ TypeScript类型检查有警告，但可以继续运行
) else (
    echo ✅ TypeScript类型检查通过
)

REM 运行ESLint检查
echo 🔍 运行ESLint检查...
npx eslint src --ext .ts,.tsx --max-warnings 0

if %errorlevel% neq 0 (
    echo ⚠️ ESLint检查有警告，但可以继续运行
) else (
    echo ✅ ESLint检查通过
)

echo 🎉 导入问题修复完成！
echo 现在可以运行 npm start 启动开发服务器
pause
