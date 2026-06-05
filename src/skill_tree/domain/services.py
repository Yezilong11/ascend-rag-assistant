from typing import List, Optional, Dict, Any
from datetime import datetime
from .models import SkillTree, SkillNode, SkillLevel, SkillType, LearningPath, SkillRelation


class SkillTreeService:
    """技能树领域服务"""

    def create_skill_tree(self, name: str, description: str) -> SkillTree:
        """创建技能树"""
        return SkillTree(
            name=name,
            description=description
        )

    def add_skill_to_tree(self, skill_tree: SkillTree, name: str, description: str, 
                         level: SkillLevel, skill_type: SkillType, learning_time: int = 0) -> SkillNode:
        """向技能树添加技能"""
        skill_node = SkillNode(
            name=name,
            description=description,
            level=level,
            skill_type=skill_type,
            learning_time=learning_time
        )
        skill_tree.add_skill_node(skill_node)
        return skill_node

    def establish_skill_relation(self, skill_tree: SkillTree, source_skill_id: str, 
                               target_skill_id: str, relation_type: str):
        """建立技能关系"""
        skill_tree.update_skill_relation(source_skill_id, target_skill_id, relation_type)

    def add_learning_resource(self, skill_tree: SkillTree, skill_id: str, resource: Dict[str, Any]):
        """为技能添加学习资源"""
        skill_node = skill_tree.get_skill_node(skill_id)
        if skill_node:
            skill_node.add_resource(resource)

    def update_skill_completion(self, skill_tree: SkillTree, skill_id: str, completion_rate: float):
        """更新技能完成率"""
        skill_node = skill_tree.get_skill_node(skill_id)
        if skill_node:
            skill_node.update_completion_rate(completion_rate)
            skill_tree.updated_at = datetime.now().isoformat()

    def generate_learning_paths(self, skill_tree: SkillTree) -> List[LearningPath]:
        """生成学习路径"""
        paths = skill_tree.generate_learning_paths()
        for path in paths:
            skill_tree.add_learning_path(path)
        return paths

    def get_skill_path(self, skill_tree: SkillTree, skill_id: str) -> List[str]:
        """获取技能的学习路径"""
        skill_node = skill_tree.get_skill_node(skill_id)
        if not skill_node:
            return []

        path = []
        current_node = skill_node
        
        # 回溯到根节点
        while current_node:
            path.insert(0, current_node.id)
            if not current_node.parent_ids:
                break
            # 取第一个父节点（简化处理）
            parent_id = current_node.parent_ids[0]
            current_node = skill_tree.get_skill_node(parent_id)
        
        return path

    def get_recommended_skills(self, skill_tree: SkillTree, current_skill_id: str, limit: int = 5) -> List[SkillNode]:
        """获取推荐技能"""
        current_skill = skill_tree.get_skill_node(current_skill_id)
        if not current_skill:
            return []

        recommended = []
        
        # 推荐子技能（进阶）
        for child_id in current_skill.child_ids[:limit]:
            child_skill = skill_tree.get_skill_node(child_id)
            if child_skill:
                recommended.append(child_skill)
        
        # 如果不够，推荐相关技能
        if len(recommended) < limit:
            for related_id in current_skill.related_ids[:limit - len(recommended)]:
                related_skill = skill_tree.get_skill_node(related_id)
                if related_skill and related_skill not in recommended:
                    recommended.append(related_skill)
        
        return recommended

    def calculate_skill_tree_completion(self, skill_tree: SkillTree) -> float:
        """计算技能树完成率"""
        if not skill_tree.skill_nodes:
            return 0.0

        total_completion = sum(skill.completion_rate for skill in skill_tree.skill_nodes.values())
        return total_completion / len(skill_tree.skill_nodes)


class SkillEvent:
    """技能领域事件基类"""
    def __init__(self, event_type: str, data: Dict[str, Any]):
        self.event_type = event_type
        self.data = data
        self.timestamp = datetime.now().isoformat()


class SkillAddedEvent(SkillEvent):
    """技能添加事件"""
    def __init__(self, skill_tree_id: str, skill_id: str, skill_name: str):
        super().__init__(
            event_type="skill_added",
            data={
                "skill_tree_id": skill_tree_id,
                "skill_id": skill_id,
                "skill_name": skill_name
            }
        )


class SkillRelationEstablishedEvent(SkillEvent):
    """技能关系建立事件"""
    def __init__(self, skill_tree_id: str, source_skill_id: str, target_skill_id: str, relation_type: str):
        super().__init__(
            event_type="skill_relation_established",
            data={
                "skill_tree_id": skill_tree_id,
                "source_skill_id": source_skill_id,
                "target_skill_id": target_skill_id,
                "relation_type": relation_type
            }
        )


class SkillCompletedEvent(SkillEvent):
    """技能完成事件"""
    def __init__(self, skill_tree_id: str, skill_id: str, completion_rate: float):
        super().__init__(
            event_type="skill_completed",
            data={
                "skill_tree_id": skill_tree_id,
                "skill_id": skill_id,
                "completion_rate": completion_rate
            }
        )


class LearningPathGeneratedEvent(SkillEvent):
    """学习路径生成事件"""
    def __init__(self, skill_tree_id: str, path_id: str, skill_count: int):
        super().__init__(
            event_type="learning_path_generated",
            data={
                "skill_tree_id": skill_tree_id,
                "path_id": path_id,
                "skill_count": skill_count
            }
        )
