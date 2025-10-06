# Lighter量化交易系统 - Web部署指南

## 部署概述

本指南详细说明如何在生产环境中部署Lighter量化交易系统的Web界面，包括前端React应用和后端FastAPI服务的部署配置。

## 部署架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx反向代理  │    │   Docker容器    │    │   外部服务      │
│                 │    │                 │    │                 │
│ • 静态文件服务   │◄──►│ • React前端     │    │ • 数据库        │
│ • SSL终止       │    │ • FastAPI后端   │    │ • Redis缓存     │
│ • 负载均衡      │    │ • 交易引擎      │    │ • 邮件服务      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 环境要求

### 服务器要求
- **操作系统**: Ubuntu 20.04+ / CentOS 8+ / RHEL 8+
- **CPU**: 4核心以上
- **内存**: 8GB以上
- **存储**: 100GB以上SSD
- **网络**: 稳定的网络连接

### 软件要求
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Nginx**: 1.18+
- **Node.js**: 16+ (用于构建前端)
- **Python**: 3.8+ (用于构建后端)

## 部署方式

### 方式一：Docker部署（推荐）

#### 1. 创建Docker配置文件

**docker-compose.yml**
```yaml
version: '3.8'

services:
  # 数据库服务
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: lighter_trading
      POSTGRES_USER: trading_user
      POSTGRES_PASSWORD: your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  # Redis缓存服务
  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  # 后端服务
  backend:
    build:
      context: ./web_backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://trading_user:your_password@postgres:5432/lighter_trading
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=your-secret-key-here
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs

  # 前端服务
  frontend:
    build:
      context: ./web_frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    depends_on:
      - backend
    restart: unless-stopped

  # Nginx反向代理
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

**web_backend/Dockerfile**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建日志目录
RUN mkdir -p /app/logs

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**web_frontend/Dockerfile**
```dockerfile
FROM node:16-alpine as build

WORKDIR /app

# 复制package文件
COPY package*.json ./

# 安装依赖
RUN npm ci --only=production

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 生产阶段
FROM nginx:alpine

# 复制构建结果
COPY --from=build /app/build /usr/share/nginx/html

# 复制nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]
```

#### 2. 创建Nginx配置

**nginx.conf**
```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:80;
    }

    # 后端API代理
    server {
        listen 80;
        server_name api.yourdomain.com;

        location / {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /ws {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }

    # 前端应用代理
    server {
        listen 80;
        server_name yourdomain.com;

        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /api {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

#### 3. 部署步骤

```bash
# 1. 克隆项目
git clone <repository-url>
cd lighter_quantification_v2

# 2. 构建和启动服务
docker-compose up -d --build

# 3. 检查服务状态
docker-compose ps

# 4. 查看日志
docker-compose logs -f
```

### 方式二：传统部署

#### 1. 后端部署

```bash
# 1. 安装Python依赖
cd web_backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑.env文件，配置数据库、Redis等

# 3. 初始化数据库
python -c "from core.database import init_db; init_db()"

# 4. 启动服务
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### 2. 前端部署

```bash
# 1. 安装Node.js依赖
cd web_frontend
npm install

# 2. 构建生产版本
npm run build

# 3. 使用Nginx服务静态文件
# 将build目录内容复制到Nginx的html目录
cp -r build/* /var/www/html/
```

#### 3. Nginx配置

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    root /var/www/html;
    index index.html;

    # 前端路由
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket代理
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## SSL配置

### 1. 获取SSL证书

```bash
# 使用Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com
```

### 2. 更新Nginx配置

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # 其他配置...
}

# HTTP重定向到HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

## 监控和日志

### 1. 日志配置

**后端日志**
```python
# web_backend/core/logging.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler('logs/app.log', maxBytes=10*1024*1024, backupCount=5),
            logging.StreamHandler()
        ]
    )
```

**前端日志**
```javascript
// web_frontend/src/utils/logger.js
export const logger = {
  info: (message) => console.log(`[INFO] ${message}`),
  error: (message) => console.error(`[ERROR] ${message}`),
  warn: (message) => console.warn(`[WARN] ${message}`)
};
```

### 2. 监控配置

**Prometheus监控**
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'lighter-trading'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

**Grafana仪表板**
- 创建仪表板监控系统性能
- 设置告警规则
- 配置通知渠道

## 备份和恢复

### 1. 数据库备份

```bash
# 创建备份脚本
#!/bin/bash
BACKUP_DIR="/backup"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U trading_user lighter_trading > $BACKUP_DIR/backup_$DATE.sql

# 定期备份
0 2 * * * /path/to/backup_script.sh
```

### 2. 应用备份

```bash
# 备份应用代码
tar -czf app_backup_$(date +%Y%m%d).tar.gz web_backend/ web_frontend/

# 备份配置文件
cp -r config/ ssl/ nginx.conf backup/
```

## 安全配置

### 1. 防火墙设置

```bash
# UFW防火墙配置
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 2. 系统安全

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装安全工具
sudo apt install fail2ban ufw

# 配置fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. 应用安全

- 使用强密码
- 定期更新依赖
- 启用HTTPS
- 配置CORS
- 限制API访问

## 性能优化

### 1. 数据库优化

```sql
-- 创建索引
CREATE INDEX idx_trades_user_id ON trades(user_id);
CREATE INDEX idx_trades_created_at ON trades(created_at);
CREATE INDEX idx_orders_status ON orders(status);

-- 分区表
CREATE TABLE trades_2024_01 PARTITION OF trades
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

### 2. 缓存优化

```python
# Redis缓存配置
CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0',
    'CACHE_DEFAULT_TIMEOUT': 300
}
```

### 3. 前端优化

```javascript
// 代码分割
const Trading = lazy(() => import('./pages/Trading'));

// 缓存策略
const cacheConfig = {
  staleTime: 5 * 60 * 1000, // 5分钟
  cacheTime: 10 * 60 * 1000  // 10分钟
};
```

## 故障排除

### 1. 常见问题

**问题**: 服务无法启动
**解决**: 检查端口占用、依赖安装、配置文件

**问题**: 数据库连接失败
**解决**: 检查数据库服务、连接字符串、权限设置

**问题**: 前端无法访问后端
**解决**: 检查CORS配置、代理设置、网络连接

### 2. 日志分析

```bash
# 查看应用日志
tail -f logs/app.log

# 查看Nginx日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# 查看Docker日志
docker-compose logs -f backend
```

### 3. 性能监控

```bash
# 系统资源监控
htop
iostat -x 1
free -h

# 网络监控
netstat -tulpn
ss -tulpn
```

## 更新和维护

### 1. 应用更新

```bash
# 拉取最新代码
git pull origin main

# 重新构建和部署
docker-compose down
docker-compose up -d --build

# 或传统部署
npm run build
systemctl restart nginx
```

### 2. 定期维护

- 清理日志文件
- 更新系统包
- 备份数据库
- 检查磁盘空间
- 监控系统性能

---

**注意**: 生产环境部署前请充分测试，确保系统稳定性和安全性。
