from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class RSSFeedCreate(BaseModel):
    name: str
    url: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    crawl_interval: int = 60


class RSSFeedUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    crawl_interval: Optional[int] = None


class RSSCategoryCreate(BaseModel):
    name: str
    icon: Optional[str] = None
    sort_order: int = 0


class RSSTagCreate(BaseModel):
    name: str
    color: Optional[str] = None


class BridgeIngestResult(BaseModel):
    success: bool
    message: str
    article_id: Optional[int] = None
    chunks_count: int = 0


class BridgeBatchResult(BaseModel):
    success: bool
    total: int
    success_count: int
    failed_count: int
    errors: List[str] = []
