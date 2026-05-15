# Checklist — RSS AI 分析从 Ollama 迁移到本地模型

## Python AI 分析服务
- [x] `src/rss_gateway/ai_cache.py` 实现基于 JSON 文件的持久化缓存
- [x] 缓存读取（get）和写入（set）功能正常
- [x] 缓存文件损坏时不崩溃，自动重建
- [x] `src/rss_gateway/ai_service.py` 实现完整的 AI 分析服务
- [x] 摘要生成功能正常（100 字以内中文摘要）
- [x] 关键词提取功能正常（5 个关键词）
- [x] 情感分析功能正常（正面/中性/负面）
- [x] 使用 threading.Lock 保证推理线程安全
- [x] RAG 引擎未加载时返回 503 和明确错误提示
- [x] 输入内容截断为前 2000 字符

## Python RSS 网关路由
- [x] `GET /api/rss/ai/config` 返回本地模型配置（非 Ollama 配置）
- [x] `PUT /api/rss/ai/config` 可更新 enabled 开关
- [x] `POST /api/rss/ai/test` 检查本地模型可用性
- [x] `POST /api/rss/articles/{id}/analyze` 使用本地模型分析文章
- [x] `POST /api/rss/articles/analyze-all` 批量分析文章
- [x] AI 路由不再代理转发到 Go 服务

## Go 端 Ollama 代码移除
- [x] `services/rss-crawler/internal/service/ai_service.go` 已删除
- [x] `services/rss-crawler/internal/handler/ai_handler.go` 已删除
- [x] `services/rss-crawler/internal/repository/ai_cache_repo.go` 已删除
- [x] `services/rss-crawler/internal/model/system.go` 中 AIAnalysisCache 已移除
- [x] `services/rss-crawler/internal/config/config.go` 中 OllamaConfig 和 AIConfig 已移除
- [x] `services/rss-crawler/config.yaml` 中 ollama 和 ai 配置段已移除
- [x] `services/rss-crawler/cmd/server/main.go` 中 AI handler 注册已移除
- [x] Go 项目 `go build ./cmd/server/` 编译通过

## 项目配置
- [x] `config/config.yaml` 包含 `rss.ai` 配置段（enabled, cache_path）

## 前端适配
- [x] `frontend/src/types/rss.ts` 中 AIConfig 类型已更新
- [x] `frontend/src/services/rssApi.ts` 中 AI API 调用已适配新格式
- [x] AI 设置 UI 显示本地模型状态（非 Ollama 配置）
- [x] AI 设置页面包含"前往智能问答加载模型"引导

## 集成测试
- [x] RAG 引擎未加载时 AI 分析返回 503
- [x] RAG 引擎加载后 AI 分析正常工作
- [x] 缓存命中时跳过模型推理
- [x] 批量分析功能正常
- [x] Go 服务编译和启动无 AI 相关错误
- [x] 前端 AI 设置页面正常显示
