# Multimodal 模块

> 版本：2.1.0
> 最后更新：2026-05-09

## 概述

多模态 RAG 模块，支持图片 OCR 识别和视觉语言模型（VLM）处理。

## 目录结构

```
src/multimodal/
├── domain/                    # 领域层
│   ├── entities/             # 实体定义
│   ├── repositories/         # 仓储接口
│   ├── services/            # 领域服务
│   └── value_objects/        # 值对象
├── engines/                   # 引擎层
│   ├── ocr_engine.py        # OCR 引擎
│   └── vlm_engine.py         # VLM 引擎
├── infrastructure/            # 基础设施层
│   └── pdf/                  # PDF 处理
├── repository.py             # 仓储实现
├── service.py               # 服务层
└── routes.py               # API 路由
```

## 核心组件

### OCR Engine

EasyOCR 文字识别引擎。

```python
from src.multimodal.engines import EasyOCREngine

ocr = EasyOCREngine()
text, blocks = ocr.extract_text_from_image("image.png")
```

### VLM Engine

Qwen-VL 视觉语言模型引擎。

```python
from src.multimodal.engines import QwenVLEngine

vlm = QwenVLEngine(vlm_enabled=True)
description = vlm.generate_image_description("image.png", ocr_text="...")
```

### ImageChunkRepository

图片片段仓储，使用 ChromaDB 向量数据库。

```python
from src.multimodal.repository import ImageChunkRepository

repo = ImageChunkRepository(persist_dir="./chroma_db_multimodal")
chunks = repo.similarity_search("查询文本", k=3)
```

### MultimodalIngestService

多模态导入服务。

```python
from src.multimodal.service import create_multimodal_service

service = create_multimodal_service(vlm_enabled=False)
result = service.ingest_image(["image1.png", "image2.jpg"])
```

## API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/multimodal/image/ingest` | 上传图片并导入知识库 |
| POST | `/api/multimodal/pdf/ingest` | 上传 PDF 并导入（文本+图片） |
| DELETE | `/api/multimodal/source/{path}` | 删除指定来源的片段 |
| GET | `/api/multimodal/status/{path}` | 获取处理状态 |

## API 响应格式

所有 API 端点统一返回以下格式：

```json
{
    "success": true,
    "data": { ... },
    "message": "操作成功"
}
```

## 使用示例

### 1. 图片上传处理

```bash
curl -X POST http://localhost:8000/api/multimodal/image/ingest \
  -F "files=@image.png" \
  -F "document_type=unknown"
```

### 2. PDF 处理

```bash
curl -X POST http://localhost:8000/api/multimodal/pdf/ingest \
  -F "file=@document.pdf" \
  -F "document_type=tech_doc"
```

## 依赖

```bash
pip install easyocr Pillow langchain langchain-huggingface langchain-chroma chromadb
# 可选（VLM 功能）
pip install transformers qwen-vl-utils
```

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 2.1.0 | 2026-05-09 | 统一 API 响应格式 |
| 2.0.0 | 2026-05-09 | 简化模块结构（Phase 1-B） |
| 1.x | 之前 | 初始版本 |
