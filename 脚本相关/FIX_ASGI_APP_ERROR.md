# 🔧 ASGI App 启动错误修复指南

## 📊 问题现象

后端日志显示错误：
```
ERROR: Error loading ASGI app. Attribute "app" not found in module "main".
```

---

## 🔍 问题根源

### 常见原因

#### 1. **工作目录不正确** ⭐ 最常见

**错误的启动方式**:
```bash
# ❌ 在项目根目录启动
cd lighter_quantification_v2
python -m uvicorn main:app --host 0.0.0.0 --port 8000
# 错误：找不到 main 模块
```

**正确的启动方式**:
```bash
# ✓ 在 web_backend 目录启动
cd lighter_quantification_v2/web_backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
# 正确：可以找到 main.py
```

---

#### 2. **启动命令路径问题**

**错误示例**:
```bash
cd lighter_quantification_v2
uvicorn web_backend.main:app  # ❌ 可能导致模块导入问题
```

**正确示例**:
```bash
cd lighter_quantification_v2/web_backend
uvicorn main:app  # ✓ 简单清晰
```

---

#### 3. **Python 路径配置问题**

如果 `main.py` 中的导入失败，也会导致 app 对象无法创建。

---

## ✅ 修复方案

### 方法1: 使用修复脚本（推荐）

#### Windows:
```cmd
fix_websocket_windows.bat
```

这个脚本会：
- ✓ 自动切换到正确的目录
- ✓ 使用正确的启动命令
- ✓ 创建必要的日志目录

---

#### Linux/macOS:
```bash
./fix_websocket_and_restart.sh
```

---

### 方法2: 手动启动（正确方式）

#### 步骤1: 停止现有进程

**Windows**:
```cmd
taskkill /F /IM python.exe
```

**Linux/macOS**:
```bash
pkill -f uvicorn
```

#### 步骤2: 切换到正确目录

```bash
cd lighter_quantification_v2/web_backend
```

⚠️ **重要**: 必须在 `web_backend` 目录下启动！

#### 步骤3: 启动服务

**前台启动**（推荐用于调试）:
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**后台启动**:

**Windows**:
```cmd
start /B python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**Linux/macOS**:
```bash
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 > ../logs/web_backend.log 2>&1 &
```

#### 步骤4: 验证启动

```bash
# 等待2秒
sleep 2  # Linux/macOS
timeout /t 2  # Windows

# 测试健康检查
curl http://localhost:8000/api/health
```

**期望输出**:
```json
{"status":"healthy","timestamp":"...","version":"1.0.0"}
```

---

## 🔍 诊断步骤

### 诊断1: 检查当前目录

```bash
# Windows
cd

# Linux/macOS
pwd
```

**应该显示**:
```
D:\project\lighter_quantification_v2\web_backend  # Windows
/path/to/lighter_quantification_v2/web_backend    # Linux
```

如果不是，使用 `cd web_backend` 切换。

---

### 诊断2: 验证 main.py 存在

```bash
# Windows
dir main.py

# Linux/macOS
ls -la main.py
```

**应该看到**:
```
main.py
```

---

### 诊断3: 测试 Python 导入

```bash
python -c "import main; print('✓ main 模块可以导入'); print('✓ app 对象:', hasattr(main, 'app'))"
```

**期望输出**:
```
✓ main 模块可以导入
✓ app 对象: True
```

如果失败，说明 `main.py` 中有语法错误或导入问题。

---

### 诊断4: 检查依赖

```bash
python -c "import fastapi, uvicorn, sqlalchemy, pydantic; print('✓ 所有核心依赖已安装')"
```

如果失败，安装依赖：
```bash
pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings
```

---

## 🐛 常见错误和解决方案

### 错误1: `ModuleNotFoundError: No module named 'main'`

**原因**: 工作目录不正确

**解决**:
```bash
cd web_backend  # 切换到正确目录
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

---

### 错误2: `ModuleNotFoundError: No module named 'fastapi'`

**原因**: 缺少依赖

**解决**:
```bash
pip install fastapi uvicorn[standard]
```

---

### 错误3: `AttributeError: module 'main' has no attribute 'app'`

**原因**: `main.py` 中有错误，导致 `app` 对象未创建

**诊断**:
```bash
python main.py
# 查看错误输出
```

**常见原因**:
- 导入错误（检查所有 import 语句）
- 语法错误（检查 Python 代码）
- 配置文件缺失（检查 `core/config.py`）

---

### 错误4: `ImportError: cannot import name 'settings' from 'core.config'`

**原因**: 配置模块有问题

**检查**:
```bash
python -c "from core.config import settings; print('✓ settings 导入成功')"
```

**解决**: 检查 `web_backend/core/config.py` 文件

---

## 📝 正确的启动流程

### 完整的启动命令序列

```bash
# 1. 进入项目根目录
cd /path/to/lighter_quantification_v2

# 2. 创建必要的目录
mkdir -p logs data backups

# 3. 进入后端目录
cd web_backend

# 4. 验证环境
python -c "import main; print('环境正常')"

# 5. 启动服务
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# 6. 在另一个终端验证
curl http://localhost:8000/api/health
```

---

## 🔄 改进的启动脚本

创建一个新的启动脚本 `start_backend_correctly.bat` (Windows):

```batch
@echo off
chcp 65001 >nul
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║     启动 Web 后端服务 - 正确方式                          ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM 获取脚本所在目录
cd /d "%~dp0"

REM 创建必要目录
if not exist "logs" mkdir logs
if not exist "data" mkdir data

REM 切换到 web_backend 目录
cd web_backend

REM 检查 main.py 是否存在
if not exist "main.py" (
    echo ✗ 错误: 找不到 main.py
    echo 当前目录: %CD%
    echo 请确保在正确的目录中运行此脚本
    pause
    exit /b 1
)

echo ✓ 找到 main.py
echo.

REM 验证 Python 环境
python -c "import main; print('✓ Python 环境验证成功')" 2>nul
if %errorlevel% neq 0 (
    echo ✗ Python 环境验证失败
    echo 请检查依赖是否已安装
    pause
    exit /b 1
)

echo.
echo 正在启动后端服务...
echo 端口: 8000
echo 日志: ../logs/web_backend.log
echo.

REM 启动服务
start /B python -m uvicorn main:app --host 0.0.0.0 --port 8000 > ..\logs\web_backend.log 2>&1

REM 等待启动
timeout /t 3 /nobreak >nul

REM 测试服务
curl -s http://localhost:8000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo.
    echo ✓ 后端服务启动成功！
    echo.
    echo 访问地址:
    echo   API: http://localhost:8000
    echo   文档: http://localhost:8000/api/docs
    echo.
) else (
    echo.
    echo ⚠️  服务可能未完全启动
    echo 请查看日志: type ..\logs\web_backend.log
    echo.
)

pause
```

---

### Linux/macOS 启动脚本 `start_backend_correctly.sh`:

```bash
#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     启动 Web 后端服务 - 正确方式                          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 创建必要目录
mkdir -p logs data

# 切换到 web_backend 目录
cd web_backend

# 检查 main.py
if [ ! -f "main.py" ]; then
    echo "✗ 错误: 找不到 main.py"
    echo "当前目录: $(pwd)"
    exit 1
fi

echo "✓ 找到 main.py"
echo

# 验证 Python 环境
if ! python3 -c "import main; print('✓ Python 环境验证成功')" 2>/dev/null; then
    echo "✗ Python 环境验证失败"
    echo "请检查依赖是否已安装"
    exit 1
fi

echo
echo "正在启动后端服务..."
echo "端口: 8000"
echo "日志: ../logs/web_backend.log"
echo

# 启动服务
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > ../logs/web_backend.log 2>&1 &
PID=$!

# 等待启动
sleep 3

# 测试服务
if curl -s http://localhost:8000/api/health >/dev/null 2>&1; then
    echo
    echo "✓ 后端服务启动成功！"
    echo "  PID: $PID"
    echo
    echo "访问地址:"
    echo "  API: http://localhost:8000"
    echo "  文档: http://localhost:8000/api/docs"
    echo
else
    echo
    echo "⚠️  服务可能未完全启动"
    echo "请查看日志: tail -f ../logs/web_backend.log"
    echo
fi
```

---

## ✅ 验证清单

启动后，请确认：

- [ ] 当前目录是 `web_backend`
- [ ] `main.py` 文件存在
- [ ] Python 可以导入 `main` 模块
- [ ] `curl http://localhost:8000/api/health` 返回 200
- [ ] 日志文件已创建（如果使用后台启动）
- [ ] 浏览器可以访问 `http://localhost:8000/api/docs`

---

## 🎯 快速命令参考

| 操作 | 命令 |
|------|------|
| **正确启动** | `cd web_backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000` |
| **检查目录** | `pwd` (Linux) / `cd` (Windows) |
| **验证环境** | `python -c "import main"` |
| **测试服务** | `curl http://localhost:8000/api/health` |
| **查看日志** | `tail -f ../logs/web_backend.log` (Linux)<br>`type ..\logs\web_backend.log` (Windows) |
| **停止服务** | `pkill -f uvicorn` (Linux)<br>`taskkill /F /IM python.exe` (Windows) |

---

## 📚 相关文档

- **后端主文件**: `web_backend/main.py`
- **配置文件**: `web_backend/core/config.py`
- **WebSocket 修复**: `WEBSOCKET_CONNECTION_FIX_GUIDE.md`
- **快速启动**: `QUICK_FIX_WEBSOCKET.md`

---

## ⏱️ 预计修复时间

- **诊断问题**: 1-2 分钟
- **修复启动**: 1 分钟
- **验证测试**: 1 分钟

**总计**: 约 3-5 分钟

---

## 🎉 成功标志

修复成功后：

1. ✅ 命令行没有报错
2. ✅ 可以访问 `http://localhost:8000/api/health`
3. ✅ 可以访问 `http://localhost:8000/api/docs`
4. ✅ 日志文件正常生成
5. ✅ Dashboard 页面可以加载数据

---

**🚀 立即修复**: 
```bash
cd web_backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

