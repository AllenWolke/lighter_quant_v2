#!/bin/bash
# 一键重启量化交易系统（Ubuntu/Linux）

echo "=========================================="
echo "量化交易系统一键重启"
echo "=========================================="
echo ""

# 第1步: 停止旧进程
echo "[1/4] 停止旧进程..."
pkill -f "python.*start_trading.py" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "  ✓ 已停止旧进程"
    sleep 1
else
    echo "  ✓ 没有运行中的进程"
fi
echo ""

# 第2步: 清理Python缓存
echo "[2/4] 清理Python缓存..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
echo "  ✓ 缓存已清理"
echo ""

# 第3步: 检查配置
echo "[3/4] 检查配置..."
if [ -f "config.yaml" ]; then
    primary_source=$(grep "primary:" config.yaml | head -1 | awk '{print $2}' | tr -d '"')
    echo "  ✓ 配置文件存在"
    echo "  主数据源: ${primary_source:-未设置}"
else
    echo "  ✗ 警告: 找不到 config.yaml"
fi
echo ""

# 第4步: 启动系统
echo "[4/4] 启动系统..."
echo "=========================================="
echo ""

# 检查Python版本
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "✗ 错误: 找不到Python"
    exit 1
fi

echo "使用Python: $PYTHON_CMD"
echo ""
echo "提示: 按 Ctrl+C 停止程序"
echo ""

# 启动系统
exec $PYTHON_CMD start_trading.py

