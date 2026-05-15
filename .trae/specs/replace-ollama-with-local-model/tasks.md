# Tasks — RSS AI 分析从 Ollama 迁移到本地模型

## 阶段 1: Python 端 AI 分析服务

- [x] Task 1.1: 创建 AI 缓存模块 `src/rss_gateway/ai_cache.py`
  - [x] 实现 `AICache` 类，基于 JSON 文件的持久化缓存
  - [x] 实现 `get(content_hash) -> Optional[dict]` 方法
  - [x] 实现 `set(content_hash, analysis_result)` 方法
  - [x] 实现 `content_hash(content: str) -> str` 工具函数（SHA-256）
  - [x] 处理缓存文件损坏的容错逻辑（忽略损坏缓存，重建文件）
  - [x] 缓存文件路径默认为 `data/rss_ai_cache.json`
  - 验收标准: 缓存可正确读写，文件损坏时不崩溃

- [x] Task 1.2: 创建 AI 分析服务 `src/rss_gateway/ai_service.py`
  - [x] 实现 `RSSAIService` 类
  - [x] 实现 `generate_summary(content: str) -> str` — 生成 100 字以内中文摘要
  - [x] 实现 `extract_keywords(content: str) -> str` — 提取 5 个关键词
  - [x] 实现 `analyze_sentiment(content: str) -> str` — 情感分析（正面/中性/负面）
  - [x] 实现 `analyze_article(article_id: int, client: RSSClient) -> dict` — 完整文章分析
  - [x] 实现 `analyze_all_articles(client: RSSClient) -> dict` — 批量分析
  - [x] 实现 `test_availability() -> dict` — 检查模型可用性
  - [x] 实现 `get_config() -> dict` — 获取当前 AI 配置
  - [x] 使用 `threading.Lock` 保证模型推理线程安全
  - [x] 输入内容截断为前 2000 字符
  - [x] 复用 `src/rag_api/dependencies.get_rag_assistant()` 获取 RAG 引擎实例
  - [x] RAG 引擎未加载时返回明确错误信息
  - 验收标准: AI 服务可正确调用本地模型生成摘要、关键词、情感分析

## 阶段 2: 修改 Python RSS 网关路由

- [x] Task 2.1: 修改 AI 路由从代理改为本地服务
  - [x] 修改 `GET /api/rss/ai/config` — 返回本地模型配置（model_key, model_name, enabled, engine_loaded）
  - [x] 修改 `PUT /api/rss/ai/config` — 更新本地模型配置（enabled 开关）
  - [x] 修改 `POST /api/rss/ai/test` — 测试本地模型可用性
  - [x] 修改 `POST /api/rss/articles/{id}/analyze` — 使用本地 AI 服务分析文章
  - [x] 修改 `POST /api/rss/articles/analyze-all` — 使用本地 AI 服务批量分析
  - [x] 保持 API 路径不变，确保前端无需修改调用路径
  - 验收标准: 所有 AI 端点使用本地模型返回正确结果，不再代理到 Go 服务

## 阶段 3: 移除 Go 端 Ollama 代码

- [x] Task 3.1: 移除 Go AI 相关文件
  - [x] 删除 `services/rss-crawler/internal/service/ai_service.go`
  - [x] 删除 `services/rss-crawler/internal/handler/ai_handler.go`
  - [x] 删除 `services/rss-crawler/internal/repository/ai_cache_repo.go`
  - 验收标准: 上述文件已删除，Go 项目编译无引用错误

- [x] Task 3.2: 修改 Go 配置和模型
  - [x] 从 `services/rss-crawler/internal/model/system.go` 移除 `AIAnalysisCache` 结构体
  - [x] 从 `services/rss-crawler/internal/config/config.go` 移除 `OllamaConfig` 和 `AIConfig` 结构体及 Config 中的对应字段
  - [x] 从 `services/rss-crawler/config.yaml` 移除 `ollama` 和 `ai` 配置段
  - 验收标准: Go 配置不再包含 Ollama 和 AI 相关字段

- [x] Task 3.3: 修改 Go 服务入口
  - [x] 从 `services/rss-crawler/cmd/server/main.go` 移除 AI handler 的创建和路由注册
  - [x] 从 `services/rss-crawler/internal/handler/` 移除对 AI handler 的引用（如有）
  - [x] 验证 Go 项目 `go build ./cmd/server/` 编译通过
  - 验收标准: Go 服务编译通过，启动无 AI 相关错误

## 阶段 4: 更新项目配置

- [x] Task 4.1: 更新主配置文件
  - [x] 在 `config/config.yaml` 的 `rss` 段下新增 `ai` 子配置（enabled, cache_path）
  - 验收标准: config.yaml 包含 rss.ai 配置

## 阶段 5: 前端适配

- [x] Task 5.1: 更新前端 AI 类型定义
  - [x] 修改 `frontend/src/types/rss.ts` 中 `AIConfig` 类型，适配新的配置结构（model_key, model_name, enabled, engine_loaded）
  - 验收标准: TypeScript 编译无错误

- [x] Task 5.2: 更新前端 AI API 服务
  - [x] 修改 `frontend/src/services/rssApi.ts` 中 AI 相关 API 调用，适配新的响应格式
  - 验收标准: AI API 调用与后端新接口格式一致

- [x] Task 5.3: 更新前端 AI 设置 UI
  - [x] 修改 AI 设置组件，从 Ollama 连接配置改为本地模型状态显示
  - [x] 显示当前模型名称、加载状态、可用模型列表
  - [x] 移除 Ollama host/model/timeout 输入框
  - [x] 添加"前往智能问答加载模型"引导链接
  - 验收标准: AI 设置页面正确显示本地模型状态

## 阶段 6: 集成测试

- [x] Task 6.1: 端到端测试
  - [x] 测试 RAG 引擎未加载时 AI 分析返回 503 错误
  - [x] 测试 RAG 引擎加载后 AI 分析正常工作
  - [x] 测试缓存命中和缓存未命中场景
  - [x] 测试批量分析功能
  - [x] 测试 Go 服务编译和启动（无 AI 相关错误）
  - [x] 测试前端 AI 设置页面显示
  - 验收标准: 所有测试场景通过

# Task Dependencies

## 串行依赖
- Task 1.2 依赖 Task 1.1（AI 服务需要缓存模块）
- Task 2.1 依赖 Task 1.2（路由修改需要 AI 服务）
- Task 3.2 依赖 Task 3.1（配置修改需要先删除引用文件）
- Task 3.3 依赖 Task 3.2（入口修改需要配置清理完成）
- Task 5.2 依赖 Task 5.1（API 修改需要类型定义）
- Task 5.3 依赖 Task 5.2（UI 修改需要 API 适配）
- Task 6.1 依赖 Task 2.1 + Task 3.3 + Task 5.3（端到端测试需要所有修改完成）

## 可并行执行
- Task 1.1-1.2（Python AI 服务）与 Task 3.1-3.3（Go 代码清理）可并行
- Task 4.1（配置更新）与 Task 5.1-5.2（前端类型和 API）可并行
