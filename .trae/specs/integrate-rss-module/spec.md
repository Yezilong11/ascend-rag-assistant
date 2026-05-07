# RSS 模块集成 Spec

## Why
当前 ascend-rag-assistant 项目仅支持本地文档知识库，缺少实时信息获取能力。将 RSS 抓取项目作为微服务集成后，系统可自动订阅和抓取竞赛相关 RSS 源，将资讯文章导入 RAG 知识库，实现实时信息增强的智能问答。

## What Changes
- 将 `E:\RSS抓取` Go 项目复制到 `services/rss-crawler/`，修改端口为 8081，调整 CORS 和配置
- 新增 Python `src/rss_gateway/` 模块，实现 FastAPI 代理路由和知识库桥接
- 新增 React 前端 RSS 管理页面（类型、API、Store、组件、路由）
- 更新项目配置、启动脚本、.gitignore、Vite 代理
- 集成期 AI 摘要保持 Ollama 不变，后续阶段再统一切换到本地 Qwen2

## Impact
- Affected specs: 无已有 spec 受影响（前端现代化 spec 已完成）
- Affected code:
  - `config/config.yaml` — 新增 rss 配置段
  - `src/rag_api/app.py` — 注册 RSS 网关路由
  - `frontend/src/App.tsx` — 新增 /rss 路由
  - `frontend/src/components/layout/Sidebar.tsx` — 新增 RSS 导航项
  - `frontend/vite.config.ts` — 新增代理规则
  - `.gitignore` — 新增忽略规则
  - `start.bat` — 新增 Go 服务启动

## ADDED Requirements

### Requirement: Go RSS 微服务嵌入
系统 SHALL 将 RSS 抓取 Go 项目作为独立微服务嵌入 `services/rss-crawler/` 目录，监听 8081 端口，CORS 允许 localhost:3000 访问。

#### Scenario: Go 服务启动
- **WHEN** 执行 `go run cmd/server/main.go` 在 `services/rss-crawler/` 目录下
- **THEN** Go 服务在 `localhost:8081` 启动，CORS 允许 localhost:3000

#### Scenario: Go 服务不可用
- **WHEN** Go 服务未启动时前端访问 RSS 功能
- **THEN** 代理层返回 503 错误和友好提示，不影响其他功能

### Requirement: FastAPI RSS 代理网关
系统 SHALL 在 FastAPI 中提供 `/api/rss/*` 代理路由，将请求转发到 Go RSS 微服务，统一 API 入口。

#### Scenario: 代理 RSS 源列表请求
- **WHEN** 前端请求 `GET /api/rss/feeds`
- **THEN** FastAPI 将请求代理到 `GET http://localhost:8081/api/feeds`，返回相同响应

#### Scenario: 代理创建 RSS 源请求
- **WHEN** 前端请求 `POST /api/rss/feeds` 包含 name 和 url
- **THEN** FastAPI 将请求代理到 Go 服务，返回创建结果

#### Scenario: Go 服务不可用时代理降级
- **WHEN** Go 服务未运行，前端请求任何 `/api/rss/*` 端点
- **THEN** 返回 `{"success": false, "message": "RSS服务不可用"}` 和 503 状态码

### Requirement: RSS 知识库桥接
系统 SHALL 提供桥接接口，将 RSS 文章内容导入 ChromaDB 向量知识库，doc_type 为 "rss_article"。

#### Scenario: 导入单篇文章到知识库
- **WHEN** 调用 `POST /api/rss/bridge/ingest-article/{id}`
- **THEN** 从 Go 服务获取文章内容，调用 KnowledgeBase.ingest() 导入，返回导入结果

#### Scenario: 批量导入未读文章
- **WHEN** 调用 `POST /api/rss/bridge/ingest-all-unread`
- **THEN** 从 Go 服务获取所有未读文章，逐篇导入知识库，返回成功/失败计数

### Requirement: React RSS 管理界面
系统 SHALL 在 React 前端提供 RSS 管理页面，包含仪表盘、源管理、文章列表、文章详情、分类管理、标签管理、设置等子功能。

#### Scenario: 查看 RSS 仪表盘
- **WHEN** 用户导航到 `/rss` 页面
- **THEN** 显示 RSS 统计概览（源数量、文章总数、今日新增、未读数）

#### Scenario: 管理 RSS 源
- **WHEN** 用户在 RSS 源管理界面添加/编辑/删除 RSS 源
- **THEN** 操作通过 API 代理到 Go 服务，界面实时更新

#### Scenario: 浏览文章列表
- **WHEN** 用户在文章列表界面按源/状态筛选文章
- **THEN** 显示筛选后的文章列表，支持分页

#### Scenario: 导入文章到知识库
- **WHEN** 用户点击文章的"导入知识库"按钮
- **THEN** 调用桥接接口，文章内容导入 ChromaDB，显示导入结果

### Requirement: 配置与部署整合
系统 SHALL 在 config.yaml 中新增 RSS 配置段，更新启动脚本同时启动 Go 和 Python 服务。

#### Scenario: 配置 RSS 服务
- **WHEN** 在 config.yaml 中设置 rss.enabled=true
- **THEN** FastAPI 启动时注册 RSS 代理路由，健康检查可检测 Go 服务状态

#### Scenario: 一键启动
- **WHEN** 执行 start.bat
- **THEN** 同时启动 Go RSS 服务（8081）和 Python FastAPI 服务（8000）

## MODIFIED Requirements

### Requirement: FastAPI 应用工厂路由注册
原 `src/rag_api/app.py` 的 `create_app()` 仅注册 RAG、技能树、多模态路由，现新增 RSS 网关路由注册，当 `rss.enabled=true` 时激活。

### Requirement: 前端侧边栏导航
原 `Sidebar.tsx` 包含智能问答、技能树、设置三个导航项，现新增"RSS 资讯"导航项。

## REMOVED Requirements
无移除的需求。
