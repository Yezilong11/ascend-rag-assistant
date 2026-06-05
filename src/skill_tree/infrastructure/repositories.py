from typing import List, Optional
import json
import logging
import os
import threading
from src.skill_tree.domain.models import SkillTree, SkillNode, SkillLevel, SkillType, LearningPath, SkillRelation

logger = logging.getLogger(__name__)


class SkillTreeRepositoryInterface:
    """技能树仓储接口"""

    def save(self, skill_tree: SkillTree) -> bool:
        """保存技能树"""
        pass

    def load(self, skill_tree_id: str) -> Optional[SkillTree]:
        """加载技能树"""
        pass

    def delete(self, skill_tree_id: str) -> bool:
        """删除技能树"""
        pass

    def list_all(self) -> List[SkillTree]:
        """列出所有技能树"""
        pass


class FileSkillTreeRepository(SkillTreeRepositoryInterface):
    """基于文件的技能树仓储实现"""

    _file_lock = threading.Lock()

    def __init__(self, storage_dir: str = "./skill_tree_data"):
        """初始化仓储"""
        self.storage_dir = storage_dir
        with self._file_lock:
            os.makedirs(self.storage_dir, exist_ok=True)

    def save(self, skill_tree: SkillTree) -> bool:
        """保存技能树到文件"""
        with self._file_lock:
            try:
                file_path = os.path.join(self.storage_dir, f"{skill_tree.id}.json")
                data = self._serialize_skill_tree(skill_tree)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                return True
            except Exception as e:
                logger.error(f"保存技能树失败: {e}", exc_info=True)
                return False

    def load(self, skill_tree_id: str) -> Optional[SkillTree]:
        """从文件加载技能树"""
        with self._file_lock:
            try:
                file_path = os.path.join(self.storage_dir, f"{skill_tree_id}.json")
                if not os.path.exists(file_path):
                    return None

                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                return self._deserialize_skill_tree(data)
            except Exception as e:
                logger.error(f"加载技能树失败: {e}", exc_info=True)
                return None

    def delete(self, skill_tree_id: str) -> bool:
        """删除技能树文件"""
        with self._file_lock:
            try:
                file_path = os.path.join(self.storage_dir, f"{skill_tree_id}.json")
                if os.path.exists(file_path):
                    os.remove(file_path)
                return True
            except Exception as e:
                logger.error(f"删除技能树失败: {e}", exc_info=True)
                return False

    def list_all(self) -> List[SkillTree]:
        """列出所有技能树"""
        with self._file_lock:
            skill_trees = []
            try:
                for filename in os.listdir(self.storage_dir):
                    if filename.endswith('.json'):
                        skill_tree_id = filename[:-5]  # 去掉 .json 后缀
                        try:
                            file_path = os.path.join(self.storage_dir, f"{skill_tree_id}.json")
                            with open(file_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            skill_tree = self._deserialize_skill_tree(data)
                            if skill_tree:
                                skill_trees.append(skill_tree)
                        except Exception as e:
                            logger.error(f"加载技能树 {skill_tree_id} 失败: {e}", exc_info=True)
            except Exception as e:
                logger.error(f"列出技能树失败: {e}", exc_info=True)
            return skill_trees

    def _serialize_skill_tree(self, skill_tree: SkillTree) -> dict:
        """序列化技能树"""
        return {
            "id": skill_tree.id,
            "name": skill_tree.name,
            "description": skill_tree.description,
            "version": skill_tree.version,
            "created_at": skill_tree.created_at,
            "updated_at": skill_tree.updated_at,
            "root_nodes": skill_tree.root_nodes,
            "skill_nodes": {
                node_id: self._serialize_skill_node(node)
                for node_id, node in skill_tree.skill_nodes.items()
            },
            "learning_paths": {
                path_id: self._serialize_learning_path(path)
                for path_id, path in skill_tree.learning_paths.items()
            }
        }

    def _serialize_skill_node(self, skill_node: SkillNode) -> dict:
        """序列化技能节点"""
        return {
            "id": skill_node.id,
            "name": skill_node.name,
            "description": skill_node.description,
            "level": skill_node.level.value,
            "skill_type": skill_node.skill_type.value,
            "parent_ids": skill_node.parent_ids,
            "child_ids": skill_node.child_ids,
            "related_ids": skill_node.related_ids,
            "resources": skill_node.resources,
            "prerequisites": [
                {
                    "source_skill_id": rel.source_skill_id,
                    "target_skill_id": rel.target_skill_id,
                    "relation_type": rel.relation_type,
                    "weight": rel.weight
                }
                for rel in skill_node.prerequisites
            ],
            "learning_time": skill_node.learning_time,
            "completion_rate": skill_node.completion_rate
        }

    def _serialize_learning_path(self, learning_path: LearningPath) -> dict:
        """序列化学习路径"""
        return {
            "path_id": learning_path.path_id,
            "skill_ids": learning_path.skill_ids,
            "estimated_time": learning_path.estimated_time,
            "difficulty": learning_path.difficulty.value
        }

    def _deserialize_skill_tree(self, data: dict) -> SkillTree:
        """反序列化技能树"""
        from datetime import datetime

        skill_tree = SkillTree(
            id=data.get("id"),
            name=data.get("name"),
            description=data.get("description"),
            version=data.get("version", "1.0"),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
            root_nodes=data.get("root_nodes", [])
        )

        # 反序列化技能节点
        skill_nodes_data = data.get("skill_nodes", {})
        for node_id, node_data in skill_nodes_data.items():
            skill_node = self._deserialize_skill_node(node_data)
            skill_tree.skill_nodes[node_id] = skill_node

        # 反序列化学习路径
        learning_paths_data = data.get("learning_paths", {})
        for path_id, path_data in learning_paths_data.items():
            learning_path = self._deserialize_learning_path(path_data)
            skill_tree.learning_paths[path_id] = learning_path

        return skill_tree

    def _deserialize_skill_node(self, data: dict) -> SkillNode:
        """反序列化技能节点"""
        skill_node = SkillNode(
            id=data.get("id"),
            name=data.get("name"),
            description=data.get("description"),
            level=SkillLevel(data.get("level", "beginner")),
            skill_type=SkillType(data.get("skill_type", "technical")),
            parent_ids=data.get("parent_ids", []),
            child_ids=data.get("child_ids", []),
            related_ids=data.get("related_ids", []),
            resources=data.get("resources", []),
            learning_time=data.get("learning_time", 0),
            completion_rate=data.get("completion_rate", 0.0)
        )

        # 反序列化前置条件
        prerequisites_data = data.get("prerequisites", [])
        for rel_data in prerequisites_data:
            relation = SkillRelation(
                source_skill_id=rel_data.get("source_skill_id"),
                target_skill_id=rel_data.get("target_skill_id"),
                relation_type=rel_data.get("relation_type"),
                weight=rel_data.get("weight", 1)
            )
            skill_node.prerequisites.append(relation)

        return skill_node

    def _deserialize_learning_path(self, data: dict) -> LearningPath:
        """反序列化学习路径"""
        return LearningPath(
            path_id=data.get("path_id"),
            skill_ids=data.get("skill_ids", []),
            estimated_time=data.get("estimated_time", 0),
            difficulty=SkillLevel(data.get("difficulty", "beginner"))
        )
