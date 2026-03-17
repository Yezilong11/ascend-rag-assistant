import os
import torch

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter


class KnowledgeBase:
    """
    私域知识库管理类
    支持PDF、TXT、MD等格式文档的导入与向量化存储
    """

    def __init__(self, persist_dir="./chroma_db", model_dir="./models"):
        """
        初始化知识库
        Args:
            persist_dir: 向量数据库持久化目录
            model_dir: 本地模型目录
        """
        # 优先使用本地模型，否则从HuggingFace下载
        embedding_model_path = os.path.join(model_dir, "bge-large-zh-v1.5")

        if os.path.exists(embedding_model_path):
            # 使用本地模型
            self.embeddings = HuggingFaceEmbeddings(
                model_name=embedding_model_path,
                model_kwargs={'device': 'cuda' if torch.cuda.is_available() else 'cpu'}
            )
        else:
            # 使用HuggingFace模型
            self.embeddings = HuggingFaceEmbeddings(
                model_name="BAAI/bge-large-zh-v1.5",
                model_kwargs={'device': 'cuda' if torch.cuda.is_available() else 'cpu'}
            )

        self.db = Chroma(
            persist_directory=persist_dir,
            embedding_function=self.embeddings
        )

    def ingest(self, file_path: str) -> bool:
        """
        导入文档到知识库
        Args:
            file_path: 文档路径
        Returns:
            导入成功返回True
        """
        # 根据文件类型选择加载器
        if file_path.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        elif file_path.endswith(('.txt', '.md')):
            loader = TextLoader(file_path, encoding='utf-8')
        else:
            raise ValueError(f"不支持的文件格式: {file_path}")

        # 加载文档
        documents = loader.load()

        # 文本切分策略
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,      # 每块500字符
            chunk_overlap=50,    # 重叠50字符
            separators=["\n\n", "\n", "。", "，", " ", ""]
        )
        chunks = text_splitter.split_documents(documents)

        # 添加到向量数据库
        self.db.add_documents(chunks)
        self.db.persist()

        print(f"✅ 成功导入 {len(chunks)} 个文档片段")
        return True

    def similarity_search(self, query: str, k: int = 3):
        """相似度检索"""
        return self.db.similarity_search(query, k=k)
