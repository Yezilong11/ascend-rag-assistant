# 增加文件类型输入支持 Spec

## Why
当前 RAG 系统 `/api/rag/ingest` 仅支持 PDF/TXT/MD 三种文件类型，无法满足用户上传 Word、Excel、PPT、HTML、JSON、图片等常见文件的需求，限制了知识库的实用性。

## What Changes
- 扩展后端 `rag_api/routes.py` 的 `allowed_extensions` 和 `supported_extensions`，新增 13 种文件扩展名
- 扩展后端 `knowledge_base.py` 的 `ingest()` 方法，新增 8 种文件格式的文本提取逻辑
- 在 `KnowledgeBase` 类中新增 `csv_to_markdown()`、`json_to_text()`、`jsonl_to_text()`、`image_ocr_to_text()` 四个辅助方法
- 扩展前端 `FileUploader.tsx` 的 `input.accept` 属性和文件路由逻辑，统一走 `knowledgeBaseApi.ingest()` 处理所有新增文件类型

## Impact
- Affected specs: 无已有 spec 受影响
- Affected code:
  - `src/rag_api/routes.py` — allowed_extensions、supported_extensions
  - `src/knowledge_base.py` — ingest() 方法 + 新增 4 个辅助方法
  - `frontend/src/components/knowledge/FileUploader.tsx` — input.accept、文件路由逻辑

## ADDED Requirements

### Requirement: Word 文件导入
系统 SHALL 支持上传 `.docx` 和 `.doc` 格式的 Word 文件，通过 `UnstructuredWordDocumentLoader` 提取文本内容后导入知识库。

#### Scenario: 上传 docx 文件
- **WHEN** 用户上传 `.docx` 文件到 `/api/rag/ingest`
- **THEN** 系统使用 `UnstructuredWordDocumentLoader` 提取文本，切分后存入 ChromaDB
- **AND** 返回 `{success: true, data: {filename, doc_type, chunks_count}}`

#### Scenario: 上传旧版 doc 文件
- **WHEN** 用户上传 `.doc` 文件
- **THEN** 系统同样使用 `UnstructuredWordDocumentLoader` 提取文本
- **AND** 如果解析失败，返回友好错误信息

### Requirement: HTML 文件导入
系统 SHALL 支持上传 `.html` 和 `.htm` 格式的 HTML 文件，通过 `UnstructuredHTMLLoader` 提取纯文本内容。

#### Scenario: 上传 HTML 文件
- **WHEN** 用户上传 `.html` 或 `.htm` 文件
- **THEN** 系统提取 HTML 中的纯文本内容（去除标签），切分后存入知识库

### Requirement: PPT 文件导入
系统 SHALL 支持上传 `.pptx` 和 `.ppt` 格式的 PowerPoint 文件，通过 `UnstructuredPowerPointLoader` 提取每页幻灯片的文本内容。

#### Scenario: 上传 pptx 文件
- **WHEN** 用户上传 `.pptx` 文件
- **THEN** 系统提取每页幻灯片的文本内容，按页拼接后切分存入知识库

### Requirement: Excel 和 CSV 文件导入
系统 SHALL 支持上传 `.csv`、`.xls`、`.xlsx` 格式的表格文件。

#### Scenario: 上传 CSV 文件
- **WHEN** 用户上传 `.csv` 文件
- **THEN** 系统使用内置 `csv` 模块解析，转为 Markdown 表格文本后切分存入知识库

#### Scenario: 上传 xlsx/xls 文件
- **WHEN** 用户上传 `.xlsx` 或 `.xls` 文件
- **THEN** 系统使用 `UnstructuredExcelLoader` 提取文本内容

### Requirement: JSON 和 JSONL 文件导入
系统 SHALL 支持上传 `.json` 和 `.jsonl` 格式的结构化数据文件。

#### Scenario: 上传 JSON 文件
- **WHEN** 用户上传 `.json` 文件
- **THEN** 系统解析 JSON 结构，递归展平为 `key: value` 格式的可读文本后存入知识库

#### Scenario: 上传 JSONL 文件
- **WHEN** 用户上传 `.jsonl` 文件
- **THEN** 系统逐行解析 JSON 对象，每行转为文本后拼接存入知识库

### Requirement: 图片文件 OCR 导入
系统 SHALL 支持上传 `.png`、`.jpg`、`.jpeg` 格式的图片文件，通过 `EasyOCREngine` 提取文字后导入知识库（无需 VLM）。

#### Scenario: 上传含文字的图片
- **WHEN** 用户上传 `.png` 或 `.jpg` 图片
- **THEN** 系统使用 `EasyOCREngine` 提取图片中的文字，将 OCR 文本切分后存入知识库

#### Scenario: 上传无文字的图片
- **WHEN** 用户上传的图片中未识别到文字
- **THEN** 系统存入 `[图片中未识别到文字]` 作为占位文本

## MODIFIED Requirements

### Requirement: RAG API 允许的文件扩展名
原 `rag_api/routes.py` 中 `allowed_extensions = [".pdf", ".txt", ".md"]`，现扩展为 `[".pdf", ".txt", ".md", ".docx", ".doc", ".html", ".htm", ".png", ".jpg", ".jpeg", ".pptx", ".ppt", ".csv", ".xls", ".xlsx", ".json", ".jsonl"]`。

### Requirement: 自动导入支持的文件扩展名
原 `rag_api/routes.py` 中 `supported_extensions = (".pdf", ".txt", ".md")`，现扩展为与 `allowed_extensions` 一致的完整列表。

### Requirement: 前端文件上传组件 accept 属性
原 `FileUploader.tsx` 的 `input.accept` 为 `.pdf,.txt,.md,.doc,.docx,.jpg,.jpeg,.png,.gif,.bmp`，现扩展为 `.pdf,.txt,.md,.doc,.docx,.html,.htm,.png,.jpg,.jpeg,.ppt,.pptx,.csv,.xls,.xlsx,.json,.jsonl`。

### Requirement: 前端文件上传路由逻辑
原 `FileUploader.tsx` 将图片文件路由到 `multimodalApi.ingestImage()`、PDF 路由到 `multimodalApi.ingestPdf()`、其余走 `knowledgeBaseApi.ingest()`。现修改为：所有新增文件类型统一走 `knowledgeBaseApi.ingest()`（后端已支持），仅保留图片走 `multimodalApi.ingestImage()` 的路由（如果用户需要 VLM 描述），PDF 文本导入也走 `knowledgeBaseApi.ingest()`。

## REMOVED Requirements
无移除的需求。
