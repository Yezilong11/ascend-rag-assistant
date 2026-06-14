# RSS Gateway 模块

> 版本：1.0.0
> 最后更新：2026-05-09

## 概述

RSS 网关模块，作为 Python 后端和 Go RSS 爬虫服务之间的桥梁。

## 目录结构

```
src/rss_gateway/
├── client.py             # RSS 服务客户端
├── bridge.py            # 知识库桥接器
├── ai_service.py       # AI 服务
├── ai_cache.py         # AI 响应缓存
├── models.py           # 数据模型
├── routes.py           # API 路由
└── __init__.py
```

## 核心组件

### RSSClient

RSS 服务 HTTP 客户端。

```python
from src.rss_gateway import RSSClient

client = RSSClient(base_url="http://localhost:8081")
status = await client.health_check()
```

### RSSBridge

RSS 文章到知识库的桥接器。

```python
from src.rss_gateway.bridge import RSSBridge

bridge = RSSBridge(rss_client, knowledge_base)
articles = await bridge.fetch_and_ingest_articles(feed_id)
```

### AIResponseCache

AI 响应缓存，减少重复调用。

```python
from src.rss_gateway.ai_cache import AIResponseCache

cache = AIResponseCache()
cached = cache.get(key)
```

## API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/rss/health` | 健康检查 |
| GET | `/api/rss/feeds` | 获取订阅源列表 |
| POST | `/api/rss/feeds` | 添加订阅源 |
| DELETE | `/api/rss/feeds/{id}` | 删除订阅源 |
| GET | `/api/rss/feeds/{id}/articles` | 获取文章列表 |
| POST | `/api/rss/feeds/{id}/ingest` | 导入文章到知识库 |

## API 响应格式

```json
{
    "success": true,
    "data": { ... },
    "message": "操作成功"
}
```

## 依赖 Go 服务

RSS Gateway 需要 Go RSS 服务运行在 `http://localhost:8081`。

启动 Go 服务：

```bash
cd services/rss-crawler
go run cmd/server/main.go
```

## 配置

从 `config/config.yaml` 读取 RSS 服务地址：

```yaml
server:
  rss:
    host: "0.0.0.0"
    port: 8081
    service_url: "http://localhost:8081"
```

## 依赖

```bash
pip install httpx pyyaml
```
