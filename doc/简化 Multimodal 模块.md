# Phase 1-B: 简化 Multimodal 模块

> 文档版本：v1.0
> 目标：简化过度分层的模块结构

---

## 当前问题分析

### 分层过度

| 层级 | 问题 |
|------|------|
| `domain/services/` | 定义了接口但实际实现在 `interface/api/routes.py` |
| `application/services/` | 与 domain/services 功能重复 |
| `application/dtos/` | DTO 过度包装 |
| `interface/api/` | 混合了路由和服务实现 |

### 调用关系混乱

```
routes.py (interface/api/)
    ↓ 调用
CombinedProcessingService (定义在 routes.py 中)
    ↓ 调用
MultimodalIngestServiceImpl (application/services/)
    ↓ 调用
MultimodalProcessingService (domain/services/ - 仅接口)
```

---

## 简化方案

### 目标结构

```
src/multimodal/          (简化后)
├── entities/
│   ├── image_chunk.py       # 实体定义
│   └── multimodal_document.py
├── value_objects/
│   ├── bounding_box.py
│   ├── device_type.py
│   └── processing_status.py
├── engines/                # 引擎层（合并）
│   ├── ocr_engine.py      # EasyOCR
│   └── vlm_engine.py      # QwenVL
├── repository.py           # 仓储（合并 domain + infrastructure）
├── service.py             # 服务层（合并 application + routes 中的服务）
└── routes.py              # API路由（仅保留路由定义）
```

### 变更清单

#### 将删除的文件/目录

| 路径 | 原因 |
|------|------|
| `application/` | 合并到 service.py |
| `domain/services/` | 仅保留接口定义或删除 |
| `domain/repositories/` | 合并到 repository.py |
| `infrastructure/device/` | 未使用或简单功能 |
| `infrastructure/ocr/` | 合并到 engines/ |
| `infrastructure/vlm/` | 合并到 engines/ |
| `infrastructure/persistence/` | 合并到 repository.py |
| `interface/` | 仅保留 routes.py |

#### 将创建/修改的文件

| 路径 | 操作 | 说明 |
|------|------|------|
| `engines/__init__.py` | 新建 | 导出引擎 |
| `engines/ocr_engine.py` | 移动 | from infrastructure/ocr/ |
| `engines/vlm_engine.py` | 移动 | from infrastructure/vlm/ |
| `repository.py` | 新建 | 合并仓储实现 |
| `service.py` | 新建 | 合并应用服务 |
| `routes.py` | 移动+简化 | from interface/api/，移除服务定义 |
| `__init__.py` | 修改 | 更新导出 |

---

## 实施步骤

### Step 1: 创建 engines 目录并移动文件

```bash
# 创建 engines 目录
mkdir -p src/multimodal/engines

# 移动 OCR 引擎
mv src/multimodal/infrastructure/ocr/easyocr_engine.py src/multimodal/engines/

# 移动 VLM 引擎
mv src/multimodal/infrastructure/vlm/qwen_vl_engine.py src/multimodal/engines/
```

### Step 2: 合并仓储

在 `repository.py` 中合并：
- `domain/repositories/image_chunk_repository.py` (接口)
- `infrastructure/persistence/chroma_image_chunk_repository.py` (实现)

### Step 3: 合并服务

在 `service.py` 中合并：
- `application/services/multimodal_ingest_service.py`
- `routes.py` 中的 `CombinedProcessingService`

### Step 4: 简化路由

在 `routes.py` 中：
- 移除 `CombinedProcessingService` 和 `create_multimodal_service` 定义
- 仅保留 API 端点定义

### Step 5: 更新 __init__.py

更新模块导出以适配新的文件结构。

### Step 6: 更新引用

检查并更新所有引用 `src.multimodal` 的文件。

---

## 风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| import 路径变更 | 高 | 逐步迁移，更新一个测试一个 |
| 服务依赖断裂 | 高 | 保持服务接口兼容 |
| API 响应格式变化 | 中 | 确保返回格式一致 |

---

## 验证清单

- [ ] 所有 import 语句正确
- [ ] API 端点响应格式不变
- [ ] 前端多模态功能正常
- [ ] 图片上传和处理正常
- [ ] 向量库存储正常
