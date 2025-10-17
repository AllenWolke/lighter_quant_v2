#!/usr/bin/env python3
"""
配置文件检查工具
检查配置文件是否正确，特别是无域名配置的安全设置
"""

import sys
import yaml
from pathlib import Path

def print_info(msg):
    print(f"[INFO] {msg}")

def print_success(msg):
    print(f"[OK] {msg}")

def print_warning(msg):
    print(f"[WARNING] {msg}")

def print_error(msg):
    print(f"[ERROR] {msg}")

def check_config_file(config_path):
    """检查配置文件"""
    print("=" * 70)
    print("配置文件检查工具")
    print("=" * 70)
    print()
    
    # 检查文件是否存在
    if not Path(config_path).exists():
        print_error(f"配置文件不存在: {config_path}")
        return False
    
    print_success(f"配置文件存在: {config_path}")
    
    # 读取配置文件
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        print_success("配置文件格式正确")
    except Exception as e:
        print_error(f"配置文件格式错误: {e}")
        return False
    
    # 检查必要配置项
    print()
    print_info("检查必要配置项...")
    
    all_ok = True
    
    # 检查 lighter 配置
    if 'lighter' in config:
        lighter_config = config['lighter']
        
        # 检查私钥
        if 'api_key_private_key' in lighter_config:
            private_key = lighter_config['api_key_private_key']
            if 'YOUR_' in private_key or 'REPLACE' in private_key or len(private_key) < 32:
                print_error("Lighter私钥未配置或使用了占位符")
                print_info("  请设置实际的主网私钥")
                all_ok = False
            else:
                print_success("Lighter私钥已配置")
        else:
            print_error("缺少 lighter.api_key_private_key 配置")
            all_ok = False
        
        # 检查base_url
        if 'base_url' in lighter_config:
            base_url = lighter_config['base_url']
            if 'mainnet' in base_url:
                print_success(f"Lighter地址: {base_url} (主网)")
            elif 'testnet' in base_url:
                print_warning(f"Lighter地址: {base_url} (测试网)")
            else:
                print_warning(f"Lighter地址: {base_url}")
        else:
            print_error("缺少 lighter.base_url 配置")
            all_ok = False
    else:
        print_error("缺少 lighter 配置")
        all_ok = False
    
    # 检查 web 配置
    print()
    print_info("检查Web配置...")
    
    if 'web' in config:
        web_config = config['web']
        
        # 检查SSL配置
        if 'backend' in web_config:
            backend = web_config['backend']
            ssl_enabled = backend.get('ssl_enabled', False)
            
            if ssl_enabled:
                print_success("SSL已启用（需要域名和证书）")
                # 检查证书路径
                if 'ssl_cert' in backend and 'ssl_key' in backend:
                    print_success(f"  证书: {backend['ssl_cert']}")
                    print_success(f"  密钥: {backend['ssl_key']}")
                else:
                    print_error("  SSL已启用但缺少证书/密钥配置")
                    all_ok = False
            else:
                print_warning("SSL未启用（使用HTTP，无需域名）")
                print_info("  访问地址将使用 http:// 而不是 https://")
        
        # 检查API URL
        if 'frontend' in web_config:
            frontend = web_config['frontend']
            if 'api_url' in frontend:
                api_url = frontend['api_url']
                if 'YOUR_' in api_url or 'localhost' in api_url:
                    print_warning(f"API URL可能需要更新: {api_url}")
                    print_info("  请将 YOUR_SERVER_IP 替换为实际IP")
                else:
                    print_success(f"API URL: {api_url}")
    else:
        print_warning("缺少 web 配置（仅命令行模式不需要）")
    
    # 检查安全配置
    print()
    print_info("检查安全配置...")
    
    if 'security' in config:
        security = config['security']
        
        # 检查访问控制
        if security.get('access_control', False):
            print_success("访问控制已启用")
            
            if 'allowed_ips' in security:
                allowed_ips = security['allowed_ips']
                print_success(f"  允许的IP: {len(allowed_ips)} 个")
                
                for ip in allowed_ips:
                    if 'YOUR_' in ip or 'REPLACE' in ip:
                        print_warning(f"  - {ip} (需要替换为实际IP)")
                    else:
                        print_success(f"  - {ip}")
            else:
                print_warning("  访问控制已启用但未配置allowed_ips")
        else:
            print_warning("访问控制未启用（不推荐）")
            print_info("  建议启用 security.access_control 并配置 allowed_ips")
        
        # 检查认证
        if security.get('require_authentication', False):
            print_success("强制认证已启用")
        else:
            print_warning("强制认证未启用（不推荐）")
        
        # 检查双因素认证
        if security.get('two_factor_auth', False):
            print_success("双因素认证已启用")
        else:
            print_warning("双因素认证未启用（建议启用）")
    else:
        print_error("缺少 security 配置（强烈建议配置）")
        all_ok = False
    
    # 检查通知配置
    print()
    print_info("检查通知配置...")
    
    if 'notifications' in config:
        if 'email' in config['notifications']:
            email = config['notifications']['email']
            if email.get('enabled', False):
                if 'your_email' in email.get('username', ''):
                    print_warning("邮件通知已启用但使用了占位符")
                    print_info("  请配置实际的邮箱地址")
                else:
                    print_success("邮件通知已正确配置")
            else:
                print_warning("邮件通知未启用")
    else:
        print_warning("缺少 notifications 配置")
    
    # 总结
    print()
    print("=" * 70)
    print("检查总结")
    print("=" * 70)
    
    if all_ok:
        print_success("所有必需配置项检查通过")
    else:
        print_error("部分必需配置项检查失败，请修复")
    
    # 无域名配置建议
    print()
    print_info("无域名部署建议:")
    print("1. 确保 ssl_enabled 设置为 false")
    print("2. 在 api_url 中使用服务器IP地址")
    print("3. 配置防火墙和IP白名单")
    print("4. 启用强认证和双因素认证")
    print("5. 使用VPN或SSH隧道访问（最安全）")
    
    print()
    print_info("获取服务器公网IP:")
    print("  curl ifconfig.me")
    print("  curl ipinfo.io/ip")
    
    return all_ok

def show_example_config():
    """显示无域名配置示例"""
    print()
    print("=" * 70)
    print("无域名配置示例")
    print("=" * 70)
    print()
    print("""web:
  backend:
    host: "0.0.0.0"
    port: 8000
    ssl_enabled: false  # 无域名时设为false
  
  frontend:
    host: "0.0.0.0"
    port: 3000
    api_url: "http://123.45.67.89:8000"  # 替换为您的服务器IP

security:
  access_control: true
  allowed_ips:
    - "192.168.1.0/24"   # 内网
    - "98.76.54.32"      # 您的办公室IP
  require_authentication: true
  two_factor_auth: true""")
    print()

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python check_config.py <配置文件路径>")
        print()
        print("示例:")
        print("  python check_config.py config.yaml")
        print("  python check_config.py config_linux_mainnet.yaml")
        print("  python check_config.py config_no_domain_example.yaml")
        print()
        print("或使用 --example 查看无域名配置示例:")
        print("  python check_config.py --example")
        sys.exit(1)
    
    if sys.argv[1] == "--example":
        show_example_config()
        sys.exit(0)
    
    config_path = sys.argv[1]
    
    try:
        success = check_config_file(config_path)
        sys.exit(0 if success else 1)
    except Exception as e:
        print_error(f"检查过程出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
