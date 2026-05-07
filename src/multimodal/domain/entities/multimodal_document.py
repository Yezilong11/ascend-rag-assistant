"""
MultimodalDocument - 多模态文档聚合根
管理文本片段和图片片段的聚合实体
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

try:
    from langchain_core.documents import Document
except ImportError:
    from langchain.schema import Document

from .image_chunk import ImageChunk


@dataclass
class MultimodalDocument:
    """
    多模态文档 - 聚合根(Aggregate Root)
    统一管理文本片段和图片片段的完整文档

    Attributes:
        id: 唯一标识符
        source_path: 原始文件路径
        document_type: 文档类型（registration/tech_doc/rules等）
        text_chunks: 文本片段列表
        image_chunks: 图片片段列表
        metadata: 文档级元数据
        created_at: 创建时间
        updated_at: 更新时间
    """

    id: str
    source_path: str
    document_type: str = "unknown"
    text_chunks: List[Document] = field(default_factory=list)
    image_chunks: List[ImageChunk] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def add_text_chunk(self, chunk: Document) -> None:
        """添加文本片段"""
        self.text_chunks.append(chunk)
        self.updated_at = datetime.now()

    def add_image_chunk(self, chunk: ImageChunk) -> None:
        """添加图片片段"""
        self.image_chunks.append(chunk)
        self.updated_at = datetime.now()

    def get_all_chunks(self) -> List:
        """获取所有片段（文本+图片）"""
        return list(self.text_chunks) + list(self.image_chunks)

    def get_processed_image_count(self) -> int:
        """获取已处理的图片数量"""
        return sum(1 for chunk in self.image_chunks if chunk.is_processed())

    def get_failed_image_count(self) -> int:
        """获取处理失败的图片数量"""
        return sum(1 for chunk in self.image_chunks if chunk.is_failed())

    def is_fully_processed(self) -> bool:
        """检查是否所有图片都已处理完成"""
        if not self.image_chunks:
            return True
        return all(chunk.is_processed() for chunk in self.image_chunks)

    def get_processing_summary(self) -> Dict[str, Any]:
        """获取处理摘要"""
        return {
            "total_images": len(self.image_chunks),
            "processed_images": self.get_processed_image_count(),
            "failed_images": self.get_failed_image_count(),
            "pending_images": len(self.image_chunks) - self.get_processed_image_count() - self.get_failed_image_count(),
            "text_chunks": len(self.text_chunks),
            "is_complete": self.is_fully_processed(),
        }

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "id": self.id,
            "source_path": self.source_path,
            "document_type": self.document_type,
            "text_chunks_count": len(self.text_chunks),
            "image_chunks": [chunk.to_dict() for chunk in self.image_chunks],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_source(
        cls,
        source_path: str,
        document_type: str = "unknown",
        text_chunks: Optional[List[Document]] = None,
    ) -> "MultimodalDocument":
        """从源文件创建多模态文档"""
        import uuid
        return cls(
            id=str(uuid.uuid4()),
            source_path=source_path,
            document_type=document_type,
            text_chunks=text_chunks or [],
        )