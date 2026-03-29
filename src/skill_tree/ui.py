import streamlit as st
from .services import SkillAssessmentService

def render_skill_tree(skill_tree_manager, progress_service, user_id):
    st.markdown("### 技能树")
    
    domains = skill_tree_manager.get_all_domains()
    
    for domain in domains:
        with st.expander(f"📚 {domain.name}"):
            st.markdown(f"**描述**：{domain.description}")
            
            for category in domain.categories:
                with st.expander(f"📋 {category.name}"):
                    st.markdown(f"**描述**：{category.description}")
                    
                    for skill in category.skills:
                        with st.expander(f"💡 {skill.name}"):
                            st.markdown(f"**描述**：{skill.description}")
                            st.markdown(f"**难度**：{skill.difficulty}")
                            st.markdown(f"**预计学习时间**：{skill.estimated_time}")
                            
                            for sub_skill in skill.sub_skills:
                                skill_path = f"{domain.id}.{category.id}.{skill.id}.{sub_skill.id}"
                                progress = progress_service.get_skill_progress(user_id, skill_path)
                                
                                with st.expander(f"🎯 {sub_skill.name}"):
                                    st.markdown(f"**描述**：{sub_skill.description}")
                                    st.progress(progress["progress"] / 100)
                                    
                                    if progress["completed"]:
                                        st.success("✅ 已完成")
                                    
                                    if progress["assessment_score"]:
                                        st.markdown(f"**评估得分**：{progress['assessment_score']}")
                                    
                                    if progress["learning_time"]:
                                        st.markdown(f"**学习时间**：{progress['learning_time']} 小时")
                                    
                                    # 学习资源
                                    if sub_skill.resources:
                                        st.markdown("#### 学习资源")
                                        for resource in sub_skill.resources:
                                            st.markdown(f"- [{resource.title}]({resource.url}) ({resource.type})")
                                    
                                    # 自测题
                                    if sub_skill.quiz:
                                        st.markdown("#### 自测题")
                                        if st.button(f"开始评估 {sub_skill.name}", key=skill_path):
                                            render_quiz(sub_skill, skill_path, progress_service, user_id, skill_tree_manager)

def render_quiz(sub_skill, skill_path, progress_service, user_id, skill_tree_manager):
    st.markdown(f"### {sub_skill.name} - 自测题")
    
    quiz_state_key = f"quiz_state_{skill_path}"
    if quiz_state_key not in st.session_state:
        st.session_state[quiz_state_key] = {}
    
    user_answers = {}
    for quiz in sub_skill.quiz:
        st.markdown(f"**{quiz.question}**")
        if quiz.id not in st.session_state[quiz_state_key]:
            st.session_state[quiz_state_key][quiz.id] = None
        
        user_answer = st.radio(
            "选择答案",
            quiz.options,
            key=f"quiz_{quiz.id}",
            index=quiz.options.index(st.session_state[quiz_state_key][quiz.id]) if st.session_state[quiz_state_key][quiz.id] in quiz.options else None
        )
        st.session_state[quiz_state_key][quiz.id] = user_answer
        user_answers[quiz.id] = user_answer
        st.divider()
    
    if st.button("提交答案"):
        assessment_service = SkillAssessmentService(skill_tree_manager)
        score, feedback = assessment_service.evaluate_skill(skill_path, user_answers)
        
        st.markdown(f"### 评估结果")
        st.markdown(f"**得分**：{score}分")
        
        if score >= 80:
            st.success("🎉 表现优秀！")
        elif score >= 60:
            st.info("💪 表现良好，继续努力！")
        else:
            st.warning("⚠️ 需要加强练习！")
        
        st.markdown("### 答题反馈")
        for i, item in enumerate(feedback):
            st.markdown(f"**问题 {i+1}**：{item['question']}")
            st.markdown(f"**你的答案**：{item['user_answer']}")
            st.markdown(f"**正确答案**：{item['correct_answer']}")
            if item['is_correct']:
                st.success("✅ 回答正确")
            else:
                st.error("❌ 回答错误")
            st.divider()
        
        # 更新学习进度
        progress_service.update_skill_progress(
            user_id,
            skill_path,
            100,
            True,
            score
        )
        st.success("学习进度已更新！")
        
        # 清除答案状态
        if quiz_state_key in st.session_state:
            del st.session_state[quiz_state_key]

def render_progress_tracking(progress_service, user_id):
    st.markdown("### 学习进度")
    
    report = progress_service.generate_progress_report(user_id)
    
    st.markdown(f"**总技能数**：{report['total_skills']}")
    st.markdown(f"**已完成技能**：{report['completed_skills']}")
    st.markdown(f"**总体进度**：{int(report['total_progress'])}%")
    
    st.progress(report['total_progress'] / 100)
    
    st.markdown("### 各领域进度")
    for domain, stats in report['domain_progress'].items():
        st.markdown(f"**{domain}**")
        st.markdown(f"- 总技能数：{stats['total']}")
        st.markdown(f"- 已完成：{stats['completed']}")
        st.markdown(f"- 进度：{int(stats['progress'])}%")
        st.progress(stats['progress'] / 100)
        st.divider()
    
    if report['recommended_competitions']:
        st.markdown("### 推荐竞赛")
        for competition in report['recommended_competitions']:
            st.markdown(f"- {competition}")

def render_competition_association(competition_service):
    st.markdown("### 竞赛技能推荐")
    
    competition_name = st.text_input("输入竞赛名称")
    
    if st.button("获取推荐技能"):
        if competition_name:
            skills = competition_service.recommend_skills(competition_name)
            
            if skills:
                st.markdown("#### 推荐技能")
                for skill in skills:
                    st.markdown(f"- {skill}")
            else:
                st.info("未找到相关技能推荐")
        else:
            st.warning("请输入竞赛名称")