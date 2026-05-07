"""
ImageChunkRepository - 图片片段仓储接口
定义图片片段的持久化操作契约
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from ..entities.image_chunk import ImageChunk


class ImageChunkRepository(ABC):
    """
    图片片段仓储接口
    定义领域实体的持久化契约，由基础设施层实现
    """

    @abstractmethod
    def save(self, chunk: ImageChunk) -> ImageChunk:
        """保存单个图片片段"""
        pass

    @abstractmethod
    def save_batch(self, chunks: List[ImageChunk]) -> List[ImageChunk]:
        """批量保存图片片段"""
        pass

    @abstractmethod
    def find_by_id(self, chunk_id: str) -> Optional[ImageChunk]:
        """根据ID查找图片片段"""
        pass

    @abstractmethod
    def find_by_source(self, source_file: str) -> List[ImageChunk]:
        """根据源文件查找所有图片片段"""
        pass

    @abstractmethod
    def find_by_document_type(self, document_type: str) -> List[ImageChunk]:
        """根据文档类型查找图片片段"""
        pass

    @abstractmethod
    def similarity_search(
        self,
        query: str,
        k: int = 3,
        filter_criteria: Dict[str, Any] = None,
    ) -> List[ImageChunk]:
        """相似度检索"""
        pass

    @abstractmethod
    def update_status(self, chunk_id: str, status) -> bool:
        """更新片段处理状态"""
        pass

    @abstractmethod
    def delete(self, chunk_id: str) -> bool:
        """删除图片片段"""
        pass

    @abstractmethod
    def delete_by_source(self, source_file: str) -> int:
        """删除指定源文件的所有片段"""
        pass

    @abstractmethod
    def count(self) -> int:
        """获取片段总数"""
        pass

    @abstractmethod
    def exists(self, chunk_id: str) -> bool:
        """检查片段是否存在"""
        pass