# 核心功能全面测试与修复 Spec

## Why
代码经过审计修改后，AI引擎无法启动（load_model 端点死锁），且存在多个导致核心功能（RAG、RSS、技能树）失效的缺陷。需要全面修复以确保系统可正常运行。

## What Changes
- 修复 load_model 端点非重入锁嵌套获取导致的死锁问题
- 修复 query() 双重调用 _retrieve_and_rerank 导致检索/重排序执行两次
- 修复降级模式下访问 kb.db._collection 导致 AttributeError
- 修复 UnicodeDecodeError 构造参数错误导致 TypeError
- 修复未释放 Reranker GPU 显存的问题
- 修复 db.persist() 在新版 ChromaDB 中已移除的问题
- 修复 pipeline() device 参数弃用问题
- 修复 HuggingFacePipeline 从弃用位置导入
- 修复 Windows 控制台 emoji 编码错误
- 修复 server.py 配置文件读取无错误处理
- 修复 Skill Tree Repository 每次请求创建新实例
- 添加 langchain-classic 到 requirements.txt

## Impact
- Affected code: src/rag_engine.py, src/rag_api/dependencies.py, src/rag_api/routes.py, src/knowledge_base.py, src/skill_tree/api/routes.py, server.py, requirements.txt

## ADDED Requirements

### Requirement: load_model 端点不得死锁
系统 SHALL 使用可重入锁（RLock）或避免在已持有锁的上下文中再次获取锁，确保 load_model 端点不会死锁。

#### Scenario: 模型加载请求不死锁
- **WHEN** 用户调用 POST /api/rag/model/load 加载模型
- **THEN** 端点 SHALL 立即返回 loading 状态，后台线程执行加载

### Requirement: query() 不得重复执行检索与重排序
系统 SHALL 确保 query() 方法只执行一次检索与重排序，从 qa_chain 返回的 source_documents 中提取来源信息。

#### Scenario: 单次查询只执行一次检索
- **WHEN** 调用 query() 进行问答
- **THEN** 向量检索和重排序 SHALL 只执行一次

### Requirement: 降级模式下端点不崩溃
系统 SHALL 在知识库降级模式（SimpleMemoryDB）下，所有端点正常工作，不因访问 _collection 属性而崩溃。

#### Scenario: 降级模式下知识库统计
- **WHEN** 知识库处于降级模式且用户请求 /api/rag/knowledge-base/stats
- **THEN** 系统 SHALL 返回合理的统计信息而非 500 错误

### Requirement: UnicodeDecodeError 正确构造
系统 SHALL 使用正确的异常类型和参数构造错误信息，不因异常构造错误而抛出 TypeError。

#### Scenario: 文件编码无法识别
- **WHEN** 导入文件时所有编码尝试均失败
- **THEN** 系统 SHALL 抛出 ValueError 而非 TypeError

### Requirement: 卸载模型时释放 Reranker 显存
系统 SHALL 在卸载模型时同时释放 Reranker 的 CrossEncoder 模型占用的 GPU 显存。

#### Scenario: 模型卸载后显存完全释放
- **WHEN** 调用 /api/rag/model/unload 卸载模型
- **THEN** 系统 SHALL 释放主模型、pipeline 和 Reranker 的全部 GPU 显存

### Requirement: ChromaDB persist 兼容性
系统 SHALL 兼容新版 ChromaDB（自动持久化），不因调用已移除的 persist() 方法而报错。

### Requirement: pipeline device 参数兼容性
系统 SHALL 不向 pipeline() 传递已弃用的 device 参数，模型已在正确设备上。

### Requirement: HuggingFacePipeline 从正确位置导入
系统 SHALL 从 langchain_huggingface 包导入 HuggingFacePipeline。

### Requirement: Windows 控制台编码兼容
系统 SHALL 在 Windows 控制台上不因 emoji 字符导致 UnicodeEncodeError。

### Requirement: 配置文件读取容错
系统 SHALL 在配置文件不存在时使用默认值而非崩溃。

### Requirement: Skill Tree Repository 单例
系统 SHALL 使用单例模式管理 FileSkillTreeRepository，避免每次请求创建新实例。

### Requirement: langchain-classic 依赖声明
系统 SHALL 在 requirements.txt 中声明 langchain-classic 依赖。

## MODIFIED Requirements
（无修改已有需求的场景）

## REMOVED Requirements
（无移除需求的场景）
