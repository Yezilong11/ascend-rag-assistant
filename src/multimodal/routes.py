"""
多模态API路由 - 简化版本
提供图片上传、PDF处理等API端点
统一响应格式: {success: bool, data: Any, message: str}
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Any
import os
import tempfile

from src.rag_api.models import success_response, error_response

router = APIRouter(prefix="/api/multimodal", tags=["multimodal"])


@router.post("/image/ingest")
async def ingest_image(
    files: List[UploadFile] = File(...),
    document_type: str = Form("unknown"),
    vlm_enabled: bool = Form(False),
) -> dict:
    """
    UC1/UC2: 上传图片并导入知识库

    统一响应格式:
        {
            "success": bool,
            "data": {
                "total_count": int,
                "success_count": int,
                "failed_count": int,
                "image_chunks": [...]
            },
            "message": str
        }
    """
    from .service import create_multimodal_service

    service = create_multimodal_service(vlm_enabled=vlm_enabled)

    temp_paths = []
    try:
        # 保存上传文件到临时目录
        for file in files:
            suffix = os.path.splitext(file.filename)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                content = await file.read()
                tmp.write(content)
                temp_paths.append(tmp.name)

        # 调用服务处理图片
        result = service.ingest_image(
            image_paths=temp_paths,
            source_file=temp_paths[0] if temp_paths else "",
            document_type=document_type,
        )

        # 统一响应格式
        if result.get("success"):
            return success_response(
                data={
                    "total_count": result.get("total_count", 0),
                    "success_count": result.get("success_count", 0),
                    "failed_count": result.get("failed_count", 0),
                    "image_chunks": result.get("image_chunks", []),
                },
                message=f"成功导入 {result.get('success_count', 0)} 个文件"
            )
        else:
            return error_response(
                message=f"导入失败",
                data={"errors": result.get("errors", [])}
            )

    except Exception as e:
        return error_response(message=f"处理失败: {str(e)}")

    finally:
        # 清理临时文件
        for path in temp_paths:
            if os.path.exists(path):
                os.remove(path)


@router.post("/pdf/ingest")
async def ingest_pdf(
    file: UploadFile = File(...),
    document_type: str = Form("unknown"),
    extract_images: bool = Form(True),
    vlm_enabled: bool = Form(False),
) -> dict:
    """
    UC3: 上传PDF并导入（文本+内嵌图片）

    统一响应格式:
        {
            "success": bool,
            "data": {
                "pdf_path": str,
                "text_chunks_count": int,
                "image_chunks_count": int,
                "extracted_images_count": int
            },
            "message": str
        }
    """
    from .service import create_multimodal_service

    service = create_multimodal_service(vlm_enabled=vlm_enabled)

    temp_path = None
    try:
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            temp_path = tmp.name

        result = service.ingest_pdf(
            pdf_path=temp_path,
            document_type=document_type,
            extract_images=extract_images,
        )

        # 统一响应格式
        if result.get("success"):
            return success_response(
                data={
                    "pdf_path": result.get("pdf_path", ""),
                    "text_chunks_count": result.get("text_chunks_count", 0),
                    "image_chunks_count": result.get("image_chunks_count", 0),
                    "extracted_images_count": result.get("extracted_images_count", 0),
                },
                message=f"成功导入，包含 {result.get('image_chunks_count', 0)} 个图片片段"
            )
        else:
            return error_response(
                message=f"PDF导入失败",
                data={"errors": result.get("errors", [])}
            )

    except Exception as e:
        return error_response(message=f"处理失败: {str(e)}")

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@router.delete("/source/{source_file:path}")
async def delete_by_source(
    source_file: str,
    vlm_enabled: bool = False,
) -> dict:
    """
    删除指定来源的所有片段

    统一响应格式:
        {
            "success": bool,
            "data": {"deleted_count": int},
            "message": str
        }
    """
    from .service import create_multimodal_service

    try:
        service = create_multimodal_service(vlm_enabled=vlm_enabled)
        count = service.delete_by_source(source_file)

        return success_response(
            data={"deleted_count": count},
            message=f"成功删除 {count} 个片段"
        )

    except Exception as e:
        return error_response(message=f"删除失败: {str(e)}")


@router.get("/status/{source_file:path}")
async def get_processing_status(
    source_file: str,
    vlm_enabled: bool = False,
) -> dict:
    """
    获取处理状态

    统一响应格式:
        {
            "success": bool,
            "data": {
                "exists": bool,
                "total_chunks": int,
                "processed": int,
                "failed": int,
                "pending": int
            },
            "message": str
        }
    """
    from .service import create_multimodal_service

    try:
        service = create_multimodal_service(vlm_enabled=vlm_enabled)
        status = service.get_processing_status(source_file)

        return success_response(
            data=status,
            message="状态查询成功" if status.get("exists") else "未找到相关片段"
        )

    except Exception as e:
        return error_response(message=f"查询失败: {str(e)}")
