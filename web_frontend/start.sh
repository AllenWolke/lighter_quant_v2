#!/bin/bash

# Lighter量化交易系统前端启动脚本

echo "🚀 启动Lighter量化交易系统前端..."

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

# 检查是否存在node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 安装依赖包..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
    echo "✅ 依赖安装完成"
else
    echo "✅ 依赖已存在"
fi

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "📝 创建环境变量文件..."
    cat > .env << EOF
# API配置
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws

# 应用配置
REACT_APP_NAME=Lighter量化交易系统
REACT_APP_VERSION=1.0.0

# 开发配置
GENERATE_SOURCEMAP=false
REACT_APP_DEBUG=true
EOF
    echo "✅ 环境变量文件创建完成"
else
    echo "✅ 环境变量文件已存在"
fi

# 启动开发服务器
echo "🌟 启动开发服务器..."
echo "📱 前端地址: http://localhost:3000"
echo "🔧 后端地址: http://localhost:8000"
echo "📚 API文档: http://localhost:8000/api/docs"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

npm start
