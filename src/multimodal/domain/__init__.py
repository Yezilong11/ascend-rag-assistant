"""
多模态RAG模块 - 领域层(Domain)
Domain Layer - 包含核心业务实体、值对象、领域服务和仓储接口
"""

from .entities.image_chunk import ImageChunk
from .entities.multimodal_document import MultimodalDocument
from .value_objects.bounding_box import BoundingBox
from .value_objects.device_type import DeviceType, DevicePriority
from .value_objects.processing_status import ProcessingStatus, ProcessingResult
from .repositories.image_chunk_repository import ImageChunkRepository

__all__ = [
    "ImageChunk",
    "MultimodalDocument",
    "BoundingBox",
    "DeviceType",
    "DevicePriority",
    "ProcessingStatus",
    "ProcessingResult",
    "ImageChunkRepository",
]