# RAG Engine 模块

> 版本：2.0.0
> 最后更新：2026-05-09

## 概述

RAG（Retrieval-Augmented Generation）引擎模块，提供基于知识库的问答能力。

## 核心组件

### Reranker

重排序器，使用 Cross-Encoder 模型对检索结果进行精排。

```python
from src.rag_engine import Reranker

reranker = Reranker(
    model_name="bge-reranker-v2-m3",
    model_dir="./models"
)
results = reranker.rerank(query, documents, top_k=3)
```

### RAGAssistant

RAG 问答助手，整合检索和生成能力。

```python
from src.rag_engine import RAGAssistant

assistant = RAGAssistant(
    model_key="qwen2-1.5b",
    model_dir="./models",
    knowledge_base=kb
)
result = assistant.query("竞赛报名截止时间是什么时候？")
```

## 配置

### 预定义模型

| Key | 名称 | 描述 |
|-----|------|------|
| `qwen2-1.5b` | Qwen2-1.5B | 标准版，推荐使用 |
| `qwen2-0.5b` | Qwen2-0.5B | 轻量版，适合 CPU |
| `chatglm3-6b` | ChatGLM3-6B | 大模型版 |

### 预定义重排序模型

| Key | 名称 | 描述 | 大小 |
|-----|------|------|------|
| `bge-reranker-v2-m3` | BGE-Reranker-v2-m3 | 推荐，多语言支持 | ~1.2GB |
| `bge-reranker-large` | BGE-Reranker-Large | 效果好，速度快 | ~1.3GB |
| `bge-reranker-base` | BGE-Reranker-Base | 速度快，效果良好 | ~0.6GB |

## 依赖

```bash
pip install torch transformers langchain langchain-huggingface langchain-chroma chromadb sentence-transformers
```

## 相关文档

- [API 接口文档](./API接口文档.md)
- [代码规范](./代码规范.md)
