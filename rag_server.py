"""
RAG API 服务器启动入口
独立启动 FastAPI 微服务，提供 RAG 问答引擎 API

启动方式：python rag_server.py
API 文档：http://localhost:8001/docs
"""

import yaml
import uvicorn
from src.rag_api.app import create_app

config_path = "./config/config.yaml"
with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

server_config = config.get("server", {})
rag_port = server_config.get("rag_port", 8001)
host = server_config.get("host", "127.0.0.1")

app = create_app()

if __name__ == "__main__":
    print("Starting RAG API server...")
    print(f"RAG API: http://localhost:{rag_port}")
    print(f"API docs: http://localhost:{rag_port}/docs")
    uvicorn.run(
        "rag_server:app",
        host=host,
        port=rag_port,
        reload=False,
    )
