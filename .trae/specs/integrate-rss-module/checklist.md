# Checklist — RSS 模块集成

## Go RSS 服务适配
- [x] services/rss-crawler/ 目录包含完整 Go 项目（cmd/, internal/, pkg/, feeds/, go.mod, go.sum）
- [x] Go 服务默认端口为 8081，不与 FastAPI 8000 冲突
- [x] CORS 中间件允许 localhost:3000 访问
- [x] Go 服务可独立启动，`go run cmd/server/main.go` 无报错
- [x] GET /api/feeds 和 GET /api/system/stats 端点可正常访问

## FastAPI 网关代理层
- [x] src/rss_gateway/ 模块包含 __init__.py, client.py, models.py, routes.py, bridge.py
- [x] httpx.AsyncClient 封装正确，支持超时和错误处理
- [x] /api/rss/health 健康检查端点返回 Go 服务状态
- [x] /api/rss/feeds 代理路由正确转发到 Go 服务 GET /api/feeds
- [x] /api/rss/articles 代理路由正确转发到 Go 服务 GET /api/articles
- [x] /api/rss/bridge/ingest-article/{id} 可将文章导入 ChromaDB
- [x] /api/rss/bridge/ingest-all-unread 可批量导入未读文章
- [x] Go 服务不可用时代理路由返回 503 和友好错误信息
- [x] create_app() 中 RSS 路由条件注册（rss.enabled=true 时激活）

## 前端 RSS 管理界面
- [x] frontend/src/types/rss.ts 包含 Feed, Article, Category, Tag, RSSStats 类型
- [x] frontend/src/services/rssApi.ts 封装全部 RSS API 调用
- [x] frontend/src/stores/rssStore.ts 使用 Zustand 管理 RSS 状态
- [x] RSSPage.tsx 页面可正常渲染，Tabs 切换子功能
- [x] RSSDashboard 组件显示统计概览
- [x] FeedManager 组件支持 RSS 源 CRUD 和爬取操作
- [x] ArticleList 组件支持筛选和分页
- [x] ArticleDetail 组件显示文章内容和 AI 摘要
- [x] IngestToKBButton 组件可触发文章导入知识库
- [x] Sidebar 中可见"RSS 资讯"导航项
- [x] 点击 RSS 导航项可跳转到 /rss 页面

## 配置与部署整合
- [x] config/config.yaml 包含 rss 配置段（enabled, service_url, timeout）
- [x] .gitignore 包含 services/rss-crawler/data/ 和 *.db 忽略规则
- [x] start.bat 可同时启动 Go RSS 服务和 Python FastAPI 服务
- [x] Vite 代理规则覆盖 /api/rss 请求

## 代码审查
- [x] Go 服务适配代码审查完成，无必须修复问题
- [x] Python RSS 网关代码审查完成，无必须修复问题
- [x] React 前端 RSS 代码审查完成，无必须修复问题
- [x] 配置和部署文件审查完成，无必须修复问题

## 功能测试
- [x] Go RSS 服务独立启动测试通过
- [x] FastAPI 代理路由转发测试通过
- [x] 知识库桥接导入测试通过
- [x] 前端 RSS 页面交互测试通过（源管理、文章浏览、导入知识库）
- [x] Go 服务不可用时降级测试通过
