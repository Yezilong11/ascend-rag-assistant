import os
import streamlit as st

from src.knowledge_base import KnowledgeBase
from src.rag_engine import RAGAssistant

# 页面配置
st.set_page_config(
    page_title="昇腾AI竞赛智能助教",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    /* 全局样式 */
    .main {
        background-color: #f8fafc;
    }

    /* 主标题 */
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(135deg, #1f77b4 0%, #6a5acd 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }

    .subtitle {
        color: #64748b;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    /* 聊天消息样式 */
    .chat-container {
        max-height: 600px;
        overflow-y: auto;
        padding: 1rem 0;
    }

    .chat-message {
        padding: 1rem 1.5rem;
        border-radius: 1rem;
        margin-bottom: 1rem;
        max-width: 85%;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        animation: fadeIn 0.3s ease-in-out;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .user-message {
        background: linear-gradient(135deg, #1f77b4 0%, #4a90d9 100%);
        color: white;
        margin-left: auto;
    }

    .assistant-message {
        background-color: white;
        color: #1e293b;
        margin-right: auto;
        border: 1px solid #e2e8f0;
    }

    .message-avatar {
        font-weight: bold;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }

    /* 来源框 */
    .source-box {
        background-color: #f1f5f9;
        padding: 0.75rem;
        border-radius: 0.5rem;
        font-size: 0.85rem;
        color: #475569;
        margin-top: 0.5rem;
        border-left: 3px solid #1f77b4;
    }

    /* 侧边栏 */
    .sidebar-section {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    .sidebar-title {
        font-size: 1.1rem;
        font-weight: bold;
        color: #1e293b;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* 状态指示器 */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
    }

    .status-ready {
        background-color: #dcfce7;
        color: #166534;
    }

    .status-not-ready {
        background-color: #fef2f2;
        color: #991b1b;
    }

    /* 输入框 */
    .chat-input-container {
        position: sticky;
        bottom: 0;
        background-color: transparent;
        padding-top: 1rem;
    }

    /* 滚动条美化 */
    ::-webkit-scrollbar {
        width: 6px;
    }

    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 3px;
    }

    ::-webkit-scrollbar-thumb {
        background: #94a3b8;
        border-radius: 3px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #64748b;
    }

    /* 欢迎卡片 */
    .welcome-card {
        background: linear-gradient(135deg, #e0f2fe 0%, #dbeafe 100%);
        border-radius: 1rem;
        padding: 2rem;
        text-align: center;
        margin-bottom: 1rem;
    }

    .welcome-card h3 {
        color: #075985;
        margin-bottom: 1rem;
    }

    .welcome-card p {
        color: #0369a1;
        line-height: 1.6;
    }

    /* 示例问题标签 */
    .example-question {
        display: inline-block;
        background-color: white;
        border: 1px solid #cbd5e1;
        border-radius: 9999px;
        padding: 0.25rem 0.75rem;
        margin: 0.25rem;
        font-size: 0.875rem;
        color: #475569;
        cursor: pointer;
        transition: all 0.2s;
    }

    .example-question:hover {
        border-color: #1f77b4;
        color: #1f77b4;
        transform: scale(1.05);
    }

    /* 按钮样式优化 */
    .stButton > button {
        width: 100%;
        border-radius: 0.5rem;
        font-weight: 500;
        transition: all 0.2s;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(31, 119, 180, 0.35);
    }

    /* 清空按钮 */
    .clear-btn > button {
        background-color: #ef4444;
        color: white;
    }

    .clear-btn > button:hover {
        background-color: #dc2626;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.35);
    }

    /* 重排序配置折叠面板 */
    .reranker-config {
        background-color: #f8fafc;
        border-radius: 0.5rem;
        padding: 0.5rem;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# 初始化session state
if 'assistant' not in st.session_state:
    st.session_state.assistant = None
if 'kb' not in st.session_state:
    st.session_state.kb = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# 页面标题
st.markdown('<p class="main-title">昇腾AI竞赛智能助教 🤖</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">基于RAG技术的全天候竞赛知识助手，为你解答竞赛报名、规则、评分等各类问题</p>', unsafe_allow_html=True)

# 侧边栏 - 知识库管理
with st.sidebar:
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">📚 知识库管理</div>', unsafe_allow_html=True)

    # 初始化知识库
    if st.session_state.kb is None:
        with st.spinner("初始化知识库..."):
            kb = KnowledgeBase()
            
            # 检查是否已有数据，如果没有才自动导入所有竞赛资料
            def auto_ingest_all_data(kb):
                """自动导入所有竞赛资料，只在数据库为空时执行"""
                # 检查集合是否已有数据
                collection = kb.db._collection
                count = collection.count()
                if count > 0:
                    print(f"知识库已有 {count} 个片段，跳过自动导入")
                    return 0, 0

                data_dirs = [
                    "data/常见问题FAQ",
                    "data/报名须知",
                    "data/技术文档",
                    "data/竞赛规则",
                    "data/评分标准"
                ]
                supported_extensions = ['.md', '.txt', '.pdf']
                total_files = 0
                success_count = 0
                
                for data_dir in data_dirs:
                    full_path = os.path.join(os.path.dirname(__file__), data_dir)
                    if not os.path.exists(full_path):
                        continue
                    
                    for root, dirs, files in os.walk(full_path):
                        for file in files:
                            if any(file.endswith(ext) for ext in supported_extensions):
                                file_path = os.path.join(root, file)
                                total_files += 1
                                try:
                                    kb.ingest(file_path)
                                    success_count += 1
                                except Exception:
                                    pass
                
                return total_files, success_count
            
            # 执行自动导入
            total, success = auto_ingest_all_data(kb)
            st.session_state.kb = kb
            
            if total > 0:
                st.success(f"✅ 知识库初始化完成，自动导入了 {success}/{total} 个文件")
            else:
                st.success("✅ 知识库初始化完成，已加载已有数据")

    # 显示知识库状态
    if st.session_state.kb is not None:
        st.markdown('<span class="status-badge status-ready">✅ 知识库已就绪</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-badge status-not-ready">❌ 知识库未就绪</span>', unsafe_allow_html=True)

    st.divider()

    # 文件上传
    uploaded_file = st.file_uploader(
        "上传竞赛资料",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
        help="支持PDF、TXT、Markdown格式"
    )

    if uploaded_file:
        if st.button("📥 添加到知识库", use_container_width=True):
            for file in uploaded_file:
                with st.spinner(f"处理 {file.name}..."):
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
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">🚀 AI引擎控制</div>', unsafe_allow_html=True)

    # 显示AI引擎状态
    if st.session_state.assistant is not None:
        st.markdown('<span class="status-badge status-ready">✅ AI引擎运行中</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-badge status-not-ready">❌ AI引擎未启动</span>', unsafe_allow_html=True)

    st.divider()

    # 模型选择
    available_models = RAGAssistant.get_available_models()
    model_options = [f"{k}: {v['name']}" for k, v in available_models.items()]
    selected_model = st.selectbox(
        "选择模型",
        options=model_options,
        format_func=lambda x: x.split(": ")[1] if ": " in x else x,
        index=0,
        help="选择要使用的大语言模型"
    )

    # 提取model_key
    if ": " in selected_model:
        model_key = selected_model.split(": ")[0]
    else:
        model_key = list(available_models.keys())[0]

    st.divider()

    # ========== 重排序配置区域 ==========
    st.markdown('<div class="sidebar-title">🎯 重排序配置</div>', unsafe_allow_html=True)
    
    # 是否启用重排序
    use_reranker = st.toggle(
        "启用重排序功能",
        value=True,
        help="启用后，系统会先检索更多候选文档，再用重排序模型精排，提升答案质量"
    )
    
    # 重排序模型选择
    available_rerankers = RAGAssistant.get_available_rerankers()
    reranker_options = [f"{k}: {v['name']} ({v['size']})" for k, v in available_rerankers.items()]
    selected_reranker = st.selectbox(
        "重排序模型",
        options=reranker_options,
        format_func=lambda x: x.split(": ")[1] if ": " in x else x,
        index=0,
        disabled=not use_reranker,
        help="选择用于精排的Cross-Encoder模型，bge-reranker-v2-m3效果最佳"
    )
    
    # 提取reranker_key
    if ": " in selected_reranker:
        reranker_key = selected_reranker.split(": ")[0]
    else:
        reranker_key = list(available_rerankers.keys())[0]
    
    # 高级配置（折叠）
    with st.expander("⚙️ 高级配置", expanded=False):
        initial_retrieval_k = st.slider(
            "初始检索数量",
            min_value=3,
            max_value=20,
            value=10,
            step=1,
            disabled=not use_reranker,
            help="先检索这么多候选文档，再让重排序模型精排"
        )
        
        reranker_top_k = st.slider(
            "精排后保留数量",
            min_value=1,
            max_value=5,
            value=3,
            step=1,
            disabled=not use_reranker,
            help="重排序后保留最相关的几个文档喂给大模型"
        )
        
        st.caption(f"💡 流程：检索 {initial_retrieval_k} 个 → 重排序 → 取前 {reranker_top_k} 个 → 生成答案")

    st.divider()

    # 模型下载路径设置
    model_dir = st.text_input(
        "模型下载路径",
        value="./models",
        help="指定模型下载保存的目录路径"
    )

    st.divider()

    # 模型初始化
    if st.button("启动AI引擎", type="primary", use_container_width=True):
        with st.spinner("加载大模型中，请稍候..."):
            st.session_state.assistant = RAGAssistant(
                knowledge_base=st.session_state.kb,
                model_key=model_key,
                model_dir=model_dir,
                use_reranker=use_reranker,
                reranker_model=reranker_key,
                reranker_top_k=reranker_top_k,
                initial_retrieval_k=initial_retrieval_k
            )
        st.success("✅ AI引擎已就绪！")

    # 清空对话按钮
    if st.session_state.chat_history:
        st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
        if st.button("🗑️ 清空对话历史", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # 系统信息
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">ℹ️ 系统信息</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size: 0.85rem; color: #64748b;">
        <b>技术栈:</b><br>
        • RAG + 大语言模型<br>
        • Chroma 向量数据库<br>
        • BGE-Large-ZH 嵌入<br>
        • BGE-Reranker-v2-m3 重排序<br>
        • 流式输出打字机效果<br>
        • ModelScope模型下载<br>
        • 昇腾NPU优化支持
    </div>
    """, unsafe_allow_html=True)
    
    # 显示重排序状态
    if use_reranker:
        st.markdown("""
        <div style="font-size: 0.85rem; color: #1f77b4; margin-top: 0.5rem;">
            ✅ 重排序功能已启用
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 0.5rem;">
            ⚪ 重排序功能未启用
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# 主界面 - 聊天区域
# 显示欢迎卡片
if not st.session_state.chat_history:
    st.markdown("""
    <div class="welcome-card">
        <h3>👋 你好！我是昇腾AI竞赛智能助教</h3>
        <p>我已经预置了近百场大学生竞赛的官方资料，你可以随时向我提问。试试点击下方常见问题，或者在输入框输入你的问题吧！</p>
    </div>
    """, unsafe_allow_html=True)

    # 示例问题
    example_questions = [
        "如何报名西门子杯？",
        "挑战杯的参赛流程是什么？",
        "大唐杯比赛内容是什么？",
        "RoboMaster机甲大师赛参赛条件？",
        "中国国际大学生创新大赛评分标准？"
    ]

    st.markdown("<div style='text-align: center; margin-bottom: 1rem;'><b>💡 常见问题示例</b></div>", unsafe_allow_html=True)
    cols = st.columns(3)
    for i, q in enumerate(example_questions):
        with cols[i % 3]:
            if st.button(q, key=f"example_{i}", use_container_width=True):
                if st.session_state.assistant is not None:
                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": q
                    })
                    with st.spinner("🤔 思考中..."):
                        result = st.session_state.assistant.query(q)
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": result["answer"],
                        "sources": result["sources"]
                    })
                    st.rerun()
                else:
                    st.warning("👈 请先点击侧边栏的「启动AI引擎」按钮")

# 显示聊天历史
chat_container = st.container()
with chat_container:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <div class="message-avatar">👤 你</div>
                <div>{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <div class="message-avatar">🤖 助教</div>
                <div>{msg["content"]}</div>
            """, unsafe_allow_html=True)
            if "sources" in msg and msg["sources"]:
                with st.expander("📖 查看参考来源"):
                    for i, source in enumerate(msg["sources"], 1):
                        # 转换为项目根目录的相对路径
                        abs_path = source["source"]
                        try:
                            rel_path = os.path.relpath(abs_path, os.path.dirname(__file__))
                        except ValueError:
                            # 如果跨盘，只保留文件名
                            rel_path = os.path.basename(abs_path)
                        st.markdown(f"**来源 {i}**: `{rel_path}`")
                        st.markdown(f"<div class='source-box'>{source['content']}...</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 输入框
st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)

if st.session_state.assistant is None:
    st.info("👈 请先点击侧边栏的「启动AI引擎」按钮开始对话", icon="ℹ️")
else:
    question = st.chat_input("请输入您的问题，按回车发送...")

    if question:
        # 立即在聊天区域显示用户消息
        with st.chat_message("user"):
            st.markdown(question)
        
        
        # 添加用户消息
        st.session_state.chat_history.append({
            "role": "user",
            "content": question
        })

        # 流式生成AI回答
        placeholder = st.empty()
        full_response = ""
        
        # 逐步输出
        for token in st.session_state.assistant.query_stream(question):
            full_response += token
            placeholder.markdown(f"""
            <div class="chat-message assistant-message">
                <div class="message-avatar">🤖 助教</div>
                <div>{full_response}▌</div>
            </div>
            """, unsafe_allow_html=True)
        
        # 获取来源信息
        sources = st.session_state.assistant._last_sources
        
        # 保存到聊天历史
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": full_response,
            "sources": sources
        })

        # 清空占位符
        placeholder.empty()
        
        # 重新渲染显示完整对话
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# 页脚
st.divider()
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.9rem;">
    🚀 昇腾AI竞赛伴随式助教系统 | Powered by RAG + LLM + Reranker | 专为昇腾AI生态打造
</div>
""", unsafe_allow_html=True)