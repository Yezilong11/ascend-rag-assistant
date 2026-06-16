# RSS抓取模块集成到 ascend-rag-assistant 完整规划

## 一、项目现状分析

### 1.1 当前项目：ascend-rag-assistant
- **定位**：基于昇腾AI的RAG竞赛智能助手
- **后端**：Python + FastAPI，包含 RAG引擎、技能树API、多模态API
- **前端**：React 19 + TypeScript + Ant Design + Vite + Zustand
- **数据**：ChromaDB 向量数据库，Markdown 文档知识库
- **端口**：前端 3000，API 8000

### 1.2 待集成项目：RSS抓取 (rss-knowledge-base)
- **定位**：本地RSS知识库系统，支持订阅管理、AI摘要、全文搜索
- **后端**：Go 1.20 + Gin + GORM/SQLite + WebSocket + gofeed
- **前端**：Vue 3 + TypeScript + Element Plus + Tailwind CSS + Pinia
- **数据**：SQLite 数据库，Meilisearch 搜索引擎
- **端口**：前端 5173，后端 8080，Meilisearch 7700，Ollama 11434

### 1.3 核心差异
| 维度 | ascend-rag-assistant | RSS抓取 |
|------|---------------------|---------|
| 后端语言 | Python (FastAPI) | Go (Gin) |
| 前端框架 | React + Ant Design | Vue 3 + Element Plus |
| 数据库 | ChromaDB (向量) | SQLite (关系) |
| AI能力 | Qwen2 本地模型 (HuggingFace格式) | Ollama 摘要 (gguf格式) |
| 搜索 | 向量相似度 | Meilisearch |
| 模型格式 | safetensors | gguf |

### 1.4 AI 模型使用策略

**当前状态**：
- ascend-rag-assistant 使用本地 Qwen2 模型（HuggingFace safetensors 格式）
- RSS抓取 使用 Ollama 服务调用本地 gguf 格式模型

**集成后的 AI 摘要方案**：

| 阶段 | AI 摘要来源 | 说明 |
|------|------------|------|
| 阶段1-4（集成期） | Ollama (保持不变) | Go RSS 服务 AI 分析暂时使用 Ollama |
| 阶段5（模型统一） | FastAPI 摘要接口 | 新增 `/api/rss/summarize` 接口，复用本地 Qwen2 |
| 阶段6（最终态） | 仅本地 Qwen2 | RSS AI 配置指向 FastAPI，不再依赖 Ollama |

**模型切换架构**：
```
阶段5后：FastAPI 新增摘要接口
                    ┌──────────────────────┐
RSS Go服务 ────────> │  POST /api/rss/summarize │
                    │      (接收文本)         │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │  FastAPI / Qwen2     │
                    │  (复用 ./models/)     │
                    └──────────────────────┘
```

---

## 二、集成策略：微服务 + 前端融合

### 2.1 架构决策

采用**微服务架构**，Go RSS 服务作为独立服务运行，Python FastAPI 作为网关统一对外：

```
┌─────────────────────────────────────────────────────────┐
│                   React 前端 (统一)                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐  │
│  │ 智能问答  │ │ 技能树    │ │ RSS管理   │ │ 设置      │  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │
              ┌──────────┴──────────┐
              │                     │
    ┌─────────▼──────────┐  ┌──────▼─────────────┐
    │  FastAPI 网关       │  │  Go RSS 微服务      │
    │  (Python :8000)    │  │  (Go :8081)         │
    │  - RAG API         │  │  - RSS 爬虫          │
    │  - 技能树 API      │  │  - 文章管理          │
    │  - RSS 代理路由    │──│  - AI 摘要           │
    │  - 知识库桥接      │  │  - WebSocket         │
    └─────────┬──────────┘  └──────┬─────────────┘
              │                     │
    ┌─────────▼──────────┐  ┌──────▼─────────────┐
    │  ChromaDB           │  │  SQLite              │
    │  (向量知识库)       │  │  (RSS 数据)          │
    └────────────────────┘  └────────────────────┘
```

### 2.2 为什么选择微服务而非重写

1. **Go 的 RSS 爬虫性能优势**：并发爬取、低内存占用，Go 天然适合
2. **最小改动原则**：Go 后端只需修改端口和 CORS 配置，无需重写
3. **独立部署**：RSS 服务可独立扩展、重启，不影响 RAG 服务
4. **技术栈解耦**：Python 负责 AI/RAG，Go 负责 RSS 爬虫，各司其职

---

## 三、实施步骤

### 阶段 1：Go RSS 服务适配（后端准备）

#### 步骤 1.1：将 RSS 项目复制到当前项目
- 在项目根目录创建 `services/rss-crawler/` 目录
- 将 `E:\RSS抓取` 的全部内容复制到该目录
- 调整 Go module 路径为 `rss-crawler`

#### 步骤 1.2：修改 Go 服务配置
- 修改默认端口从 `8080` 改为 `8081`，避免与 FastAPI 冲突
- 更新 CORS 配置，允许来自 `localhost:3000` 的请求
- 更新 `config.yaml` 模板，调整数据库路径为相对路径

#### 步骤 1.3：Go 服务 API 端点梳理
当前 Go 服务提供的 API 端点：
- `GET/POST/PUT/DELETE /api/feeds` — RSS 源 CRUD
- `POST /api/feeds/:id/crawl` — 触发单个源爬取
- `POST /api/feeds/crawl-all` — 触发全部爬取
- `GET/PUT/DELETE /api/articles` — 文章管理
- `PUT /api/articles/:id/read` — 标记已读
- `PUT /api/articles/read-all` — 全部已读
- `GET/POST/DELETE /api/categories` — 分类管理
- `GET/POST/DELETE /api/tags` — 标签管理
- `GET/PUT /api/ai/config` — AI 配置（**集成期指向 Ollama，后续改为 FastAPI**）
- `POST /api/ai/test` — 测试 AI 连接（**集成期测试 Ollama，后续测试 FastAPI**）
- `POST /api/articles/:id/analyze` — AI 分析文章（**集成期使用 Ollama，后续切换**）
- `GET /api/system/stats` — 系统统计
- `GET /api/system/status` — 系统状态
- `GET /ws` — WebSocket 实时通知

> **注意**：阶段1-4 中，Go 服务的 AI 功能保持 Ollama 调用方式不变，不做任何修改。后续阶段再统一切换到本地 Qwen2 模型。

### 阶段 2：FastAPI 网关代理层

#### 步骤 2.1：创建 RSS 代理路由模块
在 `src/` 下创建 `rss_gateway/` 模块：
```
src/rss_gateway/
├── __init__.py
├── routes.py          # FastAPI 代理路由
├── client.py          # Go 服务 HTTP 客户端
├── models.py          # 请求/响应模型
└── bridge.py          # RSS→知识库桥接服务
```

#### 步骤 2.2：实现代理路由
- 在 FastAPI 中注册 `/api/rss/*` 路由前缀
- 将所有 `/api/rss/feeds/*`、`/api/rss/articles/*` 等请求代理到 Go 服务
- 使用 `httpx` 异步客户端转发请求
- 统一错误处理和响应格式

#### 步骤 2.3：实现知识库桥接
- `bridge.py`：当 RSS 文章被标记为"已分析"时，自动将文章内容导入 ChromaDB
- 提供 `/api/rss/bridge/ingest-article/{id}` 端点，手动将 RSS 文章导入知识库
- 提供 `/api/rss/bridge/ingest-all-unread` 端点，批量导入未读文章
- 文章导入时自动设置 `doc_type="rss_article"` 元数据

#### 步骤 2.4：更新 FastAPI 应用工厂
- 在 `src/rag_api/app.py` 的 `create_app()` 中注册 RSS 网关路由
- 添加 RSS 服务健康检查端点 `/api/rss/health`

### 阶段 3：前端融合（React 重写 RSS 管理界面）

#### 步骤 3.1：创建 RSS 相关类型定义
在 `frontend/src/types/` 下创建 `rss.ts`：
- `Feed`、`Article`、`Category`、`Tag`、`RSSStats` 等类型

#### 步骤 3.2：创建 RSS API 服务
在 `frontend/src/services/` 下创建 `rssApi.ts`：
- 封装所有 RSS 相关 API 调用（通过 FastAPI 代理路由）

#### 步骤 3.3：创建 RSS 状态管理
在 `frontend/src/stores/` 下创建 `rssStore.ts`：
- 使用 Zustand 管理 RSS 状态（feeds、articles、categories、tags）

#### 步骤 3.4：创建 RSS 页面组件
在 `frontend/src/pages/` 下创建 `RSSPage.tsx`：
- 主页面，包含子标签页切换

在 `frontend/src/components/rss/` 下创建组件：
```
components/rss/
├── RSSDashboard.tsx       # RSS 仪表盘（统计概览）
├── FeedManager.tsx        # RSS 源管理（CRUD + 爬取）
├── ArticleList.tsx        # 文章列表（筛选、分页）
├── ArticleDetail.tsx      # 文章详情（内容阅读 + AI摘要）
├── CategoryManager.tsx    # 分类管理
├── TagManager.tsx         # 标签管理
├── AddFeedModal.tsx       # 添加 RSS 源弹窗
├── IngestToKBButton.tsx   # 导入知识库按钮
└── RSSSettings.tsx        # RSS AI 设置（Ollama 配置）
```

#### 步骤 3.5：集成到主应用路由
- 在 `App.tsx` 中添加 `/rss` 路由
- 在 `Sidebar.tsx` 中添加 RSS 导航项
- 在 `Header.tsx` 中更新面包屑支持

### 阶段 4：配置与部署整合

#### 步骤 4.1：更新项目配置
- 在 `config/config.yaml` 中添加 RSS 服务配置段：
```yaml
rss:
  enabled: true
  service_url: "http://localhost:8081"
  timeout: 30
  auto_ingest: false        # 是否自动将新文章导入知识库
  ingest_categories: []     # 限定导入的分类ID
```

#### 步骤 4.2：创建启动脚本
- 更新 `start.bat`，同时启动 Go RSS 服务和 Python FastAPI 服务
- 创建 `scripts/start-rss.ps1` 单独启动 RSS 服务

#### 步骤 4.3：更新 .gitignore
- 添加 `services/rss-crawler/data/` 忽略规则
- 添加 `services/rss-crawler/rss.db` 忽略规则

#### 步骤 4.4：更新 Vite 代理配置
- 在 `frontend/vite.config.ts` 中添加 `/api/rss` 代理规则到 FastAPI

### 阶段 5：数据流打通与增强功能

#### 步骤 5.1：RSS 文章 → RAG 知识库自动导入
- 在 `bridge.py` 中实现定时检查机制
- 当 RSS 爬取到新文章后，可选自动导入到 ChromaDB
- 导入时使用 `doc_type="rss_article"`，保留来源元数据

#### 步骤 5.2：RAG 问答中引用 RSS 来源
- 在 RAG 问答结果中，如果来源是 RSS 文章，显示特殊标识
- 来源面板中区分"竞赛文档"和"RSS资讯"

#### 步骤 5.3：WebSocket 实时通知集成
- 在 React 前端监听 Go 服务的 WebSocket
- 新文章到达时显示通知提示
- 可选：自动触发知识库导入

### 阶段 6：AI 模型统一（后续优化）

> **前置条件**：阶段1-5 已完成，RSS 集成正常运行

#### 步骤 6.1：新增 FastAPI 摘要接口
在 `src/rss_gateway/` 下新增 `summarizer.py`：
- 提供 `POST /api/rss/summarize` 接口
- 复用 `src/rag_engine.py` 中的模型加载逻辑
- 支持摘要生成、关键词提取、情感分析
- 与 RAG 引擎共享模型实例，避免重复加载

#### 步骤 6.2：RSS AI 配置切换
- 在 `config/config.yaml` 中新增配置：
```yaml
rss:
  ai:
    provider: "fastapi"  # 或 "ollama"（兼容旧配置）
    fastapi_endpoint: "http://localhost:8000/api/rss/summarize"
    ollama_endpoint: "http://localhost:11434"
    ollama_model: "llama2:latest"  # 旧配置，标记为deprecated
```

#### 步骤 6.3：迁移 RSS Go 服务 AI 路由（可选）
两种方案：
- **方案A（推荐）**：Go 服务 AI 请求改调 FastAPI 代理接口
- **方案B**：保留 Go 服务 AI 功能，前端直接调用 FastAPI 摘要接口

#### 步骤 6.4：移除 Ollama 依赖（可选）
- 若选择方案A，可完全移除 Ollama 依赖
- 若选择方案B，保留 Ollama 作为备选

---

## 四、目录结构规划

集成后的项目结构：
```
ascend-rag-assistant/
├── config/
│   └── config.yaml              # 添加 rss 配置段
├── data/                        # 竞赛知识库文档
├── services/
│   └── rss-crawler/             # Go RSS 微服务（独立项目）
│       ├── cmd/server/main.go
│       ├── internal/
│       ├── pkg/
│       ├── feeds/
│       ├── config.yaml          # RSS 服务独立配置
│       ├── go.mod
│       └── go.sum
├── src/                         # Python 后端
│   ├── knowledge_base.py
│   ├── rag_engine.py
│   ├── rag_api/
│   ├── skill_tree/
│   ├── multimodal/
│   └── rss_gateway/             # 新增：RSS 网关模块
│       ├── __init__.py
│       ├── routes.py
│       ├── client.py
│       ├── models.py
│       ├── bridge.py
│       └── summarizer.py        # 阶段6新增：Qwen2摘要接口
├── frontend/                    # React 前端
│   └── src/
│       ├── components/
│       │   ├── chat/
│       │   ├── layout/
│       │   ├── settings/
│       │   ├── skilltree/
│       │   └── rss/             # 新增：RSS 组件
│       ├── pages/
│       │   ├── ChatPage.tsx
│       │   ├── SkillTreePage.tsx
│       │   ├── SettingsPage.tsx
│       │   └── RSSPage.tsx      # 新增：RSS 页面
│       ├── services/
│       │   ├── ragApi.ts
│       │   ├── skillTreeApi.ts
│       │   └── rssApi.ts        # 新增：RSS API
│       ├── stores/
│       │   ├── chatStore.ts
│       │   ├── skillTreeStore.ts
│       │   └── rssStore.ts      # 新增：RSS 状态
│       └── types/
│           ├── rag.ts
│           ├── skillTree.ts
│           └── rss.ts           # 新增：RSS 类型
├── server.py
├── start.bat                    # 更新：同时启动 RSS 服务
└── README.md
```

---

## 五、API 路由规划

### 5.1 FastAPI 代理路由（新增）
| 方法 | 路径 | 说明 | 代理到 Go 服务 |
|------|------|------|---------------|
| GET | /api/rss/health | RSS 服务健康检查 | - |
| GET | /api/rss/feeds | 获取 RSS 源列表 | GET /api/feeds |
| POST | /api/rss/feeds | 创建 RSS 源 | POST /api/feeds |
| PUT | /api/rss/feeds/{id} | 更新 RSS 源 | PUT /api/feeds/{id} |
| DELETE | /api/rss/feeds/{id} | 删除 RSS 源 | DELETE /api/feeds/{id} |
| POST | /api/rss/feeds/{id}/crawl | 触发爬取 | POST /api/feeds/{id}/crawl |
| POST | /api/rss/feeds/crawl-all | 全部爬取 | POST /api/feeds/crawl-all |
| GET | /api/rss/articles | 文章列表 | GET /api/articles |
| GET | /api/rss/articles/{id} | 文章详情 | GET /api/articles/{id} |
| PUT | /api/rss/articles/{id}/read | 标记已读 | PUT /api/articles/{id}/read |
| PUT | /api/rss/articles/read-all | 全部已读 | PUT /api/articles/read-all |
| DELETE | /api/rss/articles/{id} | 删除文章 | DELETE /api/articles/{id} |
| GET | /api/rss/categories | 分类列表 | GET /api/categories |
| POST | /api/rss/categories | 创建分类 | POST /api/categories |
| PUT | /api/rss/categories/{id} | 更新分类 | PUT /api/categories/{id} |
| DELETE | /api/rss/categories/{id} | 删除分类 | DELETE /api/categories/{id} |
| GET | /api/rss/tags | 标签列表 | GET /api/tags |
| POST | /api/rss/tags | 创建标签 | POST /api/tags |
| DELETE | /api/rss/tags/{id} | 删除标签 | DELETE /api/tags/{id} |
| GET | /api/rss/ai/config | AI 配置 | GET /api/ai/config |
| PUT | /api/rss/ai/config | 更新 AI 配置 | PUT /api/ai/config |
| POST | /api/rss/ai/test | 测试 AI 连接 | POST /api/ai/test |
| POST | /api/rss/articles/{id}/analyze | AI 分析 | POST /api/articles/{id}/analyze |
| POST | /api/rss/articles/analyze-all | 批量分析 | POST /api/articles/analyze-all |
| GET | /api/rss/system/stats | 系统统计 | GET /api/system/stats |
| GET | /api/rss/system/status | 系统状态 | GET /api/system/status |

### 5.2 桥接路由（新增，FastAPI 本地处理）
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/rss/bridge/ingest-article/{id} | 将指定 RSS 文章导入知识库 |
| POST | /api/rss/bridge/ingest-feed/{id} | 将指定 RSS 源所有文章导入知识库 |
| POST | /api/rss/bridge/ingest-all-unread | 批量导入未读文章到知识库 |
| GET | /api/rss/bridge/status | 查看桥接导入状态 |

### 5.3 摘要接口路由（阶段6 新增）
| 方法 | 路径 | 说明 | 备注 |
|------|------|------|------|
| POST | /api/rss/summarize | 生成文章摘要 | 复用本地 Qwen2 模型 |
| POST | /api/rss/extract-keywords | 提取关键词 | 复用本地 Qwen2 模型 |
| POST | /api/rss/analyze-sentiment | 情感分析 | 复用本地 Qwen2 模型 |

---

## 六、依赖与配置变更

### 6.1 Python 依赖（新增）
```
httpx>=0.25.0      # 异步 HTTP 客户端，用于代理请求
```

### 6.2 前端依赖（无新增）
现有依赖已足够（axios、antd、zustand、react-router-dom）

### 6.3 外部服务依赖
| 服务 | 用途 | 集成期 | 最终态 |
|------|------|--------|--------|
| Go 1.20+ | RSS 后端服务 | 必须 | 必须 |
| Meilisearch 1.6+ | RSS 全文搜索 | 可选 | 可选 |
| Ollama | RSS AI 摘要 | 必须 | **可选/可移除** |
| Qwen2 本地模型 | RAG + 摘要 | 必须 | **必须（共享）** |

---

## 七、实施优先级与风险

### 7.1 实施优先级
| 优先级 | 阶段 | 内容 | 依赖 |
|--------|------|------|------|
| P0 | 阶段1 | Go RSS 服务适配 | 无 |
| P0 | 阶段2 | FastAPI 网关代理 | 阶段1 |
| P0 | 阶段3.1-3.3 | 前端类型、API、状态管理 | 阶段2 |
| P1 | 阶段3.4-3.5 | 前端 RSS 页面组件 | 阶段3.3 |
| P1 | 阶段4 | 配置与部署整合 | 阶段1-3 |
| P2 | 阶段5 | 数据流打通、实时通知 | 阶段1-4 |
| P3 | 阶段6 | AI 模型统一（后续优化） | 阶段1-5 |

### 7.2 风险与缓解
| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| Go 服务不可用时前端报错 | RSS 功能不可用 | 代理层增加健康检查和优雅降级 |
| 两个服务端口冲突 | 启动失败 | 使用不同端口，启动脚本检查端口 |
| RSS 文章导入知识库质量差 | RAG 回答质量下降 | 使用 rss_article 类型隔离，独立检索策略 |
| 前端组件重写工作量大 | 开发周期长 | 先实现核心功能（源管理+文章列表），后续迭代 |
| Ollama 模型格式不兼容 | 无法直接复用 Qwen2 | 阶段6通过 FastAPI 代理统一使用本地模型 |
| Ollama 服务未运行 | AI 摘要功能不可用 | 阶段6前需要确保 Ollama 运行，阶段6后不再依赖 |

### 7.3 不做的事情
- 不重写 Go 后端为 Python
- 不合并两个前端项目（Vue → React 只做组件重写）
- 不合并数据库（ChromaDB 和 SQLite 各自独立）
- 不强制依赖 Meilisearch（作为可选功能）
- **集成期不修改 Ollama AI 调用逻辑**（保持 Go 服务原样）
- **不要求必须安装 Ollama 才能完成集成**（阶段6后才完全切换）
