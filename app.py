import os

import streamlit as st

from src.knowledge_base import KnowledgeBase
from src.rag_engine import RAGAssistant

# 页面配置
st.set_page_config(
    page_title="昇腾AI竞赛智能助教",
    page_icon="🤖",
    layout="wide"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .source-box {
        background-color: #f0f2f6;
        padding: 0.5rem;
        border-radius: 0.3rem;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# 初始化session state
if 'assistant' not in st.session_state:
    st.session_state.assistant = None
if 'kb' not in st.session_state:
    st.session_state.kb = None

# 页面标题
st.markdown('<p class="main-title">昇腾AI竞赛智能助教 🤖</p>', unsafe_allow_html=True)
st.markdown("基于RAG技术的全天候竞赛知识助手")

# 侧边栏 - 知识库管理
with st.sidebar:
    st.header("📚 知识库管理")

    # 初始化知识库
    if st.session_state.kb is None:
        st.session_state.kb = KnowledgeBase()
        st.success("知识库已初始化")

    # 文件上传
    uploaded_file = st.file_uploader(
        "上传竞赛资料",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True
    )

    if uploaded_file and st.button("📥 添加到知识库"):
        with st.spinner("处理文档中..."):
            for file in uploaded_file:
                # 保存临时文件
                temp_path = f"temp_{file.name}"
                with open(temp_path, "wb") as f:
                    f.write(file.getvalue())

                # 导入知识库
                try:
                    st.session_state.kb.ingest(temp_path)
                    st.success(f"✅ {file.name} 导入成功")
                except Exception as e:
                    st.error(f"❌ {file.name} 导入失败: {str(e)}")
                finally:
                    # 清理临时文件
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

    st.divider()

    # 模型初始化
    if st.button("🚀 启动AI引擎"):
        with st.spinner("加载大模型中，请稍候..."):
            st.session_state.assistant = RAGAssistant(st.session_state.kb)
        st.success("AI引擎已就绪！")

# 主界面 - 问答区域
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("💬 智能问答")

    if st.session_state.assistant is None:
        st.info("👈 请先点击侧边栏的「启动AI引擎」按钮")
    else:
        # 用户输入
        question = st.text_input(
            "请输入您的问题：",
            placeholder="例如：如何报名昇腾AI竞赛？"
        )

        if question:
            with st.spinner("思考中..."):
                result = st.session_state.assistant.query(question)

            # 显示答案
            st.markdown("### 📝 回答")
            st.markdown(result["answer"])

            # 显示来源
            if result["sources"]:
                with st.expander("📖 参考来源"):
                    for i, source in enumerate(result["sources"], 1):
                        st.markdown(f"**来源 {i}**: {source['source']}")
                        st.markdown(
                            f"<div class='source-box'>{source['content']}...</div>",
                            unsafe_allow_html=True
                        )

with col2:
    st.subheader("📊 系统状态")

    # 显示当前状态
    status = {
        "知识库": "✅ 已连接" if st.session_state.kb else "❌ 未初始化",
        "AI引擎": "✅ 运行中" if st.session_state.assistant else "❌ 未启动",
    }

    for key, value in status.items():
        st.metric(key, value)

# 页脚
st.divider()
st.markdown("<center>🚀 昇腾AI竞赛伴随式助教系统 | Powered by RAG + LLM</center>", unsafe_allow_html=True)
