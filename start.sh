#!/bin/bash

echo "========================================"
echo "    Ascend RAG Assistant 一键启动"
echo "========================================"
echo ""

# 设置环境变量解决OMP冲突
export KMP_DUPLICATE_LIB_OK=TRUE

# 启动Go RSS服务
echo "启动Go RSS服务..."
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$SCRIPT_DIR/services/rss-crawler/server" ]; then
    (cd "$SCRIPT_DIR/services/rss-crawler" && ./server) &
else
    (cd "$SCRIPT_DIR/services/rss-crawler" && go run cmd/server/main.go) &
fi
RSS_PID=$!
echo "Go RSS服务 PID: $RSS_PID"
echo ""

# 启动API服务器
echo "启动API服务器..."
python server.py &
API_PID=$!

echo "等待API服务器启动..."
sleep 3

echo ""
echo "启动前端开发服务器..."
echo ""

(cd "$SCRIPT_DIR/frontend" && npm run dev) &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo "    所有服务已启动"
echo "    - Go RSS服务: http://localhost:8081"
echo "    - FastAPI服务: http://localhost:8000"
echo "    - 前端开发服务器: http://localhost:3000"
echo "========================================"

# 等待任意子进程退出
wait

# 退出时清理
kill $RSS_PID $API_PID $FRONTEND_PID 2>/dev/null
