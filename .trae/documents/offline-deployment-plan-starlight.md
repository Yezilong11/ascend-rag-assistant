# 后端离线部署计划（星光平台容器云）

## 前提条件

| 条件 | 说明 |
|------|------|
| 部署平台 | 星光平台 https://starlight.nscc-gz.cn/ 容器云服务 |
| 网络环境 | **完全离线**，服务器无法访问外网 |
| 部署方式 | 本地构建 Docker 镜像 → 推送至星光平台镜像仓库 → 创建容器云服务 |
| 镜像架构 | 单镜像包含 Nginx + FastAPI + RSS Go + React 前端静态文件 |
| 配置方式 | 通过环境变量传入，不硬编码 |

## 整体架构

```
容器内部（单镜像）:
  supervisord (PID 1, 进程管理)
    ├── Nginx (:80)          → 前端静态文件 + 反向代理
    ├── FastAPI (:8000)      → /api/rag, /api/skill-tree, /api/multimodal, /api/rss
    └── RSS Go (:8081)       → RSS 爬虫服务

外部访问:
  浏览器 → 星光平台域名:80 → Nginx → / 或 /api/*
```

---

## 步骤1：本地准备离线依赖包

在本地联网电脑上执行，所有依赖提前下载。

### 1.1 下载 Python 离线包

```bash
# 在本地联网环境执行
mkdir -p offline_packages/python
pip download -r requirements.txt -d offline_packages/python
```

> 注意：torch 等包体积巨大（~2GB），需根据目标平台 CPU/GPU 选择对应 wheel。
> 如果目标服务器有 GPU，需下载对应 CUDA 版本的 torch；如果只有 CPU，下载 CPU 版本。

### 1.2 下载 Node.js 离线包

```bash
# 前端构建在本地完成，不需要在容器内 npm install
# 只需在本地执行 npm run build 生成 dist/
cd frontend
npm install
npm run build
# 产物: frontend/dist/
```

### 1.3 编译 Go RSS 服务

```bash
# 在本地编译 Linux amd64 二进制（交叉编译）
cd services/rss-crawler
set GOOS=linux
set GOARCH=amd64
set CGO_ENABLED=1
go build -o rss-server ./cmd/server/main.go
# 产物: services/rss-crawler/rss-server
```

> 注意：`mattn/go-sqlite3` 需要 CGO，Windows 交叉编译 Linux 需要安装 `x86_64-linux-gnu-gcc`。
> 替代方案：在 Docker 多阶段构建中编译 Go 二进制（步骤2中处理）。

---

## 步骤2：创建 Dockerfile（多阶段构建）

**文件**: `Dockerfile`（项目根目录，新建）

### 构建策略

采用**多阶段构建**，分为 4 个阶段：

| 阶段 | 基础镜像 | 产出 | 说明 |
|------|---------|------|------|
| stage1: go-builder | golang:1.20 | rss-server 二进制 | 编译 Go 服务 |
| stage2: node-builder | node:20-alpine | frontend/dist/ | 构建前端 |
| stage3: python-base | python:3.11-slim | Python 运行环境 | 安装 Python 依赖 |
| stage4: runtime | python:3.11-slim | 最终镜像 | 合并所有产物 |

### Dockerfile 内容要点

```dockerfile
# ====== Stage 1: 编译 Go RSS 服务 ======
FROM golang:1.20 AS go-builder
WORKDIR /build
COPY services/rss-crawler/go.mod services/rss-crawler/go.sum ./
RUN go mod download
COPY services/rss-crawler/ .
RUN CGO_ENABLED=1 go build -o rss-server ./cmd/server/main.go

# ====== Stage 2: 构建前端 ======
FROM node:20-alpine AS node-builder
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# ====== Stage 3: Python 依赖 ======
FROM python:3.11-slim AS python-base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ====== Stage 4: 运行时镜像 ======
FROM python:3.11-slim AS runtime

# 安装 Nginx + supervisord + sqlite3
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx supervisor sqlite3 libsqlite3-0 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python 依赖（从 stage3 复制）
COPY --from=python-base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=python-base /usr/local/bin /usr/local/bin

# Go 二进制（从 stage1 复制）
COPY --from=go-builder /build/rss-server /app/rss-server

# 前端静态文件（从 stage2 复制）
COPY --from=node-builder /build/dist /var/www/ascend-rag/dist

# 项目源码
COPY src/ /app/src/
COPY config/ /app/config/
COPY rag_server.py /app/
COPY skill_tree_data/ /app/skill_tree_data/
COPY data/ /app/data/

# 模型文件（需提前下载到本地 models/ 目录）
COPY models/ /app/models/

# Nginx 配置
COPY deploy/nginx/ascend-rag.conf /etc/nginx/sites-available/ascend-rag
RUN ln -sf /etc/nginx/sites-available/ascend-rag /etc/nginx/sites-enabled/ascend-rag && \
    rm -f /etc/nginx/sites-enabled/default

# Supervisord 配置
COPY deploy/supervisord.conf /etc/supervisor/conf.d/ascend-rag.conf

# 启动脚本
COPY deploy/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh /app/rss-server

# 环境变量默认值
ENV CORS_ORIGINS="" \
    API_PORT=8000 \
    RSS_PORT=8081 \
    KMP_DUPLICATE_LIB_OK=TRUE

EXPOSE 80

CMD ["/app/entrypoint.sh"]
```

---

## 步骤3：创建 .dockerignore

**文件**: `.dockerignore`（项目根目录，新建）

排除不需要的文件，减小构建上下文体积：

```
.git
.trae
node_modules
frontend/node_modules
__pycache__
*.pyc
.pytest_cache
chroma_db
chroma_db_multimodal
*.db
dist
*.egg-info
```

---

## 步骤4：创建 Nginx 配置

**文件**: `deploy/nginx/ascend-rag.conf`（新建）

```nginx
server {
    listen 80;
    server_name _;

    # 前端静态文件
    location / {
        root /var/www/ascend-rag/dist;
        index index.html;
        try_files $uri $uri/ /index.html;

        # 静态资源缓存
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 30d;
            add_header Cache-Control "public, immutable";
        }
    }

    # 后端 API 反向代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 文件上传大小限制
        client_max_body_size 100M;

        # 超时设置
        proxy_connect_timeout 300s;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }

    # API 文档
    location /docs {
        proxy_pass http://127.0.0.1:8000;
    }

    location /openapi.json {
        proxy_pass http://127.0.0.1:8000;
    }

    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript;
    gzip_min_length 1000;

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

---

## 步骤5：创建 Supervisord 配置

**文件**: `deploy/supervisord.conf`（新建）

```ini
[supervisord]
nodaemon=true
logfile=/var/log/supervisor/supervisord.log
pidfile=/var/run/supervisord.pid

[program:nginx]
command=/usr/sbin/nginx -g "daemon off;"
autostart=true
autorestart=true
stdout_logfile=/var/log/supervisor/nginx.log
stderr_logfile=/var/log/supervisor/nginx-error.log

[program:fastapi]
command=/usr/local/bin/uvicorn rag_server:app --host 127.0.0.1 --port 8000
directory=/app
autostart=true
autorestart=true
stdout_logfile=/var/log/supervisor/fastapi.log
stderr_logfile=/var/log/supervisor/fastapi-error.log
environment=KMP_DUPLICATE_LIB_OK="TRUE"

[program:rss-go]
command=/app/rss-server
directory=/app
autostart=true
autorestart=true
stdout_logfile=/var/log/supervisor/rss-go.log
stderr_logfile=/var/log/supervisor/rss-go-error.log
```

---

## 步骤6：创建启动脚本

**文件**: `deploy/entrypoint.sh`（新建）

```bash
#!/bin/bash
set -e

# 创建必要目录
mkdir -p /app/data /app/skill_tree_data /var/log/supervisor

# 如果环境变量传入了 CORS_ORIGINS，写入配置
if [ -n "$CORS_ORIGINS" ]; then
    export CORS_ORIGINS="$CORS_ORIGINS"
fi

# 启动 supervisord（管理 nginx + fastapi + rss-go）
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/ascend-rag.conf
```

---

## 步骤7：修改 CORS 配置支持环境变量

**文件**: `src/rag_api/app.py`（修改）

将 `CORS_ORIGINS` 从硬编码改为环境变量读取：

```python
import os

def _get_cors_origins():
    env_origins = os.environ.get("CORS_ORIGINS", "")
    if env_origins:
        return [origin.strip() for origin in env_origins.split(",") if origin.strip()]
    return [
        "http://localhost:5173",
        "http://localhost:8501",
        "http://localhost:3000",
    ]

CORS_ORIGINS = _get_cors_origins()
```

**文件**: `server.py`（修改）

同样将 CORS 配置改为环境变量读取，逻辑与 `app.py` 一致。

---

## 步骤8：修改 rag_server.py 支持环境变量

**文件**: `rag_server.py`（修改）

支持通过环境变量覆盖端口和 host：

```python
import os

port = int(os.environ.get("API_PORT", server_config.get("api_port", 8000)))
host = os.environ.get("API_HOST", server_config.get("host", "127.0.0.1"))
```

---

## 步骤9：本地构建 Docker 镜像

在本地联网电脑上执行：

```bash
# 1. 确保模型文件已下载到 models/ 目录
#    - models/Qwen2-1.5B-Instruct/
#    - models/bge-large-zh-v1.5/

# 2. 构建 Docker 镜像
docker build -t ascend-rag:latest .

# 3. 本地测试镜像
docker run -d -p 80:80 \
    -e CORS_ORIGINS="http://your-domain.com" \
    --name ascend-rag-test \
    ascend-rag:latest

# 4. 验证
#    浏览器访问 http://localhost
#    API 文档 http://localhost/docs
#    健康检查 http://localhost/api/skill-tree

# 5. 测试完成后停止
docker stop ascend-rag-test
docker rm ascend-rag-test
```

---

## 步骤10：推送镜像到星光平台

```bash
# 1. 登录星光平台镜像仓库
docker login registry.starlight.nscc-gz.cn

# 2. 给镜像打标签
docker tag ascend-rag:latest registry.starlight.nscc-gz.cn/<你的命名空间>/ascend-rag:latest

# 3. 推送镜像
docker push registry.starlight.nscc-gz.cn/<你的命名空间>/ascend-rag:latest
```

---

## 步骤11：在星光平台创建容器云服务

1. 登录 https://starlight.nscc-gz.cn/
2. 进入「容器云服务」→「创建应用」
3. 选择镜像：`registry.starlight.nscc-gz.cn/<命名空间>/ascend-rag:latest`
4. 配置容器：
   - 端口映射：容器 80 → 外部 80
   - 环境变量：
     - `CORS_ORIGINS` = `http://你的域名,http://你的IP`
     - `API_PORT` = `8000`
     - `RSS_PORT` = `8081`
   - 持久化存储（如需）：
     - `/app/skill_tree_data` → 挂载持久卷
     - `/app/data` → 挂载持久卷
     - `/app/chroma_db` → 挂载持久卷
5. 资源配置：
   - CPU: 建议 4 核+
   - 内存: 建议 16GB+（模型加载需要）
   - GPU: 如有 NPU/GPU 资源，配置对应设备
6. 创建并启动服务

---

## 步骤12：域名配置

1. 在星光平台获取容器服务的外部访问地址（IP 或平台分配的域名）
2. 如需自定义域名：
   - 在域名服务商处添加 A 记录指向星光平台 IP
   - 或使用星光平台提供的域名
3. 更新环境变量 `CORS_ORIGINS` 为实际域名
4. 重启容器使配置生效

---

## 步骤13：部署验证

| 检查项 | 验证方式 | 预期结果 |
|--------|---------|---------|
| 前端页面 | 浏览器访问域名 | React 页面正常加载 |
| 技能树列表 | 点击技能树 | 列表正常显示 |
| 技能树详情 | 进入详情页 | 可视化图正常渲染 |
| RAG 问答 | 提交问题 | 返回回答 |
| RSS 功能 | 访问 RSS 相关页面 | 数据正常加载 |
| 完成率 | 拖动滑块 | 数值更新，进度条变化 |
| API 文档 | 访问 /docs | Swagger UI 正常显示 |

---

## 涉及文件清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `Dockerfile` | 新建 | 多阶段构建 Docker 镜像 |
| `.dockerignore` | 新建 | 排除不需要的文件 |
| `deploy/nginx/ascend-rag.conf` | 新建 | Nginx 反向代理配置 |
| `deploy/supervisord.conf` | 新建 | 进程管理配置 |
| `deploy/entrypoint.sh` | 新建 | 容器启动脚本 |
| `src/rag_api/app.py` | 修改 | CORS 支持环境变量 |
| `server.py` | 修改 | CORS 支持环境变量 |
| `rag_server.py` | 修改 | 端口/host 支持环境变量 |

## 关键注意事项

1. **模型文件体积**：`models/` 目录约 3-5GB，Docker 构建时需确保本地已下载
2. **Go 交叉编译**：`mattn/go-sqlite3` 需要 CGO，建议在 Docker 多阶段构建中编译而非本地交叉编译
3. **Python 依赖体积**：torch 等包约 2GB，最终镜像约 8-12GB
4. **GPU 支持**：如需 GPU 推理，需使用 NVIDIA/CANN 基础镜像替代 python:3.11-slim
5. **数据持久化**：`skill_tree_data/`、`chroma_db/`、`data/` 建议挂载持久卷，避免容器重建时数据丢失
6. **星光平台镜像仓库**：需提前在平台注册账号并创建命名空间
