#!/bin/bash

###############################################################################
# 检查 Lighter 交易所连接状态
###############################################################################

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo "=========================================================="
echo -e "${CYAN}  Lighter 交易所连接诊断${NC}"
echo "=========================================================="
echo ""

# 检查1: 配置文件
echo -e "${BLUE}[1/7]${NC} 检查配置文件"
echo ""

if [ -f "config.yaml" ]; then
    echo "使用配置文件: config.yaml"
    
    # 检查网络地址
    base_url=$(grep "base_url:" config.yaml | head -1 | awk '{print $2}' | tr -d '"')
    chain_id=$(grep "chain_id:" config.yaml | head -1 | awk '{print $2}')
    api_key=$(grep "api_key_private_key:" config.yaml | head -1 | awk '{print $2}' | tr -d '"')
    
    echo "  网络地址: $base_url"
    echo "  链ID: $chain_id"
    
    if [ "$api_key" == "YOUR_MAINNET_PRIVATE_KEY_HERE" ] || [ -z "$api_key" ] || [ "$api_key" == '""' ]; then
        echo -e "  私钥: ${RED}✗ 未配置${NC}"
        echo ""
        echo -e "${RED}⚠️  私钥未配置！这是连接失败的主要原因${NC}"
    else
        echo -e "  私钥: ${GREEN}✓ 已配置${NC} (${api_key:0:10}...)"
    fi
    
    # 验证网络
    if echo "$base_url" | grep -q "mainnet"; then
        echo -e "  网络: ${GREEN}✓ 主网${NC}"
    elif echo "$base_url" | grep -q "testnet"; then
        echo -e "  网络: ${YELLOW}⚠️  测试网${NC}"
    else
        echo -e "  网络: ${RED}✗ 未知${NC}"
    fi
else
    echo -e "${RED}✗ 配置文件不存在${NC}"
fi

echo ""

# 检查2: 网络连接
echo -e "${BLUE}[2/7]${NC} 测试网络连接"
echo ""

if [ -n "$base_url" ]; then
    # 提取域名
    domain=$(echo "$base_url" | sed 's|https://||' | sed 's|http://||' | cut -d'/' -f1)
    
    echo "测试连接到: $domain"
    
    # Ping 测试（可能被禁用）
    if ping -c 2 "$domain" > /dev/null 2>&1; then
        echo -e "  Ping: ${GREEN}✓ 可达${NC}"
    else
        echo -e "  Ping: ${YELLOW}⚠️  不可达（服务器可能禁用了 ICMP）${NC}"
    fi
    
    # HTTPS 测试
    if curl -s -I --connect-timeout 5 "$base_url" > /dev/null 2>&1; then
        echo -e "  HTTPS: ${GREEN}✓ 可连接${NC}"
    else
        echo -e "  HTTPS: ${RED}✗ 无法连接${NC}"
    fi
    
    # DNS 解析
    if nslookup "$domain" > /dev/null 2>&1; then
        ip=$(nslookup "$domain" | grep -A 1 "Name:" | grep "Address:" | awk '{print $2}' | head -1)
        echo -e "  DNS: ${GREEN}✓ 解析成功${NC} ($ip)"
    else
        echo -e "  DNS: ${RED}✗ 解析失败${NC}"
    fi
else
    echo -e "${RED}✗ 未找到 base_url${NC}"
fi

echo ""

# 检查3: 测试 API
echo -e "${BLUE}[3/7]${NC} 测试 Lighter API"
echo ""

if [ -n "$base_url" ]; then
    # 测试健康检查端点（如果有）
    echo "测试 API 可访问性..."
    
    response=$(curl -s -w "\n%{http_code}" --connect-timeout 10 "$base_url/api/v1/markets" 2>&1)
    http_code=$(echo "$response" | tail -1)
    
    if [ "$http_code" == "200" ]; then
        echo -e "  API 状态: ${GREEN}✓ 正常 (HTTP $http_code)${NC}"
    elif [ "$http_code" == "503" ]; then
        echo -e "  API 状态: ${RED}✗ 服务不可用 (HTTP 503)${NC}"
    elif [ -z "$http_code" ] || [ "$http_code" == "000" ]; then
        echo -e "  API 状态: ${RED}✗ 连接失败${NC}"
    else
        echo -e "  API 状态: ${YELLOW}⚠️  HTTP $http_code${NC}"
    fi
fi

echo ""

# 检查4: 检查量化交易程序日志
echo -e "${BLUE}[4/7]${NC} 检查量化交易程序日志"
echo ""

if [ -f "logs/quant_trading.log" ]; then
    echo "查找连接错误..."
    errors=$(grep -i "error\|exception\|failed\|nonce\|503" logs/quant_trading.log | tail -10)
    
    if [ -n "$errors" ]; then
        echo -e "${YELLOW}最近的错误:${NC}"
        echo "$errors"
    else
        echo -e "${GREEN}✓ 未发现明显错误${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  量化交易日志文件不存在${NC}"
    echo "  量化交易系统可能未启动"
fi

echo ""

# 检查5: 检查主程序是否运行
echo -e "${BLUE}[5/7]${NC} 检查量化交易程序状态"
echo ""

quant_pid=$(ps aux | grep "python.*main.py.*config" | grep -v grep | awk '{print $2}' | head -1)

if [ -n "$quant_pid" ]; then
    echo -e "${GREEN}✓ 量化交易程序运行中 (PID: $quant_pid)${NC}"
    echo "  命令: $(ps -p $quant_pid -o cmd= | cut -c1-80)"
else
    echo -e "${YELLOW}⚠️  量化交易程序未运行${NC}"
    echo "  这是连接中断的可能原因"
fi

echo ""

# 检查6: 检查私钥配置
echo -e "${BLUE}[6/7]${NC} 验证私钥配置"
echo ""

if [ -f "venv/bin/python" ]; then
    PYTHON_CMD="venv/bin/python"
else
    PYTHON_CMD="python3"
fi

$PYTHON_CMD << 'EOF'
import sys
import os
sys.path.insert(0, '.')

try:
    from quant_trading.utils.config import Config
    
    if os.path.exists('config.yaml'):
        config = Config.from_file('config.yaml')
        
        api_key = config.lighter_config.get('api_key_private_key', '')
        
        if not api_key or api_key == 'YOUR_MAINNET_PRIVATE_KEY_HERE' or api_key == '':
            print("✗ 私钥未配置")
            print("  这是连接失败的主要原因")
            print("")
            print("  请编辑 config.yaml 并设置:")
            print("  api_key_private_key: \"0x您的64位十六进制私钥\"")
        elif api_key.startswith('0x') and len(api_key) == 66:
            print("✓ 私钥格式正确")
        else:
            print("⚠️  私钥格式可能有问题")
            print(f"  长度: {len(api_key)} (应为66)")
            print(f"  前缀: {api_key[:4]} (应为0x)")
    else:
        print("✗ 配置文件不存在")
        
except Exception as e:
    print(f"✗ 配置加载失败: {e}")
EOF

echo ""

# 检查7: 防火墙和网络
echo -e "${BLUE}[7/7]${NC} 检查网络和防火墙"
echo ""

# 检查是否能访问外部网络
if curl -s -I --connect-timeout 5 https://www.google.com > /dev/null 2>&1; then
    echo -e "  外部网络: ${GREEN}✓ 正常${NC}"
else
    echo -e "  外部网络: ${YELLOW}⚠️  可能受限${NC}"
fi

# 检查防火墙状态
if command -v ufw &> /dev/null; then
    ufw_status=$(sudo ufw status 2>/dev/null | head -1)
    echo "  UFW 防火墙: $ufw_status"
fi

echo ""

# 总结
echo "=========================================================="
echo -e "${CYAN}诊断总结${NC}"
echo "=========================================================="
echo ""

if [ "$api_key" == "YOUR_MAINNET_PRIVATE_KEY_HERE" ] || [ -z "$api_key" ]; then
    echo -e "${RED}主要问题: 私钥未配置${NC}"
    echo ""
    echo "解决方案:"
    echo "  1. 编辑配置文件:"
    echo "     nano config.yaml"
    echo ""
    echo "  2. 找到这一行:"
    echo "     api_key_private_key: \"YOUR_MAINNET_PRIVATE_KEY_HERE\""
    echo ""
    echo "  3. 替换为您的真实私钥:"
    echo "     api_key_private_key: \"0x您的64位十六进制私钥\""
    echo ""
    echo "  4. 保存并重启量化交易程序"
elif [ -z "$quant_pid" ]; then
    echo -e "${YELLOW}主要问题: 量化交易程序未运行${NC}"
    echo ""
    echo "解决方案:"
    echo "  启动量化交易程序:"
    echo "  python3 main.py --config config.yaml"
else
    echo -e "${GREEN}配置看起来正常${NC}"
    echo ""
    echo "如果仍有连接问题，检查:"
    echo "  1. 查看详细日志: tail -f logs/quant_trading.log"
    echo "  2. 检查网络连接"
    echo "  3. 验证私钥是否有效"
    echo "  4. 检查 Lighter 交易所是否正常运作"
fi

echo ""
echo "=========================================================="

