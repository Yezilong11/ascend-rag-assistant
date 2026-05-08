# Tasks

- [x] Task 1: 创建多模态类型定义 `frontend/src/types/multimodal.ts`
  - [x] SubTask 1.1: 定义 `ImageIngestResponse` 类型（对应后端 ImageIngestResultDTO.to_dict()）
  - [x] SubTask 1.2: 定义 `PDFIngestResponse` 类型（对应后端 PDFIngestResultDTO.to_dict()）
  - [x] SubTask 1.3: 定义 `MultimodalProcessingStatus` 类型（对应后端 get_processing_status 返回值）
  - [x] SubTask 1.4: 定义 `ImageSourceData` 类型（对应后端 ImageSourceDTO.to_dict()）
  - [x] SubTask 1.5: 定义 `MultimodalQueryResponse` 类型（对应后端 MultimodalQueryResultDTO.to_dict()）

- [x] Task 2: 创建多模态 API 客户端
  - [x] SubTask 2.1: 在 `frontend/src/services/api.ts` 中新增 `multimodalApiClient` axios 实例（baseURL: `/api/multimodal`，timeout: 120000ms）
  - [x] SubTask 2.2: 创建 `frontend/src/services/multimodalApi.ts`，实现 `ingestImage()`、`ingestPdf()`、`deleteBySource()`、`getStatus()` 方法

- [x] Task 3: 扩展 FileUploader 组件支持图片和多模态 PDF 上传
  - [x] SubTask 3.1: 扩展 input.accept 支持图片格式（.jpg/.jpeg/.png/.gif/.bmp）
  - [x] SubTask 3.2: 根据文件扩展名自动路由：图片走 multimodalApi.ingestImage()，PDF 走 multimodalApi.ingestPdf()，文本走原 knowledgeBaseApi.ingest()
  - [x] SubTask 3.3: 添加 VLM 开关（Switch 组件），传递 vlm_enabled 参数
  - [x] SubTask 3.4: 支持多图片批量上传

- [x] Task 4: 扩展 KnowledgeBasePanel 显示多模态统计
  - [x] SubTask 4.1: 在统计卡片区域新增"图片块数"卡片
  - [x] SubTask 4.2: 调用 multimodalApi 获取多模态知识库状态

- [x] Task 5: 扩展 ChatInput 支持图片附件
  - [x] SubTask 5.1: 在输入框旁添加图片上传按钮（PictureOutlined 图标）
  - [x] SubTask 5.2: 实现图片缩略图预览和删除功能
  - [x] SubTask 5.3: 发送时先上传图片到多模态知识库，再基于图片内容提问

- [x] Task 6: 在设置页面添加 VLM 配置
  - [x] SubTask 6.1: 在 SettingsPage 中添加 VLM 开关组件
  - [x] SubTask 6.2: 将 VLM 开关状态存储到 appStore

- [x] Task 7: 更新侧边栏导航
  - [x] SubTask 7.1: 在 Sidebar.tsx 的 menuItems 中添加"多模态知识库"导航项（PictureOutlined 图标，路径 /multimodal）
  - [x] SubTask 7.2: 在 App.tsx 中添加 /multimodal 路由

- [x] Task 8: 创建多模态知识库页面
  - [x] SubTask 8.1: 创建 `frontend/src/pages/MultimodalPage.tsx`，包含图片上传、PDF 导入、已导入图片列表
  - [x] SubTask 8.2: 创建 `frontend/src/components/multimodal/ImageIngestPanel.tsx`，图片上传面板
  - [x] SubTask 8.3: 创建 `frontend/src/components/multimodal/PDFIngestPanel.tsx`，PDF 导入面板

# Task Dependencies
- [Task 2] depends on [Task 1] (类型定义是 API 客户端的基础)
- [Task 3] depends on [Task 2] (FileUploader 需要 multimodalApi)
- [Task 4] depends on [Task 2] (KnowledgeBasePanel 需要 multimodalApi)
- [Task 5] depends on [Task 2] (ChatInput 需要 multimodalApi)
- [Task 6] depends on [Task 1] (VLM 配置需要类型定义)
- [Task 8] depends on [Task 2] (页面需要 multimodalApi)
- [Task 7] depends on [Task 8] (路由需要页面组件)
- [Task 3, 4, 5, 6] 可并行执行
