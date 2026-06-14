"""
Pytest 配置和共享 fixtures
"""

import os
import sys
import pytest
import tempfile
import shutil

# 确保 src 目录在 Python 路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def temp_dir():
    """创建临时目录用于测试"""
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture
def sample_text():
    """测试用样本文本"""
    return """# 昇腾AI竞赛介绍

昇腾AI竞赛是由华为举办的全国性人工智能竞赛，旨在促进AI技术创新和人才培养。

## 报名时间

竞赛报名时间通常为每年的3-4月份。

## 比赛阶段

比赛分为初赛、复赛和决赛三个阶段。

## 竞赛领域

竞赛题目主要聚焦于大模型、计算机视觉、自然语言处理等AI领域。
"""


@pytest.fixture
def sample_text_file(temp_dir, sample_text):
    """创建测试用文本文件"""
    file_path = os.path.join(temp_dir, "test_sample.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(sample_text)
    return file_path


@pytest.fixture
def test_knowledge_base(temp_dir):
    """创建测试用知识库"""
    from src.knowledge_base import KnowledgeBase

    persist_dir = os.path.join(temp_dir, "test_chroma_db")
    kb = KnowledgeBase(persist_dir=persist_dir)
    yield kb

    # 清理
    shutil.rmtree(persist_dir, ignore_errors=True)
