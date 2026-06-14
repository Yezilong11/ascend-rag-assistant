"""
测试多模态模块

使用 pytest 运行：
    pytest tests/test_multimodal.py -v
"""

import os
import pytest
from unittest.mock import MagicMock, patch


class TestImageChunkRepository:
    """ImageChunkRepository 测试类"""

    def test_init(self, temp_dir):
        """测试仓储初始化"""
        from src.multimodal.repository import ImageChunkRepository

        persist_dir = os.path.join(temp_dir, "multimodal_db")
        repo = ImageChunkRepository(persist_dir=persist_dir)

        assert repo is not None
        assert repo._persist_dir == persist_dir

    def test_count_empty(self, temp_dir):
        """测试空数据库计数"""
        from src.multimodal.repository import ImageChunkRepository

        persist_dir = os.path.join(temp_dir, "multimodal_db")
        repo = ImageChunkRepository(persist_dir=persist_dir)

        count = repo.count()
        assert count == 0

    def test_exists(self, temp_dir):
        """测试存在性检查"""
        from src.multimodal.repository import ImageChunkRepository

        persist_dir = os.path.join(temp_dir, "multimodal_db")
        repo = ImageChunkRepository(persist_dir=persist_dir)

        # 不存在的 ID
        assert repo.exists("non-existent-id") is False


class TestProcessingStatus:
    """处理状态测试类"""

    def test_processing_status_values(self):
        """测试处理状态枚举值"""
        from src.multimodal.domain.value_objects.processing_status import ProcessingStatus

        assert ProcessingStatus.PENDING.value == "pending"
        assert ProcessingStatus.PROCESSING.value == "processing"
        assert ProcessingStatus.COMPLETED.value == "completed"
        assert ProcessingStatus.FAILED.value == "failed"

    def test_processing_result_creation(self):
        """测试处理结果创建"""
        from src.multimodal.domain.value_objects.processing_status import ProcessingResult

        # 成功结果
        result = ProcessingResult.success(
            message="处理成功",
            data={"key": "value"},
            duration_ms=100.0
        )
        assert result.is_success is True
        assert result.error is None

        # 失败结果
        result = ProcessingResult.failure(
            message="处理失败",
            error="具体错误",
            duration_ms=50.0
        )
        assert result.is_success is False
        assert result.error == "具体错误"


class TestBoundingBox:
    """边界框测试类"""

    def test_bounding_box_creation(self):
        """测试边界框创建"""
        from src.multimodal.domain.value_objects.bounding_box import BoundingBox

        bbox = BoundingBox(x1=10, y1=20, x2=100, y2=200)
        assert bbox.x1 == 10
        assert bbox.y1 == 20
        assert bbox.x2 == 100
        assert bbox.y2 == 200

    def test_bounding_box_to_list(self):
        """测试边界框转换列表"""
        from src.multimodal.domain.value_objects.bounding_box import BoundingBox

        bbox = BoundingBox(x1=10, y1=20, x2=100, y2=200)
        bbox_list = bbox.to_list()

        assert bbox_list == [10, 20, 100, 200]

    def test_bounding_box_from_list(self):
        """测试从列表创建边界框"""
        from src.multimodal.domain.value_objects.bounding_box import BoundingBox

        bbox = BoundingBox.from_list([10, 20, 100, 200])
        assert bbox.x1 == 10
        assert bbox.y1 == 20
        assert bbox.x2 == 100
        assert bbox.y2 == 200


class TestImageChunk:
    """图片片段测试类"""

    def test_image_chunk_creation(self):
        """测试图片片段创建"""
        from src.multimodal.domain.entities.image_chunk import ImageChunk

        chunk = ImageChunk(
            id="test-id-123",
            page_content="测试内容",
            image_path="/path/to/image.png",
            ocr_text="识别的文字",
            source_file="source.png",
            document_type="test"
        )

        assert chunk.id == "test-id-123"
        assert chunk.page_content == "测试内容"
        assert chunk.image_path == "/path/to/image.png"

    def test_image_chunk_status(self):
        """测试片段状态标记"""
        from src.multimodal.domain.entities.image_chunk import ImageChunk
        from src.multimodal.domain.value_objects.processing_status import ProcessingStatus

        chunk = ImageChunk(
            id="test-id",
            page_content="测试",
            image_path="/path/to/image.png"
        )

        # 初始状态
        assert chunk.processing_status == ProcessingStatus.PENDING

        # 标记完成
        chunk.mark_completed()
        assert chunk.processing_status == ProcessingStatus.COMPLETED

        # 标记失败
        chunk.mark_failed()
        assert chunk.processing_status == ProcessingStatus.FAILED

    def test_image_chunk_get_searchable_text(self):
        """测试可搜索文本生成"""
        from src.multimodal.domain.entities.image_chunk import ImageChunk

        chunk = ImageChunk(
            id="test-id",
            page_content="图片描述：测试图片",
            image_path="/path/to/image.png",
            ocr_text="识别的文字内容"
        )

        text = chunk.get_searchable_text()
        assert "测试图片" in text
        assert "识别的文字内容" in text


class TestEngines:
    """引擎测试类"""

    def test_ocr_engine_init(self):
        """测试OCR引擎初始化"""
        from src.multimodal.engines import EasyOCREngine

        ocr = EasyOCREngine()
        assert ocr is not None
        assert hasattr(ocr, '_initialized')
        assert ocr._initialized is False

    def test_vlm_engine_init(self):
        """测试VLM引擎初始化"""
        from src.multimodal.engines import QwenVLEngine

        # 初始化时不加载模型
        vlm = QwenVLEngine(vlm_enabled=False)
        assert vlm is not None
        assert vlm._vlm_enabled is False


class TestCombinedProcessingService:
    """组合处理服务测试类"""

    def test_service_creation(self):
        """测试服务创建"""
        from src.multimodal.service import CombinedProcessingService
        from src.multimodal.engines import EasyOCREngine, QwenVLEngine

        ocr_engine = EasyOCREngine()
        vlm_engine = QwenVLEngine(vlm_enabled=False)

        service = CombinedProcessingService(ocr_engine, vlm_engine)

        assert service is not None
        assert service._ocr == ocr_engine
        assert service._vlm == vlm_engine
