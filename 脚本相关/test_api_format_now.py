#!/usr/bin/env python3
"""
测试 API 响应格式
"""

import requests
import json

print("=" * 60)
print("测试 API 响应格式")
print("=" * 60)
print()

# 步骤1: 登录
print("[步骤 1/3] 登录...")
try:
    login_response = requests.post(
        "http://localhost:8000/api/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        token = token_data.get('accessToken') or token_data.get('access_token')
        print(f"✓ 登录成功")
        print(f"  Token: {token[:20]}...")
    else:
        print(f"✗ 登录失败: {login_response.status_code}")
        print(f"  响应: {login_response.text}")
        exit(1)
        
except Exception as e:
    print(f"✗ 登录请求失败: {e}")
    exit(1)

print()

# 步骤2: 获取账户信息
print("[步骤 2/3] 获取账户信息...")
try:
    account_response = requests.get(
        "http://localhost:8000/api/trading/account",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if account_response.status_code == 200:
        account_data = account_response.json()
        print("✓ 获取账户信息成功")
        print()
        print("完整响应:")
        print(json.dumps(account_data, indent=2, ensure_ascii=False))
    else:
        print(f"✗ 获取失败: {account_response.status_code}")
        print(f"  响应: {account_response.text}")
        exit(1)
        
except Exception as e:
    print(f"✗ 请求失败: {e}")
    exit(1)

print()

# 步骤3: 分析字段格式
print("[步骤 3/3] 分析字段格式...")
print()

# 检查 camelCase
has_camel_available = 'availableBalance' in account_data
has_camel_margin = 'marginBalance' in account_data
has_camel_pnl = 'unrealizedPnl' in account_data

# 检查 snake_case
has_snake_available = 'available_balance' in account_data
has_snake_margin = 'margin_balance' in account_data
has_snake_pnl = 'unrealized_pnl' in account_data

print("字段名检查:")
print(f"  camelCase (availableBalance): {'✓ 存在' if has_camel_available else '✗ 不存在'}")
print(f"  snake_case (available_balance): {'✓ 存在' if has_snake_available else '✗ 不存在'}")
print()

if has_camel_available:
    print("✓ API 响应使用 camelCase（前端兼容）")
    print()
    print("关键字段:")
    print(f"  availableBalance: {account_data.get('availableBalance', 'N/A')}")
    print(f"  marginBalance: {account_data.get('marginBalance', 'N/A')}")
    print(f"  unrealizedPnl: {account_data.get('unrealizedPnl', 'N/A')}")
    print(f"  totalPnl: {account_data.get('totalPnl', 'N/A')}")
    print()
    print("✅ 后端配置正确！")
    print()
    print("如果前端仍显示 0，请:")
    print("  1. 清除浏览器缓存: F12 → Application → Clear site data")
    print("  2. 强制刷新: Ctrl+Shift+R")
    print("  3. 重新登录")
    
elif has_snake_available:
    print("⚠️  API 响应使用 snake_case（前端不兼容）")
    print()
    print("当前字段:")
    print(f"  available_balance: {account_data.get('available_balance', 'N/A')}")
    print(f"  margin_balance: {account_data.get('margin_balance', 'N/A')}")
    print(f"  unrealized_pnl: {account_data.get('unrealized_pnl', 'N/A')}")
    print()
    print("❌ 后端配置未生效！")
    print()
    print("修复步骤:")
    print("  1. 检查 web_backend/schemas/trading.py 是否已更新")
    print("  2. 检查 web_backend/api/routes/trading.py 是否添加了 response_model_by_alias=True")
    print("  3. 重启后端: pkill -f uvicorn && cd web_backend && python3 -m uvicorn main:app --host 0.0.0.0 --port 8000")
    print("  4. 清理 Python 缓存: rm -rf web_backend/__pycache__ web_backend/**/__pycache__")
    exit(1)
    
else:
    print("✗ 无法识别字段格式")
    print()
    print("可用字段:")
    for key in account_data.keys():
        print(f"  {key}: {account_data[key]}")

print()
print("=" * 60)

