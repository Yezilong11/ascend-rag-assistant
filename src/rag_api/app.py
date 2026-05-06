"""
RAG API 应用工厂模块
提供 create_app() 工厂函数，创建并配置 FastAPI 应用实例

关联文档：
- API接口文档.md 第 1.1 节 — 服务架构
- API接口文档.md 第 7.2 节 — CORS 配置详情
- 代码规范.md 第 2.5 节 — 响应模型规范
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.rag_api.routes import router as rag_router
from src.rag_api.middleware import register_error_handler, register_request_logger

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def create_app() -> FastAPI:
    """
    创建并配置 RAG API FastAPI 应用实例

    工厂模式设计，便于：
    - 测试时创建独立实例
    - 不同环境使用不同配置
    - 避免模块级副作用

    Returns:
        FastAPI: 配置好的应用实例
    """

    app = FastAPI(
        title="RAG API",
        description="昇腾AI竞赛智能助教 - RAG问答引擎API",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://localhost:8501",
            "http://localhost:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_error_handler(app)
    register_request_logger(app)

    app.include_router(rag_router)

    @app.get("/")
    async def root():
        return {"message": "RAG API服务正常运行", "docs": "/docs"}

    return app
