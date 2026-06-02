# Checklist — 添加 Qwen3.6-27B 模型下载选项

## 模型注册
- [x] `PREDEFINED_MODELS` 字典中包含 `qwen3.6-27b` 条目，字段完整（repo_id, ms_repo_id, name, description, download_method, custom_local_dir, requires_npu）
- [x] `GET /api/rag/status` 返回的 `available_models` 包含 `qwen3.6-27b`，name 为 "Qwen3.6-27B"

## NPU 设备检测模块
- [x] `src/hardware_checker.py` 模块存在且可正常导入
- [x] `check_npu_available()` 函数通过 `npu-smi info` 命令检测 NPU 存在性
- [x] NPU 设备存在时返回 `True`
- [x] `npu-smi` 命令不存在时返回 `False`（不崩溃）
- [x] `npu-smi` 命令执行失败时返回 `False`（不崩溃）
- [x] 异常情况下返回 `False`（不崩溃）

## NPU 检测集成
- [x] `qwen3.6-27b` 模型启动时自动触发 NPU 检测
- [x] 不含 `requires_npu` 配置的模型跳过 NPU 检测
- [x] 检测结果存储在 `self.npu_available` 中
- [x] NPU 可用时日志输出"NPU设备检测通过，将以NPU模式加载模型"
- [x] NPU 不可用时日志输出"未检测到NPU设备，已降级为CPU模式运行，推理性能将显著下降"
- [x] NPU 模式下使用 `torch.float16` 精度
- [x] CPU 降级模式下使用 `torch.float32` 精度

## custom_local_dir 支持
- [x] 配置了 `custom_local_dir` 的模型，本地检测优先使用 `custom_local_dir` 路径
- [x] 未配置 `custom_local_dir` 的模型，本地检测逻辑与修改前完全一致
- [x] CLI 下载命令的 `--local_dir` 参数使用 `custom_local_dir` 值（当配置存在时）
- [x] CLI 下载命令精确为 `modelscope download --model Qwen/Qwen3.6-27B --local_dir D:\ModelsTemporary\Qwen3.6-27B`
- [x] SDK 下载的 `local_dir` 参数使用 `custom_local_dir` 值（当配置存在时）
- [x] HuggingFace 回退时目标目录正确

## 下载回退机制
- [x] CLI 下载失败（FileNotFoundError）时回退到 SDK
- [x] CLI 下载失败（CalledProcessError）时回退到 SDK
- [x] SDK 不可用或失败时回退到 HuggingFace 在线加载
- [x] 回退链中每一步的目标目录根据 `custom_local_dir` 正确决定

## 前端展示
- [x] 设置页面模型选择列表中出现 "Qwen3.6-27B" 选项
- [x] 点击可选择该模型，选中状态正确高亮
- [x] 选中后点击"启动AI引擎"可正常触发加载流程

## 回归验证
- [x] qwen2-1.5b 模型加载行为不受影响
- [x] qwen2-0.5b 模型加载行为不受影响
- [x] chatglm3-6b 模型加载行为不受影响
- [x] zilong-1 模型加载行为不受影响
- [x] 所有重排序模型加载行为不受影响
