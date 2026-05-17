FROM golang:1.20 AS go-builder
WORKDIR /build
COPY services/rss-crawler/go.mod services/rss-crawler/go.sum ./
RUN go mod download
COPY services/rss-crawler/ .
RUN CGO_ENABLED=1 go build -o rss-server ./cmd/server/main.go

FROM python:3.11-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx supervisor sqlite3 libsqlite3-0 gcc && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --from=go-builder /build/rss-server /app/rss-server
COPY services/rss-crawler/config.yaml /app/config.yaml
COPY services/rss-crawler/feeds/ /app/feeds/

COPY frontend/dist /var/www/ascend-rag/dist

COPY src/ /app/src/
COPY config/ /app/config/
COPY rag_server.py /app/
COPY skill_tree_data/ /app/skill_tree_data/
COPY data/ /app/data/

COPY models/ /app/models/

COPY deploy/nginx/ascend-rag.conf /etc/nginx/sites-available/ascend-rag
RUN ln -sf /etc/nginx/sites-available/ascend-rag /etc/nginx/sites-enabled/ascend-rag && \
    rm -f /etc/nginx/sites-enabled/default

COPY deploy/supervisord.conf /etc/supervisor/conf.d/ascend-rag.conf

COPY deploy/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh /app/rss-server

ENV CORS_ORIGINS="" \
    API_PORT=8000 \
    RSS_PORT=8081 \
    KMP_DUPLICATE_LIB_OK=TRUE

EXPOSE 80

CMD ["/app/entrypoint.sh"]
