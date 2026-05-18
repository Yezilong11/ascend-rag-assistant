# Checklist — 添加纸龙一号模型支持

## 模型注册
- [x] `PREDEFINED_MODELS` 字典中包含 `zilong-1` 条目
- [x] `zilong-1` 配置包含 `repo_id`、`ms_repo_id`、`name`、`description`、`download_method` 字段
- [x] `GET /api/rag/status` 返回的 `available_models` 包含 `zilong-1`

## CLI 下载逻辑
- [x] `download_method == "cli"` 时使用 `subprocess.run` 调用 `modelscope download` 命令
- [x] CLI 命令格式为 `modelscope download --model <ms_repo_id> --local_dir <target_dir>`
- [x] CLI 下载失败时回退到 `snapshot_download` SDK 方式
- [x] SDK 也不可用时回退到 HuggingFace 在线加载
- [x] `download_method` 为 `sdk` 或未指定时，行为与现有逻辑完全一致

## ModelScope repo_id 解析
- [x] 模型配置包含 `ms_repo_id` 时，ModelScope 下载使用 `ms_repo_id`
- [x] 模型配置不包含 `ms_repo_id` 时，使用现有 Qwen 大小写修正逻辑
- [x] 现有模型（qwen2-1.5b、qwen2-0.5b、chatglm3-6b）的 ModelScope repo_id 解析不受影响

## 兼容性
- [x] 现有模型加载行为不受影响
- [x] `ModelLoadRequest.model_key` 验证自动适配新模型（无需修改 `models.py`）
- [x] 前端模型选择器自动显示新模型（无需修改前端代码）
