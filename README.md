# Ascend RAG Assistant

<div align="center">

🚀 **基于昇腾AI平台的RAG智能竞赛助手**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg)](https://fastapi.tiangolo.com/)
[![Ant Design](https://img.shields.io/badge/Ant%20Design-6-1890FF.svg)](https://ant.design/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-1.5.0-purple.svg)](https://trychroma.com/)
[![Go](https://img.shields.io/badge/Go-1.20+-00ADD8.svg)](https://golang.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)

</div>

## 📖 项目简介

**Ascend RAG Assistant** 是一个基于检索增强生成（RAG）技术的AI竞赛智能助手系统，专为昇腾AI生态打造。系统能够基于竞赛官方文档、报名须知、规则说明等资料，为参赛选手提供24/7全天候的智能问答服务。

### ✨ 核心特性

- 🧠 **基于RAG的知识问答** - 结合私域知识库与大语言模型，提供准确可靠的回答
- ⚡ **昇腾NPU原生优化** - 原生支持华为昇腾910B NPU
- 🎯 **可切换模型** - 侧边栏自由切换不同大小的模型
- ✨ **流式输出** - 打字机逐字显示效果，大幅改善等待体验
- 🖥️ **现代化前端界面** - 基于React 19 + Ant Design 6构建
- 📚 **多格式文档支持** - 支持PDF、TXT、Markdown等多种文档格式的导入
- 🏠 **完全本地部署** - 支持全流程本地运行，保护数据隐私
- 🔄 **易于扩展** - 模块化设计，方便添加新的数据源和模型
- 📡 **RSS资讯订阅** - 集成RSS抓取模块，自动获取竞赛相关资讯并导入知识库
- 🐳 **Docker容器化** - 一键部署，开箱即用

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    React 前端 (localhost:3000)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  智能问答    │  │  技能树      │  │   RSS 资讯订阅   │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
           │                  │                    │
           ▼                  ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                 FastAPI 网关 (localhost:8000)                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ RAG API    │  │ 技能树 API  │  │  RSS 代理网关      │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
           │                  │                    │
           ▼                  ▼                    ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  ChromaDB        │  │ JSON 文件存储    │  │  Go RSS 微服务   │
│  (向量知识库)    │  │ (技能树数据)    │  │  (localhost:8081)│
└──────────────────┘  └──────────────────┘  └──────────────────┘
                                                       │
                                              ┌────────┴────────┐
                                              │ SQLite           │
                                              │ (RSS 数据)       │
                                              └──────────────────┘
```

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Go 1.20+
- Node.js 18+
- PyTorch 2.0+
- Docker & Docker Compose
- (可选) 华为昇腾NPU + CANN工具链

### 方式一：Docker 部署（推荐）

使用 Docker 一键部署，自动完成前端构建和服务编排。

**1. 克隆项目**
```bash
git clone https://github.com/your-username/ascend-rag-assistant.git
cd ascend-rag-assistant
```

**2. 下载模型**

```bash
pip install modelscope

# 创建模型目录
mkdir -p models

# 下载 BGE 嵌入模型
modelscope download --model BAAI/bge-large-zh-v1.5 --local_dir ./models/bge-large-zh-v1.5

# 下载 Qwen2 大语言模型
modelscope download --model qwen/Qwen2-1.5B-Instruct --local_dir ./models/Qwen2-1.5B-Instruct
```

**3. 启动服务**

```bash
# 构建并启动
docker compose up -d --build

# 查看日志
docker compose logs -f

# 停止服务
docker compose down
```

**4. 访问应用**

- 前端界面：`http://localhost:8080`
- API 文档：`http://localhost:8080/docs`

**自定义配置**

```bash
# 修改端口
HOST_PORT=3000 docker compose up -d

# 配置 CORS 允许的域名
CORS_ORIGINS="http://example.com,http://another.com" docker compose up -d
```

**数据持久化**

Docker 部署会自动挂载以下目录：
- `models/` - AI模型文件
- `data/` - 上传文件和数据
- `skill_tree_data/` - 技能树数据
- `chroma_db/` - 向量数据库

### 方式二：本地开发部署

**1. 克隆项目**
```bash
git clone https://github.com/your-username/ascend-rag-assistant.git
cd ascend-rag-assistant
```

**2. 创建Python虚拟环境**
```bash
conda create -n ascend-rag python=3.10
conda activate ascend-rag
```

**3. 安装Python依赖**
```bash
pip install -r requirements.txt
```

**4. 安装前端依赖**
```bash
cd frontend
npm install
cd ..
```

**5. 下载模型**

```bash
pip install modelscope

# 下载 BGE 嵌入模型
modelscope download --model BAAI/bge-large-zh-v1.5 --local_dir ./models/bge-large-zh-v1.5

# 下载 Qwen2 大语言模型
modelscope download --model qwen/Qwen2-1.5B-Instruct --local_dir ./models/Qwen2-1.5B-Instruct
```

**6. 一键启动**

项目需要同时启动三个服务：Go RSS 服务、FastAPI 后端、React 前端。

**方式一：一键启动（Windows）**
```bash
start.bat
```

**方式二：手动启动（需要三个终端窗口）**

终端1 - 启动 Go RSS 服务：
```bash
cd services/rss-crawler
go run cmd/server/main.go
```

终端2 - 启动 FastAPI 服务器：
```bash
python server.py
```

终端3 - 启动 React 前端：
```bash
cd frontend
npm run dev
```

应用启动后，访问：
- 前端界面：`http://localhost:3000`
- API文档：`http://localhost:8000/docs`

## 📖 使用指南

### RAG智能问答

1. **初始化知识库** - 应用启动后会自动初始化向量数据库
2. **导入竞赛资料** - 在侧边栏上传PDF/TXT/MD文件，点击「添加到知识库」
3. **启动AI引擎** - 点击「启动AI引擎」加载大模型
4. **开始问答** - 在主输入框输入问题，获取智能回答

### RSS资讯订阅

1. 点击侧边栏 **📡 RSS 资讯**
2. 在 **RSS源** 标签页添加要订阅的RSS源
3. 点击「抓取」获取最新文章
4. 浏览文章列表，点击文章查看详情
5. 点击「导入知识库」将文章内容添加到RAG知识库
6. 在智能问答中即可询问与RSS资讯相关的问题

### 竞赛技能树

1. 点击顶部标签页 **🌳 技能树**
2. **创建技能树** - 在左侧填写技能树名称和描述，点击创建
3. **添加技能** - 选择技能树后展开"➕ 添加技能"，填写技能信息
4. **建立关系** - 展开"🔗 建立技能关系"，设置前置/进阶依赖
5. **生成路径** - 点击"生成学习路径"，在"🗺️ 学习路径"查看结果
6. **浏览技能** - 在"📚 技能列表"查看所有技能节点

> 💡 **提示**：要生成学习路径，需要至少一个**根技能**（没有前置依赖的技能），从根技能开始建立关系链。

### 预置知识库

本项目已预置了近百场国内大学生竞赛的相关资料，包括：
- 报名须知
- 竞赛规则
- 评分标准
- 常见问题FAQ
- 技术文档

### 配置说明

在 `config/` 目录下可以修改系统配置：
- `config.yaml`: 模型路径、超参数、RSS服务配置等

## 🧩 模块说明

### `src/knowledge_base.py` - 知识库管理

负责文档加载、文本切分、向量化存储和检索：
- 支持多种文档格式（PDF、TXT、MD）
- 递归字符切分策略，chunk_size=500，chunk_overlap=50
- 使用 BGE-Large-ZH 中文嵌入模型
- ChromaDB 持久化存储

### `src/rag_engine.py` - RAG引擎核心

结合检索到的知识和大模型生成能力：
- 支持预定义多模型切换，默认加载 Qwen2-1.5B
- 自动从ModelScope下载模型到`./models/`文件夹
- 支持流式输出（打字机效果）
- 自定义Prompt模板
- 返回回答及参考来源
- 异常处理机制

### `src/rss_gateway/` - RSS代理网关模块

将RSS抓取服务集成到主应用：
- **client.py** - httpx异步客户端封装
- **routes.py** - FastAPI代理路由，34个端点
- **bridge.py** - 知识库桥接，将RSS文章导入ChromaDB
- **models.py** - Pydantic请求/响应模型

### `src/skill_tree/` - 竞赛技能树模块

技能树全栈模块，支持学习路径规划：
- **domain/** - 领域模型（SkillTree, SkillNode, LearningPath等）
- **application/** - 应用服务层，协调业务逻辑
- **infrastructure/** - 基础设施层，JSON文件持久化存储
- **api/** - FastAPI REST API接口

功能特性：
- 创建/删除技能树
- 添加技能节点
- 建立技能依赖关系
- 自动生成从根到叶的完整学习路径
- 计算技能难度和总学习时间

### `services/rss-crawler/` - RSS抓取微服务

独立运行的Go微服务，提供RSS订阅和抓取功能：
- RSS源管理（CRUD + 抓取调度）
- 文章存储与检索
- AI摘要生成（通过Ollama）
- WebSocket实时通知
- Meilisearch全文搜索

## ⚡ 性能优化指南

### CPU进一步优化

1. **使用更小模型** - 使用 `Qwen/Qwen2-0.5B-Instruct`，速度提升2-3倍
2. **限制生成长度** - 默认`max_new_tokens=256`，可根据需要调整
3. **关闭采样** - 设置`do_sample=False`使用贪婪搜索，速度略快但多样性减少

**性能参考（CPU/CUDA）**:
| 硬件 | 模型 | 平均生成速度 | 300字回答时间 |
|------|------|-------------|--------------|
| CPU | Qwen2-0.5B | ~8-12 tokens/s | 25-40秒 |
| CPU | Qwen2-1.5B | ~3-5 tokens/s | 60-100秒 |
| CUDA GPU | Qwen2-1.5B | ~15-20 tokens/s | 15-20秒 |

## 📊 效果展示

| 功能 | 演示 |
|------|------|
| 智能问答 | 支持竞赛报名、规则、日程等各类问题查询 |
| 来源引用 | 每个回答都标注参考来源，可追溯 |
| RSS资讯 | 自动抓取竞赛相关资讯并导入知识库 |
| 文档上传 | 支持随时添加新的竞赛资料 |

## 🛠️ 开发计划

- [x] RSS资讯订阅模块集成
- [x] Docker容器化支持
- [ ] 支持更多LLM模型（百川、灵犀等）
- [ ] Parent-document检索优化
- [ ] 支持多模态文档（图片中的文字提取）

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启一个 Pull Request

## 📄 许可证

本项目仅供学习和研究使用。

## 🙏 致谢

- [LangChain](https://www.langchain.com/) - 优秀的LLM应用框架
- [ChromaDB](https://trychroma.com/) - 开源向量数据库
- [BGE](https://github.com/FlagOpen/FlagEmbedding) - 优秀的中文嵌入模型
- [Qwen](https://github.com/QwenLM/Qwen2) - 通义千问大模型
- [ModelScope](https://modelscope.cn/) - 魔搭社区，方便的模型下载服务
- [昇腾AI](https://www.hiascend.com/) - 华为昇腾AI计算平台
- [Gin](https://github.com/gin-gonic/gin) - Go Web框架
- [React](https://react.dev/) - 用户界面库

---

<div align="center">
Made with ❤️ for the Ascend AI ecosystem
</div>
