# Tasks — 前端现代化重构双人任务分配

## 团队角色定义

| 角色 | 代号 | 技术栈 | 主要职责 |
|------|------|--------|---------|
| 后端工程师 | **成员A** | Python, FastAPI, PyTorch, LangChain | RAG API 拆分、后端测试、部署配置 |
| 前端工程师 | **成员B** | React, TypeScript, Ant Design, Vite | 前端项目搭建、组件开发、页面迁移 |

---

## 阶段 1: 后端 API 拆分（成员A 主导）

- [ ] Task 1.1: 创建 RAG API 服务框架 【成员A】 2026-05-05 → 2026-05-05
  - [ ] 创建 `src/rag_api/` 目录
  - [ ] 创建 `__init__.py`, `app.py`, `routes.py`, `models.py`, `dependencies.py`, `middleware.py` 空文件
  - 验收标准: 目录结构存在，所有文件可正常 import

- [ ] Task 1.2: 实现单例管理与依赖注入 【成员A】 2026-05-06 → 2026-05-06
  - [ ] 实现 `dependencies.py`: KnowledgeBase 单例、RAGAssistant 单例管理
  - [ ] 实现 `get_knowledge_base()`, `get_rag_assistant()`, `set_rag_assistant()` 函数
  - 验收标准: 单例函数可正确创建/获取/设置实例，单元测试通过

- [ ] Task 1.3: 实现 Pydantic 请求/响应模型 【成员A】 2026-05-07 → 2026-05-07
  - [ ] 实现 `models.py`: ChatRequest, ChatResponse, ModelLoadRequest, StatusResponse 等
  - 验收标准: 所有模型可通过 Pydantic 验证，字段类型与设计文档一致

- [ ] Task 1.4: 实现普通问答路由 `/api/rag/chat` 【成员A】 2026-05-08 → 2026-05-08
  - [ ] 实现 POST `/api/rag/chat` 路由，调用 RAGAssistant.query()
  - [ ] 处理引擎未加载时的 503 错误
  - 验收标准: curl/Swagger 可正常调用，返回 `{success, data: {answer, sources}}`

- [ ] Task 1.5: 实现 SSE 流式问答路由 `/api/rag/chat/stream` 【成员A】 2026-05-09 → 2026-05-10
  - [ ] 实现 POST `/api/rag/chat/stream` SSE 路由
  - [ ] 使用 StreamingResponse + event_generator 逐 token 推送
  - [ ] 发送 event: token / event: sources / event: done 三种事件
  - 验收标准: SSE 流正常推送，前端可解析 token 事件，流结束后收到 done 事件

- [ ] Task 1.6: 实现状态查询路由 `/api/rag/status` 【成员A】 2026-05-11 → 2026-05-11
  - [ ] 实现 GET `/api/rag/status` 返回引擎状态、模型信息、可用模型列表
  - 验收标准: 返回完整的 RAGStatus JSON，包含 engine_loaded、available_models 等

- [ ] Task 1.7: 实现模型加载/卸载路由 【成员A】 2026-05-12 → 2026-05-13
  - [ ] 实现 POST `/api/rag/model/load` 异步加载模型
  - [ ] 实现 POST `/api/rag/model/unload` 卸载模型释放显存
  - 验收标准: load 后 status 返回 engine_loaded=true；unload 后返回 false

- [ ] Task 1.8: 实现文件上传路由 `/api/rag/ingest` 【成员A】 2026-05-14 → 2026-05-14
  - [ ] 实现 POST `/api/rag/ingest` multipart/form-data 文件上传
  - [ ] 支持 pdf/txt/md 格式，自动检测文档类型
  - 验收标准: 上传文件后返回 chunks_count 和 doc_type

- [ ] Task 1.9: 实现知识库管理路由 【成员A】 2026-05-15 → 2026-05-15
  - [ ] 实现 POST `/api/rag/knowledge-base/auto-ingest` 自动导入
  - [ ] 实现 GET `/api/rag/knowledge-base/stats` 统计信息
  - 验收标准: auto-ingest 返回 total_files/success_count；stats 返回 total_chunks

- [ ] Task 1.10: 实现中间件 【成员A】 2026-05-16 → 2026-05-16
  - [ ] 实现统一错误处理中间件
  - [ ] 实现请求日志中间件
  - [ ] 配置 CORS 允许 localhost:5173
  - 验收标准: 错误返回统一 JSON 格式；日志记录请求路径和耗时

- [ ] Task 1.11: 创建 RAG API 启动入口 【成员A】 2026-05-17 → 2026-05-17
  - [ ] 创建 `rag_server.py`，读取 config.yaml，启动 uvicorn
  - [ ] 更新 `config/config.yaml` 添加 `rag_port: 8001`
  - 验收标准: `python rag_server.py` 可正常启动，Swagger UI 可访问

- [ ] Task 1.12: 更新技能树 API CORS 配置 【成员A】 2026-05-17 → 2026-05-17
  - [ ] 更新 `server.py` CORS allow_origins 添加 `http://localhost:5173`
  - 验收标准: 前端开发服务器可跨域访问技能树 API

- [ ] Task 1.13: 编写 RAG API 测试 【成员A】 2026-05-18 → 2026-05-19
  - [ ] 编写 `tests/test_rag_api.py` 覆盖所有 API 端点
  - [ ] 包含 status、chat、chat/stream、ingest、model/load 测试用例
  - 验收标准: pytest 全部通过，覆盖率 > 80%

- [ ] Task 1.14: Swagger UI 验证全部 API 【成员A】 2026-05-20 → 2026-05-20
  - [ ] 逐个验证所有 8 个 RAG API 端点
  - [ ] 验证请求/响应格式与设计文档一致
  - 验收标准: 所有 API 在 Swagger UI 中可正常调用，响应格式正确

---

## 阶段 2: 前端基础搭建（成员B 主导，与阶段1并行）

- [ ] Task 2.1: 初始化 Vite + React + TypeScript 项目 【成员B】 2026-05-08 → 2026-05-08
  - [ ] 执行 `npm create vite@latest frontend -- --template react-ts`
  - [ ] 配置 tsconfig.json 严格模式
  - 验收标准: `npm run dev` 可正常启动，浏览器显示默认页面

- [ ] Task 2.2: 安装前端依赖 【成员B】 2026-05-09 → 2026-05-09
  - [ ] 安装 antd, @ant-design/icons, zustand, react-router-dom, axios, @xyflow/react, react-markdown, dayjs
  - [ ] 安装 devDependencies: vitest, @testing-library/react, eslint, prettier
  - 验收标准: `npm run build` 无错误

- [ ] Task 2.3: 配置 Ant Design 主题 【成员B】 2026-05-10 → 2026-05-10
  - [ ] 在 App.tsx 中配置 ConfigProvider，主色 #1f77b4
  - [ ] 配置中文国际化 (zhCN)
  - 验收标准: Ant Design 组件使用主题色渲染

- [ ] Task 2.4: 实现应用主布局 【成员B】 2026-05-11 → 2026-05-12
  - [ ] 实现 `AppLayout.tsx`: 左侧边栏 + 顶部导航 + 内容区
  - [ ] 实现 `Header.tsx`: 应用标题 + 主题切换按钮
  - 验收标准: 布局在 1280px+ 宽度下正常显示

- [ ] Task 2.5: 实现侧边栏组件 【成员B】 2026-05-13 → 2026-05-14
  - [ ] 实现 `Sidebar.tsx`: 导航菜单（智能问答/技能树/设置）
  - [ ] 侧边栏底部显示知识库状态和引擎状态（Mock数据）
  - 验收标准: 点击菜单项可切换页面，状态指示器正确显示

- [ ] Task 2.6: 配置 React Router 【成员B】 2026-05-15 → 2026-05-15
  - [ ] 配置路由: `/` → ChatPage, `/skill-tree` → SkillTreePage, `/skill-tree/:id` → SkillTreeDetail, `/settings` → SettingsPage
  - [ ] 创建占位页面组件
  - 验收标准: 浏览器地址栏切换路由可显示对应页面

- [ ] Task 2.7: 封装 API Service 基础层 【成员B】 2026-05-16 → 2026-05-16
  - [ ] 实现 `services/api.ts`: 两个 axios 实例（skillTreeApiClient, ragApiClient）
  - [ ] 配置请求/响应拦截器、超时、错误处理
  - 验收标准: axios 实例可正常创建，拦截器可捕获网络错误

- [ ] Task 2.8: 封装业务 API 服务 【成员B】 2026-05-17 → 2026-05-18
  - [ ] 实现 `services/ragApi.ts`: chat, chatStream, ingest, getStatus, loadModel, unloadModel, autoIngest, getKnowledgeBaseStats
  - [ ] 实现 `services/skillTreeApi.ts`: list, get, create, delete, addSkill, establishRelation, generatePaths
  - [ ] 实现 `services/knowledgeBaseApi.ts`: upload, stats
  - 验收标准: 所有 API 函数签名与后端路由一致，TypeScript 类型正确

- [ ] Task 2.9: 实现 Zustand Store 【成员B】 2026-05-19 → 2026-05-20
  - [ ] 实现 `stores/chatStore.ts`: messages, isLoading, currentStreamingContent, addMessage, appendStreamToken, finalizeStream
  - [ ] 实现 `stores/skillTreeStore.ts`: trees, selectedTree, skills, CRUD actions
  - [ ] 实现 `stores/appStore.ts`: theme, ragStatus, sidebarCollapsed
  - 验收标准: Store 可正常创建，action 可正确更新状态

- [ ] Task 2.10: 配置 Vite 代理 【成员B】 2026-05-21 → 2026-05-21
  - [ ] 配置 `vite.config.ts`: `/api/skill-tree` → localhost:8000, `/api/rag` → localhost:8001
  - 验收标准: 前端请求 `/api/*` 可代理到后端服务

- [ ] Task 2.11: 实现 SSE Hook 【成员B】 2026-05-22 → 2026-05-23
  - [ ] 实现 `hooks/useSSE.ts`: connect/disconnect 方法
  - [ ] 支持 event: token / sources / done 三种事件解析
  - [ ] 支持 AbortController 取消请求
  - 验收标准: Hook 可正确解析 SSE 事件流，取消时无内存泄漏

- [ ] Task 2.12: 定义 TypeScript 类型 【成员B】 2026-05-24 → 2026-05-24
  - [ ] 实现 `types/chat.ts`: Message, Source, ChatState
  - [ ] 实现 `types/skillTree.ts`: SkillNode, SkillTree, LearningPath, SkillLevel, SkillType
  - [ ] 实现 `types/rag.ts`: RAGStatus, ModelInfo, RerankerInfo, ModelLoadRequest
  - [ ] 实现 `types/api.ts`: ApiResponse, PaginatedResponse
  - 验收标准: 所有类型与后端 API 响应格式一致，TypeScript 编译无错误

---

## 阶段 3: 功能迁移（成员B 主导，成员A 协助联调）

- [ ] Task 3.1: 实现智能问答页面 【成员B】 2026-05-25 → 2026-05-27
  - [ ] 实现 `ChatPage.tsx` + `ChatWindow.tsx`: 消息列表容器
  - [ ] 实现 `WelcomeCard.tsx`: 欢迎卡片 + 示例问题按钮
  - 验收标准: 页面布局与 Streamlit 版本视觉一致

- [ ] Task 3.2: 实现消息气泡组件 【成员B】 2026-05-28 → 2026-05-29
  - [ ] 实现 `MessageBubble.tsx`: 用户消息（蓝色靠右）、助手消息（白色靠左）
  - [ ] 支持 Markdown 渲染助手回复
  - 验收标准: 消息气泡样式与 Streamlit 版本一致，Markdown 正确渲染

- [ ] Task 3.3: 实现思考中动画 【成员B】 2026-05-30 → 2026-05-30
  - [ ] 实现 `ThinkingIndicator.tsx`: 三点跳动动画
  - 验收标准: 动画效果与 Streamlit 版本一致

- [ ] Task 3.4: 实现参考来源面板 【成员B】 2026-05-31 → 2026-05-31
  - [ ] 实现 `SourcePanel.tsx`: 折叠面板展示参考来源
  - [ ] 显示来源文件名和内容摘要
  - 验收标准: 点击展开可查看来源，内容与 Streamlit 版本一致

- [ ] Task 3.5: 实现聊天输入框 【成员B】 2026-06-01 → 2026-06-02
  - [ ] 实现 `ChatInput.tsx`: 输入框 + 发送按钮 + 文件上传图标
  - [ ] 支持 Enter 发送、Shift+Enter 换行
  - 验收标准: 输入框交互正常，文件上传弹窗可打开

- [ ] Task 3.6: 集成 SSE 流式输出 【成员B + 成员A联调】 2026-06-03 → 2026-06-05
  - [ ] 将 useSSE Hook 集成到 ChatWindow
  - [ ] 实现 token 逐字渲染（打字机效果）
  - [ ] 流结束后显示参考来源
  - [ ] 成员A 协助排查 SSE 连接问题
  - 验收标准: 发送问题后流式输出正常，打字机效果流畅，来源正确显示

- [ ] Task 3.7: 实现技能树列表页 【成员B】 2026-06-06 → 2026-06-07
  - [ ] 实现 `SkillTreePage.tsx` + `SkillTreeList.tsx`: 技能树列表展示
  - [ ] 实现创建技能树表单
  - [ ] 实现删除技能树确认
  - 验收标准: 列表可正常加载，创建/删除操作成功

- [ ] Task 3.8: 实现技能树详情页 【成员B】 2026-06-08 → 2026-06-09
  - [ ] 实现 `SkillTreeDetail.tsx`: 技能树详情展示
  - [ ] 展示技能节点列表、学习路径列表
  - 验收标准: 详情页数据与 Streamlit 版本一致

- [ ] Task 3.9: 实现添加技能表单 【成员B】 2026-06-10 → 2026-06-10
  - [ ] 实现 `AddSkillForm.tsx`: 技能名称/描述/难度/类型/学习时间
  - 验收标准: 表单提交后技能成功添加到技能树

- [ ] Task 3.10: 实现建立技能关系表单 【成员B】 2026-06-11 → 2026-06-11
  - [ ] 实现 `RelationForm.tsx`: 源技能/目标技能/关系类型选择
  - 验收标准: 关系建立成功，技能树详情中可看到关系

- [ ] Task 3.11: 实现学习路径列表 【成员B】 2026-06-12 → 2026-06-12
  - [ ] 实现 `LearningPathList.tsx`: 学习路径展示
  - [ ] 实现生成学习路径按钮
  - 验收标准: 路径生成成功，列表正确展示

- [ ] Task 3.12: 实现知识库管理面板 【成员B】 2026-06-13 → 2026-06-14
  - [ ] 实现 `KnowledgeBasePanel.tsx`: 知识库状态展示
  - [ ] 实现 `FileUploader.tsx`: 文件上传组件
  - 验收标准: 上传文件后知识库统计更新

- [ ] Task 3.13: 实现设置页面 【成员B】 2026-06-15 → 2026-06-16
  - [ ] 实现 `SettingsPage.tsx`: 设置页面布局
  - [ ] 实现 `ModelSelector.tsx`: 模型选择下拉框
  - [ ] 实现 `RerankerConfig.tsx`: 重排序配置（开关/模型/参数）
  - 验收标准: 配置项与 Streamlit 版本一致，保存后生效

- [ ] Task 3.14: 实现引擎启停控制 【成员B】 2026-06-17 → 2026-06-18
  - [ ] 实现 `EngineControl.tsx`: 启动/停止按钮、状态指示、加载进度
  - [ ] 集成状态轮询（每2s查询 /api/rag/status）
  - 验收标准: 点击启动后引擎加载成功，状态实时更新

---

## 阶段 4: 高级功能与优化（成员B 主导，成员A 协助部署）

- [ ] Task 4.1: 实现技能树可视化 【成员B】 2026-06-19 → 2026-06-22
  - [ ] 集成 React Flow (@xyflow/react)
  - [ ] 实现 `SkillGraph.tsx`: 交互式技能树节点图
  - [ ] 节点按难度等级着色（beginner=绿/intermediate=蓝/advanced=粉/expert=黄）
  - 验收标准: 技能树以图形方式展示，节点可点击查看详情

- [ ] Task 4.2: 实现节点拖拽和缩放交互 【成员B】 2026-06-23 → 2026-06-24
  - [ ] 支持节点拖拽调整位置
  - [ ] 支持画布缩放和平移
  - [ ] 支持节点连线展示关系
  - 验收标准: 拖拽/缩放/平移操作流畅，连线正确显示关系

- [ ] Task 4.3: 响应式布局适配 【成员B】 2026-06-25 → 2026-06-26
  - [ ] 移动端侧边栏自动折叠
  - [ ] 聊天消息全宽显示
  - [ ] 技能树列表卡片自适应列数
  - 验收标准: 在 375px-1920px 宽度范围内布局正常

- [ ] Task 4.4: 实现深色主题 【成员B】 2026-06-27 → 2026-06-28
  - [ ] 配置 Ant Design dark theme
  - [ ] 实现自定义 CSS 变量支持深色模式
  - [ ] 实现 `ThemeToggle.tsx` 切换按钮
  - 验收标准: 点击切换按钮可在亮色/深色主题间切换

- [ ] Task 4.5: 性能优化 【成员B】 2026-06-29 → 2026-06-30
  - [ ] React.lazy 路由懒加载
  - [ ] 消息列表虚拟滚动（消息 > 100条时）
  - [ ] 图片/组件预加载
  - 验收标准: 首屏加载 < 2s，Lighthouse Performance > 80

- [ ] Task 4.6: 更新启动脚本 【成员A】 2026-06-30 → 2026-06-30
  - [ ] 更新 `start.bat` / `start.sh` 添加 RAG API 启动和前端启动
  - 验收标准: 一键启动脚本可同时启动三个服务

---

## 阶段 5: 测试与上线（双人协作）

- [ ] Task 5.1: 后端 API 端到端测试 【成员A】 2026-07-01 → 2026-07-02
  - [ ] 验证所有 8 个 RAG API 端点
  - [ ] 验证 SSE 流式响应完整性
  - [ ] 验证文件上传和知识库导入
  - 验收标准: 所有 API 端点测试通过

- [ ] Task 5.2: 前端功能等价验证 【成员B】 2026-07-01 → 2026-07-03
  - [ ] 逐项验证 15 项功能等价清单
  - [ ] 对比 Streamlit 版本与 React 版本的交互行为
  - 验收标准: 15 项功能等价验证全部通过

- [ ] Task 5.3: 兼容性测试 【成员B】 2026-07-04 → 2026-07-04
  - [ ] Chrome/Firefox/Edge 浏览器测试
  - [ ] 桌面端 (1920px/1366px) + 移动端 (375px/768px) 测试
  - 验收标准: 主流浏览器和分辨率下功能正常

- [ ] Task 5.4: 部署配置 【成员A】 2026-07-04 → 2026-07-05
  - [ ] 编写 Nginx 反向代理配置
  - [ ] 编写 Docker Compose 配置（含 GPU 支持）
  - [ ] 编写前端生产构建脚本
  - 验收标准: Docker Compose 一键启动，Nginx 代理正常

- [ ] Task 5.5: 性能基准测试 【成员A + 成员B】 2026-07-06 → 2026-07-07
  - [ ] Lighthouse Performance 评分
  - [ ] 首屏加载时间测量
  - [ ] SSE 首 token 延迟测量
  - 验收标准: 首屏 < 2s，Lighthouse > 80，首 token < 200ms

---

# Task Dependencies

## 串行依赖（必须按顺序执行）
- Task 1.2 依赖 Task 1.1（单例管理需要目录结构）
- Task 1.3 依赖 Task 1.1（Pydantic 模型需要目录结构）
- Task 1.4-1.9 依赖 Task 1.2 + 1.3（路由依赖单例和模型）
- Task 1.11 依赖 Task 1.4-1.10（启动入口依赖所有路由和中间件）
- Task 1.13 依赖 Task 1.11（测试依赖服务可启动）
- Task 1.14 依赖 Task 1.13（验证依赖测试通过）
- Task 2.4 依赖 Task 2.3（布局依赖主题配置）
- Task 2.5 依赖 Task 2.4（侧边栏依赖布局）
- Task 2.8 依赖 Task 2.7（业务 API 依赖基础层）
- Task 3.6 依赖 Task 1.5 + Task 2.11（SSE 集成依赖后端 API 和前端 Hook）
- Task 3.8 依赖 Task 3.7（详情页依赖列表页）
- Task 3.9-3.11 依赖 Task 3.8（表单依赖详情页）
- Task 4.1 依赖 Task 3.8（可视化依赖详情页数据）
- Task 4.2 依赖 Task 4.1（交互依赖可视化基础）
- Task 5.1-5.5 依赖阶段 1-4 全部完成

## 可并行执行
- Task 1.1-1.3 与 Task 2.1-2.3 可并行（后端框架与前端初始化互不依赖）
- Task 1.4-1.14 与 Task 2.4-2.6 可并行（后端路由开发与前端布局开发互不依赖）
- Task 2.7-2.8 与 Task 1.4-1.9 可并行（前端 API 封装可先写接口，后端同步开发）
- Task 3.1-3.5 与 Task 3.7-3.11 可并行（聊天页面与技能树页面互不依赖）
- Task 4.3 与 Task 4.4 可并行（响应式与深色主题互不依赖）
- Task 5.1 与 Task 5.2 可并行（后端测试与前端测试互不依赖）

## 联调衔接点
- **衔接点 1** (2026-05-20): 成员A完成阶段1 → 成员B可对接真实 API
- **衔接点 2** (2026-06-03): 成员A协助 Task 3.6 SSE 联调
- **衔接点 3** (2026-06-30): 成员A完成启动脚本，成员B完成前端优化
- **衔接点 4** (2026-07-07): 双人协作完成性能测试和部署

---

# 工作量统计

| 成员 | 阶段1 | 阶段2 | 阶段3 | 阶段4 | 阶段5 | 总计工作日 |
|------|-------|-------|-------|-------|-------|-----------|
| 成员A | 14天 | 0天 | 3天(联调) | 1天 | 4天 | **22天** |
| 成员B | 0天 | 14天 | 18天 | 10天 | 4天 | **46天** |

> 注：成员B工作量较大，建议成员A在阶段2-3期间协助部分前端组件开发（如 KnowledgeBasePanel、FileUploader），以平衡工作量。调整后预估：成员A ~28天，成员B ~40天。

---

# 甘特图时间线

```
2026-05  ─────────────────────────────────────────────────────
W1 (05-05~05-09)  成员A: 1.1→1.4  |  成员B: 2.1→2.2
W2 (05-12~05-16)  成员A: 1.5→1.10 |  成员B: 2.3→2.5
W3 (05-19~05-23)  成员A: 1.11→1.14|  成员B: 2.6→2.11
W4 (05-26~05-30)  成员A: 协助/待命 |  成员B: 2.12, 3.1→3.3

2026-06  ─────────────────────────────────────────────────────
W5 (06-02~06-06)  成员A: 协助联调   |  成员B: 3.4→3.7
W6 (06-09~06-13)  成员A: 协助联调   |  成员B: 3.8→3.11
W7 (06-16~06-20)  成员A: 协助联调   |  成员B: 3.12→3.14, 4.1
W8 (06-23~06-27)  成员A: 4.6       |  成员B: 4.2→4.4
W9 (06-30)        成员A: 4.6       |  成员B: 4.5

2026-07  ─────────────────────────────────────────────────────
W10(07-01~07-03)  成员A: 5.1       |  成员B: 5.2
W11(07-04~07-07)  成员A: 5.4       |  成员B: 5.3, 5.5(协作)
```
