import os
import json
from datetime import datetime

class SkillDomain:
    def __init__(self, id: str, name: str, description: str):
        self.id = id
        self.name = name
        self.description = description
        self.categories = []
    
    def add_category(self, category):
        self.categories.append(category)
    
    def get_category(self, category_id):
        for category in self.categories:
            if category.id == category_id:
                return category
        return None

class SkillCategory:
    def __init__(self, id: str, name: str, description: str):
        self.id = id
        self.name = name
        self.description = description
        self.skills = []
    
    def add_skill(self, skill):
        self.skills.append(skill)
    
    def get_skill(self, skill_id):
        for skill in self.skills:
            if skill.id == skill_id:
                return skill
        return None

class Skill:
    def __init__(self, id: str, name: str, description: str, difficulty: str, estimated_time: str):
        self.id = id
        self.name = name
        self.description = description
        self.difficulty = difficulty
        self.estimated_time = estimated_time
        self.sub_skills = []
    
    def add_sub_skill(self, sub_skill):
        self.sub_skills.append(sub_skill)
    
    def get_sub_skill(self, sub_skill_id):
        for sub_skill in self.sub_skills:
            if sub_skill.id == sub_skill_id:
                return sub_skill
        return None

class SubSkill:
    def __init__(self, id: str, name: str, description: str):
        self.id = id
        self.name = name
        self.description = description
        self.resources = []
        self.quiz = []
    
    def add_resource(self, resource):
        self.resources.append(resource)
    
    def add_quiz(self, quiz):
        self.quiz.append(quiz)

class Resource:
    def __init__(self, type: str, title: str, url: str):
        self.type = type
        self.title = title
        self.url = url

class Quiz:
    def __init__(self, id: str, question: str, options: list, correct_answer: str):
        self.id = id
        self.question = question
        self.options = options
        self.correct_answer = correct_answer

class LearningProgress:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.skills = {}
        self.recommended_competitions = []
        self.data_file = f"data/user_progress_{user_id}.json"
        self._load_data()
    
    def _load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.skills = data.get("skills", {})
                    self.recommended_competitions = data.get("recommended_competitions", [])
            except json.JSONDecodeError:
                pass
    
    def save_data(self):
        data = {
            "skills": self.skills,
            "recommended_competitions": self.recommended_competitions
        }
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def update_skill_progress(self, skill_path: str, progress: int, completed: bool = False, assessment_score: int = None, learning_time: int = None):
        if skill_path not in self.skills:
            self.skills[skill_path] = {
                "completed": completed,
                "progress": progress,
                "last_updated": datetime.now().isoformat(),
                "assessment_score": assessment_score,
                "learning_time": learning_time
            }
        else:
            self.skills[skill_path].update({
                "completed": completed,
                "progress": progress,
                "last_updated": datetime.now().isoformat(),
                "assessment_score": assessment_score if assessment_score is not None else self.skills[skill_path].get("assessment_score"),
                "learning_time": learning_time if learning_time is not None else self.skills[skill_path].get("learning_time")
            })
        self.save_data()
    
    def get_skill_progress(self, skill_path: str):
        return self.skills.get(skill_path, {
            "completed": False,
            "progress": 0,
            "last_updated": None,
            "assessment_score": None,
            "learning_time": 0
        })

class CompetitionSkillMapping:
    def __init__(self):
        self.competitions = {}
    
    def add_competition(self, competition_id: str, name: str, required_skills: list):
        self.competitions[competition_id] = {
            "name": name,
            "required_skills": required_skills
        }
    
    def get_competition(self, competition_id: str):
        return self.competitions.get(competition_id)
    
    def get_skills_by_competition(self, competition_id: str):
        competition = self.get_competition(competition_id)
        return competition.get("required_skills", []) if competition and competition is not None else []