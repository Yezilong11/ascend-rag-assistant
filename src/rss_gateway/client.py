import httpx
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class RSSClient:
    def __init__(self, base_url: str = "http://localhost:8081", timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
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
