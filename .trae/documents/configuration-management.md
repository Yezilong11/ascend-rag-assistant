# 配置文件管理文档

## 概述

本文档记录项目中配置文件的结构和管理规范（Phase 1-A 重构）。

## 配置文件结构

```
ascend-rag-assistant/
├── config/
│   └── config.yaml           # 主配置文件（Python + 共享配置）
├── services/
│   └── rss-crawler/
│       └── config.yaml       # RSS服务专用配置（Go）
├── frontend/
│   ├── .env                  # 前端环境变量（本地开发）
│   └── .env.example          # 前端环境变量模板
└── rag_server.py             # Python服务入口
```

## 配置说明

### 1. 主配置文件 (config/config.yaml)

统一管理整个系统的核心配置：

```yaml
# 系统配置
system:
  name: "昇腾AI竞赛智能助教"
  version: "1.0.0"

# 知识库配置
knowledge_base:
  main:           # 主知识库（文本文档）
  multimodal:     # 多模态知识库（图片）

# 大模型配置
llm:
  model_id: "Qwen/Qwen2-1.5B-Instruct"
  device: "auto"

# 服务配置
server:
  api:            # Python FastAPI服务
  rss:            # Go RSS服务
  frontend:       # 前端服务

# RSS功能配置
rss:
  enabled: true
  ai:
    enabled: true
```

### 2. RSS服务配置 (services/rss-crawler/config.yaml)

Go RSS微服务专用配置，保持独立：

```yaml
server:
  host: "0.0.0.0"
  port: 8081

database:
  path: "./data/rss.db"

crawler:
  concurrent: 3
  timeout: 30
```

### 3. 前端环境变量 (frontend/.env)

前端连接后端的配置：

```bash
VITE_API_BASE_URL=http://localhost:8000
```

## 配置读取优先级

### Python服务

1. 环境变量（如 `API_PORT`）
2. `config/config.yaml` 配置文件
3. 代码默认值

### 前端

1. `.env` 文件（Vite 自动加载）
2. 环境变量

## 迁移记录

### v1.1.0 (Phase 1-A)

**变更内容**：
- 重构 `config/config.yaml` 结构，添加 `knowledge_base.main` 和 `knowledge_base.multimodal` 分组
- 服务配置重组为 `server.api`, `server.rss`, `server.frontend` 结构
- RSS服务地址从硬编码改为从配置文件读取

**修改文件**：
- `config/config.yaml` - 主配置重组
- `rag_server.py` - 适配新配置路径
- `src/rss_gateway/client.py` - 从配置文件读取RSS地址
- `frontend/.env` - 创建前端环境配置文件
- `frontend/.env.example` - 创建环境变量模板

**向后兼容**：
- `src/rss_gateway/client.py` 保留了默认值 `http://localhost:8081`
- 如果配置文件读取失败，自动使用默认值

## 使用指南

### 修改API服务端口

编辑 `config/config.yaml`:
```yaml
server:
  api:
    port: 9000  # 修改为新端口
```

### 修改RSS服务地址

编辑 `config/config.yaml`:
```yaml
server:
  rss:
    service_url: "http://your-server:8081"
```

### 前端连接不同后端

创建/修改 `frontend/.env`:
```bash
VITE_API_BASE_URL=http://your-backend:8000
```

## 注意事项

1. **Go RSS服务配置独立**：Go服务使用 `services/rss-crawler/config.yaml`，不受主配置影响
2. **环境变量优先级最高**：可通过环境变量覆盖配置文件中的任何值
3. **修改后需重启服务**：配置变更需要重启对应的服务才能生效
