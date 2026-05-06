"""
多模态RAG模块
"""

from .domain import (
    ImageChunk,
    MultimodalDocument,
    BoundingBox,
    DeviceType,
    DevicePriority,
    ProcessingStatus,
    ProcessingResult,
    ImageChunkRepository,
)

from .application import (
    MultimodalIngestService,
    MultimodalIngestServiceImpl,
    MultimodalQueryService,
    MultimodalQueryServiceImpl,
    ImageIngestDTO,
    ImageIngestResultDTO,
    PDFIngestDTO,
    PDFIngestResultDTO,
    MultimodalQueryDTO,
    MultimodalQueryResultDTO,
    ImageSourceDTO,
    TextSourceDTO,
    ImageQueryDTO,
    ImageQueryResultDTO,
)

from .infrastructure import (
    DeviceManager,
    EasyOCREngine,
    QwenVLEngine,
    PDFImageExtractor,
    ChromaImageChunkRepository,
)

from .interface import (
    router,
    render_multimodal_sidebar,
    render_image_sources,
)

__version__ = "1.1.0"

__all__ = [
    "ImageChunk",
    "MultimodalDocument",
    "BoundingBox",
    "DeviceType",
    "DevicePriority",
    "ProcessingStatus",
    "ProcessingResult",
    "ImageChunkRepository",
    "MultimodalIngestService",
    "MultimodalIngestServiceImpl",
    "MultimodalQueryService",
    "MultimodalQueryServiceImpl",
    "ImageIngestDTO",
    "ImageIngestResultDTO",
    "PDFIngestDTO",
    "PDFIngestResultDTO",
    "MultimodalQueryDTO",
    "MultimodalQueryResultDTO",
    "ImageSourceDTO",
    "TextSourceDTO",
    "ImageQueryDTO",
    "ImageQueryResultDTO",
    "DeviceManager",
    "EasyOCREngine",
    "QwenVLEngine",
    "PDFImageExtractor",
    "ChromaImageChunkRepository",
    "router",
    "render_multimodal_sidebar",
    "render_image_sources",
]