#!/bin/bash

echo "📦 安装Lighter量化交易系统前端依赖..."

# 检查Node.js版本
node_version=$(node -v 2>/dev/null)
if [ $? -ne 0 ]; then
    echo "❌ 未安装Node.js，请先安装Node.js 16+"
    exit 1
fi

echo "✅ Node.js版本: $node_version"

# 检查npm版本
npm_version=$(npm -v 2>/dev/null)
if [ $? -ne 0 ]; then
    echo "❌ 未安装npm，请先安装npm"
    exit 1
fi

echo "✅ npm版本: $npm_version"

# 清理缓存
echo "🧹 清理npm缓存..."
npm cache clean --force

# 删除node_modules和package-lock.json
if [ -d "node_modules" ]; then
    echo "🗑️ 删除旧的node_modules..."
    rm -rf node_modules
fi

if [ -f "package-lock.json" ]; then
    echo "🗑️ 删除package-lock.json..."
    rm package-lock.json
fi

# 安装依赖
echo "📦 安装依赖包..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败"
    exit 1
fi

echo "✅ 依赖安装完成"

# 检查关键依赖
echo "🔍 检查关键依赖..."

echo "检查React..."
npm list react
if [ $? -ne 0 ]; then
    echo "❌ React安装失败"
    exit 1
fi

echo "检查Ant Design..."
npm list antd
if [ $? -ne 0 ]; then
    echo "❌ Ant Design安装失败"
    exit 1
fi

echo "检查React Router..."
npm list react-router-dom
if [ $? -ne 0 ]; then
    echo "❌ React Router安装失败"
    exit 1
fi

echo "检查TypeScript..."
npm list typescript
if [ $? -ne 0 ]; then
    echo "❌ TypeScript安装失败"
    exit 1
fi

echo "✅ 所有关键依赖检查通过"

echo "🎉 依赖安装完成！"
echo "现在可以运行 npm start 启动开发服务器"
