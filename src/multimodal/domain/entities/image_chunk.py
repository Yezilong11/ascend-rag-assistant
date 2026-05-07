"""
ImageChunk - 图片片段实体
图片经过OCR+VLM处理后生成的文档片段
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..value_objects.bounding_box import BoundingBox
from ..value_objects.processing_status import ProcessingStatus


@dataclass
class ImageChunk:
    """
    图片片段 - 领域实体
    代表一张图片经过处理后生成的向量化文档单元

    Attributes:
        id: 唯一标识符
        page_content: VLM生成的图片描述文本（用于向量化）
        image_path: 图片存储路径
        ocr_text: OCR提取的原始文字
        page_number: 来源页码（PDF来源时有效）
        bounding_box: 图片在文档中的位置
        source_file: 原始文件路径
        document_type: 文档类型
        processing_status: 处理状态
        embedding_vector: 嵌入向量（存储时生成）
        metadata: 扩展元数据
        created_at: 创建时间
        updated_at: 更新时间
    """

    id: str
    page_content: str
    image_path: str
    ocr_text: str = ""
    page_number: int = 0
    bounding_box: Optional[BoundingBox] = None
    source_file: str = ""
    document_type: str = "unknown"
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    embedding_vector: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def is_processed(self) -> bool:
        """检查是否已完成处理"""
        return self.processing_status == ProcessingStatus.COMPLETED

    def is_failed(self) -> bool:
        """检查是否处理失败"""
        return self.processing_status == ProcessingStatus.FAILED

    def mark_completed(self) -> None:
        """标记为已完成"""
        self.processing_status = ProcessingStatus.COMPLETED
        self.updated_at = datetime.now()

    def mark_failed(self, error_message: str = "") -> None:
        """标记为失败"""
        self.processing_status = ProcessingStatus.FAILED
        self.metadata["error_message"] = error_message
        self.updated_at = datetime.now()

    def get_searchable_text(self) -> str:
        """获取可搜索文本（组合OCR和VLM描述）"""
        parts = []
        if self.ocr_text:
            parts.append(f"OCR文字: {self.ocr_text}")
        if self.page_content:
            parts.append(f"图片描述: {self.page_content}")
        return "\n".join(parts) if parts else self.page_content

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "id": self.id,
            "page_content": self.page_content,
            "image_path": self.image_path,
            "ocr_text": self.ocr_text,
            "page_number": self.page_number,
            "bounding_box": self.bounding_box.to_dict() if self.bounding_box else None,
            "source_file": self.source_file,
            "document_type": self.document_type,
            "processing_status": self.processing_status.value,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ImageChunk":
        """从字典反序列化"""
        bbox_data = data.get("bounding_box")
        bbox = BoundingBox.from_dict(bbox_data) if bbox_data else None

        return cls(
            id=data["id"],
            page_content=data["page_content"],
            image_path=data["image_path"],
            ocr_text=data.get("ocr_text", ""),
            page_number=data.get("page_number", 0),
            bounding_box=bbox,
            source_file=data.get("source_file", ""),
            document_type=data.get("document_type", "unknown"),
            processing_status=ProcessingStatus(data.get("processing_status", "pending")),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.now(),
        )