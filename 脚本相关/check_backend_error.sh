#!/bin/bash

echo "=========================================="
echo "  检查后端错误日志"
echo "=========================================="
echo ""

if [ -f "logs/backend.log" ]; then
    echo "最后100行日志:"
    echo ""
    tail -n 100 logs/backend.log | grep -A 10 -B 2 -E "ERROR|Traceback|Exception"
    echo ""
    echo "=========================================="
    echo "完整错误日志（最后50行）:"
    echo "=========================================="
    tail -n 50 logs/backend.log
else
    echo "未找到 logs/backend.log"
    echo "后端可能未启动"
fi

