"""
统一API服务器启动入口
整合 RAG问答引擎、技能树管理、多模态文档处理 为单一FastAPI服务

启动方式：python rag_server.py
API 文档：http://localhost:8000/docs
默认端口：8000

可通过 config/config.yaml 配置服务参数

配置更新说明 (Phase 1-A):
- 服务配置已重组为 server.api, server.rss, server.frontend 结构
- 原 api_port, rag_port, web_port 已合并
"""

import os

import yaml
import uvicorn
from src.rag_api.app import create_app

config_path = "./config/config.yaml"
with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# 读取API服务配置
server_config = config.get("server", {})
api_config = server_config.get("api", {})
port = int(os.environ.get("API_PORT", api_config.get("port", 8000)))
host = os.environ.get("API_HOST", api_config.get("host", "127.0.0.1"))

app = create_app(include_skill_tree=True, include_multimodal=True)

if __name__ == "__main__":
    print("=" * 50)
    print("竞赛智能助手 - 统一API服务")
    print("=" * 50)
    print(f"服务地址: http://localhost:{port}")
    print(f"API文档: http://localhost:{port}/docs")
    print("-" * 50)
    print("可用服务:")
    print(f"  - RAG问答: /api/rag")
    print(f"  - 技能树: /api/skill-tree")
    print(f"  - 多模态: /api/multimodal")
    print("=" * 50)
    uvicorn.run(
        "rag_server:app",
        host=host,
        port=port,
        reload=False,
    )
