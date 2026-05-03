"""
MultimodalQueryService - 多模态查询应用服务
协调RAG检索和VLM推理进行问答
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import time

from ...domain.entities.image_chunk import ImageChunk
from ...domain.repositories.image_chunk_repository import ImageChunkRepository
from ...domain.services.multimodal_processing_service import MultimodalProcessingService
from ..dtos.multimodal_query_dto import (
    MultimodalQueryDTO,
    MultimodalQueryResultDTO,
    ImageSourceDTO,
    TextSourceDTO,
    ImageQueryDTO,
    ImageQueryResultDTO,
)


class MultimodalQueryService(ABC):
    """
    多模态查询应用服务接口
    协调文本RAG和图片RAG进行混合检索

    Use Cases:
        UC5: 文本+图片混合检索问答
        UC6: 基于上传图片的问答
        UC7: 仅图片检索
    """

    @abstractmethod
    def query(self, dto: MultimodalQueryDTO) -> MultimodalQueryResultDTO:
        """混合检索问答"""
        pass

    @abstractmethod
    def query_with_image(self, dto: ImageQueryDTO) -> ImageQueryResultDTO:
        """基于图片问答"""
        pass

    @abstractmethod
    def search_images(self, query: str, k: int = 3) -> List[ImageSourceDTO]:
        """仅图片检索"""
        pass


class MultimodalQueryServiceImpl(MultimodalQueryService):
    """
    多模态查询应用服务实现
    """

    def __init__(
        self,
        image_repository: ImageChunkRepository,
        processing_service: MultimodalProcessingService,
        text_rag_retriever: Any = None,
    ):
        self.image_repository = image_repository
        self.processing_service = processing_service
        self.text_rag_retriever = text_rag_retriever

    def query(self, dto: MultimodalQueryDTO) -> MultimodalQueryResultDTO:
        """混合检索问答实现"""
        start_time = time.time()
        text_sources = []
        image_sources = []

        if dto.include_text and self.text_rag_retriever:
            try:
                text_results = self.text_rag_retriever.similarity_search(
                    dto.query, k=dto.k
                )
                for doc in text_results:
                    text_sources.append(TextSourceDTO(
                        chunk_id=doc.metadata.get("chunk_id", ""),
                        content=doc.page_content,
                        source_file=doc.metadata.get("source", ""),
                        page_number=doc.metadata.get("page", 0),
                        relevance_score=0.9,
                    ))
            except Exception:
                pass

        if dto.include_images:
            try:
                image_chunks = self.image_repository.similarity_search(
                    query=dto.query,
                    k=dto.k,
                    filter_criteria={"document_type": dto.document_types} if dto.document_types else None,
                )

                for chunk in image_chunks:
                    image_sources.append(ImageSourceDTO(
                        chunk_id=chunk.id,
                        image_path=chunk.image_path,
                        description=chunk.page_content,
                        ocr_text=chunk.ocr_text,
                        source_file=chunk.source_file,
                        page_number=chunk.page_number,
                        relevance_score=0.9,
                    ))
            except Exception:
                pass

        context_parts = []
        if text_sources:
            context_parts.append("【文本资料】\n" + "\n".join(s.content for s in text_sources[:2]))
        if image_sources:
            context_parts.append("【图片资料】\n" + "\n".join(f"图片: {s.description}" for s in image_sources[:2]))

        context = "\n\n".join(context_parts) if context_parts else "未找到相关资料"

        prompt = f"""基于以下资料回答问题。如果资料中没有相关信息，请说明"资料中未找到相关内容"。

{context}

问题: {dto.query}
回答:"""

        answer = self._generate_answer(prompt)

        duration = (time.time() - start_time) * 1000

        return MultimodalQueryResultDTO(
            query=dto.query,
            answer=answer,
            text_sources=text_sources,
            image_sources=image_sources,
            duration_ms=duration,
        )

    def query_with_image(self, dto: ImageQueryDTO) -> ImageQueryResultDTO:
        """基于图片问答实现"""
        start_time = time.time()

        ocr_text, _ = self.processing_service.extract_text_from_image(dto.image_path)

        answer = self.processing_service.analyze_image_with_query(
            image_path=dto.image_path,
            query=dto.query,
        )

        duration = (time.time() - start_time) * 1000

        return ImageQueryResultDTO(
            image_path=dto.image_path,
            query=dto.query,
            answer=answer,
            detected_text=ocr_text,
            duration_ms=duration,
        )

    def search_images(self, query: str, k: int = 3) -> List[ImageSourceDTO]:
        """仅图片检索实现"""
        image_chunks = self.image_repository.similarity_search(query=query, k=k)

        return [
            ImageSourceDTO(
                chunk_id=chunk.id,
                image_path=chunk.image_path,
                description=chunk.page_content,
                ocr_text=chunk.ocr_text,
                source_file=chunk.source_file,
                page_number=chunk.page_number,
                relevance_score=0.9,
            )
            for chunk in image_chunks
        ]

    def _generate_answer(self, prompt: str) -> str:
        """调用LLM生成答案（复用现有RAGAssistant）"""
        if self.text_rag_retriever and hasattr(self.text_rag_retriever, "llm"):
            try:
                response = self.text_rag_retriever.llm(prompt)
                return response.strip()
            except Exception:
                pass
        return "抱歉，生成答案时出现错误。"