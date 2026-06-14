# Skill Tree 模块

> 版本：1.0.0
> 最后更新：2026-05-09

## 概述

技能树模块，提供学习路径规划和技能管理功能。

## 目录结构

```
src/skill_tree/
├── api/
│   └── routes.py          # API 路由
├── application/
│   └── services.py        # 应用服务
├── domain/
│   ├── models.py          # 领域模型
│   └── services.py        # 领域服务
├── infrastructure/
│   └── repositories.py    # 仓储实现
└── __init__.py
```

## 核心组件

### SkillTreeApplicationService

技能树应用服务。

```python
from src.skill_tree.application.services import SkillTreeApplicationService
from src.skill_tree.infrastructure.repositories import FileSkillTreeRepository

repo = FileSkillTreeRepository()
service = SkillTreeApplicationService(repo)

result = service.create_skill_tree("Python 学习", "Python 编程入门")
```

### FileSkillTreeRepository

基于文件的技能树仓储。

```python
from src.skill_tree.infrastructure.repositories import FileSkillTreeRepository

repo = FileSkillTreeRepository(data_dir="./data/skill_tree")
trees = repo.find_all()
```

## API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/skill-tree/` | 获取所有技能树 |
| POST | `/api/skill-tree/` | 创建技能树 |
| GET | `/api/skill-tree/{id}` | 获取技能树详情 |
| DELETE | `/api/skill-tree/{id}` | 删除技能树 |
| POST | `/api/skill-tree/{id}/skills` | 添加技能 |
| POST | `/api/skill-tree/{id}/skills/relation` | 建立技能关系 |
| POST | `/api/skill-tree/{id}/skills/{skill_id}/resources` | 添加学习资源 |
| PUT | `/api/skill-tree/{id}/skills/{skill_id}/completion` | 更新完成率 |
| POST | `/api/skill-tree/{id}/paths/generate` | 生成学习路径 |

## API 响应格式

所有 API 端点统一返回以下格式：

```json
{
    "success": true,
    "data": { ... },
    "message": "操作成功"
}
```

## 使用示例

### 1. 创建技能树

```bash
curl -X POST http://localhost:8000/api/skill-tree/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Python 学习", "description": "Python 编程入门路径"}'
```

### 2. 添加技能

```bash
curl -X POST http://localhost:8000/api/skill-tree/{id}/skills \
  -H "Content-Type: application/json" \
  -d '{"name": "基础语法", "description": "学习 Python 基础语法", "level": "beginner", "skill_type": "knowledge"}'
```

## 数据存储

技能树数据存储在 `./data/skill_tree/` 目录下的 JSON 文件中。

## 依赖

```bash
pip install pydantic
```
