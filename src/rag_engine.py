import os
import logging
import subprocess
import warnings
import threading
from typing import Optional, List

logger = logging.getLogger(__name__)

import torch
from langchain_classic.chains.retrieval_qa.base import RetrievalQA
try:
    from langchain_huggingface import HuggingFacePipeline
except ImportError:
    from langchain_community.llms import HuggingFacePipeline
from langchain_core.prompts import PromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
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
    logger.warning("未安装sentence-transformers，重排序功能不可用。请运行: pip install sentence-transformers")

warnings.filterwarnings("ignore")


def clean_source_path(source: str) -> str:
    """
    清理 source 路径显示，将临时路径和绝对路径转换为友好的文件名
    Args:
        source: 原始路径字符串
    Returns:
        清理后的友好文件名
    """
    if not source or source == "未知":
        return source
    # 提取文件名（处理正反斜杠）
    filename = source.replace("\\", "/").split("/")[-1]
    return filename


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
    },
    "zilong-1": {
        "repo_id": "yzl111/zilong-1",
        "ms_repo_id": "yzl111/zilong-1",
        "name": "纸龙一号",
        "description": "魔搭社区模型，通过CLI下载",
        "download_method": "cli",
    },
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
            logger.warning("未知的重排序模型: %s，使用默认 bge-reranker-v2-m3", model_name)
            model_name = "bge-reranker-v2-m3"
        
        model_config = PREDEFINED_RERANKERS[model_name]
        model_id = model_config["repo_id"]
        local_model_name = model_id.split("/")[-1]
        local_model_path = os.path.join(model_dir, local_model_name)
        
        # 检查本地是否存在
        if os.path.exists(local_model_path):
            model_path = local_model_path
            logger.info("正在加载重排序模型: %s...", model_path)
        else:
            # 本地不存在，尝试从ModelScope下载
            if MODELSCOPE_AVAILABLE:
                logger.info("本地重排序模型 %s 未找到，正在从ModelScope下载...", local_model_name)
                try:
                    # ModelScope的BAAI命名格式
                    modelscope_repo_id = model_id  # BAAI/bge-reranker-v2-m3
                    target_dir = os.path.join(model_dir, local_model_name)
                    snapshot_download(
                        modelscope_repo_id,
                        local_dir=target_dir
                    )
                    model_path = target_dir
                    logger.info("ModelScope下载完成，保存到: %s", model_path)
                except Exception as e:
                    logger.warning("ModelScope下载失败: %s，尝试从HuggingFace加载", str(e))
                    model_path = model_id
            else:
                model_path = model_id
                logger.info("本地模型未找到，正在从HuggingFace下载: %s...", model_id)
        
        # 加载 Cross-Encoder
        logger.info("正在加载重排序模型到设备: %s", self.device)
        self.cross_encoder = CrossEncoder(
            model_path,
            device=self.device,
            trust_remote_code=True
        )
        logger.info("重排序器初始化完成 [%s]", model_config['description'])
    
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


class RerankCompatibleRetriever(BaseRetriever):
    """
    自定义检索器，兼容 LangChain BaseRetriever，支持重排序。
    通过构造函数接收 RAGAssistant 实例，委托其 _retrieve_and_rerank 方法完成检索与重排序。
    """

    def __init__(self, rag_assistant: 'RAGAssistant', **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, '_rag_assistant', rag_assistant)

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        docs, _ = self._rag_assistant._retrieve_and_rerank(query)
        return docs


class RAGAssistant:
    """
    RAG智能助教核心引擎
    结合知识检索与大模型生成能力
    支持多模型切换、流式输出、重排序
    """

    QA_PROMPT_TEMPLATE = """基于以下检索到的相关信息，回答用户的问题。

【重要规则】
1. 只使用与问题直接相关的信息
2. 不要罗列多个不相关的Q&A条目
3. 如果检索到的信息不足以回答问题，请明确说明
4. 用中文回答

相关信息：
{context}

用户问题：{question}

请提供专业、准确的回答："""

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
        
        # 重排序配置
        self.use_reranker = use_reranker
        self.reranker_top_k = reranker_top_k
        self.initial_retrieval_k = initial_retrieval_k
        self.reranker = None
        
        # 获取模型配置
        model_config = PREDEFINED_MODELS.get(model_key)
        if model_config is None:
            raise ValueError(f"不支持的模型: {model_key}，可选模型: {list(PREDEFINED_MODELS.keys())}")
        model_id = model_config["repo_id"]

        # 优先使用本地模型
        local_model_name = model_id.split("/")[-1]
        local_model_path = os.path.join(model_dir, local_model_name)

        if os.path.exists(local_model_path):
            model_path = local_model_path
            logger.info("正在加载本地模型: %s...", model_path)
        else:
            download_method = model_config.get("download_method", "sdk")
            ms_repo_id = model_config.get("ms_repo_id")
            target_dir = os.path.join(model_dir, local_model_name)

            if not ms_repo_id:
                if model_id.startswith("Qwen/"):
                    ms_repo_id = model_id.replace("Qwen/", "qwen/")
                else:
                    ms_repo_id = model_id

            model_path = None

            if download_method == "cli":
                logger.info("本地模型 %s 未找到，正在通过魔搭CLI下载...", local_model_name)
                try:
                    result = subprocess.run(
                        ["modelscope", "download", "--model", ms_repo_id, "--local_dir", target_dir],
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    model_path = target_dir
                    logger.info("魔搭CLI下载完成，保存到: %s", model_path)
                except FileNotFoundError:
                    logger.warning("魔搭CLI未安装，回退到ModelScope SDK下载...")
                except subprocess.CalledProcessError as e:
                    logger.warning("魔搭CLI下载失败: %s，回退到ModelScope SDK下载...", e.stderr.strip() if e.stderr else str(e))
                except Exception as e:
                    logger.warning("魔搭CLI下载异常: %s，回退到ModelScope SDK下载...", str(e))

            if model_path is None and MODELSCOPE_AVAILABLE:
                logger.info("正在从ModelScope SDK下载...")
                try:
                    snapshot_download(ms_repo_id, local_dir=target_dir)
                    model_path = target_dir
                    logger.info("ModelScope SDK下载完成，保存到: %s", model_path)
                except Exception as e:
                    logger.warning("ModelScope SDK下载失败: %s，回退到HuggingFace", str(e))

            if model_path is None:
                model_path = model_id
                logger.info("回退到HuggingFace在线加载: %s...", model_id)

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
        logger.info("使用原始模型加载")
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

        # 创建生成pipeline
        self.pipeline_obj = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            max_new_tokens=256,  # 限制生成长度，提升速度
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.1,
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
                logger.info("已启用重排序功能，模型: %s，精排后保留 %d 个文档", reranker_model, reranker_top_k)
            except Exception as e:
                logger.warning("重排序器加载失败: %s，将不使用重排序", str(e))
                self.use_reranker = False
                self.reranker = None
        else:
            self.use_reranker = False
            self.reranker = None

        # 使用统一的 Prompt 模板
        prompt = PromptTemplate(
            template=self.QA_PROMPT_TEMPLATE,
            input_variables=["context", "question"]
        )

        # 创建RAG链（使用自定义检索器，支持重排序）
        self._init_qa_chain(llm, prompt)
        
        logger.info("RAG引擎初始化完成 [%s]", model_config['name'])

    def _retrieve_and_rerank(self, question: str) -> tuple:
        """
        共享的检索与重排序逻辑，供 query() 和 query_stream() 复用
        Args:
            question: 用户问题
        Returns:
            (docs, sources) 元组：
              - docs: 重排序后的 Document 对象列表
              - sources: 包含 content 和 metadata 的字典列表
        """
        docs = self.kb.similarity_search(question, k=self.initial_retrieval_k)
        if self.use_reranker and self.reranker:
            docs = self.reranker.rerank(question, docs, top_k=self.reranker_top_k)
        else:
            docs = docs[:self.reranker_top_k]
        sources = [{"content": doc.page_content, "metadata": doc.metadata} for doc in docs]
        return docs, sources

    def _init_qa_chain(self, llm, prompt):
        """
        初始化 QA 链，支持重排序
        """
        # 创建自定义检索器实例（模块级类）
        custom_retriever = RerankCompatibleRetriever(rag_assistant=self)

        # 创建 QA 链
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=custom_retriever,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )

    def query(self, question: str) -> dict:
        """
        完整问答，返回完整结果
        Args:
            question: 用户问题
        Returns:
            包含答案和来源的字典
        Raises:
            ValueError: 模型配置等参数校验失败
            RuntimeError: 问答处理过程中发生错误
        """
        try:
            # 运行 QA 链（检索器内部调用 _retrieve_and_rerank，只执行一次）
            result = self.qa_chain({"query": question})

            # 从 qa_chain 返回的 source_documents 提取来源信息
            source_docs = result.get("source_documents", [])
            formatted_sources = [
                {
                    "content": doc.page_content[:200],
                    "source": clean_source_path(doc.metadata.get("source", "未知"))
                }
                for doc in source_docs
            ]

            # 空检索结果处理
            if not source_docs:
                return {
                    "answer": "抱歉，未找到与您问题相关的信息，请尝试换一种方式提问。",
                    "sources": []
                }

            return {
                "answer": result["result"],
                "sources": formatted_sources
            }
        except ValueError:
            raise  # Re-raise ValueError (from model_key validation etc.)
        except Exception as e:
            logger.error(f"RAG query failed: {e}", exc_info=True)
            raise RuntimeError(f"问答处理失败") from e

    def query_stream(self, question: str):
        """
        流式问答，逐token返回生成结果
        Args:
            question: 用户问题
        Yields:
            逐字生成回答片段，最后以 dict 形式 yield 来源信息
        """
        # 使用共享的检索与重排序逻辑
        docs, sources = self._retrieve_and_rerank(question)

        # 空检索结果处理
        if not docs:
            yield "抱歉，未找到与您问题相关的信息，请尝试换一种方式提问。"
            yield {"type": "sources", "sources": []}
            return

        # 格式化来源信息
        formatted_sources = [
            {
                "content": s["content"][:200],
                "source": clean_source_path(s["metadata"].get("source", "未知"))
            }
            for s in sources
        ]

        # 构建上下文
        context = "\n\n".join([doc.page_content for doc in docs])

        # 使用统一的 Prompt 模板
        prompt_text = self.QA_PROMPT_TEMPLATE.format(context=context, question=question)

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

        # 返回来源信息事件
        yield {"type": "sources", "sources": formatted_sources}
