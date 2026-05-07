"""
ImageIngestDTO - 图片导入数据传输对象
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class ImageIngestDTO:
    """
    图片导入请求DTO
    """

    image_paths: List[str] = field(default_factory=list)
    source_file: str = ""
    document_type: str = "unknown"
    page_start: int = 0
    options: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.image_paths, str):
            self.image_paths = [self.image_paths]

    @classmethod
    def from_single_image(
        cls,
        image_path: str,
        source_file: str = "",
        document_type: str = "unknown",
        **options,
    ) -> "ImageIngestDTO":
        """从单张图片创建"""
        return cls(
            image_paths=[image_path],
            source_file=source_file,
            document_type=document_type,
            options=options,
        )

    @classmethod
    def from_pdf(
        cls,
        pdf_path: str,
        document_type: str = "unknown",
        extract_images: bool = True,
    ) -> "ImageIngestDTO":
        """从PDF创建（触发图片提取）"""
        return cls(
            image_paths=[pdf_path],
            source_file=pdf_path,
            document_type=document_type,
            options={"extract_images": extract_images},
        )


@dataclass
class ImageIngestResultDTO:
    """
    图片导入结果DTO
    """

    success: bool
    total_count: int = 0
    success_count: int = 0
    failed_count: int = 0
    image_chunks: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "total_count": self.total_count,
            "success_count": self.success_count,
            "failed_count": self.failed_count,
            "image_chunks": self.image_chunks,
            "errors": self.errors,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
        }

    @property
    def is_partial_success(self) -> bool:
        return self.success_count > 0 and self.failed_count > 0

    @property
    def is_full_success(self) -> bool:
        return self.failed_count == 0 and self.success_count > 0


@dataclass
class PDFIngestDTO:
    """
    PDF导入请求DTO
    """

    pdf_path: str
    document_type: str = "unknown"
    extract_images: bool = True
    min_image_size: int = 100
    output_dir: Optional[str] = None

    def to_image_ingest_dto(self) -> ImageIngestDTO:
        """转换为图片导入DTO"""
        return ImageIngestDTO.from_pdf(
            pdf_path=self.pdf_path,
            document_type=self.document_type,
            extract_images=self.extract_images,
        )


@dataclass
class PDFIngestResultDTO:
    """
    PDF导入结果DTO
    """

    success: bool
    pdf_path: str
    text_chunks_count: int = 0
    image_chunks_count: int = 0
    extracted_images_count: int = 0
    errors: List[str] = field(default_factory=list)
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "pdf_path": self.pdf_path,
            "text_chunks_count": self.text_chunks_count,
            "image_chunks_count": self.image_chunks_count,
            "extracted_images_count": self.extracted_images_count,
            "errors": self.errors,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
        }