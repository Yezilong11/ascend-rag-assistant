"""
RAG API 路由模块
定义所有 RAG 相关的 API 端点

路由前缀: /api/rag
标签: rag

端点列表：
    POST /api/rag/chat                      — 普通问答
    POST /api/rag/chat/stream               — SSE 流式问答
    GET  /api/rag/status                    — 系统状态查询
    POST /api/rag/model/load                — 加载模型
    POST /api/rag/model/unload              — 卸载模型
    POST /api/rag/ingest                    — 上传文档
    POST /api/rag/knowledge-base/auto-ingest — 自动导入知识库
    GET  /api/rag/knowledge-base/stats      — 知识库统计

关联文档：
- API接口文档.md 第 4 节 — RAG API 接口定义
- 代码规范.md 第 2.5 节 — FastAPI 特定规范
"""

import json
import logging
import os
import tempfile
import threading
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from src.rag_api.dependencies import (
    clear_rag_assistant,
    get_is_loading,
    get_knowledge_base,
    get_rag_assistant,
    set_is_loading,
    set_rag_assistant,
)
from src.rag_api.models import ChatRequest, ModelLoadRequest
from src.rag_engine import PREDEFINED_MODELS, PREDEFINED_RERANKERS, RAGAssistant

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/rag", tags=["rag"])


@router.post("/chat")
async def chat(
    request: ChatRequest,
    assistant: Optional[RAGAssistant] = Depends(get_rag_assistant),
) -> dict:
    """
    普通问答接口

    向 RAG 引擎发送问题，获取完整回答（非流式）。
    适用于不需要打字机效果的场景。

    关联接口：API接口文档.md 4.4 普通问答

    Args:
        request: 问答请求，包含 question 字段
        assistant: RAGAssistant 实例（通过依赖注入获取）

    Returns:
        dict: 统一响应格式 {"success": bool, "data": {...}, "message": ...}

    Raises:
        HTTPException: 503 — RAG 引擎未加载
    """
    if assistant is None:
        raise HTTPException(
            status_code=503,
            detail="RAG引擎未加载，请先调用 /api/rag/model/load",
        )

    try:
        result = assistant.query(request.question)
        return {
            "success": True,
            "data": {
                "answer": result["answer"],
                "sources": result["sources"],
            },
        }
    except Exception as e:
        logger.error(f"问答处理失败: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"问答处理失败: {str(e)}",
        }


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    assistant: Optional[RAGAssistant] = Depends(get_rag_assistant),
) -> StreamingResponse:
    """
    SSE 流式问答接口

    向 RAG 引擎发送问题，通过 SSE 逐 token 流式返回回答。
    适用于聊天界面的打字机效果。

    SSE 事件类型：
        - token:   逐 token 推送，data 格式 {"token": "文字片段"}
        - sources: 参考来源列表，data 格式 {"sources": [...]}
        - done:    流结束标记，data 格式 {}

    关联接口：API接口文档.md 4.5 流式问答

    Args:
        request: 问答请求，包含 question 字段
        assistant: RAGAssistant 实例（通过依赖注入获取）

    Returns:
        StreamingResponse: SSE 事件流

    Raises:
        HTTPException: 503 — RAG 引擎未加载
    """
    if assistant is None:
        raise HTTPException(
            status_code=503,
            detail="RAG引擎未加载，请先调用 /api/rag/model/load",
        )

    def event_generator() -> str:
        for token in assistant.query_stream(request.question):
            yield f"event: token\ndata: {json.dumps({'token': token}, ensure_ascii=False)}\n\n"

        sources = getattr(assistant, "_last_sources", []) or []
        yield f"event: sources\ndata: {json.dumps({'sources': sources}, ensure_ascii=False)}\n\n"
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/status")
async def get_status() -> dict:
    """
    系统状态查询接口

    获取 RAG 引擎的当前状态，包括模型加载情况、可用模型列表等。
    此接口在引擎未加载时也可调用。

    关联接口：API接口文档.md 4.1 获取系统状态

    Returns:
        dict: 统一响应格式，data 包含引擎状态、模型信息、可用模型列表
    """
    assistant = get_rag_assistant()
    kb = get_knowledge_base()

    status_data = {
        "engine_loaded": assistant is not None,
        "model_key": assistant.model_key if assistant else "",
        "model_name": (
            PREDEFINED_MODELS.get(assistant.model_key, {}).get("name", "")
            if assistant
            else ""
        ),
        "reranker_enabled": assistant.use_reranker if assistant else False,
        "reranker_model": (
            assistant.reranker.model_name
            if assistant and hasattr(assistant, "reranker") and assistant.reranker
            else ""
        ),
        "knowledge_base_ready": kb is not None,
        "available_models": {
            k: {"name": v["name"], "description": v["description"]}
            for k, v in PREDEFINED_MODELS.items()
        },
        "available_rerankers": {
            k: {"name": v["name"], "description": v["description"], "size": v["size"]}
            for k, v in PREDEFINED_RERANKERS.items()
        },
    }

    return {"success": True, "data": status_data}


@router.post("/model/load")
async def load_model(request: ModelLoadRequest) -> dict:
    """
    加载模型接口

    异步加载指定的大语言模型和重排序模型。
    此接口立即返回，模型在后台线程中加载。
    前端通过轮询 /api/rag/status 检测加载完成。

    关联接口：API接口文档.md 4.2 加载模型

    Args:
        request: 模型加载请求，包含 model_key、reranker 配置等

    Returns:
        dict: 统一响应格式，data 包含 model_key 和 status="loading"
    """
    if get_is_loading():
        return {
            "success": False,
            "message": "模型正在加载中，请稍候",
        }

    if get_rag_assistant() is not None:
        clear_rag_assistant()

    set_is_loading(True)

    def load_model_task() -> None:
        try:
            kb = get_knowledge_base()
            assistant = RAGAssistant(
                knowledge_base=kb,
                model_key=request.model_key,
                model_dir=request.model_dir,
                use_reranker=request.use_reranker,
                reranker_model=request.reranker_model,
                reranker_top_k=request.reranker_top_k,
                initial_retrieval_k=request.initial_retrieval_k,
            )
            set_rag_assistant(assistant)
            logger.info(f"模型加载完成: model_key={request.model_key}")
        except Exception as e:
            logger.error(f"模型加载失败: {e}", exc_info=True)
        finally:
            set_is_loading(False)

    thread = threading.Thread(target=load_model_task, daemon=True)
    thread.start()

    return {
        "success": True,
        "data": {
            "model_key": request.model_key,
            "status": "loading",
        },
    }


@router.post("/model/unload")
async def unload_model() -> dict:
    """
    卸载模型接口

    卸载当前已加载的模型，释放 GPU 显存。

    关联接口：API接口文档.md 4.3 卸载模型

    Returns:
        dict: 统一响应格式，包含操作结果
    """
    if get_rag_assistant() is None:
        return {
            "success": False,
            "message": "没有已加载的模型",
        }

    clear_rag_assistant()

    return {
        "success": True,
        "message": "模型已卸载",
    }


@router.post("/ingest")
async def ingest_file(file: UploadFile = File(...)) -> dict:
    """
    统一文件上传导入接口

    上传文档到知识库，系统自动检测文件类型并选择合适的处理方式：
    - 图片文件(.png/.jpg/.jpeg/.gif/.bmp): 自动分流到多模态知识库，进行OCR处理
    - 文档文件(.pdf/.txt/.md等): 文本切分后存入主知识库

    关联接口：API接口文档.md 4.6 上传文档

    Args:
        file: 上传的文件，支持多种格式，最大 50MB

    Returns:
        dict: 统一响应格式，data 包含 filename、doc_type、chunks_count、source_type

    Raises:
        HTTPException: 400 — 不支持的文件格式或文件过大
    """
    allowed_extensions = [".pdf", ".txt", ".md", ".docx", ".doc", ".html", ".htm", ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".pptx", ".ppt", ".csv", ".xls", ".xlsx", ".json", ".jsonl"]
    image_extensions = [".png", ".jpg", ".jpeg", ".gif", ".bmp"]
    
    filename = file.filename or ""
    _, ext = os.path.splitext(filename)
    ext = ext.lower()

    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式，仅支持 {allowed_extensions}",
        )

    content = await file.read()

    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="文件大小超过50MB限制",
        )

    # 判断是否为图片文件，自动分流处理
    is_image = ext in image_extensions
    source_type = "image" if is_image else "document"

    temp_fd, temp_path = tempfile.mkstemp(suffix=ext)
    try:
        with os.fdopen(temp_fd, "wb") as f:
            f.write(content)

        if is_image:
            # 图片文件：分流到多模态知识库，进行OCR处理
            return await _ingest_image_to_multimodal(temp_path, filename)
        else:
            # 文档文件：使用主知识库文本处理
            return await _ingest_document_to_kb(temp_path, filename)

    except Exception as e:
        logger.error(f"文件导入异常: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"文件导入失败: {str(e)}",
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


async def _ingest_image_to_multimodal(image_path: str, filename: str) -> dict:
    """
    将图片导入多模态知识库（OCR处理）
    
    Args:
        image_path: 图片临时文件路径
        filename: 原始文件名
    
    Returns:
        dict: 导入结果
    """
    try:
        from src.multimodal.interface.api.routes import create_multimodal_service
        from src.multimodal.application.dtos import ImageIngestDTO
        
        service = create_multimodal_service(vlm_enabled=False)
        
        dto = ImageIngestDTO(
            image_paths=[image_path],
            source_file=filename,
            document_type="uploaded",
        )
        
        result = service.ingest_image(dto)
        
        if result.success:
            return {
                "success": True,
                "data": {
                    "filename": filename,
                    "doc_type": "image",
                    "source_type": "image",
                    "chunks_count": result.success_count,
                    "message": "图片已导入多模态知识库，完成OCR识别",
                },
            }
        else:
            return {
                "success": False,
                "message": f"图片导入失败: {result.message}",
            }
    except Exception as e:
        logger.error(f"多模态知识库导入异常: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"图片OCR处理失败: {str(e)}",
        }


async def _ingest_document_to_kb(doc_path: str, filename: str) -> dict:
    """
    将文档导入主知识库（文本处理）
    
    Args:
        doc_path: 文档临时文件路径
        filename: 原始文件名
    
    Returns:
        dict: 导入结果
    """
    kb = get_knowledge_base()
    success = kb.ingest(doc_path, display_source=filename)

    if success:
        doc_type = kb.detect_doc_type(doc_path)
        collection = kb.db._collection
        chunks_count = collection.count() if hasattr(collection, "count") else 0

        return {
            "success": True,
            "data": {
                "filename": filename,
                "doc_type": doc_type,
                "source_type": "document",
                "chunks_count": chunks_count,
            },
        }
    else:
        return {
            "success": False,
            "message": f"文件导入失败: {filename}",
        }


@router.post("/knowledge-base/auto-ingest")
async def auto_ingest() -> dict:
    """
    自动导入知识库接口

    自动扫描 data/ 目录下的所有文档并导入知识库。
    如果知识库已有数据则跳过导入。

    关联接口：API接口文档.md 4.7 自动导入知识库

    Returns:
        dict: 统一响应格式，data 包含 total_files、success_count、failed_count
    """
    kb = get_knowledge_base()

    try:
        collection = kb.db._collection
        current_count = collection.count() if hasattr(collection, "count") else 0

        if current_count > 1:
            return {
                "success": True,
                "data": {
                    "total_files": 0,
                    "success_count": 0,
                    "failed_count": 0,
                    "message": "知识库已有数据，跳过导入",
                },
            }
    except Exception:
        pass

    data_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "data",
    )

    if not os.path.exists(data_dir):
        return {
            "success": True,
            "data": {
                "total_files": 0,
                "success_count": 0,
                "failed_count": 0,
                "message": "data/ 目录不存在，无文件可导入",
            },
        }

    supported_extensions = (".pdf", ".txt", ".md", ".docx", ".doc", ".html", ".htm", ".png", ".jpg", ".jpeg", ".pptx", ".ppt", ".csv", ".xls", ".xlsx", ".json", ".jsonl")
    total_files = 0
    success_count = 0
    failed_count = 0

    for root, _dirs, files in os.walk(data_dir):
        for fname in files:
            if fname.lower().endswith(supported_extensions):
                total_files += 1
                file_path = os.path.join(root, fname)
                try:
                    result = kb.ingest(file_path)
                    if result:
                        success_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    logger.error(f"自动导入文件失败: {file_path}, 错误: {e}")
                    failed_count += 1

    return {
        "success": True,
        "data": {
            "total_files": total_files,
            "success_count": success_count,
            "failed_count": failed_count,
        },
    }


@router.get("/knowledge-base/stats")
async def knowledge_base_stats() -> dict:
    """
    知识库统计接口

    获取知识库的文档片段统计信息。

    关联接口：API接口文档.md 4.8 知识库统计

    Returns:
        dict: 统一响应格式，data 包含 total_chunks
    """
    kb = get_knowledge_base()

    try:
        collection = kb.db._collection
        total_chunks = collection.count() if hasattr(collection, "count") else 0
    except Exception:
        total_chunks = 0

    return {
        "success": True,
        "data": {
            "total_chunks": total_chunks,
        },
    }
