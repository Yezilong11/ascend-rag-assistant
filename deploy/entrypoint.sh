#!/bin/bash
set -e

mkdir -p /app/data /app/skill_tree_data /app/chroma_db /app/models /var/log/supervisor

if [ -n "$CORS_ORIGINS" ]; then
    export CORS_ORIGINS="$CORS_ORIGINS"
fi

echo "========================================"
echo " Ascend RAG Assistant - Starting"
echo "========================================"
echo " API Port:    ${API_PORT:-8000}"
echo " RSS Port:    ${RSS_PORT:-8081}"
echo " CORS Origins: ${CORS_ORIGINS:-default}"
echo "========================================"

exec /usr/bin/supervisord -c /etc/supervisor/conf.d/ascend-rag.conf
