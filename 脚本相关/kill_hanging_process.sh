#!/bin/bash

###############################################################################
# 杀死挂起的进程
###############################################################################

echo "=========================================="
echo "  杀死挂起的进程"
echo "=========================================="

# 查找并杀死 init_default_user.py 进程
echo "查找挂起的 init_default_user.py 进程..."
pids=$(ps aux | grep init_default_user | grep -v grep | awk '{print $2}')

if [ -z "$pids" ]; then
    echo "✓ 没有发现挂起的进程"
else
    echo "发现以下进程:"
    ps aux | grep init_default_user | grep -v grep
    echo ""
    echo "正在终止..."
    for pid in $pids; do
        kill -9 $pid 2>/dev/null
        echo "  ✓ 已杀死进程 $pid"
    done
fi

# 清理其他可能的挂起进程
echo ""
echo "清理其他可能挂起的Python进程..."
pkill -9 -f "python.*main.py" 2>/dev/null || true
echo "✓ 清理完成"

echo ""
echo "=========================================="
echo "✅ 所有挂起的进程已终止"
echo "=========================================="
echo ""
echo "现在可以重新运行:"
echo "  ./start_all_services.sh"
echo ""

