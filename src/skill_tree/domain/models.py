from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from uuid import uuid4
from enum import Enum


class SkillLevel(Enum):
    """技能难度等级"""
    BEGINNER = "beginner"  # 初级
    INTERMEDIATE = "intermediate"  # 中级
    ADVANCED = "advanced"  # 高级
    EXPERT = "expert"  # 专家级


class SkillType(Enum):
    """技能类型"""
    TECHNICAL = "technical"  # 技术类
    THEORETICAL = "theoretical"  # 理论类
    PRACTICAL = "practical"  # 实践类
    COMPETITION = "competition"  # 竞赛类


@dataclass(frozen=True)
class SkillRelation:
    """技能关系值对象"""
    source_skill_id: str  # 源技能ID
    target_skill_id: str  # 目标技能ID
    relation_type: str  # 关系类型：prerequisite（前置）、related（相关）、advanced（进阶）
    weight: int = 1  # 关系权重，用于学习路径排序


@dataclass(frozen=True)
class LearningPath:
    """学习路径值对象"""
    path_id: str = field(default_factory=lambda: str(uuid4()))
    skill_ids: List[str] = field(default_factory=list)  # 路径中的技能ID列表
    estimated_time: int = 0  # 预估学习时间（小时）
    difficulty: SkillLevel = SkillLevel.BEGINNER  # 路径难度


@dataclass
class SkillNode:
    """技能节点实体"""
    name: str  # 技能名称
    description: str  # 技能描述
    level: SkillLevel  # 技能难度
    skill_type: SkillType  # 技能类型
    id: str = field(default_factory=lambda: str(uuid4()))
    parent_ids: List[str] = field(default_factory=list)  # 父技能ID列表
    child_ids: List[str] = field(default_factory=list)  # 子技能ID列表
    related_ids: List[str] = field(default_factory=list)  # 相关技能ID列表
    resources: List[Dict[str, Any]] = field(default_factory=list)  # 学习资源
    prerequisites: List[SkillRelation] = field(default_factory=list)  # 前置条件
    learning_time: int = 0  # 预估学习时间（小时）
    completion_rate: float = 0.0  # 完成率（0-100）

    def add_parent(self, parent_id: str):
        """添加父技能"""
        if parent_id not in self.parent_ids:
            self.parent_ids.append(parent_id)

    def add_child(self, child_id: str):
        """添加子技能"""
        if child_id not in self.child_ids:
            self.child_ids.append(child_id)

    def add_related(self, related_id: str):
        """添加相关技能"""
        if related_id not in self.related_ids:
            self.related_ids.append(related_id)

    def add_resource(self, resource: Dict[str, Any]):
        """添加学习资源"""
        self.resources.append(resource)

    def update_completion_rate(self, rate: float):
        """更新完成率"""
        self.completion_rate = max(0.0, min(100.0, rate))


@dataclass
class SkillTree:
    """技能树聚合根"""
    name: str  # 技能树名称
    description: str  # 技能树描述
    id: str = field(default_factory=lambda: str(uuid4()))
    version: str = "1.0"  # 技能树版本
    created_at: str = field(default_factory=lambda: "2024-01-01")  # 创建时间
    updated_at: str = field(default_factory=lambda: "2024-01-01")  # 更新时间
    root_nodes: List[str] = field(default_factory=list)  # 根节点ID列表
    skill_nodes: Dict[str, SkillNode] = field(default_factory=dict)  # 技能节点字典
    learning_paths: Dict[str, LearningPath] = field(default_factory=dict)  # 学习路径字典

    def add_skill_node(self, skill_node: SkillNode):
        """添加技能节点"""
        self.skill_nodes[skill_node.id] = skill_node
        # 如果是根节点，添加到根节点列表
        if not skill_node.parent_ids:
            self.root_nodes.append(skill_node.id)

    def get_skill_node(self, skill_id: str) -> Optional[SkillNode]:
        """获取技能节点"""
        return self.skill_nodes.get(skill_id)

    def add_learning_path(self, learning_path: LearningPath):
        """添加学习路径"""
        self.learning_paths[learning_path.path_id] = learning_path

    def get_learning_path(self, path_id: str) -> Optional[LearningPath]:
        """获取学习路径"""
        return self.learning_paths.get(path_id)

    def update_skill_relation(self, source_skill_id: str, target_skill_id: str, relation_type: str):
        """更新技能关系"""
        if source_skill_id in self.skill_nodes and target_skill_id in self.skill_nodes:
            # 添加前置关系
            relation = SkillRelation(
                source_skill_id=source_skill_id,
                target_skill_id=target_skill_id,
                relation_type=relation_type
            )
            # 更新源技能的子技能
            self.skill_nodes[source_skill_id].add_child(target_skill_id)
            # 更新目标技能的父技能
            self.skill_nodes[target_skill_id].add_parent(source_skill_id)
            # 添加到前置条件
            self.skill_nodes[target_skill_id].prerequisites.append(relation)

    def generate_learning_paths(self) -> List[LearningPath]:
        """生成学习路径（迭代实现）"""
        paths = []
        # 使用栈代替递归
        stack = []
        
        # 初始化栈，将所有根节点加入
        for root_id in self.root_nodes:
            stack.append((root_id, []))
        
        while stack:
            node_id, current_path = stack.pop()
            new_path = current_path + [node_id]
            
            # 检查节点是否存在
            if node_id not in self.skill_nodes:
                continue
            
            # 如果是叶子节点，生成完整路径
            if not self.skill_nodes[node_id].child_ids:
                # 计算路径总学习时间
                total_time = 0
                for skill_id in new_path:
                    if skill_id in self.skill_nodes:
                        total_time += self.skill_nodes[skill_id].learning_time
                
                path = LearningPath(
                    skill_ids=new_path,
                    estimated_time=total_time,
                    difficulty=self._calculate_path_difficulty(new_path)
                )
                paths.append(path)
            else:
                # 将子节点加入栈
                # 注意：为了保持与递归实现相同的顺序，需要逆序添加
                for child_id in reversed(self.skill_nodes[node_id].child_ids):
                    stack.append((child_id, new_path))
        
        return paths

    def _calculate_path_difficulty(self, skill_ids: List[str]) -> SkillLevel:
        """计算路径难度"""
        if not skill_ids:
            return SkillLevel.BEGINNER
        
        # 定义难度级别顺序
        level_order = {
            SkillLevel.BEGINNER: 0,
            SkillLevel.INTERMEDIATE: 1,
            SkillLevel.ADVANCED: 2,
            SkillLevel.EXPERT: 3
        }
        
        # 取路径中最高难度
        max_level = SkillLevel.BEGINNER
        max_order = -1
        for skill_id in skill_ids:
            if skill_id in self.skill_nodes:
                level = self.skill_nodes[skill_id].level
                if level_order[level] > max_order:
                    max_order = level_order[level]
                    max_level = level
        
        return max_level
