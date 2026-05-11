"""
Persistence Infrastructure - Chroma向量数据库仓储实现
"""

import os
import uuid
from typing import List, Dict, Any, Optional
import torch

from ...domain.entities.image_chunk import ImageChunk
from ...domain.value_objects.bounding_box import BoundingBox
from ...domain.value_objects.processing_status import ProcessingStatus
from ...domain.repositories.image_chunk_repository import ImageChunkRepository

try:
    from modelscope import snapshot_download
    MODELSCOPE_AVAILABLE = True
except ImportError:
    MODELSCOPE_AVAILABLE = False


class ChromaImageChunkRepository(ImageChunkRepository):
    """
    Chroma向量数据库仓储实现
    设备: CPU (异构计算设计)
    """

    COLLECTION_NAME = "multimodal_image_chunks"
    LOCAL_MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "models", "bge-large-zh-v1.5"))

    def __init__(
        self,
        persist_dir: str = "./chroma_db_multimodal",
        embedding_model: str = None,
    ):
        self._persist_dir = persist_dir
        self._embedding_model = embedding_model or self.LOCAL_MODEL_DIR
        self._embeddings = None
        self._db = None
        self._collection = None
        self._initialized = False

    def _initialize(self):
        """初始化向量数据库"""
        if self._initialized:
            return

        os.makedirs(self._persist_dir, exist_ok=True)

        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            from langchain_chroma import Chroma
        except ImportError:
            raise ImportError(
                "向量数据库依赖未安装。请运行: pip install langchain langchain-huggingface langchain-chroma chromadb"
            )

        # 优先使用本地模型，其次ModelScope下载，最后HuggingFace在线加载
        embedding_model = self._embedding_model
        if not os.path.exists(embedding_model):
            if MODELSCOPE_AVAILABLE:
                print(f"[INFO] 本地Embedding模型未找到，正在从ModelScope下载 bge-large-zh-v1.5...")
                try:
                    os.makedirs(embedding_model, exist_ok=True)
                    snapshot_download(
                        "BAAI/bge-large-zh-v1.5",
                        local_dir=embedding_model
                    )
                    print(f"[OK] ModelScope下载完成，保存到: {embedding_model}")
                except Exception as e:
                    print(f"[WARN] ModelScope下载失败: {e}，尝试从HuggingFace加载")
                    embedding_model = "BAAI/bge-large-zh-v1.5"
            else:
                print("[INFO] 本地Embedding模型未找到，正在从HuggingFace下载 BAAI/bge-large-zh-v1.5...")
                embedding_model = "BAAI/bge-large-zh-v1.5"

        self._embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={"device": "cpu"}
        )

        try:
            self._db = Chroma(
                persist_directory=self._persist_dir,
                embedding_function=self._embeddings,
                collection_name=self.COLLECTION_NAME,
            )
            self._collection = self._db._collection
        except Exception as e:
            print(f"Chroma数据库初始化失败: {e}")
            self._db = Chroma.from_texts(
                texts=["初始化文档"],
                embedding=self._embeddings,
                persist_directory=self._persist_dir,
                collection_name=self.COLLECTION_NAME,
            )
            self._collection = self._db._collection

        self._initialized = True

    def save(self, chunk: ImageChunk) -> ImageChunk:
        """保存单个图片片段"""
        self._initialize()

        if not chunk.id:
            chunk.id = str(uuid.uuid4())

        texts = [chunk.get_searchable_text()]
        metadatas = [self._chunk_to_metadata(chunk)]
        ids = [chunk.id]

        self._db.add_texts(texts=texts, metadatas=metadatas, ids=ids)

        return chunk

    def save_batch(self, chunks: List[ImageChunk]) -> List[ImageChunk]:
        """批量保存"""
        self._initialize()

        texts = []
        metadatas = []
        ids = []

        for chunk in chunks:
            if not chunk.id:
                chunk.id = str(uuid.uuid4())

            texts.append(chunk.get_searchable_text())
            metadatas.append(self._chunk_to_metadata(chunk))
            ids.append(chunk.id)

        if texts:
            self._db.add_texts(texts=texts, metadatas=metadatas, ids=ids)

        return chunks

    def find_by_id(self, chunk_id: str) -> Optional[ImageChunk]:
        """根据ID查找"""
        self._initialize()

        try:
            result = self._collection.get(ids=[chunk_id])
            if result and result["ids"]:
                idx = result["ids"].index(chunk_id)
                return self._metadata_to_chunk(result, idx)
        except Exception:
            pass

        return None

    def find_by_source(self, source_file: str) -> List[ImageChunk]:
        """根据源文件查找"""
        self._initialize()

        try:
            result = self._collection.where(
                {"source_file": source_file}
            )
            return self._results_to_chunks(result)
        except Exception:
            return []

    def find_by_document_type(self, document_type: str) -> List[ImageChunk]:
        """根据文档类型查找"""
        self._initialize()

        try:
            result = self._collection.where(
                {"document_type": document_type}
            )
            return self._results_to_chunks(result)
        except Exception:
            return []

    def similarity_search(
        self,
        query: str,
        k: int = 3,
        filter_criteria: Dict[str, Any] = None,
    ) -> List[ImageChunk]:
        """相似度检索"""
        self._initialize()

        try:
            where_filter = None
            if filter_criteria:
                where_filter = filter_criteria

            results = self._db.similarity_search_with_score(
                query=query,
                k=k,
                filter=where_filter,
            )

            chunks = []
            for doc, score in results:
                chunk = self._document_to_chunk(doc)
                chunk.metadata["relevance_score"] = score
                chunks.append(chunk)

            return chunks

        except Exception as e:
            print(f"检索失败: {e}")
            return []

    def update_status(self, chunk_id: str, status: ProcessingStatus) -> bool:
        """更新状态"""
        self._initialize()

        try:
            chunk = self.find_by_id(chunk_id)
            if chunk:
                chunk.processing_status = status
                self.save(chunk)
                return True
        except Exception:
            pass

        return False

    def delete(self, chunk_id: str) -> bool:
        """删除"""
        self._initialize()

        try:
            self._collection.delete(ids=[chunk_id])
            return True
        except Exception:
            return False

    def delete_by_source(self, source_file: str) -> int:
        """删除指定来源"""
        self._initialize()

        chunks = self.find_by_source(source_file)
        count = 0
        for chunk in chunks:
            if self.delete(chunk.id):
                count += 1

        return count

    def count(self) -> int:
        """获取总数"""
        self._initialize()

        try:
            return self._collection.count()
        except Exception:
            return 0

    def exists(self, chunk_id: str) -> bool:
        """检查存在"""
        return self.find_by_id(chunk_id) is not None

    def _chunk_to_metadata(self, chunk: ImageChunk) -> Dict[str, Any]:
        """转换为元数据"""
        metadata = {
            "chunk_id": chunk.id,
            "image_path": chunk.image_path,
            "ocr_text": chunk.ocr_text,
            "page_content": chunk.page_content,
            "source_file": chunk.source_file,
            "document_type": chunk.document_type,
            "page_number": chunk.page_number,
            "processing_status": chunk.processing_status.value,
        }

        if chunk.bounding_box:
            metadata["bbox"] = chunk.bounding_box.to_list()

        metadata.update(chunk.metadata)

        return metadata

    def _metadata_to_chunk(self, result: Dict, idx: int) -> Optional[ImageChunk]:
        """元数据转换为片段"""
        try:
            metadata = result["metadatas"][idx]
            bbox_data = metadata.get("bbox")

            return ImageChunk(
                id=metadata.get("chunk_id", ""),
                page_content=metadata.get("page_content", ""),
                image_path=metadata.get("image_path", ""),
                ocr_text=metadata.get("ocr_text", ""),
                source_file=metadata.get("source_file", ""),
                document_type=metadata.get("document_type", "unknown"),
                page_number=metadata.get("page_number", 0),
                bounding_box=BoundingBox.from_list(bbox_data) if bbox_data else None,
                processing_status=ProcessingStatus(metadata.get("processing_status", "pending")),
                metadata={k: v for k, v in metadata.items()
                          if k not in ["chunk_id", "image_path", "ocr_text", "page_content",
                                       "source_file", "document_type", "page_number",
                                       "processing_status", "bbox"]},
            )
        except Exception:
            return None

    def _results_to_chunks(self, result: Dict) -> List[ImageChunk]:
        """结果列表转换为片段列表"""
        chunks = []
        if result and result["ids"]:
            for idx in range(len(result["ids"])):
                chunk = self._metadata_to_chunk(result, idx)
                if chunk:
                    chunks.append(chunk)
        return chunks

    def _document_to_chunk(self, doc) -> ImageChunk:
        """Document转换为片段"""
        metadata = doc.metadata

        bbox_data = metadata.get("bbox")
        bbox = BoundingBox.from_list(bbox_data) if bbox_data else None

        return ImageChunk(
            id=metadata.get("chunk_id", str(uuid.uuid4())),
            page_content=doc.page_content,
            image_path=metadata.get("image_path", ""),
            ocr_text=metadata.get("ocr_text", ""),
            source_file=metadata.get("source_file", ""),
            document_type=metadata.get("document_type", "unknown"),
            page_number=metadata.get("page_number", 0),
            bounding_box=bbox,
            processing_status=ProcessingStatus(metadata.get("processing_status", "completed")),
        )