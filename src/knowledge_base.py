import os
import re
import torch
from typing import List, Dict, Optional, Tuple
from langchain_community.document_loaders import TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter

# 兼容不同版本的 Document 导入
try:
    from langchain_core.documents import Document
except ImportError:
    from langchain.schema import Document

# PDF解析依赖，请确保已安装：pip install pdfplumber
try:
    import pdfplumber
except ImportError:
    pdfplumber = None


class KnowledgeBase:
    """
    私域知识库管理类
    支持PDF、TXT、MD等格式文档的导入与向量化存储
    根据文档类型自动选择切分策略
    """

    # 文档类型常量
    TYPE_REGISTRATION = "registration"   # 报名须知
    TYPE_TECH_DOC = "tech_doc"           # 技术文档
    TYPE_RULES = "rules"                 # 竞赛规则
    TYPE_HISTORY = "history"             # 历史赛题集
    TYPE_SCORING = "scoring"             # 评分标准
    TYPE_FAQ = "faq"                     # 常见问题
    TYPE_UNKNOWN = "unknown"

    # 默认切分配置
    DEFAULT_CONFIG = {
        "chunk_size": 800,
        "chunk_overlap": 150,
        "split_by_headers": ["h2"],       # 默认按二级标题切分
        "split_by_qa": False,             # 是否按问答对切分
        "split_lists": False,             # 是否将列表项拆分为独立块
        "keep_tables": True,              # 表格是否整体保留
        "keep_code_blocks": True,         # 代码块是否整体保留
        "separators": ["\n\n", "\n", "。", "；", " ", ""]
    }

    # 各文档类型的配置
    TYPE_CONFIGS = {
        TYPE_REGISTRATION: {
            "chunk_size": 800,
            "chunk_overlap": 150,
            "split_by_headers": ["h2"],
            "split_lists": True,           # 报名须知中的列表项可单独拆分为子块
            "keep_tables": True,
        },
        TYPE_TECH_DOC: {
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "split_by_headers": ["h2", "h3"],  # 按二、三级标题切分
            "split_lists": False,
            "keep_tables": True,
            "keep_code_blocks": True,
        },
        TYPE_RULES: {
            "chunk_size": 800,
            "chunk_overlap": 150,
            "split_by_headers": ["h2"],
            "split_lists": False,
            "keep_tables": True,
        },
        TYPE_HISTORY: {
            "chunk_size": 600,
            "chunk_overlap": 100,
            "split_by_headers": ["h2"],
            "split_lists": True,           # 历史赛题集中每个项目可独立
            "keep_tables": True,
        },
        TYPE_SCORING: {
            "chunk_size": 800,
            "chunk_overlap": 150,
            "split_by_headers": ["h2", "h3"],
            "split_lists": False,
            "keep_tables": True,
        },
        TYPE_FAQ: {
            "chunk_size": 400,
            "chunk_overlap": 50,
            "split_by_headers": ["h2"],
            "split_by_qa": True,           # 启用问答对识别
            "split_lists": False,
            "keep_tables": True,
        },
        TYPE_UNKNOWN: {
            "chunk_size": 800,
            "chunk_overlap": 150,
            "split_by_headers": ["h2"],
            "split_lists": False,
            "keep_tables": True,
        }
    }

    def __init__(self, persist_dir="./chroma_db", model_dir="./models"):
        """
        初始化知识库
        Args:
            persist_dir: 向量数据库持久化目录
            model_dir: 本地模型目录
        """
        if pdfplumber is None:
            raise ImportError("pdfplumber is required for PDF processing. Install with: pip install pdfplumber")

        # 优先使用本地模型，否则从HuggingFace下载
        embedding_model_path = os.path.join(model_dir, "bge-large-zh-v1.5")
        if os.path.exists(embedding_model_path):
            self.embeddings = HuggingFaceEmbeddings(
                model_name=embedding_model_path,
                model_kwargs={'device': 'cuda' if torch.cuda.is_available() else 'cpu'}
            )
        else:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="BAAI/bge-large-zh-v1.5",
                model_kwargs={'device': 'cuda' if torch.cuda.is_available() else 'cpu'}
            )

        # 确保持久化目录存在
        os.makedirs(persist_dir, exist_ok=True)
        
        # 初始化Chroma数据库
        try:
            # 检查是否已有数据库文件
            if os.path.exists(persist_dir) and os.listdir(persist_dir):
                # 使用现有数据库
                self.db = Chroma(
                    persist_directory=persist_dir,
                    embedding_function=self.embeddings
                )
            else:
                # 提供一个默认文档，避免空文档列表错误
                from langchain_core.documents import Document
                default_doc = Document(
                    page_content="默认文档，用于初始化知识库",
                    metadata={"source": "default", "doc_type": "unknown"}
                )
                self.db = Chroma.from_documents(
                    documents=[default_doc],
                    embedding=self.embeddings,
                    persist_directory=persist_dir
                )
            self.use_memory_db = False
        except Exception as e:
            print(f"Chroma数据库初始化失败: {e}")
            print("使用简单内存模式初始化知识库")
            # 降级到简单内存存储
            class SimpleMemoryDB:
                def __init__(self):
                    self.documents = []
                def add_documents(self, docs):
                    self.documents.extend(docs)
                def similarity_search(self, query, k=3):
                    # 简单返回前k个文档
                    return self.documents[:k]
            self.db = SimpleMemoryDB()
            self.use_memory_db = True

    def detect_doc_type(self, file_path: str) -> str:
        """
        根据文件路径或文件名判断文档类型
        Args:
            file_path: 文件路径
        Returns:
            文档类型常量
        """
        base = os.path.basename(file_path).lower()
        if "报名须知" in base or "registration" in base:
            return self.TYPE_REGISTRATION
        if "技术文档" in base or "tech_doc" in base or "技术指南" in base:
            return self.TYPE_TECH_DOC
        if "竞赛规则" in base or "规则" in base or "rules" in base:
            return self.TYPE_RULES
        if "历史赛题" in base or "history" in base or "赛题集" in base:
            return self.TYPE_HISTORY
        if "评分标准" in base or "scoring" in base:
            return self.TYPE_SCORING
        if "常见问题" in base or "faq" in base:
            return self.TYPE_FAQ
        return self.TYPE_UNKNOWN

    def pdf_to_markdown(self, pdf_path: str) -> str:
        """
        将PDF文件转换为Markdown格式的文本
        尝试保留表格、段落结构，并识别标题（基于字体大小，简版）
        Args:
            pdf_path: PDF文件路径
        Returns:
            Markdown格式字符串
        Raises:
            Exception: 当PDF解析失败时抛出异常
        """
        markdown_lines = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    # 提取文本（包含位置信息）
                    words = page.extract_words(keep_blank_chars=True, extra_attrs=["fontname", "size"])
                    # 按行组织文本（简单合并）
                    if words:
                        lines = {}
                        for w in words:
                            y = round(w['top'], 1)
                            lines.setdefault(y, []).append(w)
                        sorted_y = sorted(lines.keys())
                        for y in sorted_y:
                            line_words = sorted(lines[y], key=lambda x: x['x0'])
                            line_text = " ".join([w['text'] for w in line_words])
                            markdown_lines.append(line_text)
                    else:
                        # 无文本，尝试提取表格
                        tables = page.extract_tables()
                        if tables:
                            for table in tables:
                                if table and len(table) > 0:
                                    header = "| " + " | ".join([str(cell or "") for cell in table[0]]) + " |"
                                    separator = "| " + " | ".join(["---"] * len(table[0])) + " |"
                                    markdown_lines.append(header)
                                    markdown_lines.append(separator)
                                    for row in table[1:]:
                                        row_text = "| " + " | ".join([str(cell or "") for cell in row]) + " |"
                                        markdown_lines.append(row_text)
                    markdown_lines.append(f"\n<!-- Page {page_num} -->\n")
            return "\n".join(markdown_lines)
        except Exception as e:
            raise Exception(f"PDF解析失败: {pdf_path}, 错误: {e}")

    def _split_by_qa(self, text: str, metadata: Dict) -> List[Document]:
        """
        按问答对切分FAQ文本
        支持两种格式：
        1. ### Q1: ...\nA: ...
        2. **Q：**...\nA：...
        """
        qa_patterns = [
            # 格式1: ### Q1: ...\nA: ...
            re.compile(r'(?m)^#{1,3}\s*Q\d*[：:]\s*(.*?)\nA[：:]\s*(.*?)(?=\n#{1,3}\s*Q|\Z)', re.DOTALL),
            # 格式2: **Q：**...\nA：...
            re.compile(r'(?m)\*\*Q[：:]\*\*\s*(.*?)\nA[：:]\s*(.*?)(?=\n\*\*Q|\Z)', re.DOTALL)
        ]
        chunks = []
        for pattern in qa_patterns:
            for match in pattern.finditer(text):
                q = match.group(1).strip()
                a = match.group(2).strip()
                content = f"**Q：{q}**\nA：{a}"
                new_meta = metadata.copy()
                new_meta["question"] = q
                new_meta["answer"] = a
                chunks.append(Document(page_content=content, metadata=new_meta))
            if chunks:
                break
        return chunks

    def _split_by_headers(self, text: str, headers: List[str], metadata: Dict) -> List[Document]:
        """
        按Markdown标题层级切分
        """
        header_map = {
            "h1": "#",
            "h2": "##",
            "h3": "###",
            "h4": "####"
        }
        splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[(header_map[h], h) for h in headers])
        splits = splitter.split_text(text)
        for split in splits:
            split.metadata.update(metadata)
        return splits

    def _split_list_items(self, chunk: Document) -> List[Document]:
        """
        将文档中的有序/无序列表项拆分为独立块
        简单规则：识别以数字或-开头的行
        """
        lines = chunk.page_content.split('\n')
        list_items = []
        current_item = []
        in_list = False
        for line in lines:
            if re.match(r'^\s*(\d+\.|\-|\*)\s+', line):
                if current_item:
                    list_items.append("\n".join(current_item))
                current_item = [line]
                in_list = True
            else:
                if in_list:
                    current_item.append(line)
                else:
                    pass
        if current_item:
            list_items.append("\n".join(current_item))
        if not list_items:
            return [chunk]
        new_chunks = []
        for item in list_items:
            new_meta = chunk.metadata.copy()
            new_chunks.append(Document(page_content=item.strip(), metadata=new_meta))
        return new_chunks

    def _protect_atomic_elements(self, text: str, keep_tables: bool, keep_code: bool) -> Tuple[str, List[Dict]]:
        """
        保护表格和代码块，用占位符替换，避免被切分器破坏
        返回(处理后的文本, 替换记录)
        """
        placeholders = []
        if keep_code:
            def replace_code(match):
                idx = len(placeholders)
                placeholders.append({"type": "code", "content": match.group(0)})
                return f"__PLACEHOLDER_{idx}__"
            text = re.sub(r'```.*?```', replace_code, text, flags=re.DOTALL)
        if keep_tables:
            def replace_table(match):
                idx = len(placeholders)
                placeholders.append({"type": "table", "content": match.group(0)})
                return f"__PLACEHOLDER_{idx}__"
            text = re.sub(r'(\|.*\|\n\|[-: |]+\|\n(\|.*\|\n?)+)', replace_table, text, flags=re.MULTILINE)
        return text, placeholders

    def _restore_atomic_elements(self, chunks: List[Document], placeholders: List[Dict]) -> List[Document]:
        """
        恢复占位符为原始内容
        """
        for chunk in chunks:
            for i, placeholder in enumerate(placeholders):
                chunk.page_content = chunk.page_content.replace(f"__PLACEHOLDER_{i}__", placeholder["content"])
        return chunks

    def split_document(self, text: str, doc_type: str, source: str) -> List[Document]:
        """
        根据文档类型进行切分
        Args:
            text: 文本内容
            doc_type: 文档类型常量
            source: 原始文件路径
        Returns:
            Document列表
        """
        config = self.TYPE_CONFIGS.get(doc_type, self.DEFAULT_CONFIG)
        base_metadata = {"source": source, "doc_type": doc_type}

        # 1. 如果是FAQ且启用按问答对切分（使用.get安全访问）
        if config.get("split_by_qa", False):
            qa_chunks = self._split_by_qa(text, base_metadata)
            if qa_chunks:
                return qa_chunks

        # 2. 保护原子元素（表格、代码块）
        keep_tables = config.get("keep_tables", True)
        keep_code = config.get("keep_code_blocks", True)
        protected_text, placeholders = self._protect_atomic_elements(text, keep_tables, keep_code)

        # 3. 按标题切分
        headers = config.get("split_by_headers", [])
        if headers:
            splits = self._split_by_headers(protected_text, headers, base_metadata)
        else:
            splits = [Document(page_content=protected_text, metadata=base_metadata)]

        # 4. 对每个块进一步按长度切分
        final_chunks = []
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.get("chunk_size", 800),
            chunk_overlap=config.get("chunk_overlap", 150),
            separators=config.get("separators", self.DEFAULT_CONFIG["separators"])
        )
        for split in splits:
            if len(split.page_content) > config.get("chunk_size", 800) * 1.2:
                sub_chunks = text_splitter.split_documents([split])
                final_chunks.extend(sub_chunks)
            else:
                final_chunks.append(split)

        # 5. 若配置了拆分列表项
        if config.get("split_lists", False):
            expanded = []
            for chunk in final_chunks:
                list_chunks = self._split_list_items(chunk)
                expanded.extend(list_chunks)
            final_chunks = expanded

        # 6. 恢复原子元素
        final_chunks = self._restore_atomic_elements(final_chunks, placeholders)

        return final_chunks

    def csv_to_markdown(self, csv_path: str) -> str:
        import csv
        lines = []
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            for row_idx, row in enumerate(reader):
                line = "| " + " | ".join(row) + " |"
                lines.append(line)
                if row_idx == 0:
                    separator = "| " + " | ".join(["---"] * len(row)) + " |"
                    lines.append(separator)
        return "\n".join(lines)

    def json_to_text(self, json_path: str) -> str:
        import json
        with open(json_path, 'r', encoding='utf-8') as f:
            obj = json.load(f)

        def flatten(obj, prefix=""):
            parts = []
            if isinstance(obj, dict):
                for k, v in obj.items():
                    parts.extend(flatten(v, f"{prefix}{k}: " if prefix else f"{k}: "))
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    parts.extend(flatten(item, f"{prefix}[{i}]: "))
            else:
                parts.append(f"{prefix}{obj}")
            return parts

        return "\n".join(flatten(obj))

    def jsonl_to_text(self, jsonl_path: str) -> str:
        import json
        lines = []
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    obj = json.loads(line)
                    text = json.dumps(obj, ensure_ascii=False)
                    lines.append(text)
        return "\n".join(lines)

    def image_ocr_to_text(self, image_path: str) -> str:
        from src.multimodal.infrastructure.ocr.easyocr_engine import EasyOCREngine
        ocr = EasyOCREngine()
        text, _ = ocr.extract_text_from_image(image_path)
        return text if text else "[图片中未识别到文字]"

    def ingest(self, file_path: str, doc_type: Optional[str] = None, display_source: Optional[str] = None) -> bool:
        """
        导入文档到知识库
        Args:
            file_path: 文档路径
            doc_type: 文档类型（可选，不指定则自动判断）
            display_source: 显示用的来源路径（可选，覆盖 file_path 作为 source 元数据）
        Returns:
            导入成功返回True，失败返回False
        """
        try:
            # 1. 确定文档类型
            if doc_type is None:
                doc_type = self.detect_doc_type(file_path)

            # 2. 加载并转换为文本
            if file_path.endswith('.pdf'):
                if pdfplumber is None:
                    raise ImportError("pdfplumber not installed")
                text = self.pdf_to_markdown(file_path)
            elif file_path.endswith(('.txt', '.md')):
                try:
                    loader = TextLoader(file_path, encoding='utf-8')
                    docs = loader.load()
                    text = docs[0].page_content
                except UnicodeDecodeError:
                    for enc in ['gbk', 'gb2312', 'latin-1']:
                        try:
                            loader = TextLoader(file_path, encoding=enc)
                            docs = loader.load()
                            text = docs[0].page_content
                            print(f"[WARN] 使用编码 {enc} 成功读取文件 {file_path}")
                            break
                        except UnicodeDecodeError:
                            continue
                    else:
                        raise UnicodeDecodeError(f"无法解码文件 {file_path}，尝试的编码均失败")
            elif file_path.endswith(('.docx', '.doc')):
                from langchain_community.document_loaders import UnstructuredWordDocumentLoader
                loader = UnstructuredWordDocumentLoader(file_path, mode="elements")
                docs = loader.load()
                text = "\n\n".join([doc.page_content for doc in docs])
            elif file_path.endswith(('.html', '.htm')):
                from langchain_community.document_loaders import UnstructuredHTMLLoader
                loader = UnstructuredHTMLLoader(file_path)
                docs = loader.load()
                text = docs[0].page_content
            elif file_path.endswith(('.pptx', '.ppt')):
                from langchain_community.document_loaders import UnstructuredPowerPointLoader
                loader = UnstructuredPowerPointLoader(file_path)
                docs = loader.load()
                text = "\n\n".join([doc.page_content for doc in docs])
            elif file_path.endswith(('.xlsx', '.xls')):
                from langchain_community.document_loaders import UnstructuredExcelLoader
                loader = UnstructuredExcelLoader(file_path)
                docs = loader.load()
                text = "\n\n".join([doc.page_content for doc in docs])
            elif file_path.endswith('.csv'):
                text = self.csv_to_markdown(file_path)
            elif file_path.endswith('.json'):
                text = self.json_to_text(file_path)
            elif file_path.endswith('.jsonl'):
                text = self.jsonl_to_text(file_path)
            elif file_path.endswith(('.png', '.jpg', '.jpeg')):
                text = self.image_ocr_to_text(file_path)
            else:
                raise ValueError(f"不支持的文件格式: {file_path}")

            # 3. 切分文档
            source_for_metadata = display_source or file_path
            chunks = self.split_document(text, doc_type, source_for_metadata)

            # 4. 添加到向量数据库
            self.db.add_documents(chunks)
            # 只有在非内存模式下才执行persist
            if not hasattr(self, 'use_memory_db') or not self.use_memory_db:
                try:
                    self.db.persist()
                except Exception as e:
                    print(f"持久化数据库失败: {e}")

            print(f"[OK] 成功导入 {len(chunks)} 个文档片段（类型：{doc_type}）")
            return True
        except Exception as e:
            print(f"[ERROR] 导入失败: {file_path}, 错误: {e}")
            return False

    def similarity_search(self, query: str, k: int = 3):
        """相似度检索"""
        return self.db.similarity_search(query, k=k)