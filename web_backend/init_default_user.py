#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建默认管理员用户
用户名: admin
密码: admin123 (6位以上)

使用方法:
  python3 init_default_user.py
  或
  source ../venv/bin/activate && python init_default_user.py
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database import SessionLocal, Base, engine
from core.security import get_password_hash
from models.user import User


def create_default_admin():
    """创建默认管理员用户"""
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("✓ 数据库表已创建")
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 检查admin用户是否已存在
        existing_user = db.query(User).filter(User.username == "admin").first()
        
        if existing_user:
            print("⚠️  admin用户已存在")
            print(f"   用户名: {existing_user.username}")
            print(f"   邮箱: {existing_user.email}")
            print(f"   创建时间: {existing_user.created_at}")
            
            # 检查环境变量，如果设置了 AUTO_SKIP 则自动跳过
            import sys
            import os
            
            # 优先检查环境变量
            auto_skip = os.environ.get('AUTO_SKIP_PROMPT', '').lower() in ('1', 'true', 'yes')
            
            # 如果没有设置环境变量，检查是否在非交互式环境
            if not auto_skip:
                try:
                    is_interactive = sys.stdin.isatty()
                except:
                    # 如果检测失败，默认为非交互式
                    is_interactive = False
            else:
                is_interactive = False
            
            if is_interactive and not auto_skip:
                # 交互式环境：询问是否重置密码（带超时）
                print("\n是否重置admin密码为 'admin123'? (y/N): ", end='', flush=True)
                
                # 使用 select 实现超时（仅限 Unix）
                try:
                    import select
                    # 等待输入，5秒超时
                    if select.select([sys.stdin], [], [], 5.0)[0]:
                        response = sys.stdin.readline().strip()
                        if response.lower() == 'y':
                            existing_user.hashed_password = get_password_hash("admin123")
                            db.commit()
                            print("✓ admin密码已重置为: admin123")
                        else:
                            print("未修改密码")
                    else:
                        print("\n⏱️ 输入超时，跳过密码重置")
                except (ImportError, AttributeError):
                    # Windows 或不支持 select，直接跳过
                    print("\n✓ 自动跳过密码重置（非交互式环境）")
            else:
                # 非交互式环境：自动跳过
                print("✓ 自动跳过密码重置（非交互式环境）")
                print("💡 如需重置密码，请手动运行: python3 init_default_user.py")
            
            return
        
        # 创建默认管理员用户
        try:
            # 生成密码哈希
            password = "admin123"
            print(f"生成密码哈希，密码长度: {len(password)} 字符, {len(password.encode('utf-8'))} 字节")
            hashed_password = get_password_hash(password)
            print(f"哈希密码长度: {len(hashed_password)} 字符")
            
            admin_user = User(
                username="admin",
                email="admin@lighter-quant.local",
                full_name="系统管理员",
                hashed_password=hashed_password,
                is_active=True,
                is_superuser=True
            )
            
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
        except Exception as hash_error:
            print(f"✗ 创建用户失败: {hash_error}")
            db.rollback()
            raise
        
        print("\n" + "="*50)
        print("✓ 默认管理员用户创建成功")
        print("="*50)
        print(f"用户名: admin")
        print(f"密码: admin123")
        print(f"邮箱: {admin_user.email}")
        print(f"用户ID: {admin_user.id}")
        print("="*50)
        print("\n⚠️  请登录后立即修改默认密码！")
        print()
        
    except Exception as e:
        print(f"✗ 创建用户失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("="*50)
    print("  创建默认管理员用户")
    print("="*50)
    print()
    
    create_default_admin()
    
    print("\n可以使用以下凭据登录:")
    print("  http://localhost:3000")
    print("  用户名: admin")
    print("  密码: admin123")
    print()

