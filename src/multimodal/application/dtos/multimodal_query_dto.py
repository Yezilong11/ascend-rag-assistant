"""
MultimodalQueryDTO - 多模态查询数据传输对象
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class MultimodalQueryDTO:
    """
    多模态查询请求DTO
    """

    query: str
    k: int = 3
    include_images: bool = True
    include_text: bool = True
    document_types: List[str] = field(default_factory=list)
    image_path: Optional[str] = None
    options: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.include_images and not self.include_text:
            self.include_images = True
            self.include_text = True

    @classmethod
    def from_user_query(cls, query: str, **options) -> "MultimodalQueryDTO":
        """从用户查询创建"""
        return cls(query=query, **options)


@dataclass
class ImageSourceDTO:
    """
    图片来源DTO
    """

    chunk_id: str
    image_path: str
    description: str
    ocr_text: str
    source_file: str
    page_number: int
    relevance_score: float = 0.0
    thumbnail_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "image_path": self.image_path,
            "description": self.description,
            "ocr_text": self.ocr_text,
            "source_file": self.source_file,
            "page_number": self.page_number,
            "relevance_score": self.relevance_score,
            "thumbnail_path": self.thumbnail_path,
        }


@dataclass
class TextSourceDTO:
    """
    文本来源DTO
    """

    chunk_id: str
    content: str
    source_file: str
    page_number: int
    relevance_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "content": self.content,
            "source_file": self.source_file,
            "page_number": self.page_number,
            "relevance_score": self.relevance_score,
        }


@dataclass
class MultimodalQueryResultDTO:
    """
    多模态查询结果DTO
    """

    query: str
    answer: str
    text_sources: List[TextSourceDTO] = field(default_factory=list)
    image_sources: List[ImageSourceDTO] = field(default_factory=list)
    total_sources: int = 0
    confidence: float = 0.0
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "answer": self.answer,
            "text_sources": [s.to_dict() for s in self.text_sources],
            "image_sources": [s.to_dict() for s in self.image_sources],
            "total_sources": self.total_sources,
            "confidence": self.confidence,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
        }

    def __post_init__(self):
        self.total_sources = len(self.text_sources) + len(self.image_sources)


@dataclass
class ImageQueryDTO:
    """
    图片问答请求DTO
    """

    image_path: str
    query: str
    options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ImageQueryResultDTO:
    """
    图片问答结果DTO
    """

    image_path: str
    query: str
    answer: str
    detected_text: str = ""
    confidence: float = 0.0
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "image_path": self.image_path,
            "query": self.query,
            "answer": self.answer,
            "detected_text": self.detected_text,
            "confidence": self.confidence,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
        }