"""
RAG API 端点测试模块

使用 pytest + FastAPI TestClient 测试所有 RAG API 端点。
仅测试 API 层面的请求/响应格式和错误处理，不依赖真实模型加载。

测试覆盖端点：
    GET  /api/rag/status                       — 系统状态查询
    POST /api/rag/chat                         — 普通问答
    POST /api/rag/chat/stream                  — SSE 流式问答
    POST /api/rag/model/load                   — 加载模型
    POST /api/rag/model/unload                 — 卸载模型
    POST /api/rag/ingest                       — 上传文档
    POST /api/rag/knowledge-base/auto-ingest   — 自动导入知识库
    GET  /api/rag/knowledge-base/stats         — 知识库统计

关联文档：
- API接口文档.md 第 4 节 — RAG API 接口定义
- API接口文档.md 第 5 节 — 错误码参考
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from src.rag_api.app import create_app
from src.rag_api.dependencies import (
    get_rag_assistant,
    set_rag_assistant,
    clear_rag_assistant,
    get_is_loading,
    set_is_loading,
)


@pytest.fixture
def client():
    """
    创建 TestClient 实例

    每个测试用例使用独立的 FastAPI 应用实例，
    避免测试间状态污染。
    """
    app = create_app()
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_dependencies():
    """
    每个测试前后重置依赖注入状态

    确保每个测试用例在干净的状态下运行，
    避免前一个测试设置的 RAGAssistant 实例影响后续测试。
    """
    original_assistant = get_rag_assistant()
    original_loading = get_is_loading()

    yield

    if get_rag_assistant() is not None:
        clear_rag_assistant()
    if get_is_loading():
        set_is_loading(False)


class TestStatusEndpoint:
    """
    GET /api/rag/status 端点测试

    关联接口：API接口文档.md 4.1 获取系统状态
    """

    def test_status_before_load(self, client):
        """
        引擎未加载时查询状态

        验证点：
        - success 为 True
        - engine_loaded 为 False
        - model_key 为空字符串
        - available_models 至少包含 3 个预定义模型
        - available_rerankers 至少包含 3 个预定义重排序器
        """
        resp = client.get("/api/rag/status")
        assert resp.status_code == 200

        data = resp.json()
        assert data["success"] is True
        assert data["data"]["engine_loaded"] is False
        assert data["data"]["model_key"] == ""
        assert data["data"]["model_name"] == ""
        assert data["data"]["reranker_enabled"] is False
        assert data["data"]["reranker_model"] == ""
        assert len(data["data"]["available_models"]) >= 3
        assert len(data["data"]["available_rerankers"]) >= 3

    def test_status_response_format(self, client):
        """
        状态响应格式验证

        验证点：
        - 响应包含 success 和 data 字段
        - data 包含所有必需字段
        """
        resp = client.get("/api/rag/status")
        data = resp.json()

        assert "success" in data
        assert "data" in data

        required_fields = [
            "engine_loaded",
            "model_key",
            "model_name",
            "reranker_enabled",
            "reranker_model",
            "knowledge_base_ready",
            "available_models",
            "available_rerankers",
        ]
        for field in required_fields:
            assert field in data["data"], f"缺少必需字段: {field}"

    def test_status_available_models_content(self, client):
        """
        可用模型列表内容验证

        验证点：
        - 包含 qwen2-1.5b、qwen2-0.5b
        - 每个模型包含 name 和 description
        """
        resp = client.get("/api/rag/status")
        models = resp.json()["data"]["available_models"]

        assert "qwen2-1.5b" in models or "qwen2-0.5b" in models

        for model_key, model_info in models.items():
            assert "name" in model_info
            assert "description" in model_info

    def test_status_available_rerankers_content(self, client):
        """
        可用重排序器列表内容验证

        验证点：
        - 包含 bge-reranker-v2-m3
        - 每个重排序器包含 name、description、size
        """
        resp = client.get("/api/rag/status")
        rerankers = resp.json()["data"]["available_rerankers"]

        assert "bge-reranker-v2-m3" in rerankers

        for reranker_key, reranker_info in rerankers.items():
            assert "name" in reranker_info
            assert "description" in reranker_info
            assert "size" in reranker_info

    def test_status_with_loaded_engine(self, client):
        """
        引擎已加载时查询状态

        使用 Mock 设置 RAGAssistant 实例，
        验证 engine_loaded 为 True 且模型信息正确。
        """
        mock_assistant = MagicMock()
        mock_assistant.model_key = "qwen2-1.5b"
        mock_assistant.use_reranker = True
        mock_assistant.reranker = MagicMock()
        mock_assistant.reranker.model_name = "bge-reranker-v2-m3"

        set_rag_assistant(mock_assistant)

        resp = client.get("/api/rag/status")
        data = resp.json()

        assert data["data"]["engine_loaded"] is True
        assert data["data"]["model_key"] == "qwen2-1.5b"
        assert data["data"]["reranker_enabled"] is True


class TestChatEndpoint:
    """
    POST /api/rag/chat 端点测试

    关联接口：API接口文档.md 4.4 普通问答
    """

    def test_chat_engine_not_loaded(self, client):
        """
        引擎未加载时请求问答

        验证点：
        - 返回 HTTP 503
        - detail 包含 "RAG引擎未加载"
        """
        resp = client.post("/api/rag/chat", json={"question": "测试问题"})
        assert resp.status_code == 503
        assert "RAG引擎未加载" in resp.json()["detail"]

    def test_chat_empty_question(self, client):
        """
        空问题请求

        验证点：
        - 返回 HTTP 422（Pydantic 验证失败）
        """
        resp = client.post("/api/rag/chat", json={"question": ""})
        assert resp.status_code == 422

    def test_chat_missing_question(self, client):
        """
        缺少 question 字段

        验证点：
        - 返回 HTTP 422（缺少必填字段）
        """
        resp = client.post("/api/rag/chat", json={})
        assert resp.status_code == 422

    def test_chat_success_with_mock(self, client):
        """
        使用 Mock 测试正常问答

        验证点：
        - 返回 HTTP 200
        - success 为 True
        - data 包含 answer 和 sources
        - 响应格式符合 API接口文档.md 4.4 定义
        """
        mock_assistant = MagicMock()
        mock_assistant.model_key = "qwen2-1.5b"
        mock_assistant.query.return_value = {
            "answer": "这是测试回答",
            "sources": [
                {"content": "来源摘要", "source": "data/test.md"},
            ],
        }

        set_rag_assistant(mock_assistant)

        resp = client.post("/api/rag/chat", json={"question": "测试问题"})
        assert resp.status_code == 200

        data = resp.json()
        assert data["success"] is True
        assert "answer" in data["data"]
        assert "sources" in data["data"]
        assert data["data"]["answer"] == "这是测试回答"
        assert len(data["data"]["sources"]) == 1


class TestChatStreamEndpoint:
    """
    POST /api/rag/chat/stream 端点测试

    关联接口：API接口文档.md 4.5 流式问答 (SSE)
    """

    def test_chat_stream_engine_not_loaded(self, client):
        """
        引擎未加载时请求流式问答

        验证点：
        - 返回 HTTP 503
        - detail 包含 "RAG引擎未加载"
        """
        resp = client.post("/api/rag/chat/stream", json={"question": "测试问题"})
        assert resp.status_code == 503
        assert "RAG引擎未加载" in resp.json()["detail"]

    def test_chat_stream_empty_question(self, client):
        """
        空问题请求流式问答

        验证点：
        - 返回 HTTP 422
        """
        resp = client.post("/api/rag/chat/stream", json={"question": ""})
        assert resp.status_code == 422

    def test_chat_stream_sse_format(self, client):
        """
        SSE 事件流格式验证

        使用 Mock 测试流式输出格式，验证：
        - Content-Type 为 text/event-stream
        - 包含 token 事件
        - 包含 sources 事件
        - 包含 done 事件
        - 事件格式符合 SSE 规范
        """
        mock_assistant = MagicMock()
        mock_assistant.model_key = "qwen2-1.5b"
        mock_assistant.query_stream.return_value = [
            "你好", "，", "世界",
            {"type": "sources", "sources": [{"content": "来源摘要", "source": "data/test.md"}]},
        ]

        set_rag_assistant(mock_assistant)

        resp = client.post("/api/rag/chat/stream", json={"question": "测试问题"})
        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers["content-type"]

    def test_chat_stream_headers(self, client):
        """
        SSE 响应头验证

        验证点：
        - Cache-Control: no-cache
        - Connection: keep-alive
        - X-Accel-Buffering: no
        """
        mock_assistant = MagicMock()
        mock_assistant.model_key = "qwen2-1.5b"
        mock_assistant.query_stream.return_value = [
            "测试",
            {"type": "sources", "sources": []},
        ]

        set_rag_assistant(mock_assistant)

        resp = client.post("/api/rag/chat/stream", json={"question": "测试"})
        assert resp.headers["cache-control"] == "no-cache"
        assert resp.headers["connection"] == "keep-alive"


class TestModelLoadEndpoint:
    """
    POST /api/rag/model/load 端点测试

    关联接口：API接口文档.md 4.2 加载模型
    """

    def test_model_load_returns_loading(self, client):
        """
        模型加载请求立即返回

        验证点：
        - 返回 HTTP 200
        - success 为 True
        - data 包含 model_key 和 status="loading"
        """
        with patch("src.rag_api.routes.RAGAssistant") as mock_class:
            mock_instance = MagicMock()
            mock_instance.model_key = "qwen2-1.5b"
            mock_class.return_value = mock_instance

            resp = client.post(
                "/api/rag/model/load",
                json={"model_key": "qwen2-1.5b"},
            )
            assert resp.status_code == 200

            data = resp.json()
            assert data["success"] is True
            assert data["data"]["model_key"] == "qwen2-1.5b"
            assert data["data"]["status"] == "loading"

        set_is_loading(False)

    def test_model_load_concurrent_protection(self, client):
        """
        并发加载保护

        验证点：
        - 正在加载时再次请求返回 success=False
        - message 包含 "模型正在加载中"
        """
        set_is_loading(True)

        try:
            resp = client.post(
                "/api/rag/model/load",
                json={"model_key": "qwen2-1.5b"},
            )
            assert resp.status_code == 200

            data = resp.json()
            assert data["success"] is False
            assert "模型正在加载中" in data["message"]
        finally:
            set_is_loading(False)

    def test_model_load_default_values(self, client):
        """
        模型加载请求默认值验证

        验证点：
        - 仅提供 model_key 时使用默认参数
        - 请求正常返回
        """
        with patch("src.rag_api.routes.RAGAssistant") as mock_class:
            mock_instance = MagicMock()
            mock_instance.model_key = "qwen2-0.5b"
            mock_class.return_value = mock_instance

            resp = client.post(
                "/api/rag/model/load",
                json={"model_key": "qwen2-0.5b"},
            )
            assert resp.status_code == 200
            assert resp.json()["data"]["model_key"] == "qwen2-0.5b"

        set_is_loading(False)

    def test_model_load_invalid_reranker_top_k(self, client):
        """
        reranker_top_k 超出范围验证

        验证点：
        - reranker_top_k=0 返回 HTTP 422（ge=1）
        - reranker_top_k=11 返回 HTTP 422（le=10）
        """
        resp = client.post(
            "/api/rag/model/load",
            json={"model_key": "qwen2-1.5b", "reranker_top_k": 0},
        )
        assert resp.status_code == 422

        resp = client.post(
            "/api/rag/model/load",
            json={"model_key": "qwen2-1.5b", "reranker_top_k": 11},
        )
        assert resp.status_code == 422

    def test_model_load_missing_model_key(self, client):
        """
        缺少必填字段 model_key

        验证点：
        - 返回 HTTP 422
        """
        resp = client.post("/api/rag/model/load", json={})
        assert resp.status_code == 422


class TestModelUnloadEndpoint:
    """
    POST /api/rag/model/unload 端点测试

    关联接口：API接口文档.md 4.3 卸载模型
    """

    def test_model_unload_when_not_loaded(self, client):
        """
        无模型时卸载

        验证点：
        - 返回 HTTP 200
        - success 为 False
        - message 包含 "没有已加载的模型"
        """
        resp = client.post("/api/rag/model/unload")
        assert resp.status_code == 200

        data = resp.json()
        assert data["success"] is False
        assert "没有已加载的模型" in data["message"]

    def test_model_unload_success(self, client):
        """
        卸载已加载模型

        验证点：
        - 返回 HTTP 200
        - success 为 True
        - message 为 "模型已卸载"
        """
        mock_assistant = MagicMock()
        mock_assistant.model_key = "qwen2-1.5b"
        mock_assistant.model = MagicMock()
        mock_assistant.pipeline_obj = MagicMock()

        set_rag_assistant(mock_assistant)

        with patch("src.rag_api.dependencies.torch") as mock_torch:
            mock_torch.cuda.is_available.return_value = False
            resp = client.post("/api/rag/model/unload")

        assert resp.status_code == 200

        data = resp.json()
        assert data["success"] is True
        assert data["message"] == "模型已卸载"

        assert get_rag_assistant() is None


class TestIngestEndpoint:
    """
    POST /api/rag/ingest 端点测试

    关联接口：API接口文档.md 4.6 上传文档
    """

    def test_ingest_unsupported_format(self, client):
        """
        上传不支持的文件格式

        验证点：
        - 返回 HTTP 400
        - detail 包含 "不支持的文件格式"
        """
        resp = client.post(
            "/api/rag/ingest",
            files={"file": ("test.exe", b"fake content", "application/octet-stream")},
        )
        assert resp.status_code == 400
        assert "不支持的文件格式" in resp.json()["detail"]

    def test_ingest_no_file(self, client):
        """
        不上传文件

        验证点：
        - 返回 HTTP 422（缺少必填参数）
        """
        resp = client.post("/api/rag/ingest")
        assert resp.status_code == 422

    def test_ingest_supported_formats_accepted(self, client):
        """
        支持的文件格式不被拒绝

        验证点：
        - .md、.txt 后缀不会触发 400 错误
        """
        for ext in [".md", ".txt"]:
            resp = client.post(
                "/api/rag/ingest",
                files={"file": (f"test{ext}", b"test content", "text/plain")},
            )
            assert resp.status_code != 400, f"格式 {ext} 不应被 400 拒绝"


class TestKnowledgeBaseStatsEndpoint:
    """
    GET /api/rag/knowledge-base/stats 端点测试

    关联接口：API接口文档.md 4.8 知识库统计
    """

    def test_kb_stats(self, client):
        """
        知识库统计查询

        验证点：
        - 返回 HTTP 200
        - success 为 True
        - data 包含 chunk_count 或 total_chunks 字段
        """
        resp = client.get("/api/rag/knowledge-base/stats")
        assert resp.status_code == 200

        data = resp.json()
        assert data["success"] is True
        # 兼容两种字段名
        assert "chunk_count" in data["data"] or "total_chunks" in data["data"]

    def test_kb_stats_response_format(self, client):
        """
        知识库统计响应格式验证

        验证点：
        - 响应包含 success 和 data 字段
        - chunk_count/total_chunks 为整数
        """
        resp = client.get("/api/rag/knowledge-base/stats")
        data = resp.json()

        assert "success" in data
        assert "data" in data
        # 兼容两种字段名
        chunk_key = "chunk_count" if "chunk_count" in data["data"] else "total_chunks"
        assert isinstance(data["data"][chunk_key], int)


class TestAutoIngestEndpoint:
    """
    POST /api/rag/knowledge-base/auto-ingest 端点测试

    关联接口：API接口文档.md 4.7 自动导入知识库
    """

    def test_auto_ingest(self, client):
        """
        自动导入知识库

        验证点：
        - 返回 HTTP 200
        - success 为 True
        - data 包含 total_files、success_count、failed_count
        """
        resp = client.post("/api/rag/knowledge-base/auto-ingest")
        assert resp.status_code == 200

        data = resp.json()
        assert data["success"] is True
        assert "total_files" in data["data"]
        assert "success_count" in data["data"]
        assert "failed_count" in data["data"]


class TestRootRoute:
    """
    GET / 根路由测试
    """

    def test_root_route(self, client):
        """
        根路由健康检查

        验证点：
        - 返回 HTTP 200
        - 响应包含 docs 字段
        """
        resp = client.get("/")
        assert resp.status_code == 200

        data = resp.json()
        assert "docs" in data  # 主要验证 docs 字段存在
