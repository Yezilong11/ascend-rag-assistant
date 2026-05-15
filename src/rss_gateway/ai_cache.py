import hashlib
import json
import logging
import os
import threading
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class AICache:
    def __init__(self, cache_path: str = "data/rss_ai_cache.json"):
        self._cache_path = cache_path
        self._lock = threading.Lock()
        self._cache: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        if not os.path.exists(self._cache_path):
            return {}
        try:
            with open(self._cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    logger.warning("缓存文件格式异常，预期为字典，重置为空缓存")
                    return {}
                return data
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("缓存文件加载失败，将使用空缓存: %s", e)
            return {}

    def _save(self) -> None:
        try:
            os.makedirs(os.path.dirname(self._cache_path), exist_ok=True)
            with open(self._cache_path, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, ensure_ascii=False, indent=2)
        except OSError as e:
            logger.error("缓存文件保存失败: %s", e)

    def get(self, content_hash: str) -> Optional[dict]:
        with self._lock:
            return self._cache.get(content_hash)

    def set(self, content_hash: str, result: dict) -> None:
        with self._lock:
            self._cache[content_hash] = result
            self._save()
