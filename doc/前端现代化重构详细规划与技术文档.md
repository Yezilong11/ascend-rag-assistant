# 昇腾AI竞赛智能助教 — 前端现代化重构详细规划与技术文档

> 文档版本: 1.0
> 创建日期: 2026-05-02
> 基于文档: `2026-04-29-frontend-modernization-proposal.md`
> 目标: 将 Streamlit 前端迁移至 React + TypeScript 现代化架构，后端拆分为独立微服务

---

## 目录

1. [现有系统深度分析](#1-现有系统深度分析)
2. [迁移目标与原则](#2-迁移目标与原则)
3. [目标架构设计](#3-目标架构设计)
4. [后端 API 拆分设计](#4-后端-api-拆分设计)
5. [前端架构设计](#5-前端架构设计)
6. [数据流与交互设计](#6-数据流与交互设计)
7. [详细实施计划](#7-详细实施计划)
8. [测试策略](#8-测试策略)
9. [部署方案](#9-部署方案)
10. [风险管理与回滚策略](#10-风险管理与回滚策略)
11. [验收标准](#11-验收标准)

---

## 1. 现有系统深度分析

### 1.1 代码结构总览

```
d:\ascend-rag-assistant\
├── app.py                          # Streamlit 前端 (~1346行，含350行CSS)
├── server.py                       # FastAPI 技能树 API 服务 (port 8000)
├── config/
│   └── config.yaml                 # 全局配置
├── src/
│   ├── rag_engine.py               # RAG 引擎 (RAGAssistant + Reranker)
│   ├── knowledge_base.py           # 知识库管理 (ChromaDB + 文档切分)
│   ├── ascend_adapter.py           # 昇腾 NPU 适配
│   └── skill_tree/                 # 技能树模块 (DDD 架构)
│       ├── api/routes.py           # FastAPI 路由
│       ├── application/services.py # 应用服务层
│       ├── domain/
│       │   ├── models.py           # 领域模型
│       │   └── services.py         # 领域服务
│       └── infrastructure/
│           └── repositories.py     # JSON 文件仓储
├── data/                           # 竞赛知识库数据
│   ├── 常见问题FAQ/
│   ├── 报名须知/
│   ├── 技术文档/
│   ├── 竞赛规则/
│   └── 评分标准/
├── tests/                          # 测试目录
├── requirements.txt                # Python 依赖
└── start.bat / start.sh            # 启动脚本
```

### 1.2 现有模块职责与耦合分析

| 模块 | 文件 | 行数 | 职责 | 耦合问题 |
|------|------|------|------|---------|
| **前端 UI** | `app.py` | ~1346 | Streamlit 页面渲染、CSS、交互逻辑 | 直接 import RAGAssistant/KnowledgeBase |
| **RAG 引擎** | `src/rag_engine.py` | ~509 | 模型加载、问答生成、流式输出 | 被 app.py 直接实例化，无法独立部署 |
| **知识库** | `src/knowledge_base.py` | ~459 | 文档导入、切分、向量检索 | 被 RAGAssistant 直接持有 |
| **技能树 API** | `server.py` + `src/skill_tree/` | ~300+ | 技能树 CRUD REST API | 已独立，无耦合问题 |
| **配置** | `config/config.yaml` | ~34 | 全局配置 | 各模块直接读取 |

### 1.3 app.py 功能拆解

`app.py` 是一个 1346 行的单文件，包含以下功能模块：

| 功能区域 | 行数范围 | 功能描述 |
|---------|---------|---------|
| CSS 样式 | 42-350 | ~308 行自定义 CSS（聊天、技能树、动画等） |
| Session State 初始化 | 352-368 | assistant、kb、chat_history 等状态 |
| 侧边栏 - 知识库管理 | 375-478 | 初始化知识库、自动导入、文件上传 |
| 侧边栏 - AI 引擎控制 | 480-578 | 模型启动、重排序配置、模型路径 |
| 侧边栏 - 系统信息 | 580-610 | 技术栈信息展示 |
| 主界面 - 智能问答 | 612-858 | 聊天历史、流式输出、预制问题 |
| 主界面 - 技能树 | 860-1338 | 技能树 CRUD、技能管理、学习路径 |
| 页脚 | 1340-1346 | 版权信息 |

### 1.4 关键技术依赖

**后端 Python 依赖：**

| 依赖 | 版本 | 用途 |
|------|------|------|
| langchain | >=1.2.0 | RAG 链 |
| transformers | >=5.0.0 | LLM 加载与推理 |
| torch | >=2.10.0 | 模型推理 |
| chromadb | >=1.5.0 | 向量数据库 |
| sentence-transformers | >=5.0.0 | 嵌入与重排序 |
| fastapi | >=0.130.0 | REST API |
| streamlit | >=1.50.0 | 前端 UI |
| modelscope | >=1.9.0 | 模型下载 |

**前端当前依赖：** 无（Streamlit 内置）

### 1.5 现有 API 路由清单

**技能树 API (port 8000, 前缀 `/api/skill-tree`)：**

| 方法 | 路径 | 功能 | 请求体 |
|------|------|------|--------|
| POST | `/` | 创建技能树 | `{name, description}` |
| GET | `/` | 列出所有技能树 | - |
| GET | `/{id}` | 获取技能树详情 | - |
| DELETE | `/{id}` | 删除技能树 | - |
| POST | `/{id}/skills` | 添加技能 | `{name, description, level, skill_type, learning_time}` |
| POST | `/{id}/skills/relation` | 建立技能关系 | `{source_skill_id, target_skill_id, relation_type}` |
| POST | `/{id}/skills/{skill_id}/resources` | 添加学习资源 | `resource: Dict` |
| PUT | `/{id}/skills/{skill_id}/completion` | 更新完成率 | `completion_rate: float` |
| POST | `/{id}/paths/generate` | 生成学习路径 | - |

### 1.6 现有数据模型

**SkillTree (聚合根)：**

```
SkillTree
├── id: str (UUID)
├── name: str
├── description: str
├── version: str ("1.0")
├── created_at / updated_at: str
├── root_nodes: List[str]          # 根节点 ID 列表
├── skill_nodes: Dict[str, SkillNode]  # 技能节点字典
└── learning_paths: Dict[str, LearningPath]  # 学习路径字典
```

**SkillNode (实体)：**

```
SkillNode
├── id: str (UUID)
├── name: str
├── description: str
├── level: SkillLevel (beginner|intermediate|advanced|expert)
├── skill_type: SkillType (technical|theoretical|practical|competition)
├── parent_ids / child_ids / related_ids: List[str]
├── resources: List[Dict]
├── prerequisites: List[SkillRelation]
├── learning_time: int (小时)
└── completion_rate: float (0-100)
```

**RAG 引擎状态：**

```
RAGAssistant
├── kb: KnowledgeBase
├── model_key: str
├── model: AutoModelForCausalLM
├── tokenizer: AutoTokenizer
├── qa_chain: RetrievalQA
├── use_reranker: bool
├── reranker: Reranker | None
├── reranker_top_k: int
├── initial_retrieval_k: int
├── _last_sources: List[Dict]  # 最近一次检索来源
└── _last_reranked_docs: List[Document]
```

### 1.7 核心问题总结

| # | 问题 | 严重程度 | 根因 | 影响 |
|---|------|---------|------|------|
| P1 | RAG 引擎与前端强耦合 | 🔴 高 | app.py 直接 import RAGAssistant | 无法独立部署/扩展/测试 |
| P2 | 模型加载阻塞 UI 线程 | 🔴 高 | Streamlit 同步执行模型加载 | 首次启动体验极差 |
| P3 | 单文件 1346 行 | 🔴 高 | 所有 UI 逻辑集中 | 维护困难、协作冲突 |
| P4 | 308 行 CSS hack 注入 | 🟡 中 | Streamlit 不支持原生样式定制 | 样式维护困难 |
| P5 | 无响应式设计 | 🟡 中 | Streamlit 布局限制 | 移动端不可用 |
| P6 | 技能树无可视化 | 🟡 中 | Streamlit 图表能力有限 | 无法直观展示技能关系 |
| P7 | 流式输出依赖 Streamlit | 🟡 中 | 使用 Streamlit generator | 迁移需重新实现 |

---

## 2. 迁移目标与原则

### 2.1 迁移目标

| 维度 | 当前状态 | 目标状态 |
|------|---------|---------|
| **架构** | 单体 Streamlit 应用 | 前后端分离，React + 双 FastAPI 微服务 |
| **部署** | 2 进程 (Streamlit + FastAPI) | 3 进程 (React + SkillTree API + RAG API) |
| **首屏加载** | ~5s (含模型加载) | < 2s (模型异步加载) |
| **交互响应** | 依赖 Streamlit rerun | < 100ms (React 状态更新) |
| **移动端** | ❌ 不可用 | ✅ 完全响应式 |
| **技能树可视化** | ❌ 无 | ✅ 交互式图形 |
| **代码组织** | 单文件 1346 行 | 模块化组件，单文件 < 200 行 |

### 2.2 迁移原则

1. **渐进式迁移**：新前端开发期间，原 Streamlit 版本保持可用，通过端口区分
2. **后端先行**：先完成 RAG API 拆分，再开发前端，确保 API 稳定后再对接
3. **功能等价**：迁移后所有现有功能必须完整保留，不丢失任何交互
4. **向后兼容**：现有技能树 API (port 8000) 保持不变，新增 RAG API (port 8001)
5. **可回滚**：保留 Streamlit 版本，通过环境变量切换前后端

---

## 3. 目标架构设计

### 3.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         React 前端 (Vite Dev Server)                        │
│                         http://localhost:5173                               │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                        React 18 + TypeScript                          │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │  │
│  │  │  智能问答页面 │  │  技能树页面   │  │  知识库页面  │  │  设置页面  │ │  │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────┬──────┘ │  │
│  │         │                │                │                │         │  │
│  │  ┌──────┴────────────────┴────────────────┴────────────────┘         │  │
│  │  │                    API Service Layer (services/)                   │  │
│  │  │  • ragApi.ts ── SSE 流式通信                                       │  │
│  │  │  • skillTreeApi.ts ── REST CRUD                                   │  │
│  │  │  • knowledgeBaseApi.ts ── 文件上传                                 │  │
│  │  └──────────────────────────────────────────────────────────────────┘ │  │
│  │  ┌──────────────────────────────────────────────────────────────────┐ │  │
│  │  │                    State Management (Zustand)                     │ │  │
│  │  │  • chatStore: messages, isLoading, sendMessage                   │ │  │
│  │  │  • skillTreeStore: trees, selectedTree, skills                   │ │  │
│  │  │  • appStore: settings, theme, modelConfig                        │ │  │
│  │  └──────────────────────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                    │                           │
                    │ HTTP/SSE                   │ HTTP REST
                    ▼                           ▼
┌──────────────────────────────┐  ┌──────────────────────────────────────────┐
│     RAG API (FastAPI)        │  │     技能树 API (FastAPI)                  │
│     http://localhost:8001    │  │     http://localhost:8000                 │
│  ┌────────────────────────┐  │  │  ┌──────────────────────────────────────┐│
│  │ /api/rag/chat          │  │  │  │ /api/skill-tree/                    ││
│  │ /api/rag/chat/stream   │  │  │  │ /api/skill-tree/{id}                ││
│  │ /api/rag/ingest        │  │  │  │ /api/skill-tree/{id}/skills         ││
│  │ /api/rag/status        │  │  │  │ /api/skill-tree/{id}/skills/relation││
│  │ /api/rag/model/load    │  │  │  │ /api/skill-tree/{id}/paths/generate ││
│  │ /api/rag/model/status  │  │  │  └──────────────────────────────────────┘│
│  └──────────┬─────────────┘  │  │                    │                      │
│             │                 │  │                    │                      │
│  ┌──────────┴─────────────┐  │  │  ┌─────────────────┴──────────────────┐  │
│  │ RAGAssistant (单例)     │  │  │  │ SkillTreeApplicationService       │  │
│  │ KnowledgeBase (单例)    │  │  │  │ SkillTreeService (领域)           │  │
│  │ Reranker (可选)         │  │  │  │ FileSkillTreeRepository           │  │
│  └──────────┬─────────────┘  │  │  └────────────────┬──────────────────┘  │
│             │                 │  │                   │                      │
│  ┌──────────┴─────────────┐  │  │  ┌────────────────┴──────────────────┐  │
│  │ ChromaDB               │  │  │  │ JSON 文件存储                     │  │
│  │ ./chroma_db/           │  │  │  │ ./skill_tree_data/*.json          │  │
│  └────────────────────────┘  │  │  └───────────────────────────────────┘  │
└──────────────────────────────┘  └──────────────────────────────────────────┘
```

### 3.2 进程与端口分配

| 服务 | 进程 | 端口 | 启动命令 | 说明 |
|------|------|------|---------|------|
| React 前端 | Node.js | 5173 | `cd frontend && npm run dev` | Vite 开发服务器 |
| 技能树 API | Python | 8000 | `python server.py` | 现有，不变 |
| RAG API | Python | 8001 | `python rag_server.py` | 新建 |
| 前端生产 | Nginx | 80/443 | `nginx -c nginx.conf` | 生产环境 |

### 3.3 通信协议

| 场景 | 协议 | 说明 |
|------|------|------|
| 技能树 CRUD | HTTP REST (JSON) | 标准 RESTful API |
| RAG 普通问答 | HTTP POST (JSON) | 同步请求-响应 |
| RAG 流式问答 | SSE (Server-Sent Events) | 单向流式推送 |
| 文件上传 | HTTP POST (multipart/form-data) | 知识库文档导入 |
| 前端开发代理 | Vite Proxy → API | 开发环境跨域处理 |

---

## 4. 后端 API 拆分设计

### 4.1 RAG API 服务设计

#### 4.1.1 新增文件结构

```
src/
├── rag_api/
│   ├── __init__.py
│   ├── app.py              # FastAPI 应用入口
│   ├── routes.py           # API 路由定义
│   ├── models.py           # Pydantic 请求/响应模型
│   ├── dependencies.py     # 依赖注入 (单例管理)
│   └── middleware.py       # 中间件 (CORS, 错误处理, 日志)
├── rag_engine.py           # 现有，不修改
└── knowledge_base.py       # 现有，不修改
rag_server.py               # 新增，RAG API 启动入口
```

#### 4.1.2 核心设计：单例管理

RAG 引擎和知识库是重量级对象（模型加载耗时数十秒），必须在 API 服务生命周期内保持单例：

```python
# src/rag_api/dependencies.py

from functools import lru_cache
from src.rag_engine import RAGAssistant
from src.knowledge_base import KnowledgeBase

_rag_assistant: RAGAssistant | None = None
_knowledge_base: KnowledgeBase | None = None

def get_knowledge_base() -> KnowledgeBase:
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = KnowledgeBase()
    return _knowledge_base

def get_rag_assistant() -> RAGAssistant | None:
    return _rag_assistant

def set_rag_assistant(assistant: RAGAssistant):
    global _rag_assistant
    _rag_assistant = assistant
```

#### 4.1.3 API 路由设计

**POST `/api/rag/chat` — 普通问答**

```python
# 请求
{
    "question": "如何报名西门子杯？"
}

# 响应
{
    "success": true,
    "data": {
        "answer": "西门子杯报名流程如下...",
        "sources": [
            {
                "content": "报名须知摘要...",
                "source": "data/报名须知/西门子杯-报名须知.md"
            }
        ]
    }
}
```

**POST `/api/rag/chat/stream` — 流式问答 (SSE)**

```python
# 请求
{
    "question": "如何报名西门子杯？"
}

# 响应 (SSE)
Content-Type: text/event-stream

event: token
data: {"token": "西门子"}

event: token
data: {"token": "杯"}

event: sources
data: {"sources": [{"content": "...", "source": "..."}]}

event: done
data: {}
```

**POST `/api/rag/ingest` — 上传文档**

```python
# 请求: multipart/form-data
# file: 上传的文件 (pdf/txt/md)

# 响应
{
    "success": true,
    "data": {
        "filename": "西门子杯-报名须知.md",
        "chunks_count": 12,
        "doc_type": "registration"
    }
}
```

**GET `/api/rag/status` — 获取系统状态**

```python
# 响应
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
            "qwen2-1.5b": {"name": "Qwen2-1.5B", "description": "标准版"},
            "qwen2-0.5b": {"name": "Qwen2-0.5B", "description": "最快"},
            "chatglm3-6b": {"name": "ChatGLM3-6B", "description": "大模型"}
        },
        "available_rerankers": {
            "bge-reranker-v2-m3": {"name": "BGE-Reranker-v2-m3", "size": "~1.2GB"},
            "bge-reranker-large": {"name": "BGE-Reranker-Large", "size": "~1.3GB"},
            "bge-reranker-base": {"name": "BGE-Reranker-Base", "size": "~0.6GB"}
        }
    }
}
```

**POST `/api/rag/model/load` — 加载模型**

```python
# 请求
{
    "model_key": "qwen2-1.5b",
    "model_dir": "./models",
    "use_reranker": true,
    "reranker_model": "bge-reranker-v2-m3",
    "reranker_top_k": 3,
    "initial_retrieval_k": 10
}

# 响应
{
    "success": true,
    "data": {
        "model_key": "qwen2-1.5b",
        "model_name": "Qwen2-1.5B",
        "reranker_enabled": true
    }
}
```

**POST `/api/rag/model/unload` — 卸载模型（释放显存）**

```python
# 响应
{
    "success": true,
    "message": "模型已卸载"
}
```

**POST `/api/rag/knowledge-base/auto-ingest` — 自动导入知识库**

```python
# 响应
{
    "success": true,
    "data": {
        "total_files": 64,
        "success_count": 62,
        "failed_count": 2
    }
}
```

**GET `/api/rag/knowledge-base/stats` — 知识库统计**

```python
# 响应
{
    "success": true,
    "data": {
        "total_chunks": 1234,
        "doc_types": {
            "registration": 120,
            "tech_doc": 340,
            "rules": 280,
            "faq": 180,
            "scoring": 314
        }
    }
}
```

#### 4.1.4 SSE 流式响应实现

```python
# src/rag_api/routes.py

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import json

router = APIRouter(prefix="/api/rag", tags=["rag"])

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    assistant = get_rag_assistant()
    if not assistant:
        raise HTTPException(status_code=503, detail="RAG引擎未加载")

    def event_generator():
        sources = []
        for token in assistant.query_stream(request.question):
            yield f"event: token\ndata: {json.dumps({'token': token})}\n\n"

        sources = assistant._last_sources or []
        yield f"event: sources\ndata: {json.dumps({'sources': sources})}\n\n"
        yield f"event: done\ndata: {{}}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )
```

#### 4.1.5 rag_server.py 启动入口

```python
# rag_server.py

import yaml
import uvicorn
from src.rag_api.app import create_app

config_path = "./config/config.yaml"
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

server_config = config.get('server', {})
rag_port = server_config.get('rag_port', 8001)
host = server_config.get('host', '127.0.0.1')

app = create_app()

if __name__ == "__main__":
    print(f"Starting RAG API server...")
    print(f"RAG API: http://localhost:{rag_port}")
    print(f"API docs: http://localhost:{rag_port}/docs")
    uvicorn.run("rag_server:app", host=host, port=rag_port, reload=False)
```

#### 4.1.6 配置文件更新

在 `config/config.yaml` 中新增 RAG API 端口配置：

```yaml
server:
  web_port: 8501       # Streamlit (保留，兼容)
  api_port: 8000       # 技能树 API
  rag_port: 8001       # RAG API (新增)
  host: "0.0.0.0"
```

### 4.2 技能树 API 变更

技能树 API 保持现有接口不变，仅确保 CORS 配置允许前端开发服务器访问：

```python
# server.py 中 CORS 配置更新
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite 开发服务器
        "http://localhost:8501",   # Streamlit (兼容)
        "http://localhost:3000",   # 备用
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 5. 前端架构设计

### 5.1 技术选型

| 层级 | 技术 | 版本 | 选型理由 |
|------|------|------|---------|
| 构建工具 | **Vite** | ^5.0 | 极速 HMR，原生 ESM |
| 前端框架 | **React** | ^18.2 | 生态丰富，组件化 |
| 类型系统 | **TypeScript** | ^5.3 | 类型安全，IDE 支持好 |
| UI 组件库 | **Ant Design** | ^5.12 | 企业级组件，中文友好 |
| 状态管理 | **Zustand** | ^4.4 | 轻量，无 boilerplate |
| 路由 | **React Router** | ^6.20 | 声明式路由 |
| HTTP 客户端 | **axios** | ^1.6 | 拦截器、超时、取消请求 |
| 图标 | **@ant-design/icons** | ^5.2 | 与 Ant Design 一致 |
| 技能树可视化 | **React Flow** | ^11.10 | 交互式节点图，拖拽支持 |
| 代码规范 | **ESLint + Prettier** | latest | 代码风格统一 |

### 5.2 目录结构

```
frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatWindow.tsx         # 聊天窗口主容器
│   │   │   ├── MessageBubble.tsx      # 消息气泡
│   │   │   ├── ChatInput.tsx          # 输入框
│   │   │   ├── ThinkingIndicator.tsx  # 思考中动画
│   │   │   ├── SourcePanel.tsx        # 参考来源面板
│   │   │   └── WelcomeCard.tsx        # 欢迎卡片
│   │   ├── skilltree/
│   │   │   ├── SkillTreeList.tsx      # 技能树列表
│   │   │   ├── SkillTreeDetail.tsx    # 技能树详情
│   │   │   ├── SkillNodeCard.tsx      # 技能节点卡片
│   │   │   ├── SkillGraph.tsx         # 技能树可视化 (React Flow)
│   │   │   ├── AddSkillForm.tsx       # 添加技能表单
│   │   │   ├── RelationForm.tsx       # 建立关系表单
│   │   │   └── LearningPathList.tsx   # 学习路径列表
│   │   ├── knowledge/
│   │   │   ├── KnowledgeBasePanel.tsx # 知识库状态面板
│   │   │   └── FileUploader.tsx       # 文件上传组件
│   │   ├── settings/
│   │   │   ├── ModelSelector.tsx      # 模型选择器
│   │   │   ├── RerankerConfig.tsx     # 重排序配置
│   │   │   └── EngineControl.tsx      # 引擎启停控制
│   │   └── layout/
│   │       ├── AppLayout.tsx          # 应用主布局
│   │       ├── Sidebar.tsx            # 侧边栏
│   │       ├── Header.tsx             # 顶部导航
│   │       └── ThemeToggle.tsx        # 主题切换
│   ├── pages/
│   │   ├── ChatPage.tsx               # 智能问答页面
│   │   ├── SkillTreePage.tsx          # 技能树页面
│   │   └── SettingsPage.tsx           # 设置页面
│   ├── hooks/
│   │   ├── useChat.ts                 # 聊天逻辑 Hook
│   │   ├── useSSE.ts                  # SSE 流式通信 Hook
│   │   ├── useSkillTree.ts            # 技能树 CRUD Hook
│   │   └── useRAGStatus.ts            # RAG 状态轮询 Hook
│   ├── services/
│   │   ├── api.ts                     # axios 实例与拦截器
│   │   ├── ragApi.ts                  # RAG API 封装
│   │   ├── skillTreeApi.ts            # 技能树 API 封装
│   │   └── knowledgeBaseApi.ts        # 知识库 API 封装
│   ├── stores/
│   │   ├── chatStore.ts               # 聊天状态
│   │   ├── skillTreeStore.ts          # 技能树状态
│   │   └── appStore.ts                # 全局应用状态
│   ├── types/
│   │   ├── chat.ts                    # 聊天相关类型
│   │   ├── skillTree.ts               # 技能树相关类型
│   │   ├── rag.ts                     # RAG 相关类型
│   │   └── api.ts                     # API 通用类型
│   ├── utils/
│   │   ├── sse.ts                     # SSE 解析工具
│   │   └── constants.ts               # 常量定义
│   ├── App.tsx                        # 应用根组件
│   ├── main.tsx                       # 入口文件
│   └── vite-env.d.ts                  # Vite 类型声明
├── index.html
├── package.json
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
├── .eslintrc.cjs
└── .prettierrc
```

### 5.3 TypeScript 类型定义

```typescript
// types/chat.ts

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
  timestamp: number;
}

export interface Source {
  content: string;
  source: string;
}

export interface ChatState {
  messages: Message[];
  isLoading: boolean;
  currentStreamingContent: string;
}
```

```typescript
// types/skillTree.ts

export type SkillLevel = 'beginner' | 'intermediate' | 'advanced' | 'expert';
export type SkillType = 'technical' | 'theoretical' | 'practical' | 'competition';

export interface SkillNode {
  id: string;
  name: string;
  description: string;
  level: SkillLevel;
  type: SkillType;
  parent_ids: string[];
  child_ids: string[];
  related_ids: string[];
  resources: Record<string, unknown>[];
  learning_time: number;
  completion_rate: number;
}

export interface LearningPath {
  path_id: string;
  skill_ids: string[];
  estimated_time: number;
  difficulty: SkillLevel;
}

export interface SkillTree {
  id: string;
  name: string;
  description: string;
  version: string;
  root_nodes: string[];
  skill_nodes: Record<string, SkillNode>;
  learning_paths: Record<string, LearningPath>;
  completion_rate: number;
}

export interface SkillTreeListItem {
  id: string;
  name: string;
  description: string;
  version: string;
  skill_count: number;
  completion_rate: number;
}
```

```typescript
// types/rag.ts

export interface RAGStatus {
  engine_loaded: boolean;
  model_key: string;
  model_name: string;
  reranker_enabled: boolean;
  reranker_model: string;
  knowledge_base_ready: boolean;
  available_models: Record<string, ModelInfo>;
  available_rerankers: Record<string, RerankerInfo>;
}

export interface ModelInfo {
  name: string;
  description: string;
}

export interface RerankerInfo {
  name: string;
  description: string;
  size: string;
}

export interface ModelLoadRequest {
  model_key: string;
  model_dir?: string;
  use_reranker?: boolean;
  reranker_model?: string;
  reranker_top_k?: number;
  initial_retrieval_k?: number;
}
```

### 5.4 API Service 层设计

```typescript
// services/api.ts

import axios from 'axios';

const SKILL_TREE_API_BASE = 'http://localhost:8000/api';
const RAG_API_BASE = 'http://localhost:8001/api';

export const skillTreeApiClient = axios.create({
  baseURL: SKILL_TREE_API_BASE,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

export const ragApiClient = axios.create({
  baseURL: RAG_API_BASE,
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
});
```

```typescript
// services/ragApi.ts

import { ragApiClient } from './api';
import type { RAGStatus, ModelLoadRequest } from '../types/rag';
import type { Source } from '../types/chat';

export const ragApi = {
  chat: async (question: string) => {
    const { data } = await ragApiClient.post('/rag/chat', { question });
    return data;
  },

  chatStream: async (question: string): Promise<ReadableStream<Uint8Array>> => {
    const response = await fetch(`${RAG_API_BASE}/rag/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    });
    if (!response.body) throw new Error('No response body');
    return response.body;
  },

  ingest: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const { data } = await ragApiClient.post('/rag/ingest', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  getStatus: async (): Promise<RAGStatus> => {
    const { data } = await ragApiClient.get('/rag/status');
    return data.data;
  },

  loadModel: async (request: ModelLoadRequest) => {
    const { data } = await ragApiClient.post('/rag/model/load', request);
    return data;
  },

  unloadModel: async () => {
    const { data } = await ragApiClient.post('/rag/model/unload');
    return data;
  },

  autoIngest: async () => {
    const { data } = await ragApiClient.post('/rag/knowledge-base/auto-ingest');
    return data;
  },

  getKnowledgeBaseStats: async () => {
    const { data } = await ragApiClient.get('/rag/knowledge-base/stats');
    return data.data;
  },
};
```

### 5.5 SSE Hook 设计

```typescript
// hooks/useSSE.ts

import { useCallback, useRef } from 'react';

interface SSECallbacks {
  onToken: (token: string) => void;
  onSources: (sources: Source[]) => void;
  onDone: () => void;
  onError: (error: Error) => void;
}

export function useSSE() {
  const abortControllerRef = useRef<AbortController | null>(null);

  const connect = useCallback(async (question: string, callbacks: SSECallbacks) => {
    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch('http://localhost:8001/api/rag/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
        signal: abortControllerRef.current.signal,
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) throw new Error('No reader available');

      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        let currentEvent = '';
        for (const line of lines) {
          if (line.startsWith('event: ')) {
            currentEvent = line.slice(7).trim();
          } else if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));
            switch (currentEvent) {
              case 'token':
                callbacks.onToken(data.token);
                break;
              case 'sources':
                callbacks.onSources(data.sources);
                break;
              case 'done':
                callbacks.onDone();
                break;
            }
          }
        }
      }
    } catch (error) {
      if (error instanceof DOMException && error.name === 'AbortError') return;
      callbacks.onError(error as Error);
    }
  }, []);

  const disconnect = useCallback(() => {
    abortControllerRef.current?.abort();
  }, []);

  return { connect, disconnect };
}
```

### 5.6 Zustand Store 设计

```typescript
// stores/chatStore.ts

import { create } from 'zustand';
import type { Message, Source } from '../types/chat';

interface ChatStore {
  messages: Message[];
  isLoading: boolean;
  currentStreamingContent: string;
  currentStreamingSources: Source[];

  addMessage: (message: Message) => void;
  appendStreamToken: (token: string) => void;
  finalizeStream: () => void;
  setLoading: (loading: boolean) => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatStore>((set, get) => ({
  messages: [],
  isLoading: false,
  currentStreamingContent: '',
  currentStreamingSources: [],

  addMessage: (message) => set((state) => ({
    messages: [...state.messages, message],
  })),

  appendStreamToken: (token) => set((state) => ({
    currentStreamingContent: state.currentStreamingContent + token,
  })),

  finalizeStream: () => {
    const { currentStreamingContent, currentStreamingSources, messages } = get();
    const assistantMessage: Message = {
      id: crypto.randomUUID(),
      role: 'assistant',
      content: currentStreamingContent,
      sources: currentStreamingSources,
      timestamp: Date.now(),
    };
    set({
      messages: [...messages, assistantMessage],
      currentStreamingContent: '',
      currentStreamingSources: [],
      isLoading: false,
    });
  },

  setLoading: (loading) => set({ isLoading: loading }),
  clearMessages: () => set({ messages: [], currentStreamingContent: '', currentStreamingSources: [] }),
}));
```

```typescript
// stores/appStore.ts

import { create } from 'zustand';
import type { RAGStatus } from '../types/rag';

interface AppStore {
  theme: 'light' | 'dark';
  ragStatus: RAGStatus | null;
  sidebarCollapsed: boolean;

  setTheme: (theme: 'light' | 'dark') => void;
  setRagStatus: (status: RAGStatus) => void;
  toggleSidebar: () => void;
}

export const useAppStore = create<AppStore>((set) => ({
  theme: 'light',
  ragStatus: null,
  sidebarCollapsed: false,

  setTheme: (theme) => set({ theme }),
  setRagStatus: (status) => set({ ragStatus: status }),
  toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
}));
```

### 5.7 Vite 代理配置

```typescript
// vite.config.ts

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api/skill-tree': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/api/rag': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
    },
  },
});
```

---

## 6. 数据流与交互设计

### 6.1 聊天流程

```
用户输入问题
    │
    ▼
ChatInput.onSubmit()
    │
    ├── 1. chatStore.addMessage({role: 'user', content: question})
    ├── 2. chatStore.setLoading(true)
    └── 3. useSSE.connect(question, callbacks)
            │
            ▼
        POST /api/rag/chat/stream
            │
            ▼
        RAG API Server
            │
            ├── 1. RAGAssistant.query_stream(question)
            │       ├── KnowledgeBase.similarity_search()
            │       ├── Reranker.rerank() (可选)
            │       └── TextIteratorStreamer → yield token
            │
            ▼
        SSE Response Stream
            │
            ├── event: token → chatStore.appendStreamToken(token)
            ├── event: sources → chatStore.currentStreamingSources = sources
            └── event: done → chatStore.finalizeStream()
                    │
                    ▼
                UI 自动更新 (React re-render)
```

### 6.2 模型加载流程

```
用户点击「启动AI引擎」
    │
    ▼
EngineControl.onLoad()
    │
    ├── 1. 收集配置 (model_key, use_reranker, reranker_model, ...)
    ├── 2. POST /api/rag/model/load
    │       │
    │       ▼
    │   RAG API Server
    │       │
    │       ├── KnowledgeBase() 初始化
    │       ├── RAGAssistant() 加载模型 (耗时 30-120s)
    │       └── 返回 {success: true, data: {...}}
    │
    ├── 3. 轮询 GET /api/rag/status (每 2s)
    │       └── 直到 engine_loaded === true
    └── 4. 更新 appStore.ragStatus
```

### 6.3 技能树 CRUD 流程

```
用户操作
    │
    ▼
skillTreeStore.action()
    │
    ▼
skillTreeApi.method()
    │
    ▼
GET/POST/DELETE /api/skill-tree/...
    │
    ▼
技能树 API (port 8000)
    │
    ▼
SkillTreeApplicationService → SkillTreeService → FileSkillTreeRepository
    │
    ▼
返回 JSON 响应
    │
    ▼
skillTreeStore 更新 → UI 自动刷新
```

### 6.4 页面路由设计

| 路径 | 组件 | 说明 |
|------|------|------|
| `/` | `ChatPage` | 智能问答（默认页） |
| `/skill-tree` | `SkillTreePage` | 技能树管理 |
| `/skill-tree/:id` | `SkillTreeDetail` | 技能树详情 |
| `/settings` | `SettingsPage` | 系统设置 |

---

## 7. 详细实施计划

### 7.1 阶段总览

```
阶段 1: 后端 API 拆分 ──────────────────────────── 预计 5-8 天
  ├─ 1.1 创建 RAG API 服务框架
  ├─ 1.2 实现单例管理与依赖注入
  ├─ 1.3 实现核心 API 路由
  ├─ 1.4 实现 SSE 流式响应
  ├─ 1.5 实现文件上传接口
  ├─ 1.6 实现模型加载/卸载接口
  ├─ 1.7 添加错误处理与日志中间件
  └─ 1.8 编写 API 测试

阶段 2: 前端基础搭建 ──────────────────────────── 预计 4-6 天
  ├─ 2.1 初始化 Vite + React + TypeScript 项目
  ├─ 2.2 配置 Ant Design + 主题
  ├─ 2.3 搭建路由与布局框架
  ├─ 2.4 封装 API Service 层
  ├─ 2.5 实现 Zustand Store
  └─ 2.6 配置 Vite 代理

阶段 3: 功能迁移 ──────────────────────────────── 预计 8-12 天
  ├─ 3.1 智能问答页面 (含 SSE 流式)
  ├─ 3.2 技能树列表页
  ├─ 3.3 技能树详情页
  ├─ 3.4 技能添加/关系表单
  ├─ 3.5 知识库管理面板
  ├─ 3.6 设置页面 (模型/重排序配置)
  └─ 3.7 引擎启停控制

阶段 4: 高级功能与优化 ────────────────────────── 预计 5-7 天
  ├─ 4.1 技能树可视化 (React Flow)
  ├─ 4.2 响应式适配
  ├─ 4.3 深色主题
  ├─ 4.4 性能优化 (懒加载、缓存)
  └─ 4.5 启动脚本更新

阶段 5: 测试与上线 ────────────────────────────── 预计 3-5 天
  ├─ 5.1 端到端功能测试
  ├─ 5.2 兼容性测试
  ├─ 5.3 性能基准测试
  └─ 5.4 文档与部署
```

### 7.2 阶段 1 详细任务

| 任务 ID | 任务描述 | 交付物 | 依赖 |
|---------|---------|--------|------|
| 1.1 | 创建 `src/rag_api/` 目录结构，含 `__init__.py`, `app.py`, `routes.py`, `models.py`, `dependencies.py`, `middleware.py` | 目录与文件 | 无 |
| 1.2 | 实现 `dependencies.py`：KnowledgeBase 单例、RAGAssistant 单例管理、生命周期控制 | `dependencies.py` | 1.1 |
| 1.3 | 实现 `models.py`：Pydantic 请求/响应模型 (ChatRequest, ChatResponse, ModelLoadRequest, StatusResponse 等) | `models.py` | 1.1 |
| 1.4 | 实现 `/api/rag/chat` 普通问答路由 | `routes.py` 片段 | 1.2, 1.3 |
| 1.5 | 实现 `/api/rag/chat/stream` SSE 流式路由 | `routes.py` 片段 | 1.2, 1.3 |
| 1.6 | 实现 `/api/rag/status` 状态查询路由 | `routes.py` 片段 | 1.2 |
| 1.7 | 实现 `/api/rag/model/load` 和 `/api/rag/model/unload` | `routes.py` 片段 | 1.2, 1.3 |
| 1.8 | 实现 `/api/rag/ingest` 文件上传路由 | `routes.py` 片段 | 1.2 |
| 1.9 | 实现 `/api/rag/knowledge-base/auto-ingest` 和 `/api/rag/knowledge-base/stats` | `routes.py` 片段 | 1.2 |
| 1.10 | 实现 `middleware.py`：统一错误处理、请求日志、CORS | `middleware.py` | 1.1 |
| 1.11 | 创建 `rag_server.py` 启动入口 | `rag_server.py` | 1.4-1.10 |
| 1.12 | 更新 `config/config.yaml` 添加 `rag_port` | `config.yaml` | 1.11 |
| 1.13 | 编写 API 测试 (`tests/test_rag_api.py`) | 测试文件 | 1.11 |
| 1.14 | 使用 Swagger UI 验证所有 API | 验证报告 | 1.13 |

### 7.3 阶段 2 详细任务

| 任务 ID | 任务描述 | 交付物 | 依赖 |
|---------|---------|--------|------|
| 2.1 | `npm create vite@latest frontend -- --template react-ts` 初始化项目 | `frontend/` 目录 | 阶段 1 完成 |
| 2.2 | 安装依赖：antd, @ant-design/icons, zustand, react-router-dom, axios | `package.json` | 2.1 |
| 2.3 | 配置 Ant Design 主题（主色 #1f77b4，圆角等） | `App.tsx` ConfigProvider | 2.2 |
| 2.4 | 实现 `AppLayout.tsx`：左侧边栏 + 顶部导航 + 内容区 | 布局组件 | 2.3 |
| 2.5 | 实现 `Sidebar.tsx`：导航菜单 + 知识库状态 + 引擎状态 | 侧边栏组件 | 2.4 |
| 2.6 | 配置 React Router：`/`, `/skill-tree`, `/skill-tree/:id`, `/settings` | 路由配置 | 2.4 |
| 2.7 | 实现 `services/api.ts`：axios 实例、拦截器、错误处理 | API 基础层 | 2.2 |
| 2.8 | 实现 `services/ragApi.ts` 和 `services/skillTreeApi.ts` | API 封装 | 2.7 |
| 2.9 | 实现 `stores/chatStore.ts`, `stores/skillTreeStore.ts`, `stores/appStore.ts` | 状态管理 | 2.2 |
| 2.10 | 配置 `vite.config.ts` 代理规则 | Vite 配置 | 2.1 |
| 2.11 | 实现 `hooks/useSSE.ts` | SSE Hook | 2.7 |
| 2.12 | 定义所有 TypeScript 类型 (`types/`) | 类型文件 | 2.1 |

### 7.4 阶段 3 详细任务

| 任务 ID | 任务描述 | 交付物 | 依赖 |
|---------|---------|--------|------|
| 3.1 | 实现 `ChatPage.tsx` + `ChatWindow.tsx`：消息列表、输入框、欢迎卡片 | 问答页面 | 阶段 2 |
| 3.2 | 实现 `MessageBubble.tsx`：用户/助手消息气泡，支持 Markdown 渲染 | 消息组件 | 3.1 |
| 3.3 | 实现 `ThinkingIndicator.tsx`：思考中动画（三点跳动） | 动画组件 | 3.1 |
| 3.4 | 实现 `SourcePanel.tsx`：参考来源折叠面板 | 来源组件 | 3.2 |
| 3.5 | 实现 `ChatInput.tsx`：输入框 + 发送按钮 + 文件上传图标 | 输入组件 | 3.1 |
| 3.6 | 集成 SSE 流式输出到 ChatWindow | 完整问答功能 | 3.1-3.5 |
| 3.7 | 实现 `SkillTreePage.tsx` + `SkillTreeList.tsx`：技能树列表与创建 | 技能树列表 | 阶段 2 |
| 3.8 | 实现 `SkillTreeDetail.tsx`：技能树详情展示 | 详情页 | 3.7 |
| 3.9 | 实现 `AddSkillForm.tsx`：添加技能表单 | 表单组件 | 3.8 |
| 3.10 | 实现 `RelationForm.tsx`：建立技能关系表单 | 表单组件 | 3.8 |
| 3.11 | 实现 `LearningPathList.tsx`：学习路径列表 | 路径组件 | 3.8 |
| 3.12 | 实现 `KnowledgeBasePanel.tsx` + `FileUploader.tsx` | 知识库面板 | 阶段 2 |
| 3.13 | 实现 `SettingsPage.tsx` + `ModelSelector.tsx` + `RerankerConfig.tsx` | 设置页面 | 阶段 2 |
| 3.14 | 实现 `EngineControl.tsx`：引擎启停、状态显示 | 引擎控制 | 3.13 |

### 7.5 阶段 4 详细任务

| 任务 ID | 任务描述 | 交付物 | 依赖 |
|---------|---------|--------|------|
| 4.1 | 集成 React Flow，实现 `SkillGraph.tsx`：交互式技能树可视化 | 可视化组件 | 阶段 3 |
| 4.2 | 实现节点拖拽、缩放、连线交互 | 交互功能 | 4.1 |
| 4.3 | 响应式布局适配（移动端侧边栏折叠、消息全宽等） | 响应式 CSS | 阶段 3 |
| 4.4 | 实现深色主题（Ant Design dark theme + 自定义 CSS 变量） | 主题切换 | 阶段 3 |
| 4.5 | 性能优化：React.lazy 路由懒加载、消息列表虚拟滚动 | 优化代码 | 阶段 3 |
| 4.6 | 更新 `start.bat` / `start.sh` 启动脚本 | 启动脚本 | 4.5 |

---

## 8. 测试策略

### 8.1 后端测试

| 测试类型 | 范围 | 工具 | 目标 |
|---------|------|------|------|
| 单元测试 | RAG API 路由逻辑 | pytest + httpx | 覆盖所有 API 端点 |
| 集成测试 | SSE 流式响应 | pytest + SSE 客户端 | 验证流式数据完整性 |
| 接口测试 | API 契约验证 | Swagger UI + curl | 验证请求/响应格式 |

**关键测试用例：**

```python
# tests/test_rag_api.py

def test_status_before_model_load():
    """模型未加载时，status 应返回 engine_loaded=false"""
    response = client.get("/api/rag/status")
    assert response.json()["data"]["engine_loaded"] is False

def test_load_model():
    """加载模型后，status 应返回 engine_loaded=true"""
    response = client.post("/api/rag/model/load", json={
        "model_key": "qwen2-0.5b",
        "use_reranker": False
    })
    assert response.json()["success"] is True

def test_chat_stream():
    """流式问答应返回 SSE 事件流"""
    with client.stream("POST", "/api/rag/chat/stream", json={"question": "测试"}) as response:
        events = parse_sse(response)
        assert any(e["event"] == "token" for e in events)
        assert any(e["event"] == "done" for e in events)

def test_ingest_file():
    """文件上传应成功导入知识库"""
    response = client.post("/api/rag/ingest", files={"file": ("test.md", content)})
    assert response.json()["success"] is True
```

### 8.2 前端测试

| 测试类型 | 范围 | 工具 | 目标 |
|---------|------|------|------|
| 组件测试 | UI 组件渲染与交互 | Vitest + React Testing Library | 组件行为正确 |
| Hook 测试 | useChat, useSSE | Vitest + renderHook | Hook 逻辑正确 |
| E2E 测试 | 关键用户流程 | Playwright | 端到端功能验证 |

**关键 E2E 测试场景：**

1. 启动 AI 引擎 → 发送问题 → 收到流式回答 → 查看参考来源
2. 创建技能树 → 添加技能 → 建立关系 → 生成学习路径
3. 上传文档 → 导入知识库 → 验证知识库统计更新
4. 切换模型 → 验证状态更新 → 重新问答

### 8.3 功能等价验证清单

| # | 原有功能 (Streamlit) | 新功能 (React) | 验证方法 |
|---|---------------------|---------------|---------|
| 1 | 侧边栏知识库状态显示 | Sidebar 知识库状态 | 视觉对比 |
| 2 | 侧边栏文件上传 | FileUploader 组件 | 上传同一文件，对比导入结果 |
| 3 | 侧边栏 AI 引擎启停 | EngineControl 组件 | 对比启动/停止行为 |
| 4 | 侧边栏重排序配置 | RerankerConfig 组件 | 对比配置项与参数 |
| 5 | 侧边栏模型选择 | ModelSelector 组件 | 对比可选模型列表 |
| 6 | 聊天消息气泡（用户/助手） | MessageBubble 组件 | 视觉对比 |
| 7 | 流式输出打字机效果 | SSE + appendStreamToken | 对比输出速度与内容 |
| 8 | 思考中动画 | ThinkingIndicator | 视觉对比 |
| 9 | 参考来源折叠面板 | SourcePanel | 对比来源内容 |
| 10 | 预制问题按钮 | WelcomeCard 示例问题 | 对比点击行为 |
| 11 | 技能树列表/创建/删除 | SkillTreeList | 对比 CRUD 结果 |
| 12 | 添加技能表单 | AddSkillForm | 对比表单字段与提交 |
| 13 | 建立技能关系 | RelationForm | 对比关系建立结果 |
| 14 | 学习路径展示 | LearningPathList | 对比路径内容 |
| 15 | 页脚信息 | Footer | 视觉对比 |

---

## 9. 部署方案

### 9.1 开发环境

```bash
# Terminal 1: 技能树 API
python server.py

# Terminal 2: RAG API
python rag_server.py

# Terminal 3: 前端开发服务器
cd frontend
npm run dev
```

### 9.2 生产环境

**方案 A：Nginx 反向代理（推荐）**

```nginx
# nginx.conf

upstream skill_tree_api {
    server 127.0.0.1:8000;
}

upstream rag_api {
    server 127.0.0.1:8001;
}

server {
    listen 80;
    server_name localhost;

    # 前端静态文件
    location / {
        root /var/www/ascend-rag/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 技能树 API
    location /api/skill-tree/ {
        proxy_pass http://skill_tree_api;
        proxy_set_header Host $host;
    }

    # RAG API (含 SSE)
    location /api/rag/ {
        proxy_pass http://rag_api;
        proxy_set_header Host $host;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        proxy_buffering off;           # SSE 必须关闭缓冲
        proxy_cache off;
        proxy_read_timeout 300s;       # 长连接超时
    }
}
```

**方案 B：Docker Compose**

```yaml
# docker-compose.yml

version: '3.8'

services:
  skill-tree-api:
    build: .
    command: python server.py
    ports:
      - "8000:8000"
    volumes:
      - ./skill_tree_data:/app/skill_tree_data
      - ./config:/app/config

  rag-api:
    build: .
    command: python rag_server.py
    ports:
      - "8001:8001"
    volumes:
      - ./chroma_db:/app/chroma_db
      - ./models:/app/models
      - ./data:/app/data:ro
      - ./config:/app/config
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - skill-tree-api
      - rag-api
```

### 9.3 启动脚本更新

```bat
@echo off
chcp 65001 >nul
echo ========================================
echo    Ascend RAG Assistant 一键启动
echo ========================================
echo.
echo 设置环境变量解决OMP冲突...
set KMP_DUPLICATE_LIB_OK=TRUE
echo.
echo 启动技能树API服务器...
start "SkillTree API" python server.py
echo.
echo 启动RAG API服务器...
start "RAG API" python rag_server.py
echo.
echo 等待API服务器启动...
timeout /t 5 /nobreak >nul
echo.
echo 启动前端开发服务器...
cd frontend
start "React Frontend" npm run dev
echo.
echo ========================================
echo    所有服务已启动！
echo    前端: http://localhost:5173
echo    技能树API: http://localhost:8000/docs
echo    RAG API: http://localhost:8001/docs
echo ========================================
pause
```

---

## 10. 风险管理与回滚策略

### 10.1 技术风险

| 风险 | 可能性 | 影响 | 对策 | 负责阶段 |
|------|--------|------|------|---------|
| SSE 在代理/防火墙下不稳定 | 中 | 高 | 1. Nginx 关闭 proxy_buffering<br>2. 备选方案：WebSocket 或长轮询 | 阶段 1 |
| 模型加载耗时过长 (>120s) | 高 | 中 | 1. 前端显示进度条<br>2. 后台异步加载 + 状态轮询<br>3. 首次加载后缓存到磁盘 | 阶段 1, 3 |
| 大文件上传超时 | 中 | 低 | 1. 限制文件大小 (50MB)<br>2. 分片上传<br>3. 后台异步处理 | 阶段 1 |
| React Flow 性能问题 (节点过多) | 低 | 中 | 1. 虚拟化渲染<br>2. 限制可视节点数<br>3. 懒加载子树 | 阶段 4 |
| CORS 跨域问题 | 中 | 低 | 1. Vite 代理 (开发)<br>2. Nginx 同源 (生产) | 阶段 2 |

### 10.2 迁移风险

| 风险 | 可能性 | 影响 | 对策 |
|------|--------|------|------|
| 功能遗漏 | 中 | 高 | 使用功能等价验证清单逐项检查 |
| 流式输出体验下降 | 中 | 中 | 对比 Streamlit 与 React 的流式体验，优化 token 渲染频率 |
| 用户习惯改变 | 低 | 低 | 保持 UI 布局与 Streamlit 版本相似 |
| 部署复杂度增加 | 中 | 中 | 提供 Docker Compose 一键部署 |

### 10.3 回滚策略

1. **代码层面**：Git 分支管理，`main` 保持 Streamlit 版本，`feature/react-migration` 开发新版本
2. **运行层面**：通过环境变量 `FRONTEND_MODE=streamlit|react` 切换
3. **数据层面**：技能树数据 (JSON) 和知识库数据 (ChromaDB) 不受前端迁移影响
4. **并行运行**：开发期间 Streamlit (8501) 和 React (5173) 可同时运行

---

## 11. 验收标准

### 11.1 功能验收

- [ ] 所有 15 项功能等价验证清单通过
- [ ] SSE 流式输出延迟 < 200ms（首 token）
- [ ] 技能树 CRUD 操作与原版行为一致
- [ ] 文件上传功能正常（PDF/TXT/MD）
- [ ] 模型加载/卸载功能正常
- [ ] 重排序配置可正常调整并生效

### 11.2 性能验收

| 指标 | 目标 | 测量方法 |
|------|------|---------|
| 首屏加载时间 | < 2s | Lighthouse Performance |
| 页面切换时间 | < 300ms | React Profiler |
| 流式首 token 延迟 | < 200ms | 端到端计时 |
| 技能树列表加载 | < 500ms | API 响应时间 |
| Lighthouse Performance 评分 | > 80 | Lighthouse |

### 11.3 质量验收

- [ ] TypeScript 严格模式无错误
- [ ] ESLint 无 error 级别警告
- [ ] 后端 API 测试覆盖率 > 80%
- [ ] 前端组件测试覆盖核心组件
- [ ] E2E 测试覆盖 4 个关键场景

---

## 附录

### A. 完整 API 路由汇总

**技能树 API (port 8000)：**

| 方法 | 路径 | 功能 | 状态 |
|------|------|------|------|
| POST | `/api/skill-tree/` | 创建技能树 | ✅ 已有 |
| GET | `/api/skill-tree/` | 列出所有技能树 | ✅ 已有 |
| GET | `/api/skill-tree/{id}` | 获取技能树详情 | ✅ 已有 |
| DELETE | `/api/skill-tree/{id}` | 删除技能树 | ✅ 已有 |
| POST | `/api/skill-tree/{id}/skills` | 添加技能 | ✅ 已有 |
| POST | `/api/skill-tree/{id}/skills/relation` | 建立技能关系 | ✅ 已有 |
| POST | `/api/skill-tree/{id}/skills/{skill_id}/resources` | 添加学习资源 | ✅ 已有 |
| PUT | `/api/skill-tree/{id}/skills/{skill_id}/completion` | 更新完成率 | ✅ 已有 |
| POST | `/api/skill-tree/{id}/paths/generate` | 生成学习路径 | ✅ 已有 |

**RAG API (port 8001)：**

| 方法 | 路径 | 功能 | 状态 |
|------|------|------|------|
| POST | `/api/rag/chat` | 普通问答 | 🆕 新建 |
| POST | `/api/rag/chat/stream` | 流式问答 (SSE) | 🆕 新建 |
| POST | `/api/rag/ingest` | 上传文档 | 🆕 新建 |
| GET | `/api/rag/status` | 获取系统状态 | 🆕 新建 |
| POST | `/api/rag/model/load` | 加载模型 | 🆕 新建 |
| POST | `/api/rag/model/unload` | 卸载模型 | 🆕 新建 |
| POST | `/api/rag/knowledge-base/auto-ingest` | 自动导入知识库 | 🆕 新建 |
| GET | `/api/rag/knowledge-base/stats` | 知识库统计 | 🆕 新建 |

### B. 前端依赖清单

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "antd": "^5.12.0",
    "@ant-design/icons": "^5.2.0",
    "zustand": "^4.4.0",
    "axios": "^1.6.0",
    "@xyflow/react": "^12.0.0",
    "dayjs": "^1.11.0",
    "react-markdown": "^9.0.0"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.2.0",
    "eslint": "^8.55.0",
    "prettier": "^3.1.0",
    "vitest": "^1.0.0",
    "@testing-library/react": "^14.0.0",
    "@playwright/test": "^1.40.0"
  }
}
```

### C. 关键文件变更清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `rag_server.py` | 🆕 新建 | RAG API 启动入口 |
| `src/rag_api/__init__.py` | 🆕 新建 | RAG API 包初始化 |
| `src/rag_api/app.py` | 🆕 新建 | FastAPI 应用工厂 |
| `src/rag_api/routes.py` | 🆕 新建 | RAG API 路由 |
| `src/rag_api/models.py` | 🆕 新建 | Pydantic 模型 |
| `src/rag_api/dependencies.py` | 🆕 新建 | 依赖注入 |
| `src/rag_api/middleware.py` | 🆕 新建 | 中间件 |
| `config/config.yaml` | ✏️ 修改 | 新增 rag_port |
| `server.py` | ✏️ 修改 | CORS 更新 |
| `frontend/` | 🆕 新建 | 整个前端项目 |
| `start.bat` / `start.sh` | ✏️ 修改 | 新增 RAG API 启动 |
| `app.py` | 🔒 保留 | Streamlit 版本保留作为回滚 |
| `src/rag_engine.py` | 🔒 保留 | 不修改，被 RAG API 引用 |
| `src/knowledge_base.py` | 🔒 保留 | 不修改，被 RAG API 引用 |
| `tests/test_rag_api.py` | 🆕 新建 | RAG API 测试 |

---

**文档结束**
