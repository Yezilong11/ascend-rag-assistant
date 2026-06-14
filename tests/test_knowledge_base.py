"""
测试知识库功能

使用 pytest 运行：
    pytest tests/test_knowledge_base.py -v
"""

import os
import pytest


class TestKnowledgeBase:
    """知识库测试类"""

    def test_init(self):
        """测试知识库初始化"""
        from src.knowledge_base import KnowledgeBase

        kb = KnowledgeBase(persist_dir="./test_chroma_db")

        assert kb is not None
        assert hasattr(kb, 'persist_dir')
        assert kb.persist_dir == "./test_chroma_db"

    def test_ingest_text_file(self, test_knowledge_base, sample_text_file):
        """测试文本文件导入"""
        result = test_knowledge_base.ingest(sample_text_file)

        assert result is True

    def test_similarity_search(self, test_knowledge_base, sample_text_file):
        """测试相似度检索"""
        # 先导入文档
        test_knowledge_base.ingest(sample_text_file)

        # 执行检索
        results = test_knowledge_base.similarity_search("昇腾AI竞赛什么时候报名", k=2)

        assert len(results) > 0
        assert all(hasattr(doc, 'page_content') for doc in results)

    def test_get_docs_count(self, test_knowledge_base, sample_text_file):
        """测试获取文档数量"""
        # 先导入文档
        test_knowledge_base.ingest(sample_text_file)

        # 执行检索验证有文档
        results = test_knowledge_base.similarity_search("昇腾AI竞赛", k=10)
        assert len(results) > 0

    def test_clean_source_path(self):
        """测试源路径清理"""
        from src.rag_engine import clean_source_path

        # Windows 路径
        assert clean_source_path(r"C:\Users\test\file.txt") == "file.txt"
        # Unix 路径
        assert clean_source_path("/home/test/file.txt") == "file.txt"
        # 已经是文件名
        assert clean_source_path("file.txt") == "file.txt"
        # 空值
        assert clean_source_path("") == ""
        # 未知
        assert clean_source_path("未知") == "未知"


class TestKnowledgeBaseDocumentTypes:
    """文档类型测试类"""

    def test_default_document_type(self, test_knowledge_base, sample_text_file):
        """测试默认文档类型"""
        result = test_knowledge_base.ingest(sample_text_file)
        assert result is True

    def test_custom_document_type(self, test_knowledge_base, sample_text_file):
        """测试自定义文档类型"""
        result = test_knowledge_base.ingest(
            sample_text_file,
            doc_type="registration"
        )
        assert result is True
