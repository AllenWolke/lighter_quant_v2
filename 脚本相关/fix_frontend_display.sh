#!/bin/bash
# 修复前端显示问题脚本

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    前端账户金额显示修复工具                               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

PYTHON_CMD="python3"
command -v python3 &> /dev/null || PYTHON_CMD="python"

# ============================================================================
# 测试 1: 检查后端 API 响应格式
# ============================================================================
echo -e "${CYAN}[测试 1/4] 检查后端 API 响应格式${NC}"
echo ""

# 首先获取 token
echo "获取登录 Token..."
TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')

TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"accessToken":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
fi

if [ -z "$TOKEN" ]; then
    echo -e "${RED}✗ 登录失败${NC}"
    echo "请确保后端服务正在运行"
    exit 1
fi

echo -e "${GREEN}✓ 登录成功${NC}"
echo ""

# 获取账户信息
echo "调用 /api/trading/account..."
ACCOUNT_RESPONSE=$(curl -s http://localhost:8000/api/trading/account \
  -H "Authorization: Bearer $TOKEN")

echo "后端响应:"
echo "$ACCOUNT_RESPONSE" | $PYTHON_CMD -m json.tool 2>/dev/null || echo "$ACCOUNT_RESPONSE"
echo ""

# 检查响应格式
echo "检查字段名格式..."
$PYTHON_CMD << EOF
import json
import sys

response = '''$ACCOUNT_RESPONSE'''
try:
    data = json.loads(response)
    
    # 检查字段名
    has_camel = 'availableBalance' in data
    has_snake = 'available_balance' in data
    
    print(f"camelCase (availableBalance): {'✓' if has_camel else '✗'}")
    print(f"snake_case (available_balance): {'✓' if has_snake else '✗'}")
    print()
    
    if has_camel:
        print("✓ 响应使用 camelCase（前端兼容）")
        print(f"  availableBalance: {data.get('availableBalance', 'N/A')}")
        print(f"  marginBalance: {data.get('marginBalance', 'N/A')}")
        sys.exit(0)
    elif has_snake:
        print("⚠️  响应使用 snake_case（需要转换）")
        print(f"  available_balance: {data.get('available_balance', 'N/A')}")
        print(f"  margin_balance: {data.get('margin_balance', 'N/A')}")
        print()
        print("前端期望 camelCase 格式，后端需要配置别名")
        sys.exit(1)
    else:
        print("✗ 无法识别字段格式")
        sys.exit(1)
        
except Exception as e:
    print(f"✗ 解析响应失败: {e}")
    sys.exit(1)
EOF

API_FORMAT_TEST=$?

echo ""

# ============================================================================
# 测试 2: 验证 Pydantic 配置
# ============================================================================
echo -e "${CYAN}[测试 2/4] 验证 Pydantic 配置${NC}"
echo ""

cd web_backend

$PYTHON_CMD << 'EOF'
try:
    from schemas.trading import AccountInfo
    
    # 测试序列化
    test_data = {
        "balance": 10000.0,
        "available_balance": 9500.0,
        "margin_balance": 10000.0,
        "unrealized_pnl": 100.0,
        "total_pnl": 500.0,
        "margin_ratio": 0.05,
        "risk_level": "low"
    }
    
    account_info = AccountInfo(**test_data)
    
    # 序列化为 JSON (使用别名)
    json_str = account_info.model_dump_json(by_alias=True)
    
    print("✓ Pydantic 模型验证通过")
    print()
    print("序列化输出:")
    print(json_str)
    print()
    
    # 检查是否包含 camelCase
    if 'availableBalance' in json_str:
        print("✓ 序列化使用 camelCase")
    else:
        print("⚠️  序列化未使用 camelCase")
        
except Exception as e:
    print(f"✗ Pydantic 验证失败: {e}")
    import traceback
    traceback.print_exc()
EOF

cd ..

echo ""

# ============================================================================
# 测试 3: 检查 FastAPI 响应配置
# ============================================================================
echo -e "${CYAN}[测试 3/4] 检查 FastAPI 路由配置${NC}"
echo ""

echo "检查 trading.py 路由配置..."
if grep -q "response_model_by_alias=True" web_backend/api/routes/trading.py 2>/dev/null; then
    echo -e "${GREEN}✓ 路由配置了 by_alias${NC}"
else
    echo -e "${YELLOW}⚠️  路由未配置 by_alias${NC}"
    echo "需要在路由装饰器中添加: response_model_by_alias=True"
fi

echo ""

# ============================================================================
# 测试 4: 前端数据接收测试
# ============================================================================
echo -e "${CYAN}[测试 4/4] 前端数据接收测试${NC}"
echo ""

echo "请在浏览器中测试（http://localhost:3000/dashboard）:"
echo ""
echo "1. 打开浏览器开发者工具 (F12)"
echo "2. 切换到 Console 标签"
echo "3. 运行以下代码:"
echo ""
echo -e "${YELLOW}fetch('/api/trading/account', {"
echo "  headers: {"
echo "    'Authorization': 'Bearer ' + localStorage.getItem('token')"
echo "  }"
echo "})"
echo ".then(r => r.json())"
echo ".then(data => {"
echo "  console.log('API 响应:', data);"
echo "  console.log('availableBalance:', data.availableBalance);"
echo "  console.log('available_balance:', data.available_balance);"
echo "  "
echo "  if (data.availableBalance !== undefined) {"
echo "    console.log('✓ 使用 camelCase');"
echo "  } else if (data.available_balance !== undefined) {"
echo "    console.log('⚠️  使用 snake_case');"
echo "  }"
echo "})${NC}"
echo ""

# ============================================================================
# 总结和建议
# ============================================================================
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    诊断结果                                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ $API_FORMAT_TEST -eq 0 ]; then
    echo -e "${GREEN}✓ 后端 API 响应格式正确 (camelCase)${NC}"
    echo ""
    echo "如果前端仍显示 0，可能的原因:"
    echo "  1. 浏览器缓存问题 - 强制刷新: Ctrl+Shift+R"
    echo "  2. Token 过期 - 重新登录"
    echo "  3. 前端代码未更新 - 重启前端服务"
    echo ""
    echo "建议操作:"
    echo "  1. 重启后端: pkill -f uvicorn && cd web_backend && python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 &"
    echo "  2. 清除浏览器缓存: F12 → Application → Clear storage"
    echo "  3. 强制刷新: Ctrl+Shift+R"
else
    echo -e "${YELLOW}⚠️  后端 API 响应格式需要修复 (snake_case → camelCase)${NC}"
    echo ""
    echo "修复步骤:"
    echo "  1. 已更新 web_backend/schemas/trading.py"
    echo "  2. 重启后端服务:"
    echo "     pkill -f uvicorn"
    echo "     cd web_backend"
    echo "     python3 -m uvicorn main:app --host 0.0.0.0 --port 8000"
    echo "  3. 重新运行此脚本验证"
fi

echo ""
echo -e "${CYAN}查看后端日志:${NC}"
echo "  tail -f logs/web_backend.log | grep -i '账户\|account'"
echo ""

