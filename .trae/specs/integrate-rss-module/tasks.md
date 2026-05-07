# Tasks — RSS 模块集成

## 阶段 1: Go RSS 服务适配

- [x] Task 1.1: 将 RSS 抓取项目复制到 services/rss-crawler/
  - [x] 创建 `services/rss-crawler/` 目录
  - [x] 复制 `E:\RSS抓取` 的 Go 后端代码（cmd/, internal/, pkg/, feeds/, go.mod, go.sum）
  - [x] 不复制 Vue 前端代码（frontend/ 目录）和 demo/ 目录
  - [x] 不复制 scripts/ 目录（后续重写启动脚本）
  - 验收标准: `services/rss-crawler/` 目录包含完整的 Go 项目，`go build ./cmd/server/` 编译通过

- [x] Task 1.2: 修改 Go 服务配置适配集成
  - [x] 修改 `services/rss-crawler/config.yaml` 默认端口从 8080 改为 8081
  - [x] 修改 `services/rss-crawler/internal/middleware/cors.go` 添加 localhost:3000 到允许来源
  - [x] 调整数据库路径配置为 `./data/rss.db`（相对于 services/rss-crawler/）
  - 验收标准: Go 服务在 8081 端口启动，从 localhost:3000 发起的请求不被 CORS 拦截

- [x] Task 1.3: 验证 Go 服务独立运行
  - [x] 在 `services/rss-crawler/` 下执行 `go run cmd/server/main.go`
  - [x] 验证 `GET http://localhost:8081/api/feeds` 返回空列表（200）
  - [x] 验证 `GET http://localhost:8081/api/system/stats` 返回统计数据
  - 验收标准: Go 服务独立启动无报错，核心 API 端点可正常访问

## 阶段 2: FastAPI 网关代理层

- [x] Task 2.1: 创建 RSS 网关模块骨架
  - [x] 创建 `src/rss_gateway/__init__.py`
  - [x] 创建 `src/rss_gateway/client.py` — httpx 异步客户端封装
  - [x] 创建 `src/rss_gateway/models.py` — Pydantic 请求/响应模型
  - [x] 创建 `src/rss_gateway/routes.py` — FastAPI 代理路由
  - [x] 创建 `src/rss_gateway/bridge.py` — 知识库桥接服务
  - 验收标准: 所有文件可正常 import，无语法错误

- [x] Task 2.2: 实现 httpx 客户端和代理路由
  - [x] 在 `client.py` 中实现 RSSClient 类，封装 httpx.AsyncClient
  - [x] 实现健康检查方法 `health_check()` → GET /api/system/status
  - [x] 实现通用代理方法 `proxy_request(method, path, **kwargs)`
  - [x] 在 `routes.py` 中实现所有 `/api/rss/*` 代理路由（feeds, articles, categories, tags, ai, system）
  - [x] 实现 `/api/rss/health` 健康检查端点
  - 验收标准: 所有代理路由可正确转发请求到 Go 服务并返回响应

- [x] Task 2.3: 实现知识库桥接服务
  - [x] 在 `bridge.py` 中实现 `ingest_article(article_id)` — 单篇导入
  - [x] 实现 `ingest_feed(feed_id)` — 按源批量导入
  - [x] 实现 `ingest_all_unread()` — 全部未读导入
  - [x] 实现 `get_bridge_status()` — 桥接状态查询
  - [x] 在 `routes.py` 中注册桥接路由 `/api/rss/bridge/*`
  - 验收标准: 桥接接口可将 RSS 文章内容导入 ChromaDB，doc_type 为 rss_article

- [x] Task 2.4: 注册 RSS 网关到 FastAPI 应用工厂
  - [x] 在 `src/rag_api/app.py` 的 `create_app()` 中添加 RSS 路由注册
  - [x] 添加条件注册：当 config.yaml 中 `rss.enabled=true` 时才注册
  - [x] 更新根路由 `/` 返回的 services 信息，添加 rss 服务
  - 验收标准: FastAPI 启动后 `/docs` 中可见 RSS API 端点，`/api/rss/health` 返回状态

## 阶段 3: 前端 RSS 管理界面

- [x] Task 3.1: 创建 RSS 类型定义
  - [x] 创建 `frontend/src/types/rss.ts`
  - [x] 定义 Feed, Article, Category, Tag, RSSStats, SystemStatus 类型
  - [x] 定义 ArticleFilter, ArticleListResponse 类型
  - 验收标准: TypeScript 编译无错误，类型与 Go 服务 API 响应格式一致

- [x] Task 3.2: 创建 RSS API 服务
  - [x] 创建 `frontend/src/services/rssApi.ts`
  - [x] 封装 feeds, articles, categories, tags, ai, system, bridge 全部 API 调用
  - [x] 统一使用 `/api/rss/` 前缀
  - 验收标准: 所有 API 函数签名正确，TypeScript 编译无错误

- [x] Task 3.3: 创建 RSS 状态管理
  - [x] 创建 `frontend/src/stores/rssStore.ts`
  - [x] 使用 Zustand 管理 feeds, articles, categories, tags, stats, loading 状态
  - [x] 实现 CRUD actions 和数据获取 actions
  - 验收标准: Store 创建成功，actions 可正确更新状态

- [x] Task 3.4: 创建 RSS 页面和组件
  - [x] 创建 `frontend/src/pages/RSSPage.tsx` — 主页面，Tabs 切换子功能
  - [x] 创建 `frontend/src/components/rss/RSSDashboard.tsx` — 统计仪表盘
  - [x] 创建 `frontend/src/components/rss/FeedManager.tsx` — RSS 源管理
  - [x] 创建 `frontend/src/components/rss/ArticleList.tsx` — 文章列表
  - [x] 创建 `frontend/src/components/rss/ArticleDetail.tsx` — 文章详情
  - [x] 创建 `frontend/src/components/rss/AddFeedModal.tsx` — 添加源弹窗
  - [x] 创建 `frontend/src/components/rss/IngestToKBButton.tsx` — 导入知识库按钮
  - 验收标准: RSS 页面可正常渲染，各子组件功能完整

- [x] Task 3.5: 集成 RSS 到主应用
  - [x] 在 `App.tsx` 中添加 `/rss` 路由指向 RSSPage
  - [x] 在 `Sidebar.tsx` 中添加"RSS 资讯"导航项（图标用 RssOutlined）
  - 验收标准: 侧边栏可见 RSS 导航项，点击可跳转到 RSS 页面

## 阶段 4: 配置与部署整合

- [x] Task 4.1: 更新项目配置文件
  - [x] 在 `config/config.yaml` 中添加 rss 配置段（enabled, service_url, timeout, auto_ingest）
  - [x] 更新 `.gitignore` 添加 `services/rss-crawler/data/` 和 `services/rss-crawler/*.db`
  - 验收标准: config.yaml 包含 rss 配置，git status 不显示 RSS 数据文件

- [x] Task 4.2: 更新 Vite 代理和启动脚本
  - [x] 在 `frontend/vite.config.ts` 中确认 `/api/rss` 代理到 localhost:8000（已有 `/api` 代理规则覆盖）
  - [x] 更新 `start.bat` 添加 Go RSS 服务启动命令
  - 验收标准: 前端开发服务器可代理 RSS API 请求，start.bat 可同时启动两个后端服务

## 阶段 5: 代码审查与测试

- [x] Task 5.1: 代码审查
  - [x] 审查 Go 服务适配代码（端口、CORS、配置修改）
  - [x] 审查 Python RSS 网关代码（client, routes, bridge, models）
  - [x] 审查 React 前端 RSS 代码（types, api, store, components, pages）
  - [x] 审查配置和部署文件（config.yaml, .gitignore, start.bat, vite.config.ts）
  - [x] 输出审查报告，列出发现的问题
  - 验收标准: 审查报告完成，所有问题分类为"必须修复"/"建议优化"

- [x] Task 5.2: 修复审查发现的问题
  - [x] 修复 Bridge 端点路径错误（3处）
  - [x] 修复 AI 端点路径错误（3处）
  - [x] 修复 Go 服务响应格式与前端期望不一致问题
  - 验收标准: 所有必须修复的问题已解决

- [x] Task 5.3: 功能测试
  - [x] 测试 Go RSS 服务独立启动和 API 端点
  - [x] 测试 FastAPI 代理路由转发功能
  - [x] 测试知识库桥接导入功能
  - [x] 测试前端 RSS 页面交互（源管理、文章浏览、导入知识库）
  - [x] 测试 Go 服务不可用时的降级表现
  - 验收标准: 所有核心功能测试通过，降级场景表现正常

# Task Dependencies

## 串行依赖
- Task 1.2 依赖 Task 1.1（配置修改需要项目文件存在）
- Task 1.3 依赖 Task 1.2（验证需要配置修改完成）
- Task 2.2 依赖 Task 2.1（路由实现需要模块骨架）
- Task 2.3 依赖 Task 2.2（桥接需要客户端可用）
- Task 2.4 依赖 Task 2.2 + 2.3（注册需要路由和桥接完成）
- Task 3.2 依赖 Task 3.1（API 服务需要类型定义）
- Task 3.3 依赖 Task 3.2（Store 需要 API 服务）
- Task 3.4 依赖 Task 3.3（组件需要 Store）
- Task 3.5 依赖 Task 3.4（路由集成需要页面组件）
- Task 5.1 依赖 Task 1.1-4.2 全部完成
- Task 5.2 依赖 Task 5.1
- Task 5.3 依赖 Task 5.2

## 可并行执行
- Task 1.1-1.3（Go 服务适配）与 Task 2.1-2.2（Python 网关骨架）可并行
- Task 3.1-3.3（前端基础）与 Task 2.3-2.4（Python 桥接和注册）可并行
- Task 4.1 与 Task 4.2 可并行
