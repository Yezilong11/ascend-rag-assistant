import hashlib
import logging
import re
import threading
from typing import Optional, Dict, Any

from .ai_cache import AICache, content_hash

logger = logging.getLogger(__name__)

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_HTML_ENTITY_RE = re.compile(r"&[a-zA-Z]+;")
_WHITESPACE_RE = re.compile(r"\s+")


def _strip_html(html: str) -> str:
    text = _HTML_TAG_RE.sub("", html)
    text = _HTML_ENTITY_RE.sub(" ", text)
    text = _WHITESPACE_RE.sub(" ", text)
    return text.strip()


def _clean_output(text: str) -> str:
    text = text.strip()
    for stop in ("</s>", "<|endoftext|>", "<|im_end|>"):
        if stop in text:
            text = text[: text.index(stop)]
    lines = text.split("\n")
    cleaned = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line in ("摘要：", "关键词：", "情感："):
            continue
        cleaned.append(line)
    return "\n".join(cleaned).strip()


class RSSAIService:

    def __init__(self):
        self._lock = threading.Lock()
        self._cache = AICache()

    def _get_assistant(self):
        from src.rag_api.dependencies import get_rag_assistant
        assistant = get_rag_assistant()
        if assistant is None:
            raise RuntimeError("RAG引擎未加载，请先在智能问答页面加载模型")
        return assistant

    def _run_inference(self, prompt: str, max_new_tokens: int = 256) -> str:
        assistant = self._get_assistant()
        with self._lock:
            result = assistant.pipeline_obj(
                prompt, max_new_tokens=max_new_tokens, do_sample=True, temperature=0.7, top_p=0.9
            )
        generated = result[0]["generated_text"]
        return generated[len(prompt):].strip()

    def generate_summary(self, content: str) -> str:
        truncated = content[:2000]
        prompt = f"请为以下文章生成一个简洁的中文摘要（100字以内）：\n\n{truncated}\n\n摘要："
        raw = self._run_inference(prompt, max_new_tokens=200)
        return _clean_output(raw)

    def extract_keywords(self, content: str) -> str:
        truncated = content[:2000]
        prompt = f"请从以下文章中提取5个关键词，用逗号分隔：\n\n{truncated}\n\n关键词："
        raw = self._run_inference(prompt, max_new_tokens=100)
        cleaned = _clean_output(raw)
        if "\n" in cleaned:
            cleaned = cleaned.split("\n")[0]
        return cleaned

    def analyze_sentiment(self, content: str) -> str:
        truncated = content[:2000]
        prompt = f"请分析以下文章的情感倾向，只能回答：正面、中性或负面\n\n{truncated}\n\n情感："
        raw = self._run_inference(prompt, max_new_tokens=20)
        cleaned = _clean_output(raw).lower()
        if "正面" in cleaned:
            return "正面"
        if "负面" in cleaned:
            return "负面"
        return "中性"

    async def analyze_article(self, article_id: int, client) -> dict:
        try:
            resp = await client.proxy_request("GET", f"/articles/{article_id}")
            if resp.status_code != 200:
                logger.error("获取文章 %d 失败: HTTP %d", article_id, resp.status_code)
                return {"summary": "", "keywords": "", "sentiment": ""}
        except Exception as e:
            logger.error("获取文章 %d 失败: %s", article_id, e)
            return {"summary": "", "keywords": "", "sentiment": ""}

        article = resp.json()
        raw_content = article.get("content", "") or article.get("description", "")
        if not raw_content:
            return {"summary": "", "keywords": "", "sentiment": ""}

        content = _strip_html(raw_content)
        if not content:
            return {"summary": "", "keywords": "", "sentiment": ""}

        c_hash = content_hash(content)
        cached = self._cache.get(c_hash)
        if cached:
            return cached

        summary = self.generate_summary(content)
        keywords = ""
        sentiment = ""
        try:
            keywords = self.extract_keywords(content)
        except Exception as e:
            logger.warning("提取关键词失败: %s", e)
        try:
            sentiment = self.analyze_sentiment(content)
        except Exception as e:
            logger.warning("情感分析失败: %s", e)

        result = {"summary": summary, "keywords": keywords, "sentiment": sentiment}
        self._cache.set(c_hash, result)
        return result

    async def analyze_all_articles(self, client) -> dict:
        resp = await client.proxy_request("GET", "/articles")
        data = resp.json()
        articles = data.get("data", []) if isinstance(data, dict) else data
        count = len(articles)

        def _background():
            import asyncio
            from .client import RSSClient
            bg_client = RSSClient(base_url=client.base_url, timeout=client.timeout)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                for article in articles:
                    article_id = article.get("id")
                    if not article_id:
                        continue
                    try:
                        loop.run_until_complete(
                            self.analyze_article(article_id, bg_client)
                        )
                    except Exception as e:
                        logger.error("分析文章 %d 失败: %s", article_id, e)
            finally:
                loop.run_until_complete(bg_client.close())
                loop.close()

        thread = threading.Thread(target=_background, daemon=True)
        thread.start()
        return {"message": "analysis started", "count": count}

    def test_availability(self) -> dict:
        from src.rag_api.dependencies import get_rag_assistant
        from src.rag_engine import PREDEFINED_MODELS
        assistant = get_rag_assistant()
        if assistant is None:
            return {"available": False, "model_key": "", "model_name": ""}
        model_info = PREDEFINED_MODELS.get(assistant.model_key, {})
        return {
            "available": True,
            "model_key": assistant.model_key,
            "model_name": model_info.get("name", ""),
        }

    def get_config(self) -> dict:
        from src.rag_api.dependencies import get_rag_assistant
        from src.rag_engine import PREDEFINED_MODELS
        assistant = get_rag_assistant()
        engine_loaded = assistant is not None
        model_key = assistant.model_key if engine_loaded else ""
        model_name = (
            PREDEFINED_MODELS.get(model_key, {}).get("name", "") if model_key else ""
        )
        return {
            "model_key": model_key,
            "model_name": model_name,
            "engine_loaded": engine_loaded,
            "available_models": PREDEFINED_MODELS,
        }
