import os
import yaml
import streamlit as st
import requests

from src.knowledge_base import KnowledgeBase
from src.rag_engine import RAGAssistant

# 读取配置文件
config_path = "./config/config.yaml"
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 获取服务端口配置
server_config = config.get('server', {})
web_port = server_config.get('web_port', 8501)
api_port = server_config.get('api_port', 8000)
host = server_config.get('host', '127.0.0.1')

# 技能树API地址
API_BASE = f"http://localhost:{api_port}/api"

# 检查API服务是否已启动
try:
    response = requests.get(f"http://localhost:{api_port}/", timeout=2)
    if response.status_code == 200:
        print(f"✓ 技能树API已连接 (http://localhost:{api_port})")
except requests.exceptions.RequestException:
    print(f"⚠ 技能树API未启动，请先运行: python server.py")
    st.warning(f"⚠ 技能树API服务未启动，请先在另一个终端运行: python server.py")


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
    
    /* 现代化聊天输入框 */
    .modern-input-container {
        width: min(560px, 100%);
        max-width: 560px;
        margin: 0 auto 1rem;
        border-radius: 20px;
        padding: 2px; /* 渐变边框厚度 */
        background: linear-gradient(135deg, #1f77b4, #6a5acd);
        box-shadow: 0 8px 20px rgba(23, 43, 76, 0.2);
    }

    .modern-input-inner {
        background-color: white;
        border-radius: 18px;
        padding: 14px;
        display: flex;
        flex-direction: column;
        gap: 12px;
    }
    
    .input-area {
        position: relative;
        width: 100%;
    }
    
    .input-area textarea {
        width: 100%;
        max-width: 100%;
        border: none;
        resize: none;
        min-height: 40px;
        max-height: 100px;
        height: 40px;
        font-size: 0.95rem;
        line-height: 1.5;
        padding: 10px 12px;
        border-radius: 10px;
        background-color: #f8fafc;
        font-family: inherit;
    }
    
    .input-area textarea:focus {
        outline: none;
        background-color: white;
        box-shadow: 0 0 0 2px rgba(31, 119, 180, 0.1);
    }
    
    .upload-btn {
        background: none;
        border: none;
        cursor: pointer;
        font-size: 1.1rem;
        padding: 6px;
        border-radius: 6px;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .upload-btn:hover {
        background-color: #f1f5f9;
    }
    
    .send-btn {
        background-color: #1f77b4;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        cursor: pointer;
        font-size: 0.875rem;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .send-btn:hover {
        background-color: #1a5688;
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(31, 119, 180, 0.2);
    }
    
    .send-btn:disabled {
        background-color: #94a3b8;
        cursor: not-allowed;
        transform: none;
        box-shadow: none;
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

# ========== 初始化 session state ==========
if 'assistant' not in st.session_state:
    st.session_state.assistant = None
if 'kb' not in st.session_state:
    st.session_state.kb = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'preset_question' not in st.session_state:
    st.session_state.preset_question = None
if 'is_loading_model' not in st.session_state:
    st.session_state.is_loading_model = False
if 'is_processing_preset' not in st.session_state:
    st.session_state.is_processing_preset = False
if 'show_upload_window' not in st.session_state:
    st.session_state.show_upload_window = False

# 页面标题
st.markdown('<p class="main-title">昇腾AI竞赛智能助教 🤖</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">基于RAG技术的全天候竞赛知识助手，为你解答竞赛报名、规则、评分等各类问题</p>', unsafe_allow_html=True)

# 侧边栏 - 导航菜单
with st.sidebar:
    # 导航选项
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">🚀 功能导航</div>', unsafe_allow_html=True)
    
    # 使用radio创建导航选择
    nav_option = st.radio(
        "选择功能",
        options=["💬 智能问答", "🌳 技能树"],
        index=0,
        key="nav_option",
        horizontal=False
    )
    st.markdown('</div>', unsafe_allow_html=True)

# 侧边栏 - 知识库管理
with st.sidebar:
    # 知识库管理部分
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">📚 知识库管理</div>', unsafe_allow_html=True)

    # 初始化知识库
    if st.session_state.kb is None:
        with st.spinner("初始化知识库..."):
            kb = KnowledgeBase()
            
            def auto_ingest_all_data(kb):
                """自动导入所有竞赛资料，只在数据库为空时执行"""
                # 检查知识库是否为空
                try:
                    # 尝试访问Chroma数据库的collection
                    collection = kb.db._collection
                    count = collection.count()
                    if count > 0:
                        print(f"知识库已有 {count} 个片段，跳过自动导入")
                        return 0, 0
                except AttributeError:
                    # 对于SimpleMemoryDB，检查documents属性
                    if hasattr(kb.db, 'documents') and len(kb.db.documents) > 0:
                        print(f"知识库已有 {len(kb.db.documents)} 个片段，跳过自动导入")
                        return 0, 0
                except Exception as e:
                    print(f"检查知识库状态时出错: {str(e)}")
                    # 继续执行导入

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

    # 上传功能已移至主界面的+按钮
    st.markdown('</div>', unsafe_allow_html=True)

# 侧边栏 - AI引擎控制
with st.sidebar:
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">🚀 AI引擎控制</div>', unsafe_allow_html=True)

    # 显示AI引擎状态
    if st.session_state.assistant is not None:
        st.markdown('<span class="status-badge status-ready">✅ AI引擎运行中</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-badge status-not-ready">❌ AI引擎未启动</span>', unsafe_allow_html=True)

    # 启动AI引擎按钮
    if st.session_state.assistant is None:
        button_disabled = st.session_state.is_loading_model
        if st.button("🚀 启动AI引擎", type="primary", use_container_width=True, disabled=button_disabled):
            st.session_state.is_loading_model = True
            with st.spinner("加载大模型中，请稍候..."):
                try:
                    # 确保model_key已初始化
                    if 'model_key' not in st.session_state or st.session_state.model_key is None:
                        available_models = RAGAssistant.get_available_models()
                        if available_models:
                            st.session_state.model_key = list(available_models.keys())[0]
                    
                    st.session_state.assistant = RAGAssistant(
                        knowledge_base=st.session_state.kb,
                        model_key=st.session_state.model_key,
                        model_dir=st.session_state.model_dir,
                        use_reranker=st.session_state.use_reranker,
                        reranker_model=st.session_state.reranker_key,
                        reranker_top_k=st.session_state.reranker_top_k,
                        initial_retrieval_k=st.session_state.initial_retrieval_k
                    )
                    st.success("✅ AI引擎已就绪！")
                except Exception as e:
                    st.error(f"❌ 模型加载失败: {str(e)}")
                finally:
                    st.session_state.is_loading_model = False
                st.rerun()

    st.divider()

    # ========== 重排序配置区域 ==========
    st.markdown('<div class="sidebar-title">🎯 重排序配置</div>', unsafe_allow_html=True)
    
    use_reranker = st.toggle(
        "启用重排序功能",
        value=True,
        help="启用后，系统会先检索更多候选文档，再用重排序模型精排，提升答案质量",
        disabled=st.session_state.is_loading_model  # 加载时禁用
    )
    
    available_rerankers = RAGAssistant.get_available_rerankers()
    reranker_options = [f"{k}: {v['name']} ({v['size']})" for k, v in available_rerankers.items()]
    selected_reranker = st.selectbox(
        "重排序模型",
        options=reranker_options,
        format_func=lambda x: x.split(": ")[1] if ": " in x else x,
        index=0,
        disabled=not use_reranker or st.session_state.is_loading_model,
        help="选择用于精排的Cross-Encoder模型，bge-reranker-v2-m3效果最佳"
    )
    
    if ": " in selected_reranker:
        reranker_key = selected_reranker.split(": ")[0]
    else:
        reranker_key = list(available_rerankers.keys())[0]
    
    with st.expander("⚙️ 高级配置", expanded=False):
        initial_retrieval_k = st.slider(
            "初始检索数量",
            min_value=3,
            max_value=20,
            value=10,
            step=1,
            disabled=not use_reranker or st.session_state.is_loading_model,
            help="先检索这么多候选文档，再让重排序模型精排"
        )
        
        reranker_top_k = st.slider(
            "精排后保留数量",
            min_value=1,
            max_value=5,
            value=3,
            step=1,
            disabled=not use_reranker or st.session_state.is_loading_model,
            help="重排序后保留最相关的几个文档喂给大模型"
        )
        
        st.caption(f"💡 流程：检索 {initial_retrieval_k} 个 → 重排序 → 取前 {reranker_top_k} 个 → 生成答案")
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # 模型下载路径设置
    model_dir = st.text_input(
        "模型下载路径",
        value="./models",
        help="指定模型下载保存的目录路径",
        disabled=st.session_state.is_loading_model  # 加载时禁用
    )

    # 保存配置到session state
    st.session_state.use_reranker = use_reranker
    st.session_state.selected_reranker = selected_reranker
    st.session_state.reranker_key = reranker_key
    st.session_state.initial_retrieval_k = initial_retrieval_k
    st.session_state.reranker_top_k = reranker_top_k
    st.session_state.model_dir = model_dir

    st.markdown('</div>', unsafe_allow_html=True)

# 侧边栏 - 系统信息
with st.sidebar:
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
    
    if 'use_reranker' in locals() or 'use_reranker' in globals():
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

# ========== 主界面 - 智能问答 ==========
if nav_option == "💬 智能问答":

    
    # 处理预制问题（在显示聊天历史和欢迎卡片之前处理）
    if st.session_state.preset_question and st.session_state.assistant is not None and not st.session_state.is_processing_preset:
        st.session_state.is_processing_preset = True
        question = st.session_state.preset_question
        st.session_state.preset_question = None
        
        # 添加用户消息到历史
        st.session_state.chat_history.append({
            "role": "user",
            "content": question
        })
        
        # 立即重新渲染以显示用户消息
        st.rerun()

    # 显示欢迎卡片（仅在无历史时）
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
        
        # 预制问题按钮（带防误触）
        button_disabled = st.session_state.is_processing_preset or st.session_state.assistant is None
        for i, q in enumerate(example_questions):
            with cols[i % 3]:
                if st.button(q, key=f"example_{i}", use_container_width=True, disabled=button_disabled):
                    if st.session_state.assistant is not None:
                        st.session_state.preset_question = q
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
                            abs_path = source["source"]
                            try:
                                rel_path = os.path.relpath(abs_path, os.path.dirname(__file__))
                            except ValueError:
                                rel_path = os.path.basename(abs_path)
                            st.markdown(f"**来源 {i}**: `{rel_path}`")
                            st.markdown(f"<div class='source-box'>{source['content']}...</div>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        # 如果正在处理中，显示"思考中……"提示
        if st.session_state.is_processing_preset:
            st.markdown("""
            <div class="chat-message assistant-message" style="opacity: 0.7;">
                <div class="message-avatar">🤖 助教</div>
                <div>思考中……</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # 输入框
    st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)

    if st.session_state.assistant is None:
        st.info("👈 请先点击侧边栏的「启动AI引擎」按钮开始对话", icon="ℹ️")
    else:
        # 上传竞赛资料模态窗口
        if st.session_state.show_upload_window:
            # 添加模态窗口样式
            st.markdown("""
            <style>
                .modal-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background-color: rgba(0, 0, 0, 0.5);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    z-index: 1000;
                }
                .modal-content {
                    background-color: white;
                    border-radius: 12px;
                    padding: 2rem;
                    width: 90%;
                    max-width: 600px;
                    max-height: 80vh;
                    overflow-y: auto;
                    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
                    animation: modalFadeIn 0.3s ease-in-out;
                }
                @keyframes modalFadeIn {
                    from { opacity: 0; transform: translateY(-20px); }
                    to { opacity: 1; transform: translateY(0); }
                }
            </style>
            """, unsafe_allow_html=True)
            
            # 创建模态窗口
            st.markdown('<div class="modal-overlay" id="uploadModal">', unsafe_allow_html=True)
            st.markdown('<div class="modal-content">', unsafe_allow_html=True)
            
            # 添加关闭按钮和标题
            st.markdown("### 📤 上传竞赛资料")
            
            # 上传文件区域
            uploaded_files = st.file_uploader(
                "选择要上传的文件",
                type=["pdf", "txt", "md"],
                accept_multiple_files=True,
                help="支持PDF、TXT、Markdown格式"
            )
            
            if uploaded_files:
                if st.button("📥 添加到知识库", key="add_to_kb", use_container_width=True):
                    for file in uploaded_files:
                        with st.spinner(f"处理 {file.name}..."):
                            temp_path = f"temp_{file.name}"
                            with open(temp_path, "wb") as f:
                                f.write(file.getvalue())

                            try:
                                st.session_state.kb.ingest(temp_path)
                                st.success(f"✅ {file.name} 导入成功")
                            except Exception as e:
                                st.error(f"❌ {file.name} 导入失败: {str(e)}")
                            finally:
                                if os.path.exists(temp_path):
                                    os.remove(temp_path)
            
            # 添加关闭按钮
            if st.button("关闭", key="close_upload_window", use_container_width=True):
                st.session_state.show_upload_window = False
            
            st.markdown('</div>', unsafe_allow_html=True)  # 结束modal-content
            st.markdown('</div>', unsafe_allow_html=True)  # 结束modal-overlay
            
            # 添加点击外部关闭的逻辑
            st.markdown("""
            <script>
                // 点击模态窗口外部关闭
                document.addEventListener('click', function(e) {
                    const modalOverlay = document.getElementById('uploadModal');
                    const modalContent = modalOverlay.querySelector('.modal-content');
                    if (modalOverlay && !modalContent.contains(e.target)) {
                        // 触发关闭按钮的点击事件
                        const closeButton = document.querySelector('button[data-testid="stButton"]');
                        if (closeButton && closeButton.textContent.includes('关闭')) {
                            closeButton.click();
                        }
                    }
                });
            </script>
            """, unsafe_allow_html=True)
        
        # 现代化聊天输入框组件（统一渐变边框）
        st.markdown('<div class="modern-input-container">', unsafe_allow_html=True)
        st.markdown('<div class="modern-input-inner">', unsafe_allow_html=True)

        # 中间输入区域
        st.markdown('<div class="input-area">', unsafe_allow_html=True)
        question = st.text_area(
            "",
            height=40,
            max_chars=1000,
            disabled=st.session_state.is_processing_preset,
            key="user_input",
            placeholder="请输入您的问题，按回车发送"
        )
        st.markdown('</div>', unsafe_allow_html=True)  # 结束input-area

        st.markdown("""
        <script>
            const inputArea = document.querySelector('textarea[data-testid="stTextArea"]');
            if (inputArea) {
                inputArea.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        const sendButton = Array.from(document.querySelectorAll('button')).find(btn => btn.innerText.trim().includes('发送'));
                        if (sendButton) {
                            sendButton.click();
                        }
                    }
                });
            }
        </script>
        """, unsafe_allow_html=True)

        # 底部操作按钮（嵌入到输入框内部）
        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            if st.button("上传竞赛资料", key="upload_button"):
                st.session_state.show_upload_window = True

        with col2:
            available_models = RAGAssistant.get_available_models()
            model_options = [f"{k}: {v['name']}" for k, v in available_models.items()]

            for i, option in enumerate(model_options):
                if "deepseek-R1" in option:
                    model_options[i] = option.replace("deepseek-R1模型", "Qwen2-1.5b模型")

            selected_model = st.selectbox(
                "",
                options=model_options,
                format_func=lambda x: x.split(": ")[1] if ": " in x else x,
                index=0,
                disabled=st.session_state.is_loading_model or st.session_state.is_processing_preset,
                label_visibility="collapsed"
            )
            st.session_state.selected_model = selected_model

            if ": " in selected_model:
                model_key = selected_model.split(": ")[0]
            else:
                model_key = list(available_models.keys())[0]

            if "deepseek-R1" in model_key:
                model_key = "qwen2-1.5b"

            st.session_state.model_key = model_key

        with col3:
            send_button = st.button("发送", disabled=st.session_state.is_processing_preset)

        st.markdown('</div>', unsafe_allow_html=True)  # 结束modern-input-inner
        st.markdown('</div>', unsafe_allow_html=True)  # 结束modern-input-container

        # 确保model_key已初始化
        if 'model_key' not in st.session_state or st.session_state.model_key is None:
            available_models = RAGAssistant.get_available_models()
            if available_models:
                st.session_state.model_key = list(available_models.keys())[0]

        # 处理用户输入
        if st.session_state.is_processing_preset:
            # 获取最后一条用户消息
            last_user_msg = None
            for msg in reversed(st.session_state.chat_history):
                if msg["role"] == "user":
                    last_user_msg = msg["content"]
                    break
            
            if last_user_msg and st.session_state.assistant:
                # 生成回答并添加到聊天历史
                try:
                    # 流式生成AI回答
                    full_response = ""
                    for token in st.session_state.assistant.query_stream(last_user_msg):
                        full_response += token
                        # 实时更新聊天历史中的最后一条消息
                        if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "assistant":
                            st.session_state.chat_history[-1]["content"] = full_response
                        else:
                            # 添加新的助手消息
                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "content": full_response
                            })
                        # 立即重新渲染以显示实时更新
                        st.rerun()
                    
                    # 完成生成后添加来源信息
                    sources = st.session_state.assistant._last_sources
                    if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "assistant":
                        st.session_state.chat_history[-1]["sources"] = sources
                except Exception as e:
                    st.error(f"生成回答时出错: {str(e)}")
                finally:
                    st.session_state.is_processing_preset = False
                    st.rerun()
        
        elif (question and send_button):
            st.session_state.is_processing_preset = True
            
            # 添加用户消息到历史
            st.session_state.chat_history.append({
                "role": "user",
                "content": question
            })
            
            # 立即重新渲染以显示用户消息
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ========== 主界面 - 技能树 ==========
elif nav_option == "🌳 技能树":
    # 技能树模块前端界面
    st.markdown("""
    <style>
        /* 技能树样式 */
        .skill-tree-container {
            background-color: white;
            border-radius: 0.75rem;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 1.5rem;
        }
        
        .skill-tree-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
        }
        
        .skill-tree-title {
            font-size: 1.25rem;
            font-weight: bold;
            color: #1e293b;
        }
        
        .skill-node {
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 0.5rem;
            padding: 1rem;
            margin-bottom: 0.75rem;
            transition: all 0.2s;
        }
        
        .skill-node:hover {
            border-color: #1f77b4;
            box-shadow: 0 4px 6px rgba(31, 119, 180, 0.1);
        }
        
        .skill-node-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        }
        
        .skill-node-name {
            font-weight: 600;
            color: #1e293b;
        }
        
        .skill-node-level {
            font-size: 0.75rem;
            padding: 0.25rem 0.5rem;
            border-radius: 9999px;
            font-weight: 500;
        }
        
        .level-beginner {
            background-color: #dcfce7;
            color: #166534;
        }
        
        .level-intermediate {
            background-color: #dbeafe;
            color: #1e40af;
        }
        
        .level-advanced {
            background-color: #fce7f3;
            color: #9d174d;
        }
        
        .level-expert {
            background-color: #fef3c7;
            color: #92400e;
        }
        
        .skill-node-description {
            font-size: 0.875rem;
            color: #64748b;
            margin-bottom: 0.75rem;
        }
        
        .skill-node-meta {
            display: flex;
            gap: 1rem;
            font-size: 0.75rem;
            color: #94a3b8;
        }
        
        .skill-relation {
            margin-top: 0.75rem;
            padding-top: 0.75rem;
            border-top: 1px solid #e2e8f0;
        }
        
        .relation-title {
            font-size: 0.875rem;
            font-weight: 500;
            color: #475569;
            margin-bottom: 0.5rem;
        }
        
        .relation-list {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }
        
        .relation-tag {
            background-color: #f1f5f9;
            padding: 0.25rem 0.5rem;
            border-radius: 0.25rem;
            font-size: 0.75rem;
            color: #64748b;
        }
        
        .learning-path {
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 0.5rem;
            padding: 1rem;
            margin-bottom: 0.75rem;
        }
        
        .path-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.75rem;
        }
        
        .path-name {
            font-weight: 600;
            color: #1e293b;
        }
        
        .path-meta {
            display: flex;
            gap: 1rem;
            font-size: 0.75rem;
            color: #64748b;
        }
        
        .path-skills {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.5rem;
        }
        
        .path-skill {
            background-color: #e2e8f0;
            padding: 0.25rem 0.5rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            color: #475569;
        }
        
        /* 表单样式 */
        .form-section {
            background-color: white;
            border-radius: 0.75rem;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 1.5rem;
        }
        
        .form-title {
            font-size: 1.1rem;
            font-weight: bold;
            color: #1e293b;
            margin-bottom: 1.25rem;
        }
        
        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1rem;
        }
        
        .form-group {
            margin-bottom: 1rem;
        }
        
        .form-label {
            font-size: 0.875rem;
            font-weight: 500;
            color: #475569;
            margin-bottom: 0.5rem;
            display: block;
        }
        
        .form-input {
            width: 100%;
            padding: 0.5rem;
            border: 1px solid #e2e8f0;
            border-radius: 0.375rem;
            font-size: 0.875rem;
        }
        
        .form-input:focus {
            outline: none;
            border-color: #1f77b4;
            box-shadow: 0 0 0 3px rgba(31, 119, 180, 0.1);
        }
        
        /* 按钮样式 */
        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 0.5rem 1rem;
            border-radius: 0.375rem;
            font-size: 0.875rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .btn-primary {
            background-color: #1f77b4;
            color: white;
        }
        
        .btn-primary:hover {
            background-color: #1a5688;
            transform: translateY(-1px);
        }
        
        .btn-secondary {
            background-color: #e2e8f0;
            color: #475569;
        }
        
        .btn-secondary:hover {
            background-color: #cbd5e1;
            transform: translateY(-1px);
        }
        
        /* 加载状态 */
        .loading-spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 2px solid rgba(31, 119, 180, 0.3);
            border-radius: 50%;
            border-top-color: #1f77b4;
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
     </style>
""", unsafe_allow_html=True)

# 技能树管理功能
import requests

# 初始化session state
if 'skill_trees' not in st.session_state:
    st.session_state.skill_trees = []
if 'selected_skill_tree' not in st.session_state:
    st.session_state.selected_skill_tree = None
if 'skill_tree_skills' not in st.session_state:
    st.session_state.skill_tree_skills = {}
if 'learning_paths' not in st.session_state:
    st.session_state.learning_paths = {}
    
# 获取技能树列表
def fetch_skill_trees():
    with st.spinner("加载技能树列表..."):
        try:
            response = requests.get(f"{API_BASE}/skill-tree/")
            if response.status_code == 200:
                result = response.json()
                # 确保返回的数据格式正确
                if isinstance(result, dict) and "data" in result:
                    st.session_state.skill_trees = result["data"]
                else:
                    st.session_state.skill_trees = result
                st.success("技能树列表加载成功！")
            else:
                st.error(f"获取技能树列表失败: {response.status_code}")
        except Exception as e:
            st.error(f"获取技能树列表时出错: {str(e)}")
    
# 获取技能树详情
def fetch_skill_tree_detail(skill_tree_id):
    try:
        response = requests.get(f"{API_BASE}/skill-tree/{skill_tree_id}")
        if response.status_code == 200:
            result = response.json()
            # 确保返回的数据格式正确
            if isinstance(result, dict) and "data" in result:
                return result["data"]
            else:
                return result
        else:
            st.error(f"获取技能树详情失败: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"获取技能树详情时出错: {str(e)}")
        return None
    
# 创建技能树
def create_skill_tree(name, description):
    try:
        response = requests.post(
            f"{API_BASE}/skill-tree/",
            json={"name": name, "description": description}
        )
        if response.status_code == 200:
            st.success("技能树创建成功！")
            fetch_skill_trees()
        else:
            st.error(f"创建技能树失败: {response.status_code}")
    except Exception as e:
        st.error(f"创建技能树时出错: {str(e)}")
    
# 添加技能
def add_skill(skill_tree_id, name, description, level, skill_type, learning_time):
    try:
        response = requests.post(
            f"{API_BASE}/skill-tree/{skill_tree_id}/skills",
            json={
                "name": name,
                "description": description,
                "level": level,
                "skill_type": skill_type,
                "learning_time": learning_time
            }
        )
        if response.status_code == 200:
            st.success("技能添加成功！")
            # 刷新技能树详情
            fetch_skill_trees()
        else:
            st.error(f"添加技能失败: {response.status_code}")
    except Exception as e:
        st.error(f"添加技能时出错: {str(e)}")
    
# 建立技能关系
def establish_relation(skill_tree_id, source_skill_id, target_skill_id, relation_type):
    try:
        response = requests.post(
            f"{API_BASE}/skill-tree/{skill_tree_id}/skills/relation",
            json={
                "source_skill_id": source_skill_id,
                "target_skill_id": target_skill_id,
                "relation_type": relation_type
            }
        )
        if response.status_code == 200:
            st.success("技能关系建立成功！")
            # 刷新技能树详情
            fetch_skill_trees()
        else:
            st.error(f"建立技能关系失败: {response.status_code}")
    except Exception as e:
        st.error(f"建立技能关系时出错: {str(e)}")
    
# 生成学习路径
def generate_learning_paths(skill_tree_id):
    try:
        response = requests.post(f"{API_BASE}/skill-tree/{skill_tree_id}/paths/generate")
        if response.status_code == 200:
            st.success("学习路径生成成功！")
            # 刷新技能树详情
            fetch_skill_trees()
        else:
            st.error(f"生成学习路径失败: {response.status_code}")
    except Exception as e:
        st.error(f"生成学习路径时出错: {str(e)}")
    
# 删除技能树
def delete_skill_tree(skill_tree_id):
    try:
        response = requests.delete(f"{API_BASE}/skill-tree/{skill_tree_id}")
        if response.status_code == 200:
            st.success("技能树删除成功！")
            fetch_skill_trees()
            st.session_state.selected_skill_tree = None
        else:
            st.error(f"删除技能树失败: {response.status_code}")
    except Exception as e:
        st.error(f"删除技能树时出错: {str(e)}")
    
# 页面标题
st.markdown('<h2 style="color: #1e293b; margin-bottom: 1.5rem;">🌳 竞赛技能树</h2>', unsafe_allow_html=True)

# 技能树管理区域
with st.expander("📋 技能树管理", expanded=True):
    col1, col2 = st.columns([2, 1])
    
    # 左侧：创建技能树
    with col1:
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<div class="form-title">创建新技能树</div>', unsafe_allow_html=True)
        
        with st.form(key="create_skill_tree_form"):
            name = st.text_input("技能树名称")
            description = st.text_area("技能树描述")
            submit_button = st.form_submit_button("创建技能树", type="primary")
            
            if submit_button:
                if name and description:
                    create_skill_tree(name, description)
                else:
                    st.error("请填写技能树名称和描述")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 右侧：技能树列表
    with col2:
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<div class="form-title">现有技能树</div>', unsafe_allow_html=True)
        
        # 刷新技能树列表
        if st.button("刷新列表"):
            fetch_skill_trees()
        
        # 显示技能树列表
        if st.session_state.skill_trees:
            for skill_tree in st.session_state.skill_trees:
                with st.expander(f"{skill_tree['name']}"):
                    st.write(f"描述: {skill_tree['description']}")
                    st.write(f"版本: {skill_tree['version']}")
                    
                    # 选择技能树
                    if st.button(f"选择", key=f"select_{skill_tree['id']}"):
                        st.session_state.selected_skill_tree = skill_tree
                    
                    # 删除技能树
                    if st.button(f"删除", key=f"delete_{skill_tree['id']}", type="secondary"):
                        delete_skill_tree(skill_tree['id'])
        else:
            st.info("暂无技能树，请创建新技能树")
        st.markdown('</div>', unsafe_allow_html=True)

# 选中技能树后显示详情
if st.session_state.selected_skill_tree:
    skill_tree = st.session_state.selected_skill_tree
    st.markdown(f"""
    <div class="skill-tree-container">
        <div class="skill-tree-header">
            <h3 class="skill-tree-title">{skill_tree['name']}</h3>
            <div>
                <button class="btn btn-primary" onclick="generatePaths('{skill_tree['id']}')">生成学习路径</button>
            </div>
        </div>
        <p style="color: #64748b; margin-bottom: 1.5rem;">{skill_tree['description']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 添加技能区域
    with st.expander("➕ 添加技能", expanded=False):
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<div class="form-title">添加新技能</div>', unsafe_allow_html=True)
         
        with st.form(key="add_skill_form"):
            skill_name = st.text_input("技能名称")
            skill_description = st.text_area("技能描述")
            skill_level = st.selectbox("技能难度", ["beginner", "intermediate", "advanced", "expert"], format_func=lambda x: x.capitalize())
            skill_type = st.selectbox("技能类型", ["technical", "theoretical", "practical", "competition"], format_func=lambda x: x.capitalize())
            learning_time = st.number_input("预估学习时间（小时）", min_value=0, step=1)
            submit_button = st.form_submit_button("添加技能", type="primary")
            
            if submit_button:
                if skill_name and skill_description:
                    add_skill(
                    skill_tree['id'],
                    skill_name,
                    skill_description,
                    skill_level,
                    skill_type,
                    learning_time
                )
            else:
                st.error("请填写技能名称和描述")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 建立技能关系区域
    with st.expander("🔗 建立技能关系", expanded=False):
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<div class="form-title">建立技能关系</div>', unsafe_allow_html=True)
        
        # 获取技能树中的技能列表
    skill_tree_detail = fetch_skill_tree_detail(skill_tree['id'])
    if skill_tree_detail and 'skill_nodes' in skill_tree_detail:
        skills = skill_tree_detail['skill_nodes']
        skill_options = [(skill['id'], skill['name']) for skill in skills.values()]
        
        with st.form(key="establish_relation_form"):
            source_skill = st.selectbox("源技能", options=skill_options, format_func=lambda x: x[1])
            target_skill = st.selectbox("目标技能", options=skill_options, format_func=lambda x: x[1])
            relation_type = st.selectbox("关系类型", ["prerequisite", "related", "advanced"])
            submit_button = st.form_submit_button("建立关系", type="primary")
            
            if submit_button:
                if source_skill[0] != target_skill[0]:
                    establish_relation(
                        skill_tree['id'],
                        source_skill[0],
                        target_skill[0],
                        relation_type
                    )
                else:
                    st.error("源技能和目标技能不能相同")
    else:
        st.info("请先添加技能")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 技能列表区域
    with st.expander("📚 技能列表", expanded=True):
        st.markdown('<div class="skill-tree-container">', unsafe_allow_html=True)
        st.markdown('<div class="skill-tree-title">技能节点</div>', unsafe_allow_html=True)
        
        if skill_tree_detail and 'skill_nodes' in skill_tree_detail:
            skills = skill_tree_detail['skill_nodes']
            for skill_id, skill in skills.items():
                # 难度级别样式
                level_class = f"level-{skill['level'].lower()}"
                
                st.markdown(f"""
                <div class="skill-node">
                    <div class="skill-node-header">
                        <span class="skill-node-name">{skill['name']}</span>
                        <span class="skill-node-level {level_class}">{skill['level']}</span>
                    </div>
                    <div class="skill-node-description">{skill['description']}</div>
                     <div class="skill-node-meta">
                         <span>类型: {skill['type']}</span>
                         <span>学习时间: {skill['learning_time']}小时</span>
                         <span>完成率: {skill['completion_rate']}%</span>
                     </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("暂无技能节点，请添加技能")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 学习路径区域
    with st.expander("🗺️ 学习路径", expanded=True):
        st.markdown('<div class="skill-tree-container">', unsafe_allow_html=True)
        st.markdown('<div class="skill-tree-title">学习路径</div>', unsafe_allow_html=True)
        
        if skill_tree_detail and 'learning_paths' in skill_tree_detail:
            paths = skill_tree_detail['learning_paths']
            if paths:
                for path_id, path in paths.items():
                    # 难度级别样式
                    level_class = f"level-{path['difficulty'].lower()}"
                    
                    st.markdown(f"""
                    <div class="learning-path">
                        <div class="path-header">
                            <span class="path-name">学习路径 {path_id[:8]}</span>
                            <div class="path-meta">
                                <span class="skill-node-level {level_class}">{path['difficulty']}</span>
                                <span>预估时间: {path['estimated_time']}小时</span>
                            </div>
                        </div>
                        <div class="path-skills">
                            {''.join([f'<span class="path-skill">{skill_tree_detail["skill_nodes"][skill_id]["name"]}</span>' for skill_id in path['skill_ids']])}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("暂无学习路径，请生成学习路径")
        else:
            st.info("暂无学习路径，请生成学习路径")
        st.markdown('</div>', unsafe_allow_html=True)

# 初始化时获取技能树列表
if not st.session_state.skill_trees:
    fetch_skill_trees()

# 页脚
st.divider()
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.9rem;">
    🚀 昇腾AI竞赛伴随式助教系统 | Powered by RAG + LLM + Reranker | 专为昇腾AI生态打造
</div>
""", unsafe_allow_html=True)