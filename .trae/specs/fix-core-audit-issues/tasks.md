# Tasks

- [x] Task 1: RAG 引擎检索逻辑去冗余与 Prompt 统一
  - [x] 1.1: 在 RAGAssistant 中提取 `_retrieve_and_rerank(question)` 方法，包含 similarity_search + rerank 逻辑
  - [x] 1.2: 让 query() 通过 RerankCompatibleRetriever 调用 `_retrieve_and_rerank`，而非独立实现
  - [x] 1.3: 让 query_stream() 调用 `_retrieve_and_rerank`，删除重复的检索代码
  - [x] 1.4: 统一 query() 和 query_stream() 的 Prompt 模板为同一份，放置在类常量中
  - [x] 1.5: 将 `_last_reranked_docs` 和 `_last_sources` 从实例属性改为方法返回值，消除并发数据混淆

- [x] Task 2: RerankCompatibleRetriever 提取为模块级类
  - [x] 2.1: 将 RerankCompatibleRetriever 从 _init_qa_chain 内部提取到模块级别
  - [x] 2.2: 移除 Pydantic arbitrary_types_allowed 绕过，改为正常参数传递
  - [x] 2.3: 将方法内部的 import 语句移到模块顶部

- [x] Task 3: 全局状态线程安全保护
  - [x] 3.1: 在 dependencies.py 中添加 threading.Lock 保护 _rag_assistant、_knowledge_base、_is_loading
  - [x] 3.2: 修改 get_rag_assistant()、set_rag_assistant()、clear_rag_assistant() 使用锁保护
  - [x] 3.3: 修改 load_model 路由使用锁保护 _is_loading 标记

- [x] Task 4: 安全漏洞修复
  - [x] 4.1: 在 ingest_file 端点中对 file.filename 进行安全清洗（使用 pathlib.Path 或正则移除路径分隔符）
  - [x] 4.2: 收紧 CORS 配置，将 allow_methods 和 allow_headers 从通配符改为具体值列表
  - [x] 4.3: 在 routes.py 异常处理中使用通用错误消息，不暴露 str(e) 内部细节

- [x] Task 5: 知识库缺陷修复
  - [x] 5.1: 移除 ChromaDB 初始化时插入默认文档的逻辑
  - [x] 5.2: 修复 auto_ingest 中 `current_count > 1` 的判断逻辑
  - [x] 5.3: 在 SimpleMemoryDB 降级时添加告警状态标志和查询提示

- [x] Task 6: RSS 网关修复
  - [x] 6.1: 将 RSSAIService 的 threading.Lock 改为 threading.Semaphore(2)，添加推理超时参数
  - [x] 6.2: 将 analyze_all_articles 改为使用 FastAPI BackgroundTasks
  - [x] 6.3: 实现 update_ai_config PUT 端点的实际更新逻辑

- [x] Task 7: 技能树修复
  - [x] 7.1: 为 FileSkillTreeRepository 添加文件锁（threading.Lock 或 filelock）
  - [x] 7.2: 将硬编码的 "2024-01-01" 时间戳改为 datetime.now().isoformat()

- [x] Task 8: 其他代码质量修复
  - [x] 8.1: 在 query_stream 中添加检索结果为空时的早期返回提示
  - [x] 8.2: 为 model_key 添加 PREDEFINED_MODELS.get() 回退逻辑
  - [x] 8.3: 让 query() 异常时抛出类型化异常而非返回伪装正常结果
  - [x] 8.4: 将 rag_engine.py 和 knowledge_base.py 中的 print 替换为 logging
  - [x] 8.5: 将 ingest_file 从全量读入内存改为流式写入（shutil.copyfileobj）

# Task Dependencies
- Task 1 和 Task 2 有依赖：Task 2（提取 RerankCompatibleRetriever）应在 Task 1（检索逻辑去冗余）之前或同时完成
- Task 3 独立
- Task 4 独立
- Task 5 独立
- Task 6 独立
- Task 7 独立
- Task 8 独立
- Task 1, 2, 3, 4, 5, 6, 7, 8 可并行执行（除 Task 1 和 2 的内部依赖外）
