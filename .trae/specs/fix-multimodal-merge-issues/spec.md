# 多模态前端集成 Spec

## Why
后端多模态模块（`src/multimodal/`）已合并到主分支，API 路由已注册到 `server.py`，但前端完全缺失对应的 API 客户端、类型定义和 UI 组件，导致多模态功能无法被用户使用。

## What Changes
- 新增前端多模态 API 客户端（`multimodalApi.ts`）和 axios 实例
- 新增前端多模态类型定义（`multimodal.ts`）
- 扩展 `FileUploader` 组件支持图片上传和 PDF 多模态导入
- 扩展 `KnowledgeBasePanel` 组件显示多模态统计信息
- 扩展 `ChatInput` 组件支持图片附件上传
- 扩展 `SettingsPage` 添加 VLM 开关配置
- 更新 `Sidebar` 添加多模态知识库导航项

## Impact
- Affected specs: 无已有 spec 受影响
- Affected code:
  - `frontend/src/services/api.ts` — 新增 multimodalApiClient
  - `frontend/src/services/multimodalApi.ts` — 新建
  - `frontend/src/types/multimodal.ts` — 新建
  - `frontend/src/components/knowledge/FileUploader.tsx` — 扩展支持图片
  - `frontend/src/components/knowledge/KnowledgeBasePanel.tsx` — 扩展统计
  - `frontend/src/components/chat/ChatInput.tsx` — 扩展图片附件
  - `frontend/src/pages/SettingsPage.tsx` — 添加 VLM 配置
  - `frontend/src/components/layout/Sidebar.tsx` — 添加导航项

## ADDED Requirements

### Requirement: 多模态 API 客户端
系统 SHALL 在前端提供 `multimodalApiClient` axios 实例和 `multimodalApi` 服务模块，对接后端 `/api/multimodal/*` 端点。

#### Scenario: 上传图片导入知识库
- **WHEN** 用户通过 `multimodalApi.ingestImage()` 上传图片文件列表和文档类型
- **THEN** 向 `POST /api/multimodal/image/ingest` 发送 multipart/form-data 请求，包含 files、document_type、vlm_enabled 字段
- **AND** 返回 `ImageIngestResponse` 包含 success、total_count、success_count、failed_count

#### Scenario: 上传 PDF 多模态导入
- **WHEN** 用户通过 `multimodalApi.ingestPdf()` 上传 PDF 文件
- **THEN** 向 `POST /api/multimodal/pdf/ingest` 发送 multipart/form-data 请求，包含 file、document_type、extract_images、vlm_enabled 字段
- **AND** 返回 `PDFIngestResponse` 包含 success、image_chunks_count、extracted_images_count

#### Scenario: 删除多模态来源
- **WHEN** 用户通过 `multimodalApi.deleteBySource()` 删除指定来源
- **THEN** 向 `DELETE /api/multimodal/source/{source_file}` 发送请求
- **AND** 返回 deleted_count

#### Scenario: 获取处理状态
- **WHEN** 用户通过 `multimodalApi.getStatus()` 查询处理状态
- **THEN** 向 `GET /api/multimodal/status/{source_file}` 发送请求
- **AND** 返回 exists、total_chunks、processed、failed、pending 字段

### Requirement: 多模态类型定义
系统 SHALL 在 `frontend/src/types/multimodal.ts` 中定义完整的 TypeScript 类型，对应后端 DTO。

#### Scenario: 类型完整性
- **WHEN** 前端代码引用多模态类型
- **THEN** 可使用 `ImageIngestResponse`、`PDFIngestResponse`、`MultimodalProcessingStatus`、`ImageSourceData`、`MultimodalQueryResponse` 等类型
- **AND** 所有类型字段与后端 DTO 的 `to_dict()` 输出一致

### Requirement: 图片上传支持
系统 SHALL 扩展 `FileUploader` 组件，支持图片格式上传和多模态 PDF 导入。

#### Scenario: 上传图片文件
- **WHEN** 用户在文件上传区域选择 `.jpg/.jpeg/.png/.gif/.bmp` 格式文件
- **THEN** 文件通过 `multimodalApi.ingestImage()` 上传到多模态知识库
- **AND** 上传成功后显示成功提示

#### Scenario: 上传 PDF 启用图片提取
- **WHEN** 用户上传 PDF 文件且勾选"提取图片"选项
- **THEN** 文件通过 `multimodalApi.ingestPdf()` 上传，extract_images 设为 true
- **AND** 上传成功后显示提取的图片数量

#### Scenario: VLM 开关
- **WHEN** 用户在上传区域切换 VLM 开关
- **THEN** 上传请求中 vlm_enabled 字段跟随开关状态

### Requirement: 知识库多模态统计
系统 SHALL 在 `KnowledgeBasePanel` 组件中展示多模态知识库的统计信息。

#### Scenario: 显示图片块统计
- **WHEN** 知识库面板加载
- **THEN** 在现有统计卡片旁新增"图片块数"统计卡片
- **AND** 通过 `multimodalApi.getStatus()` 或后端扩展接口获取图片块数量

### Requirement: 聊天图片附件
系统 SHALL 扩展 `ChatInput` 组件，支持在提问时附加图片。

#### Scenario: 附加图片提问
- **WHEN** 用户点击输入框旁的图片按钮并选择图片
- **THEN** 图片缩略图显示在输入框上方，可删除
- **AND** 发送时图片通过 `multimodalApi.ingestImage()` 先上传，再基于图片内容提问

#### Scenario: 取消图片附件
- **WHEN** 用户点击图片缩略图上的删除按钮
- **THEN** 图片从附件列表中移除

### Requirement: VLM 配置
系统 SHALL 在设置页面提供 VLM 开关配置。

#### Scenario: 启用 VLM
- **WHEN** 用户在设置页面开启 VLM 开关
- **THEN** 后续多模态上传请求中 vlm_enabled 为 true
- **AND** VLM 将对图片生成描述文本

#### Scenario: 禁用 VLM
- **WHEN** 用户在设置页面关闭 VLM 开关
- **THEN** 后续多模态上传请求中 vlm_enabled 为 false
- **AND** 仅使用 OCR 提取文字

### Requirement: 多模态导航入口
系统 SHALL 在侧边栏添加"多模态知识库"导航项。

#### Scenario: 导航到多模态知识库
- **WHEN** 用户点击侧边栏"多模态知识库"导航项
- **THEN** 路由跳转到 `/multimodal` 页面
- **AND** 显示多模态知识库管理界面

## MODIFIED Requirements

### Requirement: 前端 API 客户端注册
原 `frontend/src/services/api.ts` 仅包含 skillTreeApiClient、ragApiClient、rssApiClient，现新增 multimodalApiClient，baseURL 为 `/api/multimodal`，timeout 为 120000ms（图片处理耗时较长）。

### Requirement: 文件上传组件 accept 属性
原 `FileUploader` 的 input.accept 仅为 `.pdf,.txt,.md,.doc,.docx`，现扩展为 `.pdf,.txt,.md,.doc,.docx,.jpg,.jpeg,.png,.gif,.bmp`，并根据文件类型自动路由到对应 API。

### Requirement: 侧边栏导航项
原 `Sidebar.tsx` 包含智能问答、技能树、RSS 资讯、系统设置四个导航项，现新增"多模态知识库"导航项，使用 `PictureOutlined` 图标。

## REMOVED Requirements
无移除的需求。
