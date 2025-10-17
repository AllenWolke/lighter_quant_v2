@echo off
REM 查看交易信号脚本 - Windows

echo ============================================================
echo   交易信号查看器
echo ============================================================
echo.

set LOG_FILE=logs\quant_trading.log

if not exist "%LOG_FILE%" (
    echo [ERROR] 日志文件不存在
    pause
    exit /b 1
)

echo 📊 交易信号统计
echo ----------------------------------------
powershell -Command ^
"$signals = (Select-String -Path '%LOG_FILE%' -Pattern '交易信号').Count; ^
 $long = (Select-String -Path '%LOG_FILE%' -Pattern '交易信号: LONG').Count; ^
 $short = (Select-String -Path '%LOG_FILE%' -Pattern '交易信号: SHORT').Count; ^
 $exit = (Select-String -Path '%LOG_FILE%' -Pattern '交易信号: EXIT').Count; ^
 Write-Host '总信号数:' $signals; ^
 Write-Host '做多信号:' $long; ^
 Write-Host '做空信号:' $short; ^
 Write-Host '平仓信号:' $exit"

echo.
echo 📝 最近10个交易信号
echo ----------------------------------------
powershell -Command "Select-String -Path '%LOG_FILE%' -Pattern '交易信号' | Select-Object -Last 10 | ForEach-Object { $_.Line }"

echo.
echo 💰 交易记录
echo ----------------------------------------
powershell -Command "Select-String -Path '%LOG_FILE%' -Pattern '记录交易' | Select-Object -Last 5 | ForEach-Object { $_.Line }"

echo.
echo ⚠️  最近的警告
echo ----------------------------------------
powershell -Command "Select-String -Path '%LOG_FILE%' -Pattern 'WARNING' | Select-Object -Last 5 | ForEach-Object { $_.Line }"

echo.
echo ❌ 最近的错误
echo ----------------------------------------
powershell -Command "Select-String -Path '%LOG_FILE%' -Pattern 'ERROR' | Select-Object -Last 5 | ForEach-Object { $_.Line }" || echo 无错误

echo.
pause

