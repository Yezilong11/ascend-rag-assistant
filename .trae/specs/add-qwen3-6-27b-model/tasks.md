# Tasks — 添加 Qwen3.6-27B 模型下载选项

## 阶段 1: 注册模型

- [x] Task 1.1: 在 `PREDEFINED_MODELS` 中新增 `qwen3.6-27b` 模型条目
  - [x] 在 `src/rag_engine.py` 的 `PREDEFINED_MODELS` 字典中添加 `"qwen3.6-27b"` key
  - [x] 配置字段：`repo_id: "Qwen/Qwen3.6-27B"`, `ms_repo_id: "Qwen/Qwen3.6-27B"`, `name: "Qwen3.6-27B"`, `description: "大模型，需NPU加速，通过魔搭CLI下载到指定目录"`, `download_method: "cli"`, `custom_local_dir: "D:\\ModelsTemporary\\Qwen3.6-27B"`, `requires_npu: True`
  - 验收标准: `PREDEFINED_MODELS["qwen3.6-27b"]` 返回正确的配置字典，`GET /api/rag/status` 返回的模型列表包含 Qwen3.6-27B

## 阶段 2: 开发 NPU 设备检测模块

- [x] Task 2.1: 创建 `src/hardware_checker.py` 模块，实现 NPU 设备存在性检测
  - [x] 实现 `check_npu_available() -> bool` 函数
  - [x] 通过 `subprocess.run(["npu-smi", "info"], capture_output=True, text=True)` 检测 NPU 设备
  - [x] 若命令执行成功（返回码为 0 且 stdout 非空），返回 `True`
  - [x] 若命令不存在（`FileNotFoundError`）或执行失败（返回码非 0），返回 `False`
  - [x] 捕获所有异常，确保检测函数不会因异常而中断模型加载流程
  - 验收标准: 有 NPU 设备时返回 True；无 NPU 设备时返回 False；异常时不崩溃

## 阶段 3: 集成 NPU 检测到模型启动流程

- [x] Task 3.1: 修改 `RAGAssistant.__init__`，在模型下载前集成 NPU 检测
  - [x] 在获取模型配置后，检查 `model_config.get("requires_npu", False)`
  - [x] 若 `requires_npu` 为 True，调用 `check_npu_available()` 执行 NPU 检测
  - [x] 将检测结果存储到 `self.npu_available`
  - [x] 若检测通过：设置 `self.device = "npu"`，`self.torch_dtype = torch.float16`，输出"NPU设备检测通过，将以NPU模式加载模型"
  - [x] 若检测不通过：设置 `self.device = "cpu"`，`self.torch_dtype = torch.float32`，输出降级警告
  - [x] 若 `requires_npu` 为 False：保持现有设备检测逻辑（CUDA/CPU）
  - 验收标准: `qwen3.6-27b` 模型启动时自动触发 NPU 检测；其他模型不受影响

- [x] Task 3.2: 修改模型加载逻辑，根据检测结果选择设备和精度
  - [x] 在 `AutoModelForCausalLM.from_pretrained()` 调用中，使用 `self.torch_dtype` 替代硬编码的 `torch.float16`
  - [x] 在模型 `.to(device)` 调用中，使用 `self.device` 替代自动检测
  - [x] 确保 NPU 模式下使用 `torch_npu` 进行设备映射（如可用）
  - 验收标准: NPU 检测通过时模型以 float16 + NPU 加载；检测失败时以 float32 + CPU 加载

## 阶段 4: 实现 custom_local_dir 支持

- [x] Task 4.1: 修改 `RAGAssistant.__init__` 中本地模型检测逻辑，支持 `custom_local_dir`
  - [x] 在获取模型配置后，检查 `model_config.get("custom_local_dir")`
  - [x] 若 `custom_local_dir` 存在，使用该路径作为 `local_model_path` 进行本地检测
  - [x] 若 `custom_local_dir` 不存在，保持现有逻辑（`os.path.join(model_dir, local_model_name)`）
  - 验收标准: 配置了 `custom_local_dir` 的模型优先从指定目录检测和加载；未配置的模型行为不变

- [x] Task 4.2: 修改 CLI 下载逻辑，支持 `custom_local_dir` 作为下载目标目录
  - [x] 当 `custom_local_dir` 存在时，CLI 下载的 `--local_dir` 参数使用 `custom_local_dir` 值
  - [x] 当 `custom_local_dir` 不存在时，保持现有逻辑（`os.path.join(model_dir, local_model_name)`）
  - [x] 确保 `subprocess.run` 的 `--local_dir` 参数正确传递 Windows 路径
  - 验收标准: `qwen3.6-27b` 模型 CLI 下载命令为 `modelscope download --model Qwen/Qwen3.6-27B --local_dir D:\ModelsTemporary\Qwen3.6-27B`

- [x] Task 4.3: 修改 SDK 下载和 HuggingFace 回退逻辑，支持 `custom_local_dir`
  - [x] 当 `custom_local_dir` 存在时，SDK 下载的 `local_dir` 参数使用 `custom_local_dir` 值
  - [x] 当 `custom_local_dir` 存在且 CLI 和 SDK 均失败时，HuggingFace 回退仍使用 `custom_local_dir` 作为缓存目录
  - 验收标准: 回退链中每一步都使用正确的目标目录

## 阶段 5: 端到端验证

- [x] Task 5.1: 验证模型列表 API
  - [x] 启动后端服务，调用 `GET /api/rag/status`
  - [x] 确认 `available_models` 中包含 `qwen3.6-27b` 条目
  - [x] 确认 name 为 "Qwen3.6-27B"，description 正确
  - 验收标准: API 返回正确的模型信息

- [x] Task 5.2: 验证前端模型选择 UI
  - [x] 启动前端服务，进入设置页面
  - [x] 确认模型选择列表中出现 "Qwen3.6-27B" 选项
  - [x] 确认点击可选择该模型
  - 验收标准: 前端正确展示新模型选项

- [x] Task 5.3: 验证 NPU 检测模块
  - [x] 在非 NPU 环境下触发 `qwen3.6-27b` 模型加载，确认检测返回 False
  - [x] 确认降级为 CPU 模式，日志中记录降级原因
  - [x] 确认模型以 float32 + CPU 模式加载
  - 验收标准: NPU 检测正确执行，降级流程正常

- [x] Task 5.4: 验证 CLI 下载命令
  - [x] 模拟本地目录不存在的情况，触发 `qwen3.6-27b` 模型加载
  - [x] 确认执行的命令为 `modelscope download --model Qwen/Qwen3.6-27B --local_dir D:\ModelsTemporary\Qwen3.6-27B`
  - [x] 确认 CLI 失败时正确回退到 SDK
  - 验收标准: 命令参数正确，回退机制正常

- [x] Task 5.5: 验证现有模型不受影响
  - [x] 分别加载 qwen2-1.5b、qwen2-0.5b、chatglm3-6b、zilong-1 模型
  - [x] 确认所有现有模型的下载和加载行为与修改前一致
  - 验收标准: 现有模型功能无回归

# Task Dependencies

## 串行依赖
- Task 3.1 依赖 Task 1.1 + Task 2.1（集成检测需要模型配置和检测模块）
- Task 3.2 依赖 Task 3.1（设备选择需要检测结果）
- Task 4.1-4.3 依赖 Task 1.1（目录逻辑需要模型配置中的 `custom_local_dir` 字段）
- Task 5.1-5.5 依赖 Task 3.1 + Task 3.2 + Task 4.1-4.3

## 可并行执行
- Task 2.1 可与 Task 1.1 并行（检测模块与模型注册相互独立）
- Task 4.1-4.3 可与 Task 3.1-3.2 并行（目录逻辑与检测逻辑修改不同代码段）
- Task 5.1-5.5 可并行执行
