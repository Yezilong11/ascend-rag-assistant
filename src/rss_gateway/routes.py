"""
RSS 网关代理路由模块
将前端对 RSS 服务的请求代理转发到后端 Go 服务，并提供知识库桥接功能

路由前缀: /api/rss
标签: rss

端点列表：
    健康检查:
        GET  /api/rss/health                         — RSS 服务健康检查

    Feeds 代理:
        GET    /api/rss/feeds                        — 获取 Feed 列表
        POST   /api/rss/feeds                        — 创建 Feed
        GET    /api/rss/feeds/{id}                   — 获取单个 Feed
        PUT    /api/rss/feeds/{id}                   — 更新 Feed
        DELETE /api/rss/feeds/{id}                   — 删除 Feed
        POST   /api/rss/feeds/{id}/crawl             — 抓取单个 Feed
        POST   /api/rss/feeds/crawl-all              — 抓取所有 Feed

    Articles 代理:
        GET    /api/rss/articles                     — 获取文章列表
        GET    /api/rss/articles/{id}                — 获取单篇文章
        PUT    /api/rss/articles/{id}/read           — 标记文章已读
        PUT    /api/rss/articles/read-all            — 标记所有文章已读
        DELETE /api/rss/articles/{id}                — 删除文章

    Categories 代理:
        GET    /api/rss/categories                   — 获取分类列表
        POST   /api/rss/categories                   — 创建分类
        GET    /api/rss/categories/{id}              — 获取单个分类
        PUT    /api/rss/categories/{id}              — 更新分类
        DELETE /api/rss/categories/{id}              — 删除分类
        PUT    /api/rss/categories/reorder           — 分类排序

    Tags 代理:
        GET    /api/rss/tags                         — 获取标签列表
        POST   /api/rss/tags                         — 创建标签
        GET    /api/rss/tags/{id}                    — 获取单个标签
        DELETE /api/rss/tags/{id}                    — 删除标签

    AI 代理:
        GET    /api/rss/ai/config                    — 获取 AI 配置
        PUT    /api/rss/ai/config                    — 更新 AI 配置
        POST   /api/rss/ai/test                      — 测试 AI 连接
        POST   /api/rss/articles/{id}/analyze        — AI 分析单篇文章
        POST   /api/rss/articles/analyze-all         — AI 分析所有文章

    System 代理:
        GET    /api/rss/system/stats                 — 获取系统统计
        GET    /api/rss/system/status                — 获取系统状态

    Bridge 路由（知识库桥接）:
        POST   /api/rss/bridge/ingest-article/{id}   — 导入单篇文章到知识库
        POST   /api/rss/bridge/ingest-feed/{id}      — 导入 Feed 下所有文章到知识库
        POST   /api/rss/bridge/ingest-all-unread      — 导入所有未读文章到知识库
        GET    /api/rss/bridge/status                 — 获取桥接状态
"""

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse

from .client import RSSClient, RSSServiceUnavailableError
from .models import (
    RSSCategoryCreate,
    RSSFeedCreate,
    RSSFeedUpdate,
    RSSTagCreate,
)
from .bridge import ingest_article, ingest_feed, ingest_all_unread, get_bridge_status

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/rss", tags=["rss"])

# 模块级 RSSClient 单例
_rss_client: Optional[RSSClient] = None


def get_rss_client() -> RSSClient:
    """获取 RSSClient 单例实例"""
    global _rss_client
    if _rss_client is None:
        _rss_client = RSSClient()
    return _rss_client


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------

async def _proxy(method: str, path: str, **kwargs) -> JSONResponse:
    """
    通用代理转发函数，将请求转发到 Go RSS 服务并返回响应。
    捕获 RSSServiceUnavailableError 并返回 503。
    """
    client = get_rss_client()
    try:
        resp = await client.proxy_request(method, path, **kwargs)
        return JSONResponse(
            status_code=resp.status_code,
            content=resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {"data": resp.text},
        )
    except RSSServiceUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))


# ===========================================================================
# 健康检查
# ===========================================================================

@router.get("/health")
async def health_check():
    """RSS 服务健康检查"""
    client = get_rss_client()
    result = await client.health_check()
    if result["available"]:
        return {"success": True, "data": result["data"]}
    return JSONResponse(
        status_code=503,
        content={"success": False, "message": "RSS服务不可用", "error": result.get("error", "")},
    )


# ===========================================================================
# Feeds 代理
# ===========================================================================

@router.get("/feeds")
async def list_feeds(request: Request):
    """获取 Feed 列表"""
    params = dict(request.query_params)
    return await _proxy("GET", "/feeds", params=params)


@router.post("/feeds")
async def create_feed(body: RSSFeedCreate):
    """创建 Feed"""
    return await _proxy("POST", "/feeds", json=body.model_dump(exclude_none=True))


@router.get("/feeds/{feed_id}")
async def get_feed(feed_id: int):
    """获取单个 Feed"""
    return await _proxy("GET", f"/feeds/{feed_id}")


@router.put("/feeds/{feed_id}")
async def update_feed(feed_id: int, body: RSSFeedUpdate):
    """更新 Feed"""
    return await _proxy("PUT", f"/feeds/{feed_id}", json=body.model_dump(exclude_none=True))


@router.delete("/feeds/{feed_id}")
async def delete_feed(feed_id: int):
    """删除 Feed"""
    return await _proxy("DELETE", f"/feeds/{feed_id}")


@router.post("/feeds/{feed_id}/crawl")
async def crawl_feed(feed_id: int):
    """抓取单个 Feed"""
    return await _proxy("POST", f"/feeds/{feed_id}/crawl")


@router.post("/feeds/crawl-all")
async def crawl_all_feeds():
    """抓取所有 Feed"""
    return await _proxy("POST", "/feeds/crawl-all")


# ===========================================================================
# Articles 代理
# ===========================================================================

@router.get("/articles")
async def list_articles(request: Request):
    """获取文章列表"""
    params = dict(request.query_params)
    return await _proxy("GET", "/articles", params=params)


@router.get("/articles/{article_id}")
async def get_article(article_id: int):
    """获取单篇文章"""
    return await _proxy("GET", f"/articles/{article_id}")


@router.put("/articles/{article_id}/read")
async def mark_article_read(article_id: int):
    """标记文章已读"""
    return await _proxy("PUT", f"/articles/{article_id}/read")


@router.put("/articles/read-all")
async def mark_all_read(request: Request):
    """标记所有文章已读"""
    params = dict(request.query_params)
    return await _proxy("PUT", "/articles/read-all", params=params)


@router.delete("/articles/{article_id}")
async def delete_article(article_id: int):
    """删除文章"""
    return await _proxy("DELETE", f"/articles/{article_id}")


# ===========================================================================
# Categories 代理
# ===========================================================================

@router.get("/categories")
async def list_categories():
    """获取分类列表"""
    return await _proxy("GET", "/categories")


@router.post("/categories")
async def create_category(body: RSSCategoryCreate):
    """创建分类"""
    return await _proxy("POST", "/categories", json=body.model_dump(exclude_none=True))


@router.get("/categories/{category_id}")
async def get_category(category_id: int):
    """获取单个分类"""
    return await _proxy("GET", f"/categories/{category_id}")


@router.put("/categories/{category_id}")
async def update_category(category_id: int, body: RSSCategoryCreate):
    """更新分类"""
    return await _proxy("PUT", f"/categories/{category_id}", json=body.model_dump(exclude_none=True))


@router.delete("/categories/{category_id}")
async def delete_category(category_id: int):
    """删除分类"""
    return await _proxy("DELETE", f"/categories/{category_id}")


@router.put("/categories/reorder")
async def reorder_categories(request: Request):
    """分类排序"""
    body = await request.json()
    return await _proxy("PUT", "/categories/reorder", json=body)


# ===========================================================================
# Tags 代理
# ===========================================================================

@router.get("/tags")
async def list_tags():
    """获取标签列表"""
    return await _proxy("GET", "/tags")


@router.post("/tags")
async def create_tag(body: RSSTagCreate):
    """创建标签"""
    return await _proxy("POST", "/tags", json=body.model_dump(exclude_none=True))


@router.get("/tags/{tag_id}")
async def get_tag(tag_id: int):
    """获取单个标签"""
    return await _proxy("GET", f"/tags/{tag_id}")


@router.delete("/tags/{tag_id}")
async def delete_tag(tag_id: int):
    """删除标签"""
    return await _proxy("DELETE", f"/tags/{tag_id}")


# ===========================================================================
# AI 代理
# ===========================================================================

@router.get("/ai/config")
async def get_ai_config():
    """获取 AI 配置"""
    return await _proxy("GET", "/ai/config")


@router.put("/ai/config")
async def update_ai_config(request: Request):
    """更新 AI 配置"""
    body = await request.json()
    return await _proxy("PUT", "/ai/config", json=body)


@router.post("/ai/test")
async def test_ai_connection():
    """测试 AI 连接"""
    return await _proxy("POST", "/ai/test")


@router.post("/articles/{article_id}/analyze")
async def analyze_article(article_id: int):
    """AI 分析单篇文章"""
    return await _proxy("POST", f"/articles/{article_id}/analyze")


@router.post("/articles/analyze-all")
async def analyze_all_articles():
    """AI 分析所有文章"""
    return await _proxy("POST", "/articles/analyze-all")


# ===========================================================================
# System 代理
# ===========================================================================

@router.get("/system/stats")
async def get_system_stats():
    """获取系统统计"""
    return await _proxy("GET", "/system/stats")


@router.get("/system/status")
async def get_system_status():
    """获取系统状态"""
    return await _proxy("GET", "/system/status")


# ===========================================================================
# Bridge 路由（知识库桥接）
# ===========================================================================

@router.post("/bridge/ingest-article/{article_id}")
async def bridge_ingest_article(article_id: int):
    """
    导入单篇文章到知识库

    从 RSS 服务获取指定文章内容，写入临时 Markdown 文件后导入知识库。
    """
    client = get_rss_client()
    result = await ingest_article(article_id, client)
    if result.success:
        return {"success": True, "data": result.model_dump()}
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": result.message, "data": result.model_dump()},
    )


@router.post("/bridge/ingest-feed/{feed_id}")
async def bridge_ingest_feed(feed_id: int):
    """
    导入 Feed 下所有文章到知识库

    从 RSS 服务获取指定 Feed 下的文章列表，逐篇导入知识库。
    """
    client = get_rss_client()
    result = await ingest_feed(feed_id, client)
    if result.success:
        return {"success": True, "data": result.model_dump()}
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "部分或全部导入失败", "data": result.model_dump()},
    )


@router.post("/bridge/ingest-all-unread")
async def bridge_ingest_all_unread():
    """
    导入所有未读文章到知识库

    从 RSS 服务获取所有未读文章，逐篇导入知识库。
    """
    client = get_rss_client()
    result = await ingest_all_unread(client)
    if result.success:
        return {"success": True, "data": result.model_dump()}
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "部分或全部导入失败", "data": result.model_dump()},
    )


@router.get("/bridge/status")
async def bridge_status():
    """获取知识库桥接状态"""
    return {"success": True, "data": get_bridge_status()}
