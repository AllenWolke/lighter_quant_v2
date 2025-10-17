#!/bin/bash

###############################################################################
# 批量修复所有前端 toFixed 错误
# 在所有 TypeScript 文件中查找并提示需要修复的位置
###############################################################################

echo "=========================================="
echo "  查找所有 toFixed 调用"
echo "=========================================="
echo ""

cd web_frontend/src

echo "查找需要修复的文件..."
echo ""

# 查找所有 .toFixed( 调用
grep -rn "\.toFixed(" --include="*.tsx" --include="*.ts" . | \
  grep -v "?" | \
  grep -v "||" | \
  grep -v "safeToFixed" | \
  head -50

echo ""
echo "=========================================="
echo "建议："
echo "=========================================="
echo ""
echo "所有 .toFixed() 调用应该添加空值检查："
echo ""
echo "修复前:"
echo "  value.toFixed(2)"
echo ""
echo "修复后:"
echo "  value ? value.toFixed(2) : '0.00'"
echo "  或"
echo "  (value || 0).toFixed(2)"
echo ""
echo "=========================================="

cd ../..

