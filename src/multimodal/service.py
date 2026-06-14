"""
多模态服务 - 合并应用服务和处理服务
提供图片导入、PDF处理、图片检索等核心功能
"""

from typing import List, Dict, Any, Optional, Tuple
import time
import uuid
import os

from .domain.entities.image_chunk import ImageChunk
from .domain.value_objects.processing_status import ProcessingStatus, ProcessingResult
from .engines.ocr_engine import EasyOCREngine
from .engines.vlm_engine import QwenVLEngine
from .repository import ImageChunkRepository


class CombinedProcessingService:
    """组合OCR+VLM处理服务"""

    def __init__(self, ocr_engine: EasyOCREngine, vlm_engine: QwenVLEngine):
        self._ocr = ocr_engine
        self._vlm = vlm_engine

    def process_image(
        self,
        image_path: str,
        source_file: str = "",
        page_number: int = 0,
        options: Dict[str, Any] = None,
    ) -> ProcessingResult:
        """处理单张图片（OCR + VLM描述）"""
        start_time = time.time()

        try:
            ocr_text, _ = self._ocr.extract_text_from_image(image_path)
            vlm_description = None

            try:
                vlm_description = self._vlm.generate_image_description(
                    image_path=image_path,
                    ocr_text=ocr_text,
                )
            except Exception as e:
                print(f"⚠️ VLM不可用，使用OCR文字作为描述: {e}")
                vlm_description = None

            if not vlm_description:
                vlm_description = f"图片包含文字: {ocr_text}" if ocr_text else "图片内容（无文字）"

            chunk = ImageChunk(
                id=str(uuid.uuid4()),
                page_content=vlm_description,
                image_path=image_path,
                ocr_text=ocr_text,
                page_number=page_number,
                source_file=source_file,
                document_type=options.get("document_type", "unknown") if options else "unknown",
            )
            chunk.mark_completed()

            return ProcessingResult.success(
                message="图片处理完成",
                data=chunk,
                duration_ms=(time.time() - start_time) * 1000,
            )

        except Exception as e:
            return ProcessingResult.failure(
                message=f"处理失败: {str(e)}",
                error=str(e),
                duration_ms=(time.time() - start_time) * 1000,
            )

    def process_image_batch(
        self,
        image_paths: List[str],
        source_file: str = "",
        start_page: int = 0,
        options: Dict[str, Any] = None,
    ) -> ProcessingResult:
        """批量处理图片"""
        results = []
        failed_count = 0
        for idx, path in enumerate(image_paths):
            result = self.process_image(path, source_file, start_page + idx, options)
            if result.is_success:
                results.append(result.data)
            else:
                failed_count += 1

        return ProcessingResult.partial(
            message=f"批量处理完成",
            data=results,
            success_count=len(results),
            failed_count=failed_count,
        )

    def extract_text_from_image(self, image_path: str) -> Tuple[str, List[Dict]]:
        """从图片提取文字"""
        return self._ocr.extract_text_from_image(image_path)

    def generate_image_description(self, image_path: str, ocr_text: str = "", prompt: str = None):
        """生成图片描述"""
        try:
            return self._vlm.generate_image_description(image_path, ocr_text, prompt)
        except Exception:
            return f"图片包含文字: {ocr_text}" if ocr_text else "图片内容"

    def analyze_image_with_query(self, image_path: str, query: str):
        """基于问题分析图片"""
        try:
            return self._vlm.analyze_image_with_query(image_path, query)
        except Exception:
            return "VLM不可用，无法分析图片"


class IndexingServiceWrapper:
    """将ImageChunkRepository适配为索引服务接口"""

    def __init__(self, repository: ImageChunkRepository):
        if not hasattr(repository, 'save'):
            raise ValueError(f"Repository {type(repository)} must have 'save' method")
        self._repo = repository

    def index_image_chunk(self, chunk: ImageChunk):
        """索引单个图片片段"""
        return self._repo.save(chunk)

    def index_batch(self, chunks: List[ImageChunk]):
        """批量索引"""
        self._repo.save_batch(chunks)
        return len(chunks), 0

    def search_similar(self, query: str, k: int = 3, document_type: str = None):
        """相似检索"""
        return self._repo.similarity_search(query, k)

    def delete_from_index(self, chunk_id: str):
        """从索引中删除"""
        return self._repo.delete(chunk_id)


class PDFImageExtractor:
    """PDF图片提取器"""

    def __init__(self):
        pass

    def extract_images_from_pdf(
        self,
        pdf_path: str,
        output_dir: str = None,
        min_size: int = 100,
    ) -> List[Dict[str, Any]]:
        """从PDF提取所有图片"""
        # 延迟导入以避免循环依赖
        from .infrastructure.pdf.pdf_image_extractor import PDFImageExtractor as OriginalExtractor
        extractor = OriginalExtractor()
        return extractor.extract_images_from_pdf(pdf_path, output_dir, min_size)

    def extract_images_from_page(
        self,
        pdf_path: str,
        page_number: int,
        output_dir: str = None,
    ) -> List[Dict[str, Any]]:
        """从指定页面提取图片"""
        from .infrastructure.pdf.pdf_image_extractor import PDFImageExtractor as OriginalExtractor
        extractor = OriginalExtractor()
        return extractor.extract_images_from_page(pdf_path, page_number, output_dir)


class MultimodalIngestService:
    """多模态导入服务"""

    def __init__(
        self,
        processing_service: CombinedProcessingService,
        indexing_service: IndexingServiceWrapper,
        pdf_extraction_service: PDFImageExtractor,
        repository: ImageChunkRepository,
    ):
        self.processing_service = processing_service
        self.indexing_service = indexing_service
        self.pdf_extraction_service = pdf_extraction_service
        self.repository = repository

    def ingest_image(self, image_paths: List[str], source_file: str = "", document_type: str = "unknown", page_start: int = 0, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """导入图片实现"""
        start_time = time.time()
        results = []
        errors = []

        options = options or {}
        options["document_type"] = document_type

        for idx, image_path in enumerate(image_paths):
            try:
                result = self.processing_service.process_image(
                    image_path=image_path,
                    source_file=source_file,
                    page_number=page_start + idx,
                    options=options,
                )

                if result.is_success and result.data:
                    chunk = result.data
                    chunk.document_type = document_type
                    self.indexing_service.index_image_chunk(chunk)
                    results.append(chunk.to_dict())
                else:
                    errors.append(f"{image_path}: {result.error or result.message}")

            except Exception as e:
                errors.append(f"{image_path}: {str(e)}")

        duration = (time.time() - start_time) * 1000

        return {
            "success": len(errors) == 0,
            "total_count": len(image_paths),
            "success_count": len(results),
            "failed_count": len(errors),
            "image_chunks": results,
            "errors": errors,
            "duration_ms": duration,
        }

    def ingest_pdf(self, pdf_path: str, document_type: str = "unknown", extract_images: bool = True, output_dir: str = None, min_image_size: int = 100) -> Dict[str, Any]:
        """导入PDF实现"""
        start_time = time.time()
        errors = []

        extracted_images = []
        if extract_images:
            extracted_images = self.pdf_extraction_service.extract_images_from_pdf(
                pdf_path=pdf_path,
                output_dir=output_dir,
                min_size=min_image_size,
            )

        image_result = self.ingest_image(
            image_paths=[img["image_path"] for img in extracted_images],
            source_file=pdf_path,
            document_type=document_type,
        )

        duration = (time.time() - start_time) * 1000

        return {
            "success": image_result["success"],
            "pdf_path": pdf_path,
            "text_chunks_count": 1,
            "image_chunks_count": image_result["success_count"],
            "extracted_images_count": len(extracted_images),
            "errors": errors + image_result["errors"],
            "duration_ms": duration,
        }

    def get_processing_status(self, source_file: str) -> Dict[str, Any]:
        """获取处理状态"""
        chunks = self.repository.find_by_source(source_file)
        if not chunks:
            return {"exists": False}

        return {
            "exists": True,
            "total_chunks": len(chunks),
            "processed": sum(1 for c in chunks if c.is_processed()),
            "failed": sum(1 for c in chunks if c.is_failed()),
            "pending": sum(1 for c in chunks if not c.is_processed() and not c.is_failed()),
        }

    def delete_by_source(self, source_file: str) -> int:
        """删除指定来源的所有片段"""
        chunks = self.repository.find_by_source(source_file)
        count = 0
        for chunk in chunks:
            if self.repository.delete(chunk.id):
                count += 1
        return count


def create_multimodal_service(vlm_enabled: bool = False) -> MultimodalIngestService:
    """创建多模态服务实例"""
    ocr_engine = EasyOCREngine()
    vlm_engine = QwenVLEngine(vlm_enabled=vlm_enabled)
    pdf_extractor = PDFImageExtractor()
    repository = ImageChunkRepository()
    indexing_wrapper = IndexingServiceWrapper(repository)

    print(f"[DEBUG] VLM enabled: {vlm_enabled}")

    service = MultimodalIngestService(
        processing_service=CombinedProcessingService(ocr_engine, vlm_engine),
        indexing_service=indexing_wrapper,
        pdf_extraction_service=pdf_extractor,
        repository=repository,
    )

    return service
