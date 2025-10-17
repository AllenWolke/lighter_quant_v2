@echo off
chcp 65001 >nul
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║     Lighter 配置修复工具 - Windows 版本                    ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到 Python
    echo 请先安装 Python 3.9+
    pause
    exit /b 1
)

echo ✓ Python 已安装
echo.

REM 检查配置文件
if not exist "config.yaml" (
    echo ❌ 错误: 未找到配置文件 config.yaml
    pause
    exit /b 1
)

echo ✓ 配置文件存在
echo.

REM 验证配置
echo [验证配置中...]
python -c "import yaml; config = yaml.safe_load(open('config.yaml', encoding='utf-8')); print('网络:', config['lighter']['base_url']); print('私钥前缀:', config['lighter']['api_key_private_key'][:10]); print('私钥长度:', len(config['lighter']['api_key_private_key']))"

if %errorlevel% neq 0 (
    echo.
    echo ❌ 配置验证失败
    echo.
    goto :manual_config
)

REM 检查私钥
python -c "import yaml; import sys; config = yaml.safe_load(open('config.yaml', encoding='utf-8')); pk = config['lighter']['api_key_private_key']; sys.exit(0 if pk not in ['YOUR_MAINNET_PRIVATE_KEY_HERE', 'YOUR_TESTNET_PRIVATE_KEY_HERE'] and pk.startswith('0x') and len(pk) == 66 else 1)"

if %errorlevel% neq 0 (
    echo.
    echo ⚠️ 私钥未正确配置
    echo.
    goto :manual_config
)

echo.
echo ✅ 配置验证通过！
echo.
echo 下一步操作:
echo   1. 测试网络连接:
echo      curl -I https://mainnet.zklighter.elliot.ai
echo.
echo   2. 启动量化交易程序:
echo      python main.py --config config.yaml
echo.
pause
exit /b 0

:manual_config
echo ════════════════════════════════════════════════════════════
echo   需要手动配置私钥
echo ════════════════════════════════════════════════════════════
echo.
echo 请按以下步骤操作:
echo.
echo 1. 使用文本编辑器打开 config.yaml
echo    notepad config.yaml
echo.
echo 2. 找到这一行:
echo    api_key_private_key: "YOUR_MAINNET_PRIVATE_KEY_HERE"
echo.
echo 3. 替换为您的私钥:
echo    api_key_private_key: "0x您的64位私钥"
echo.
echo 4. 保存文件并重新运行此脚本
echo.
echo ════════════════════════════════════════════════════════════
echo.
set /p open_editor="是否现在打开配置文件编辑？(Y/N): "
if /i "%open_editor%"=="Y" (
    notepad config.yaml
)
echo.
pause
exit /b 1

