#!/bin/bash
# 检查系统状态（Ubuntu/Linux）

echo "=========================================="
echo "系统状态检查"
echo "=========================================="
echo ""

# 检查进程
echo "[1] 进程状态:"
if ps aux | grep "python.*start_trading.py" | grep -v grep > /dev/null; then
    echo "  ✓ 系统正在运行"
    echo ""
    echo "  进程详情:"
    ps aux | grep "python.*start_trading.py" | grep -v grep | awk '{printf "    PID: %s\n    CPU: %s%%\n    MEM: %s%%\n    运行时间: %s\n", $2, $3, $4, $10}'
else
    echo "  ✗ 系统未运行"
fi

echo ""

# 检查日志
echo "[2] 日志状态:"
if [ -f "logs/quant_trading.log" ]; then
    log_size=$(ls -lh logs/quant_trading.log | awk '{print $5}')
    log_time=$(stat -c '%y' logs/quant_trading.log 2>/dev/null | cut -d'.' -f1)
    log_lines=$(wc -l < logs/quant_trading.log)
    
    echo "  ✓ 日志文件存在"
    echo "    文件大小: ${log_size}"
    echo "    最后修改: ${log_time}"
    echo "    总行数: ${log_lines}"
    
    # 检查最后更新时间
    current_time=$(date +%s)
    log_mtime=$(stat -c %Y logs/quant_trading.log 2>/dev/null)
    time_diff=$((current_time - log_mtime))
    
    if [ $time_diff -lt 300 ]; then
        echo "    更新状态: ✓ 活跃 (${time_diff}秒前更新)"
    else
        minutes=$((time_diff / 60))
        echo "    更新状态: ⚠ 可能停滞 (${minutes}分钟未更新)"
    fi
else
    echo "  ✗ 日志文件不存在"
fi

echo ""

# 检查配置
echo "[3] 配置状态:"
if [ -f "config.yaml" ]; then
    echo "  ✓ 配置文件存在"
    
    # 提取关键配置
    primary=$(grep "primary:" config.yaml | head -1 | awk '{print $2}' | tr -d '"')
    base_url=$(grep "base_url:" config.yaml | head -1 | awk '{print $2}' | tr -d '"')
    
    echo "    主数据源: ${primary:-未设置}"
    echo "    API地址: ${base_url:-未设置}"
else
    echo "  ✗ 配置文件不存在"
fi

echo ""
echo "=========================================="

