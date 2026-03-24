import os
import warnings
import threading

import torch
from langchain_classic.chains.retrieval_qa.base import RetrievalQA
from langchain_community.llms import HuggingFacePipeline
from langchain_core.prompts import PromptTemplate
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer, pipeline, TextIteratorStreamer

# 导入重排序模型
try:
    from sentence_transformers import CrossEncoder
    RERANKER_AVAILABLE = True
except ImportError:
    RERANKER_AVAILABLE = False
    print("⚠️ 未安装sentence-transformers，重排序功能不可用")

# ModelScope支持
try:
    from modelscope import snapshot_download
    MODELSCOPE_AVAILABLE = True
except ImportError:
    MODELSCOPE_AVAILABLE = False

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


class Reranker:
    """
    重排序器：对检索到的文档片段进行重新排序
    使用交叉编码器（Cross-Encoder）计算查询与文档的相关性分数
    """
    
    def __init__(self, model_name="BAAI/bge-reranker-base"):
        """
        初始化重排序器
        
        Args:
            model_name: 重排序模型名称
                       可选: "BAAI/bge-reranker-base" (中文优化)
                            "cross-encoder/ms-marco-MiniLM-L-6-v2" (英文)
        """
        if not RERANKER_AVAILABLE:
            raise ImportError("请先安装sentence-transformers: pip install sentence-transformers")
        
        print(f"🚀 加载重排序模型: {model_name}")
        self.model = CrossEncoder(model_name, max_length=512)
        print("✅ 重排序模型加载完成")
    
    def rerank(self, query: str, documents: list, top_k: int = 3) -> list:
        """
        对检索结果进行重排序
        
        Args:
            query: 用户查询
            documents: 检索到的文档列表，每个元素是文档内容字符串
            top_k: 返回前k个最相关的文档
            
        Returns:
            重排序后的文档列表（按相关性从高到低）
        """
        if not documents:
            return []
        
        # 准备查询-文档对
        pairs = [(query, doc) for doc in documents]
        
        # 计算相关性分数
        scores = self.model.predict(pairs)
        
        # 将分数与文档配对并排序
        scored_docs = list(zip(documents, scores))
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        # 返回前top_k个文档
        return [doc for doc, score in scored_docs[:top_k]]
    
    def rerank_with_metadata(self, query: str, documents_with_meta: list, top_k: int = 3) -> list:
        """
        重排序并保留元数据
        
        Args:
            query: 用户查询
            documents_with_meta: 包含元数据的文档列表
                                [{"content": "...", "metadata": {...}}, ...]
            top_k: 返回前k个最相关的文档
            
        Returns:
            重排序后的文档列表（包含元数据和分数）
        """
        if not documents_with_meta:
            return []
        
        # 提取文档内容
        contents = [doc["content"] for doc in documents_with_meta]
        
        # 计算相关性分数
        pairs = [(query, content) for content in contents]
        scores = self.model.predict(pairs)
        
        # 添加分数到元数据
        for doc, score in zip(documents_with_meta, scores):
            doc["relevance_score"] = float(score)
        
        # 按分数排序
        sorted_docs = sorted(documents_with_meta, 
                           key=lambda x: x["relevance_score"], 
                           reverse=True)
        
        return sorted_docs[:top_k]


class RAGAssistant:
    """
    RAG智能助教核心引擎
    结合知识检索与大模型生成能力
    支持多模型切换、流式输出
    """

    @classmethod
    def get_available_models(cls):
        """获取所有预定义模型列表"""
        return PREDEFINED_MODELS

    def __init__(self, knowledge_base, model_key="qwen2-1.5b", model_dir="./models", use_reranker=True):
        """
        初始化RAG助手
        
        Args:
            knowledge_base: KnowledgeBase实例
            model_key: 预定义模型key
            model_dir: 本地模型目录
            use_reranker: 是否启用重排序功能
        """
        self.kb = knowledge_base
        self.model_key = model_key
        self.use_reranker = use_reranker
        self.model = None
        self.tokenizer = None
        self._last_sources = None

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
                    local_model_path = snapshot_download(
                        modelscope_repo_id,
                        local_dir=target_dir
                    )
                    model_path = local_model_path
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
        pipeline_obj = pipeline(
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

        llm = HuggingFacePipeline(pipeline=pipeline_obj)

        # 自定义Prompt模板
        template = """基于以下检索到的相关信息，回答用户的问题。
如果无法从信息中找到答案，请明确告知。

相关信息：
{context}

用户问题：{question}

请提供专业、准确的回答："""

        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )

        # ========== 重排序功能初始化 ==========
        if use_reranker and RERANKER_AVAILABLE:
            print("\n🔍 初始化重排序器...")
            try:
                self.reranker = Reranker()
                print("✅ 重排序器初始化完成")
                
                # 创建支持重排序的自定义检索器
                from langchain.schema import BaseRetriever, Document
                
                class RerankingRetriever(BaseRetriever):
                    """自定义检索器，支持重排序"""
                    
                    def __init__(self, base_retriever, reranker):
                        self.base_retriever = base_retriever
                        self.reranker = reranker
                    
                    def get_relevant_documents(self, query: str):
                        # 1. 基础检索（检索更多文档）
                        docs = self.base_retriever.get_relevant_documents(query)
                        
                        # 2. 准备重排序数据
                        documents_with_meta = []
                        for doc in docs:
                            documents_with_meta.append({
                                "content": doc.page_content,
                                "metadata": doc.metadata
                            })
                        
                        # 3. 重排序
                        reranked = self.reranker.rerank_with_metadata(
                            query=query,
                            documents_with_meta=documents_with_meta,
                            top_k=3  # 最终返回3个
                        )
                        
                        # 4. 转换回Document格式
                        result_docs = []
                        for item in reranked:
                            doc = Document(
                                page_content=item["content"],
                                metadata={
                                    **item["metadata"],
                                    "relevance_score": item["relevance_score"]
                                }
                            )
                            result_docs.append(doc)
                        
                        return result_docs
                
                # 创建基础检索器（检索更多文档）
                base_retriever = self.kb.db.as_retriever(search_kwargs={"k": 10})
                
                # 创建自定义检索器
                custom_retriever = RerankingRetriever(base_retriever, self.reranker)
                
                # 使用自定义检索器
                retriever_to_use = custom_retriever
                print("✅ 已启用重排序功能（检索10个 → 重排序 → 选3个）")
                
            except Exception as e:
                print(f"⚠️ 重排序器初始化失败: {str(e)}，使用普通检索器")
                retriever_to_use = self.kb.db.as_retriever(search_kwargs={"k": 3})
        else:
            # 不使用重排序，直接检索3个文档
            if use_reranker and not RERANKER_AVAILABLE:
                print("⚠️ 重排序功能不可用（未安装sentence-transformers），使用普通检索器")
            retriever_to_use = self.kb.db.as_retriever(search_kwargs={"k": 3})

        # 创建RAG链
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever_to_use,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )

        print(f"✅ RAG引擎初始化完成 [{model_config['name']}]")

    def query(self, question: str) -> dict:
        """
        完整问答，返回完整结果
        Args:
            question: 用户问题
        Returns:
            包含答案和来源的字典
        """
        try:
            result = self.qa_chain({"query": question})
            
            # 格式化输出，包含重排序分数
            sources = []
            for doc in result["source_documents"]:
                source_info = {
                    "content": doc.page_content[:200],
                    "source": doc.metadata.get("source", "未知")
                }
                
                # 如果有重排序分数，添加到输出
                if "relevance_score" in doc.metadata:
                    source_info["relevance_score"] = doc.metadata["relevance_score"]
                
                sources.append(source_info)
            
            return {
                "answer": result["result"],
                "sources": sources
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
        # 先检索知识库（支持重排序）
        if hasattr(self, 'reranker') and self.use_reranker:
            # 使用重排序检索
            from langchain.schema import Document
            
            # 检索更多文档
            docs = self.kb.similarity_search(question, k=10)
            
            # 准备重排序数据
            documents_with_meta = []
            for doc in docs:
                documents_with_meta.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata
                })
            
            # 重排序
            reranked = self.reranker.rerank_with_metadata(
                query=question,
                documents_with_meta=documents_with_meta,
                top_k=3
            )
            
            # 转换回Document格式
            docs = []
            for item in reranked:
                doc = Document(
                    page_content=item["content"],
                    metadata={
                        **item["metadata"],
                        "relevance_score": item["relevance_score"]
                    }
                )
                docs.append(doc)
        else:
            # 普通检索
            docs = self.kb.similarity_search(question, k=3)
        
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

        # 保存来源信息
        self._last_sources = []
        for doc in docs:
            source_info = {
                "content": doc.page_content[:200],
                "source": doc.metadata.get("source", "未知")
            }
            if "relevance_score" in doc.metadata:
                source_info["relevance_score"] = doc.metadata["relevance_score"]
            self._last_sources.append(source_info)


# 测试代码
if __name__ == "__main__":
    print("🧪 测试重排序功能")
    
    # 模拟测试
    from unittest.mock import Mock
    
    # 创建模拟知识库
    mock_kb = Mock()
    mock_kb.db = Mock()
    mock_kb.db.as_retriever = Mock(return_value=Mock())
    
    # 测试初始化
    try:
        assistant = RAGAssistant(mock_kb, use_reranker=True)
        print("✅ RAG助手初始化成功（带重排序）")
    except Exception as e:
        print(f"⚠️ 初始化失败: {e}")
        print("请安装依赖: pip install sentence-transformers")
