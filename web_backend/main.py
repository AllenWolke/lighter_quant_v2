"""
Web后端主应用
基于FastAPI的量化交易系统Web API
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import asyncio
import logging
import json
import os
from datetime import datetime

from core.config import settings
# from core.database import init_db
from api.routes import auth, trading, data, strategies, positions, notifications
from services.trading_service import TradingService
from services.data_service import DataService
from services.websocket_manager import WebSocketManager
from models.database import init_database


# 全局服务实例
trading_service = None
data_service = None
websocket_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global trading_service, data_service, websocket_manager
    
    # 启动时初始化
    logging.info("启动Web后端服务...")
    
    # 初始化数据库
    await init_database()
    
    # 初始化服务
    trading_service = TradingService()
    data_service = DataService()
    websocket_manager = WebSocketManager()
    
    # 启动后台任务
    asyncio.create_task(websocket_manager.start())
    asyncio.create_task(trading_service.start_background_tasks())
    
    logging.info("Web后端服务启动完成")
    
    yield
    
    # 关闭时清理
    logging.info("关闭Web后端服务...")
    
    if websocket_manager:
        await websocket_manager.stop()
    if trading_service:
        await trading_service.stop()
    
    logging.info("Web后端服务已关闭")


# 创建FastAPI应用
app = FastAPI(
    title="Lighter量化交易系统API",
    description="基于FastAPI的量化交易系统Web API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# 静态文件服务（可选，如果前端构建文件存在）
if os.path.exists("web_frontend/build/static"):
    app.mount("/static", StaticFiles(directory="web_frontend/build/static"), name="static")

# 包含路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(trading.router, prefix="/api/trading", tags=["交易"])
app.include_router(data.router, prefix="/api/data", tags=["数据"])
app.include_router(strategies.router, prefix="/api/strategies", tags=["策略"])
app.include_router(positions.router, prefix="/api/positions", tags=["持仓"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["通知"])


@app.get("/")
async def root():
    """根路径，返回前端页面"""
    try:
        with open("web_frontend/build/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse("""
        <html>
            <head><title>Lighter量化交易系统</title></head>
            <body>
                <h1>Lighter量化交易系统</h1>
                <p>前端页面未找到，请先构建前端项目</p>
                <p>运行命令: cd web_frontend && npm run build</p>
            </body>
        </html>
        """)


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket连接端点"""
    # 生成唯一的客户端ID
    import uuid
    client_id = str(uuid.uuid4())
    
    try:
        # 建立连接
        await websocket_manager.connect(websocket, client_id)
        
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 处理不同类型的消息
            if message.get("type") == "subscribe":
                # 订阅数据更新
                channel = message.get("channel") or message.get("symbol")
                if channel:
                    await websocket_manager.subscribe(client_id, channel)
                    await websocket.send_text(json.dumps({
                        "type": "subscribed",
                        "channel": channel
                    }))
                
            elif message.get("type") == "unsubscribe":
                # 取消订阅
                channel = message.get("channel") or message.get("symbol")
                if channel:
                    await websocket_manager.unsubscribe(client_id, channel)
                    await websocket.send_text(json.dumps({
                        "type": "unsubscribed",
                        "channel": channel
                    }))
                
            elif message.get("type") == "ping":
                # 心跳检测
                await websocket.send_text(json.dumps({"type": "pong"}))
                
    except WebSocketDisconnect:
        logging.info(f"WebSocket客户端断开连接: {client_id}")
        await websocket_manager.disconnect(client_id)
    except Exception as e:
        logging.error(f"WebSocket错误 ({client_id}): {e}")
        await websocket_manager.disconnect(client_id)


# 依赖注入
def get_trading_service() -> TradingService:
    """获取交易服务实例"""
    if trading_service is None:
        raise HTTPException(status_code=503, detail="交易服务未初始化")
    return trading_service


def get_data_service() -> DataService:
    """获取数据服务实例"""
    if data_service is None:
        raise HTTPException(status_code=503, detail="数据服务未初始化")
    return data_service


def get_websocket_manager() -> WebSocketManager:
    """获取WebSocket管理器实例"""
    if websocket_manager is None:
        raise HTTPException(status_code=503, detail="WebSocket管理器未初始化")
    return websocket_manager


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
