#!/bin/bash
# 清理Python缓存（Ubuntu/Linux）

echo "清理Python缓存..."

# 清理__pycache__目录
echo "  清理__pycache__目录..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
echo "  ✓ __pycache__目录已清理"

# 清理.pyc文件
echo "  清理.pyc文件..."
find . -type f -name "*.pyc" -delete 2>/dev/null
echo "  ✓ .pyc文件已清理"

# 清理.pyo文件
echo "  清理.pyo文件..."
find . -type f -name "*.pyo" -delete 2>/dev/null
echo "  ✓ .pyo文件已清理"

echo ""
echo "✓ 缓存清理完成"

