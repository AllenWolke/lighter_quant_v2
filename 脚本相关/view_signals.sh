#!/bin/bash
# 查看交易信号脚本 - Linux/macOS

echo "============================================================"
echo "  交易信号查看器"
echo "============================================================"
echo ""

LOG_FILE="logs/quant_trading.log"

if [ ! -f "$LOG_FILE" ]; then
    echo "❌ 错误: 日志文件不存在"
    exit 1
fi

echo "📊 交易信号统计"
echo "----------------------------------------"

# 统计信号数量
total_signals=$(grep "交易信号" "$LOG_FILE" | wc -l)
long_signals=$(grep "交易信号: LONG" "$LOG_FILE" | wc -l)
short_signals=$(grep "交易信号: SHORT" "$LOG_FILE" | wc -l)
exit_signals=$(grep "交易信号: EXIT" "$LOG_FILE" | wc -l)

echo "总信号数: $total_signals"
echo "做多信号: $long_signals"
echo "做空信号: $short_signals"
echo "平仓信号: $exit_signals"
echo ""

echo "📝 最近10个交易信号"
echo "----------------------------------------"
grep "交易信号" "$LOG_FILE" | tail -10

echo ""
echo "💰 交易记录"
echo "----------------------------------------"
grep "记录交易" "$LOG_FILE" | tail -5

echo ""
echo "⚠️  最近的警告"
echo "----------------------------------------"
grep "WARNING" "$LOG_FILE" | tail -5

echo ""
echo "❌ 最近的错误"
echo "----------------------------------------"
grep "ERROR" "$LOG_FILE" | tail -5 || echo "无错误"

