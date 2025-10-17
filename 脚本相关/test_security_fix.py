#!/usr/bin/env python3
"""测试 security.py 修复"""

import sys
import os

sys.path.insert(0, 'web_backend')

print("="*60)
print("测试密码哈希和验证功能")
print("="*60)

try:
    from core.security import get_password_hash, verify_password
    
    # 测试1: 生成哈希
    print("\n【测试1】生成密码哈希")
    password = "admin123"
    print(f"密码: {password}")
    
    hashed = get_password_hash(password)
    print(f"✓ 哈希生成成功")
    print(f"  哈希长度: {len(hashed)} 字符")
    print(f"  哈希前缀: {hashed[:10]}...")
    
    # 测试2: 验证密码
    print("\n【测试2】验证密码")
    if verify_password(password, hashed):
        print(f"✓ 密码验证成功")
    else:
        print(f"✗ 密码验证失败")
        sys.exit(1)
    
    # 测试3: 错误密码
    print("\n【测试3】测试错误密码")
    if verify_password("wrong_password", hashed):
        print(f"✗ 错误：错误密码通过了验证")
        sys.exit(1)
    else:
        print(f"✓ 正确拒绝了错误密码")
    
    # 测试4: 长密码
    print("\n【测试4】测试长密码")
    long_password = "A" * 100
    long_hash = get_password_hash(long_password)
    print(f"✓ 长密码哈希成功（自动截断）")
    
    # 验证截断后的密码
    if verify_password(long_password, long_hash):
        print(f"✓ 长密码验证成功")
    else:
        print(f"✗ 长密码验证失败")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✅ 所有测试通过！密码功能正常")
    print("="*60)
    
except Exception as e:
    print(f"\n✗ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

