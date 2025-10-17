#!/usr/bin/env python3
"""
测试 Lighter 交易所连接
验证 API 密钥和账户配置是否正确
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from quant_trading import Config
import lighter


async def test_connection():
    """测试 Lighter 连接"""
    print("=" * 60)
    print("  Lighter Connection Test")
    print("=" * 60)
    print()
    
    api_client = None
    signer_client = None
    
    try:
        # 加载配置
        print("Step 1: Loading configuration...")
        print("-" * 60)
        try:
            config = Config.from_file('config.yaml')
            print("[OK] Config loaded successfully")
            print(f"  Base URL: {config.lighter_config['base_url']}")
            print(f"  Account Index: {config.lighter_config['account_index']}")
            print(f"  API Key Index: {config.lighter_config['api_key_index']}")
            
            # 检查私钥格式
            private_key = config.lighter_config['api_key_private_key']
            if not private_key or private_key == "YOUR_PRIVATE_KEY_HERE" or private_key == "YOUR_MAINNET_PRIVATE_KEY_HERE":
                print("[FAIL] Private key not configured")
                print("  Please set api_key_private_key in config.yaml")
                return False
            
            if len(private_key) != 64:
                print(f"[WARN] Private key length is {len(private_key)}, expected 64")
            else:
                print(f"[OK] Private key format looks correct (64 chars)")
            
        except FileNotFoundError:
            print("[FAIL] config.yaml not found")
            return False
        except Exception as e:
            print(f"[FAIL] Config loading error: {e}")
            return False
        
        print()
        
        # 测试 API 客户端
        print("Step 2: Testing API Client...")
        print("-" * 60)
        try:
            api_client = lighter.ApiClient(
                configuration=lighter.Configuration(host=config.lighter_config["base_url"])
            )
            print("[OK] API Client created")
            
            # 测试获取市场列表
            from lighter.api.order_api import OrderApi
            order_api = OrderApi(api_client)
            
            markets = await order_api.order_books()
            
            if markets and hasattr(markets, 'order_books'):
                market_count = len(markets.order_books)
                print(f"[OK] Successfully fetched market data")
                print(f"  Found {market_count} markets")
                
                # 显示前3个市场
                if market_count > 0:
                    print("\n  Available markets:")
                    for i, market in enumerate(markets.order_books[:3]):
                        print(f"    Market {market.market_id}: {getattr(market, 'symbol', 'Unknown')}")
                    if market_count > 3:
                        print(f"    ... and {market_count - 3} more markets")
            else:
                print("[WARN] Market data format unexpected")
            
        except Exception as e:
            print(f"[FAIL] API Client test failed: {e}")
            print("  Possible reasons:")
            print("  - Network connection issue")
            print("  - Invalid base_url")
            print("  - Lighter service unavailable")
            return False
        
        print()
        
        # 测试 Signer 客户端
        print("Step 3: Testing Signer Client...")
        print("-" * 60)
        try:
            signer_client = lighter.SignerClient(
                url=config.lighter_config["base_url"],
                private_key=config.lighter_config["api_key_private_key"],
                account_index=config.lighter_config["account_index"],
                api_key_index=config.lighter_config["api_key_index"]
            )
            print("[OK] Signer Client created")
            
            # 检查客户端
            err = signer_client.check_client()
            if err is not None:
                print(f"[FAIL] Client check failed: {err}")
                print("  Possible reasons:")
                print("  - Invalid private key")
                print("  - Wrong account/API key index")
                return False
            else:
                print("[OK] Client check passed")
                print("  Authentication successful - can submit orders")
            
        except Exception as e:
            print(f"[FAIL] Signer Client test failed: {e}")
            print("  Possible reasons:")
            print("  - Invalid private key format")
            print("  - Wrong configuration")
            return False
        
        print()
        
        # 测试获取账户信息（可选，不影响主要功能）
        print("Step 4: Testing Account Access (Optional)...")
        print("-" * 60)
        try:
            from lighter.api.account_api import AccountApi
            account_api = AccountApi(api_client)
            
            # 使用配置的索引获取账户信息
            account_index = config.lighter_config["account_index"]
            
            try:
                account_info = await account_api.account(by="index", value=str(account_index))
                if account_info:
                    print(f"[OK] Account info fetched")
                    print(f"  Account Index: {account_index}")
                    
                    # 显示账户信息
                    if hasattr(account_info, 'l1_address'):
                        print(f"  Account Address (L1): {account_info.l1_address}")
                    
                else:
                    print("[INFO] Account info not available")
                    print("  This is normal, authentication already verified in Step 3")
                    
            except Exception as e:
                print(f"[INFO] Account details unavailable: {e}")
                print("  This is normal, not required for trading")
            
        except Exception as e:
            print(f"[INFO] Account access test skipped: {e}")
            print("  Not critical - authentication already verified")
        
        print()
        
        # 最终总结
        print("=" * 60)
        print("  Connection Test Summary")
        print("=" * 60)
        print()
        print("[OK] Configuration: Valid")
        print("[OK] API Client: Connected")
        print("[OK] Signer Client: Authenticated")
        print("[OK] Ready to Trade: YES")
        print()
        print("=" * 60)
        print("Result: ALL TESTS PASSED")
        print("=" * 60)
        print()
        print("Your trading account is successfully connected to Lighter!")
        print()
        print("Next steps:")
        print("  1. Run: python start_trading.py")
        print("  2. Monitor: python check_system_simple.py")
        print("  3. Check logs: tail -f logs/quant_trading.log")
        print()
        
        return True
        
    finally:
        # 清理资源 - 修复资源泄露问题
        print("Cleaning up resources...")
        try:
            if api_client is not None:
                await api_client.close()
                print("[OK] API Client closed")
        except Exception as e:
            pass
        
        try:
            if signer_client is not None:
                await signer_client.close()
                print("[OK] Signer Client closed")
        except Exception as e:
            pass
        
        # 等待所有异步任务完成
        await asyncio.sleep(0.1)


async def main():
    """主函数"""
    try:
        success = await test_connection()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\nTest cancelled")
        return 1
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
