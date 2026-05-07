"""
统一API服务器启动入口
整合 RAG问答引擎、技能树管理、多模态文档处理 为单一FastAPI服务

启动方式：python rag_server.py
API 文档：http://localhost:8000/docs
默认端口：8000

可通过 config/config.yaml 配置服务参数
"""

import yaml
import uvicorn
from src.rag_api.app import create_app

config_path = "./config/config.yaml"
with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

server_config = config.get("server", {})
port = server_config.get("api_port", 8000)
host = server_config.get("host", "127.0.0.1")

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
