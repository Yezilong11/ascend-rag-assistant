# 多模态知识库文件上传问题分析与解决方案

## 问题概述
用户执行文件上传操作并收到"上传成功"反馈后，存在两个问题：
1. **成功上传的文件在系统中的存储位置不明确**
2. **文档数量统计和分块数量统计中未显示已上传文件的相关数据**

---

## 技术原因分析

### 问题1：存储位置不明确

#### 根本原因
1. **临时文件被删除**：上传的图片首先保存到临时文件，OCR/VLM处理完成后临时文件被删除
2. **元数据中存储的是临时路径**：`ChromaImageChunkRepository._chunk_to_metadata()` 只存储 `image_path`（临时文件路径），不存储原始图片
3. **上传响应缺少存储位置信息**：`_ingest_image_to_multimodal()` 返回结果中未包含存储位置

#### 代码证据
- `routes.py` 第341-342行：处理后删除临时文件
- `chroma_image_chunk_repository.py` 第236行：存储 `image_path` 为临时文件路径
- `routes.py` 第370-380行：响应中无存储位置字段

### 问题2：统计数据未更新

#### 根本原因
1. **统计接口只查询主知识库**：`/api/rag/knowledge-base/stats` 只返回主知识库的分块数，忽略多模态知识库
2. **数据模型不匹配**：前端期望 `document_count`, `chunk_count`, `status`，后端只返回 `total_chunks`
3. **图片块数量未传递**：SettingsPage 未传递 `imageChunkCount` prop 给 KnowledgeBasePanel

#### 代码证据
- `routes.py` 第519-532行：统计接口实现
- `rag.ts` 第46-50行：前端类型定义
- `SettingsPage.tsx` 第141-145行：未传递 imageChunkCount

---

## 解决方案

### 阶段1：修复统计数据问题

#### 步骤1.1：扩展统计接口
**修改文件**: `src/rag_api/routes.py`

修改 `/api/rag/knowledge-base/stats` 端点：
```python
@router.get("/knowledge-base/stats")
async def knowledge_base_stats() -> dict:
    kb = get_knowledge_base()
    text_chunk_count = 0
    multimodal_chunk_count = 0

    try:
        collection = kb.db._collection
        text_chunk_count = collection.count()
    except Exception:
        pass

    try:
        from src.multimodal.interface.api.routes import create_multimodal_service
        multimodal_service = create_multimodal_service(vlm_enabled=False)
        multimodal_chunk_count = multimodal_service.repository.count()
    except Exception:
        pass

    return {
        "success": True,
        "data": {
            "document_count": text_chunk_count + multimodal_chunk_count,
            "chunk_count": text_chunk_count,
            "image_chunk_count": multimodal_chunk_count,
            "status": "ready" if kb else "initializing",
        },
    }
```

#### 步骤1.2：更新前端类型定义
**修改文件**: `frontend/src/types/rag.ts`

```typescript
export interface KnowledgeBaseStats {
  document_count: number;
  chunk_count: number;
  image_chunk_count: number;  // 新增
  status: string;
}
```

#### 步骤1.3：修复SettingsPage传参
**修改文件**: `frontend/src/pages/SettingsPage.tsx`

在 KnowledgeBasePanel 组件调用处添加 imageChunkCount prop：
```tsx
<KnowledgeBasePanel
  stats={kbStats}
  onAutoIngest={handleAutoIngest}
  onUploadSuccess={handleUploadSuccess}
  imageChunkCount={kbStats?.image_chunk_count}  // 新增
/>
```

### 阶段2：修复存储位置问题

#### 步骤2.1：返回存储位置信息
**修改文件**: `src/rag_api/routes.py`

修改 `_ingest_image_to_multimodal()` 返回数据：
```python
return {
    "success": True,
    "data": {
        "filename": filename,
        "doc_type": "image",
        "source_type": "image",
        "chunks_count": result.success_count,
        "storage_location": "./chroma_db_multimodal",
        "message": "图片已导入多模态知识库，完成OCR识别。数据存储位置: ./chroma_db_multimodal",
    },
}
```

#### 步骤2.2：更新API返回类型
**修改文件**: `frontend/src/services/knowledgeBaseApi.ts`

```typescript
ingest: async (file: File): Promise<{
  filename: string
  source_type: string
  chunks_count: number
  storage_location?: string  // 新增
}> => { ... }
```

#### 步骤2.3：显示存储位置反馈
**修改文件**: `frontend/src/components/knowledge/FileUploader.tsx`

```typescript
const storageInfo = result.storage_location ? `\n存储位置: ${result.storage_location}` : ''
const successMsg = fileType === '图片'
  ? `${file.name} 已导入多模态知识库，完成OCR识别${storageInfo}`
  : `${file.name} 导入成功${storageInfo}`
```

---

## 实施步骤清单

| 步骤 | 文件 | 操作 | 优先级 |
|------|------|------|--------|
| 1.1 | src/rag_api/routes.py | 扩展统计接口，同时查询主知识库和多模态知识库 | High |
| 1.2 | frontend/src/types/rag.ts | 添加 image_chunk_count 字段 | High |
| 1.3 | frontend/src/pages/SettingsPage.tsx | 传递 imageChunkCount prop | High |
| 2.1 | src/rag_api/routes.py | 返回 storage_location 字段 | Medium |
| 2.2 | frontend/src/services/knowledgeBaseApi.ts | 更新 ingest 返回类型 | Medium |
| 2.3 | frontend/src/components/knowledge/FileUploader.tsx | 显示存储位置 | Medium |

---

## 验证方法

1. **前端 lint 检查**：`cd frontend && npm run lint`
2. **Python 语法检查**：`python -m py_compile src/rag_api/routes.py`
3. **功能测试**：
   - 上传图片文件，验证成功消息显示存储位置
   - 检查统计面板，验证图片块数更新
   - 上传文档文件，验证文档数/分块数正确更新
