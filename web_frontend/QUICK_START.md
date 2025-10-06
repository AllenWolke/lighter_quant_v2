# Lighter量化交易系统前端 - 快速启动指南

## 🚀 一键启动

### Windows用户
```cmd
# 1. 安装依赖（如果还没安装）
install_dependencies.bat

# 2. 启动开发服务器
start.bat
```

### Linux/Mac用户
```bash
# 1. 安装依赖（如果还没安装）
chmod +x install_dependencies.sh
./install_dependencies.sh

# 2. 启动开发服务器
chmod +x start.sh
./start.sh
```

## 📋 手动启动步骤

### 1. 检查环境
```bash
# 检查Node.js版本（需要16+）
node --version

# 检查npm版本（需要8+）
npm --version
```

### 2. 安装依赖
```bash
# 进入前端目录
cd web_frontend

# 安装依赖
npm install
```

### 3. 启动开发服务器
```bash
# 启动开发服务器
npm start
```

## 🌐 访问应用

启动成功后，在浏览器中访问：
- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/api/docs

## 🔧 功能特性

### ✅ 已实现的功能
1. **数字货币选择下拉框** - 支持ETH、BTC、BNB等多种数字货币
2. **交易策略选择下拉框** - 支持UT Bot、均值回归、动量、套利等策略
3. **策略参数调整下拉框** - 支持杠杆倍数、止损止盈等参数调整
4. **当前持仓信息显示** - 实时显示持仓金额、盈亏、杠杆等信息
5. **K线图显示界面** - 支持多种时间周期的K线图和技术指标

### 🎨 界面特性
- **响应式设计**: 支持桌面、平板、手机等设备
- **实时数据**: WebSocket实时推送市场数据
- **主题支持**: 支持明暗主题切换
- **国际化**: 支持多语言切换

### 🔧 技术特性
- **TypeScript**: 完整的类型安全
- **状态管理**: Zustand轻量级状态管理
- **图表库**: Recharts专业图表组件
- **UI组件**: Ant Design企业级UI组件库

## 📁 项目结构

```
web_frontend/
├── src/
│   ├── components/     # 组件
│   │   ├── Layout/    # 布局组件
│   │   ├── Trading/   # 交易组件
│   │   └── Dashboard/ # 仪表板组件
│   ├── pages/         # 页面
│   │   ├── Login.tsx      # 登录页
│   │   ├── Dashboard.tsx  # 仪表板
│   │   ├── Trading.tsx    # 交易控制台
│   │   ├── Strategies.tsx # 策略管理
│   │   ├── Positions.tsx  # 持仓管理
│   │   ├── History.tsx    # 交易历史
│   │   └── Settings.tsx   # 系统设置
│   ├── store/         # 状态管理
│   ├── api/           # API接口
│   ├── types/         # 类型定义
│   ├── utils/         # 工具函数
│   ├── App.tsx        # 主应用
│   └── index.tsx      # 应用入口
├── package.json       # 依赖配置
├── tsconfig.json      # TypeScript配置
└── README.md          # 项目说明
```

## 🛠️ 开发命令

```bash
# 启动开发服务器
npm start

# 构建生产版本
npm run build

# 运行测试
npm test

# 代码检查
npm run lint

# 代码格式化
npm run lint:fix

# 类型检查
npm run type-check
```

## 🐛 常见问题

### 问题1: 端口被占用
```bash
# 使用其他端口
PORT=3001 npm start
```

### 问题2: 模块找不到
```bash
# 重新安装依赖
rm -rf node_modules package-lock.json
npm install
```

### 问题3: TypeScript错误
```bash
# 重启TypeScript服务
# 在VS Code中按 Ctrl+Shift+P，输入 "TypeScript: Restart TS Server"
```

## 📚 更多文档

- [完整安装指南](INSTALLATION_GUIDE.md)
- [项目README](README.md)
- [API文档](http://localhost:8000/api/docs)

## 🎉 开始使用

1. 启动前端应用
2. 在浏览器中访问 http://localhost:3000
3. 使用默认账户登录（或注册新账户）
4. 开始体验量化交易系统！

---

**注意**: 确保后端服务也在运行（端口8000），否则前端无法获取数据。
