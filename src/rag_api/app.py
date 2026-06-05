"""
RAG API 应用工厂模块
提供 create_app() 工厂函数，创建并配置统一的 FastAPI 应用实例

统一服务架构：
- RAG API (技能问答)
- Skill Tree API (技能树管理)
- Multimodal API (多模态文档处理, 可选)

关联文档：
- API接口文档.md 第 1.1 节 — 服务架构
- API接口文档.md 第 7.2 节 — CORS 配置详情
- 代码规范.md 第 2.5 节 — 响应模型规范
"""

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.rag_api.routes import router as rag_router
from src.rag_api.middleware import register_error_handler, register_request_logger
from src.rss_gateway.routes import router as rss_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def _get_cors_origins():
    env_origins = os.environ.get("CORS_ORIGINS", "")
    if env_origins:
        return [origin.strip() for origin in env_origins.split(",") if origin.strip()]
    return [
        "http://localhost:5173",
        "http://localhost:8501",
        "http://localhost:3000",
    ]


CORS_ORIGINS = _get_cors_origins()


def create_app(include_skill_tree: bool = True, include_multimodal: bool = True, include_rss: bool = True) -> FastAPI:
    """
    创建并配置统一的 FastAPI 应用实例

    工厂模式设计，便于：
    - 测试时创建独立实例
    - 不同环境使用不同配置
    - 避免模块级副作用

    Args:
        include_skill_tree: 是否包含技能树API路由
        include_multimodal: 是否包含多模态API路由
        include_rss: 是否包含RSS网关API路由

    Returns:
        FastAPI: 配置好的应用实例
    """

    app = FastAPI(
        title="竞赛智能助手 API",
        description="昇腾AI竞赛智能助手 - 统一API服务",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "Accept"],
    )

    register_error_handler(app)
    register_request_logger(app)

    app.include_router(rag_router)

    if include_skill_tree:
        from src.skill_tree.api.routes import router as skill_tree_router
        app.include_router(skill_tree_router)
        logging.info("技能树API路由已注册")

    if include_multimodal:
        try:
            from src.multimodal.interface.api.routes import router as multimodal_router
            app.include_router(multimodal_router)
            logging.info("多模态API路由已注册")
        except ImportError as e:
            logging.warning(f"多模态模块未安装，部分功能不可用: {e}")

    if include_rss:
        try:
            app.include_router(rss_router)
            logging.info("RSS网关API路由已注册")
        except Exception as e:
            logging.warning(f"RSS网关模块注册失败: {e}")

    @app.get("/")
    async def root():
        return {
            "message": "竞赛智能助手API服务正常运行",
            "docs": "/docs",
            "services": {
                "rag": "/api/rag",
                "skill_tree": "/api/skill-tree" if include_skill_tree else None,
                "multimodal": "/api/multimodal" if include_multimodal else None,
                "rss": "/api/rss" if include_rss else None,
            }
        }

    return app
