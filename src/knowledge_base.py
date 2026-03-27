import os
import time
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
        # 转换为绝对路径
        persist_dir = os.path.abspath(persist_dir)
        model_dir = os.path.abspath(model_dir)
        
        # 创建持久化目录（如果不存在）
        if not os.path.exists(persist_dir):
            os.makedirs(persist_dir, exist_ok=True)
            print(f"创建持久化目录: {persist_dir}")
        
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

        # 初始化Chroma向量数据库
        try:
            self.db = Chroma(
                persist_directory=persist_dir,
                embedding_function=self.embeddings
            )
            print(f"成功初始化Chroma数据库: {persist_dir}")
        except Exception as e:
            print(f"初始化Chroma数据库失败: {e}")
            # 尝试清除可能的损坏状态
            import shutil
            if os.path.exists(persist_dir):
                shutil.rmtree(persist_dir)
                os.makedirs(persist_dir, exist_ok=True)
            # 重新初始化
            self.db = Chroma(
                persist_directory=persist_dir,
                embedding_function=self.embeddings
            )
            print(f"重新初始化Chroma数据库成功: {persist_dir}")
        
        # 文档跟踪
        self.documents = []  # 跟踪已上传的文档

    def ingest(self, file_path: str, original_filename: str = None) -> bool:
        """
        导入文档到知识库
        Args:
            file_path: 文档路径
            original_filename: 原始文件名
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
        
        # 获取文件名（使用原始文件名）
        filename = original_filename or os.path.basename(file_path)
        
        # 添加到文档跟踪列表
        if filename not in [doc['name'] for doc in self.documents]:
            self.documents.append({
                'name': filename,
                'path': file_path,
                'size': os.path.getsize(file_path),
                'uploaded_at': int(time.time())
            })
        
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
    
    def get_documents(self):
        """获取已上传的文档列表"""
        return self.documents
    
    def delete_document(self, filename: str) -> bool:
        """删除文档"""
        try:
            # 从跟踪列表中删除
            self.documents = [doc for doc in self.documents if doc['name'] != filename]
            print(f"✅ 成功删除文档: {filename}")
            return True
        except Exception as e:
            print(f"❌ 删除文档失败: {str(e)}")
            return False
