import unittest
import os
import shutil
from src.skill_tree.domain.models import SkillTree, SkillNode, SkillLevel, SkillType
from src.skill_tree.domain.services import SkillTreeService
from src.skill_tree.infrastructure.repositories import FileSkillTreeRepository
from src.skill_tree.application.services import SkillTreeApplicationService


class TestSkillTree(unittest.TestCase):
    """技能树模块测试"""

    def setUp(self):
        """设置测试环境"""
        # 创建临时存储目录
        self.test_dir = "./test_skill_tree_data"
        os.makedirs(self.test_dir, exist_ok=True)
        # 创建仓储实例
        self.repository = FileSkillTreeRepository(self.test_dir)
        # 创建应用服务实例
        self.service = SkillTreeApplicationService(self.repository)

    def tearDown(self):
        """清理测试环境"""
        # 删除临时存储目录
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_create_skill_tree(self):
        """测试创建技能树"""
        result = self.service.create_skill_tree(
            name="竞赛技能树",
            description="竞赛相关技能树"
        )
        self.assertTrue(result["success"])
        self.assertIn("data", result)
        self.assertIn("id", result["data"])

    def test_add_skill(self):
        """测试添加技能"""
        # 先创建技能树
        create_result = self.service.create_skill_tree(
            name="竞赛技能树",
            description="竞赛相关技能树"
        )
        skill_tree_id = create_result["data"]["id"]

        # 添加技能
        add_result = self.service.add_skill(
            skill_tree_id=skill_tree_id,
            name="Python基础",
            description="Python编程语言基础",
            level="beginner",
            skill_type="technical",
            learning_time=20
        )
        self.assertTrue(add_result["success"])
        self.assertIn("data", add_result)
        self.assertIn("id", add_result["data"])

    def test_establish_skill_relation(self):
        """测试建立技能关系"""
        # 先创建技能树
        create_result = self.service.create_skill_tree(
            name="竞赛技能树",
            description="竞赛相关技能树"
        )
        skill_tree_id = create_result["data"]["id"]

        # 添加两个技能
        skill1_result = self.service.add_skill(
            skill_tree_id=skill_tree_id,
            name="Python基础",
            description="Python编程语言基础",
            level="beginner",
            skill_type="technical"
        )
        skill1_id = skill1_result["data"]["id"]

        skill2_result = self.service.add_skill(
            skill_tree_id=skill_tree_id,
            name="算法基础",
            description="算法基础知识",
            level="intermediate",
            skill_type="technical"
        )
        skill2_id = skill2_result["data"]["id"]

        # 建立关系
        relation_result = self.service.establish_skill_relation(
            skill_tree_id=skill_tree_id,
            source_skill_id=skill1_id,
            target_skill_id=skill2_id,
            relation_type="prerequisite"
        )
        self.assertTrue(relation_result["success"])

    def test_add_learning_resource(self):
        """测试添加学习资源"""
        # 先创建技能树和技能
        create_result = self.service.create_skill_tree(
            name="竞赛技能树",
            description="竞赛相关技能树"
        )
        skill_tree_id = create_result["data"]["id"]

        add_result = self.service.add_skill(
            skill_tree_id=skill_tree_id,
            name="Python基础",
            description="Python编程语言基础",
            level="beginner",
            skill_type="technical"
        )
        skill_id = add_result["data"]["id"]

        # 添加学习资源
        resource = {
            "name": "Python官方文档",
            "url": "https://docs.python.org/3/",
            "type": "document",
            "description": "Python官方文档"
        }
        resource_result = self.service.add_learning_resource(
            skill_tree_id=skill_tree_id,
            skill_id=skill_id,
            resource=resource
        )
        self.assertTrue(resource_result["success"])

    def test_update_skill_completion(self):
        """测试更新技能完成率"""
        # 先创建技能树和技能
        create_result = self.service.create_skill_tree(
            name="竞赛技能树",
            description="竞赛相关技能树"
        )
        skill_tree_id = create_result["data"]["id"]

        add_result = self.service.add_skill(
            skill_tree_id=skill_tree_id,
            name="Python基础",
            description="Python编程语言基础",
            level="beginner",
            skill_type="technical"
        )
        skill_id = add_result["data"]["id"]

        # 更新完成率
        completion_result = self.service.update_skill_completion(
            skill_tree_id=skill_tree_id,
            skill_id=skill_id,
            completion_rate=85.5
        )
        self.assertTrue(completion_result["success"])

    def test_generate_learning_paths(self):
        """测试生成学习路径"""
        # 先创建技能树和技能
        create_result = self.service.create_skill_tree(
            name="竞赛技能树",
            description="竞赛相关技能树"
        )
        skill_tree_id = create_result["data"]["id"]

        # 添加技能
        skill1_result = self.service.add_skill(
            skill_tree_id=skill_tree_id,
            name="Python基础",
            description="Python编程语言基础",
            level="beginner",
            skill_type="technical",
            learning_time=20
        )
        skill1_id = skill1_result["data"]["id"]

        skill2_result = self.service.add_skill(
            skill_tree_id=skill_tree_id,
            name="算法基础",
            description="算法基础知识",
            level="intermediate",
            skill_type="technical",
            learning_time=30
        )
        skill2_id = skill2_result["data"]["id"]

        skill3_result = self.service.add_skill(
            skill_tree_id=skill_tree_id,
            name="机器学习",
            description="机器学习基础",
            level="advanced",
            skill_type="technical",
            learning_time=40
        )
        skill3_id = skill3_result["data"]["id"]

        # 建立关系
        self.service.establish_skill_relation(
            skill_tree_id=skill_tree_id,
            source_skill_id=skill1_id,
            target_skill_id=skill2_id,
            relation_type="prerequisite"
        )

        self.service.establish_skill_relation(
            skill_tree_id=skill_tree_id,
            source_skill_id=skill2_id,
            target_skill_id=skill3_id,
            relation_type="prerequisite"
        )

        # 生成学习路径
        paths_result = self.service.generate_learning_paths(skill_tree_id)
        self.assertTrue(paths_result["success"])
        self.assertIn("data", paths_result)
        self.assertGreater(len(paths_result["data"]), 0)

    def test_get_skill_tree(self):
        """测试获取技能树"""
        # 先创建技能树
        create_result = self.service.create_skill_tree(
            name="竞赛技能树",
            description="竞赛相关技能树"
        )
        skill_tree_id = create_result["data"]["id"]

        # 获取技能树
        get_result = self.service.get_skill_tree(skill_tree_id)
        self.assertTrue(get_result["success"])
        self.assertIn("data", get_result)
        self.assertEqual(get_result["data"]["name"], "竞赛技能树")

    def test_list_skill_trees(self):
        """测试列出所有技能树"""
        # 创建两个技能树
        self.service.create_skill_tree(
            name="竞赛技能树1",
            description="竞赛相关技能树1"
        )

        self.service.create_skill_tree(
            name="竞赛技能树2",
            description="竞赛相关技能树2"
        )

        # 列出所有技能树
        list_result = self.service.list_skill_trees()
        self.assertTrue(list_result["success"])
        self.assertIn("data", list_result)
        self.assertGreaterEqual(len(list_result["data"]), 2)

    def test_delete_skill_tree(self):
        """测试删除技能树"""
        # 先创建技能树
        create_result = self.service.create_skill_tree(
            name="竞赛技能树",
            description="竞赛相关技能树"
        )
        skill_tree_id = create_result["data"]["id"]

        # 删除技能树
        delete_result = self.service.delete_skill_tree(skill_tree_id)
        self.assertTrue(delete_result["success"])

        # 验证删除成功
        get_result = self.service.get_skill_tree(skill_tree_id)
        self.assertFalse(get_result["success"])


if __name__ == "__main__":
    unittest.main()
