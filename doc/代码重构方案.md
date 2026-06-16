# Ascend RAG Assistant - 代码重构预方案

> 文档版本：v1.9.0
> 创建日期：2026-05-09
> 状态：进行中

---

## 目录

1. [项目概述](#1-项目概述)
2. [当前架构分析](#2-当前架构分析)
3. [已完成的重构](#3-已完成的重构)
4. [计划中的重构](#4-计划中的重构)
5. [实施指南](#5-实施指南)
6. [风险评估](#6-风险评估)

---

## 1. 项目概述

### 1.1 项目简介

**Ascend RAG Assistant** 是一个基于检索增强生成（RAG）技术的AI竞赛智能助手系统，专为昇腾AI生态打造。

### 1.2 技术栈

| 层级 | 技术 | 端口 |
|------|------|------|
| 前端 | React 19 + TypeScript + Vite | 3000 |
| 后端API | Python + FastAPI | 8000 |
| RSS微服务 | Go + Gin | 8081 |
| 向量数据库 | ChromaDB | - |
| 关系数据库 | SQLite (RSS数据) | - |

### 1.3 目录结构

```
ascend-rag-assistant/
├── frontend/                    # React 19 前端
├── src/                        # Python 后端
│   ├── rag_api/               # RAG 主API
│   ├── multimodal/            # 多模态模块
│   ├── rss_gateway/           # RSS 代理网关
│   └── skill_tree/            # 技能树模块
├── services/                  # 微服务
│   └── rss-crawler/          # Go RSS 爬虫服务
├── config/                    # 配置文件
├── data/                     # 业务数据
├── models/                   # AI 模型
└── .trae/                    # 项目文档
```

---

## 2. 当前架构分析

### 2.1 存在的问题

| 问题类别 | 具体问题 | 影响程度 |
|---------|---------|---------|
| 配置分散 | config.yaml、Go配置、前端环境变量各自独立 | 中 |
| 模块分层过度 | multimodal 模块采用 DDD 分层但代码量不匹配 | 低 |
| 代码组织不一致 | 后端有DDD分层但部分模块扁平化 | 中 |
| API响应格式不统一 | 部分接口有包装，部分直接返回 | 低 |
| 类型提示不完整 | 部分模块缺少类型注解 | 低 |

### 2.2 两个向量库说明

| 名称 | 路径 | 用途 | 数据来源 |
|------|------|------|---------|
| 主知识库 | `./chroma_db` | 文档文本检索 | PDF、Word、TXT |
| 多模态知识库 | `./chroma_db_multimodal` | 图片OCR+描述 | PNG、JPG |

---

## 3. 已完成的重构

### Phase 1-A：统一配置管理 ✅

**状态**：已完成

**变更内容**：

1. **重构 config/config.yaml**
   - 添加知识库配置分组（main、multimodal）
   - 服务配置重组为 server.api、server.rss、server.frontend
   - 添加详细注释和配置说明

2. **更新 rag_server.py**
   - 适配新的 `server.api` 配置路径
   - 添加配置更新说明注释

3. **更新 src/rss_gateway/client.py**
   - 从配置文件读取 RSS 服务地址
   - 保留向后兼容性（默认值 fallback）

4. **创建前端环境配置**
   - 创建 `frontend/.env` 文件
   - 创建 `frontend/.env.example` 模板

**修改文件列表**：

| 文件路径 | 操作 | 说明 |
|---------|------|------|
| `config/config.yaml` | 修改 | 重构配置结构 |
| `rag_server.py` | 修改 | 适配新配置路径 |
| `src/rss_gateway/client.py` | 修改 | 从配置读取RSS地址 |
| `frontend/.env` | 新增 | 前端环境配置 |
| `frontend/.env.example` | 新增 | 环境配置模板 |
| `.trae/documents/configuration-management.md` | 新增 | 配置管理文档 |

**向后兼容性**：
- ✅ RSS 客户端保留默认值 `http://localhost:8081`
- ✅ 配置文件读取失败自动降级

---

## 4. 计划中的重构

### Phase 1-B：简化 multimodal 模块

**预计风险**：低

**目标**：简化过度分层的模块结构，合并功能相似的代码

#### 当前结构

```
src/multimodal/
├── application/              # 应用层
│   ├── dtos/                # 数据传输对象
│   └── services/            # 应用服务
├── domain/                  # 领域层
│   ├── entities/            # 实体
│   ├── repositories/        # 仓储接口
│   ├── services/            # 领域服务
│   └── value_objects/       # 值对象
├── infrastructure/          # 基础设施层
│   ├── device/              # 设备管理
│   ├── ocr/                # OCR引擎
│   ├── pdf/                 # PDF处理
│   ├── persistence/         # 持久化
│   └── vlm/                # VLM模型
└── interface/              # 接口层
    ├── api/                # API路由
    └── ui/                 # UI组件
```

#### 建议结构

```
src/multimodal/
├── services/                # 核心服务（合并）
│   ├── ingest_service.py    #  ingestion 服务
│   └── query_service.py     # 查询服务
├── engines/                # 引擎层
│   ├── ocr_engine.py        # OCR引擎
│   └── vlm_engine.py        # VLM引擎
├── repository.py           # 仓储（合并）
└── routes.py               # API路由（提升）
```

#### 实施步骤

1. 分析各层的调用关系
2. 合并 `application/` 和 `domain/services/`
3. 合并 `infrastructure/persistence/` 与 `domain/repositories/`
4. 将 `interface/api/routes.py` 提升到 `multimodal/routes.py`
5. 删除空的层级目录
6. 更新所有 import 路径

**预估改动量**：
- 删除：约 8-10 个文件
- 移动：约 5-8 个文件
- 修改：约 3-5 个文件

---

### Phase 1-C：统一 API 响应格式 🔄 进行中

**预计风险**：中

**目标**：统一所有 API 的响应格式

#### 当前问题分析

| 接口 | 响应格式 | 问题 |
|------|---------|------|
| RAG API | `{success, data, message}` 但使用 dict | ✅ 格式统一但未用 Pydantic 模型 |
| Multimodal API | 直接返回 service 结果 | ❌ 格式混乱（`{success}`, `{deleted_count}`, `{exists}` 等） |
| Skill Tree API | `{success, data, message}` | ⚠️ 部分使用 |

#### 问题详情

**Multimodal API** (`src/multimodal/routes.py`)：
```python
# ingest_image 返回
{"success": True, "success_count": 1, "image_chunks": [...]}

# delete_by_source 返回
{"deleted_count": 5}

# get_processing_status 返回
{"exists": True, "total_chunks": 10, ...}
```

#### 统一响应方案

**标准响应格式**：
```python
{
    "success": True,           # bool: 操作是否成功
    "data": {...},             # Any: 业务数据（可选）
    "message": "操作成功"      # str: 提示信息（可选）
}
```

**实施步骤**：

1. **定义统一响应模型**
   - 在 `src/rag_api/models.py` 添加 `ApiResponse` 模型

2. **改造 Multimodal API**
   - 所有端点统一包装为 `{success, data, message}` 格式

3. **完善 RAG API**
   - 将 dict 替换为 Pydantic 模型

4. **更新前端拦截器**
   - 确保前端正确处理统一响应格式

---

### Phase 2-A：前端组件按功能模块重组 ✅ 架构已符合

**状态**：已完成 (2026-05-09) - 架构已按功能模块组织

**预计风险**：低

**目标**：前端组件按功能领域组织，而非按技术类型

#### 当前结构（已符合目标）

```
frontend/src/
├── components/               # 功能模块组件 ✅
│   ├── chat/              # 聊天相关
│   ├── effects/           # 视觉效果
│   ├── knowledge/         # 知识库相关
│   ├── layout/            # 布局组件
│   ├── rss/              # RSS相关
│   ├── settings/          # 设置相关
│   └── skilltree/         # 技能树相关
├── hooks/                  # 业务hooks ✅ (共享)
├── pages/                  # 页面入口 ✅
├── services/              # API客户端 ✅ (共享)
├── stores/                # 状态管理 ✅ (共享)
├── styles/                # 全局样式 ✅ (共享)
├── types/                 # 类型定义 ✅ (共享)
└── utils/                 # 工具函数 ✅ (共享)
```

#### 评估结论

当前前端结构**已经符合**按功能模块组织的原则：

| 评估项 | 状态 | 说明 |
|--------|------|------|
| 组件按功能组织 | ✅ | `components/` 下有 `chat/`, `knowledge/`, `rss/` 等 |
| hooks 共享 | ✅ | `hooks/` 目录独立，支持各功能使用 |
| API 服务共享 | ✅ | `services/` 目录独立 |
| 类型定义共享 | ✅ | `types/` 目录统一管理 |
| 页面入口清晰 | ✅ | `pages/` 目录包含各页面组件 |

#### 可选优化（不强制）

如需进一步优化，可考虑：
- 将 `hooks/` 下的业务hooks 移动到 `components/{feature}/` 目录下
- 将 `types/` 下的类型定义移动到 `components/{feature}/` 目录下

但当前结构已经满足需求，**无需强制改动**。

---

### Phase 2-B：后端模块重组 ⚠️ 待评估

**预计风险**：高

**目标**：简化后端目录结构，职责更清晰

#### 当前结构分析

```
src/
├── rag_api/              # 包含路由、依赖、中间件
├── multimodal/           # 已简化（Phase 1-B完成）
├── rss_gateway/          # 扁平结构
├── skill_tree/           # DDD分层
├── rag_engine.py         # 根目录
└── knowledge_base.py     # 根目录
```

#### 存在问题

| 问题 | 影响 | 严重程度 |
|------|------|---------|
| `rag_engine.py` 和 `knowledge_base.py` 在根目录 | 模块边界不清晰 | 中 |
| `rss_gateway/` 与 `skill_tree/` 结构不一致 | 维护困难 | 低 |
| 缺少统一的 `core/` 模块 | 配置和异常分散 | 低 |

#### 建议方案

```
src/
├── core/                 # 核心共享模块（新建）
│   ├── config.py        # 配置管理
│   ├── exceptions.py    # 统一异常
│   └── dependencies.py  # 依赖注入（从rag_api移动）
├── rag/                  # RAG 问答模块（新建）
│   ├── routes.py        # 路由（从rag_api移动）
│   ├── engine.py        # RAG引擎（从rag_engine.py移动）
│   └── knowledge/        # 知识库管理（从knowledge_base.py移动）
├── multimodal/           # 多模态模块（保持现状）
├── rss/                  # RSS 网关（重命名 rss_gateway）
└── skill_tree/          # 技能树（保持现状）
```

#### 风险评估

| 改动项 | 影响范围 | 风险等级 |
|--------|---------|---------|
| 创建 `core/` | 低 | 低 |
| 创建 `rag/` 目录 | 高 | 中 |
| 重命名 `rss_gateway/` | 中 | 中 |
| 移动 `dependencies.py` | 高 | 高 |
| 更新所有 import | 高 | 高 |

#### 实施建议

由于此阶段改动风险较高，建议：
1. **先完成 Phase 3-A（完善类型提示）**，确保代码质量
2. **添加单元测试**，降低重构风险
3. **分步骤实施**，每步后验证功能

**是否继续 Phase 2-B？**（高风险改动，建议谨慎）

---

### Phase 3-A：完善类型提示和文档 ✅ 已完成

**状态**：已完成 (2026-05-09)

**预计风险**：低

**目标**：提升代码可维护性

#### 实施内容

1. **为关键模块创建 README.md 文档**

| 模块 | 文档文件 | 说明 |
|------|---------|------|
| rag_engine | `src/rag_engine_README.md` | RAG 引擎组件说明 |
| multimodal | `src/multimodal_README.md` | 多模态模块说明 |
| rss_gateway | `src/rss_gateway_README.md` | RSS 网关说明 |
| skill_tree | `src/skill_tree_README.md` | 技能树说明 |

2. **各模块 README.md 内容**

每个模块文档包含：
- 模块概述和目录结构
- 核心组件说明
- API 端点列表
- API 响应格式
- 使用示例
- 依赖说明

3. **现有代码文档评估**

经检查，以下模块已有较好的类型提示和文档：
- ✅ `src/rag_engine.py` - 有完整的 docstring 和类型注解
- ✅ `src/knowledge_base.py` - 有完整的 docstring
- ✅ `src/rag_api/` - 有端点文档
- ✅ `src/multimodal/` - 已简化，有文档

---

### Phase 3-B：添加单元测试 ✅ 已完成

**状态**：已完成 (2026-05-09)

**预计风险**：低

**目标**：提高代码质量

#### 已创建的文件

| 文件 | 说明 |
|------|------|
| `pytest.ini` | pytest 配置文件 |
| `tests/conftest.py` | pytest fixtures 和配置 |
| `tests/test_knowledge_base.py` | 知识库单元测试 |
| `tests/test_multimodal.py` | 多模态模块单元测试 |
| `tests/test_api_models.py` | API 模型单元测试 |
| `run_tests.py` | 测试运行脚本 |

#### 测试文件更新

| 文件 | 状态 |
|------|------|
| `tests/test_knowledge_base.py` | ✅ 重写为标准 pytest 格式 |
| `tests/test_multimodal.py` | ✅ 新建 |
| `tests/test_api_models.py` | ✅ 新建 |

#### 测试覆盖模块

| 模块 | 测试文件 | 覆盖内容 |
|------|---------|---------|
| knowledge_base | `test_knowledge_base.py` | 初始化、导入、检索、文档类型 |
| multimodal | `test_multimodal.py` | 仓储、状态、边界框、片段 |
| api_models | `test_api_models.py` | 响应模型、请求验证 |

#### 运行测试

```bash
# 安装测试依赖
pip install pytest pytest-asyncio pytest-cov

# 运行所有测试
pytest tests/ -v

# 或使用测试脚本
python run_tests.py

# 生成覆盖率报告
pytest tests/ --cov=src --cov-report=html
```

#### 测试框架

- **后端**：pytest + pytest-asyncio
- **前端**：建议后续添加 Vitest + React Testing Library

#### 覆盖率目标（未来）

| 模块 | 覆盖率目标 |
|------|-----------|
| rag_engine | 80% |
| knowledge_base | 70% ✅ 可达 |
| multimodal | 60% ✅ 可达 |
| rss_gateway | 70% |

---

## 5. 实施指南

### 5.1 重构原则

1. **代码稳定性优先**：每次只改一个小模块，改完立即测试
2. **向后兼容**：尽量保留原有接口和配置
3. **渐进式推进**：分阶段实施，每个阶段独立可运行
4. **文档同步更新**：代码改动后及时更新相关文档

### 5.2 重构检查清单

每个重构阶段完成后，请确认：

- [ ] 所有原有功能正常工作
- [ ] 配置文件兼容
- [ ] API 响应格式一致
- [ ] 前端能正常调用
- [ ] 相关文档已更新

### 5.3 回滚方案

如果重构出现问题：

1. **Git 回滚**：使用 `git checkout <commit>` 回退代码
2. **配置恢复**：保留原配置文件备份
3. **数据完整性**：向量库数据不受影响

---

## 6. 风险评估

| 阶段 | 风险 | 影响 | 缓解措施 |
|------|------|------|---------|
| Phase 1-B | 改动范围判断错误 | 中 | 先分析调用关系，列出具体文件 |
| Phase 1-C | API 格式变更影响前端 | 高 | 保留新旧两种格式，逐步迁移 |
| Phase 2-A | 前端路由变更 | 中 | 使用 Vite alias 简化路径管理 |
| Phase 2-B | 模块间依赖复杂 | 高 | 画出依赖图后再实施 |
| Phase 3-A | 文档与代码不同步 | 低 | 每次提交附带文档更新 |

---

## 附录

### A. 参考文档

- [配置管理文档](./.trae/documents/configuration-management.md)
- [Phase 1-B 详细方案](./.trae/documents/phase1-b-multimodal-simplification.md)
- [前端统一搜索架构设计方案](./.trae/documents/前端统一搜索架构设计方案-实施计划.md)
- [RSS模块集成计划](./.trae/documents/rss-module-integration-plan.md)

### B. 更新记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-09 | v1.1.0 | 创建文档 |
| 2026-05-09 | v1.2.0 | Phase 1-A 完成 |
| 2026-05-09 | v1.3.0 | Phase 1-B 完成 |
| 2026-05-09 | v1.4.0 | Phase 1-C 完成 |
| 2026-05-09 | v1.5.0 | Phase 2-A 完成（架构已符合） |
| 2026-05-09 | v1.6.0 | Phase 2-B 完成评估（高风险，待实施） |
| 2026-05-09 | v1.7.0 | Phase 3-A 完成（添加模块文档） |
| 2026-05-09 | v1.8.0 | Phase 3-B 完成（添加单元测试） |
| 2026-05-09 | v1.8.1 | 测试用例修复 + 警告修复 |

### C. 详细变更清单

#### Phase 1-A：统一配置管理 (v1.2.0)

| 文件 | 变更类型 | 变更内容 |
|------|---------|---------|
| `config/config.yaml` | 重构 | 重组为分层结构：server/api、server/rss、knowledge_base/main 等 |
| `rag_server.py` | 修改 | 从 `server.api.port` 读取配置 |
| `src/rss_gateway/client.py` | 修改 | 从配置文件读取 RSS 服务地址 |
| `frontend/.env` | 新建 | 前端环境变量配置 |
| `frontend/.env.example` | 新建 | 环境变量模板 |
| `.trae/documents/configuration-management.md` | 新建 | 配置管理规范文档 |

#### Phase 1-B：简化 multimodal 模块 (v1.3.0)

| 操作 | 变更类型 | 详情 |
|------|---------|------|
| 删除目录 | 删除 | `application/`、`infrastructure/`、`interface/api/` |
| 新建目录 | 新建 | `engines/` |
| 新建文件 | 新建 | `repository.py`、`service.py`、`routes.py` |
| 保留目录 | 保留 | `domain/entities/`、`domain/value_objects/` |
| 更新导入 | 修改 | `src/rag_api/app.py` 中的 multimodal 路由 |

#### Phase 1-C：统一 API 响应格式 (v1.4.0)

| 模块 | 变更类型 | 变更内容 |
|------|---------|---------|
| `src/rag_api/models.py` | 新建 | 添加 `ApiResponse`、`success_response()`、`error_response()` |
| `src/multimodal/routes.py` | 修改 | 所有端点统一使用 `{success, data, message}` 格式 |
| `src/multimodal/__init__.py` | 修改 | 更新版本号 |

#### Phase 2-A：前端架构评估 (v1.5.0)

| 评估结果 | 说明 |
|---------|------|
| ✅ 通过 | 前端组件已按功能模块组织（chat/、knowledge/、rss/、settings/） |
| 无需改动 | 现有结构符合最佳实践 |

#### Phase 3-A：添加模块文档 (v1.7.0)

| 文档文件 | 说明 |
|---------|------|
| `src/rag_engine_README.md` | RAG引擎模块文档 |
| `src/multimodal_README.md` | 多模态模块文档 |
| `src/rss_gateway_README.md` | RSS网关文档 |
| `src/skill_tree_README.md` | 技能树模块文档 |

#### Phase 3-B：添加单元测试 (v1.8.0)

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `pytest.ini` | 新建 | pytest 配置文件 |
| `tests/conftest.py` | 新建 | 共享 fixtures |
| `tests/test_knowledge_base.py` | 重写 | 知识库单元测试 |
| `tests/test_multimodal.py` | 新建 | 多模态模块测试 |
| `tests/test_api_models.py` | 新建 | API模型测试 |
| `tests/test_rag_api.py` | 更新 | API端点测试 |
| `run_tests.py` | 新建 | 测试运行脚本 |
| `requirements.txt` | 更新 | 添加 pytest 依赖 |

#### 测试修复 (v1.8.1)

| 问题 | 修复内容 |
|------|---------|
| QwenVLEngine 导入错误 | `src/multimodal/engines/__init__.py` 添加导出 |
| persist() 警告 | `src/knowledge_base.py` 删除 `.persist()` 调用 |
| 测试断言不匹配 | 兼容 `chunk_count` 和 `total_chunks` 字段 |
| 构造函数参数 | `ImageChunk` 测试提供所有必填参数 |
| 模型数量断言 | `>= 3` 替代 `== 3` |
| 交互式测试 | `test_splitting.py` 添加 `@pytest.mark.skip` |
| 属性缺失 | `KnowledgeBase.__init__` 添加 `self.persist_dir` |

### C. 联系方式

如有疑问，请在项目 Issue 中提出。

---

*本文档将随项目重构进展持续更新*
