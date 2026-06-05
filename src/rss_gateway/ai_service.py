import hashlib
import logging
import re
import threading
import time
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
        self._semaphore = threading.Semaphore(2)  # Allow 2 concurrent inference requests
        self._cache = AICache()
        self._config: Dict[str, Any] = {
            "max_new_tokens": 256,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True,
        }

    def _get_assistant(self):
        from src.rag_api.dependencies import get_rag_assistant
        assistant = get_rag_assistant()
        if assistant is None:
            raise RuntimeError("RAG引擎未加载，请先在智能问答页面加载模型")
        return assistant

    def _run_inference(self, prompt: str, max_new_tokens: int = 256, timeout: float = 120.0) -> str:
        assistant = self._get_assistant()
        with self._semaphore:
            start = time.monotonic()
            result = assistant.pipeline_obj(
                prompt,
                max_new_tokens=max_new_tokens,
                do_sample=self._config.get("do_sample", True),
                temperature=self._config.get("temperature", 0.7),
                top_p=self._config.get("top_p", 0.9),
            )
            elapsed = time.monotonic() - start
            if elapsed > timeout:
                logger.warning(
                    "推理耗时 %.1fs 超过阈值 %.1fs，prompt 长度=%d",
                    elapsed, timeout, len(prompt),
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
            "inference_config": dict(self._config),
        }

    def update_config(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """更新推理配置参数，仅覆盖已提供的字段"""
        allowed_keys = {"max_new_tokens", "temperature", "top_p", "do_sample"}
        for key, value in updates.items():
            if key in allowed_keys and value is not None:
                self._config[key] = value
                logger.info("AI 配置更新: %s = %s", key, value)
        return dict(self._config)
