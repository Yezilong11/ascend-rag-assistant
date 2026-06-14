"""
测试 API 响应模型

使用 pytest 运行：
    pytest tests/test_api_models.py -v
"""

import pytest


class TestApiResponse:
    """统一 API 响应模型测试"""

    def test_success_response_creation(self):
        """测试成功响应创建"""
        from src.rag_api.models import success_response

        # 无数据
        response = success_response()
        assert response["success"] is True
        assert "data" not in response
        assert "message" not in response

        # 带数据
        response = success_response(data={"key": "value"})
        assert response["success"] is True
        assert response["data"] == {"key": "value"}

        # 带消息
        response = success_response(message="操作成功")
        assert response["success"] is True
        assert response["message"] == "操作成功"

        # 带数据和消息
        response = success_response(data={"id": 1}, message="创建成功")
        assert response["success"] is True
        assert response["data"] == {"id": 1}
        assert response["message"] == "创建成功"

    def test_error_response_creation(self):
        """测试错误响应创建"""
        from src.rag_api.models import error_response

        # 基本错误 - data 为 None 时不应包含 data 键
        response = error_response("发生错误")
        assert response["success"] is False
        assert response["message"] == "发生错误"
        assert "data" not in response  # data 为 None 时不包含该键

        # 带附加数据
        response = error_response("验证失败", data={"field": "name"})
        assert response["success"] is False
        assert response["message"] == "验证失败"
        assert response["data"] == {"field": "name"}

    def test_api_response_model(self):
        """测试 ApiResponse 模型"""
        from src.rag_api.models import ApiResponse

        # 创建成功响应
        response = ApiResponse(
            success=True,
            data={"answer": "测试答案"},
            message=None
        )
        assert response.success is True
        assert response.data == {"answer": "测试答案"}
        assert response.message is None

        # 创建失败响应
        response = ApiResponse(
            success=False,
            data=None,
            message="未找到资源"
        )
        assert response.success is False
        assert response.data is None
        assert response.message == "未找到资源"


class TestChatRequest:
    """聊天请求模型测试"""

    def test_chat_request_creation(self):
        """测试聊天请求创建"""
        from src.rag_api.models import ChatRequest

        request = ChatRequest(question="什么是昇腾AI？")
        assert request.question == "什么是昇腾AI？"

    def test_chat_request_validation(self):
        """测试聊天请求验证"""
        from src.rag_api.models import ChatRequest
        from pydantic import ValidationError

        # 空问题应验证失败
        with pytest.raises(ValidationError):
            ChatRequest(question="")

        # 有效问题
        request = ChatRequest(question="测试问题")
        assert request.question == "测试问题"


class TestModelLoadRequest:
    """模型加载请求测试"""

    def test_valid_model_load_request(self):
        """测试有效模型加载请求"""
        from src.rag_api.models import ModelLoadRequest

        request = ModelLoadRequest(
            model_key="qwen2-1.5b",
            model_dir="./models",
            use_reranker=True,
            reranker_model="bge-reranker-v2-m3"
        )

        assert request.model_key == "qwen2-1.5b"
        assert request.use_reranker is True
        assert request.reranker_top_k == 3  # 默认值

    def test_invalid_model_key(self):
        """测试无效模型 key"""
        from src.rag_api.models import ModelLoadRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ModelLoadRequest(model_key="invalid-model")

    def test_invalid_reranker_model(self):
        """测试无效重排序模型"""
        from src.rag_api.models import ModelLoadRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ModelLoadRequest(
                model_key="qwen2-1.5b",
                reranker_model="invalid-reranker"
            )

    def test_reranker_top_k_range(self):
        """测试 reranker_top_k 范围验证"""
        from src.rag_api.models import ModelLoadRequest
        from pydantic import ValidationError

        # 超出范围应失败
        with pytest.raises(ValidationError):
            ModelLoadRequest(
                model_key="qwen2-1.5b",
                reranker_top_k=20  # 超过最大值 10
            )
