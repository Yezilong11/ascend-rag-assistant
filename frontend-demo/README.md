# 昇腾AI竞赛智能助教 - React 前端 Demo

> 本项目是基于架构设计文档创建的 React 前端 Demo，展示了将 Streamlit 单体应用重构为现代化 React + FastAPI 架构的前端实现方案。

## 技术栈

- **框架**: React 18 + TypeScript
- **构建工具**: Vite 5
- **UI 组件库**: Ant Design 5
- **状态管理**: Zustand
- **路由**: React Router 6
- **样式**: Tailwind CSS
- **HTTP 客户端**: Axios

## 项目结构

```
frontend-demo/
├── src/
│   ├── components/          # UI 组件
│   │   ├── chat/           # 聊天相关组件
│   │   │   ├── ChatMessage.tsx
│   │   │   ├── ChatInput.tsx
│   │   │   └── ChatWindow.tsx
│   │   ├── common/         # 通用组件
│   │   │   ├── Layout.tsx
│   │   │   ├── Header.tsx
│   │   │   └── Sidebar.tsx
│   │   ├── skilltree/      # 技能树相关组件
│   │   │   ├── SkillTreeCard.tsx
│   │   │   └── SkillNodeCard.tsx
│   │   └── knowledge/      # 知识库相关组件
│   │       └── FileUploader.tsx
│   ├── pages/              # 页面组件
│   │   ├── ChatPage.tsx
│   │   ├── SkillTreePage.tsx
│   │   ├── KnowledgeBasePage.tsx
│   │   └── SettingsPage.tsx
│   ├── stores/             # 状态管理 (Zustand)
│   │   ├── chatStore.ts
│   │   ├── skillTreeStore.ts
│   │   └── appStore.ts
│   ├── services/           # API 服务层
│   │   └── api.ts
│   ├── types/              # TypeScript 类型定义
│   │   └── index.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── public/
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.js
└── README.md
```

## 功能特性

### 1. 智能问答页面
- 实时流式对话输出
- 消息气泡样式
- 参考来源展示
- 文件上传到知识库
- 模型选择切换

### 2. 技能树管理页面
- 技能树列表展示
- 创建/删除技能树
- 技能节点管理
- 学习路径生成
- 技能完成进度跟踪

### 3. 知识库管理页面
- 文档上传（支持 PDF/TXT/MD）
- 文档列表展示
- 知识库统计信息
- 文档类型分类

### 4. 设置页面
- 系统状态监控
- 主题模式切换
- 模型配置
- 重排序参数调整
- API 地址配置

## 快速开始

### 环境要求

- Node.js >= 18.0.0
- npm >= 9.0.0

### 安装依赖

```bash
cd frontend-demo
npm install
```

### 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3000 查看 Demo。

### 构建生产版本

```bash
npm run build
```

构建产物将输出到 `dist/` 目录。

## API 集成

Demo 默认配置连接以下后端服务：

- **技能树 API**: http://localhost:8000
- **RAG API**: http://localhost:8001

如需修改，可通过环境变量配置：

```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_RAG_API_BASE_URL=http://localhost:8001
```

## 与后端 API 的对应关系

### 技能树 API (Port 8000)

| 前端调用 | 后端接口 | 说明 |
|---------|---------|------|
| `GET /api/skill-tree/` | 获取技能树列表 |
| `POST /api/skill-tree/` | 创建技能树 |
| `GET /api/skill-tree/{id}` | 获取技能树详情 |
| `DELETE /api/skill-tree/{id}` | 删除技能树 |
| `POST /api/skill-tree/{id}/skills` | 添加技能 |
| `POST /api/skill-tree/{id}/skills/relation` | 建立技能关系 |
| `POST /api/skill-tree/{id}/paths/generate` | 生成学习路径 |

### RAG API (Port 8001)

| 前端调用 | 后端接口 | 说明 |
|---------|---------|------|
| `POST /api/rag/chat` | 普通问答 |
| `POST /api/rag/chat/stream` | 流式问答 (SSE) |
| `POST /api/rag/ingest` | 上传文档 |
| `GET /api/rag/status` | 获取状态 |
| `POST /api/rag/model/load` | 加载模型 |

## 核心代码示例

### 1. 状态管理 (Zustand)

```typescript
// stores/chatStore.ts
import { create } from 'zustand'

interface ChatState {
  messages: Message[]
  isStreaming: boolean
  sendMessage: (content: string) => Promise<void>
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isStreaming: false,

  sendMessage: async (content) => {
    // 实现发送消息逻辑
  },
}))
```

### 2. API 服务封装

```typescript
// services/api.ts
import axios from 'axios'

class ApiService {
  private apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
  })

  async chatStream(
    request: ChatRequest,
    onChunk: (chunk: StreamChatResponse) => void
  ): Promise<void> {
    // 实现 SSE 流式请求
  }
}

export const apiService = new ApiService()
```

### 3. 路由配置

```typescript
// App.tsx
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route path="chat" element={<ChatPage />} />
          <Route path="skill-tree" element={<SkillTreePage />} />
          <Route path="knowledge-base" element={<KnowledgeBasePage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
```

## 部署说明

### 开发环境部署

```bash
npm install
npm run dev
```

### 生产环境部署

```bash
npm run build
npm run preview
```

构建产物可部署到任何静态文件服务器或 CDN。

### Docker 部署 (可选)

```dockerfile
FROM nginx:alpine
COPY dist/ /usr/share/nginx/html/
EXPOSE 80
```

## 扩展阅读

- [架构设计文档创建计划](../.trae/documents/架构设计文档创建计划.md) - 详细的架构设计规划
- [前端现代化重构-两人协作开发计划](../前端现代化重构-两人协作开发计划.md) - 项目重构计划

## License

MIT License
