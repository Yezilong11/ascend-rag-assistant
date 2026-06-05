from pydantic import BaseModel, Field
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


class AIConfigUpdate(BaseModel):
    """AI 推理配置更新模型"""
    max_new_tokens: Optional[int] = Field(None, ge=1, le=2048, description="最大生成 token 数")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="采样温度")
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0, description="Top-p 采样参数")
    do_sample: Optional[bool] = Field(None, description="是否启用采样")


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
