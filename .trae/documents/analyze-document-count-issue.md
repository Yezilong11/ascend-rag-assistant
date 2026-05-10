# 多模态知识库文档数异常分析计划

## 问题现象
用户上传了一个文件，但系统显示文档数为三百多。

## 根本原因分析

### 1. 统计逻辑
`document_count` 是根据 Chroma 数据库中**唯一的 `source` 元数据数量**来计算的。

### 2. data/ 目录内容
经过检查，`data/` 目录下包含 **375 个文件**：
- 评分标准
- 报名须知
- 常见问题FAQ
- 技术文档
- 竞赛规则
- 历史赛题集

### 3. 自动导入机制
当用户点击"自动导入知识库"时，系统会：
1. 扫描 `data/` 目录下所有支持的文件格式（.pdf, .txt, .md, .docx, .png, .jpg 等）
2. 对每个文件进行分块处理
3. 存储到 Chroma 数据库

### 4. 结论
用户看到的"三百多"文档数，**不是用户上传的文件数量**，而是 `data/` 目录下**已被导入的唯一源文件数量**。

## 解决方案

### 方案1：区分"系统已有文档"和"用户上传文档"

修改统计接口，增加用户上传文件的独立计数：

```python
@router.get("/knowledge-base/stats")
async def knowledge_base_stats() -> dict:
    kb = get_knowledge_base()
    text_chunk_count = 0
    document_count = 0
    multimodal_chunk_count = 0
    uploaded_count = 0

    try:
        collection = kb.db._collection
        text_chunk_count = collection.count()

        # 获取唯一文档数
        all_data = collection.get(include=["metadatas"])
        unique_sources = set()
        uploaded_sources = set()
        for metadata in all_data["metadatas"]:
            if metadata and "source" in metadata:
                source = metadata["source"]
                unique_sources.add(source)
                # 用户上传的文件通常有特定标识
                if "_uploaded_" in source or "temp" in source.lower():
                    uploaded_sources.add(source)
        document_count = len(unique_sources)
        uploaded_count = len(uploaded_sources)

    except Exception:
        pass

    # 多模态统计...

    return {
        "success": True,
        "data": {
            "document_count": document_count,
            "uploaded_document_count": uploaded_count,  # 新增
            "system_document_count": document_count - uploaded_count,  # 新增
            "chunk_count": text_chunk_count,
            "image_chunk_count": multimodal_chunk_count,
            "status": "ready" if kb else "initializing",
        },
    }
```

### 方案2：在前端明确区分"系统文档"和"上传文档"

修改前端显示，添加说明文字：
- 系统文档数：自动导入的 data/ 目录文档
- 上传文档数：用户手动上传的文档

## 实施步骤

1. 修改统计接口，添加 `system_document_count` 和 `uploaded_document_count`
2. 更新前端类型定义
3. 修改前端显示，区分两类文档

## 验证方法

1. 检查 Chroma 数据库中的 source 元数据
2. 确认 document_count 与唯一 source 数量一致
