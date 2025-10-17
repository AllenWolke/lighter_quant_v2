#!/bin/bash
# Lighter 配置修复和验证脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Lighter 量化交易系统 - 配置修复和验证工具             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

CONFIG_FILE="config.yaml"

# 步骤1: 检查配置文件
echo -e "${CYAN}[步骤 1/4] 检查配置文件${NC}"
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}✗ 配置文件不存在: $CONFIG_FILE${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 配置文件存在${NC}"
echo ""

# 步骤2: 读取配置
echo -e "${CYAN}[步骤 2/4] 读取当前配置${NC}"

BASE_URL=$(grep "base_url:" "$CONFIG_FILE" | grep -v "^#" | head -1 | sed 's/.*base_url: *"\([^"]*\)".*/\1/')
PRIVATE_KEY=$(grep "api_key_private_key:" "$CONFIG_FILE" | grep -v "^#" | head -1 | sed 's/.*api_key_private_key: *"\([^"]*\)".*/\1/')
CHAIN_ID=$(grep "chain_id:" "$CONFIG_FILE" | grep -v "^#" | head -1 | awk '{print $2}')

echo -e "  网络地址: ${CYAN}$BASE_URL${NC}"
echo -e "  链ID: ${CYAN}$CHAIN_ID${NC}"

# 检查私钥状态
if [ "$PRIVATE_KEY" = "YOUR_MAINNET_PRIVATE_KEY_HERE" ] || [ "$PRIVATE_KEY" = "YOUR_TESTNET_PRIVATE_KEY_HERE" ]; then
    echo -e "  私钥: ${RED}✗ 未配置${NC}"
    PRIVATE_KEY_OK=false
elif [[ $PRIVATE_KEY == 0x* ]]; then
    echo -e "  私钥: ${GREEN}✓ 已配置 (${PRIVATE_KEY:0:12}...)${NC}"
    PRIVATE_KEY_OK=true
else
    echo -e "  私钥: ${YELLOW}⚠️  已配置但可能缺少 0x 前缀 (${PRIVATE_KEY:0:12}...)${NC}"
    PRIVATE_KEY_OK=partial
fi
echo ""

# 步骤3: 私钥配置
echo -e "${CYAN}[步骤 3/4] 配置私钥${NC}"

if [ "$PRIVATE_KEY_OK" = "false" ]; then
    echo -e "${YELLOW}私钥未配置，需要手动配置${NC}"
    echo ""
    echo -e "${CYAN}配置方法:${NC}"
    echo -e "  1. 打开配置文件:"
    echo -e "     ${GREEN}nano $CONFIG_FILE${NC}"
    echo ""
    echo -e "  2. 找到这一行:"
    echo -e "     ${YELLOW}api_key_private_key: \"YOUR_MAINNET_PRIVATE_KEY_HERE\"${NC}"
    echo ""
    echo -e "  3. 修改为您的私钥:"
    echo -e "     ${GREEN}api_key_private_key: \"0x您的64位私钥\"${NC}"
    echo ""
    echo -e "  4. 保存退出: Ctrl+X → Y → Enter"
    echo ""
    echo -e "${RED}❌ 私钥未配置，无法继续${NC}"
    exit 1
elif [ "$PRIVATE_KEY_OK" = "partial" ]; then
    echo -e "${YELLOW}检测到私钥可能缺少 0x 前缀${NC}"
    echo -e "当前私钥前缀: ${CYAN}${PRIVATE_KEY:0:10}${NC}"
    echo ""
    read -p "是否自动添加 0x 前缀？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # 备份配置文件
        cp "$CONFIG_FILE" "${CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
        echo -e "${GREEN}✓ 已备份配置文件${NC}"
        
        # 添加 0x 前缀
        sed -i "s|api_key_private_key: \"$PRIVATE_KEY\"|api_key_private_key: \"0x$PRIVATE_KEY\"|g" "$CONFIG_FILE"
        echo -e "${GREEN}✓ 已添加 0x 前缀${NC}"
        PRIVATE_KEY="0x$PRIVATE_KEY"
        PRIVATE_KEY_OK=true
    else
        echo -e "${YELLOW}跳过自动修复${NC}"
    fi
else
    echo -e "${GREEN}✓ 私钥配置正确${NC}"
fi
echo ""

# 步骤4: 验证配置
echo -e "${CYAN}[步骤 4/4] 验证配置${NC}"

# 使用 Python 验证配置
python3 << EOF
import sys
import yaml

try:
    # 读取配置文件
    with open("$CONFIG_FILE", 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 验证必要字段
    lighter_config = config.get('lighter', {})
    base_url = lighter_config.get('base_url', '')
    private_key = lighter_config.get('api_key_private_key', '')
    chain_id = lighter_config.get('chain_id', 0)
    
    print("Python 配置验证:")
    print(f"  网络地址: {base_url}")
    print(f"  链ID: {chain_id}")
    print(f"  私钥长度: {len(private_key)}")
    print(f"  私钥前缀: {private_key[:10]}")
    
    # 验证网络地址
    if not base_url or base_url == "":
        print("\n❌ 错误: base_url 为空")
        sys.exit(1)
    
    if not base_url.startswith("http"):
        print("\n❌ 错误: base_url 格式不正确")
        sys.exit(1)
    
    # 验证私钥
    if private_key in ["YOUR_MAINNET_PRIVATE_KEY_HERE", "YOUR_TESTNET_PRIVATE_KEY_HERE"]:
        print("\n❌ 错误: 私钥未配置")
        sys.exit(1)
    
    if not private_key.startswith("0x"):
        print("\n⚠️  警告: 私钥缺少 0x 前缀")
    
    if len(private_key) != 66:  # 0x + 64 hex chars
        print(f"\n⚠️  警告: 私钥长度不正确 (期望66位，实际{len(private_key)}位)")
    
    print("\n✓ 配置验证通过")
    sys.exit(0)
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Python 配置验证通过${NC}"
else
    echo -e "${RED}✗ Python 配置验证失败${NC}"
    exit 1
fi
echo ""

# 最终总结
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                     配置验证完成                           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ "$PRIVATE_KEY_OK" = "true" ]; then
    echo -e "${GREEN}✅ 配置完整，可以启动系统${NC}"
    echo ""
    echo -e "${CYAN}下一步:${NC}"
    echo -e "  1. 测试网络连接:"
    echo -e "     ${GREEN}curl -I $BASE_URL${NC}"
    echo ""
    echo -e "  2. 启动量化交易程序:"
    echo -e "     ${GREEN}python3 main.py --config $CONFIG_FILE${NC}"
    echo ""
    echo -e "  3. 查看日志:"
    echo -e "     ${GREEN}tail -f logs/quant_trading.log${NC}"
else
    echo -e "${YELLOW}⚠️  配置不完整，请手动配置私钥${NC}"
    echo ""
    echo -e "${CYAN}配置命令:${NC}"
    echo -e "  ${GREEN}nano $CONFIG_FILE${NC}"
fi

echo ""

