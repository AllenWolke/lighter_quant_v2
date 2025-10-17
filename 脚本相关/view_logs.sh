#!/bin/bash
# 查看日志（Ubuntu/Linux）

if [ ! -f "logs/quant_trading.log" ]; then
    echo "✗ 日志文件不存在: logs/quant_trading.log"
    exit 1
fi

echo "=========================================="
echo "实时查看日志"
echo "=========================================="
echo "按 Ctrl+C 退出"
echo ""

# 实时查看日志
tail -f logs/quant_trading.log

