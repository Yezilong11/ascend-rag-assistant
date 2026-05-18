# 添加纸龙一号模型支持 Spec

## Why
项目当前仅支持 Qwen2 和 ChatGLM3 三个预定义 LLM 模型，需要新增"纸龙一号"（zilong-1）模型支持。该模型托管于魔搭 ModelScope（`yzl111/zilong-1`），需要增加通过魔搭 CLI 下载的能力，与现有的 Python SDK `snapshot_download` 方式并行支持。

## What Changes
- 在 `PREDEFINED_MODELS` 字典中新增 `zilong-1` 模型条目
- 在模型配置中新增 `ms_repo_id` 字段，用于指定 ModelScope 上的仓库 ID
- 在模型配置中新增 `download_method` 字段，支持 `sdk`（默认，使用 `snapshot_download`）和 `cli`（使用 `modelscope download` 命令行）两种下载方式
- 修改 `rag_engine.py` 中 LLM 模型下载逻辑，增加 CLI 下载分支（通过 `subprocess` 调用 `modelscope download --model <repo_id> --local_dir <target_dir>`）
- 前端无需修改（模型列表从后端 API 动态获取）

## Impact
- Affected specs: 无
- Affected code:
  - `src/rag_engine.py` — 修改 `PREDEFINED_MODELS` 字典，修改 LLM 下载逻辑
  - `src/rag_api/models.py` — 无需修改（`ModelLoadRequest.model_key` 验证自动适配新模型）

## ADDED Requirements

### Requirement: 纸龙一号模型注册
系统 SHALL 在 `PREDEFINED_MODELS` 字典中注册 `zilong-1` 模型，包含 `repo_id`、`ms_repo_id`、`name`、`description`、`download_method` 字段。

#### Scenario: 模型列表包含纸龙一号
- **WHEN** 前端请求 `GET /api/rag/status` 获取可用模型列表
- **THEN** 返回的 `available_models` 中包含 `zilong-1` 条目，name 为"纸龙一号"，description 说明其来源

### Requirement: 魔搭 CLI 下载支持
系统 SHALL 支持通过魔搭 CLI（`modelscope download`）下载模型，作为 Python SDK `snapshot_download` 之外的替代下载方式。

#### Scenario: 使用 CLI 下载纸龙一号模型
- **WHEN** 用户选择加载 `zilong-1` 模型且本地不存在该模型，且模型配置 `download_method` 为 `cli`
- **THEN** 系统通过 `subprocess` 执行 `modelscope download --model yzl111/zilong-1 --local_dir ./models/zilong-1` 下载模型
- **AND** 下载完成后从本地目录加载模型

#### Scenario: CLI 下载失败回退
- **WHEN** 魔搭 CLI 下载失败（命令不存在、网络错误、返回非零退出码）
- **THEN** 系统回退到 Python SDK `snapshot_download` 方式下载
- **AND** 如果 SDK 也不可用，回退到 HuggingFace 在线加载

#### Scenario: 使用 SDK 下载的模型（默认行为不变）
- **WHEN** 模型配置 `download_method` 为 `sdk` 或未指定
- **THEN** 使用现有的 `snapshot_download` 方式下载，行为与当前完全一致

### Requirement: 模型配置扩展
系统 SHALL 在 `PREDEFINED_MODELS` 的模型配置字典中支持以下新增字段：
- `ms_repo_id`: ModelScope 上的仓库 ID（当与 HuggingFace `repo_id` 不同时使用）
- `download_method`: 下载方式，可选 `sdk`（默认）或 `cli`

#### Scenario: ms_repo_id 存在时使用
- **WHEN** 模型配置包含 `ms_repo_id` 字段
- **THEN** ModelScope 下载时使用 `ms_repo_id` 而非 `repo_id`

#### Scenario: ms_repo_id 不存在时回退
- **WHEN** 模型配置不包含 `ms_repo_id` 字段
- **THEN** ModelScope 下载时使用 `repo_id`（兼容现有模型）

## MODIFIED Requirements

### Requirement: LLM 模型下载逻辑
原 `rag_engine.py` 中 LLM 下载逻辑仅支持"本地 -> ModelScope SDK -> HuggingFace"三级降级，现增加 CLI 下载方式，降级链变为"本地 -> ModelScope CLI（如配置） -> ModelScope SDK -> HuggingFace"四级降级。

## REMOVED Requirements
无
