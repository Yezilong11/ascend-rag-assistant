#!/usr/bin/env python3
"""
测试 KnowledgeBase 切分策略的输出结果
"""

import os
import sys
import re
from typing import List, Dict

# 添加 src 目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.knowledge_base import KnowledgeBase

# 兼容不同版本的 Document 导入
try:
    from langchain_core.documents import Document
except ImportError:
    from langchain.schema import Document

# 简化的测试类，只包含切分方法
class TestSplitter:
    def __init__(self):
        # 复制 KnowledgeBase 的配置
        self.TYPE_CONFIGS = KnowledgeBase.TYPE_CONFIGS
        self.DEFAULT_CONFIG = KnowledgeBase.DEFAULT_CONFIG

    def split_document(self, text: str, doc_type: str, source: str) -> List[Document]:
        """直接调用 KnowledgeBase 的 split_document 方法"""
        return self._split_document_logic(text, doc_type, source)

    def _split_document_logic(self, text: str, doc_type: str, source: str) -> List[Document]:
        """复制 KnowledgeBase 的切分逻辑"""
        from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter

        config = self.TYPE_CONFIGS.get(doc_type, self.DEFAULT_CONFIG)
        base_metadata = {"source": source, "doc_type": doc_type}

        # 1. 如果是FAQ且启用按问答对切分
        if config.get("split_by_qa", False):
            qa_chunks = self._split_by_qa(text, base_metadata)
            if qa_chunks:
                return qa_chunks

        # 2. 保护原子元素（表格、代码块）
        keep_tables = config.get("keep_tables", True)
        keep_code = config.get("keep_code_blocks", True)
        protected_text, placeholders = self._protect_atomic_elements(text, keep_tables, keep_code)

        # 3. 按标题切分
        headers = config.get("split_by_headers", [])
        if headers:
            header_map = {"h1": "#", "h2": "##", "h3": "###", "h4": "####"}
            splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[(header_map[h], h) for h in headers])
            splits = splitter.split_text(protected_text)
            for split in splits:
                split.metadata.update(base_metadata)
        else:
            splits = [Document(page_content=protected_text, metadata=base_metadata)]

        # 4. 对每个块进一步按长度切分
        final_chunks = []
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.get("chunk_size", 800),
            chunk_overlap=config.get("chunk_overlap", 150),
            separators=config.get("separators", self.DEFAULT_CONFIG["separators"])
        )
        for split in splits:
            if len(split.page_content) > config.get("chunk_size", 800) * 1.2:
                sub_chunks = text_splitter.split_documents([split])
                final_chunks.extend(sub_chunks)
            else:
                final_chunks.append(split)

        # 5. 若配置了拆分列表项
        if config.get("split_lists", False):
            expanded = []
            for chunk in final_chunks:
                list_chunks = self._split_list_items(chunk)
                expanded.extend(list_chunks)
            final_chunks = expanded

        # 6. 恢复原子元素
        final_chunks = self._restore_atomic_elements(final_chunks, placeholders)

        return final_chunks

    def _split_by_qa(self, text: str, metadata: Dict) -> List[Document]:
        """按问答对切分FAQ文本"""
        qa_patterns = [
            re.compile(r'(?m)^#{1,3}\s*Q\d*[：:]\s*(.*?)\nA[：:]\s*(.*?)(?=\n#{1,3}\s*Q|\Z)', re.DOTALL),
            re.compile(r'(?m)\*\*Q[：:]\*\*\s*(.*?)\nA[：:]\s*(.*?)(?=\n\*\*Q|\Z)', re.DOTALL)
        ]
        chunks = []
        for pattern in qa_patterns:
            for match in pattern.finditer(text):
                q = match.group(1).strip()
                a = match.group(2).strip()
                content = f"**Q：{q}**\nA：{a}"
                new_meta = metadata.copy()
                new_meta["question"] = q
                new_meta["answer"] = a
                chunks.append(Document(page_content=content, metadata=new_meta))
            if chunks:
                break
        return chunks

    def _protect_atomic_elements(self, text: str, keep_tables: bool, keep_code: bool) -> tuple:
        """保护表格和代码块"""
        placeholders = []
        if keep_code:
            def replace_code(match):
                idx = len(placeholders)
                placeholders.append({"type": "code", "content": match.group(0)})
                return f"__PLACEHOLDER_{idx}__"
            text = re.sub(r'```.*?```', replace_code, text, flags=re.DOTALL)
        if keep_tables:
            def replace_table(match):
                idx = len(placeholders)
                placeholders.append({"type": "table", "content": match.group(0)})
                return f"__PLACEHOLDER_{idx}__"
            text = re.sub(r'(\|.*\|\n\|[-: |]+\|\n(\|.*\|\n?)+)', replace_table, text, flags=re.MULTILINE)
        return text, placeholders

    def _restore_atomic_elements(self, chunks: List[Document], placeholders: List[Dict]) -> List[Document]:
        """恢复占位符"""
        for chunk in chunks:
            for i, placeholder in enumerate(placeholders):
                chunk.page_content = chunk.page_content.replace(f"__PLACEHOLDER_{i}__", placeholder["content"])
        return chunks

    def _split_list_items(self, chunk: Document) -> List[Document]:
        """将列表项拆分为独立块"""
        lines = chunk.page_content.split('\n')
        list_items = []
        current_item = []
        in_list = False
        for line in lines:
            if re.match(r'^\s*(\d+\.|\-|\*)\s+', line):
                if current_item:
                    list_items.append("\n".join(current_item))
                current_item = [line]
                in_list = True
            else:
                if in_list:
                    current_item.append(line)
                else:
                    pass
        if current_item:
            list_items.append("\n".join(current_item))
        if not list_items:
            return [chunk]
        new_chunks = []
        for item in list_items:
            new_meta = chunk.metadata.copy()
            new_chunks.append(Document(page_content=item.strip(), metadata=new_meta))
        return new_chunks

def test_splitting_strategy():
    """测试不同文档类型的切分策略"""

    # 使用测试类
    splitter = TestSplitter()

    # 测试文本样例
    test_cases = [
        {
            "name": "FAQ文档",
            "doc_type": KnowledgeBase.TYPE_FAQ,
            "text": """### Q1: 如何报名参赛？
A: 参赛者需要登录官方网站，填写报名信息并提交相关材料。

### Q2: 比赛时间是什么时候？
A: 比赛时间为2024年5月1日至5月31日。

### Q3: 参赛费用多少？
A: 本次比赛免收参赛费用。
"""
        },
        {
            "name": "技术文档",
            "doc_type": KnowledgeBase.TYPE_TECH_DOC,
            "text": """## 1. 引言

本技术文档介绍了系统架构和使用方法。

### 1.1 系统概述

系统采用微服务架构，主要包含以下组件：
- 用户服务
- 订单服务
- 支付服务

## 2. 安装指南

### 2.1 环境要求

- Python 3.8+
- Docker 20.0+

### 2.2 安装步骤

1. 克隆代码库
2. 安装依赖
3. 运行服务
"""
        },
        {
            "name": "历史赛题集",
            "doc_type": KnowledgeBase.TYPE_HISTORY,
            "text": """## 2023年赛题

### 题目1：智能家居系统设计
要求：设计一个基于物联网的智能家居系统

### 题目2：机器人路径规划
要求：实现机器人自主导航算法

### 题目3：数据可视化应用
要求：开发数据分析可视化工具

## 2022年赛题

### 题目1：电商推荐系统
要求：构建个性化推荐算法
"""
        },
        {
            "name": "竞赛规则",
            "doc_type": KnowledgeBase.TYPE_RULES,
            "text": """## 竞赛规则

### 参赛资格
1. 全日制在校大学生
2. 具有良好的编程基础
3. 团队成员不超过3人

### 比赛流程
1. 初赛：在线笔试
2. 复赛：项目开发
3. 决赛：现场答辩

### 评分标准
- 创新性：30%
- 技术难度：25%
- 完成度：25%
- 演示效果：20%
"""
        }
    ]

    print("=" * 60)
    print("KnowledgeBase 切分策略测试")
    print("=" * 60)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. 测试案例：{test_case['name']}")
        print("-" * 40)

        # 调用切分方法
        chunks = splitter.split_document(
            text=test_case['text'],
            doc_type=test_case['doc_type'],
            source=f"test_{test_case['doc_type']}.md"
        )

        print(f"文档类型：{test_case['doc_type']}")
        print(f"切分结果：{len(chunks)} 个片段")
        print()

        # 显示每个片段
        for j, chunk in enumerate(chunks, 1):
            print(f"片段 {j}:")
            print(f"  内容长度：{len(chunk.page_content)} 字符")
            print(f"  元数据：{chunk.metadata}")
            print(f"  内容预览：{chunk.page_content[:200]}{'...' if len(chunk.page_content) > 200 else ''}")
            print()

        print("-" * 40)

def test_custom_text():
    """测试自定义文本的切分"""

    # 使用与上面相同的测试类
    splitter = TestSplitter()

    # 让用户输入自定义文本进行测试
    print("\n" + "=" * 60)
    print("自定义文本测试")
    print("=" * 60)

    custom_text = input("请输入要测试的文本（直接回车使用默认文本）:").strip()

    if not custom_text:
        custom_text = """## 人工智能发展趋势

### 1. 机器学习
机器学习是AI的核心技术之一。

#### 1.1 监督学习
监督学习需要标注数据。

#### 1.2 无监督学习
无监督学习不需要标注数据。

### 2. 深度学习
深度学习使用神经网络。

### 3. 自然语言处理
NLP是AI的重要分支。

#### 3.1 文本分类
文本分类是基础任务。

#### 3.2 机器翻译
机器翻译连接不同语言。
"""

    doc_types = [
        ("FAQ", KnowledgeBase.TYPE_FAQ),
        ("技术文档", KnowledgeBase.TYPE_TECH_DOC),
        ("历史赛题", KnowledgeBase.TYPE_HISTORY),
        ("竞赛规则", KnowledgeBase.TYPE_RULES),
        ("未知类型", KnowledgeBase.TYPE_UNKNOWN)
    ]

    print(f"\n测试文本：\n{custom_text}\n")

    for name, doc_type in doc_types:
        print(f"\n--- 使用 {name} 类型的切分策略 ---")
        chunks = splitter.split_document(custom_text, doc_type, "custom_test.md")

        print(f"切分结果：{len(chunks)} 个片段")

        for j, chunk in enumerate(chunks, 1):
            print(f"\n片段 {j}:")
            print(f"内容：{chunk.page_content}")
            print(f"元数据：{chunk.metadata}")

if __name__ == "__main__":
    try:
        test_splitting_strategy()
        test_custom_text()
    except Exception as e:
        print(f"测试过程中出现错误：{e}")
        import traceback
        traceback.print_exc()