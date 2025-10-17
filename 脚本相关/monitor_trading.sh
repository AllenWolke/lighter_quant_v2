#!/bin/bash
# 量化交易系统监控脚本 - Linux/macOS

echo "============================================================"
echo "  Lighter 量化交易系统 - 实时监控"
echo "============================================================"
echo ""
echo "日志文件: logs/quant_trading.log"
echo "按 Ctrl+C 停止监控"
echo ""
echo "============================================================"
echo ""

# 检查日志文件是否存在
if [ ! -f "logs/quant_trading.log" ]; then
    echo "❌ 错误: 日志文件不存在"
    echo "请确保交易系统正在运行"
    exit 1
fi

# 实时监控日志，高亮显示关键信息
tail -f logs/quant_trading.log | while read line; do
    # 提取时间戳
    timestamp=$(echo "$line" | cut -d'-' -f1)
    
    # 交易信号 - 绿色加粗
    if echo "$line" | grep -q "交易信号"; then
        echo -e "\033[1;32m[SIGNAL] $line\033[0m"
    
    # 订单成交 - 青色
    elif echo "$line" | grep -q "订单已成交"; then
        echo -e "\033[1;36m[FILLED] $line\033[0m"
    
    # 记录交易 - 蓝色
    elif echo "$line" | grep -q "记录交易"; then
        echo -e "\033[1;34m[TRADE] $line\033[0m"
    
    # 错误 - 红色
    elif echo "$line" | grep -q "ERROR"; then
        echo -e "\033[1;31m[ERROR] $line\033[0m"
    
    # 警告 - 黄色
    elif echo "$line" | grep -q "WARNING"; then
        echo -e "\033[1;33m[WARNING] $line\033[0m"
    
    # 风险检查 - 橙色
    elif echo "$line" | grep -q "风险"; then
        echo -e "\033[0;33m[RISK] $line\033[0m"
    
    # 普通日志 - 灰色
    else
        echo -e "\033[0;37m$line\033[0m"
    fi
done

