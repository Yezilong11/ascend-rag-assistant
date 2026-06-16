# 阶段一：后端 API 拆分 — 详细实施计划

> 基于 `d:\ascend-rag-assistant\doc\2026-05-02-frontend-modernization-plan.md` 第4章、第7.2节
> 目标：将 RAG 引擎从 Streamlit 前端解耦，封装为独立 FastAPI 微服务 (port 8001)

---

## 总览

阶段一包含 14 个任务（Task 1.1 ~ Task 1.14），按依赖关系分为 4 个执行批次：

| 批次 | 任务 | 前置依赖 | 可并行 |
|------|------|---------|--------|
| 批次A | 1.1, 1.2, 1.3 | 无 | 三者可并行 |
| 批次B | 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10 | 批次A | 七者可并行 |
| 批次C | 1.11, 1.12 | 批次B | 两者可并行 |
| 批次D | 1.13, 1.14 | 批次C | 串行 |

---

## Task 1.1: 创建 RAG API 服务框架

### 执行内容

在 `src/` 目录下创建 `rag_api/` Python 包，包含以下文件：

| 文件 | 初始内容 | 职责 |
|------|---------|------|
| `src/rag_api/__init__.py` | 空文件或版本号常量 | 包标识 |
| `src/rag_api/app.py` | `create_app()` 工厂函数骨架 | FastAPI 应用创建与配置 |
| `src/rag_api/routes.py` | `router = APIRouter(prefix="/api/rag", tags=["rag"])` | 路由注册 |
| `src/rag_api/models.py` | 空文件 | Pydantic 模型占位 |
| `src/rag_api/dependencies.py` | 空文件 | 依赖注入占位 |
| `src/rag_api/middleware.py` | 空文件 | 中间件占位 |

### 技术要点

1. **`app.py` 工厂模式**：使用 `create_app()` 函数而非模块级 `app = FastAPI()`，便于测试时创建独立实例
2. **路由注册**：在 `create_app()` 中通过 `app.include_router(router)` 注册路由
3. **CORS 配置**：在 `create_app()` 中添加 CORSMiddleware，允许 `http://localhost:5173` 和 `http://localhost:8501`
4. **参考现有 `server.py`**：保持与技能树 API 一致的代码风格（yaml 配置读取、uvicorn 启动方式）

### 执行提示词

```
在 d:\ascend-rag-assistant\src\rag_api\ 目录下创建 RAG API 服务框架。

创建以下文件：
1. __init__.py — 空文件
2. app.py — 包含 create_app() 工厂函数，返回配置好 CORS 和路由的 FastAPI 实例。
   CORS 允许 origins: ["http://localhost:5173", "http://localhost:8501", "http://localhost:3000"]。
   在 create_app() 中 include_router(router)，router 从 routes.py 导入。
   添加根路由 GET "/" 返回 {"message": "RAG API服务正常运行", "docs": "/docs"}。
3. routes.py — 创建 APIRouter(prefix="/api/rag", tags=["rag"])，暂无路由。
4. models.py — 空文件
5. dependencies.py — 空文件
6. middleware.py — 空文件

参考 d:\ascend-rag-assistant\server.py 的代码风格，保持一致。
不要添加任何注释。
```

### 验收标准

| 验证项 | 方法 | 通过条件 |
|--------|------|---------|
| 目录结构完整 | `ls src/rag_api/` | 6 个文件均存在 |
| 包可导入 | `python -c "from src.rag_api.app import create_app"` | 无报错 |
| FastAPI 实例可创建 | `python -c "from src.rag_api.app import create_app; app = create_app(); print(app.title)"` | 输出应用标题 |
| 路由前缀正确 | 检查 `routes.py` 中 `APIRouter` 的 prefix 参数 | prefix="/api/rag" |

---

## Task 1.2: 实现单例管理与依赖注入

### 执行内容

实现 `src/rag_api/dependencies.py`，管理 KnowledgeBase 和 RAGAssistant 的单例生命周期。

### 技术要点

1. **模块级全局变量**：使用 `_rag_assistant` 和 `_knowledge_base` 模块级变量持有单例，而非 `lru_cache`（因为 RAGAssistant 需要动态替换）
2. **KnowledgeBase 惰性初始化**：首次调用 `get_knowledge_base()` 时创建实例，后续调用返回同一实例
3. **RAGAssistant 动态管理**：通过 `set_rag_assistant()` 设置（模型加载后），通过 `get_rag_assistant()` 获取（可能返回 None）
4. **线程安全**：RAGAssistant 的 `query_stream()` 内部已使用 threading，API 层面无需额外加锁（FastAPI 异步处理单请求）
5. **配置参数**：KnowledgeBase 初始化参数从 `config.yaml` 读取（persist_dir, model_dir）

### 执行提示词

```
实现 d:\ascend-rag-assistant\src\rag_api\dependencies.py，管理 RAG 引擎和知识库的单例生命周期。

需要实现：
1. 模块级全局变量 _rag_assistant (初始 None) 和 _knowledge_base (初始 None)
2. get_knowledge_base() -> KnowledgeBase：惰性初始化，首次调用时创建 KnowledgeBase 实例。
   参数从 config/config.yaml 的 knowledge_base 节读取 persist_dir 和 embedding_model，
   model_dir 默认 "./models"。后续调用返回同一实例。
3. get_rag_assistant() -> RAGAssistant | None：返回当前 RAGAssistant 实例，可能为 None
4. set_rag_assistant(assistant: RAGAssistant)：设置 RAGAssistant 实例
5. clear_rag_assistant()：将 _rag_assistant 设为 None，并尝试释放 GPU 显存
   (del assistant.model, del assistant.pipeline_obj, torch.cuda.empty_cache())

从 src.rag_engine 导入 RAGAssistant 和 PREDEFINED_MODELS, PREDEFINED_RERANKERS。
从 src.knowledge_base 导入 KnowledgeBase。
不要添加任何注释。
```

### 验收标准

| 验证项 | 方法 | 通过条件 |
|--------|------|---------|
| KnowledgeBase 单例 | 连续两次调用 `get_knowledge_base()`，比较 `id()` | 返回同一对象 |
| RAGAssistant 初始为 None | 调用 `get_rag_assistant()` | 返回 None |
| set/get 配对 | `set_rag_assistant(mock_obj)` 后调用 `get_rag_assistant()` | 返回 mock_obj |
| clear 生效 | `clear_rag_assistant()` 后调用 `get_rag_assistant()` | 返回 None |
| 模块可导入 | `python -c "from src.rag_api.dependencies import get_knowledge_base, get_rag_assistant"` | 无报错 |

---

## Task 1.3: 实现 Pydantic 请求/响应模型

### 执行内容

实现 `src/rag_api/models.py`，定义所有 API 端点的请求和响应 Pydantic 模型。

### 技术要点

1. **请求模型**：
   - `ChatRequest`: question (str, 必填, min_length=1)
   - `ModelLoadRequest`: model_key, model_dir, use_reranker, reranker_model, reranker_top_k, initial_retrieval_k
   - `IngestRequest`: 无（使用 UploadFile，不需要 Pydantic 模型）
2. **响应模型**：统一使用 `Dict[str, Any]` 返回，与现有技能树 API 风格一致（`{success, data/message}`）
3. **字段验证**：model_key 必须在 PREDEFINED_MODELS 中；reranker_model 必须在 PREDEFINED_RERANKERS 中
4. **可选字段默认值**：model_dir 默认 "./models"，use_reranker 默认 True，reranker_top_k 默认 3，initial_retrieval_k 默认 10

### 执行提示词

```
实现 d:\ascend-rag-assistant\src\rag_api\models.py，定义 RAG API 的 Pydantic 请求模型。

需要实现：
1. ChatRequest(BaseModel)：
   - question: str (min_length=1, description="用户问题")

2. ModelLoadRequest(BaseModel)：
   - model_key: str (description="预定义模型key，如 qwen2-1.5b")
   - model_dir: str = "./models"
   - use_reranker: bool = True
   - reranker_model: str = "bge-reranker-v2-m3"
   - reranker_top_k: int = 3 (ge=1, le=10)
   - initial_retrieval_k: int = 10 (ge=3, le=30)

3. ModelUnloadResponse(BaseModel)：
   - success: bool
   - message: str

4. IngestResponse(BaseModel)：
   - success: bool
   - data: dict | None = None
   - message: str | None = None

5. StatusResponse(BaseModel)：
   - success: bool
   - data: dict | None = None

6. ChatResponse(BaseModel)：
   - success: bool
   - data: dict | None = None
   - message: str | None = None

使用 pydantic 的 BaseModel，从 pydantic 导入。
不要添加任何注释。
```

### 验收标准

| 验证项 | 方法 | 通过条件 |
|--------|------|---------|
| ChatRequest 验证 | `ChatRequest(question="")` | 抛出 ValidationError |
| ChatRequest 正常 | `ChatRequest(question="测试")` | 创建成功 |
| ModelLoadRequest 默认值 | `ModelLoadRequest(model_key="qwen2-1.5b")` | use_reranker=True, reranker_top_k=3 |
| ModelLoadRequest 边界 | `ModelLoadRequest(model_key="x", reranker_top_k=0)` | 抛出 ValidationError (ge=1) |
| 所有模型可导入 | `from src.rag_api.models import ChatRequest, ModelLoadRequest, ...` | 无报错 |

---

## Task 1.4: 实现普通问答路由 `/api/rag/chat`

### 执行内容

在 `src/rag_api/routes.py` 中实现 POST `/api/rag/chat` 路由。

### 技术要点

1. **依赖注入**：通过 `Depends(get_rag_assistant)` 获取 RAGAssistant 实例
2. **引擎未加载处理**：assistant 为 None 时返回 HTTP 503 Service Unavailable
3. **调用方式**：使用 `assistant.query(question)` 获取完整结果，返回 `{success: True, data: {answer, sources}}`
4. **异常处理**：捕获 RAGAssistant.query() 内部异常，返回 `{success: False, message: str(e)}`
5. **响应格式**：与设计文档 4.1.3 节完全一致

### 执行提示词

```
在 d:\ascend-rag-assistant\src\rag_api\routes.py 中实现 POST /api/rag/chat 路由。

router 已存在 (APIRouter prefix="/api/rag" tags=["rag"])，添加以下路由：

@router.post("/chat")
async def chat(request: ChatRequest, assistant = Depends(get_rag_assistant)):
    如果 assistant 为 None，抛出 HTTPException(status_code=503, detail="RAG引擎未加载，请先调用 /api/rag/model/load")
    try:
        result = assistant.query(request.question)
        return {"success": True, "data": {"answer": result["answer"], "sources": result["sources"]}}
    except Exception as e:
        return {"success": False, "message": f"问答处理失败: {str(e)}"}

从 fastapi 导入 APIRouter, HTTPException, Depends。
从 src.rag_api.models 导入 ChatRequest。
从 src.rag_api.dependencies 导入 get_rag_assistant。
不要添加任何注释。
```

### 验收标准

| 验证项 | 方法 | 通过条件 |
|--------|------|---------|
| 引擎未加载时 503 | curl POST `/api/rag/chat` (未加载模型) | 返回 503 |
| 正常问答 | curl POST `/api/rag/chat` (已加载模型) | 返回 `{success: true, data: {answer, sources}}` |
| 空问题拒绝 | POST `{"question": ""}` | 返回 422 Validation Error |
| 异常处理 | 模拟 query() 抛出异常 | 返回 `{success: false, message: ...}` |

---

## Task 1.5: 实现 SSE 流式问答路由 `/api/rag/chat/stream`

### 执行内容

在 `src/rag_api/routes.py` 中实现 POST `/api/rag/chat/stream` SSE 路由。

### 技术要点

1. **SSE 协议格式**：每条消息格式为 `event: <type>\ndata: <json>\n\n`，严格遵守 SSE 规范
2. **三种事件类型**：
   - `event: token` — 携带 `{"token": "文字片段"}`，逐 token 推送
   - `event: sources` — 携带 `{"sources": [...]}`，推送参考来源
   - `event: done` — 携带 `{}`，标记流结束
3. **StreamingResponse**：使用 `fastapi.responses.StreamingResponse`，media_type 为 `text/event-stream`
4. **关键 HTTP 头**：
   - `Cache-Control: no-cache` — 禁止缓存
   - `Connection: keep-alive` — 保持连接
   - `X-Accel-Buffering: no` — Nginx 环境下禁止缓冲
5. **生成器函数**：使用同步生成器 `event_generator()` 包装 `assistant.query_stream()` 的迭代输出
6. **来源获取**：流式输出结束后，从 `assistant._last_sources` 获取参考来源

### 执行提示词

```
在 d:\ascend-rag-assistant\src\rag_api\routes.py 中实现 POST /api/rag/chat/stream SSE 流式路由。

添加以下路由：

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest, assistant = Depends(get_rag_assistant)):
    如果 assistant 为 None，抛出 HTTPException(status_code=503, detail="RAG引擎未加载")

    def event_generator():
        for token in assistant.query_stream(request.question):
            yield f"event: token\ndata: {json.dumps({'token': token}, ensure_ascii=False)}\n\n"
        sources = assistant._last_sources or []
        yield f"event: sources\ndata: {json.dumps({'sources': sources}, ensure_ascii=False)}\n\n"
        yield f"event: done\ndata: {{}}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"}
    )

需要导入 json, 以及从 fastapi.responses 导入 StreamingResponse。
不要添加任何注释。
```

### 验收标准

| 验证项 | 方法 | 通过条件 |
|--------|------|---------|
| SSE 响应头 | curl POST，检查 Content-Type | `text/event-stream` |
| token 事件 | curl 接收流，检查事件格式 | `event: token\ndata: {"token": "..."}\n\n` |
| sources 事件 | 流结束后检查 | `event: sources\ndata: {"sources": [...]}\n\n` |
| done 事件 | 流最后一条消息 | `event: done\ndata: {}\n\n` |
| 引擎未加载 503 | 未加载模型时请求 | 返回 503 |
| 中文正常输出 | 发送中文问题 | token 中中文不乱码 (ensure_ascii=False) |

---

## Task 1.6: 实现状态查询路由 `/api/rag/status`

### 执行内容

在 `src/rag_api/routes.py` 中实现 GET `/api/rag/status` 路由。

### 技术要点

1. **无需引擎加载**：此路由在引擎未加载时也可调用，返回 `engine_loaded: false`
2. **返回字段**：engine_loaded, model_key, model_name, reranker_enabled, reranker_model, knowledge_base_ready, available_models, available_rerankers
3. **KnowledgeBase 状态**：通过 `get_knowledge_base()` 获取实例，检查是否初始化成功
4. **available_models 来源**：从 `RAGAssistant.get_available_models()` 获取（类方法，无需实例）
5. **available_rerankers 来源**：从 `RAGAssistant.get_available_rerankers()` 获取

### 执行提示词

```
在 d:\ascend-rag-assistant\src\rag_api\routes.py 中实现 GET /api/rag/status 路由。

添加以下路由：

@router.get("/status")
async def get_status():
    assistant = get_rag_assistant()
    kb = get_knowledge_base()
    status_data = {
        "engine_loaded": assistant is not None,
        "model_key": assistant.model_key if assistant else "",
        "model_name": PREDEFINED_MODELS.get(assistant.model_key, {}).get("name", "") if assistant else "",
        "reranker_enabled": assistant.use_reranker if assistant else False,
        "reranker_model": assistant.reranker.model_name if assistant and assistant.reranker else "",
        "knowledge_base_ready": kb is not None,
        "available_models": {k: {"name": v["name"], "description": v["description"]} for k, v in PREDEFINED_MODELS.items()},
        "available_rerankers": {k: {"name": v["name"], "description": v["description"], "size": v["size"]} for k, v in PREDEFINED_RERANKERS.items()}
    }
    return {"success": True, "data": status_data}

从 src.rag_api.dependencies 导入 get_rag_assistant, get_knowledge_base。
从 src.rag_engine 导入 PREDEFINED_MODELS, PREDEFINED_RERANKERS。
不要添加任何注释。
```

### 验收标准

| 验证项 | 方法 | 通过条件 |
|--------|------|---------|
| 引擎未加载时 | GET `/api/rag/status` (未加载模型) | `engine_loaded: false`, available_models 非空 |
| 引擎已加载时 | GET `/api/rag/status` (已加载模型) | `engine_loaded: true`, model_key 非空 |
| available_models 完整 | 检查响应 | 包含 qwen2-1.5b, qwen2-0.5b, chatglm3-6b |
| available_rerankers 完整 | 检查响应 | 包含 bge-reranker-v2-m3, bge-reranker-large, bge-reranker-base |
| knowledge_base_ready | 检查响应 | 值为 true（KB 在服务启动时初始化） |

---

## Task 1.7: 实现模型加载/卸载路由

### 执行内容

在 `src/rag_api/routes.py` 中实现 POST `/api/rag/model/load` 和 POST `/api/rag/model/unload` 路由。

### 技术要点

1. **模型加载是耗时操作**：RAGAssistant 初始化需要 30-120 秒（加载模型到 GPU），必须使用后台线程
2. **异步加载方案**：
   - `/model/load` 立即返回 `{success: true, data: {status: "loading"}}` 
   - 前端通过轮询 `/status` 检测 `engine_loaded` 变为 true
3. **线程安全**：使用 `threading.Thread` 在后台执行模型加载，设置全局 `_rag_assistant`
4. **卸载模型**：删除模型对象并调用 `torch.cuda.empty_cache()` 释放显存
5. **防重复加载**：如果引擎已加载，先卸载再加载
6. **加载状态标记**：添加 `_is_loading` 全局变量防止并发加载

### 执行提示词

```
在 d:\ascend-rag-assistant\src\rag_api\routes.py 中实现模型加载和卸载路由。

在 dependencies.py 中添加：
- _is_loading: bool = False（模块级变量）
- get_is_loading() -> bool
- set_is_loading(val: bool)

在 routes.py 中添加两个路由：

1. POST /model/load：
   接收 ModelLoadRequest。
   如果 _is_loading 为 True，返回 {"success": False, "message": "模型正在加载中，请稍候"}。
   如果 assistant 已存在，先调用 clear_rag_assistant() 卸载旧模型。
   设置 _is_loading = True。
   启动后台线程执行加载：
     def load_model_task():
         kb = get_knowledge_base()
         assistant = RAGAssistant(
             knowledge_base=kb,
             model_key=request.model_key,
             model_dir=request.model_dir,
             use_reranker=request.use_reranker,
             reranker_model=request.reranker_model,
             reranker_top_k=request.reranker_top_k,
             initial_retrieval_k=request.initial_retrieval_k
         )
         set_rag_assistant(assistant)
         set_is_loading(False)
   立即返回 {"success": True, "data": {"model_key": request.model_key, "status": "loading"}}

2. POST /model/unload：
   如果 assistant 为 None，返回 {"success": False, "message": "没有已加载的模型"}
   调用 clear_rag_assistant()
   返回 {"success": True, "message": "模型已卸载"}

使用 threading.Thread(target=load_model_task) 启动后台线程。
从 src.rag_api.dependencies 导入 get_rag_assistant, set_rag_assistant, clear_rag_assistant, get_is_loading, set_is_loading, get_knowledge_base。
从 src.rag_engine 导入 RAGAssistant。
不要添加任何注释。
```

### 验收标准

| 验证项 | 方法 | 通过条件 |
|--------|------|---------|
| 加载请求立即返回 | POST `/api/rag/model/load` | 返回 `{status: "loading"}`，不阻塞 |
| 加载完成后状态更新 | 轮询 `/api/rag/status` | `engine_loaded` 从 false 变为 true |
| 防重复加载 | 加载中再次请求 | 返回 `{success: false, message: "模型正在加载中"}` |
| 卸载成功 | POST `/api/rag/model/unload` | 返回 `{success: true}`，status 中 engine_loaded=false |
| 卸载后显存释放 | 检查 nvidia-smi | GPU 显存占用下降 |
| 无模型时卸载 | 未加载时调用 unload | 返回 `{success: false, message: "没有已加载的模型"}` |

---

## Task 1.8: 实现文件上传路由 `/api/rag/ingest`

### 执行内容

在 `src/rag_api/routes.py` 中实现 POST `/api/rag/ingest` 路由。

### 技术要点

1. **UploadFile**：使用 FastAPI 的 `UploadFile` 类型接收文件
2. **文件格式验证**：仅接受 `.pdf`, `.txt`, `.md` 后缀
3. **临时文件处理**：将上传文件保存到临时路径，调用 `kb.ingest()` 后删除临时文件
4. **文档类型自动检测**：KnowledgeBase.ingest() 内部已实现 `detect_doc_type()`，无需手动指定
5. **文件大小限制**：建议限制 50MB，通过 FastAPI 配置或路由内检查

### 执行提示词

```
在 d:\ascend-rag-assistant\src\rag_api\routes.py 中实现 POST /api/rag/ingest 文件上传路由。

添加以下路由：

@router.post("/ingest")
async def ingest_file(file: UploadFile = File(...)):
    检查文件后缀：filename = file.filename，allowed = [".pdf", ".txt", ".md"]
    如果后缀不在 allowed 中，抛出 HTTPException(status_code=400, detail=f"不支持的文件格式，仅支持 {allowed}")
    
    检查文件大小：content = await file.read()，如果 len(content) > 50 * 1024 * 1024，抛出 HTTPException(status_code=400, detail="文件大小超过50MB限制")
    
    保存临时文件：
    temp_path = f"temp_upload_{file.filename}"
    with open(temp_path, "wb") as f: f.write(content)
    
    try:
        kb = get_knowledge_base()
        success = kb.ingest(temp_path)
        if success:
            doc_type = kb.detect_doc_type(temp_path)
            collection = kb.db._collection
            chunks_count = collection.count() if hasattr(collection, 'count') else 0
            return {"success": True, "data": {"filename": file.filename, "doc_type": doc_type, "chunks_count": chunks_count}}
        else:
            return {"success": False, "message": f"文件导入失败: {file.filename}"}
    except Exception as e:
        return {"success": False, "message": f"导入出错: {str(e)}"}
    finally:
        if os.path.exists(temp_path): os.remove(temp_path)

从 fastapi 导入 UploadFile, File。
导入 os。
从 src.rag_api.dependencies 导入 get_knowledge_base。
不要添加任何注释。
```

### 验收标准

| 验证项 | 方法 | 通过条件 |
|--------|------|---------|
| MD 文件上传 | curl POST 上传 `.md` 文件 | 返回 `{success: true, data: {filename, doc_type, chunks_count}}` |
| PDF 文件上传 | curl POST 上传 `.pdf` 文件 | 返回 `{success: true}` |
| 不支持格式 | curl POST 上传 `.exe` 文件 | 返回 400 |
| 大文件拒绝 | 上传 > 50MB 文件 | 返回 400 |
| 临时文件清理 | 上传后检查 `temp_upload_*` 文件 | 不存在 |
| 知识库可检索 | 上传后调用 chat 接口 | 能检索到上传内容 |

---

## Task 1.9: 实现知识库管理路由

### 执行内容

在 `src/rag_api/routes.py` 中实现 POST `/api/rag/knowledge-base/auto-ingest` 和 GET `/api/rag/knowledge-base/stats` 路由。

### 技术要点

1. **auto-ingest**：复用 `app.py` 中 `auto_ingest_all_data()` 的逻辑，遍历 `data/` 目录下 5 个子目录
2. **stats**：从 ChromaDB collection 获取文档数量，按 doc_type 统计
3. **耗时操作**：auto-ingest 可能需要数分钟（首次导入 64+ 文件），考虑异步处理
4. **去重逻辑**：检查 collection.count()，如果 > 0 则跳过自动导入

### 执行提示词

```
在 d:\ascend-rag-assistant\src\rag_api\routes.py 中实现知识库管理路由。

添加以下两个路由：

1. POST /knowledge-base/auto-ingest：
   kb = get_knowledge_base()
   检查是否已有数据：collection = kb.db._collection, count = collection.count()
   如果 count > 0，返回 {"success": True, "data": {"total_files": 0, "success_count": 0, "message": "知识库已有数据，跳过导入"}}
   
   data_dirs = ["data/常见问题FAQ", "data/报名须知", "data/技术文档", "data/竞赛规则", "data/评分标准"]
   supported_extensions = ['.md', '.txt', '.pdf']
   total_files = 0, success_count = 0
   
   遍历 data_dirs，对每个目录 os.walk 遍历文件：
     如果文件后缀在 supported_extensions 中：
       total_files += 1
       try: kb.ingest(file_path); success_count += 1
       except: pass
   
   返回 {"success": True, "data": {"total_files": total_files, "success_count": success_count, "failed_count": total_files - success_count}}

2. GET /knowledge-base/stats：
   kb = get_knowledge_base()
   collection = kb.db._collection
   total_chunks = collection.count() if hasattr(collection, 'count') else 0
   返回 {"success": True, "data": {"total_chunks": total_chunks}}

导入 os。
从 src.rag_api.dependencies 导入 get_knowledge_base。
不要添加任何注释。
```

### 验收标准

| 验证项 | 方法 | 通过条件 |
|--------|------|---------|
| 首次自动导入 | 清空 chroma_db 后调用 auto-ingest | 返回 total_files > 0, success_count > 0 |
| 重复导入跳过 | 已有数据时调用 auto-ingest | 返回 total_files=0, message 含"跳过" |
| 统计信息 | GET `/api/rag/knowledge-base/stats` | 返回 total_chunks > 0 |
| 空库统计 | 清空 chroma_db 后调用 stats | 返回 total_chunks=0 或 1（默认文档） |

---

## Task 1.10: 实现中间件

### 执行内容

实现 `src/rag_api/middleware.py`，包含统一错误处理和请求日志中间件。

### 技术要点

1. **错误处理中间件**：捕获所有未处理异常，返回统一 JSON 格式 `{success: false, message: "...", detail: "..."}`
2. **请求日志中间件**：记录每个请求的方法、路径、耗时、状态码
3. **CORS**：在 `app.py` 的 `create_app()` 中通过 CORSMiddleware 配置（非自定义中间件）
4. **中间件注册**：在 `create_app()` 中通过 `app.middleware("request")` 或 `app.add_middleware()` 注册

### 执行提示词

```
实现 d:\ascend-rag-assistant\src\rag_api\middleware.py，包含两个中间件函数。

1. register_error_handler(app: FastAPI)：
   使用 @app.exception_handler(Exception) 注册全局异常处理器。
   返回 JSONResponse(status_code=500, content={"success": False, "message": "服务器内部错误", "detail": str(exc)})

2. register_request_logger(app: FastAPI)：
   使用 @app.middleware("http") 注册请求日志中间件。
   记录请求开始时间，调用 await call_next(request)，计算耗时。
   打印日志：f"{request.method} {request.url.path} - {response.status_code} - {elapsed_ms:.0f}ms"
   返回 response。

然后在 app.py 的 create_app() 中调用：
   register_error_handler(app)
   register_request_logger(app)

从 fastapi 导入 FastAPI, Request。
从 fastapi.responses 导入 JSONResponse。
导入 time, logging。
logger = logging.getLogger("rag_api")
不要添加任何注释。
```

### 验收标准

| 验证项 | 方法 | 通过条件 |
|--------|------|---------|
| 未处理异常返回 JSON | 触发路由内 1/0 异常 | 返回 `{success: false, message: "服务器内部错误"}` |
| 请求日志输出 | 发送请求后检查控制台 | 输出 `GET /api/rag/status - 200 - XXms` |
| CORS 生效 | 从 localhost:5173 发送 OPTIONS 预检 | 返回 200，含 Access-Control-Allow-Origin |

---

## Task 1.11: 创建 RAG API 启动入口

### 执行内容

创建 `rag_server.py` 项目根目录启动入口，并更新 `config/config.yaml` 添加 `rag_port`。

### 技术要点

1. **与 server.py 风格一致**：yaml 配置读取、uvicorn 启动、端口打印
2. **配置新增**：在 config.yaml 的 server 节添加 `rag_port: 8001`
3. **uvicorn 启动**：使用 `uvicorn.run("rag_server:app", ...)` 字符串引用，支持 reload
4. **自动导入**：启动时可选择是否自动导入知识库数据

### 执行提示词

```
创建 d:\ascend-rag-assistant\rag_server.py 作为 RAG API 启动入口。

内容参考 d:\ascend-rag-assistant\server.py 的风格：

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

同时更新 d:\ascend-rag-assistant\config\config.yaml：
在 server 节添加 rag_port: 8001，保持其他配置不变。
不要添加任何注释。
```

### 验收标准

| 验证项 | 方法 | 通过条件 |
|--------|------|---------|
| 服务可启动 | `python rag_server.py` | 控制台输出启动信息，无报错 |
| Swagger UI 可访问 | 浏览器打开 `http://localhost:8001/docs` | 显示所有 API 端点 |
| 根路由正常 | curl `http://localhost:8001/` | 返回 `{message: "RAG API服务正常运行"}` |
| 端口配置生效 | 修改 config.yaml rag_port 为 8002 后启动 | 服务在 8002 端口启动 |
| 技能树 API 不受影响 | 同时运行 `python server.py` | 两个服务独立运行，端口不冲突 |

---

## Task 1.12: 更新技能树 API CORS 配置

### 执行内容

更新 `server.py` 的 CORS 配置，允许前端开发服务器访问。

### 技术要点

1. **当前 CORS**：`allow_origins=["*"]`，过于宽松
2. **目标 CORS**：限制为具体来源 `["http://localhost:5173", "http://localhost:8501", "http://localhost:3000"]`
3. **保持兼容**：开发阶段仍可使用 `"*"`，但建议明确列出

### 执行提示词

```
修改 d:\ascend-rag-assistant\server.py 的 CORS 配置。

将 allow_origins 从 ["*"] 改为 ["http://localhost:5173", "http://localhost:8501", "http://localhost:3000"]。

其他 CORS 配置保持不变。
不要添加任何注释。
```

### 验收标准

| 验证项 | 方法 | 通过条件 |
|--------|------|---------|
| localhost:5173 可访问 | 从 Vite 前端请求技能树 API | 无 CORS 错误 |
| localhost:8501 可访问 | 从 Streamlit 请求技能树 API | 无 CORS 错误 |
| 技能树 API 功能正常 | curl 测试 CRUD | 所有端点正常 |

---

## Task 1.13: 编写 RAG API 测试

### 执行内容

创建 `tests/test_rag_api.py`，使用 pytest + httpx 的 TestClient 测试所有 API 端点。

### 技术要点

1. **TestClient**：使用 `from fastapi.testclient import TestClient` 创建测试客户端
2. **Mock 策略**：由于 RAGAssistant 加载模型耗时，测试中使用 mock 替代真实模型
3. **测试覆盖**：
   - status 端点（引擎未加载/已加载）
   - chat 端点（正常/异常/引擎未加载）
   - chat/stream 端点（SSE 事件流）
   - model/load 和 model/unload
   - ingest 文件上传
   - knowledge-base/stats
4. **参考现有测试**：`tests/test_skill_tree.py` 使用 unittest，新测试使用 pytest 风格

### 执行提示词

```
创建 d:\ascend-rag-assistant\tests\test_rag_api.py，使用 pytest 测试 RAG API。

使用 fastapi.testclient.TestClient，从 src.rag_api.app 导入 create_app。

测试用例：

1. test_status_before_load：GET /api/rag/status，验证 engine_loaded=False, available_models 非空
2. test_status_response_format：验证响应包含 success, data 字段
3. test_chat_engine_not_loaded：POST /api/rag/chat，验证返回 503
4. test_chat_stream_engine_not_loaded：POST /api/rag/chat/stream，验证返回 503
5. test_ingest_unsupported_format：POST /api/rag/ingest，上传 .exe 文件，验证返回 400
6. test_ingest_no_file：POST /api/rag/ingest，不上传文件，验证返回 422
7. test_kb_stats：GET /api/rag/knowledge-base/stats，验证返回 success=True
8. test_model_load_invalid_key：POST /api/rag/model/load，使用无效 model_key，验证行为（RAGAssistant 会使用默认模型或报错）
9. test_model_unload_when_not_loaded：POST /api/rag/model/unload，验证返回 success=False

使用 pytest fixture 创建 TestClient 实例：
  @pytest.fixture
  def client():
      app = create_app()
      return TestClient(app)

注意：不测试需要真实模型加载的场景（耗时过长），仅测试 API 层面的请求/响应格式和错误处理。
不要添加任何注释。
```

### 验收标准

| 验证项 | 方法 | 通过条件 |
|--------|------|---------|
| 测试可运行 | `pytest tests/test_rag_api.py -v` | 所有测试通过 |
| 覆盖所有端点 | 检查测试文件 | 8 个 API 端点均有测试 |
| 错误场景覆盖 | 检查测试文件 | 503/400/422 场景有测试 |
| 无真实模型依赖 | 运行测试无需 GPU | 测试通过 Mock 或仅测试 API 层 |

---

## Task 1.14: Swagger UI 验证全部 API

### 执行内容

启动 RAG API 服务，通过 Swagger UI 逐个验证所有 8 个 API 端点。

### 技术要点

1. **验证顺序**：status → model/load → status(确认加载) → chat → chat/stream → ingest → kb/stats → kb/auto-ingest → model/unload → status(确认卸载)
2. **SSE 验证**：Swagger UI 不支持 SSE 流式显示，需使用 curl 单独验证
3. **响应格式**：每个端点的响应 JSON 必须与设计文档 4.1.3 节完全一致

### 执行提示词

```
此步骤为手动验证，无需编写代码。

启动 RAG API 服务：python rag_server.py
打开 Swagger UI：http://localhost:8001/docs

按以下顺序验证每个端点：

1. GET /api/rag/status — 验证 engine_loaded=false, available_models 有 3 个模型
2. POST /api/rag/model/load — body: {"model_key": "qwen2-1.5b", "use_reranker": false}，验证返回 status=loading
3. 等待 30-120 秒，GET /api/rag/status — 验证 engine_loaded=true
4. POST /api/rag/chat — body: {"question": "如何报名西门子杯？"}，验证返回 answer 和 sources
5. curl 验证 SSE：curl -N -X POST http://localhost:8001/api/rag/chat/stream -H "Content-Type: application/json" -d '{"question": "测试"}'，验证流式输出
6. POST /api/rag/ingest — 上传一个 .md 文件，验证返回 filename 和 chunks_count
7. GET /api/rag/knowledge-base/stats — 验证 total_chunks > 0
8. POST /api/rag/model/unload — 验证返回 success=true
9. GET /api/rag/status — 验证 engine_loaded=false

记录每个端点的实际响应，与设计文档对比。
```

### 验收标准

| 验证项 | 方法 | 通过条件 |
|--------|------|---------|
| 所有 8 个端点可调用 | Swagger UI / curl | 无 500 错误 |
| 响应格式一致 | 对比设计文档 4.1.3 | JSON 结构完全匹配 |
| SSE 流正常 | curl 接收流 | token/sources/done 事件完整 |
| 模型加载/卸载 | 完整流程 | load → status=true → unload → status=false |
| 文件上传 | 上传 .md 文件 | 返回 chunks_count > 0 |
| Swagger UI 文档 | 检查 /docs 页面 | 所有端点有描述、请求/响应示例 |

---

## 批次依赖关系图

```
批次A (可并行):
  Task 1.1 ──┐
  Task 1.2 ──┼──→ 批次B
  Task 1.3 ──┘

批次B (可并行，依赖批次A):
  Task 1.4 ──┐
  Task 1.5 ──┤
  Task 1.6 ──┼──→ 批次C
  Task 1.7 ──┤
  Task 1.8 ──┤
  Task 1.9 ──┤
  Task 1.10 ─┘

批次C (可并行，依赖批次B):
  Task 1.11 ──┬──→ 批次D
  Task 1.12 ──┘

批次D (串行，依赖批次C):
  Task 1.13 ──→ Task 1.14
```

## 整体验收标准汇总

| 类别 | 验证项 | 通过条件 |
|------|--------|---------|
| **功能** | 8 个 API 端点全部可调用 | Swagger UI / curl 无 500 错误 |
| **功能** | SSE 流式输出正常 | token/sources/done 事件完整 |
| **功能** | 模型加载/卸载流程完整 | load → unload 循环正常 |
| **功能** | 文件上传导入成功 | .md/.pdf/.txt 均可导入 |
| **代码质量** | 无 import 错误 | `python -c "from src.rag_api.app import create_app"` 通过 |
| **代码质量** | 无语法错误 | `python -m py_compile src/rag_api/*.py` 全部通过 |
| **代码质量** | 测试通过 | `pytest tests/test_rag_api.py` 全部 PASS |
| **代码质量** | 无代码注释 | 所有新建文件不含注释 |
| **文档** | Swagger UI 完整 | /docs 页面显示所有端点 |
| **文档** | 响应格式与设计文档一致 | JSON 结构匹配 |
| **兼容** | 技能树 API 不受影响 | server.py 正常运行 |
| **兼容** | Streamlit 版本不受影响 | app.py 正常运行 |
| **兼容** | 两个 API 服务可同时运行 | 端口 8000 和 8001 不冲突 |
