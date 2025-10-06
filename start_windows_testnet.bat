@echo off
REM Windows测试环境启动脚本
REM 用于启动Lighter量化交易系统的Windows测试环境

echo ========================================
echo   Lighter量化交易系统 - Windows测试环境
echo ========================================
echo.

REM 设置编码为UTF-8
chcp 65001 > nul

REM 检查Python环境
echo [1/6] 检查Python环境...
python --version > nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.9+
    pause
    exit /b 1
)
echo 成功: Python环境检查通过

REM 检查虚拟环境
echo.
echo [2/6] 检查虚拟环境...
if not exist "venv\Scripts\activate.bat" (
    echo 错误: 未找到虚拟环境，请先创建虚拟环境
    echo 运行命令: python -m venv venv
    pause
    exit /b 1
)

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo 错误: 虚拟环境激活失败
    pause
    exit /b 1
)
echo 成功: 虚拟环境激活成功

REM 检查配置文件
echo.
echo [3/6] 检查配置文件...
if not exist "config_windows_testnet.yaml" (
    echo 错误: 未找到配置文件 config_windows_testnet.yaml
    echo 请先复制并配置配置文件
    pause
    exit /b 1
)
echo 成功: 配置文件检查通过

REM 检查依赖
echo.
echo [4/6] 检查依赖包...
python -c "import lighter, eth_account, pydantic" > nul 2>&1
if errorlevel 1 (
    echo 警告: 部分依赖可能缺失，尝试安装...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo 错误: 依赖安装失败
        pause
        exit /b 1
    )
)
echo 成功: 依赖检查通过

REM 创建必要目录
echo.
echo [5/6] 创建必要目录...
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "backups" mkdir backups
echo 成功: 目录创建完成

REM 测试连接
echo.
echo [6/6] 测试Lighter连接...
python -c "
import asyncio
import sys
sys.path.append('.')
from quant_trading.utils.config import Config
import lighter

async def test_connection():
    try:
        config = Config.from_file('config_windows_testnet.yaml')
        configuration = lighter.Configuration()
        configuration.host = config.lighter_base_url
        api_client = lighter.ApiClient(configuration)
        
        block_api = lighter.BlockApi(api_client)
        blocks = await block_api.blocks(limit=1)
        print('成功: Lighter连接测试通过')
        await api_client.close()
        return True
    except Exception as e:
        print(f'警告: 连接测试失败: {e}')
        print('注意: Windows平台不支持实际交易，仅用于测试')
        return False

result = asyncio.run(test_connection())
"
echo.

REM 选择启动模式
echo ========================================
echo   选择启动模式:
echo ========================================
echo 1. 启动Web系统 (前端 + 后端)
echo 2. 启动量化交易系统 (命令行)
echo 3. 启动完整系统 (Web + 交易)
echo 4. 运行回测
echo 5. 退出
echo ========================================

set /p choice="请输入选择 (1-5): "

if "%choice%"=="1" goto start_web
if "%choice%"=="2" goto start_trading
if "%choice%"=="3" goto start_full
if "%choice%"=="4" goto run_backtest
if "%choice%"=="5" goto end
echo 无效选择，请重新运行脚本
pause
exit /b 1

:start_web
echo.
echo 启动Web系统...
echo 启动后端服务...
start "Lighter Backend" cmd /k "cd web_backend && python main.py"
timeout /t 3 > nul

echo 启动前端服务...
start "Lighter Frontend" cmd /k "cd web_frontend && npm start"
echo.
echo Web系统启动完成！
echo 后端地址: http://localhost:8000
echo 前端地址: http://localhost:3000
echo.
echo 按任意键继续...
pause > nul
goto end

:start_trading
echo.
echo 启动量化交易系统...
echo 注意: Windows平台不支持实际交易，仅用于策略测试
echo.
python main.py --config config_windows_testnet.yaml
goto end

:start_full
echo.
echo 启动完整系统...
echo 启动后端服务...
start "Lighter Backend" cmd /k "cd web_backend && python main.py"
timeout /t 3 > nul

echo 启动前端服务...
start "Lighter Frontend" cmd /k "cd web_frontend && npm start"
timeout /t 5 > nul

echo 启动交易系统...
start "Lighter Trading" cmd /k "python main.py --config config_windows_testnet.yaml"
echo.
echo 完整系统启动完成！
echo 后端地址: http://localhost:8000
echo 前端地址: http://localhost:3000
echo 交易系统: 命令行模式
echo.
echo 按任意键继续...
pause > nul
goto end

:run_backtest
echo.
echo 运行回测...
echo 可用的回测选项:
echo 1. 动量策略回测
echo 2. 均值回归策略回测
echo 3. 自定义回测
echo.
set /p backtest_choice="请选择回测类型 (1-3): "

if "%backtest_choice%"=="1" (
    echo 运行动量策略回测...
    python run_backtest.py --strategy momentum --start-date 2024-01-01 --end-date 2024-01-31 --config config_windows_testnet.yaml
) else if "%backtest_choice%"=="2" (
    echo 运行均值回归策略回测...
    python run_backtest.py --strategy mean_reversion --start-date 2024-01-01 --end-date 2024-01-31 --config config_windows_testnet.yaml
) else if "%backtest_choice%"=="3" (
    set /p strategy_name="请输入策略名称: "
    set /p start_date="请输入开始日期 (YYYY-MM-DD): "
    set /p end_date="请输入结束日期 (YYYY-MM-DD): "
    python run_backtest.py --strategy %strategy_name% --start-date %start_date% --end-date %end_date% --config config_windows_testnet.yaml
) else (
    echo 无效选择
)
goto end

:end
echo.
echo ========================================
echo   系统已关闭
echo ========================================
echo.
echo 注意事项:
echo 1. Windows平台不支持实际交易
echo 2. 仅用于策略开发和测试
echo 3. 实际交易需要在Linux/macOS上运行
echo 4. 请定期备份重要数据
echo.
pause
