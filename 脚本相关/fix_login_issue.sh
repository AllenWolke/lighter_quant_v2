#!/bin/bash

###############################################################################
# 修复登录问题
# 确保用户创建成功并可以登录
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
echo -e "${CYAN}  修复登录问题${NC}"
echo "=========================================================="
echo ""

# 步骤1: 停止服务
echo -e "${BLUE}▶ 步骤1: 停止所有服务${NC}"
if [ -f "stop_all_services.sh" ]; then
    ./stop_all_services.sh 2>/dev/null || true
fi
pkill -9 -f "python.*main.py" 2>/dev/null || true
pkill -9 -f "npm start" 2>/dev/null || true
echo -e "${GREEN}✓ 服务已停止${NC}"
echo ""

# 步骤2: 清理数据库
echo -e "${BLUE}▶ 步骤2: 清理旧数据库${NC}"
rm -f data/*.db 2>/dev/null || true
rm -f web_backend/*.db 2>/dev/null || true
echo -e "${GREEN}✓ 数据库已清理${NC}"
echo ""

# 步骤3: 创建用户
echo -e "${BLUE}▶ 步骤3: 创建默认管理员用户${NC}"
chmod +x verify_user.sh 2>/dev/null || true
if [ -f "verify_user.sh" ]; then
    ./verify_user.sh
else
    echo -e "${YELLOW}⚠ verify_user.sh 不存在，直接创建用户${NC}"
    
    cd web_backend
    export AUTO_SKIP_PROMPT=1
    
    if [ -f "../venv/bin/python" ]; then
        ../venv/bin/python init_default_user.py
    else
        python3 init_default_user.py
    fi
    
    unset AUTO_SKIP_PROMPT
    cd ..
fi
echo ""

# 步骤4: 验证用户
echo -e "${BLUE}▶ 步骤4: 验证用户和密码${NC}"

if [ -f "venv/bin/python" ]; then
    PYTHON_CMD="venv/bin/python"
else
    PYTHON_CMD="python3"
fi

$PYTHON_CMD << 'EOF'
import sys
sys.path.insert(0, 'web_backend')

try:
    from core.database import SessionLocal
    from core.security import verify_password
    from models.user import User
    
    db = SessionLocal()
    user = db.query(User).filter(User.username == "admin").first()
    
    if user:
        print(f"✓ 用户存在: {user.username}")
        
        # 验证密码
        if verify_password("admin123", user.hashed_password):
            print("✓ 密码验证通过")
            print("\n" + "="*50)
            print("✅ 登录凭据验证成功")
            print("="*50)
            print("用户名: admin")
            print("密码:   admin123")
            print("="*50)
        else:
            print("✗ 密码验证失败")
            print("正在重置密码...")
            from core.security import get_password_hash
            user.hashed_password = get_password_hash("admin123")
            db.commit()
            print("✓ 密码已重置为: admin123")
    else:
        print("✗ 用户不存在")
        sys.exit(1)
    
    db.close()
    
except Exception as e:
    print(f"✗ 验证失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ 用户验证失败${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 用户验证通过${NC}"
echo ""

# 步骤5: 启动服务
echo -e "${BLUE}▶ 步骤5: 启动服务${NC}"
if [ -f "start_all_services.sh" ]; then
    chmod +x start_all_services.sh
    ./start_all_services.sh
else
    echo -e "${RED}✗ 未找到启动脚本${NC}"
    exit 1
fi

# 最终提示
echo ""
echo "=========================================================="
echo -e "${GREEN}🎉 登录问题已修复！${NC}"
echo "=========================================================="
echo ""
echo -e "${CYAN}访问信息:${NC}"
echo "  🌐 Web前端: http://localhost:3000"
echo "  🔌 Web后端: http://localhost:8000"
echo ""
echo -e "${CYAN}登录凭据:${NC}"
echo "  👤 用户名: admin"
echo "  🔑 密码:   admin123"
echo ""
echo -e "${YELLOW}⚠️  请立即登录并修改密码！${NC}"
echo ""
echo "=========================================================="

