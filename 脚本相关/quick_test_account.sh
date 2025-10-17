#!/bin/bash
# 快速测试账户数据脚本

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}快速测试账户数据${NC}"
echo "===================="
echo ""

# 检测 Python
PYTHON_CMD="python3"
command -v python3 &> /dev/null || PYTHON_CMD="python"

# 测试 1: 检查后端
echo -e "${CYAN}1. 检查后端服务...${NC}"
if curl -s http://localhost:8000/api/health >/dev/null 2>&1; then
    echo -e "${GREEN}✓ 后端运行中${NC}"
else
    echo -e "${RED}✗ 后端未运行${NC}"
    echo "请启动: cd web_backend && python3 -m uvicorn main:app --host 0.0.0.0 --port 8000"
    exit 1
fi
echo ""

# 测试 2: 获取账户信息
echo -e "${CYAN}2. 测试账户信息 API...${NC}"

$PYTHON_CMD << 'EOF'
import asyncio
import sys
import os

sys.path.insert(0, os.getcwd())

async def test():
    from web_backend.services.trading_service import TradingService
    
    service = TradingService()
    info = await service.get_account_info()
    
    print(f"可用余额: {info['available_balance']} USDT")
    print(f"总余额: {info['balance']} USDT")
    print(f"保证金: {info['margin_balance']} USDT")
    print(f"未实现盈亏: {info['unrealized_pnl']} USDT")
    print()
    
    if info['available_balance'] == 9500.0:
        print("⚠️  使用模拟数据")
        print("💡 配置 config.yaml 中的私钥以使用真实数据")
        return False
    else:
        print("✓ 使用真实 Lighter 账户数据")
        return True

result = asyncio.run(test())
sys.exit(0 if result else 1)
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 获取真实账户数据成功${NC}"
else
    echo -e "${YELLOW}⚠️  使用模拟数据${NC}"
fi

echo ""

# 测试 3: 检查配置
echo -e "${CYAN}3. 检查配置文件...${NC}"

$PYTHON_CMD << 'EOF'
import yaml

with open('config.yaml') as f:
    config = yaml.safe_load(f)
    
api_key = config.get('lighter', {}).get('api_key_private_key', '')

if api_key in ['YOUR_MAINNET_PRIVATE_KEY_HERE', 'YOUR_TESTNET_PRIVATE_KEY_HERE', '']:
    print("❌ 私钥未配置")
    print()
    print("配置方法:")
    print("  nano config.yaml")
    print("  # 修改:")
    print("  lighter:")
    print("    api_key_private_key: \"0x您的私钥\"")
elif api_key.startswith('0x') and len(api_key) in [66, 80]:
    print(f"✓ 私钥已配置 ({api_key[:10]}...)")
    if len(api_key) == 80:
        print(f"  格式: Lighter 扩展格式 (80位)")
    else:
        print(f"  格式: 标准格式 (66位)")
elif len(api_key) in [64, 78]:
    print(f"⚠️  私钥已配置但缺少 0x 前缀 (长度: {len(api_key)})")
    print(f"  建议在私钥前添加 '0x'")
else:
    print(f"⚠️  私钥格式可能有误")
    print(f"  长度: {len(api_key)} (支持: 66位或80位)")
    print(f"  前缀: {api_key[:4] if len(api_key) >= 4 else api_key}")
EOF

echo ""
echo "===================="
echo -e "${GREEN}测试完成${NC}"
echo ""

