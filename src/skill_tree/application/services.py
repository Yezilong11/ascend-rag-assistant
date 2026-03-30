import logging
from typing import List, Optional, Dict, Any
from src.skill_tree.domain.models import SkillTree, SkillNode, SkillLevel, SkillType, LearningPath
from src.skill_tree.domain.services import SkillTreeService
from src.skill_tree.infrastructure.repositories import SkillTreeRepositoryInterface

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SkillTreeApplicationService:
    """技能树应用服务"""

    def __init__(self, repository: SkillTreeRepositoryInterface):
        """初始化应用服务"""
        self.repository = repository
        self.skill_tree_service = SkillTreeService()

    def create_skill_tree(self, name: str, description: str) -> Dict[str, Any]:
        """创建技能树"""
        logger.info(f"创建技能树: name={name}, description={description}")
        try:
            skill_tree = self.skill_tree_service.create_skill_tree(name, description)
            logger.info(f"技能树创建成功: id={skill_tree.id}")
            
            saved = self.repository.save(skill_tree)
            if saved:
                logger.info(f"技能树保存成功: id={skill_tree.id}")
                return {
                    "success": True,
                    "data": {
                        "id": skill_tree.id,
                        "name": skill_tree.name,
                        "description": skill_tree.description
                    }
                }
            else:
                logger.error(f"技能树保存失败: id={skill_tree.id}")
                return {
                    "success": False,
                    "message": "创建技能树失败"
                }
        except Exception as e:
            logger.error(f"创建技能树时发生错误: {str(e)}")
            return {
                "success": False,
                "message": f"创建技能树失败: {str(e)}"
            }

    def add_skill(self, skill_tree_id: str, name: str, description: str, 
                 level: str, skill_type: str, learning_time: int = 0) -> Dict[str, Any]:
        """添加技能"""
        logger.info(f"添加技能: skill_tree_id={skill_tree_id}, name={name}, level={level}, skill_type={skill_type}")
        try:
            skill_tree = self.repository.load(skill_tree_id)
            if not skill_tree:
                logger.error(f"技能树不存在: id={skill_tree_id}")
                return {
                    "success": False,
                    "message": "技能树不存在"
                }

            try:
                level_enum = SkillLevel(level)
                type_enum = SkillType(skill_type)
            except ValueError as e:
                logger.error(f"无效的技能等级或类型: {str(e)}")
                return {
                    "success": False,
                    "message": "无效的技能等级或类型"
                }

            skill_node = self.skill_tree_service.add_skill_to_tree(
                skill_tree, name, description, level_enum, type_enum, learning_time
            )
            logger.info(f"技能添加成功: id={skill_node.id}, name={skill_node.name}")
            
            saved = self.repository.save(skill_tree)
            if saved:
                logger.info(f"技能树保存成功: id={skill_tree.id}")
                return {
                    "success": True,
                    "data": {
                        "id": skill_node.id,
                        "name": skill_node.name,
                        "level": skill_node.level.value,
                        "type": skill_node.skill_type.value
                    }
                }
            else:
                logger.error(f"技能树保存失败: id={skill_tree.id}")
                return {
                    "success": False,
                    "message": "添加技能失败"
                }
        except Exception as e:
            logger.error(f"添加技能时发生错误: {str(e)}")
            return {
                "success": False,
                "message": f"添加技能失败: {str(e)}"
            }

    def establish_skill_relation(self, skill_tree_id: str, source_skill_id: str, 
                               target_skill_id: str, relation_type: str) -> Dict[str, Any]:
        """建立技能关系"""
        skill_tree = self.repository.load(skill_tree_id)
        if not skill_tree:
            return {
                "success": False,
                "message": "技能树不存在"
            }

        if source_skill_id not in skill_tree.skill_nodes:
            return {
                "success": False,
                "message": "源技能不存在"
            }

        if target_skill_id not in skill_tree.skill_nodes:
            return {
                "success": False,
                "message": "目标技能不存在"
            }

        self.skill_tree_service.establish_skill_relation(
            skill_tree, source_skill_id, target_skill_id, relation_type
        )
        saved = self.repository.save(skill_tree)
        if saved:
            return {
                "success": True,
                "message": "技能关系建立成功"
            }
        else:
            return {
                "success": False,
                "message": "建立技能关系失败"
            }

    def add_learning_resource(self, skill_tree_id: str, skill_id: str, 
                             resource: Dict[str, Any]) -> Dict[str, Any]:
        """添加学习资源"""
        skill_tree = self.repository.load(skill_tree_id)
        if not skill_tree:
            return {
                "success": False,
                "message": "技能树不存在"
            }

        if skill_id not in skill_tree.skill_nodes:
            return {
                "success": False,
                "message": "技能不存在"
            }

        self.skill_tree_service.add_learning_resource(skill_tree, skill_id, resource)
        saved = self.repository.save(skill_tree)
        if saved:
            return {
                "success": True,
                "message": "学习资源添加成功"
            }
        else:
            return {
                "success": False,
                "message": "添加学习资源失败"
            }

    def update_skill_completion(self, skill_tree_id: str, skill_id: str, 
                               completion_rate: float) -> Dict[str, Any]:
        """更新技能完成率"""
        skill_tree = self.repository.load(skill_tree_id)
        if not skill_tree:
            return {
                "success": False,
                "message": "技能树不存在"
            }

        if skill_id not in skill_tree.skill_nodes:
            return {
                "success": False,
                "message": "技能不存在"
            }

        self.skill_tree_service.update_skill_completion(skill_tree, skill_id, completion_rate)
        saved = self.repository.save(skill_tree)
        if saved:
            return {
                "success": True,
                "message": "技能完成率更新成功"
            }
        else:
            return {
                "success": False,
                "message": "更新技能完成率失败"
            }

    def generate_learning_paths(self, skill_tree_id: str) -> Dict[str, Any]:
        """生成学习路径"""
        skill_tree = self.repository.load(skill_tree_id)
        if not skill_tree:
            return {
                "success": False,
                "message": "技能树不存在"
            }

        paths = self.skill_tree_service.generate_learning_paths(skill_tree)
        saved = self.repository.save(skill_tree)
        if saved:
            return {
                "success": True,
                "data": [
                    {
                        "path_id": path.path_id,
                        "skill_count": len(path.skill_ids),
                        "estimated_time": path.estimated_time,
                        "difficulty": path.difficulty.value
                    }
                    for path in paths
                ]
            }
        else:
            return {
                "success": False,
                "message": "生成学习路径失败"
            }

    def get_skill_tree(self, skill_tree_id: str) -> Dict[str, Any]:
        """获取技能树"""
        skill_tree = self.repository.load(skill_tree_id)
        if not skill_tree:
            return {
                "success": False,
                "message": "技能树不存在"
            }

        return {
            "success": True,
            "data": {
                "id": skill_tree.id,
                "name": skill_tree.name,
                "description": skill_tree.description,
                "root_nodes": skill_tree.root_nodes,
                "skill_nodes": {
                    node_id: {
                        "id": node.id,
                        "name": node.name,
                        "description": node.description,
                        "level": node.level.value,
                        "type": node.skill_type.value,
                        "parent_ids": node.parent_ids,
                        "child_ids": node.child_ids,
                        "related_ids": node.related_ids,
                        "resources": node.resources,
                        "learning_time": node.learning_time,
                        "completion_rate": node.completion_rate
                    }
                    for node_id, node in skill_tree.skill_nodes.items()
                },
                "learning_paths": {
                    path_id: {
                        "path_id": path.path_id,
                        "skill_ids": path.skill_ids,
                        "estimated_time": path.estimated_time,
                        "difficulty": path.difficulty.value
                    }
                    for path_id, path in skill_tree.learning_paths.items()
                },
                "completion_rate": self.skill_tree_service.calculate_skill_tree_completion(skill_tree)
            }
        }

    def list_skill_trees(self) -> Dict[str, Any]:
        """列出所有技能树"""
        skill_trees = self.repository.list_all()
        return {
            "success": True,
            "data": [
                 {
                     "id": tree.id,
                     "name": tree.name,
                     "description": tree.description,
                     "version": tree.version,
                     "skill_count": len(tree.skill_nodes),
                     "completion_rate": self.skill_tree_service.calculate_skill_tree_completion(tree)
                 }
                 for tree in skill_trees
            ]
        }

    def delete_skill_tree(self, skill_tree_id: str) -> Dict[str, Any]:
        """删除技能树"""
        deleted = self.repository.delete(skill_tree_id)
        if deleted:
            return {
                "success": True,
                "message": "技能树删除成功"
            }
        else:
            return {
                "success": False,
                "message": "删除技能树失败"
            }
