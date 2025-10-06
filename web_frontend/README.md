# Lighter量化交易系统 - 前端

基于React + TypeScript + Ant Design的现代化Web前端界面。

## 功能特性

### 🎯 核心功能
- **交易控制台**: 实时交易管理，支持多种订单类型
- **策略管理**: 创建、配置和管理量化交易策略
- **持仓管理**: 实时监控和管理交易持仓
- **图表分析**: 交互式K线图和技术指标
- **历史记录**: 完整的交易历史和数据分析

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

## 技术栈

- **React 18**: 现代化React框架
- **TypeScript**: 类型安全的JavaScript
- **Ant Design**: 企业级UI组件库
- **Recharts**: 数据可视化图表库
- **Zustand**: 轻量级状态管理
- **React Query**: 数据获取和缓存
- **React Router**: 客户端路由
- **Axios**: HTTP客户端
- **Socket.io**: WebSocket客户端

## 项目结构

```
src/
├── components/          # 组件
│   ├── Layout/         # 布局组件
│   ├── Trading/        # 交易相关组件
│   └── Dashboard/      # 仪表板组件
├── pages/              # 页面
│   ├── Login.tsx       # 登录页
│   ├── Dashboard.tsx   # 仪表板
│   ├── Trading.tsx     # 交易控制台
│   ├── Strategies.tsx  # 策略管理
│   ├── Positions.tsx   # 持仓管理
│   ├── History.tsx     # 交易历史
│   └── Settings.tsx    # 系统设置
├── store/              # 状态管理
│   ├── authStore.ts    # 认证状态
│   ├── tradingStore.ts # 交易状态
│   └── websocketStore.ts # WebSocket状态
├── api/                # API接口
│   ├── auth.ts         # 认证API
│   ├── trading.ts      # 交易API
│   ├── strategies.ts   # 策略API
│   ├── positions.ts    # 持仓API
│   └── notifications.ts # 通知API
├── types/              # 类型定义
│   └── index.ts        # 通用类型
├── utils/              # 工具函数
│   ├── constants.ts    # 常量配置
│   ├── helpers.ts      # 工具函数
│   └── index.ts        # 统一导出
├── App.tsx             # 主应用组件
└── index.tsx           # 应用入口
```

## 快速开始

### 环境要求

- Node.js 16+
- npm 8+ 或 yarn 1.22+

### 安装依赖

```bash
# 使用npm
npm install

# 或使用yarn
yarn install
```

### 环境配置

创建 `.env` 文件：

```env
# API配置
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws

# 应用配置
REACT_APP_NAME=Lighter量化交易系统
REACT_APP_VERSION=1.0.0
```

### 启动开发服务器

```bash
# 使用npm
npm start

# 或使用yarn
yarn start
```

应用将在 http://localhost:3000 启动。

### 构建生产版本

```bash
# 使用npm
npm run build

# 或使用yarn
yarn build
```

构建文件将生成在 `build` 目录中。

## 开发指南

### 代码规范

项目使用以下工具确保代码质量：

- **ESLint**: 代码检查
- **Prettier**: 代码格式化
- **TypeScript**: 类型检查

```bash
# 代码检查
npm run lint

# 代码格式化
npm run lint:fix

# 类型检查
npm run type-check
```

### 组件开发

1. **组件结构**: 使用函数式组件和Hooks
2. **类型定义**: 为所有props和state定义TypeScript类型
3. **样式**: 使用Ant Design组件和CSS模块
4. **状态管理**: 使用Zustand进行全局状态管理

### API集成

1. **API客户端**: 使用Axios创建API客户端
2. **错误处理**: 统一的错误处理机制
3. **类型安全**: 为所有API响应定义TypeScript类型
4. **缓存**: 使用React Query进行数据缓存

### 状态管理

使用Zustand进行状态管理：

```typescript
// 创建store
const useStore = create((set) => ({
  data: [],
  setData: (data) => set({ data }),
}));

// 使用store
const { data, setData } = useStore();
```

## 部署指南

### 开发环境

```bash
# 启动前端
npm start

# 启动后端（需要单独启动）
# 参考后端README
```

### 生产环境

#### 使用Docker

```bash
# 构建镜像
docker build -t lighter-frontend .

# 运行容器
docker run -p 3000:80 lighter-frontend
```

#### 使用Nginx

```bash
# 构建应用
npm run build

# 复制构建文件到Nginx目录
cp -r build/* /var/www/html/

# 配置Nginx
# 参考nginx.conf配置
```

## 常见问题

### Q: 如何添加新的交易对？

A: 在 `src/utils/constants.ts` 中的 `SYMBOLS` 数组添加新的交易对配置。

### Q: 如何自定义主题？

A: 在 `src/App.tsx` 中修改 `ConfigProvider` 的主题配置。

### Q: 如何添加新的技术指标？

A: 在 `src/utils/constants.ts` 中的 `TECHNICAL_INDICATORS` 数组添加新的指标配置。

### Q: 如何处理WebSocket连接断开？

A: 在 `src/store/websocketStore.ts` 中实现自动重连机制。

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

- 项目链接: [https://github.com/your-username/lighter-trading](https://github.com/your-username/lighter-trading)
- 问题反馈: [Issues](https://github.com/your-username/lighter-trading/issues)
