"""
MultimodalIngestService - 多模态导入应用服务
协调OCR、VLM、PDF提取器进行文档导入
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import time

from ...domain.entities.image_chunk import ImageChunk
from ...domain.value_objects.processing_status import ProcessingStatus, ProcessingResult
from ...domain.services.multimodal_processing_service import (
    MultimodalProcessingService,
    ImageIndexingService,
    PDFImageExtractionService,
)
from ...domain.repositories.image_chunk_repository import ImageChunkRepository
from ..dtos.image_ingest_dto import (
    ImageIngestDTO,
    ImageIngestResultDTO,
    PDFIngestDTO,
    PDFIngestResultDTO,
)


class MultimodalIngestService(ABC):
    """
    多模态导入应用服务接口
    协调OCR、VLM、PDF提取器进行文档导入

    Use Cases:
        UC1: 上传单张图片并导入知识库
        UC2: 批量上传多张图片并导入知识库
        UC3: 从PDF提取内嵌图片并导入知识库
        UC4: 导入整个文件夹的图片和PDF
    """

    @abstractmethod
    def ingest_image(self, dto: ImageIngestDTO) -> ImageIngestResultDTO:
        """导入单张或批量图片"""
        pass

    @abstractmethod
    def ingest_pdf(self, dto: PDFIngestDTO) -> PDFIngestResultDTO:
        """导入PDF文档（文本+内嵌图片）"""
        pass

    @abstractmethod
    def ingest_folder(self, folder_path: str, document_type: str = "unknown") -> Dict[str, Any]:
        """导入整个文件夹"""
        pass

    @abstractmethod
    def get_processing_status(self, source_file: str) -> Dict[str, Any]:
        """获取文档处理状态"""
        pass

    @abstractmethod
    def delete_by_source(self, source_file: str) -> int:
        """删除指定来源的所有片段"""
        pass


class MultimodalIngestServiceImpl(MultimodalIngestService):
    """
    多模态导入应用服务实现
    """

    def __init__(
        self,
        processing_service: MultimodalProcessingService,
        indexing_service: ImageIndexingService,
        pdf_extraction_service: PDFImageExtractionService,
        repository: ImageChunkRepository,
    ):
        self.processing_service = processing_service
        self.indexing_service = indexing_service
        self.pdf_extraction_service = pdf_extraction_service
        self.repository = repository

    def ingest_image(self, dto: ImageIngestDTO) -> ImageIngestResultDTO:
        """导入图片实现"""
        start_time = time.time()
        results = []
        errors = []

        for idx, image_path in enumerate(dto.image_paths):
            try:
                result = self.processing_service.process_image(
                    image_path=image_path,
                    source_file=dto.source_file,
                    page_number=dto.page_start + idx,
                    options=dto.options,
                )

                if result.is_success and result.data:
                    chunk = result.data
                    chunk.document_type = dto.document_type
                    print(f"[DEBUG ingest_image] self.indexing_service type: {type(self.indexing_service)}")
                    print(f"[DEBUG ingest_image] hasattr index_image_chunk: {hasattr(self.indexing_service, 'index_image_chunk')}")
                    self.indexing_service.index_image_chunk(chunk)
                    results.append(chunk.to_dict())
                else:
                    errors.append(f"{image_path}: {result.error or result.message}")

            except Exception as e:
                errors.append(f"{image_path}: {str(e)}")

        duration = (time.time() - start_time) * 1000

        return ImageIngestResultDTO(
            success=len(errors) == 0,
            total_count=len(dto.image_paths),
            success_count=len(results),
            failed_count=len(errors),
            image_chunks=results,
            errors=errors,
            duration_ms=duration,
        )

    def ingest_pdf(self, dto: PDFIngestDTO) -> PDFIngestResultDTO:
        """导入PDF实现"""
        start_time = time.time()
        errors = []

        extracted_images = []
        if dto.extract_images:
            extracted_images = self.pdf_extraction_service.extract_images_from_pdf(
                pdf_path=dto.pdf_path,
                output_dir=dto.output_dir,
                min_size=dto.min_image_size,
            )

        text_result = ProcessingResult.success(message="PDF text extraction handled by KnowledgeBase")

        image_ingest_dto = ImageIngestDTO(
            image_paths=[img["image_path"] for img in extracted_images],
            source_file=dto.pdf_path,
            document_type=dto.document_type,
        )

        image_result = self.ingest_image(image_ingest_dto)

        duration = (time.time() - start_time) * 1000

        return PDFIngestResultDTO(
            success=image_result.success,
            pdf_path=dto.pdf_path,
            text_chunks_count=1,
            image_chunks_count=image_result.success_count,
            extracted_images_count=len(extracted_images),
            errors=errors + image_result.errors,
            duration_ms=duration,
        )

    def ingest_folder(
        self,
        folder_path: str,
        document_type: str = "unknown",
    ) -> Dict[str, Any]:
        """导入文件夹实现"""
        import os
        from pathlib import Path

        supported_extensions = {".jpg", ".jpeg", ".png", ".pdf"}
        files = []
        for ext in supported_extensions:
            files.extend(Path(folder_path).glob(f"**/*{ext}"))

        results = {
            "total_files": len(files),
            "images_processed": 0,
            "pdfs_processed": 0,
            "failed": [],
        }

        for file_path in files:
            file_path = str(file_path)
            if file_path.lower().endswith(".pdf"):
                dto = PDFIngestDTO(
                    pdf_path=file_path,
                    document_type=document_type,
                )
                result = self.ingest_pdf(dto)
                if result.success:
                    results["pdfs_processed"] += 1
                else:
                    results["failed"].append(file_path)
            else:
                dto = ImageIngestDTO.from_single_image(
                    image_path=file_path,
                    source_file=file_path,
                    document_type=document_type,
                )
                result = self.ingest_image(dto)
                if result.success:
                    results["images_processed"] += 1
                else:
                    results["failed"].append(file_path)

        return results

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
            "pending": sum(1 for c in chunks if c.is_pending()),
        }

    def delete_by_source(self, source_file: str) -> int:
        """删除指定来源的所有片段"""
        chunks = self.repository.find_by_source(source_file)
        count = 0
        for chunk in chunks:
            if self.repository.delete(chunk.id):
                count += 1
        return count