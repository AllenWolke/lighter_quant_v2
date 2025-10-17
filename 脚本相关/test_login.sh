#!/bin/bash

###############################################################################
# 测试登录功能
# 诊断为什么登录失败
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
echo "  登录功能诊断"
echo "=========================================================="
echo ""

# 检查1: 验证后端是否运行
echo -e "${BLUE}▶ 检查1: 后端服务状态${NC}"
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 后端服务运行正常${NC}"
else
    echo -e "${RED}✗ 后端服务未运行${NC}"
    echo "请先启动服务: ./start_all_services.sh"
    exit 1
fi
echo ""

# 检查2: 验证用户存在
echo -e "${BLUE}▶ 检查2: 验证用户${NC}"

if [ -f "venv/bin/python" ]; then
    PYTHON_CMD="venv/bin/python"
else
    PYTHON_CMD="python3"
fi

$PYTHON_CMD << 'EOF'
import sys
sys.path.insert(0, 'web_backend')

from core.database import SessionLocal
from core.security import verify_password
from models.user import User

db = SessionLocal()

try:
    # 查找 admin 用户
    user = db.query(User).filter(User.username == "admin").first()
    
    if not user:
        print("✗ admin用户不存在")
        sys.exit(1)
    
    print(f"✓ 用户存在: {user.username}")
    print(f"  ID: {user.id}")
    print(f"  邮箱: {user.email}")
    print(f"  激活状态: {user.is_active}")
    print(f"  超级用户: {user.is_superuser}")
    
    # 测试密码
    print("\n测试密码验证:")
    
    test_passwords = ["admin", "admin123", "Admin123"]
    password_ok = False
    
    for pwd in test_passwords:
        if verify_password(pwd, user.hashed_password):
            print(f"  ✓ 密码 '{pwd}' 验证通过")
            password_ok = True
            break
        else:
            print(f"  ✗ 密码 '{pwd}' 验证失败")
    
    if not password_ok:
        print("\n⚠️  所有测试密码都失败，需要重置密码")
        sys.exit(1)
    
except Exception as e:
    print(f"✗ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    db.close()
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ 用户验证失败${NC}"
    echo ""
    echo "解决方案:"
    echo "  ./force_restart.sh --clean-db"
    exit 1
fi

echo ""

# 检查3: 测试登录 API
echo -e "${BLUE}▶ 检查3: 测试登录 API${NC}"
echo ""

echo "测试 admin/admin123:"
response=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" \
  -w "\nHTTP_CODE:%{http_code}")

http_code=$(echo "$response" | grep "HTTP_CODE" | cut -d: -f2)
body=$(echo "$response" | grep -v "HTTP_CODE")

echo "响应代码: $http_code"
echo "响应内容: $body"
echo ""

if [ "$http_code" == "200" ]; then
    echo -e "${GREEN}✓ 登录 API 测试成功${NC}"
    echo ""
    echo "访问令牌已获取，登录功能正常"
elif [ "$http_code" == "401" ]; then
    echo -e "${RED}✗ 登录失败: 用户名或密码错误 (401)${NC}"
    echo ""
    echo "可能的原因:"
    echo "  1. 密码哈希不匹配"
    echo "  2. 用户未激活"
    echo "  3. 密码验证函数有问题"
    echo ""
    echo "解决方案:"
    echo "  ./force_restart.sh --clean-db"
elif [ "$http_code" == "422" ]; then
    echo -e "${RED}✗ 请求格式错误 (422)${NC}"
    echo ""
    echo "可能的原因:"
    echo "  1. 请求参数格式不正确"
    echo "  2. Pydantic 验证失败"
else
    echo -e "${YELLOW}⚠️  未知响应: HTTP $http_code${NC}"
fi

echo ""

# 检查4: 测试前端登录接口
echo -e "${BLUE}▶ 检查4: 测试前端登录接口 (JSON格式)${NC}"
echo ""

response2=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  -w "\nHTTP_CODE:%{http_code}")

http_code2=$(echo "$response2" | grep "HTTP_CODE" | cut -d: -f2)
body2=$(echo "$response2" | grep -v "HTTP_CODE")

echo "响应代码: $http_code2"
echo "响应内容: $body2"
echo ""

if [ "$http_code2" == "200" ] || [ "$http_code" == "200" ]; then
    echo -e "${GREEN}✅ 登录功能正常${NC}"
    echo ""
    echo "后端登录 API 工作正常"
    echo "如果前端仍无法登录，可能是前端问题:"
    echo "  1. 检查浏览器控制台 (F12)"
    echo "  2. 查看 Network 标签的请求详情"
    echo "  3. 检查 CORS 错误"
else
    echo -e "${RED}✗ 登录 API 异常${NC}"
    echo ""
    echo "需要修复后端登录逻辑"
fi

echo ""
echo "=========================================================="
echo "诊断完成"
echo "=========================================================="
echo ""

if [ "$http_code" == "200" ] || [ "$http_code2" == "200" ]; then
    echo -e "${GREEN}建议:${NC}"
    echo "  后端登录正常，如果前端仍无法登录:"
    echo "  1. 打开浏览器开发者工具 (F12)"
    echo "  2. 查看 Console 标签的错误信息"
    echo "  3. 查看 Network 标签的登录请求"
    echo "  4. 清除浏览器缓存后重试"
else
    echo -e "${YELLOW}建议:${NC}"
    echo "  后端登录异常，执行以下命令修复:"
    echo "  ./force_restart.sh --clean-db"
fi

echo ""

