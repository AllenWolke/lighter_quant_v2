#!/bin/bash

###############################################################################
# 验证并创建默认用户
###############################################################################

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "=========================================="
echo "  验证默认用户"
echo "=========================================="
echo ""

cd web_backend 2>/dev/null || cd ~/lighter_quantification_v2/web_backend

# 设置 Python 命令
if [ -f "../venv/bin/python" ]; then
    PYTHON_CMD="../venv/bin/python"
elif [ -f "venv/bin/python" ]; then
    PYTHON_CMD="venv/bin/python"
else
    PYTHON_CMD="python3"
fi

echo -e "${BLUE}[INFO]${NC} 使用 Python: $PYTHON_CMD"
echo ""

# 检查用户是否存在
echo -e "${BLUE}[INFO]${NC} 检查用户..."

$PYTHON_CMD << 'EOF'
import sys
import os
sys.path.insert(0, '.')
sys.path.insert(0, '..')

try:
    from core.database import SessionLocal, Base, engine
    from core.security import get_password_hash
    from models.user import User
    
    # 创建表
    Base.metadata.create_all(bind=engine)
    
    # 创建会话
    db = SessionLocal()
    
    try:
        # 检查用户
        user = db.query(User).filter(User.username == "admin").first()
        
        if user:
            print("✓ admin用户已存在")
            print(f"  ID: {user.id}")
            print(f"  用户名: {user.username}")
            print(f"  邮箱: {user.email}")
            print(f"  激活: {user.is_active}")
            
            # 测试密码验证
            from core.security import verify_password
            if verify_password("admin123", user.hashed_password):
                print("  密码: ✓ 正确")
            else:
                print("  密码: ✗ 错误，正在重置...")
                user.hashed_password = get_password_hash("admin123")
                db.commit()
                print("  密码: ✓ 已重置为 admin123")
        else:
            print("⚠ admin用户不存在，正在创建...")
            
            # 创建用户
            admin_user = User(
                username="admin",
                email="admin@lighter-quant.local",
                full_name="系统管理员",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                is_superuser=True
            )
            
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
            print("✓ admin用户创建成功")
            print(f"  ID: {admin_user.id}")
            print(f"  用户名: {admin_user.username}")
            print(f"  密码: admin123")
        
        print("\n" + "="*50)
        print("✅ 用户验证完成")
        print("="*50)
        print("登录信息:")
        print("  用户名: admin")
        print("  密码:   admin123")
        print("="*50)
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        sys.exit(1)
    finally:
        db.close()
        
except Exception as e:
    print(f"✗ 导入错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}✅ 验证成功${NC}"
else
    echo -e "${RED}✗ 验证失败${NC}"
fi

echo ""
echo "现在可以使用以下凭据登录:"
echo "  用户名: admin"
echo "  密码:   admin123"
echo ""

