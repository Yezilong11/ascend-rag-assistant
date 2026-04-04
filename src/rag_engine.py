import os
import warnings
import threading

import torch
from langchain_classic.chains.retrieval_qa.base import RetrievalQA
from langchain_community.llms import HuggingFacePipeline
from langchain_core.prompts import PromptTemplate
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer, pipeline, TextIteratorStreamer

# ModelScope支持
try:
    from modelscope import snapshot_download
    MODELSCOPE_AVAILABLE = True
except ImportError:
    MODELSCOPE_AVAILABLE = False

# 重排序依赖
try:
    from sentence_transformers import CrossEncoder
    RERANKER_AVAILABLE = True
except ImportError:
    RERANKER_AVAILABLE = False
    print("⚠️ 未安装sentence-transformers，重排序功能不可用。请运行: pip install sentence-transformers")

warnings.filterwarnings("ignore")


# 预定义模型配置
PREDEFINED_MODELS = {
    "qwen2-1.5b": {
        "repo_id": "Qwen/Qwen2-1.5B-Instruct",
        "name": "Qwen2-1.5B",
        "description": "标准版，质量最好",
    },
    "qwen2-0.5b": {
        "repo_id": "Qwen/Qwen2-0.5B-Instruct",
        "name": "Qwen2-0.5B",
        "description": "最快，适合CPU",
    },
    "chatglm3-6b": {
        "repo_id": "THUDM/chatglm3-6b",
        "name": "ChatGLM3-6B",
        "description": "大模型，质量更好",
    }
}


# 预定义重排序模型配置
PREDEFINED_RERANKERS = {
    "bge-reranker-v2-m3": {
        "repo_id": "BAAI/bge-reranker-v2-m3",
        "name": "BGE-Reranker-v2-m3",
        "description": "推荐，多语言支持，效果最佳",
        "size": "~1.2GB"
    },
    "bge-reranker-large": {
        "repo_id": "BAAI/bge-reranker-large",
        "name": "BGE-Reranker-Large",
        "description": "效果好，速度较快",
        "size": "~1.3GB"
    },
    "bge-reranker-base": {
        "repo_id": "BAAI/bge-reranker-base",
        "name": "BGE-Reranker-Base",
        "description": "速度快，效果良好",
        "size": "~0.6GB"
    }
}


class Reranker:
    """
    重排序器
    使用 Cross-Encoder 模型对检索结果进行精排
    """
    
    @classmethod
    def get_available_models(cls):
        """获取所有预定义重排序模型列表"""
        return PREDEFINED_RERANKERS
    
    def __init__(self, model_name: str = "bge-reranker-v2-m3", model_dir: str = "./models", device: str = None):
        """
        初始化重排序器
        Args:
            model_name: 模型名称，可选 bge-reranker-v2-m3 / bge-reranker-large / bge-reranker-base
            model_dir: 本地模型存放目录
            device: 设备，None则自动检测
        """
        if not RERANKER_AVAILABLE:
            raise ImportError("sentence-transformers未安装，无法使用重排序功能")
        
        self.model_name = model_name
        
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        # 获取模型配置
        if model_name not in PREDEFINED_RERANKERS:
            print(f"⚠️ 未知的重排序模型: {model_name}，使用默认 bge-reranker-v2-m3")
            model_name = "bge-reranker-v2-m3"
        
        model_config = PREDEFINED_RERANKERS[model_name]
        model_id = model_config["repo_id"]
        local_model_name = model_id.split("/")[-1]
        local_model_path = os.path.join(model_dir, local_model_name)
        
        # 检查本地是否存在
        if os.path.exists(local_model_path):
            model_path = local_model_path
            print(f"正在加载重排序模型: {model_path}...")
        else:
            # 本地不存在，尝试从ModelScope下载
            if MODELSCOPE_AVAILABLE:
                print(f"🔍 本地重排序模型 {local_model_name} 未找到，正在从ModelScope下载...")
                try:
                    # ModelScope的BAAI命名格式
                    modelscope_repo_id = model_id  # BAAI/bge-reranker-v2-m3
                    target_dir = os.path.join(model_dir, local_model_name)
                    snapshot_download(
                        modelscope_repo_id,
                        local_dir=target_dir
                    )
                    model_path = target_dir
                    print(f"✅ ModelScope下载完成，保存到: {model_path}")
                except Exception as e:
                    print(f"⚠️ ModelScope下载失败: {str(e)}，尝试从HuggingFace加载")
                    model_path = model_id
            else:
                model_path = model_id
                print(f"本地模型未找到，正在从HuggingFace下载: {model_id}...")
        
        # 加载 Cross-Encoder
        print(f"正在加载重排序模型到设备: {self.device}")
        self.cross_encoder = CrossEncoder(
            model_path,
            device=self.device,
            trust_remote_code=True
        )
        print(f"✅ 重排序器初始化完成 [{model_config['description']}]")
    
    def rerank(self, query: str, documents: list, top_k: int = 3) -> list:
        """
        对检索结果进行重排序
        Args:
            query: 用户问题
            documents: 原始文档块列表，每个元素是包含 page_content 和 metadata 的对象
            top_k: 返回的最相关文档数量
        Returns:
            重排序后的文档块列表（按相关度降序）
        """
        if not documents:
            return []
        
        # 准备 query-document 对
        pairs = [(query, doc.page_content) for doc in documents]
        
        # 计算相关性分数
        scores = self.cross_encoder.predict(pairs)
        
        # 组合文档和分数
        doc_with_scores = list(zip(documents, scores))
        
        # 按分数降序排序
        doc_with_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 返回 top_k 个文档（仅文档对象）
        reranked_docs = [doc for doc, _ in doc_with_scores[:top_k]]
        
        return reranked_docs


class RAGAssistant:
    """
    RAG智能助教核心引擎
    结合知识检索与大模型生成能力
    支持多模型切换、流式输出、重排序
    """

    @classmethod
    def get_available_models(cls):
        """获取所有预定义模型列表"""
        return PREDEFINED_MODELS

    @classmethod
    def get_available_rerankers(cls):
        """获取所有预定义重排序模型列表"""
        return PREDEFINED_RERANKERS

    def __init__(self, knowledge_base, model_key="qwen2-1.5b", model_dir="./models", 
                 use_reranker: bool = True, reranker_model: str = "bge-reranker-v2-m3",
                 reranker_top_k: int = 3, initial_retrieval_k: int = 10):
        """
        初始化RAG助手
        Args:
            knowledge_base: KnowledgeBase实例
            model_key: 预定义模型key
            model_dir: 本地模型目录
            use_reranker: 是否启用重排序
            reranker_model: 重排序模型名称
            reranker_top_k: 重排序后返回的文档数量
            initial_retrieval_k: 初始检索的文档数量
        """
        self.kb = knowledge_base
        self.model_key = model_key
        self.model = None
        self.tokenizer = None
        self._last_sources = None
        
        # 重排序配置
        self.use_reranker = use_reranker
        self.reranker_top_k = reranker_top_k
        self.initial_retrieval_k = initial_retrieval_k
        self.reranker = None
        
        # 获取模型配置
        model_config = PREDEFINED_MODELS[model_key]
        model_id = model_config["repo_id"]

        # 优先使用本地模型
        local_model_name = model_id.split("/")[-1]
        local_model_path = os.path.join(model_dir, local_model_name)

        if os.path.exists(local_model_path):
            model_path = local_model_path
            print(f"正在加载本地模型: {model_path}...")
        else:
            # 本地不存在，尝试从ModelScope下载
            if MODELSCOPE_AVAILABLE:
                print(f"🔍 本地模型 {local_model_name} 未找到，正在从ModelScope下载...")
                try:
                    # ModelScope的Qwen命名格式修正
                    if model_id.startswith("Qwen/"):
                        modelscope_repo_id = model_id.replace("Qwen/", "qwen/")
                    else:
                        modelscope_repo_id = model_id
                    # 确保下载到项目的models文件夹
                    target_dir = os.path.join(model_dir, local_model_name)
                    snapshot_download(
                        modelscope_repo_id,
                        local_dir=target_dir
                    )
                    model_path = target_dir
                    print(f"✅ ModelScope下载完成，保存到: {model_path}")
                except Exception as e:
                    print(f"⚠️ ModelScope下载失败: {str(e)}，回退到HuggingFace")
                    model_path = model_id
            else:
                model_path = model_id
                print(f"本地模型未找到，正在从HuggingFace下载: {model_id}...")

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            trust_remote_code=True
        )

        # 加载配置
        config = AutoConfig.from_pretrained(
            model_path,
            trust_remote_code=True
        )

        # 普通加载
        print("🔍 使用原始模型加载")
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            config=config,
            trust_remote_code=True,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        )

        # 修复模型缺少的属性
        if not hasattr(self.model, 'all_tied_weights_keys'):
            self.model.all_tied_weights_keys = set()

        # 移动到设备
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = self.model.to(device)

        # 修复pipeline的device参数
        if torch.cuda.is_available():
            device_id = 0
        else:
            device_id = -1

        # 创建生成pipeline
        self.pipeline_obj = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            max_new_tokens=256,  # 限制生成长度，提升速度
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.1,
            device=device_id,
            do_sample=True
        )

        llm = HuggingFacePipeline(pipeline=self.pipeline_obj)

        # 初始化重排序器（如果启用）
        if self.use_reranker and RERANKER_AVAILABLE:
            try:
                self.reranker = Reranker(
                    model_name=reranker_model,
                    model_dir=model_dir,
                    device=device
                )
                print(f"✅ 已启用重排序功能，模型: {reranker_model}，精排后保留 {reranker_top_k} 个文档")
            except Exception as e:
                print(f"⚠️ 重排序器加载失败: {str(e)}，将不使用重排序")
                self.use_reranker = False
                self.reranker = None
        else:
            self.use_reranker = False
            self.reranker = None

        # 自定义Prompt模板
        template = """基于以下检索到的相关信息，回答用户的问题。

【重要规则】
1. 只使用与问题直接相关的信息
2. 不要罗列多个不相关的Q&A条目
3. 如果信息不足，直接告知用户缺少哪些具体信息
4. 回答要简洁、直接、不废话

相关信息：
{context}

用户问题：{question}

请提供专业、准确的回答："""

        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )

        # 创建RAG链（使用自定义检索器，支持重排序）
        self._init_qa_chain(llm, prompt)
        
        print(f"✅ RAG引擎初始化完成 [{model_config['name']}]")

    def _init_qa_chain(self, llm, prompt):
        """
        初始化 QA 链，支持重排序
        """
        from langchain_core.retrievers import BaseRetriever
        from langchain_core.callbacks import CallbackManagerForRetrieverRun
        from typing import List
        from langchain_core.documents import Document

        # 定义一个符合 LangChain 标准的检索器
        class RerankCompatibleRetriever(BaseRetriever):
            """自定义检索器，兼容 LangChain BaseRetriever，支持重排序"""
            rag_assistant: 'RAGAssistant'
            
            class Config:
                arbitrary_types_allowed = True

            def _get_relevant_documents(
                self, query: str, *, run_manager: CallbackManagerForRetrieverRun
            ) -> List[Document]:
                # 1. 初步检索（获取更多候选）
                docs = self.rag_assistant.kb.similarity_search(
                    query, 
                    k=self.rag_assistant.initial_retrieval_k
                )
                
                # 2. 重排序（如果启用）
                if self.rag_assistant.use_reranker and self.rag_assistant.reranker:
                    docs = self.rag_assistant.reranker.rerank(
                        query, 
                        docs, 
                        top_k=self.rag_assistant.reranker_top_k
                    )
                else:
                    # 没有重排序，直接取前 top_k
                    docs = docs[:self.rag_assistant.reranker_top_k]
                
                # 保存检索结果，供后续使用
                self.rag_assistant._last_reranked_docs = docs
                return docs
        
        # 创建自定义检索器实例
        custom_retriever = RerankCompatibleRetriever(rag_assistant=self)
        
        # 创建 QA 链
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=custom_retriever,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )
        
        # 初始化存储最后检索文档的变量
        self._last_reranked_docs = []

    def query(self, question: str) -> dict:
        """
        完整问答，返回完整结果
        Args:
            question: 用户问题
        Returns:
            包含答案和来源的字典
        """
        try:
            # 清空上次的检索结果
            self._last_reranked_docs = []
            
            result = self.qa_chain({"query": question})
            
            # 获取来源（使用重排序后的文档）
            source_docs = self._last_reranked_docs if self._last_reranked_docs else result["source_documents"]
            
            return {
                "answer": result["result"],
                "sources": [
                    {
                        "content": doc.page_content[:200],
                        "source": doc.metadata.get("source", "未知")
                    }
                    for doc in source_docs
                ]
            }
        except Exception as e:
            return {
                "answer": f"处理问题时出错: {str(e)}",
                "sources": []
            }

    def query_stream(self, question: str):
        """
        流式问答，逐token返回生成结果
        Args:
            question: 用户问题
        Yields:
            逐字生成回答片段
        """
        # 清空上次的检索结果
        self._last_reranked_docs = []
        
        # 1. 初步检索（获取更多候选）
        docs = self.kb.similarity_search(question, k=self.initial_retrieval_k)
        
        # 2. 重排序（如果启用）
        if self.use_reranker and self.reranker:
            docs = self.reranker.rerank(question, docs, top_k=self.reranker_top_k)
        else:
            docs = docs[:self.reranker_top_k]
        
        # 保存来源信息
        self._last_reranked_docs = docs
        self._last_sources = [
            {
                "content": doc.page_content[:200],
                "source": doc.metadata.get("source", "未知")
            }
            for doc in docs
        ]
        
        # 构建上下文
        context = "\n\n".join([doc.page_content for doc in docs])

        # 构建Prompt
        template = """基于以下检索到的相关信息，回答用户的问题。
如果无法从信息中找到答案，请明确告知。

相关信息：
{context}

用户问题：{question}

请提供专业、准确的回答："""

        prompt_text = template.format(context=context, question=question)

        # Tokenize
        inputs = self.tokenizer([prompt_text], return_tensors="pt")
        if torch.cuda.is_available():
            inputs = inputs.to("cuda")

        # 创建streamer
        streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True, skip_special_tokens=True)

        # Generation kwargs
        generation_kwargs = dict(
            inputs,
            streamer=streamer,
            max_new_tokens=256,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.1,
            do_sample=True
        )

        # 在后台线程生成
        thread = threading.Thread(target=self.model.generate, kwargs=generation_kwargs)
        thread.start()

        # 逐步返回
        for new_text in streamer:
            yield new_text

        thread.join()