"""
技能树API服务器
独立启动FastAPI服务
"""

import os

os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

import yaml
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.skill_tree.api.routes import router as skill_tree_router
from src.rag_api.routes import router as rag_router

try:
    from src.multimodal.interface.api.routes import router as multimodal_router
    MULTIMODAL_AVAILABLE = True
except ImportError as e:
    MULTIMODAL_AVAILABLE = False
    print(f"⚠️ 多模态模块未安装: {e}")

try:
    from src.rss_gateway.routes import router as rss_router
    RSS_AVAILABLE = True
except Exception as e:
    RSS_AVAILABLE = False
    print(f"⚠️ RSS网关模块未安装: {e}")

# 读取配置文件
config_path = "./config/config.yaml"
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 获取服务端口配置
server_config = config.get('server', {})
api_port = server_config.get('api_port', 8000)
host = server_config.get('host', '127.0.0.1')

# 初始化FastAPI应用
app = FastAPI(
    title="技能树API",
    description="竞赛技能树管理API",
    version="1.0.0"
)

# 配置CORS
def _get_cors_origins():
    env_origins = os.environ.get("CORS_ORIGINS", "")
    if env_origins:
        return [origin.strip() for origin in env_origins.split(",") if origin.strip()]
    return [
        "http://localhost:5173",
        "http://localhost:8501",
        "http://localhost:3000",
    ]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(skill_tree_router)
app.include_router(rag_router)

if MULTIMODAL_AVAILABLE:
    app.include_router(multimodal_router)
    print("✅ 多模态RAG API路由已注册")

if RSS_AVAILABLE:
    app.include_router(rss_router)
    print("✅ RSS网关API路由已注册")

# 添加根路由
@app.get("/")
async def root():
    return {"message": "技能树API服务正常运行", "docs": "/docs"}

if __name__ == "__main__":
    print(f"Starting skill tree API server...")
    print(f"API address: http://localhost:{api_port}")
    print(f"API docs: http://localhost:{api_port}/docs")
    uvicorn.run(
        "server:app",
        host=host,
        port=api_port,
        reload=False
    )
