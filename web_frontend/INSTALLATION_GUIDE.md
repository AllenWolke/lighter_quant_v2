# Lighter量化交易系统前端 - 安装指南

## 环境要求

- **Node.js**: 16.0.0 或更高版本
- **npm**: 8.0.0 或更高版本
- **操作系统**: Windows 10+, macOS 10.15+, Ubuntu 18.04+

## 快速安装

### Windows用户

1. **运行安装脚本**
   ```cmd
   install_dependencies.bat
   ```

2. **修复导入问题**
   ```cmd
   fix_imports.bat
   ```

3. **启动开发服务器**
   ```cmd
   start.bat
   ```

### Linux/Mac用户

1. **运行安装脚本**
   ```bash
   chmod +x install_dependencies.sh
   ./install_dependencies.sh
   ```

2. **启动开发服务器**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

## 手动安装

### 1. 检查环境

```bash
# 检查Node.js版本
node --version
# 应该显示 v16.0.0 或更高版本

# 检查npm版本
npm --version
# 应该显示 8.0.0 或更高版本
```

### 2. 安装依赖

```bash
# 进入前端目录
cd web_frontend

# 清理缓存
npm cache clean --force

# 删除旧的依赖（如果存在）
rm -rf node_modules package-lock.json

# 安装依赖
npm install
```

### 3. 配置环境变量

创建 `.env` 文件：

```env
# API配置
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws

# 应用配置
REACT_APP_NAME=Lighter量化交易系统
REACT_APP_VERSION=1.0.0

# 开发配置
GENERATE_SOURCEMAP=false
REACT_APP_DEBUG=true

# TypeScript配置
TSC_COMPILE_ON_ERROR=true
ESLINT_NO_DEV_ERRORS=true
```

### 4. 启动开发服务器

```bash
npm start
```

应用将在 http://localhost:3000 启动。

## 常见问题解决

### 问题1: 模块找不到错误

**错误信息**: `Cannot find module 'react' or its corresponding type declarations`

**解决方案**:
```bash
# 重新安装依赖
rm -rf node_modules package-lock.json
npm install

# 或者使用yarn
yarn install
```

### 问题2: TypeScript类型错误

**错误信息**: `JSX element implicitly has type 'any'`

**解决方案**:
1. 确保 `tsconfig.json` 配置正确
2. 确保安装了 `@types/react` 和 `@types/react-dom`
3. 重启TypeScript服务

### 问题3: 端口被占用

**错误信息**: `Port 3000 is already in use`

**解决方案**:
```bash
# 使用其他端口
PORT=3001 npm start

# 或者杀死占用端口的进程
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:3000 | xargs kill -9
```

### 问题4: 内存不足

**错误信息**: `JavaScript heap out of memory`

**解决方案**:
```bash
# 增加Node.js内存限制
export NODE_OPTIONS="--max-old-space-size=4096"
npm start
```

### 问题5: 依赖版本冲突

**错误信息**: `peer dependency warnings`

**解决方案**:
```bash
# 使用--legacy-peer-deps标志
npm install --legacy-peer-deps

# 或者使用yarn
yarn install
```

## 开发工具配置

### VS Code推荐扩展

1. **ES7+ React/Redux/React-Native snippets**
2. **TypeScript Importer**
3. **Auto Rename Tag**
4. **Bracket Pair Colorizer**
5. **Prettier - Code formatter**
6. **ESLint**

### VS Code设置

创建 `.vscode/settings.json`:

```json
{
  "typescript.preferences.importModuleSpecifier": "relative",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "emmet.includeLanguages": {
    "typescript": "html",
    "typescriptreact": "html"
  }
}
```

## 构建生产版本

```bash
# 构建生产版本
npm run build

# 预览构建结果
npx serve -s build -l 3000
```

## 部署到生产环境

### 使用Docker

```dockerfile
FROM node:16-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 使用Nginx

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    root /var/www/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 技术支持

如果遇到问题，请：

1. 检查Node.js和npm版本
2. 查看控制台错误信息
3. 检查网络连接
4. 查看项目文档
5. 联系技术支持

## 更新日志

- **v1.0.0**: 初始版本发布
- 支持React 18 + TypeScript
- 集成Ant Design UI组件库
- 实现完整的交易界面功能
