import os
import httpx
import logging
import yaml
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def _get_rss_service_url() -> str:
    """
    从配置文件读取RSS服务地址
    配置路径: config/config.yaml -> server.rss.service_url
    """
    try:
        config_path = os.environ.get("CONFIG_PATH", "./config/config.yaml")
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        rss_config = config.get("server", {}).get("rss", {})
        service_url = rss_config.get("service_url")
        if service_url:
            return service_url
    except Exception as e:
        logger.debug(f"Failed to load RSS service URL from config: {e}")
    return "http://localhost:8081"


class RSSClient:
    def __init__(self, base_url: str = None, timeout: float = 30.0):
        self.base_url = (base_url or _get_rss_service_url()).rstrip("/")
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(self.timeout),
            )
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def health_check(self) -> Dict[str, Any]:
        client = await self._get_client()
        try:
            resp = await client.get("/api/system/status")
            resp.raise_for_status()
            return {"available": True, "data": resp.json()}
        except httpx.HTTPError as e:
            logger.warning(f"RSS service health check failed: {e}")
            return {"available": False, "error": str(e)}

    async def proxy_request(
        self, method: str, path: str, **kwargs
    ) -> httpx.Response:
        client = await self._get_client()
        url = f"/api{path}"
        try:
            resp = await client.request(method, url, **kwargs)
            return resp
        except httpx.ConnectError:
            raise RSSServiceUnavailableError("RSS服务不可用，请确认Go服务已启动")
        except httpx.TimeoutException:
            raise RSSServiceUnavailableError("RSS服务响应超时")


class RSSServiceUnavailableError(Exception):
    pass
