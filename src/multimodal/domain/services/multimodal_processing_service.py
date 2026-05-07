"""
MultimodalProcessingService - 多模态处理领域服务
定义核心业务逻辑，不依赖具体技术实现
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple, Optional

from ..entities.image_chunk import ImageChunk
from ..value_objects.processing_status import ProcessingResult


class MultimodalProcessingService(ABC):
    """
    多模态处理领域服务接口
    定义图片处理的核心业务逻辑契约
    """

    @abstractmethod
    def process_image(
        self,
        image_path: str,
        source_file: str = "",
        page_number: int = 0,
        options: Dict[str, Any] = None,
    ) -> ProcessingResult:
        """
        处理单张图片（OCR + VLM描述）
        核心业务流程：
        1. OCR识别文字（CPU）
        2. VLM生成描述（GPU/NPU）
        3. 组合结果生成ImageChunk
        """
        pass

    @abstractmethod
    def process_image_batch(
        self,
        image_paths: List[str],
        source_file: str = "",
        start_page: int = 0,
        options: Dict[str, Any] = None,
    ) -> ProcessingResult:
        """批量处理图片"""
        pass

    @abstractmethod
    def extract_text_from_image(self, image_path: str) -> Tuple[str, List[Dict]]:
        """从图片提取文字（OCR）"""
        pass

    @abstractmethod
    def generate_image_description(
        self,
        image_path: str,
        ocr_text: str = "",
        prompt: str = None,
    ) -> str:
        """生成图片描述（VLM）"""
        pass

    @abstractmethod
    def analyze_image_with_query(
        self,
        image_path: str,
        query: str,
    ) -> str:
        """基于问题分析图片"""
        pass


class ImageIndexingService(ABC):
    """
    图片索引领域服务接口
    定义图片向量化和检索的业务逻辑
    """

    @abstractmethod
    def index_image_chunk(self, chunk: ImageChunk) -> bool:
        """将图片片段添加到索引"""
        pass

    @abstractmethod
    def index_batch(
        self,
        chunks: List[ImageChunk],
    ) -> Tuple[int, int]:
        """批量索引"""
        pass

    @abstractmethod
    def search_similar(
        self,
        query: str,
        k: int = 3,
        document_type: str = None,
    ) -> List[ImageChunk]:
        """检索相似图片"""
        pass

    @abstractmethod
    def delete_from_index(self, chunk_id: str) -> bool:
        """从索引中删除"""
        pass


class PDFImageExtractionService(ABC):
    """
    PDF图片提取领域服务接口
    定义从PDF提取图片的业务逻辑
    """

    @abstractmethod
    def extract_images_from_pdf(
        self,
        pdf_path: str,
        output_dir: str = None,
        min_size: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        从PDF提取所有图片
        Returns:
            [{"page": 1, "image_path": "...", "bbox": [...], "size": (w,h)}, ...]
        """
        pass

    @abstractmethod
    def extract_images_from_page(
        self,
        pdf_path: str,
        page_number: int,
        output_dir: str = None,
    ) -> List[Dict[str, Any]]:
        """从指定页面提取图片"""
        pass