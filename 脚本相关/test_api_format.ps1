# 测试 API 响应格式
Write-Host ""
Write-Host "============================================================" -ForegroundColor Blue
Write-Host "测试 API 响应格式" -ForegroundColor Blue
Write-Host "============================================================" -ForegroundColor Blue
Write-Host ""

# 步骤1: 登录
Write-Host "[步骤 1/3] 登录..." -ForegroundColor Cyan
Write-Host ""

$loginBody = @{
    username = "admin"
    password = "admin123"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" `
        -Method Post `
        -Body $loginBody `
        -ContentType "application/json"
    
    $token = $loginResponse.accessToken
    if (-not $token) {
        $token = $loginResponse.access_token
    }
    
    Write-Host "✓ 登录成功" -ForegroundColor Green
    Write-Host "  Token: $($token.Substring(0,20))..." -ForegroundColor Gray
} catch {
    Write-Host "✗ 登录失败: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 步骤2: 获取账户信息
Write-Host "[步骤 2/3] 获取账户信息..." -ForegroundColor Cyan
Write-Host ""

try {
    $headers = @{
        "Authorization" = "Bearer $token"
    }
    
    $accountResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/trading/account" `
        -Method Get `
        -Headers $headers
    
    Write-Host "✓ 获取账户信息成功" -ForegroundColor Green
    Write-Host ""
    Write-Host "完整响应:" -ForegroundColor Yellow
    $accountResponse | ConvertTo-Json -Depth 5
} catch {
    Write-Host "✗ 获取失败: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 步骤3: 分析字段格式
Write-Host "[步骤 3/3] 分析字段格式..." -ForegroundColor Cyan
Write-Host ""

$hasCamelAvailable = $accountResponse.PSObject.Properties.Name -contains "availableBalance"
$hasSnakeAvailable = $accountResponse.PSObject.Properties.Name -contains "available_balance"

Write-Host "字段名检查:"
if ($hasCamelAvailable) {
    Write-Host "  camelCase (availableBalance): ✓ 存在" -ForegroundColor Green
} else {
    Write-Host "  camelCase (availableBalance): ✗ 不存在" -ForegroundColor Red
}

if ($hasSnakeAvailable) {
    Write-Host "  snake_case (available_balance): ✓ 存在" -ForegroundColor Yellow
} else {
    Write-Host "  snake_case (available_balance): ✗ 不存在" -ForegroundColor Gray
}

Write-Host ""

if ($hasCamelAvailable) {
    Write-Host "✓ API 响应使用 camelCase（前端兼容）" -ForegroundColor Green
    Write-Host ""
    Write-Host "关键字段:"
    Write-Host "  availableBalance: $($accountResponse.availableBalance)" -ForegroundColor Cyan
    Write-Host "  marginBalance: $($accountResponse.marginBalance)" -ForegroundColor Cyan
    Write-Host "  balance: $($accountResponse.balance)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "✅ 后端配置正确！" -ForegroundColor Green
    Write-Host ""
    Write-Host "如果前端仍显示 0，请:" -ForegroundColor Yellow
    Write-Host "  1. 清除浏览器缓存: F12 → Application → Clear site data"
    Write-Host "  2. 强制刷新: Ctrl+Shift+R"
    Write-Host "  3. 重新登录"
    Write-Host "  4. 检查浏览器 Console 是否有错误"
    
} elseif ($hasSnakeAvailable) {
    Write-Host "⚠️  API 响应使用 snake_case（前端不兼容）" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "当前字段:"
    Write-Host "  available_balance: $($accountResponse.available_balance)" -ForegroundColor Gray
    Write-Host "  margin_balance: $($accountResponse.margin_balance)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "❌ 后端配置未生效！" -ForegroundColor Red
    Write-Host ""
    Write-Host "修复步骤:" -ForegroundColor Yellow
    Write-Host "  1. 清理 Python 缓存:"
    Write-Host "     Remove-Item -Recurse -Force web_backend\__pycache__"
    Write-Host "     Remove-Item -Recurse -Force web_backend\**\__pycache__"
    Write-Host ""
    Write-Host "  2. 重启后端服务:"
    Write-Host "     taskkill /F /IM python.exe"
    Write-Host "     cd web_backend"
    Write-Host "     python -m uvicorn main:app --host 0.0.0.0 --port 8000"
    Write-Host ""
    Write-Host "  3. 重新运行此测试"
    exit 1
    
} else {
    Write-Host "✗ 无法识别字段格式" -ForegroundColor Red
    Write-Host ""
    Write-Host "响应包含的字段:"
    $accountResponse.PSObject.Properties | ForEach-Object {
        Write-Host "  $($_.Name): $($_.Value)"
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Blue

