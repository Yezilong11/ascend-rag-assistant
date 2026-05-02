# 昇腾AI竞赛智能助教 — API 接口文档

> 文档版本: 1.0
> 创建日期: 2026-05-02
> 关联文档: `代码规范.md`、`2026-05-02-frontend-modernization-plan.md`

---

## 目录

1. [概述](#1-概述)
2. [通用约定](#2-通用约定)
3. [技能树 API (port 8000)](#3-技能树-api)
4. [RAG API (port 8001)](#4-rag-api)
5. [错误码参考](#5-错误码参考)
6. [数据模型定义](#6-数据模型定义)
7. [安全与权限](#7-安全与权限)

---

## 1. 概述

### 1.1 服务架构

本系统采用前后端分离架构，后端由两个独立的 FastAPI 微服务组成：

| 服务 | 基地址 | 职责 | 状态 |
|------|--------|------|------|
| 技能树 API | `http://localhost:8000` | 技能树 CRUD 管理 | ✅ 已上线 |
| RAG API | `http://localhost:8001` | 智能问答、知识库管理、模型管理 | 🆕 新建 |

### 1.2 通信协议

| 场景 | 协议 | Content-Type |
|------|------|-------------|
| 技能树 CRUD | HTTP REST | `application/json` |
| RAG 普通问答 | HTTP REST | `application/json` |
| RAG 流式问答 | SSE | `text/event-stream` |
| 文件上传 | HTTP REST | `multipart/form-data` |

### 1.3 开发环境代理

前端开发时通过 Vite 代理统一访问后端，避免跨域问题：

| 前端请求路径 | 代理目标 |
|-------------|---------|
| `/api/skill-tree/**` | `http://localhost:8000` |
| `/api/rag/**` | `http://localhost:8001` |

---

## 2. 通用约定

### 2.1 统一响应格式

所有接口遵循统一的 JSON 响应结构：

**成功响应：**

```json
{
    "success": true,
    "data": { ... }
}
```

**失败响应：**

```json
{
    "success": false,
    "message": "错误描述信息"
}
```

**HTTP 状态码与 success 字段对应关系：**

| HTTP 状态码 | success | 含义 |
|------------|---------|------|
| 200 | true | 请求成功 |
| 400 | false | 请求参数错误 |
| 404 | false | 资源不存在 |
| 422 | false | 请求体验证失败（Pydantic 校验） |
| 500 | false | 服务器内部错误 |
| 503 | false | 服务不可用（如 RAG 引擎未加载） |

### 2.2 请求头约定

| 请求头 | 值 | 必填 | 说明 |
|--------|---|------|------|
| `Content-Type` | `application/json` | 是（除文件上传外） | 请求体格式 |
| `Content-Type` | `multipart/form-data` | 是（文件上传时） | 由浏览器自动设置 |
| `Accept` | `application/json` | 否 | 期望的响应格式 |

### 2.3 分页与列表

列表接口返回数组，暂不分页（数据量较小）：

```json
{
    "success": true,
    "data": [ ... ]
}
```

### 2.4 ID 格式

所有实体 ID 使用 UUID v4 格式，示例：`"a1b2c3d4-e5f6-7890-abcd-ef1234567890"`

### 2.5 时间格式

时间字段使用 ISO 8601 格式：`"2026-05-02T10:30:00"`

### 2.6 SSE 事件格式

SSE 流式响应遵循 W3C Server-Sent Events 规范，每条消息格式：

```
event: <事件类型>
data: <JSON数据>

```

注意：每条消息以两个换行符 `\n\n` 结尾。

---

## 3. 技能树 API

**服务基地址：** `http://localhost:8000`
**路由前缀：** `/api/skill-tree`
**Swagger 文档：** `http://localhost:8000/docs`

---

### 3.1 创建技能树

创建一棵新的技能树。

| 属性 | 值 |
|------|---|
| **路径** | `POST /api/skill-tree/` |
| **Content-Type** | `application/json` |
| **业务场景** | 用户在技能树管理页面点击"创建技能树" |

**请求参数：**

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| name | string | ✅ | — | 技能树名称，1-100字符 |
| description | string | ✅ | — | 技能树描述，1-500字符 |

**请求示例：**

```json
{
    "name": "西门子杯竞赛技能树",
    "description": "涵盖西门子杯竞赛所需全部技能"
}
```

**成功响应 (200)：**

```json
{
    "success": true,
    "data": {
        "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "name": "西门子杯竞赛技能树",
        "description": "涵盖西门子杯竞赛所需全部技能"
    }
}
```

**失败响应 (400)：**

```json
{
    "success": false,
    "message": "创建技能树失败: 名称不能为空"
}
```

---

### 3.2 列出所有技能树

获取系统中所有技能树的摘要列表。

| 属性 | 值 |
|------|---|
| **路径** | `GET /api/skill-tree/` |
| **Content-Type** | `application/json` |
| **业务场景** | 用户进入技能树管理页面时加载列表 |

**请求参数：** 无

**成功响应 (200)：**

```json
{
    "success": true,
    "data": [
        {
            "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "name": "西门子杯竞赛技能树",
            "description": "涵盖西门子杯竞赛所需全部技能",
            "version": "1.0",
            "skill_count": 12,
            "completion_rate": 35.5
        },
        {
            "id": "f0e1d2c3-b4a5-6789-0abc-def123456789",
            "name": "PLC编程技能树",
            "description": "PLC编程相关技能体系",
            "version": "1.0",
            "skill_count": 8,
            "completion_rate": 0.0
        }
    ]
}
```

---

### 3.3 获取技能树详情

获取指定技能树的完整数据，包含所有技能节点和学习路径。

| 属性 | 值 |
|------|---|
| **路径** | `GET /api/skill-tree/{skill_tree_id}` |
| **Content-Type** | `application/json` |
| **业务场景** | 用户点击技能树列表项查看详情 |

**路径参数：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skill_tree_id | string (UUID) | ✅ | 技能树 ID |

**成功响应 (200)：**

```json
{
    "success": true,
    "data": {
        "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "name": "西门子杯竞赛技能树",
        "description": "涵盖西门子杯竞赛所需全部技能",
        "root_nodes": ["skill-uuid-001"],
        "skill_nodes": {
            "skill-uuid-001": {
                "id": "skill-uuid-001",
                "name": "PLC基础",
                "description": "可编程逻辑控制器基础知识",
                "level": "beginner",
                "type": "technical",
                "parent_ids": [],
                "child_ids": ["skill-uuid-002"],
                "related_ids": [],
                "resources": [],
                "learning_time": 20,
                "completion_rate": 50.0
            }
        },
        "learning_paths": {
            "path-uuid-001": {
                "path_id": "path-uuid-001",
                "skill_ids": ["skill-uuid-001", "skill-uuid-002"],
                "estimated_time": 50,
                "difficulty": "intermediate"
            }
        },
        "completion_rate": 25.0
    }
}
```

**失败响应 (404)：**

```json
{
    "success": false,
    "message": "技能树不存在"
}
```

---

### 3.4 删除技能树

删除指定的技能树及其所有关联数据。

| 属性 | 值 |
|------|---|
| **路径** | `DELETE /api/skill-tree/{skill_tree_id}` |
| **Content-Type** | `application/json` |
| **业务场景** | 用户在技能树列表中点击删除按钮 |

**路径参数：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skill_tree_id | string (UUID) | ✅ | 技能树 ID |

**成功响应 (200)：**

```json
{
    "success": true,
    "message": "技能树删除成功"
}
```

**失败响应 (400)：**

```json
{
    "success": false,
    "message": "删除技能树失败"
}
```

---

### 3.5 添加技能

向指定技能树添加一个新的技能节点。

| 属性 | 值 |
|------|---|
| **路径** | `POST /api/skill-tree/{skill_tree_id}/skills` |
| **Content-Type** | `application/json` |
| **业务场景** | 用户在技能树详情页点击"添加技能" |

**路径参数：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skill_tree_id | string (UUID) | ✅ | 技能树 ID |

**请求参数：**

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| name | string | ✅ | — | 技能名称 |
| description | string | ✅ | — | 技能描述 |
| level | string | ✅ | — | 难度等级：`beginner` / `intermediate` / `advanced` / `expert` |
| skill_type | string | ✅ | — | 技能类型：`technical` / `theoretical` / `practical` / `competition` |
| learning_time | integer | ❌ | 0 | 预估学习时间（小时） |

**请求示例：**

```json
{
    "name": "PLC基础",
    "description": "可编程逻辑控制器基础知识",
    "level": "beginner",
    "skill_type": "technical",
    "learning_time": 20
}
```

**成功响应 (200)：**

```json
{
    "success": true,
    "data": {
        "id": "skill-uuid-001",
        "name": "PLC基础",
        "level": "beginner",
        "type": "technical"
    }
}
```

**失败响应 (400)：**

```json
{
    "success": false,
    "message": "无效的技能等级或类型"
}
```

---

### 3.6 建立技能关系

在两个技能节点之间建立关系。

| 属性 | 值 |
|------|---|
| **路径** | `POST /api/skill-tree/{skill_tree_id}/skills/relation` |
| **Content-Type** | `application/json` |
| **业务场景** | 用户在技能树详情页选择两个技能建立前置/进阶/相关关系 |

**路径参数：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skill_tree_id | string (UUID) | ✅ | 技能树 ID |

**请求参数：**

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| source_skill_id | string (UUID) | ✅ | — | 源技能 ID（前置技能） |
| target_skill_id | string (UUID) | ✅ | — | 目标技能 ID（后续技能） |
| relation_type | string | ✅ | — | 关系类型：`prerequisite`（前置）/ `related`（相关）/ `advanced`（进阶） |

**请求示例：**

```json
{
    "source_skill_id": "skill-uuid-001",
    "target_skill_id": "skill-uuid-002",
    "relation_type": "prerequisite"
}
```

**成功响应 (200)：**

```json
{
    "success": true,
    "message": "技能关系建立成功"
}
```

**失败响应 (400)：**

```json
{
    "success": false,
    "message": "源技能不存在"
}
```

---

### 3.7 添加学习资源

为指定技能添加学习资源链接。

| 属性 | 值 |
|------|---|
| **路径** | `POST /api/skill-tree/{skill_tree_id}/skills/{skill_id}/resources` |
| **Content-Type** | `application/json` |
| **业务场景** | 用户在技能详情中添加学习资料链接 |

**路径参数：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skill_tree_id | string (UUID) | ✅ | 技能树 ID |
| skill_id | string (UUID) | ✅ | 技能 ID |

**请求参数：** 请求体为自由 JSON 对象，推荐结构：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | ✅ | 资源名称 |
| url | string | ❌ | 资源链接 |
| type | string | ❌ | 资源类型：`document` / `video` / `course` |
| description | string | ❌ | 资源描述 |

**请求示例：**

```json
{
    "name": "PLC官方文档",
    "url": "https://www.siemens.com/plc/docs",
    "type": "document",
    "description": "西门子PLC编程官方文档"
}
```

**成功响应 (200)：**

```json
{
    "success": true,
    "message": "学习资源添加成功"
}
```

---

### 3.8 更新技能完成率

更新指定技能的学习完成率。

| 属性 | 值 |
|------|---|
| **路径** | `PUT /api/skill-tree/{skill_tree_id}/skills/{skill_id}/completion` |
| **Content-Type** | `application/json` |
| **业务场景** | 用户标记技能学习进度 |

**路径参数：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skill_tree_id | string (UUID) | ✅ | 技能树 ID |
| skill_id | string (UUID) | ✅ | 技能 ID |

**查询参数：**

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| completion_rate | float | ✅ | — | 完成率，范围 0.0 - 100.0 |

**请求示例：**

```
PUT /api/skill-tree/a1b2c3d4/skills/skill-uuid-001/completion?completion_rate=85.5
```

**成功响应 (200)：**

```json
{
    "success": true,
    "message": "技能完成率更新成功"
}
```

---

### 3.9 生成学习路径

根据技能树中的技能关系自动生成学习路径。

| 属性 | 值 |
|------|---|
| **路径** | `POST /api/skill-tree/{skill_tree_id}/paths/generate` |
| **Content-Type** | `application/json` |
| **业务场景** | 用户点击"生成学习路径"按钮 |

**路径参数：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skill_tree_id | string (UUID) | ✅ | 技能树 ID |

**请求参数：** 无

**成功响应 (200)：**

```json
{
    "success": true,
    "data": [
        {
            "path_id": "path-uuid-001",
            "skill_count": 3,
            "estimated_time": 70,
            "difficulty": "advanced"
        },
        {
            "path_id": "path-uuid-002",
            "skill_count": 2,
            "estimated_time": 40,
            "difficulty": "intermediate"
        }
    ]
}
```

---

## 4. RAG API

**服务基地址：** `http://localhost:8001`
**路由前缀：** `/api/rag`
**Swagger 文档：** `http://localhost:8001/docs`

---

### 4.1 获取系统状态

获取 RAG 引擎的当前状态，包括模型加载情况、可用模型列表等。此接口在引擎未加载时也可调用。

| 属性 | 值 |
|------|---|
| **路径** | `GET /api/rag/status` |
| **Content-Type** | `application/json` |
| **业务场景** | 前端轮询（每2秒）检测引擎状态；设置页面初始化加载 |

**请求参数：** 无

**成功响应 (200)：**

```json
{
    "success": true,
    "data": {
        "engine_loaded": true,
        "model_key": "qwen2-1.5b",
        "model_name": "Qwen2-1.5B",
        "reranker_enabled": true,
        "reranker_model": "bge-reranker-v2-m3",
        "knowledge_base_ready": true,
        "available_models": {
            "qwen2-1.5b": {
                "name": "Qwen2-1.5B",
                "description": "标准版，质量最好"
            },
            "qwen2-0.5b": {
                "name": "Qwen2-0.5B",
                "description": "最快，适合CPU"
            },
            "chatglm3-6b": {
                "name": "ChatGLM3-6B",
                "description": "大模型，质量更好"
            }
        },
        "available_rerankers": {
            "bge-reranker-v2-m3": {
                "name": "BGE-Reranker-v2-m3",
                "description": "推荐，多语言支持，效果最佳",
                "size": "~1.2GB"
            },
            "bge-reranker-large": {
                "name": "BGE-Reranker-Large",
                "description": "效果好，速度较快",
                "size": "~1.3GB"
            },
            "bge-reranker-base": {
                "name": "BGE-Reranker-Base",
                "description": "速度快，效果良好",
                "size": "~0.6GB"
            }
        }
    }
}
```

**引擎未加载时：**

```json
{
    "success": true,
    "data": {
        "engine_loaded": false,
        "model_key": "",
        "model_name": "",
        "reranker_enabled": false,
        "reranker_model": "",
        "knowledge_base_ready": true,
        "available_models": { ... },
        "available_rerankers": { ... }
    }
}
```

---

### 4.2 加载模型

异步加载指定的大语言模型和重排序模型。此接口立即返回，模型在后台线程中加载。前端通过轮询 `/api/rag/status` 检测加载完成。

| 属性 | 值 |
|------|---|
| **路径** | `POST /api/rag/model/load` |
| **Content-Type** | `application/json` |
| **业务场景** | 用户在设置页面点击"启动AI引擎" |

**请求参数：**

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| model_key | string | ✅ | — | 预定义模型 key，可选值见 `/api/rag/status` 的 `available_models` |
| model_dir | string | ❌ | `"./models"` | 本地模型存放目录 |
| use_reranker | boolean | ❌ | `true` | 是否启用重排序 |
| reranker_model | string | ❌ | `"bge-reranker-v2-m3"` | 重排序模型 key，可选值见 `available_rerankers` |
| reranker_top_k | integer | ❌ | `3` | 重排序后保留的文档数量，范围 1-10 |
| initial_retrieval_k | integer | ❌ | `10` | 初始检索的文档数量，范围 3-30 |

**请求示例：**

```json
{
    "model_key": "qwen2-1.5b",
    "model_dir": "./models",
    "use_reranker": true,
    "reranker_model": "bge-reranker-v2-m3",
    "reranker_top_k": 3,
    "initial_retrieval_k": 10
}
```

**成功响应 (200)：**

```json
{
    "success": true,
    "data": {
        "model_key": "qwen2-1.5b",
        "status": "loading"
    }
}
```

**正在加载中 (200)：**

```json
{
    "success": false,
    "message": "模型正在加载中，请稍候"
}
```

**加载完成检测：** 前端每 2 秒轮询 `GET /api/rag/status`，当 `engine_loaded` 变为 `true` 时表示加载完成。

---

### 4.3 卸载模型

卸载当前已加载的模型，释放 GPU 显存。

| 属性 | 值 |
|------|---|
| **路径** | `POST /api/rag/model/unload` |
| **Content-Type** | `application/json` |
| **业务场景** | 用户点击"停止AI引擎"释放显存 |

**请求参数：** 无

**成功响应 (200)：**

```json
{
    "success": true,
    "message": "模型已卸载"
}
```

**无模型时 (200)：**

```json
{
    "success": false,
    "message": "没有已加载的模型"
}
```

---

### 4.4 普通问答

向 RAG 引擎发送问题，获取完整回答（非流式）。适用于不需要打字机效果的场景。

| 属性 | 值 |
|------|---|
| **路径** | `POST /api/rag/chat` |
| **Content-Type** | `application/json` |
| **业务场景** | 需要一次性获取完整回答（如 API 对接、导出等） |

**请求参数：**

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| question | string | ✅ | — | 用户问题，至少 1 个字符 |

**请求示例：**

```json
{
    "question": "如何报名西门子杯？"
}
```

**成功响应 (200)：**

```json
{
    "success": true,
    "data": {
        "answer": "西门子杯的报名流程如下：1. 访问官方网站...",
        "sources": [
            {
                "content": "报名须知摘要：西门子杯报名时间一般为每年3-5月...",
                "source": "data/报名须知/西门子杯-报名须知.md"
            },
            {
                "content": "常见问题：报名需要准备个人身份证明...",
                "source": "data/常见问题FAQ/报名FAQ.md"
            }
        ]
    }
}
```

**引擎未加载 (503)：**

```json
{
    "detail": "RAG引擎未加载，请先调用 /api/rag/model/load"
}
```

**问答异常 (200)：**

```json
{
    "success": false,
    "message": "问答处理失败: [具体错误信息]"
}
```

---

### 4.5 流式问答 (SSE)

向 RAG 引擎发送问题，通过 SSE 逐 token 流式返回回答。适用于聊天界面的打字机效果。

| 属性 | 值 |
|------|---|
| **路径** | `POST /api/rag/chat/stream` |
| **Content-Type** | `application/json` |
| **响应 Content-Type** | `text/event-stream` |
| **业务场景** | 聊天窗口实时流式输出 |

**请求参数：**

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| question | string | ✅ | — | 用户问题，至少 1 个字符 |

**请求示例：**

```json
{
    "question": "如何报名西门子杯？"
}
```

**SSE 响应流：**

```
event: token
data: {"token": "西门子"}

event: token
data: {"token": "杯"}

event: token
data: {"token": "的"}

event: token
data: {"token": "报名流程"}

event: token
data: {"token": "如下："}

event: token
data: {"token": "1. 访问官方网站..."}

event: sources
data: {"sources": [{"content": "报名须知摘要...", "source": "data/报名须知/西门子杯-报名须知.md"}]}

event: done
data: {}
```

**SSE 事件类型定义：**

| 事件类型 | data 格式 | 说明 |
|---------|----------|------|
| `token` | `{"token": "文字片段"}` | 逐 token 推送，前端拼接显示 |
| `sources` | `{"sources": [...]}` | 参考来源列表，流结束后推送一次 |
| `done` | `{}` | 流结束标记 |

**响应头：**

```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
X-Accel-Buffering: no
```

**引擎未加载 (503)：**

```json
{
    "detail": "RAG引擎未加载，请先调用 /api/rag/model/load"
}
```

**前端对接要点：**

1. 使用 `fetch` + `ReadableStream` 读取 SSE（不使用 EventSource，因为需要 POST 请求）
2. 维护 buffer 处理不完整的数据行
3. 解析 `event:` 和 `data:` 行，根据事件类型分发处理
4. 支持 `AbortController` 取消正在进行的流式请求
5. 中文 token 使用 `ensure_ascii=False` 编码，前端无需额外解码

---

### 4.6 上传文档

上传文档到知识库，支持 PDF、TXT、MD 格式。系统自动检测文档类型并选择合适的切分策略。

| 属性 | 值 |
|------|---|
| **路径** | `POST /api/rag/ingest` |
| **Content-Type** | `multipart/form-data` |
| **业务场景** | 用户在知识库管理面板上传文档 |

**请求参数：**

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| file | File | ✅ | — | 上传的文件，支持 `.pdf` / `.txt` / `.md`，最大 50MB |

**请求示例 (curl)：**

```bash
curl -X POST http://localhost:8001/api/rag/ingest \
  -F "file=@/path/to/西门子杯-报名须知.md"
```

**请求示例 (前端 axios)：**

```typescript
const formData = new FormData();
formData.append('file', file);
await ragApiClient.post('/rag/ingest', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
});
```

**成功响应 (200)：**

```json
{
    "success": true,
    "data": {
        "filename": "西门子杯-报名须知.md",
        "doc_type": "registration",
        "chunks_count": 12
    }
}
```

**不支持的格式 (400)：**

```json
{
    "detail": "不支持的文件格式，仅支持 ['.pdf', '.txt', '.md']"
}
```

**文件过大 (400)：**

```json
{
    "detail": "文件大小超过50MB限制"
}
```

---

### 4.7 自动导入知识库

自动扫描 `data/` 目录下的所有文档并导入知识库。如果知识库已有数据则跳过。

| 属性 | 值 |
|------|---|
| **路径** | `POST /api/rag/knowledge-base/auto-ingest` |
| **Content-Type** | `application/json` |
| **业务场景** | 首次启动时一键导入全部知识库数据 |

**请求参数：** 无

**成功响应 (200)：**

```json
{
    "success": true,
    "data": {
        "total_files": 64,
        "success_count": 62,
        "failed_count": 2
    }
}
```

**知识库已有数据 (200)：**

```json
{
    "success": true,
    "data": {
        "total_files": 0,
        "success_count": 0,
        "message": "知识库已有数据，跳过导入"
    }
}
```

---

### 4.8 知识库统计

获取知识库的文档片段统计信息。

| 属性 | 值 |
|------|---|
| **路径** | `GET /api/rag/knowledge-base/stats` |
| **Content-Type** | `application/json` |
| **业务场景** | 知识库管理面板展示统计信息 |

**请求参数：** 无

**成功响应 (200)：**

```json
{
    "success": true,
    "data": {
        "total_chunks": 1234
    }
}
```

---

## 5. 错误码参考

### 5.1 HTTP 状态码

| 状态码 | 含义 | 触发场景 |
|--------|------|---------|
| 200 | 成功 | 请求处理成功 |
| 400 | 请求错误 | 参数无效、文件格式不支持、文件过大 |
| 404 | 资源不存在 | 技能树/技能 ID 不存在 |
| 422 | 验证失败 | Pydantic 模型校验失败（缺少必填字段、类型错误） |
| 500 | 服务器错误 | 未捕获的异常 |
| 503 | 服务不可用 | RAG 引擎未加载、模型正在加载中 |

### 5.2 422 验证错误响应格式

FastAPI 自动生成的验证错误格式：

```json
{
    "detail": [
        {
            "loc": ["body", "question"],
            "msg": "ensure this value has at least 1 characters",
            "type": "value_error.any_str.min_length"
        }
    ]
}
```

### 5.3 业务错误码

业务逻辑错误通过 `success: false` 和 `message` 字段传递，不使用独立错误码：

| message 模式 | 含义 |
|-------------|------|
| `"技能树不存在"` | 指定 ID 的技能树未找到 |
| `"源技能不存在"` | 建立关系时源技能 ID 无效 |
| `"目标技能不存在"` | 建立关系时目标技能 ID 无效 |
| `"无效的技能等级或类型"` | level 或 skill_type 枚举值无效 |
| `"RAG引擎未加载，请先调用 /api/rag/model/load"` | 引擎未初始化 |
| `"模型正在加载中，请稍候"` | 并发加载请求被拒绝 |
| `"没有已加载的模型"` | 卸载时无模型可卸 |
| `"不支持的文件格式，仅支持 [...]"` | 文件后缀不在白名单 |
| `"文件大小超过50MB限制"` | 文件体积超限 |

---

## 6. 数据模型定义

### 6.1 枚举值

**SkillLevel（技能难度等级）：**

| 值 | 中文 | 说明 |
|---|------|------|
| `beginner` | 初级 | 入门级技能 |
| `intermediate` | 中级 | 进阶级技能 |
| `advanced` | 高级 | 高阶技能 |
| `expert` | 专家级 | 专家水平技能 |

**SkillType（技能类型）：**

| 值 | 中文 | 说明 |
|---|------|------|
| `technical` | 技术类 | 编程、工具使用等技术技能 |
| `theoretical` | 理论类 | 理论知识、原理理解 |
| `practical` | 实践类 | 实验操作、项目实践 |
| `competition` | 竞赛类 | 竞赛特定技能 |

**RelationType（技能关系类型）：**

| 值 | 中文 | 说明 |
|---|------|------|
| `prerequisite` | 前置 | 源技能是目标技能的前置条件 |
| `related` | 相关 | 两个技能有关联但无先后关系 |
| `advanced` | 进阶 | 源技能是目标技能的进阶方向 |

**DocType（文档类型）：**

| 值 | 中文 | 自动检测关键词 |
|---|------|--------------|
| `registration` | 报名须知 | 报名须知、registration |
| `tech_doc` | 技术文档 | 技术文档、tech_doc、技术指南 |
| `rules` | 竞赛规则 | 竞赛规则、规则、rules |
| `history` | 历史赛题集 | 历史赛题、history、赛题集 |
| `scoring` | 评分标准 | 评分标准、scoring |
| `faq` | 常见问题 | 常见问题、faq |
| `unknown` | 未知 | 无法自动识别 |

### 6.2 模型 Key 映射

**LLM 模型：**

| model_key | name | description | 约需显存 |
|-----------|------|-------------|---------|
| `qwen2-1.5b` | Qwen2-1.5B | 标准版，质量最好 | ~4GB |
| `qwen2-0.5b` | Qwen2-0.5B | 最快，适合CPU | ~2GB |
| `chatglm3-6b` | ChatGLM3-6B | 大模型，质量更好 | ~14GB |

**重排序模型：**

| reranker_model | name | description | size |
|---------------|------|-------------|------|
| `bge-reranker-v2-m3` | BGE-Reranker-v2-m3 | 推荐，多语言支持，效果最佳 | ~1.2GB |
| `bge-reranker-large` | BGE-Reranker-Large | 效果好，速度较快 | ~1.3GB |
| `bge-reranker-base` | BGE-Reranker-Base | 速度快，效果良好 | ~0.6GB |

---

## 7. 安全与权限

### 7.1 当前安全机制

本系统为内部工具，当前阶段不实现用户认证和授权。安全策略如下：

| 机制 | 说明 |
|------|------|
| CORS 白名单 | 仅允许 `localhost:5173`、`localhost:8501`、`localhost:3000` 访问 |
| 文件上传限制 | 仅允许 `.pdf`、`.txt`、`.md` 后缀，最大 50MB |
| 输入验证 | 所有请求参数通过 Pydantic 模型校验 |
| 模型 Key 白名单 | `model_key` 和 `reranker_model` 必须为预定义值 |

### 7.2 CORS 配置详情

**技能树 API (port 8000)：**

```python
allow_origins = ["*"]  # 当前允许所有来源（待收紧）
```

**RAG API (port 8001)：**

```python
allow_origins = [
    "http://localhost:5173",   # React 前端开发服务器
    "http://localhost:8501",   # Streamlit 前端
    "http://localhost:3000",   # 备用前端端口
]
```

### 7.3 未来安全规划

| 阶段 | 安全措施 |
|------|---------|
| V1.0 | CORS 白名单 + 输入验证 + 文件类型限制 |
| V2.0 | JWT Token 认证 + API Key 限流 |
| V3.0 | RBAC 角色权限 + 操作审计日志 |

---

**文档结束**
