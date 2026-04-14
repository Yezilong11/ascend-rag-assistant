import os
import warnings
import threading
import json

import torch
import torch_npu  # 添加 NPU 支持
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


# ============ 读取 NPU 配置 ============
def load_device_config(config_path="config/device_config.json"):
    """从配置文件读取设备配置"""
    default_config = {
        "device_type": "auto",  # auto, cpu, cuda, npu
        "npu_device_ids": [0],  # NPU 设备 ID 列表
        "cuda_device_id": 0,    # CUDA 设备 ID
    }
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return {**default_config, **config}
        except Exception as e:
            print(f"⚠️ 读取设备配置失败: {e}，使用默认配置")
    
    return default_config


def get_optimal_device(config_path="config/device_config.json"):
    """
    根据配置文件和可用设备，返回最优设备和设备ID
    Returns:
        device (str): 设备类型字符串 ('cpu', 'cuda', 'npu')
        device_id (int or list): 设备ID
    """
    config = load_device_config(config_path)
    device_type = config.get("device_type", "auto")
    
    # 自动检测
    if device_type == "auto":
        # 优先级: NPU > CUDA > CPU
        try:
            if torch.npu.is_available():
                device_type = "npu"
                print("✅ 自动检测到 NPU 设备")
            elif torch.cuda.is_available():
                device_type = "cuda"
                print("✅ 自动检测到 CUDA 设备")
            else:
                device_type = "cpu"
                print("✅ 使用 CPU 设备")
        except:
            if torch.cuda.is_available():
                device_type = "cuda"
                print("✅ 自动检测到 CUDA 设备")
            else:
                device_type = "cpu"
                print("✅ 使用 CPU 设备")
    
    # 根据设备类型返回
    if device_type == "npu":
        try:
            if torch.npu.is_available():
                device_ids = config.get("npu_device_ids", [0])
                device_id = device_ids[0] if device_ids else 0
                print(f"✅ 使用 NPU 设备，device_id={device_id}")
                return "npu", device_id
            else:
                print("⚠️ 配置要求使用 NPU，但 NPU 不可用，回退到 CPU")
                return "cpu", -1
        except Exception as e:
            print(f"⚠️ NPU 初始化失败: {e}，回退到 CPU")
            return "cpu", -1
    
    elif device_type == "cuda":
        if torch.cuda.is_available():
            device_id = config.get("cuda_device_id", 0)
            print(f"✅ 使用 CUDA 设备，device_id={device_id}")
            return "cuda", device_id
        else:
            print("⚠️ 配置要求使用 CUDA，但 CUDA 不可用，回退到 CPU")
            return "cpu", -1
    
    else:  # cpu
        print("✅ 使用 CPU 设备")
        return "cpu", -1


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
            device: 设备，None则使用全局配置
        """
        if not RERANKER_AVAILABLE:
            raise ImportError("sentence-transformers未安装，无法使用重排序功能")
        
        self.model_name = model_name
        
        # 使用全局设备配置
        if device is None:
            device_type, device_id = get_optimal_device()
            self.device = device_type
            if device_type == "npu":
                # 重排序器可能不支持 NPU，使用 CPU
                self.device = "cpu"
                print("⚠️ 重排序器暂不支持 NPU，使用 CPU")
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
                    modelscope_repo_id = model_id
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
        """对检索结果进行重排序"""
        if not documents:
            return []
        
        pairs = [(query, doc.page_content) for doc in documents]
        scores = self.cross_encoder.predict(pairs)
        doc_with_scores = list(zip(documents, scores))
        doc_with_scores.sort(key=lambda x: x[1], reverse=True)
        reranked_docs = [doc for doc, _ in doc_with_scores[:top_k]]
        
        return reranked_docs


class RAGAssistant:
    """RAG智能助教核心引擎"""

    @classmethod
    def get_available_models(cls):
        return PREDEFINED_MODELS

    @classmethod
    def get_available_rerankers(cls):
        return PREDEFINED_RERANKERS

    def __init__(self, knowledge_base, model_key="qwen2-1.5b", model_dir="./models", 
                 use_reranker: bool = True, reranker_model: str = "bge-reranker-v2-m3",
                 reranker_top_k: int = 3, initial_retrieval_k: int = 10,
                 config_path: str = "config/device_config.json"):
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
            config_path: 设备配置文件路径
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
        
        # ============ 修复1: 从配置文件读取设备信息 ============
        self.device_type, self.device_id = get_optimal_device(config_path)
        
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
            if MODELSCOPE_AVAILABLE:
                print(f"🔍 本地模型 {local_model_name} 未找到，正在从ModelScope下载...")
                try:
                    if model_id.startswith("Qwen/"):
                        modelscope_repo_id = model_id.replace("Qwen/", "qwen/")
                    else:
                        modelscope_repo_id = model_id
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

        config = AutoConfig.from_pretrained(
            model_path,
            trust_remote_code=True
        )

        # ============ 修复2: 根据设备类型加载模型 ============
        print(f"🔍 使用设备类型: {self.device_type}")
        
        # 确定数据类型
        if self.device_type in ["cuda", "npu"]:
            dtype = torch.float16
        else:
            dtype = torch.float32
        
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            config=config,
            trust_remote_code=True,
            torch_dtype=dtype,
        )

        # 修复模型缺少的属性
        if not hasattr(self.model, 'all_tied_weights_keys'):
            self.model.all_tied_weights_keys = set()

        # ============ 修复3: 移动到正确设备 ============
        if self.device_type == "npu":
            self.model = self.model.npu()
            if hasattr(self, 'device_id'):
                torch.npu.set_device(self.device_id)
        elif self.device_type == "cuda":
            self.model = self.model.cuda()
            if hasattr(self, 'device_id'):
                torch.cuda.set_device(self.device_id)
        else:
            self.model = self.model.cpu()

        # ============ 修复4: pipeline使用正确的device_id ============
        if self.device_type == "npu":
            pipeline_device_id = self.device_id if hasattr(self, 'device_id') else 0
        elif self.device_type == "cuda":
            pipeline_device_id = self.device_id if hasattr(self, 'device_id') else 0
        else:
            pipeline_device_id = -1

        # 创建生成pipeline
        self.pipeline_obj = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            max_new_tokens=256,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.1,
            device=pipeline_device_id,  # 使用配置文件中的device_id
            do_sample=True
        )

        llm = HuggingFacePipeline(pipeline=self.pipeline_obj)

        # ============ 修复5: 重排序器使用正确的设备 ============
        if self.use_reranker and RERANKER_AVAILABLE:
            try:
                # 重排序器使用独立设备配置
                reranker_device = "cpu" if self.device_type == "npu" else self.device_type
                self.reranker = Reranker(
                    model_name=reranker_model,
                    model_dir=model_dir,
                    device=reranker_device
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

        # 创建RAG链
        self._init_qa_chain(llm, prompt)
        
        print(f"✅ RAG引擎初始化完成 [{model_config['name']}]，设备: {self.device_type.upper()}")

    def _init_qa_chain(self, llm, prompt):
        """初始化 QA 链，支持重排序"""
        from langchain_core.retrievers import BaseRetriever
        from langchain_core.callbacks import CallbackManagerForRetrieverRun
        from typing import List
        from langchain_core.documents import Document

        class RerankCompatibleRetriever(BaseRetriever):
            """自定义检索器"""
            rag_assistant: 'RAGAssistant'
            
            class Config:
                arbitrary_types_allowed = True

            def _get_relevant_documents(
                self, query: str, *, run_manager: CallbackManagerForRetrieverRun
            ) -> List[Document]:
                docs = self.rag_assistant.kb.similarity_search(
                    query, 
                    k=self.rag_assistant.initial_retrieval_k
                )
                
                if self.rag_assistant.use_reranker and self.rag_assistant.reranker:
                    docs = self.rag_assistant.reranker.rerank(
                        query, 
                        docs, 
                        top_k=self.rag_assistant.reranker_top_k
                    )
                else:
                    docs = docs[:self.rag_assistant.reranker_top_k]
                
                self.rag_assistant._last_reranked_docs = docs
                return docs
        
        custom_retriever = RerankCompatibleRetriever(rag_assistant=self)
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=custom_retriever,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )
        
        self._last_reranked_docs = []

    def query(self, question: str) -> dict:
        """完整问答"""
        try:
            self._last_reranked_docs = []
            result = self.qa_chain({"query": question})
            
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
        """流式问答"""
        self._last_reranked_docs = []
        
        docs = self.kb.similarity_search(question, k=self.initial_retrieval_k)
        
        if self.use_reranker and self.reranker:
            docs = self.reranker.rerank(question, docs, top_k=self.reranker_top_k)
        else:
            docs = docs[:self.reranker_top_k]
        
        self._last_reranked_docs = docs
        self._last_sources = [
            {
                "content": doc.page_content[:200],
                "source": doc.metadata.get("source", "未知")
            }
            for doc in docs
        ]
        
        context = "\n\n".join([doc.page_content for doc in docs])

        template = """基于以下检索到的相关信息，回答用户的问题。
如果无法从信息中找到答案，请明确告知。

相关信息：
{context}

用户问题：{question}

请提供专业、准确的回答："""

        prompt_text = template.format(context=context, question=question)

        inputs = self.tokenizer([prompt_text], return_tensors="pt")
        
        # ============ 修复6: 流式生成时使用正确设备 ============
        if self.device_type == "npu":
            inputs = inputs.npu()
        elif self.device_type == "cuda":
            inputs = inputs.cuda()

        streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True, skip_special_tokens=True)

        generation_kwargs = dict(
            inputs,
            streamer=streamer,
            max_new_tokens=256,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.1,
            do_sample=True
        )

        thread = threading.Thread(target=self.model.generate, kwargs=generation_kwargs)
        thread.start()

        for new_text in streamer:
            yield new_text

        thread.join()