import logging
import tempfile
import os
from typing import Dict, List, Any

from .client import RSSClient
from .models import BridgeIngestResult, BridgeBatchResult

logger = logging.getLogger(__name__)

_bridge_status = {
    "last_ingest_time": None,
    "total_ingested": 0,
    "last_error": None,
}


async def ingest_article(article_id: int, client: RSSClient) -> BridgeIngestResult:
    try:
        resp = await client.proxy_request("GET", f"/articles/{article_id}")
        if resp.status_code != 200:
            return BridgeIngestResult(
                success=False,
                message=f"获取文章失败: HTTP {resp.status_code}",
                article_id=article_id,
            )
        article = resp.json()
        content = article.get("content", "")
        title = article.get("title", "")
        if not content:
            content = article.get("description", "")
        if not content:
            return BridgeIngestResult(
                success=False,
                message="文章内容为空",
                article_id=article_id,
            )

        from src.rag_api.dependencies import get_knowledge_base
        kb = get_knowledge_base()
        if kb is None:
            return BridgeIngestResult(
                success=False,
                message="知识库未初始化",
                article_id=article_id,
            )

        temp_fd, temp_path = tempfile.mkstemp(suffix=".md")
        try:
            with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
                f.write(f"# {title}\n\n{content}")
            success = kb.ingest(temp_path, doc_type="rss_article", display_source=f"RSS: {title}")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

        if success:
            _bridge_status["total_ingested"] += 1
            return BridgeIngestResult(
                success=True,
                message="导入成功",
                article_id=article_id,
                chunks_count=1,
            )
        else:
            return BridgeIngestResult(
                success=False,
                message="知识库导入失败",
                article_id=article_id,
            )
    except Exception as e:
        logger.error(f"Bridge ingest article {article_id} failed: {e}")
        return BridgeIngestResult(
            success=False,
            message=str(e),
            article_id=article_id,
        )


async def ingest_feed(feed_id: int, client: RSSClient) -> BridgeBatchResult:
    try:
        resp = await client.proxy_request("GET", "/articles", params={"feed_id": feed_id, "limit": 100})
        if resp.status_code != 200:
            return BridgeBatchResult(
                success=False,
                total=0,
                success_count=0,
                failed_count=0,
                errors=[f"获取文章列表失败: HTTP {resp.status_code}"],
            )
        data = resp.json()
        articles = data.get("data", []) if isinstance(data, dict) else data
        total = len(articles)
        success_count = 0
        failed_count = 0
        errors = []
        for article in articles:
            result = await ingest_article(article.get("id", 0), client)
            if result.success:
                success_count += 1
            else:
                failed_count += 1
                errors.append(f"Article {article.get('id')}: {result.message}")
        return BridgeBatchResult(
            success=True,
            total=total,
            success_count=success_count,
            failed_count=failed_count,
            errors=errors,
        )
    except Exception as e:
        return BridgeBatchResult(
            success=False,
            total=0,
            success_count=0,
            failed_count=0,
            errors=[str(e)],
        )


async def ingest_all_unread(client: RSSClient) -> BridgeBatchResult:
    try:
        resp = await client.proxy_request("GET", "/articles", params={"read_status": 0, "limit": 100})
        if resp.status_code != 200:
            return BridgeBatchResult(
                success=False,
                total=0,
                success_count=0,
                failed_count=0,
                errors=[f"获取未读文章失败: HTTP {resp.status_code}"],
            )
        data = resp.json()
        articles = data.get("data", []) if isinstance(data, dict) else data
        total = len(articles)
        success_count = 0
        failed_count = 0
        errors = []
        for article in articles:
            result = await ingest_article(article.get("id", 0), client)
            if result.success:
                success_count += 1
            else:
                failed_count += 1
                errors.append(f"Article {article.get('id')}: {result.message}")
        return BridgeBatchResult(
            success=True,
            total=total,
            success_count=success_count,
            failed_count=failed_count,
            errors=errors,
        )
    except Exception as e:
        return BridgeBatchResult(
            success=False,
            total=0,
            success_count=0,
            failed_count=0,
            errors=[str(e)],
        )


def get_bridge_status() -> Dict[str, Any]:
    return _bridge_status.copy()
