#!/bin/bash
# 停止量化交易系统（Ubuntu/Linux）

echo "停止量化交易系统..."

# 停止进程
pkill -f "python.*start_trading.py"

if [ $? -eq 0 ]; then
    echo "✓ 系统已停止"
else
    echo "✓ 系统未在运行"
fi

# 确认进程已停止
sleep 1
if ps aux | grep "python.*start_trading.py" | grep -v grep > /dev/null; then
    echo "⚠ 进程仍在运行，强制停止..."
    pkill -9 -f "python.*start_trading.py"
    echo "✓ 强制停止完成"
fi

