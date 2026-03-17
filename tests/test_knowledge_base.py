"""测试知识库功能"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.knowledge_base import KnowledgeBase  # noqa: E402


def test_init():
    """测试初始化"""
    print("Testing KnowledgeBase initialization...")
    kb = KnowledgeBase(persist_dir="./test_chroma_db")
    print("OK: Initialization successful")
    return kb


def test_import_file():
    """测试文件导入"""
    print("\nTesting file import...")

    # 创建一个简单的测试文件
    test_content = """# 昇腾AI竞赛介绍

昇腾AI竞赛是由华为举办的全国性人工智能竞赛，旨在促进AI技术创新和人才培养。

竞赛报名时间通常为每年的3-4月份，比赛分为初赛、复赛和决赛三个阶段。

竞赛题目主要聚焦于大模型、计算机视觉、自然语言处理等AI领域。
"""

    test_file = "test_sample.txt"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(test_content)

    kb = test_init()
    result = kb.ingest(test_file)

    # 清理测试文件
    os.remove(test_file)

    if result:
        print("OK: File import successful")

    return kb


def test_search():
    """测试相似度检索"""
    print("\nTesting similarity search...")

    kb = test_import_file()
    results = kb.similarity_search("昇腾AI竞赛什么时候报名", k=2)

    print(f"OK: Found {len(results)} results")
    for i, doc in enumerate(results, 1):
        print(f"\nResult {i}:\n{doc.page_content}")


if __name__ == "__main__":
    test_search()
