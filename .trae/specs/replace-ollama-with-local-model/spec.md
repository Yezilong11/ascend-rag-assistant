# RSS AI 分析从 Ollama 迁移到本地模型 Spec

## Why
当前 RSS 模块的 AI 分析功能依赖外部 Ollama 服务（默认 llama2），需要额外部署和维护。项目自身已有基于 Qwen2 的本地模型推理能力（RAG 引擎），将 RSS AI 分析迁移到本地模型可消除外部依赖、统一模型管理、降低运维复杂度。

## What Changes
- 新增 Python RSS AI 分析服务 `src/rss_gateway/ai_service.py`，复用 RAG 引擎已加载的模型 pipeline
- 修改 Python RSS 网关路由 `src/rss_gateway/routes.py`，AI 相关端点从代理 Go 改为调用本地 AI 服务
- 新增 Python 文件缓存 `src/rss_gateway/ai_cache.py`，JSON 文件持久化分析结果
- **BREAKING** 移除 Go RSS 服务中全部 Ollama 相关代码（AIService、AIHandler、AICacheRepository、AIAnalysisCache 模型、配置）
- 修改 Go RSS 服务配置 `services/rss-crawler/config.yaml`，移除 ollama 和 ai 配置段
- 修改 Go RSS 服务入口 `services/rss-crawler/cmd/server/main.go`，移除 AI handler 注册
- 修改项目配置 `config/config.yaml`，新增 `rss.ai` 配置段
- 修改前端 `AIConfig` 类型定义和 AI 设置 UI，适配新的配置结构

## Impact
- Affected specs: integrate-rss-module（AI 代理部分需更新）
- Affected code:
  - `src/rss_gateway/ai_service.py` — 新增
  - `src/rss_gateway/ai_cache.py` — 新增
  - `src/rss_gateway/routes.py` — 修改 AI 路由
  - `src/rss_gateway/__init__.py` — 可能更新导出
  - `config/config.yaml` — 新增 rss.ai 配置
  - `services/rss-crawler/internal/service/ai_service.go` — 删除
  - `services/rss-crawler/internal/handler/ai_handler.go` — 删除
  - `services/rss-crawler/internal/repository/ai_cache_repo.go` — 删除
  - `services/rss-crawler/internal/model/system.go` — 移除 AIAnalysisCache
  - `services/rss-crawler/internal/config/config.go` — 移除 OllamaConfig、AIConfig
  - `services/rss-crawler/cmd/server/main.go` — 移除 AI handler 注册
  - `services/rss-crawler/config.yaml` — 移除 ollama 和 ai 段
  - `frontend/src/types/rss.ts` — 修改 AIConfig 类型
  - `frontend/src/services/rssApi.ts` — 适配新 AI API 响应格式
  - `frontend/src/components/rss/` — AI 设置 UI 适配

## ADDED Requirements

### Requirement: Python RSS AI 分析服务
系统 SHALL 在 Python 端提供 RSS AI 分析服务，复用 RAG 引擎已加载的模型 pipeline 进行文本生成，支持文章摘要生成、关键词提取、情感分析三项能力。

#### Scenario: 分析单篇文章
- **WHEN** 调用 `POST /api/rss/articles/{id}/analyze` 且 RAG 引擎已加载模型
- **THEN** 从 Go 服务获取文章内容，使用本地模型生成摘要、关键词、情感分析，缓存结果到 JSON 文件，返回分析结果

#### Scenario: RAG 引擎未加载
- **WHEN** 调用 AI 分析端点但 RAG 引擎未加载模型
- **THEN** 返回 503 错误和提示信息"RAG引擎未加载，请先在智能问答页面加载模型"

#### Scenario: 批量分析所有文章
- **WHEN** 调用 `POST /api/rss/articles/analyze-all`
- **THEN** 从 Go 服务获取所有文章列表，在后台线程逐篇分析，立即返回"分析已开始"

#### Scenario: 分析结果缓存命中
- **WHEN** 请求分析的文章已有缓存结果（基于内容哈希匹配）
- **THEN** 直接返回缓存结果，不调用模型推理

### Requirement: Python 文件缓存
系统 SHALL 使用 JSON 文件持久化 AI 分析结果，缓存键为文章内容哈希，支持跨重启保留。

#### Scenario: 缓存写入
- **WHEN** AI 分析完成一篇文章
- **THEN** 将分析结果以 `{content_hash: {summary, keywords, sentiment, timestamp}}` 格式写入 JSON 文件

#### Scenario: 缓存读取
- **WHEN** 请求分析文章且缓存文件中存在该文章内容哈希
- **THEN** 直接返回缓存结果，跳过模型推理

#### Scenario: 缓存文件损坏
- **WHEN** 缓存 JSON 文件格式损坏或不可读
- **THEN** 忽略缓存，重新执行分析，重建缓存文件

### Requirement: AI 配置端点适配
系统 SHALL 将 AI 配置端点从 Ollama 配置改为本地模型配置。

#### Scenario: 获取 AI 配置
- **WHEN** 调用 `GET /api/rss/ai/config`
- **THEN** 返回本地模型配置（model_key, model_name, enabled, engine_loaded）

#### Scenario: 测试 AI 连接
- **WHEN** 调用 `POST /api/rss/ai/test`
- **THEN** 检查 RAG 引擎是否已加载模型，返回可用性状态

### Requirement: 线程安全推理
系统 SHALL 保证模型推理的线程安全，避免并发请求导致推理异常。

#### Scenario: 并发分析请求
- **WHEN** 多个 AI 分析请求同时到达
- **THEN** 使用线程锁串行化模型推理，确保每次只有一个请求使用 pipeline

## MODIFIED Requirements

### Requirement: RSS AI 代理路由
原 `src/rss_gateway/routes.py` 中 AI 相关路由代理转发到 Go 服务的 Ollama 端点，现改为调用 Python 本地 AI 服务，不再转发到 Go。

### Requirement: Go RSS 服务 AI 功能
原 Go RSS 服务包含完整的 AI 分析功能（AIService、AIHandler、缓存），现全部移除，AI 分析职责转移到 Python 端。

### Requirement: 前端 AI 配置界面
原前端 AI 设置界面显示 Ollama 连接配置（host、model、timeout），现改为显示本地模型状态（当前模型、加载状态、可用模型列表）。

## REMOVED Requirements

### Requirement: Ollama 集成
**Reason**: 替换为项目本地模型，消除外部 Ollama 依赖
**Migration**: 所有 Ollama 相关代码从 Go 服务移除，Python 端使用 RAG 引擎模型替代

### Requirement: Go 端 AI 分析缓存
**Reason**: 缓存管理迁移到 Python 端，使用 JSON 文件替代 SQLite 表
**Migration**: 已有的 Go SQLite 缓存数据不迁移（分析结果可重新生成）
