"""
RAG API 请求/响应模型模块
定义所有 API 端点的 Pydantic 数据模型

模型命名规范：{动作}{资源}Request / {资源}Response
所有响应模型遵循统一结构：{"success": bool, "data": ..., "message": ...}

关联文档：
- API接口文档.md 第 2.1 节 — 统一响应格式
- API接口文档.md 第 4 节 — RAG API 接口定义
- 代码规范.md 第 2.5.2 节 — 请求模型命名规范
"""

from typing import Optional, Dict, Any, Literal, Generic, TypeVar

from pydantic import BaseModel, Field, field_validator

from src.rag_engine import PREDEFINED_MODELS as MODEL_OPTIONS
from src.rag_engine import PREDEFINED_RERANKERS as RERANKER_OPTIONS


PREDEFINED_MODELS = {k: v["name"] for k, v in MODEL_OPTIONS.items()}
PREDEFINED_RERANKERS = {k: v["name"] for k, v in RERANKER_OPTIONS.items()}


# ============================================================================
# 统一响应模型
# ============================================================================

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """
    统一 API 响应模型

    所有 API 端点统一返回此格式，确保前端处理逻辑一致。

    格式：
        {
            "success": bool,      # 操作是否成功
            "data": T,            # 业务数据（可选，success=True 时存在）
            "message": str        # 提示信息（可选）
        }

    示例（成功）：
        {"success": true, "data": {"answer": "..."}, "message": null}

    示例（失败）：
        {"success": false, "data": null, "message": "错误描述"}

    关联文档：API接口文档.md 第 2.1 节 — 统一响应格式
    """

    success: bool = Field(
        description="操作是否成功",
    )
    data: Optional[T] = Field(
        default=None,
        description="业务数据，success=True 时存在",
    )
    message: Optional[str] = Field(
        default=None,
        description="提示信息或错误描述",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"key": "value"},
                "message": None,
            }
        }


def success_response(data: Any = None, message: str = None) -> dict:
    """
    创建成功响应

    Args:
        data: 业务数据
        message: 提示信息（可选）

    Returns:
        统一响应字典
    """
    response = {"success": True}
    if data is not None:
        response["data"] = data
    if message:
        response["message"] = message
    return response


def error_response(message: str, data: Any = None) -> dict:
    """
    创建错误响应

    Args:
        message: 错误信息
        data: 附加数据（可选）

    Returns:
        统一响应字典
    """
    response = {"success": False, "message": message}
    if data is not None:
        response["data"] = data
    return response


class ChatRequest(BaseModel):
    """
    问答请求模型

    用于 POST /api/rag/chat 和 POST /api/rag/chat/stream 接口。
    前端聊天窗口用户输入问题后发送。

    关联接口：API接口文档.md 4.4 普通问答、4.5 流式问答
    """

    question: str = Field(
        min_length=1,
        description="用户问题",
    )


class ModelLoadRequest(BaseModel):
    """
    模型加载请求模型

    用于 POST /api/rag/model/load 接口。
    用户在设置页面选择模型和重排序参数后点击"启动AI引擎"。

    关联接口：API接口文档.md 4.2 加载模型

    字段说明：
        model_key:           必填，预定义模型 key，对应 PREDEFINED_MODELS 字典的键
        model_dir:           本地模型存放目录，默认 "./models"
        use_reranker:        是否启用重排序，默认 True
        reranker_model:      重排序模型 key，对应 PREDEFINED_RERANKERS 字典的键
        reranker_top_k:      重排序后保留的文档数量，范围 1-10
        initial_retrieval_k: 初始检索的文档数量，范围 3-30
    """

    model_key: str = Field(
        description="预定义模型key，如 qwen2-1.5b",
    )
    model_dir: str = Field(
        default="./models",
        description="本地模型存放目录",
    )
    use_reranker: bool = Field(
        default=True,
        description="是否启用重排序",
    )
    reranker_model: str = Field(
        default="bge-reranker-v2-m3",
        description="重排序模型key，如 bge-reranker-v2-m3",
    )
    reranker_top_k: int = Field(
        default=3,
        ge=1,
        le=10,
        description="重排序后保留的文档数量，范围 1-10",
    )
    initial_retrieval_k: int = Field(
        default=10,
        ge=3,
        le=30,
        description="初始检索的文档数量，范围 3-30",
    )

    @field_validator("model_key")
    @classmethod
    def validate_model_key(cls, v: str) -> str:
        if v not in PREDEFINED_MODELS:
            raise ValueError(f"无效的模型key: {v}，可选值: {list(PREDEFINED_MODELS.keys())}")
        return v

    @field_validator("reranker_model")
    @classmethod
    def validate_reranker_model(cls, v: str) -> str:
        if v not in PREDEFINED_RERANKERS:
            raise ValueError(f"无效的重排序模型key: {v}，可选值: {list(PREDEFINED_RERANKERS.keys())}")
        return v


class ModelUnloadResponse(BaseModel):
    """
    模型卸载响应模型

    用于 POST /api/rag/model/unload 接口的响应。
    无论卸载成功或失败，均返回此结构。

    关联接口：API接口文档.md 4.3 卸载模型
    """

    success: bool = Field(
        description="操作是否成功",
    )
    message: str = Field(
        description="操作结果描述",
    )


class StatusResponse(BaseModel):
    """
    系统状态响应模型

    用于 GET /api/rag/status 接口的响应。
    包含引擎加载状态、模型信息、可用模型列表等。

    关联接口：API接口文档.md 4.1 获取系统状态

    data 字段结构（engine_loaded=True 时）：
        {
            "engine_loaded": true,
            "model_key": "qwen2-1.5b",
            "model_name": "Qwen2-1.5B",
            "reranker_enabled": true,
            "reranker_model": "bge-reranker-v2-m3",
            "knowledge_base_ready": true,
            "available_models": { ... },
            "available_rerankers": { ... }
        }
    """

    success: bool = Field(
        description="请求是否成功",
    )
    data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="状态数据，包含引擎状态、模型信息、可用模型列表",
    )


class ChatResponse(BaseModel):
    """
    问答响应模型

    用于 POST /api/rag/chat 接口的响应（非流式）。
    流式问答使用 SSE 事件推送，不使用此模型。

    关联接口：API接口文档.md 4.4 普通问答

    data 字段结构（成功时）：
        {
            "answer": "回答文本",
            "sources": [
                {"content": "来源摘要", "source": "来源路径"}
            ]
        }
    """

    success: bool = Field(
        description="请求是否成功",
    )
    data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="问答结果，包含 answer 和 sources",
    )
    message: Optional[str] = Field(
        default=None,
        description="错误信息，仅在 success=false 时存在",
    )


class IngestResponse(BaseModel):
    """
    文档导入响应模型

    用于 POST /api/rag/ingest 和 POST /api/rag/knowledge-base/auto-ingest 接口的响应。

    关联接口：API接口文档.md 4.6 上传文档、4.7 自动导入知识库

    data 字段结构（上传文档成功时）：
        {
            "filename": "文件名.md",
            "doc_type": "registration",
            "chunks_count": 12
        }

    data 字段结构（自动导入成功时）：
        {
            "total_files": 64,
            "success_count": 62,
            "failed_count": 2
        }
    """

    success: bool = Field(
        description="操作是否成功",
    )
    data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="导入结果数据",
    )
    message: Optional[str] = Field(
        default=None,
        description="错误或提示信息",
    )
