# 修复文档数统计错误问题

## 问题描述
用户只上传了一个文件，但文档数和分块数都显示为八千多，且两者相等。

## 根本原因分析

在 `src/rag_api/routes.py` 第537行，错误地将分块总数当作文档数量：

```python
document_count = text_chunk_count + multimodal_chunk_count
```

这导致：
- 如果主知识库有8000多个文本分块
- 那么 document_count 也显示为8000多
- 但实际上可能只有几百篇文档

## 解决方案

### 方案：修正 document_count 计算逻辑

将 `document_count` 改为只使用 `text_chunk_count`，因为之前的实现中 document_count 和 chunk_count 本质上是等价的（都指文本分块）。

**修改文件**: `src/rag_api/routes.py`

```python
# 修改第537行
document_count = text_chunk_count  # 不再累加 multimodal_chunk_count
```

或者更好的方案是：分别返回文本文档数和多模态文档数，但需要更复杂的实现。

---

## 实施步骤

| 步骤 | 文件 | 操作 |
|------|------|------|
| 1 | src/rag_api/routes.py | 修改 document_count 计算逻辑 |

## 验证方法

1. 检查统计接口返回的 document_count 是否合理
2. 确认文档数应该远小于分块数
