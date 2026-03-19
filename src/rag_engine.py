import os
import warnings

import torch
from langchain_classic.chains.retrieval_qa.base import RetrievalQA
from langchain_community.llms import HuggingFacePipeline
from langchain_core.prompts import PromptTemplate
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer, pipeline

# GPTQ量化支持
try:
    from auto_gptq import AutoGPTQForCausalLM
    GPTQ_AVAILABLE = True
except ImportError:
    GPTQ_AVAILABLE = False

warnings.filterwarnings("ignore")


# 预定义模型配置
PREDEFINED_MODELS = {
    "qwen2-1.5b-gptq-int4": {
        "repo_id": "Qwen/Qwen2-1.5B-Instruct-GPTQ-Int4",
        "name": "Qwen2-1.5B (GPTQ-Int4 量化)",
        "description": "推荐，速度快，质量损失小",
        "is_quantized": True
    },
    "qwen2-1.5b": {
        "repo_id": "Qwen/Qwen2-1.5B-Instruct",
        "name": "Qwen2-1.5B (FP16)",
        "description": "标准版，质量最好",
        "is_quantized": False
    },
    "qwen2-0.5b": {
        "repo_id": "Qwen/Qwen2-0.5B-Instruct",
        "name": "Qwen2-0.5B (FP16)",
        "description": "最快，适合CPU",
        "is_quantized": False
    },
    "chatglm3-6b": {
        "repo_id": "THUDM/chatglm3-6b",
        "name": "ChatGLM3-6B (FP16)",
        "description": "大模型，质量更好",
        "is_quantized": False
    }
}


class RAGAssistant:
    """
    RAG智能助教核心引擎
    结合知识检索与大模型生成能力
    支持GPTQ量化模型加速推理
    支持多模型切换
    """

    @classmethod
    def get_available_models(cls):
        """获取所有预定义模型列表"""
        return PREDEFINED_MODELS

    def __init__(self, knowledge_base, model_key="qwen2-1.5b-gptq-int4", model_dir="./models"):
        """
        初始化RAG助手
        Args:
            knowledge_base: KnowledgeBase实例
            model_key: 预定义模型key
            model_dir: 本地模型目录
        """
        self.kb = knowledge_base
        self.model_key = model_key

        # 获取模型配置
        model_config = PREDEFINED_MODELS[model_key]
        model_id = model_config["repo_id"]

        # 优先使用本地模型，自动优先检测量化版
        local_model_name = model_id.split("/")[-1]
        local_model_path = os.path.join(model_dir, local_model_name)

        # 检查本地是否存在，如果不存在并且优先有量化版，尝试检测量化版
        if not os.path.exists(local_model_path) and not model_config["is_quantized"]:
            # 尝试查找是否有同名量化版
            quantized_candidates = [
                f"{local_model_name}-GPTQ-Int4",
                f"{local_model_name}-int4",
                f"{local_model_name}-gptq"
            ]
            for candidate in quantized_candidates:
                candidate_path = os.path.join(model_dir, candidate)
                if os.path.exists(candidate_path):
                    local_model_path = candidate_path
                    print(f"🔍 未找到原版模型，自动使用本地量化版: {candidate}")
                    break

        if os.path.exists(local_model_path):
            model_path = local_model_path
            print(f"正在加载本地模型: {model_path}...")
        else:
            model_path = model_id
            print(f"本地模型未找到，正在从HuggingFace下载: {model_id}...")

        tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            trust_remote_code=True
        )

        # 修复ChatGLM3与新版本transformers兼容性问题
        config = AutoConfig.from_pretrained(
            model_path,
            trust_remote_code=True
        )

        # 添加缺失的属性
        if not hasattr(config, 'max_length'):
            config.max_length = 2048
        if not hasattr(config, 'max_seq_length'):
            config.max_seq_length = 2048
        if not hasattr(config, 'tie_word_embeddings'):
            config.tie_word_embeddings = False

        # 判断是否使用GPTQ
        is_gptq_model = model_config.get("is_quantized", None)
        if is_gptq_model is None:
            # 自动检测: 模型路径中包含GPTQ或int4/int8字样
            is_gptq_model = any(keyword in model_path.lower() for keyword in ['gptq', 'int4', 'int8'])

        # 当GPTQ不可用时，强制禁用量化检测
        if not GPTQ_AVAILABLE and is_gptq_model:
            print("⚠️ GPTQ不可用，禁用量化配置以普通模式加载")
            if hasattr(config, 'quantization_config'):
                delattr(config, 'quantization_config')
            is_gptq_model = False

        # 加载模型 - GPTQ量化分支
        if GPTQ_AVAILABLE and is_gptq_model:
            try:
                print("⚡ 使用GPTQ量化模型加速推理")
                model = AutoGPTQForCausalLM.from_quantized(
                    model_path,
                    device_map="auto",
                    trust_remote_code=True,
                    use_safetensors=True,
                    inject_fused_attention=False
                )
            except Exception as e:
                print(f"⚠️ GPTQ加载失败，降级到普通模型: {str(e)}")
                model = AutoModelForCausalLM.from_pretrained(
                    model_path,
                    config=config,
                    trust_remote_code=True,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                )
        else:
            # 普通加载
            print("🔍 使用原始模型加载")
            # 不传递config来避免自动量化检测
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                trust_remote_code=True,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            )

            # 修复模型缺少的属性
            if not hasattr(model, 'all_tied_weights_keys'):
                model.all_tied_weights_keys = set()

            # 移动到设备
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model = model.to(device)

        # 修复pipeline的device参数
        if torch.cuda.is_available():
            device_id = 0
        else:
            device_id = -1

        # 创建生成pipeline
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=256,  # 限制生成长度，提升速度
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.1,
            device=device_id,
            do_sample=True
        )

        self.llm = HuggingFacePipeline(pipeline=pipe)

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

        # 创建RAG链
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.kb.db.as_retriever(search_kwargs={"k": 3}),
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )

        print(f"✅ RAG引擎初始化完成 [{model_config['name']}]")

    def query(self, question: str) -> dict:
        """
        处理用户查询
        Args:
            question: 用户问题
        Returns:
            包含答案和来源的字典
        """
        try:
            result = self.qa_chain({"query": question})
            return {
                "answer": result["result"],
                "sources": [
                    {
                        "content": doc.page_content[:200],
                        "source": doc.metadata.get("source", "未知")
                    }
                    for doc in result["source_documents"]
                ]
            }
        except Exception as e:
            return {
                "answer": f"处理问题时出错: {str(e)}",
                "sources": []
            }
