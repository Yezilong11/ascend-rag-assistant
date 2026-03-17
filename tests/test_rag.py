"""测试RAG问答引擎"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.knowledge_base import KnowledgeBase  # noqa: E402
from src.rag_engine import RAGAssistant  # noqa: E402


# 初始化
kb = KnowledgeBase()
assistant = RAGAssistant(kb)

# 测试问答
test_questions = [
    "昇腾AI竞赛的报名截止日期是什么时候？",
    "如何配置昇腾910B环境？",
    "竞赛评分标准是什么？"
]

for q in test_questions:
    print(f"\n问题: {q}")
    result = assistant.query(q)
    print(f"答案: {result['answer']}")
    print(f"来源: {len(result['sources'])} 个文档片段")
