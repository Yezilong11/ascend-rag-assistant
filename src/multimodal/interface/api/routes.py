"""
API Routes - FastAPI路由定义
"""

from fastapi import APIRouter, UploadFile, File, Form, Depends
from typing import List
import os
import tempfile

router = APIRouter(prefix="/api/multimodal", tags=["multimodal"])


class IndexingServiceWrapper:
    """将ImageChunkRepository适配为ImageIndexingService"""

    def __init__(self, repository):
        if not hasattr(repository, 'save'):
            raise ValueError(f"Repository {type(repository)} must have 'save' method")
        self._repo = repository

    def index_image_chunk(self, chunk):
        return self._repo.save(chunk)

    def index_batch(self, chunks):
        self._repo.save_batch(chunks)
        return len(chunks), 0

    def search_similar(self, query, k=3, document_type=None):
        return self._repo.similarity_search(query, k)

    def delete_from_index(self, chunk_id):
        return self._repo.delete(chunk_id)


class CombinedProcessingService:
    """组合OCR+VLM处理服务"""

    def __init__(self, ocr_engine, vlm_engine):
        self._ocr = ocr_engine
        self._vlm = vlm_engine

    def process_image(self, image_path, source_file="", page_number=0, options=None):
        from ...domain.entities.image_chunk import ImageChunk
        from ...domain.value_objects.processing_status import ProcessingResult
        import uuid
        import time

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

    def process_image_batch(self, image_paths, source_file="", start_page=0, options=None):
        results = []
        failed_count = 0
        for idx, path in enumerate(image_paths):
            result = self.process_image(path, source_file, start_page + idx, options)
            if result.is_success:
                results.append(result.data)
            else:
                failed_count += 1
        from ...domain.value_objects.processing_status import ProcessingResult
        return ProcessingResult.partial(
            message=f"批量处理完成",
            data=results,
            success_count=len(results),
            failed_count=failed_count,
        )

    def extract_text_from_image(self, image_path):
        return self._ocr.extract_text_from_image(image_path)

    def generate_image_description(self, image_path, ocr_text="", prompt=None):
        try:
            return self._vlm.generate_image_description(image_path, ocr_text, prompt)
        except Exception:
            return f"图片包含文字: {ocr_text}" if ocr_text else "图片内容"

    def analyze_image_with_query(self, image_path, query):
        try:
            return self._vlm.analyze_image_with_query(image_path, query)
        except Exception:
            return "VLM不可用，无法分析图片"


def get_multimodal_service():
    """获取多模态服务实例（依赖注入）"""
    from ...application.services import MultimodalIngestServiceImpl
    from ...infrastructure import (
        PaddleOCREngine,
        QwenVLEngine,
        PDFImageExtractor,
        ChromaImageChunkRepository,
    )

    ocr_engine = PaddleOCREngine()
    vlm_engine = QwenVLEngine()
    pdf_extractor = PDFImageExtractor()
    repository = ChromaImageChunkRepository()
    indexing_wrapper = IndexingServiceWrapper(repository)

    print(f"[DEBUG] IndexingServiceWrapper type: {type(indexing_wrapper)}")
    print(f"[DEBUG] IndexingServiceWrapper.index_image_chunk: {hasattr(indexing_wrapper, 'index_image_chunk')}")

    service = MultimodalIngestServiceImpl(
        processing_service=CombinedProcessingService(ocr_engine, vlm_engine),
        indexing_service=indexing_wrapper,
        pdf_extraction_service=pdf_extractor,
        repository=repository,
    )

    print(f"[DEBUG] MultimodalIngestServiceImpl.indexing_service type: {type(service.indexing_service)}")
    return service


@router.post("/image/ingest")
async def ingest_image(
    files: List[UploadFile] = File(...),
    document_type: str = Form("unknown"),
    service = Depends(get_multimodal_service, use_cache=False),
):
    """UC1/UC2: 上传图片并导入知识库"""
    from ...application.dtos import ImageIngestDTO

    temp_paths = []
    try:
        for file in files:
            suffix = os.path.splitext(file.filename)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                content = await file.read()
                tmp.write(content)
                temp_paths.append(tmp.name)

        dto = ImageIngestDTO(
            image_paths=temp_paths,
            source_file=temp_paths[0] if temp_paths else "",
            document_type=document_type,
        )

        result = service.ingest_image(dto)

        return result.to_dict()

    finally:
        for path in temp_paths:
            if os.path.exists(path):
                os.remove(path)


@router.post("/pdf/ingest")
async def ingest_pdf(
    file: UploadFile = File(...),
    document_type: str = Form("unknown"),
    extract_images: bool = Form(True),
    service = Depends(get_multimodal_service, use_cache=False),
):
    """UC3: 上传PDF并导入（文本+内嵌图片）"""
    from ...application.dtos import PDFIngestDTO

    temp_path = None
    try:
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            temp_path = tmp.name

        dto = PDFIngestDTO(
            pdf_path=temp_path,
            document_type=document_type,
            extract_images=extract_images,
        )

        result = service.ingest_pdf(dto)

        return result.to_dict()

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@router.delete("/source/{source_file:path}")
async def delete_by_source(
    source_file: str,
    service = Depends(get_multimodal_service, use_cache=False),
):
    """删除指定来源的所有片段"""
    count = service.delete_by_source(source_file)
    return {"deleted_count": count}


@router.get("/status/{source_file:path}")
async def get_processing_status(
    source_file: str,
    service = Depends(get_multimodal_service, use_cache=False),
):
    """获取处理状态"""
    return service.get_processing_status(source_file)