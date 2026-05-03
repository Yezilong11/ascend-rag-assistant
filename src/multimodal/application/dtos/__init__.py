"""
Application Layer DTOs
数据传输对象，隔离领域实体和外部接口
"""

from .image_ingest_dto import ImageIngestDTO, ImageIngestResultDTO, PDFIngestDTO, PDFIngestResultDTO
from .multimodal_query_dto import (
    MultimodalQueryDTO,
    MultimodalQueryResultDTO,
    ImageSourceDTO,
    TextSourceDTO,
    ImageQueryDTO,
    ImageQueryResultDTO,
)

__all__ = [
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
]