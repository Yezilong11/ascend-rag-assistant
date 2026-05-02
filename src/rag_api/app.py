"""
RAG API 应用工厂模块
提供 create_app() 工厂函数，创建并配置 FastAPI 应用实例
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.rag_api.routes import router as rag_router


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

    # 初始化 FastAPI 应用
    app = FastAPI(
        title="RAG API",
        description="昇腾AI竞赛智能助教 - RAG问答引擎API",
        version="1.0.0",
    )

    # 配置 CORS 跨域访问
    # 允许前端开发服务器 (5173)、Streamlit (8501) 和备用端口 (3000) 访问
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",   # React 前端开发服务器 (Vite 默认端口)
            "http://localhost:8501",   # Streamlit 前端 (兼容旧版)
            "http://localhost:3000",   # 备用前端端口
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册 RAG API 路由
    app.include_router(rag_router)

    # 根路由 - 服务健康检查与文档入口
    @app.get("/")
    async def root():
        return {"message": "RAG API服务正常运行", "docs": "/docs"}

    return app
