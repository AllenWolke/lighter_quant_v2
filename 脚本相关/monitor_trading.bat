@echo off
REM 量化交易系统监控脚本 - Windows

echo ============================================================
echo   Lighter 量化交易系统 - 实时监控
echo ============================================================
echo.
echo 日志文件: logs\quant_trading.log
echo 按 Ctrl+C 停止监控
echo.
echo ============================================================
echo.

REM 检查日志文件是否存在
if not exist "logs\quant_trading.log" (
    echo [ERROR] 日志文件不存在
    echo 请确保交易系统正在运行
    pause
    exit /b 1
)

REM 使用PowerShell实时监控日志
powershell -Command ^
"Get-Content logs\quant_trading.log -Wait -Tail 50 | ForEach-Object { ^
    if ($_ -match '交易信号') { ^
        Write-Host '[SIGNAL]' $_ -ForegroundColor Green ^
    } elseif ($_ -match '订单已成交') { ^
        Write-Host '[FILLED]' $_ -ForegroundColor Cyan ^
    } elseif ($_ -match '记录交易') { ^
        Write-Host '[TRADE]' $_ -ForegroundColor Blue ^
    } elseif ($_ -match 'ERROR') { ^
        Write-Host '[ERROR]' $_ -ForegroundColor Red ^
    } elseif ($_ -match 'WARNING') { ^
        Write-Host '[WARNING]' $_ -ForegroundColor Yellow ^
    } else { ^
        Write-Host $_ ^
    } ^
}"

