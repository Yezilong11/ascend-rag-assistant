# 添加 Qwen3.6-27B 模型下载选项 Spec

## Why
项目当前对话模型选择功能仅提供 4 个预定义模型（Qwen2-1.5B、Qwen2-0.5B、ChatGLM3-6B、纸龙一号），需要新增 Qwen3.6-27B 大模型选项。该模型需通过魔搭 CLI 执行 `modelscope download --model Qwen/Qwen3.6-27B --local_dir D:\ModelsTemporary\Qwen3.6-27B` 命令下载到指定目录，并在下载完成后自动加载为对话模型。

## What Changes
- 在 `PREDEFINED_MODELS` 字典中新增 `qwen3.6-27b` 模型条目
- 在模型配置中新增 `custom_local_dir` 字段，支持指定非默认的模型下载/加载目录（如 `D:\ModelsTemporary\Qwen3.6-27B`）
- 修改 `rag_engine.py` 中 LLM 模型下载逻辑，当模型配置包含 `custom_local_dir` 时，CLI 下载和本地加载均使用该目录
- 修改 `rag_engine.py` 中本地模型检测逻辑，优先检查 `custom_local_dir` 目录
- 修改 `ModelLoadRequest` 的 `model_dir` 字段默认值逻辑，当模型配置包含 `custom_local_dir` 时覆盖默认值
- 前端无需修改（模型列表从后端 API 动态获取，`ModelSelector` 组件自动渲染新选项）

## Impact
- Affected specs: add-zilong-1-model（复用其 CLI 下载机制，扩展 `custom_local_dir` 支持）
- Affected code:
  - `src/rag_engine.py` — 修改 `PREDEFINED_MODELS` 字典，修改 LLM 下载/加载逻辑
  - `src/rag_api/models.py` — 无需修改（`ModelLoadRequest.model_key` 验证自动适配新模型）
  - `src/rag_api/routes.py` — 可能需修改 `load_model` 端点，传递 `custom_local_dir` 到 `RAGAssistant`
  - `frontend/src/` — 无需修改

## ADDED Requirements

### Requirement: Qwen3.6-27B 模型注册
系统 SHALL 在 `PREDEFINED_MODELS` 字典中注册 `qwen3.6-27b` 模型，包含 `repo_id`、`ms_repo_id`、`name`、`description`、`download_method`、`custom_local_dir` 字段。

#### Scenario: 模型列表包含 Qwen3.6-27B
- **WHEN** 前端请求 `GET /api/rag/status` 获取可用模型列表
- **THEN** 返回的 `available_models` 中包含 `qwen3.6-27b` 条目，name 为"Qwen3.6-27B"，description 说明其为"大模型，需GPU加速，通过魔搭CLI下载到指定目录"

### Requirement: 自定义本地目录支持
系统 SHALL 支持为模型配置自定义本地目录（`custom_local_dir`），当该字段存在时，模型下载和加载均使用该目录而非默认的 `./models/<model_name>` 目录。

#### Scenario: 使用 custom_local_dir 下载模型
- **WHEN** 用户选择加载 `qwen3.6-27b` 模型且本地 `D:\ModelsTemporary\Qwen3.6-27B` 目录不存在该模型
- **THEN** 系统通过 `subprocess` 执行 `modelscope download --model Qwen/Qwen3.6-27B --local_dir D:\ModelsTemporary\Qwen3.6-27B` 下载模型
- **AND** 下载完成后从 `D:\ModelsTemporary\Qwen3.6-27B` 目录加载模型

#### Scenario: 使用 custom_local_dir 检测本地模型
- **WHEN** 用户选择加载 `qwen3.6-27b` 模型且 `D:\ModelsTemporary\Qwen3.6-27B` 目录已存在模型文件
- **THEN** 系统直接从 `D:\ModelsTemporary\Qwen3.6-27B` 目录加载模型，跳过下载步骤

#### Scenario: 不含 custom_local_dir 的模型行为不变
- **WHEN** 模型配置不包含 `custom_local_dir` 字段
- **THEN** 使用现有逻辑（`./models/<model_name>` 目录），行为与当前完全一致

### Requirement: CLI 下载命令精确匹配
系统 SHALL 在下载 Qwen3.6-27B 模型时，精确执行命令 `modelscope download --model Qwen/Qwen3.6-27B --local_dir D:\ModelsTemporary\Qwen3.6-27B`。

#### Scenario: 命令参数正确
- **WHEN** 系统执行 CLI 下载命令
- **THEN** `subprocess.run` 的参数为 `["modelscope", "download", "--model", "Qwen/Qwen3.6-27B", "--local_dir", "D:\\ModelsTemporary\\Qwen3.6-27B"]`

### Requirement: CLI 下载失败回退
系统 SHALL 在魔搭 CLI 下载失败时，依次回退到 ModelScope SDK 和 HuggingFace 在线加载。

#### Scenario: CLI 命令不存在
- **WHEN** `modelscope` CLI 未安装（`FileNotFoundError`）
- **THEN** 回退到 ModelScope SDK `snapshot_download` 方式，下载目录仍为 `D:\ModelsTemporary\Qwen3.6-27B`

#### Scenario: CLI 下载过程出错
- **WHEN** CLI 下载返回非零退出码（`CalledProcessError`）
- **THEN** 回退到 ModelScope SDK 方式，下载目录仍为 `D:\ModelsTemporary\Qwen3.6-27B`

#### Scenario: SDK 也不可用
- **WHEN** ModelScope SDK 不可用或下载失败
- **THEN** 回退到 HuggingFace 在线加载（使用 `repo_id` 传给 `from_pretrained`）

### Requirement: 下载进度反馈
系统 SHALL 在 CLI 下载过程中提供进度反馈，避免用户长时间等待无响应。

#### Scenario: 下载进度日志
- **WHEN** CLI 下载正在进行
- **THEN** 系统在日志/控制台输出下载进度信息
- **AND** 前端通过轮询 `GET /api/rag/status` 可感知"模型加载中"状态

### Requirement: 大模型 GPU 检测提示
系统 SHALL 在加载 Qwen3.6-27B 模型前检测 GPU 可用性，并在无 GPU 时给出警告。

#### Scenario: 无 GPU 时加载大模型
- **WHEN** 用户选择加载 `qwen3.6-27b` 模型但系统未检测到 CUDA GPU
- **THEN** 在日志中输出警告信息"Qwen3.6-27B 模型较大，未检测到GPU，加载和推理可能非常缓慢"
- **AND** 仍然允许加载（不阻止用户操作）

#### Scenario: 有 GPU 时正常加载
- **WHEN** 用户选择加载 `qwen3.6-27b` 模型且系统检测到 CUDA GPU
- **THEN** 正常执行下载和加载流程，使用 `torch.float16` 精度

## MODIFIED Requirements

### Requirement: LLM 模型下载逻辑
原 `rag_engine.py` 中 LLM 下载逻辑的本地模型检测仅检查 `./models/<model_name>` 目录，现增加 `custom_local_dir` 优先检测：当模型配置包含 `custom_local_dir` 时，优先检查该目录是否存在；若存在则直接加载，否则下载到该目录。

降级链保持不变：本地 -> CLI（如配置） -> SDK -> HuggingFace，但各步骤的目标目录根据 `custom_local_dir` 配置动态决定。

### Requirement: RAGAssistant 初始化参数
`RAGAssistant.__init__` 的 `model_dir` 参数语义扩展：当模型配置包含 `custom_local_dir` 时，该参数被忽略，改用 `custom_local_dir` 作为模型存储和加载路径。

## REMOVED Requirements
无
