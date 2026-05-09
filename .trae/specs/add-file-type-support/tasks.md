# Tasks

- [x] Task 1: 扩展后端 API 允许的文件扩展名
  - [x] SubTask 1.1: 修改 `src/rag_api/routes.py` 第 296 行 `allowed_extensions` 列表，新增 `.docx, .doc, .html, .htm, .png, .jpg, .jpeg, .pptx, .ppt, .csv, .xls, .xlsx, .json, .jsonl`
  - [x] SubTask 1.2: 修改 `src/rag_api/routes.py` 第 400 行 `supported_extensions` 元组，同步新增相同扩展名

- [x] Task 2: 在 KnowledgeBase 中新增辅助方法
  - [x] SubTask 2.1: 新增 `csv_to_markdown(csv_path)` 方法，使用 Python 内置 csv 模块解析 CSV 并转为 Markdown 表格
  - [x] SubTask 2.2: 新增 `json_to_text(json_path)` 方法，解析 JSON 并递归展平为 `key: value` 格式文本
  - [x] SubTask 2.3: 新增 `jsonl_to_text(jsonl_path)` 方法，逐行解析 JSONL 并拼接文本
  - [x] SubTask 2.4: 新增 `image_ocr_to_text(image_path)` 方法，使用 `EasyOCREngine` 提取图片文字

- [x] Task 3: 扩展 KnowledgeBase.ingest() 文件读取逻辑
  - [x] SubTask 3.1: 添加 `.docx/.doc` 分支，使用 `UnstructuredWordDocumentLoader`
  - [x] SubTask 3.2: 添加 `.html/.htm` 分支，使用 `UnstructuredHTMLLoader`
  - [x] SubTask 3.3: 添加 `.pptx/.ppt` 分支，使用 `UnstructuredPowerPointLoader`
  - [x] SubTask 3.4: 添加 `.xlsx/.xls` 分支，使用 `UnstructuredExcelLoader`
  - [x] SubTask 3.5: 添加 `.csv` 分支，调用 `self.csv_to_markdown()`
  - [x] SubTask 3.6: 添加 `.json` 分支，调用 `self.json_to_text()`
  - [x] SubTask 3.7: 添加 `.jsonl` 分支，调用 `self.jsonl_to_text()`
  - [x] SubTask 3.8: 添加 `.png/.jpg/.jpeg` 分支，调用 `self.image_ocr_to_text()`

- [x] Task 4: 扩展前端 FileUploader 组件
  - [x] SubTask 4.1: 更新 `input.accept` 属性为 `.pdf,.txt,.md,.doc,.docx,.html,.htm,.png,.jpg,.jpeg,.ppt,.pptx,.csv,.xls,.xlsx,.json,.jsonl`
  - [x] SubTask 4.2: 更新文件路由逻辑：所有新增文件类型统一走 `knowledgeBaseApi.ingest()`，仅图片保留 `multimodalApi.ingestImage()` 路由（当 VLM 开关开启时）
  - [x] SubTask 4.3: 更新提示文字为 "支持 PDF、Word、Excel、PPT、HTML、JSON、CSV、图片等格式，最大 50MB"

# Task Dependencies
- [Task 2] depends on nothing (可独立开发)
- [Task 3] depends on [Task 2] (ingest 调用新方法)
- [Task 1] depends on nothing (可独立开发)
- [Task 4] depends on [Task 1, Task 3] (前端需要后端支持新类型)
- [Task 1, Task 2] 可并行执行
