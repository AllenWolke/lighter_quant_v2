#!/usr/bin/env python3
"""
测试账户余额 API 脚本
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_account_balance():
    """测试账户余额获取"""
    print("=" * 60)
    print("测试账户余额 API")
    print("=" * 60)
    print()
    
    # 测试 1: 直接测试 TradingService
    print("[测试 1/3] 测试 TradingService.get_account_info()")
    print("-" * 60)
    
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
        
        # 检查数据来源
        if account_info.get('available_balance') == 9500.0:
            print("⚠️  当前使用模拟数据")
            print("   原因可能是:")
            print("   1. config.yaml 未正确配置")
            print("   2. Lighter API 调用失败")
            print("   3. 私钥未配置或不正确")
        else:
            print("✓ 使用真实数据")
        
    except Exception as e:
        print(f"✗ TradingService 调用失败: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 60)
    
    # 测试 2: 检查配置文件
    print("[测试 2/3] 检查配置文件")
    print("-" * 60)
    
    try:
        from quant_trading.utils.config import Config
        
        config_file = "config.yaml"
        if os.path.exists(config_file):
            config = Config.from_file(config_file)
            
            print(f"✓ 配置文件存在: {config_file}")
            print()
            print("Lighter 配置:")
            print(f"  base_url: {config.lighter_config.get('base_url')}")
            print(f"  account_index: {config.lighter_config.get('account_index')}")
            print(f"  chain_id: {config.lighter_config.get('chain_id')}")
            
            # 检查私钥
            api_key = config.lighter_config.get('api_key_private_key', '')
            if api_key in ['YOUR_MAINNET_PRIVATE_KEY_HERE', 'YOUR_TESTNET_PRIVATE_KEY_HERE', '']:
                print(f"  api_key_private_key: ⚠️  未配置")
                print()
                print("⚠️  私钥未配置！")
                print("   请编辑 config.yaml 并设置:")
                print("   lighter:")
                print("     api_key_private_key: \"0x您的私钥\"")
            else:
                print(f"  api_key_private_key: ✓ 已配置 ({api_key[:10]}...)")
        else:
            print(f"✗ 配置文件不存在: {config_file}")
            
    except Exception as e:
        print(f"✗ 读取配置失败: {e}")
    
    print()
    print("=" * 60)
    
    # 测试 3: 测试 Lighter API 连接
    print("[测试 3/3] 测试 Lighter API 连接")
    print("-" * 60)
    
    try:
        from lighter import ApiClient, Configuration
        from lighter.api import AccountApi
        from quant_trading.utils.config import Config
        
        config_file = "config.yaml"
        if os.path.exists(config_file):
            config = Config.from_file(config_file)
            
            # 创建 API 客户端
            configuration = Configuration(
                host=config.lighter_config.get("base_url", "https://mainnet.zklighter.elliot.ai")
            )
            api_client = ApiClient(configuration)
            account_api = AccountApi(api_client)
            
            print(f"✓ Lighter API 客户端创建成功")
            print(f"  URL: {configuration.host}")
            print()
            
            # 尝试获取账户信息
            account_index = config.lighter_config.get("account_index", 0)
            print(f"尝试获取账户信息 (索引: {account_index})...")
            
            try:
                account_response = await account_api.account(
                    by="index",
                    value=str(account_index)
                )
                
                if account_response and account_response.code == 200:
                    print("✓ Lighter API 调用成功")
                    print()
                    print("账户数据:")
                    print(f"  collateral: {account_response.collateral}")
                    print(f"  available_balance: {account_response.available_balance}")
                    print(f"  status: {account_response.status}")
                    
                    if hasattr(account_response, 'total_asset_value'):
                        print(f"  total_asset_value: {account_response.total_asset_value}")
                    
                    if hasattr(account_response, 'positions') and account_response.positions:
                        print(f"  positions: {len(account_response.positions)} 个持仓")
                else:
                    print(f"⚠️  API 返回非 200 状态码: {account_response.code if account_response else 'None'}")
                    
            except Exception as api_error:
                print(f"✗ Lighter API 调用失败: {api_error}")
                print()
                print("可能的原因:")
                print("  1. 私钥未配置或不正确")
                print("  2. 账户索引不正确")
                print("  3. 网络连接问题")
                print("  4. API 服务不可用")
        else:
            print(f"✗ 配置文件不存在，无法测试 API")
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 60)
    print()
    
    # 总结和建议
    print("总结:")
    print()
    print("如果看到 '⚠️ 当前使用模拟数据'，请:")
    print("1. 确保 config.yaml 中配置了正确的私钥")
    print("2. 确保私钥格式为: 0x + 64位十六进制 (总共66位)")
    print("3. 确保账户索引正确")
    print("4. 重启后端服务: cd web_backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000")
    print()
    print("如果配置正确但仍使用模拟数据，查看后端日志:")
    print("  tail -f logs/web_backend.log | grep -i account")
    print()

if __name__ == "__main__":
    asyncio.run(test_account_balance())

