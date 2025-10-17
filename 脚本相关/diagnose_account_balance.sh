#!/bin/bash
# 诊断账户余额问题脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    账户余额诊断工具                                       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

PYTHON_CMD="python3"
command -v python3 &> /dev/null || PYTHON_CMD="python"

# ============================================================================
# 步骤 1: 检查配置文件
# ============================================================================
echo -e "${CYAN}[1/6] 检查配置文件${NC}"
echo ""

$PYTHON_CMD << 'EOF'
import yaml
import sys

try:
    with open('config.yaml') as f:
        config = yaml.safe_load(f)
    
    lighter = config.get('lighter', {})
    api_key = lighter.get('api_key_private_key', '')
    
    print(f"配置文件: ✓ 存在")
    print(f"base_url: {lighter.get('base_url')}")
    print(f"account_index: {lighter.get('account_index')}")
    print(f"chain_id: {lighter.get('chain_id')}")
    print()
    
    # 检查私钥
    print("私钥检查:")
    print(f"  长度: {len(api_key)}")
    
    if api_key in ['YOUR_MAINNET_PRIVATE_KEY_HERE', 'YOUR_TESTNET_PRIVATE_KEY_HERE', '']:
        print(f"  状态: ❌ 未配置")
        print()
        print("⚠️  私钥未配置！系统将使用模拟数据。")
        sys.exit(1)
    elif api_key.startswith('0x'):
        print(f"  前缀: ✓ 有 0x")
        print(f"  前10位: {api_key[:10]}...")
        
        if len(api_key) == 80:
            print(f"  格式: ✓ Lighter 扩展格式 (80位)")
        elif len(api_key) == 66:
            print(f"  格式: ✓ 标准以太坊格式 (66位)")
        else:
            print(f"  格式: ⚠️  长度不标准 ({len(api_key)}位)")
        
        print(f"  状态: ✓ 已配置")
    else:
        print(f"  前缀: ⚠️  缺少 0x")
        print(f"  状态: ⚠️  格式可能有误")
    
except Exception as e:
    print(f"✗ 读取配置失败: {e}")
    sys.exit(1)
EOF

CONFIG_CHECK=$?

echo ""

# ============================================================================
# 步骤 2: 测试网络连接
# ============================================================================
echo -e "${CYAN}[2/6] 测试网络连接${NC}"
echo ""

BASE_URL=$($PYTHON_CMD -c "import yaml; print(yaml.safe_load(open('config.yaml'))['lighter']['base_url'])")

echo "测试连接到: $BASE_URL"

if curl -s -I "$BASE_URL" | head -1 | grep -q "200\|301\|302"; then
    echo -e "${GREEN}✓ 网络连接正常${NC}"
else
    echo -e "${YELLOW}⚠️  网络连接可能有问题${NC}"
fi

echo ""

# ============================================================================
# 步骤 3: 测试 Lighter API
# ============================================================================
echo -e "${CYAN}[3/6] 测试 Lighter API 调用${NC}"
echo ""

$PYTHON_CMD << 'EOF'
import asyncio
import sys
import os

sys.path.insert(0, os.getcwd())

async def test_lighter_api():
    try:
        from lighter import ApiClient, Configuration
        from lighter.api import AccountApi
        from quant_trading.utils.config import Config
        
        config = Config.from_file('config.yaml')
        
        configuration = Configuration(
            host=config.lighter_config.get("base_url")
        )
        
        # 使用 async with 确保资源正确关闭
        async with ApiClient(configuration) as api_client:
            account_api = AccountApi(api_client)
            account_index = config.lighter_config.get("account_index", 0)
            
            print(f"正在调用 Lighter API (账户索引: {account_index})...")
            
            response = await account_api.account(
                by="index",
                value=str(account_index)
            )
            
            if response and response.code == 200:
                print("✓ API 调用成功")
                print(f"  状态码: {response.code}")
                print(f"  消息: {response.message}")
                print(f"  账户数量: {response.total}")
                print()
                
                if response.accounts:
                    account = response.accounts[0]
                    print("账户详细信息:")
                    print(f"  collateral (保证金): {account.collateral}")
                    print(f"  available_balance (可用余额): {account.available_balance}")
                    
                    if hasattr(account, 'total_asset_value'):
                        print(f"  total_asset_value (总资产): {account.total_asset_value}")
                    
                    print(f"  status (状态): {account.status}")
                    
                    if hasattr(account, 'positions') and account.positions:
                        print(f"  positions (持仓): {len(account.positions)} 个")
                        
                        total_unrealized = 0.0
                        for i, pos in enumerate(account.positions[:5]):  # 只显示前5个
                            if hasattr(pos, 'unrealized_pnl') and pos.unrealized_pnl:
                                pnl = float(pos.unrealized_pnl)
                                total_unrealized += pnl
                                print(f"    [{i+1}] 未实现盈亏: {pnl}")
                        
                        print(f"  总未实现盈亏: {total_unrealized}")
                    else:
                        print(f"  positions: 无持仓")
                    
                    return True
                else:
                    print("⚠️  账户列表为空")
                    return False
            else:
                print(f"✗ API 返回错误状态: {response.code if response else 'None'}")
                return False
                
    except Exception as e:
        print(f"✗ Lighter API 调用失败: {e}")
        import traceback
        traceback.print_exc()
        return False

result = asyncio.run(test_lighter_api())
sys.exit(0 if result else 1)
EOF

LIGHTER_API_TEST=$?

echo ""

# ============================================================================
# 步骤 4: 测试 TradingService
# ============================================================================
echo -e "${CYAN}[4/6] 测试 TradingService${NC}"
echo ""

$PYTHON_CMD << 'EOF'
import asyncio
import sys
import os

sys.path.insert(0, os.getcwd())

async def test_trading_service():
    try:
        from web_backend.services.trading_service import TradingService
        
        service = TradingService()
        info = await service.get_account_info()
        
        print("TradingService 返回的账户信息:")
        print(f"  balance: {info['balance']}")
        print(f"  available_balance: {info['available_balance']}")
        print(f"  margin_balance: {info['margin_balance']}")
        print(f"  unrealized_pnl: {info['unrealized_pnl']}")
        print(f"  total_pnl: {info['total_pnl']}")
        print(f"  margin_ratio: {info['margin_ratio']}")
        print(f"  risk_level: {info['risk_level']}")
        print()
        
        # 判断数据来源
        if info['available_balance'] == 9500.0:
            print("⚠️  使用模拟数据")
            return False
        else:
            print("✓ 使用真实 Lighter 数据")
            return True
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

result = asyncio.run(test_trading_service())
sys.exit(0 if result else 1)
EOF

TRADING_SERVICE_TEST=$?

echo ""

# ============================================================================
# 步骤 5: 对比 Lighter 网站数据
# ============================================================================
echo -e "${CYAN}[5/6] 对比数据说明${NC}"
echo ""

echo "请手动对比以下数据:"
echo ""
echo "1. 打开 Lighter 网站:"
echo "   https://mainnet.zklighter.elliot.ai (主网)"
echo "   https://testnet.zklighter.elliot.ai (测试网)"
echo ""
echo "2. 连接钱包并查看账户余额"
echo ""
echo "3. 访问 Dashboard:"
echo "   http://localhost:3000/dashboard"
echo ""
echo "4. 对比以下数值:"
echo "   - 可用余额 (Available Balance)"
echo "   - 保证金 (Collateral/Margin)"
echo "   - 总资产 (Total Asset Value)"
echo ""

if [ $LIGHTER_API_TEST -eq 0 ]; then
    echo -e "${GREEN}✓ Lighter API 已成功返回数据${NC}"
    echo "  Dashboard 应该显示上面显示的余额"
else
    echo -e "${YELLOW}⚠️  Lighter API 调用失败${NC}"
    echo "  Dashboard 将显示模拟数据"
fi

echo ""

# ============================================================================
# 步骤 6: 检查后端日志
# ============================================================================
echo -e "${CYAN}[6/6] 检查后端日志${NC}"
echo ""

if [ -f "logs/web_backend.log" ]; then
    echo "最近的账户相关日志:"
    echo ""
    tail -50 logs/web_backend.log | grep -E "账户|Lighter|API|available|collateral" | tail -10 || echo "  (无相关日志)"
else
    echo -e "${YELLOW}⚠️  日志文件不存在${NC}"
fi

echo ""

# ============================================================================
# 总结
# ============================================================================
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    诊断结果总结                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ $CONFIG_CHECK -eq 0 ] && [ $LIGHTER_API_TEST -eq 0 ] && [ $TRADING_SERVICE_TEST -eq 0 ]; then
    echo -e "${GREEN}✅ 所有测试通过 - 系统正在使用真实账户数据${NC}"
    echo ""
    echo "下一步:"
    echo "  1. 访问 Dashboard: http://localhost:3000/dashboard"
    echo "  2. 验证余额与 Lighter 网站一致"
    echo "  3. 如果仍有差异，请检查:"
    echo "     - 账户索引是否正确"
    echo "     - 是否选择了正确的网络 (主网/测试网)"
    echo "     - Lighter 网站和 Dashboard 是否使用同一个账户"
elif [ $CONFIG_CHECK -ne 0 ]; then
    echo -e "${RED}❌ 配置文件问题${NC}"
    echo ""
    echo "请配置 config.yaml 中的私钥:"
    echo "  nano config.yaml"
    echo "  # 设置:"
    echo "  lighter:"
    echo "    api_key_private_key: \"0x您的私钥\" (80位 Lighter 格式)"
else
    echo -e "${YELLOW}⚠️  部分测试失败 - 系统正在使用模拟数据${NC}"
    echo ""
    echo "可能的原因:"
    echo "  1. 私钥配置不正确"
    echo "  2. 账户索引不匹配"
    echo "  3. 网络连接问题"
    echo "  4. API 服务不可用"
    echo ""
    echo "建议:"
    echo "  1. 检查后端日志: tail -50 logs/web_backend.log"
    echo "  2. 验证私钥格式"
    echo "  3. 测试网络连接: curl $BASE_URL"
fi

echo ""
echo -e "${CYAN}查看详细日志:${NC}"
echo "  tail -f logs/web_backend.log | grep -i '账户\|lighter\|api'"
echo ""

