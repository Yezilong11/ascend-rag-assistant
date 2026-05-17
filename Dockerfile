FROM golang:1.20 AS go-builder
WORKDIR /build
ENV GOPROXY=https://goproxy.cn,direct
COPY services/rss-crawler/go.mod services/rss-crawler/go.sum ./
RUN go mod download
COPY services/rss-crawler/ .
RUN CGO_ENABLED=1 go build -o rss-server ./cmd/server/main.go

FROM node:20-slim AS frontend-builder
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install --registry=https://registry.npmmirror.com
COPY frontend/ .
RUN npm run build

FROM python:3.11-slim AS runtime

RUN sed -i 's|http://deb.debian.org|http://mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources && \
    sed -i 's|http://security.debian.org|http://mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && apt-get install -y --no-install-recommends \
    nginx supervisor sqlite3 libsqlite3-0 gcc curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --trusted-host pypi.tuna.tsinghua.edu.cn

COPY --from=go-builder /build/rss-server /app/rss-server
COPY services/rss-crawler/config.yaml /app/rss-config.yaml
COPY services/rss-crawler/feeds/ /app/feeds/

COPY --from=frontend-builder /build/dist /var/www/ascend-rag/dist

COPY src/ /app/src/
COPY config/ /app/config/
COPY rag_server.py /app/

COPY deploy/nginx/ascend-rag.conf /etc/nginx/sites-available/ascend-rag
RUN ln -sf /etc/nginx/sites-available/ascend-rag /etc/nginx/sites-enabled/ascend-rag && \
    rm -f /etc/nginx/sites-enabled/default

COPY deploy/supervisord.conf /etc/supervisor/conf.d/ascend-rag.conf

COPY deploy/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh /app/rss-server

RUN mkdir -p /app/data /app/skill_tree_data /app/chroma_db /app/models

ENV CORS_ORIGINS="" \
    API_PORT=8000 \
    RSS_PORT=8081 \
    KMP_DUPLICATE_LIB_OK=TRUE

EXPOSE 80

VOLUME ["/app/models", "/app/data", "/app/skill_tree_data", "/app/chroma_db"]

CMD ["/app/entrypoint.sh"]
