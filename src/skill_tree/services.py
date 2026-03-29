import os
import json
from datetime import datetime
from .domain import SkillDomain, SkillCategory, Skill, SubSkill, Resource, Quiz, CompetitionSkillMapping

class SkillTreeManager:
    def __init__(self, data_file: str = "data/skill_tree.json"):
        self.data_file = data_file
        self.skill_domains = []
        self._load_data()
    
    def _load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for domain_data in data.get("skill_domains", []):
                    domain = SkillDomain(
                        domain_data["id"],
                        domain_data["name"],
                        domain_data["description"]
                    )
                    for category_data in domain_data.get("categories", []):
                        category = SkillCategory(
                            category_data["id"],
                            category_data["name"],
                            category_data["description"]
                        )
                        for skill_data in category_data.get("skills", []):
                            skill = Skill(
                                skill_data["id"],
                                skill_data["name"],
                                skill_data["description"],
                                skill_data.get("difficulty", ""),
                                skill_data.get("estimated_time", "")
                            )
                            for sub_skill_data in skill_data.get("sub_skills", []):
                                sub_skill = SubSkill(
                                    sub_skill_data["id"],
                                    sub_skill_data["name"],
                                    sub_skill_data["description"]
                                )
                                for resource_data in sub_skill_data.get("resources", []):
                                    resource = Resource(
                                        resource_data["type"],
                                        resource_data["title"],
                                        resource_data["url"]
                                    )
                                    sub_skill.add_resource(resource)
                                for quiz_data in sub_skill_data.get("quiz", []):
                                    quiz = Quiz(
                                        quiz_data["id"],
                                        quiz_data["question"],
                                        quiz_data["options"],
                                        quiz_data["correct_answer"]
                                    )
                                    sub_skill.add_quiz(quiz)
                                skill.add_sub_skill(sub_skill)
                            category.add_skill(skill)
                        domain.add_category(category)
                    self.skill_domains.append(domain)
    
    def save_data(self):
        data = {
            "skill_domains": [
                {
                    "id": domain.id,
                    "name": domain.name,
                    "description": domain.description,
                    "categories": [
                        {
                            "id": category.id,
                            "name": category.name,
                            "description": category.description,
                            "skills": [
                                {
                                    "id": skill.id,
                                    "name": skill.name,
                                    "description": skill.description,
                                    "difficulty": skill.difficulty,
                                    "estimated_time": skill.estimated_time,
                                    "sub_skills": [
                                        {
                                            "id": sub_skill.id,
                                            "name": sub_skill.name,
                                            "description": sub_skill.description,
                                            "resources": [
                                                {
                                                    "type": resource.type,
                                                    "title": resource.title,
                                                    "url": resource.url
                                                }
                                                for resource in sub_skill.resources
                                            ],
                                            "quiz": [
                                                {
                                                    "id": quiz.id,
                                                    "question": quiz.question,
                                                    "options": quiz.options,
                                                    "correct_answer": quiz.correct_answer
                                                }
                                                for quiz in sub_skill.quiz
                                            ]
                                        }
                                        for sub_skill in skill.sub_skills
                                    ]
                                }
                                for skill in category.skills
                            ]
                        }
                        for category in domain.categories
                    ]
                }
                for domain in self.skill_domains
            ]
        }
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_all_domains(self):
        return self.skill_domains
    
    def get_domain(self, domain_id):
        for domain in self.skill_domains:
            if domain.id == domain_id:
                return domain
        return None
    
    def get_skill_by_path(self, skill_path):
        """通过路径获取技能，路径格式：domain.category.skill.sub_skill"""
        parts = skill_path.split(".")
        if len(parts) != 4:
            return None
        
        domain = self.get_domain(parts[0])
        if not domain:
            return None
        
        category = domain.get_category(parts[1])
        if not category:
            return None
        
        skill = category.get_skill(parts[2])
        if not skill:
            return None
        
        sub_skill = skill.get_sub_skill(parts[3])
        return sub_skill

class SkillAssessmentService:
    def __init__(self, skill_tree_manager):
        self.skill_tree_manager = skill_tree_manager
    
    def get_quiz_for_skill(self, skill_path):
        sub_skill = self.skill_tree_manager.get_skill_by_path(skill_path)
        if not sub_skill:
            return []
        return sub_skill.quiz
    
    def evaluate_skill(self, skill_path, user_answers):
        sub_skill = self.skill_tree_manager.get_skill_by_path(skill_path)
        if not sub_skill:
            return 0, []
        
        correct_count = 0
        feedback = []
        
        for quiz in sub_skill.quiz:
            user_answer = user_answers.get(quiz.id)
            is_correct = user_answer == quiz.correct_answer
            if is_correct:
                correct_count += 1
            feedback.append({
                "question": quiz.question,
                "user_answer": user_answer,
                "correct_answer": quiz.correct_answer,
                "is_correct": is_correct
            })
        
        score = int((correct_count / len(sub_skill.quiz)) * 100) if sub_skill.quiz else 0
        return score, feedback

class ProgressTrackingService:
    def __init__(self, data_file: str = "data/user_progress.json"):
        self.data_file = data_file
        self.user_progress = {}
        self._load_data()
    
    def _load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    self.user_progress = data.get("user_progress", {})
                except json.JSONDecodeError:
                    self.user_progress = {}
    
    def save_data(self):
        data = {"user_progress": self.user_progress}
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_user_progress(self, user_id):
        if user_id not in self.user_progress:
            self.user_progress[user_id] = {
                "user_id": user_id,
                "skills": {},
                "recommended_competitions": []
            }
        return self.user_progress[user_id]
    
    def update_skill_progress(self, user_id, skill_path, progress, completed=False, assessment_score=None, learning_time=None):
        user_progress = self.get_user_progress(user_id)
        if skill_path not in user_progress["skills"]:
            user_progress["skills"][skill_path] = {
                "completed": completed,
                "progress": progress,
                "last_updated": datetime.now().isoformat(),
                "assessment_score": assessment_score,
                "learning_time": learning_time
            }
        else:
            user_progress["skills"][skill_path].update({
                "completed": completed,
                "progress": progress,
                "last_updated": datetime.now().isoformat(),
                "assessment_score": assessment_score if assessment_score is not None else user_progress["skills"][skill_path].get("assessment_score"),
                "learning_time": learning_time if learning_time is not None else user_progress["skills"][skill_path].get("learning_time")
            })
        self.save_data()
    
    def get_skill_progress(self, user_id, skill_path):
        user_progress = self.get_user_progress(user_id)
        return user_progress["skills"].get(skill_path, {
            "completed": False,
            "progress": 0,
            "last_updated": None,
            "assessment_score": None,
            "learning_time": 0
        })
    
    def generate_progress_report(self, user_id):
        user_progress = self.get_user_progress(user_id)
        skills = user_progress["skills"]
        
        total_skills = len(skills)
        completed_skills = sum(1 for skill in skills.values() if skill["completed"])
        total_progress = sum(skill["progress"] for skill in skills.values()) / total_skills if total_skills > 0 else 0
        
        # 计算各领域的进度
        domain_progress = {}
        for skill_path, progress in skills.items():
            domain = skill_path.split(".")[0]
            if domain not in domain_progress:
                domain_progress[domain] = {
                    "total": 0,
                    "completed": 0,
                    "progress": 0
                }
            domain_progress[domain]["total"] += 1
            if progress["completed"]:
                domain_progress[domain]["completed"] += 1
            domain_progress[domain]["progress"] += progress["progress"]
        
        for domain, stats in domain_progress.items():
            if stats["total"] > 0:
                stats["progress"] /= stats["total"]
        
        return {
            "total_skills": total_skills,
            "completed_skills": completed_skills,
            "total_progress": total_progress,
            "domain_progress": domain_progress,
            "recommended_competitions": user_progress["recommended_competitions"]
        }

class CompetitionAssociationService:
    def __init__(self, knowledge_base=None, mapping_file: str = "data/competition_skill_mapping.json"):
        self.knowledge_base = knowledge_base
        self.mapping_file = mapping_file
        self.competition_mapping = CompetitionSkillMapping()
        self._load_data()
    
    def _load_data(self):
        if os.path.exists(self.mapping_file):
            try:
                with open(self.mapping_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for competition_id, info in data.get("competition_skill_mapping", {}).items():
                        self.competition_mapping.add_competition(
                            competition_id,
                            info["name"],
                            info["required_skills"]
                        )
            except json.JSONDecodeError:
                pass
    
    def save_data(self):
        data = {
            "competition_skill_mapping": {
                competition_id: info
                for competition_id, info in self.competition_mapping.competitions.items()
            }
        }
        with open(self.mapping_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_skills_for_competition(self, competition_name):
        # 首先尝试通过名称匹配
        for competition_id, info in self.competition_mapping.competitions.items():
            if competition_name in info["name"]:
                return info["required_skills"]
        
        # 如果没有匹配，返回空列表
        return []
    
    def recommend_skills(self, competition_name):
        skills = self.get_skills_for_competition(competition_name)
        return skills

class LearningPathService:
    def __init__(self, skill_tree_manager, progress_tracking_service):
        self.skill_tree_manager = skill_tree_manager
        self.progress_tracking_service = progress_tracking_service
    
    def generate_learning_path(self, user_id, competition_name=None):
        # 获取用户进度
        user_progress = self.progress_tracking_service.get_user_progress(user_id)
        
        # 如果指定了竞赛，基于竞赛推荐技能
        if competition_name:
            # 这里可以集成CompetitionAssociationService
            # 暂时返回空列表
            return []
        
        # 基于用户进度生成学习路径
        all_skills = []
        for domain in self.skill_tree_manager.get_all_domains():
            for category in domain.categories:
                for skill in category.skills:
                    for sub_skill in skill.sub_skills:
                        skill_path = f"{domain.id}.{category.id}.{skill.id}.{sub_skill.id}"
                        progress = self.progress_tracking_service.get_skill_progress(user_id, skill_path)
                        all_skills.append({
                            "path": skill_path,
                            "name": sub_skill.name,
                            "difficulty": skill.difficulty,
                            "progress": progress["progress"],
                            "completed": progress["completed"]
                        })
        
        # 按进度排序，优先推荐进度低的技能
        sorted_skills = sorted(all_skills, key=lambda x: x["progress"])
        return sorted_skills[:10]  # 返回前10个推荐技能