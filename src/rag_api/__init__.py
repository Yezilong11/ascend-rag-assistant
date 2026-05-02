"""
RAG API 模块
将 RAG 引擎封装为独立的 FastAPI 微服务
"""

from src.rag_api.app import create_app

__all__ = ["create_app"]
