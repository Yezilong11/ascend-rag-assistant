# Tasks — 添加纸龙一号模型支持

## 阶段 1: 注册模型

- [x] Task 1.1: 在 `PREDEFINED_MODELS` 中新增 `zilong-1` 模型条目
  - [x] 在 `src/rag_engine.py` 的 `PREDEFINED_MODELS` 字典中添加 `"zilong-1"` key
  - [x] 配置字段：`repo_id: "yzl111/zilong-1"`, `ms_repo_id: "yzl111/zilong-1"`, `name: "纸龙一号"`, `description: "魔搭社区模型，通过CLI下载"`, `download_method: "cli"`
  - 验收标准: `PREDEFINED_MODELS["zilong-1"]` 返回正确的配置字典，`GET /api/rag/status` 返回的模型列表包含纸龙一号

## 阶段 2: 实现 CLI 下载逻辑

- [x] Task 2.1: 修改 `rag_engine.py` 中 LLM 模型下载逻辑，增加 CLI 下载分支
  - [x] 在模型下载代码段（`__init__` 方法中 `if os.path.exists(local_model_path)` 的 `else` 分支）中，增加 CLI 下载判断
  - [x] 当 `download_method == "cli"` 时，使用 `subprocess.run(["modelscope", "download", "--model", ms_repo_id, "--local_dir", target_dir], check=True)` 执行下载
  - [x] CLI 下载失败时，回退到 `snapshot_download` SDK 方式
  - [x] SDK 也不可用时，回退到 HuggingFace 在线加载
  - [x] 降级链：本地 -> CLI（如配置） -> SDK -> HuggingFace
  - 验收标准: zilong-1 模型可通过 CLI 下载；CLI 失败时自动回退到 SDK；其他模型行为不变

- [x] Task 2.2: 修改 ModelScope repo_id 解析逻辑，优先使用 `ms_repo_id`
  - [x] 当模型配置包含 `ms_repo_id` 时，ModelScope 下载使用 `ms_repo_id`
  - [x] 当模型配置不包含 `ms_repo_id` 时，使用现有逻辑（Qwen 大小写修正等）
  - 验收标准: zilong-1 使用 `yzl111/zilong-1` 作为 ModelScope repo_id；现有 Qwen 模型仍使用大小写修正逻辑

## 阶段 3: 验证

- [x] Task 3.1: 端到端验证
  - [x] 验证 `GET /api/rag/status` 返回的模型列表包含 `zilong-1`
  - [x] 验证 `POST /api/rag/model/load` 使用 `model_key: "zilong-1"` 时能正确触发下载逻辑
  - [x] 验证现有模型（qwen2-1.5b、qwen2-0.5b、chatglm3-6b）加载行为不受影响
  - 验收标准: 所有验证通过

# Task Dependencies

## 串行依赖
- Task 2.1 依赖 Task 1.1（下载逻辑需要模型配置中的 `download_method` 字段）
- Task 2.2 依赖 Task 1.1（repo_id 解析需要模型配置中的 `ms_repo_id` 字段）
- Task 3.1 依赖 Task 2.1 + Task 2.2

## 可并行执行
- Task 2.1 和 Task 2.2 可并行（修改同一文件的不同逻辑段，但建议串行避免冲突）
