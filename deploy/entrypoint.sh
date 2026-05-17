#!/bin/bash
set -e

mkdir -p /app/data /app/skill_tree_data /var/log/supervisor

if [ -n "$CORS_ORIGINS" ]; then
    export CORS_ORIGINS="$CORS_ORIGINS"
fi

exec /usr/bin/supervisord -c /etc/supervisor/conf.d/ascend-rag.conf
