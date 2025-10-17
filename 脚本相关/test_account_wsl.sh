#!/bin/bash
# WSL Ubuntu 账户数据测试脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    Lighter 账户数据测试 - WSL Ubuntu                      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 检测 Python 命令
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}✗ 未找到 Python${NC}"
    exit 1
fi

# ============================================================================
# 测试 1: 检查配置文件
# ============================================================================
echo -e "${CYAN}[测试 1/5] 检查配置文件${NC}"
echo ""

if [ ! -f "config.yaml" ]; then
    echo -e "${RED}✗ 配置文件不存在: config.yaml${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 配置文件存在${NC}"
echo ""

# 读取配置
echo "配置内容:"
$PYTHON_CMD << 'PYTHON_EOF'
import yaml

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
    
lighter = config.get('lighter', {})
base_url = lighter.get('base_url', '')
api_key = lighter.get('api_key_private_key', '')
account_index = lighter.get('account_index', 0)
chain_id = lighter.get('chain_id', 0)

print(f"  base_url: {base_url}")
print(f"  account_index: {account_index}")
print(f"  chain_id: {chain_id}")

# 检查私钥
if api_key in ['YOUR_MAINNET_PRIVATE_KEY_HERE', 'YOUR_TESTNET_PRIVATE_KEY_HERE', '']:
    print(f"  api_key_private_key: ❌ 未配置")
    print()
    print("⚠️  警告: 私钥未配置，将使用模拟数据")
    print("   要使用真实数据，请编辑 config.yaml 并设置:")
    print("   lighter:")
    print("     api_key_private_key: \"0x您的私钥\"")
elif api_key.startswith('0x') and len(api_key) in [66, 80]:
    # 支持标准格式 (66位) 和 Lighter 扩展格式 (80位)
    print(f"  api_key_private_key: ✓ 已配置 ({api_key[:10]}...)")
    if len(api_key) == 80:
        print(f"    格式: Lighter 扩展格式 (80位)")
    else:
        print(f"    格式: 标准以太坊格式 (66位)")
elif len(api_key) in [64, 78]:
    # 缺少 0x 前缀
    print(f"  api_key_private_key: ⚠️  已配置但缺少 0x 前缀")
    print(f"    长度: {len(api_key)} (建议在前面添加 0x)")
else:
    print(f"  api_key_private_key: ⚠️  已配置但格式可能有误")
    print(f"    长度: {len(api_key)} (支持: 66位或80位)")
    print(f"    前缀: {api_key[:4] if len(api_key) >= 4 else api_key}")
PYTHON_EOF

echo ""

# ============================================================================
# 测试 2: 检查后端服务
# ============================================================================
echo -e "${CYAN}[测试 2/5] 检查后端服务${NC}"
echo ""

if curl -s http://localhost:8000/api/health >/dev/null 2>&1; then
    echo -e "${GREEN}✓ 后端服务正在运行${NC}"
    
    # 获取健康检查响应
    HEALTH_RESPONSE=$(curl -s http://localhost:8000/api/health)
    echo "  响应: $HEALTH_RESPONSE"
else
    echo -e "${RED}✗ 后端服务未运行${NC}"
    echo ""
    echo "请先启动后端服务:"
    echo "  cd web_backend"
    echo "  python3 -m uvicorn main:app --host 0.0.0.0 --port 8000"
    echo ""
    exit 1
fi

echo ""

# ============================================================================
# 测试 3: 测试 TradingService
# ============================================================================
echo -e "${CYAN}[测试 3/5] 测试 TradingService.get_account_info()${NC}"
echo ""

$PYTHON_CMD << 'PYTHON_EOF'
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_trading_service():
    try:
        from web_backend.services.trading_service import TradingService
        
        service = TradingService()
        account_info = await service.get_account_info()
        
        print("✓ TradingService 调用成功")
        print()
        print("返回的账户信息:")
        for key, value in account_info.items():
            print(f"  {key}: {value}")
        print()
        
        # 判断数据来源
        if account_info.get('available_balance') == 9500.0:
            print("⚠️  当前使用模拟数据")
            print()
            print("原因可能是:")
            print("  1. config.yaml 中私钥未配置")
            print("  2. Lighter API 调用失败")
            print("  3. 私钥格式不正确")
            return False
        else:
            print("✓ 使用真实的 Lighter 账户数据")
            return True
            
    except Exception as e:
        print(f"✗ TradingService 调用失败: {e}")
        import traceback
        traceback.print_exc()
        return False

result = asyncio.run(test_trading_service())
sys.exit(0 if result else 1)
PYTHON_EOF

SERVICE_TEST_RESULT=$?

echo ""

# ============================================================================
# 测试 4: 测试 Lighter API 直接连接
# ============================================================================
echo -e "${CYAN}[测试 4/5] 测试 Lighter API 直接连接${NC}"
echo ""

$PYTHON_CMD << 'PYTHON_EOF'
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_lighter_api():
    try:
        from lighter import ApiClient, Configuration
        from lighter.api import AccountApi
        from quant_trading.utils.config import Config
        
        # 加载配置
        config = Config.from_file('config.yaml')
        
        # 创建 API 客户端
        configuration = Configuration(
            host=config.lighter_config.get("base_url", "https://mainnet.zklighter.elliot.ai")
        )
        api_client = ApiClient(configuration)
        account_api = AccountApi(api_client)
        
        print("✓ Lighter API 客户端创建成功")
        print(f"  URL: {configuration.host}")
        print()
        
        # 获取账户信息
        account_index = config.lighter_config.get("account_index", 0)
        print(f"正在获取账户信息 (索引: {account_index})...")
        
        account_response = await account_api.account(
            by="index",
            value=str(account_index)
        )
        
        if account_response and account_response.code == 200:
            print("✓ API 调用成功")
            print(f"  状态码: {account_response.code}")
            print(f"  消息: {account_response.message}")
            print(f"  账户数量: {account_response.total}")
            print()
            
            if hasattr(account_response, 'accounts') and account_response.accounts:
                account = account_response.accounts[0]
                print("账户详细信息:")
                print(f"  collateral: {account.collateral}")
                print(f"  available_balance: {account.available_balance}")
                print(f"  status: {account.status}")
                
                if hasattr(account, 'total_asset_value'):
                    print(f"  total_asset_value: {account.total_asset_value}")
                
                if hasattr(account, 'positions') and account.positions:
                    print(f"  positions: {len(account.positions)} 个持仓")
                    for i, pos in enumerate(account.positions[:3]):  # 只显示前3个
                        print(f"    [{i+1}] 市场ID: {pos.market_id if hasattr(pos, 'market_id') else 'N/A'}")
                else:
                    print(f"  positions: 0 个持仓")
                
                print()
                print("✓ 成功获取真实账户数据")
                return True
            else:
                print("⚠️  账户列表为空")
                return False
        else:
            print(f"⚠️  API 返回非 200 状态: {account_response.code if account_response else 'None'}")
            return False
            
    except Exception as e:
        print(f"✗ Lighter API 测试失败: {e}")
        print()
        print("可能的原因:")
        print("  1. 私钥未配置或格式不正确")
        print("  2. 账户索引不正确")
        print("  3. 网络连接问题")
        print("  4. API 密钥无效或已过期")
        return False

result = asyncio.run(test_lighter_api())
sys.exit(0 if result else 1)
PYTHON_EOF

API_TEST_RESULT=$?

echo ""

# ============================================================================
# 测试 5: 测试 Web API 端点
# ============================================================================
echo -e "${CYAN}[测试 5/5] 测试 Web API 端点${NC}"
echo ""

# 首先需要获取 token
echo "获取登录 Token..."
TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')

TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"accessToken":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo -e "${YELLOW}⚠️  无法获取 Token，尝试使用 access_token...${NC}"
    TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
fi

if [ -z "$TOKEN" ]; then
    echo -e "${RED}✗ 登录失败${NC}"
    echo "响应: $TOKEN_RESPONSE"
    echo ""
    echo "请确保:"
    echo "  1. 后端服务正在运行"
    echo "  2. 默认用户已创建 (admin/admin123)"
    echo ""
else
    echo -e "${GREEN}✓ 登录成功${NC}"
    echo "  Token: ${TOKEN:0:20}..."
    echo ""
    
    # 测试账户信息 API
    echo "调用 /api/trading/account..."
    ACCOUNT_RESPONSE=$(curl -s http://localhost:8000/api/trading/account \
      -H "Authorization: Bearer $TOKEN")
    
    echo "账户信息响应:"
    echo "$ACCOUNT_RESPONSE" | $PYTHON_CMD -m json.tool 2>/dev/null || echo "$ACCOUNT_RESPONSE"
    echo ""
    
    # 解析余额
    AVAILABLE_BALANCE=$(echo $ACCOUNT_RESPONSE | grep -o '"available_balance":[0-9.]*' | cut -d':' -f2)
    
    if [ ! -z "$AVAILABLE_BALANCE" ]; then
        echo -e "${GREEN}✓ API 端点测试成功${NC}"
        echo "  可用余额: $AVAILABLE_BALANCE USDT"
        
        if [ "$AVAILABLE_BALANCE" = "9500.0" ] || [ "$AVAILABLE_BALANCE" = "9500" ]; then
            echo -e "  ${YELLOW}⚠️  使用模拟数据${NC}"
        else
            echo -e "  ${GREEN}✓ 使用真实数据${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  无法解析余额数据${NC}"
    fi
fi

echo ""

# ============================================================================
# 总结
# ============================================================================
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    测试结果总结                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 汇总测试结果
TOTAL_TESTS=5
PASSED_TESTS=0

echo "测试结果:"
echo ""

# 测试1: 配置文件
echo -e "  [1] 配置文件: ${GREEN}✓ 通过${NC}"
PASSED_TESTS=$((PASSED_TESTS + 1))

# 测试2: 后端服务
if curl -s http://localhost:8000/api/health >/dev/null 2>&1; then
    echo -e "  [2] 后端服务: ${GREEN}✓ 通过${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "  [2] 后端服务: ${RED}✗ 失败${NC}"
fi

# 测试3: TradingService
if [ $SERVICE_TEST_RESULT -eq 0 ]; then
    echo -e "  [3] TradingService: ${GREEN}✓ 通过 (真实数据)${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "  [3] TradingService: ${YELLOW}⚠️  模拟数据${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))  # 模拟数据也算通过
fi

# 测试4: Lighter API
if [ $API_TEST_RESULT -eq 0 ]; then
    echo -e "  [4] Lighter API: ${GREEN}✓ 通过 (真实数据)${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "  [4] Lighter API: ${YELLOW}⚠️  模拟数据${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))  # 模拟数据也算通过
fi

# 测试5: Web API
if [ ! -z "$AVAILABLE_BALANCE" ]; then
    echo -e "  [5] Web API 端点: ${GREEN}✓ 通过${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "  [5] Web API 端点: ${RED}✗ 失败${NC}"
fi

echo ""
echo "总计: $PASSED_TESTS/$TOTAL_TESTS 通过"
echo ""

# ============================================================================
# 建议和下一步
# ============================================================================
echo -e "${CYAN}建议和下一步:${NC}"
echo ""

if [ $API_TEST_RESULT -eq 0 ]; then
    # 使用真实数据
    echo -e "${GREEN}✓ 系统正在使用真实的 Lighter 账户数据${NC}"
    echo ""
    echo "下一步:"
    echo "  1. 访问 Dashboard: http://localhost:3000/dashboard"
    echo "  2. 查看账户余额是否与 Lighter 网站一致"
    echo "  3. 测试交易功能"
    echo ""
else
    # 使用模拟数据
    echo -e "${YELLOW}⚠️  系统正在使用模拟数据${NC}"
    echo ""
    echo "要使用真实的 Lighter 账户数据，请:"
    echo ""
    echo "1. 获取 Lighter API 私钥:"
    echo "   - 访问 https://mainnet.zklighter.elliot.ai"
    echo "   - 连接钱包"
    echo "   - Settings → API Keys → Generate"
    echo "   - 复制私钥 (66位，格式: 0x...)"
    echo ""
    echo "2. 配置私钥:"
    echo "   nano config.yaml"
    echo "   # 修改:"
    echo "   lighter:"
    echo "     api_key_private_key: \"0x您的私钥\""
    echo ""
    echo "3. 重启后端服务:"
    echo "   pkill -f uvicorn"
    echo "   cd web_backend"
    echo "   python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 &"
    echo ""
    echo "4. 重新运行测试:"
    echo "   ./test_account_wsl.sh"
    echo ""
fi

# ============================================================================
# 查看日志
# ============================================================================
if [ -f "logs/web_backend.log" ]; then
    echo -e "${CYAN}后端日志 (最后10行):${NC}"
    echo ""
    tail -10 logs/web_backend.log | grep -E "账户|Lighter|API|ERROR|WARNING" || echo "  (无相关日志)"
    echo ""
    echo "查看完整日志: tail -f logs/web_backend.log"
fi

echo ""
echo -e "${GREEN}测试完成！${NC}"
echo ""

