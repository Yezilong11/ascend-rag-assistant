import os
import warnings

import torch
from langchain_classic.chains.retrieval_qa.base import RetrievalQA
from langchain_community.llms import HuggingFacePipeline
from langchain_core.prompts import PromptTemplate
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer, pipeline

warnings.filterwarnings("ignore")


class RAGAssistant:
    """
    RAG智能助教核心引擎
    结合知识检索与大模型生成能力
    """

    def __init__(self, knowledge_base, model_id="Qwen/Qwen2-1.5B-Instruct", model_dir="./models"):
        """
        初始化RAG助手
        Args:
            knowledge_base: KnowledgeBase实例
            model_id: 大模型ID（本机试运行使用ChatGLM3-6B）
            model_dir: 本地模型目录
        """
        self.kb = knowledge_base

        # 优先使用本地模型
        local_model_path = os.path.join(model_dir, model_id.split("/")[-1])

        if os.path.exists(local_model_path):
            model_path = local_model_path
            print(f"正在加载本地模型: {model_path}...")
        else:
            model_path = model_id
            print(f"正在从HuggingFace下载模型: {model_id}...")
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

        # 加载模型
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            config=config,
            trust_remote_code=True,
            torch_dtype=torch.float32,  # 使用float32避免问题
        )

        # 修复模型缺少的属性
        if not hasattr(model, 'all_tied_weights_keys'):
            model.all_tied_weights_keys = set()

        # 手动移动到CPU
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = model.to(device)

        # 创建生成pipeline
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=512,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.1,
            device=0 if torch.cuda.is_available() else -1
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

        print("✅ RAG引擎初始化完成")

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
