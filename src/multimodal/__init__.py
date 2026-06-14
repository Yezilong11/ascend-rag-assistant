"""
多模态RAG模块 - 简化版结构

目录结构:
    entities/          - 实体定义
    value_objects/     - 值对象
    engines/          - 引擎（OCR、VLM）
    repository.py     - 仓储实现
    service.py        - 服务层
    routes.py        - API路由

统一响应格式:
    {
        "success": bool,
        "data": Any,
        "message": str
    }

使用示例:
    from src.multimodal import create_multimodal_service, ImageChunkRepository
"""

from .domain.entities.image_chunk import ImageChunk
from .domain.entities.multimodal_document import MultimodalDocument
from .domain.value_objects.bounding_box import BoundingBox
from .domain.value_objects.device_type import DeviceType, DevicePriority
from .domain.value_objects.processing_status import ProcessingStatus, ProcessingResult

from .engines import EasyOCREngine, QwenVLEngine
from .repository import ImageChunkRepository, ChromaImageChunkRepository
from .service import (
    CombinedProcessingService,
    IndexingServiceWrapper,
    PDFImageExtractor,
    MultimodalIngestService,
    create_multimodal_service,
)

from .routes import router

__version__ = "2.1.0"

__all__ = [
    # 实体
    "ImageChunk",
    "MultimodalDocument",

    # 值对象
    "BoundingBox",
    "DeviceType",
    "DevicePriority",
    "ProcessingStatus",
    "ProcessingResult",

    # 引擎
    "EasyOCREngine",
    "QwenVLEngine",

    # 仓储
    "ImageChunkRepository",
    "ChromaImageChunkRepository",

    # 服务
    "CombinedProcessingService",
    "IndexingServiceWrapper",
    "PDFImageExtractor",
    "MultimodalIngestService",
    "create_multimodal_service",

    # 路由
    "router",
]
