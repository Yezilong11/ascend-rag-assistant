"""
RAG API 中间件模块
提供统一错误处理、请求日志等中间件功能

关联文档：
- 代码规范.md 第 2.6 节 — 错误处理规范
- API接口文档.md 第 2.1 节 — 统一响应格式
- API接口文档.md 第 5 节 — 错误码参考
"""

import time
import logging
from typing import Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("rag_api")


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    全局异常处理中间件

    捕获所有未处理的异常，返回统一 JSON 格式响应。
    避免向客户端暴露内部错误详情（如堆栈信息）。

    响应格式遵循 API接口文档.md 第 2.1 节：
    {
        "success": false,
        "message": "服务器内部错误",
        "detail": "错误摘要（仅调试模式）"
    }
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            logger.error(
                "未处理异常: %s %s -> %s: %s",
                request.method,
                request.url.path,
                type(exc).__name__,
                str(exc),
                exc_info=True,
            )
            import json
            from starlette.responses import JSONResponse

            error_body = {
                "success": False,
                "message": "服务器内部错误",
            }

            return JSONResponse(
                status_code=500,
                content=error_body,
            )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    请求日志中间件

    记录每个请求的方法、路径、耗时、状态码。
    日志格式：[METHOD] /path -> 200 (0.123s)

    关联文档：代码规范.md 第 2.6.3 节 — 日志规范
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()

        response = await call_next(request)

        elapsed = time.perf_counter() - start_time
        logger.info(
            "[%s] %s -> %d (%.3fs)",
            request.method,
            request.url.path,
            response.status_code,
            elapsed,
        )

        return response


def register_error_handler(app: FastAPI) -> None:
    """
    注册全局异常处理器到 FastAPI 应用

    使用 BaseHTTPMiddleware 实现统一错误处理，
    捕获所有未处理异常并返回标准 JSON 格式。

    Args:
        app: FastAPI 应用实例
    """
    app.add_middleware(ErrorHandlingMiddleware)


def register_request_logger(app: FastAPI) -> None:
    """
    注册请求日志中间件到 FastAPI 应用

    记录每个请求的方法、路径、耗时、状态码，
    便于排查性能问题和追踪请求链路。

    Args:
        app: FastAPI 应用实例
    """
    app.add_middleware(RequestLoggingMiddleware)
