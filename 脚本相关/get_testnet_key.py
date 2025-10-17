#!/usr/bin/env python3
"""
获取Lighter测试网私钥的简化脚本
用于快速获取测试网配置参数
"""

import asyncio
import sys

def print_info(message):
    """打印信息"""
    print(f"[INFO] {message}")

def print_success(message):
    """打印成功信息"""
    print(f"[SUCCESS] {message}")

def print_error(message):
    """打印错误信息"""
    print(f"[ERROR] {message}")

async def get_testnet_credentials():
    """获取测试网凭证"""
    print("=" * 70)
    print("Lighter测试网配置获取工具")
    print("=" * 70)
    print()
    
    try:
        # 导入必要的模块
        print_info("导入lighter模块...")
        from lighter import ApiClient, Configuration
        from lighter.api.account_api import AccountApi
        from lighter.signer_client import SignerClient, create_api_key
        try:
            from lighter.exceptions import ApiException
        except ImportError:
            from lighter.errors import ApiException
        
        import eth_account
        
        print_success("模块导入成功")
        
        # 测试网配置
        BASE_URL = "https://testnet.zklighter.elliot.ai"
        # 这是一个示例私钥，已在测试网注册
        ETH_PRIVATE_KEY = "1234567812345678123456781234567812345678123456781234567812345678"
        API_KEY_INDEX = 3
        
        print()
        print_info(f"连接测试网: {BASE_URL}")
        
        # 创建API客户端
        api_client = ApiClient(configuration=Configuration(host=BASE_URL))
        
        # 从以太坊私钥获取地址
        print_info("验证以太坊账户...")
        eth_acc = eth_account.Account.from_key(ETH_PRIVATE_KEY)
        eth_address = eth_acc.address
        print_success(f"以太坊地址: {eth_address}")
        
        # 查询账户
        print_info("查询Lighter账户...")
        try:
            response = await AccountApi(api_client).accounts_by_l1_address(
                l1_address=eth_address
            )
        except ApiException as e:
            if hasattr(e, 'data') and hasattr(e.data, 'message'):
                if e.data.message == "account not found":
                    print_error(f"账户未找到: {eth_address}")
                    print()
                    print("注意事项:")
                    print("1. 这个示例私钥可能未在测试网注册")
                    print("2. 您可以使用自己的测试网私钥")
                    print("3. 或者访问Lighter测试网水龙头获取测试账户")
                    await api_client.close()
                    return False
            raise e
        
        # 获取账户索引
        if len(response.sub_accounts) > 1:
            print_success(f"找到 {len(response.sub_accounts)} 个子账户")
            for sub_account in response.sub_accounts:
                print(f"  - 账户索引: {sub_account.index}")
            account_index = response.sub_accounts[0].index
            print_info(f"使用第一个账户，索引: {account_index}")
        else:
            account_index = response.sub_accounts[0].index
            print_success(f"账户索引: {account_index}")
        
        # 生成API密钥对
        print()
        print_info("生成API密钥对...")
        private_key, public_key, err = create_api_key()
        if err is not None:
            print_error(f"生成密钥失败: {err}")
            await api_client.close()
            return False
        
        print_success("API密钥对生成成功")
        
        # 创建签名客户端
        print_info("创建签名客户端...")
        tx_client = SignerClient(
            url=BASE_URL,
            private_key=private_key,
            account_index=account_index,
            api_key_index=API_KEY_INDEX,
        )
        
        # 更改API密钥
        print_info("更新API密钥（这可能需要一些时间）...")
        response, err = await tx_client.change_api_key(
            eth_private_key=ETH_PRIVATE_KEY,
            new_pubkey=public_key,
        )
        if err is not None:
            print_error(f"更新密钥失败: {err}")
            await tx_client.close()
            await api_client.close()
            return False
        
        print_success("API密钥更新成功")
        
        # 等待密钥更新完成
        print_info("等待密钥同步...")
        import time
        time.sleep(10)
        
        # 验证密钥
        print_info("验证新密钥...")
        err = tx_client.check_client()
        if err is not None:
            print_error(f"密钥验证失败: {err}")
        else:
            print_success("密钥验证成功")
        
        # 输出配置信息
        print()
        print("=" * 70)
        print("测试网配置信息")
        print("=" * 70)
        print()
        print("请将以下配置复制到 config_linux_testnet.yaml 文件中:")
        print()
        print(f"""lighter:
  base_url: "{BASE_URL}"
  api_key_private_key: "{private_key}"
  api_key_index: {API_KEY_INDEX}
  account_index: {account_index}
  chain_id: 300
""")
        print("=" * 70)
        
        # 关闭客户端
        await tx_client.close()
        await api_client.close()
        
        print()
        print_success("配置获取完成！")
        print()
        print("下一步:")
        print("1. 将上述配置复制到 config_linux_testnet.yaml")
        print("2. 运行 python quick_start.py 启动系统")
        
        return True
        
    except ImportError as e:
        print_error(f"模块导入失败: {e}")
        print()
        print("请确保已安装所有依赖:")
        print("  pip install -r requirements-minimal.txt")
        return False
        
    except Exception as e:
        print_error(f"发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

async def simple_test():
    """简单测试lighter模块导入"""
    print("=" * 70)
    print("Lighter模块导入测试")
    print("=" * 70)
    print()
    
    try:
        print_info("测试导入lighter模块...")
        import lighter
        print_success(f"lighter模块导入成功")
        print(f"  版本: {getattr(lighter, '__version__', '未知')}")
        
        print()
        print_info("测试导入ApiClient...")
        from lighter import ApiClient, Configuration
        print_success("ApiClient导入成功")
        
        print()
        print_info("测试导入AccountApi...")
        from lighter.api.account_api import AccountApi
        print_success("AccountApi导入成功")
        
        print()
        print_info("测试导入SignerClient...")
        from lighter.signer_client import SignerClient, create_api_key
        print_success("SignerClient导入成功")
        
        print()
        print_success("所有核心模块导入成功！")
        print()
        print("您可以继续运行完整的配置获取流程:")
        print("  python get_testnet_key.py --full")
        
        return True
        
    except ImportError as e:
        print_error(f"模块导入失败: {e}")
        print()
        print("请检查:")
        print("1. 是否已安装lighter: pip install lighter>=0.0.4")
        print("2. 是否在虚拟环境中: source venv/bin/activate")
        print("3. 是否安装了所有依赖: pip install -r requirements-minimal.txt")
        return False
    except Exception as e:
        print_error(f"测试失败: {e}")
        return False

def main():
    """主函数"""
    import sys
    
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == "--full":
        # 运行完整流程
        success = asyncio.run(get_testnet_credentials())
    else:
        # 只运行简单测试
        print("运行简单导入测试（使用 --full 参数运行完整配置获取流程）")
        print()
        success = asyncio.run(simple_test())
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n程序异常: {e}")
        sys.exit(1)
