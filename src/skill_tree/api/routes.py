from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from pydantic import BaseModel
from src.skill_tree.application.services import SkillTreeApplicationService
from src.skill_tree.infrastructure.repositories import FileSkillTreeRepository

# 创建路由器
router = APIRouter(prefix="/api/skill-tree", tags=["skill-tree"])

# 依赖注入
async def get_skill_tree_service() -> SkillTreeApplicationService:
    repository = FileSkillTreeRepository()
    return SkillTreeApplicationService(repository)


# 请求模型
class CreateSkillTreeRequest(BaseModel):
    name: str
    description: str


@router.post("/", response_model=Dict[str, Any])
async def create_skill_tree(
    request: CreateSkillTreeRequest,
    service: SkillTreeApplicationService = Depends(get_skill_tree_service)
):
    """创建技能树"""
    result = service.create_skill_tree(request.name, request.description)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.get("/", response_model=Dict[str, Any])
async def list_skill_trees(
    service: SkillTreeApplicationService = Depends(get_skill_tree_service)
):
    """列出所有技能树"""
    return service.list_skill_trees()


@router.get("/{skill_tree_id}", response_model=Dict[str, Any])
async def get_skill_tree(
    skill_tree_id: str,
    service: SkillTreeApplicationService = Depends(get_skill_tree_service)
):
    """获取技能树详情"""
    result = service.get_skill_tree(skill_tree_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    return result


@router.delete("/{skill_tree_id}", response_model=Dict[str, Any])
async def delete_skill_tree(
    skill_tree_id: str,
    service: SkillTreeApplicationService = Depends(get_skill_tree_service)
):
    """删除技能树"""
    result = service.delete_skill_tree(skill_tree_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


# 请求模型
class AddSkillRequest(BaseModel):
    name: str
    description: str
    level: str
    skill_type: str
    learning_time: int = 0


@router.post("/{skill_tree_id}/skills", response_model=Dict[str, Any])
async def add_skill(
    skill_tree_id: str,
    request: AddSkillRequest,
    service: SkillTreeApplicationService = Depends(get_skill_tree_service)
):
    """添加技能"""
    result = service.add_skill(
        skill_tree_id, request.name, request.description, request.level, request.skill_type, request.learning_time
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


# 请求模型
class EstablishRelationRequest(BaseModel):
    source_skill_id: str
    target_skill_id: str
    relation_type: str


@router.post("/{skill_tree_id}/skills/relation", response_model=Dict[str, Any])
async def establish_skill_relation(
    skill_tree_id: str,
    request: EstablishRelationRequest,
    service: SkillTreeApplicationService = Depends(get_skill_tree_service)
):
    """建立技能关系"""
    result = service.establish_skill_relation(
        skill_tree_id, request.source_skill_id, request.target_skill_id, request.relation_type
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.post("/{skill_tree_id}/skills/{skill_id}/resources", response_model=Dict[str, Any])
async def add_learning_resource(
    skill_tree_id: str,
    skill_id: str,
    resource: Dict[str, Any],
    service: SkillTreeApplicationService = Depends(get_skill_tree_service)
):
    """添加学习资源"""
    result = service.add_learning_resource(skill_tree_id, skill_id, resource)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.put("/{skill_tree_id}/skills/{skill_id}/completion", response_model=Dict[str, Any])
async def update_skill_completion(
    skill_tree_id: str,
    skill_id: str,
    completion_rate: float,
    service: SkillTreeApplicationService = Depends(get_skill_tree_service)
):
    """更新技能完成率"""
    result = service.update_skill_completion(skill_tree_id, skill_id, completion_rate)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.post("/{skill_tree_id}/paths/generate", response_model=Dict[str, Any])
async def generate_learning_paths(
    skill_tree_id: str,
    service: SkillTreeApplicationService = Depends(get_skill_tree_service)
):
    """生成学习路径"""
    result = service.generate_learning_paths(skill_tree_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result
