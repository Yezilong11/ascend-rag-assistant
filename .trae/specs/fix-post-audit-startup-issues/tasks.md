# Tasks

- [x] Task 1: 修复 load_model 端点死锁问题（Critical）
  - [x] 1.1: 将 dependencies.py 中的 `threading.Lock()` 改为 `threading.RLock()`
  - [x] 1.2: 验证 routes.py load_model 端点不再死锁

- [x] Task 2: 修复 query() 双重调用 _retrieve_and_rerank（Critical）
  - [x] 2.1: 修改 query() 方法，不再显式调用 _retrieve_and_rerank()，改为从 qa_chain 返回的 source_documents 中提取 sources
  - [x] 2.2: 确保 source_documents 中的文档经过重排序

- [x] Task 3: 修复降级模式下端点崩溃问题（High）
  - [x] 3.1: 在 routes.py 的 _ingest_document_to_kb、auto_ingest、knowledge_base_stats 中添加降级模式检查
  - [x] 3.2: 降级模式下使用安全的计数方式替代 kb.db._collection 访问

- [x] Task 4: 修复 UnicodeDecodeError 构造参数错误（High）
  - [x] 4.1: 将 knowledge_base.py 第501行的 `raise UnicodeDecodeError(...)` 改为 `raise ValueError(...)`

- [x] Task 5: 修复未释放 Reranker GPU 显存问题（High）
  - [x] 5.1: 在 dependencies.py 的 _clear_rag_assistant_unlocked() 中添加 Reranker 清理逻辑

- [x] Task 6: 修复 ChromaDB persist 兼容性（Medium）
  - [x] 6.1: 在 knowledge_base.py 中添加 hasattr 检查后再调用 db.persist()

- [x] Task 7: 修复 pipeline device 参数和 HuggingFacePipeline 导入（Medium）
  - [x] 7.1: 移除 rag_engine.py 中 pipeline() 的 device 参数
  - [x] 7.2: 将 HuggingFacePipeline 导入从 langchain_community 改为 langchain_huggingface

- [x] Task 8: 修复 Windows 控制台编码和配置文件容错（Medium）
  - [x] 8.1: 在 server.py 中添加 sys.stdout 编码设置或替换 emoji 为 ASCII
  - [x] 8.2: 在 server.py 中为配置文件读取添加 try-except

- [x] Task 9: 修复 Skill Tree Repository 单例和依赖声明（Low）
  - [x] 9.1: 将 FileSkillTreeRepository 改为模块级单例
  - [x] 9.2: 在 requirements.txt 中添加 langchain-classic 依赖

# Task Dependencies
- Task 1 独立（最高优先级，死锁修复）
- Task 2 独立
- Task 3 独立
- Task 4 独立
- Task 5 独立
- Task 6 独立
- Task 7 独立
- Task 8 独立
- Task 9 独立
- 所有 Task 可并行执行
