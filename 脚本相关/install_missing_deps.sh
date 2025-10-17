#!/bin/bash

###############################################################################
# 安装缺失的依赖
# 快速修复 email-validator 和其他可能缺失的包
###############################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "===================================================="
echo "  安装缺失的依赖"
echo "===================================================="
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${RED}[ERROR]${NC} 虚拟环境不存在"
    echo "请先运行: python3 -m venv venv"
    exit 1
fi

# 激活虚拟环境
echo -e "${BLUE}[INFO]${NC} 激活虚拟环境..."
source venv/bin/activate

# 升级 pip
echo -e "${BLUE}[INFO]${NC} 升级 pip..."
pip install --upgrade pip -q

# 安装关键缺失的包
echo -e "${BLUE}[INFO]${NC} 安装缺失的依赖包..."
echo ""

# 1. email-validator
echo "1. 安装 email-validator..."
pip install email-validator>=2.0.0 -q
echo -e "   ${GREEN}✓${NC} email-validator 已安装"

# 2. pydantic[email]
echo "2. 安装 pydantic[email]..."
pip install "pydantic[email]>=2.5.0" -q
echo -e "   ${GREEN}✓${NC} pydantic[email] 已安装"

# 3. 其他可能缺失的包
echo "3. 检查其他依赖..."
pip install fastapi>=0.104.0 \
            uvicorn[standard]>=0.24.0 \
            pydantic-settings>=2.1.0 \
            sqlalchemy>=2.0.0 \
            passlib[bcrypt]>=1.7.4 \
            python-jose[cryptography]>=3.3.0 \
            python-multipart>=0.0.6 \
            aiosqlite>=0.19.0 \
            websockets>=12.0 \
            httpx>=0.25.0 \
            aiohttp>=3.9.0 \
            python-dotenv>=1.0.0 \
            pyyaml>=6.0 \
            loguru>=0.7.0 \
            bcrypt>=4.0.0 \
            -q

echo -e "   ${GREEN}✓${NC} 其他依赖已确认"

# 验证安装
echo ""
echo -e "${BLUE}[INFO]${NC} 验证安装..."

python3 << 'EOF'
import sys

packages_to_check = [
    ("email_validator", "email-validator"),
    ("pydantic", "pydantic"),
    ("fastapi", "fastapi"),
    ("uvicorn", "uvicorn"),
    ("sqlalchemy", "sqlalchemy"),
    ("passlib", "passlib"),
    ("bcrypt", "bcrypt"),
]

all_ok = True
for module_name, package_name in packages_to_check:
    try:
        __import__(module_name)
        print(f"✓ {package_name}")
    except ImportError:
        print(f"✗ {package_name} (缺失)")
        all_ok = False

if all_ok:
    print("\n✅ 所有依赖验证通过")
    sys.exit(0)
else:
    print("\n✗ 部分依赖缺失")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "===================================================="
    echo -e "${GREEN}✅ 依赖安装完成！${NC}"
    echo "===================================================="
    echo ""
    echo -e "${BLUE}下一步:${NC}"
    echo "  1. 退出虚拟环境: deactivate"
    echo "  2. 重启服务: ./start_all_services.sh"
    echo ""
else
    echo ""
    echo "===================================================="
    echo -e "${RED}✗ 依赖安装失败${NC}"
    echo "===================================================="
    echo ""
    echo "请尝试手动安装:"
    echo "  source venv/bin/activate"
    echo "  pip install -r web_backend/requirements.txt"
    echo "  deactivate"
    echo ""
    deactivate
    exit 1
fi

# 退出虚拟环境
deactivate

echo "虚拟环境已退出"

