# 核心功能代码审计修复 Spec

## Why
项目经过两轮代码审计，共发现40+个问题，涵盖代码冗余、并发安全、安全漏洞、架构缺陷等。需要按照审计报告对已有功能进行修复，提升代码质量和系统稳定性。

## What Changes
- 提取 RAG 引擎冗余检索逻辑为共享方法，统一 Prompt 模板
- 修复并发安全问题：全局状态加锁、实例状态追踪改为返回值传递
- 修复安全漏洞：文件上传路径遍历、CORS 配置、错误信息泄露
- 修复知识库降级模式、默认文档插入等缺陷
- 修复 RSS 网关全局锁、事件循环、空操作端点等问题
- 修复技能树并发写入、时间戳硬编码等问题
- 替换 print 为 logging，修复 model_key 崩溃、异常隐藏等问题

## Impact
- Affected code: src/rag_engine.py, src/rag_api/dependencies.py, src/rag_api/routes.py, src/rag_api/app.py, src/knowledge_base.py, src/rss_gateway/ai_service.py, src/rss_gateway/routes.py, src/rss_gateway/client.py, src/rss_gateway/ai_cache.py, src/skill_tree/infrastructure/repositories.py, src/skill_tree/domain/models.py, src/skill_tree/domain/services.py, server.py

## ADDED Requirements

### Requirement: RAG 引擎检索逻辑去冗余
系统 SHALL 将 query() 和 query_stream() 中重复的检索+重排序逻辑提取为 `_retrieve_and_rerank()` 共享方法。

#### Scenario: 检索逻辑统一
- **WHEN** 调用 query() 或 query_stream() 进行文档检索
- **THEN** 两者 SHALL 使用同一个 `_retrieve_and_rerank()` 方法，确保行为一致

### Requirement: 统一 Prompt 模板
系统 SHALL 使用统一的 Prompt 模板，非流式和流式接口 SHALL 使用相同的指令规则。

#### Scenario: Prompt 一致性
- **WHEN** 通过不同接口（query/query_stream）对同一问题进行问答
- **THEN** 两个接口 SHALL 使用完全相同的 Prompt 模板

### Requirement: 并发安全的状态追踪
系统 SHALL 将 `_last_reranked_docs` 和 `_last_sources` 从实例属性改为方法返回值，避免并发请求间的数据混淆。

#### Scenario: 并发请求不混淆来源信息
- **WHEN** 多个用户同时发起问答请求
- **THEN** 每个用户 SHALL 只看到自己请求对应的文档来源信息

### Requirement: 全局状态线程安全保护
系统 SHALL 为 dependencies.py 中的全局变量添加 threading.Lock 保护，防止并发加载导致的竞态条件。

#### Scenario: 并发模型加载保护
- **WHEN** 用户A发起模型加载请求时用户B也发起加载
- **THEN** 系统 SHALL 通过锁机制确保只有一个加载进程运行

### Requirement: RerankCompatibleRetriever 提取为模块级类
系统 SHALL 将 RerankCompatibleRetriever 从 _init_qa_chain 方法内部提取为模块级类，消除 Pydantic arbitrary_types_allowed 绕过和内部导入问题。

### Requirement: 文件上传路径安全
系统 SHALL 对 ingest_file 端点的 file.filename 进行安全清洗，防止路径遍历攻击。

#### Scenario: 恶意文件名拦截
- **WHEN** 用户上传文件名包含路径遍历字符（如 `../../../etc/passwd`）
- **THEN** 系统 SHALL 清洗文件名或拒绝请求

### Requirement: CORS 配置收紧
系统 SHALL 将 CORS 中间件的 allow_methods 和 allow_headers 从通配符 `*` 改为具体允许的值列表。

### Requirement: 错误信息不泄露内部细节
系统 SHALL 在异常处理中使用通用错误消息返回给客户端，不暴露内部路径、模型信息、堆栈细节。

### Requirement: 知识库降级模式改进
系统 SHALL 在 ChromaDB 初始化失败降级到 SimpleMemoryDB 时记录告警状态，并在查询时返回明确提示。

### Requirement: 移除知识库默认文档插入
系统 SHALL 移除 ChromaDB 初始化时插入默认文档的逻辑，并修复 auto_ingest 中 `current_count > 1` 的隐式前提。

### Requirement: RSS AI 分析并发改进
系统 SHALL 将 RSSAIService 的全局互斥锁改为 Semaphore，添加推理超时机制。

### Requirement: analyze_all_articles 异步模式修复
系统 SHALL 使用 FastAPI BackgroundTasks 替代手动创建线程和事件循环的模式。

### Requirement: update_ai_config 端点修复
系统 SHALL 实现 update_ai_config PUT 端点的实际更新逻辑，或将其改为 GET 端点。

### Requirement: 技能树文件写入并发保护
系统 SHALL 为 FileSkillTreeRepository 添加文件锁，防止并发写入导致 JSON 文件损坏。

### Requirement: 技能树时间戳修复
系统 SHALL 将技能树中硬编码的 "2024-01-01" 时间戳改为使用 datetime.now().isoformat()。

### Requirement: 流式输出边界条件处理
系统 SHALL 在检索结果为空时返回明确提示而非让模型无参考信息生成回答。

### Requirement: model_key 不存在时优雅处理
系统 SHALL 在 model_key 不存在于 PREDEFINED_MODELS 时返回错误而非 KeyError 崩溃。

### Requirement: query() 异常不隐藏真实错误
系统 SHALL 让 query() 在异常时抛出类型化异常，而非返回伪装成正常结果的错误消息。

### Requirement: 替换 print 为 logging
系统 SHALL 将 rag_engine.py 和 knowledge_base.py 中的 print 语句替换为 logging 模块调用。

### Requirement: 文件上传流式写入
系统 SHALL 将 ingest_file 端点从全量读入内存再写文件改为流式写入，避免大文件内存泄漏。

## MODIFIED Requirements
（无修改已有需求的场景）

## REMOVED Requirements
（无移除需求的场景）
