# 多模态RAG模块 技术设计文档

**项目**: Ascend RAG Assistant - 多模态扩展
**版本**: v1.1.0
**日期**: 2026-05-02
**架构**: DDD (Domain-Driven Design)

---

## 1. 项目背景与目标

### 1.1 业务背景

现有Ascend RAG Assistant项目已实现基于文本的RAG问答能力，需扩展多模态支持以处理图片和PDF内嵌图片。

### 1.2 技术目标

| 目标 | 实现 |
|------|------|
| 图片OCR+分析存入知识库 | ✅ |
| PDF内嵌图片提取处理 | ✅ |
| 侧边栏图片上传UI | ✅ |
| 检索返回图片内容 | ✅ |
| OCR在CPU，VLM在GPU/NPU | ✅ |
| 8GB显存消费级硬件适配 | ✅ |

### 1.3 异构计算架构

```
┌─────────────────────────────────────────────────────────────┐
│                      用户请求                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    应用层 (Application)                      │
│  MultimodalIngestService / MultimodalQueryService          │
└─────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   领域层 Domain  │ │   领域层 Domain  │ │   领域层 Domain  │
│   OCR领域服务   │ │   VLM领域服务   │ │  索引领域服务   │
│   (CPU运行)     │ │   (GPU/NPU)     │ │   (CPU运行)     │
└─────────────────┘ └─────────────────┘ └─────────────────┘
          │                   │                   │
          ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ 基础设施层 Infra │ │ 基础设施层 Infra │ │ 基础设施层 Infra │
│ PaddleOCR/EasyOCR│ │ Qwen-VL-2B INT4 │ │ Chroma VectorDB │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

### 1.4 显存分配（8GB基准）

| 组件 | 设备 | 模型 | 量化 | 显存 |
|------|------|------|------|------|
| OCR识别 | CPU | PaddleOCR | - | ~1GB |
| VLM推理 | GPU 8GB | Qwen-VL-2B | INT4 | ~1.5GB |
| 嵌入模型 | CPU | BGE-Large | - | ~1.5GB |
| 向量库 | CPU | Chroma | - | ~0.5GB |
| **预留** | - | - | - | **~3.5GB** |

---

## 2. DDD分层架构

### 2.1 分层职责

```
┌────────────────────────────────────────────────────────────┐
│                      接口层 Interface                       │
│   API Routes (FastAPI)  │  Streamlit UI Components        │
│   - /api/multimodal/    │   - 侧边栏上传组件               │
└────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────┐
│                    应用层 Application                       │
│   Services: MultimodalIngestService, MultimodalQueryService │
│   DTOs: ImageIngestDTO, QueryDTO, QueryResultDTO         │
└────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────┐
│                      领域层 Domain                          │
│   Entities: ImageChunk, MultimodalDocument                  │
│   Value Objects: BoundingBox, DeviceType, ProcessingStatus│
│   Domain Services: MultimodalProcessingService (Interface) │
│   Repositories: ImageChunkRepository (Interface)          │
└────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────┐
│                   基础设施层 Infrastructure                  │
│   OCR: PaddleOCREngine / EasyOCREngine                     │
│   VLM: QwenVLEngine                                        │
│   PDF: PDFImageExtractor                                   │
│   Device: DeviceManager                                    │
│   Persistence: ChromaImageChunkRepository                 │
└────────────────────────────────────────────────────────────┘
```

---

## 3. 领域层设计 (Domain Layer)

### 3.1 实体 (Entities)

#### 3.1.1 ImageChunk - 图片片段实体

```python
# 文件: src/multimodal/domain/entities/image_chunk.py

@dataclass
class ImageChunk:
    """
    图片片段 - 领域实体 (Entity)
    代表一张图片经过OCR+VLM处理后生成的文档片段

    Attributes:
        id: str                          # 唯一标识符 (UUID)
        page_content: str                # VLM生成的图片描述（用于向量化）
        image_path: str                  # 图片存储路径
        ocr_text: str                    # OCR提取的原始文字
        page_number: int                 # 来源页码
        bounding_box: BoundingBox        # 图片在文档中的位置
        source_file: str                 # 原始文件路径
        document_type: str               # 文档类型
        processing_status: ProcessingStatus  # 处理状态
        embedding_vector: List[float]    # 嵌入向量
        metadata: Dict[str, Any]         # 扩展元数据
        created_at: datetime              # 创建时间
        updated_at: datetime              # 更新时间

    Identity:
        - id: 唯一标识符
        - image_path + source_file: 业务标识

    Business Rules:
        - 只有processing_status为COMPLETED才能被索引
        - page_content由VLM生成，不可为空
        - OCR失败不影响VLM处理（使用空字符串）
    """

    id: str
    page_content: str
    image_path: str
    ocr_text: str = ""
    page_number: int = 0
    bounding_box: Optional[BoundingBox] = None
    source_file: str = ""
    document_type: str = "unknown"
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    embedding_vector: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # === 业务方法 ===
    def is_processed(self) -> bool: ...
    def is_failed(self) -> bool: ...
    def mark_completed(self) -> None: ...
    def mark_failed(self, error_message: str) -> None: ...
    def get_searchable_text(self) -> str: ...
```

#### 3.1.2 MultimodalDocument - 多模态文档聚合根

```python
# 文件: src/multimodal/domain/entities/multimodal_document.py

@dataclass
class MultimodalDocument:
    """
    多模态文档 - 聚合根 (Aggregate Root)
    统一管理文本片段和图片片段的完整文档

    Aggregate Boundary:
        - text_chunks: 文本片段（复用现有Document）
        - image_chunks: 图片片段（ImageChunk实体）

    Invariants:
        - 所有image_chunks的source_file必须等于self.source_path
        - document_type一旦设置不可随意更改
    """

    id: str
    source_path: str
    document_type: str = "unknown"
    text_chunks: List[Document] = field(default_factory=list)
    image_chunks: List[ImageChunk] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # === 聚合方法 ===
    def add_text_chunk(self, chunk: Document) -> None: ...
    def add_image_chunk(self, chunk: ImageChunk) -> None: ...
    def get_all_chunks(self) -> List: ...
    def get_processing_summary(self) -> Dict[str, Any]: ...
    def is_fully_processed(self) -> bool: ...
```

### 3.2 值对象 (Value Objects)

#### 3.2.1 BoundingBox - 边界框

```python
# 文件: src/multimodal/domain/value_objects/bounding_box.py

@dataclass(frozen=True)
class BoundingBox:
    """
    边界框 - 值对象 (Value Object)
    不可变，表示二维空间中的矩形区域

    Value Object Characteristics:
        - 不可变 (frozen=True)
        - 相等性基于属性值而非引用
        - 无唯一标识符
    """

    x1: float   # 左上角X
    y1: float   # 左上角Y
    x2: float   # 右下角X
    y2: float   # 右下角Y

    @property
    def width(self) -> float: ...
    @property
    def height(self) -> float: ...
    @property
    def area(self) -> float: ...
    @property
    def center(self) -> Tuple[float, float]: ...

    def contains(self, point: Tuple[float, float]) -> bool: ...
    def overlaps(self, other: BoundingBox) -> bool: ...

    # === 工厂方法 ===
    @classmethod
    def from_paddleocr(cls, bbox_data) -> "BoundingBox": ...
    @classmethod
    def from_easyocr(cls, bbox_data) -> "BoundingBox": ...
```

#### 3.2.2 DeviceType - 设备类型

```python
# 文件: src/multimodal/domain/value_objects/device_type.py

class DeviceType(Enum):
    """
    设备类型枚举
    """

    NPU = "npu"     # 昇腾NPU
    CUDA = "cuda"   # NVIDIA GPU
    CPU = "cpu"     # 中央处理器

    @property
    def is_accelerator(self) -> bool: ...
    def get_memory_estimate_mb(self, model_type: str) -> int: ...


class DevicePriority:
    """
    设备优先级管理器
    实现 NPU > GPU > CPU 自动选择
    """

    DEFAULT_PRIORITY = [DeviceType.NPU, DeviceType.CUDA, DeviceType.CPU]

    def get_available_device(
        self,
        npu_available: bool = False,
        cuda_available: bool = False,
        forced_device: DeviceType = None,
    ) -> DeviceType: ...

    def get_vlm_device(self, npu_available, cuda_available) -> DeviceType: ...
    def get_ocr_device(self) -> DeviceType: ...
    def get_embedding_device(self) -> DeviceType: ...

    def get_allocation_plan(self, total_memory_mb: int = 8192) -> Dict[str, int]:
        """
        生成分显存分配方案（8GB基准）
        Returns:
            {
                "reserved_mb": 3584,
                "vlm_mb": 1536,
                "ocr_mb": 1024,
                "embedding_mb": 1536,
                "vectorstore_mb": 512,
            }
        """
```

#### 3.2.3 ProcessingStatus - 处理状态

```python
# 文件: src/multimodal/domain/value_objects/processing_status.py

class ProcessingStatus(Enum):
    """
    处理状态枚举
    """

    PENDING = "pending"       # 待处理
    PROCESSING = "processing" # 处理中
    COMPLETED = "completed"   # 已完成
    FAILED = "failed"        # 失败
    PARTIAL = "partial"      # 部分成功

    def is_terminal(self) -> bool: ...
    def is_successful(self) -> bool: ...


@dataclass
class ProcessingResult:
    """
    处理结果值对象
    """

    status: ProcessingStatus
    message: str = ""
    data: Optional[Any] = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_success(self) -> bool: ...
    @property
    def is_failure(self) -> bool: ...

    @classmethod
    def success(cls, message, data=None, duration_ms=0.0) -> "ProcessingResult": ...
    @classmethod
    def failure(cls, message, error=None, duration_ms=0.0) -> "ProcessingResult": ...
    @classmethod
    def partial(cls, message, failed_count, success_count) -> "ProcessingResult": ...
```

### 3.3 领域服务接口 (Domain Services)

#### 3.3.1 MultimodalProcessingService - 多模态处理服务

```python
# 文件: src/multimodal/domain/services/multimodal_processing_service.py

class MultimodalProcessingService(ABC):
    """
    多模态处理领域服务接口
    定义图片处理的核心业务逻辑契约

    Business Logic:
        1. OCR识别文字（CPU）
        2. VLM生成描述（GPU/NPU）
        3. 组合结果生成ImageChunk
    """

    def process_image(
        self,
        image_path: str,
        source_file: str = "",
        page_number: int = 0,
        options: Dict[str, Any] = None,
    ) -> ProcessingResult:
        """
        处理单张图片
        Returns: ProcessingResult with data=ImageChunk
        """
        ...

    def process_image_batch(
        self,
        image_paths: List[str],
        source_file: str = "",
        start_page: int = 0,
        options: Dict[str, Any] = None,
    ) -> ProcessingResult:
        """
        批量处理图片
        Returns: ProcessingResult with data=List[ImageChunk]
        """
        ...

    def extract_text_from_image(self, image_path: str) -> Tuple[str, List[Dict]]:
        """
        OCR识别
        Returns: (完整文字, 带位置的文字块列表)
        """
        ...

    def generate_image_description(
        self,
        image_path: str,
        ocr_text: str = "",
        prompt: str = None,
    ) -> str:
        """
        VLM生成图片描述
        """
        ...

    def analyze_image_with_query(
        self,
        image_path: str,
        query: str,
    ) -> str:
        """
        基于问题分析图片（VLM推理）
        """
        ...


class ImageIndexingService(ABC):
    """
    图片索引领域服务接口
    """

    def index_image_chunk(self, chunk: ImageChunk) -> bool: ...
    def index_batch(self, chunks: List[ImageChunk]) -> Tuple[int, int]: ...
    def search_similar(
        self,
        query: str,
        k: int = 3,
        document_type: str = None,
    ) -> List[ImageChunk]: ...
    def delete_from_index(self, chunk_id: str) -> bool: ...


class PDFImageExtractionService(ABC):
    """
    PDF图片提取领域服务接口
    """

    def extract_images_from_pdf(
        self,
        pdf_path: str,
        output_dir: str = None,
        min_size: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Returns: [{"page": 1, "image_path": "...", "bbox": [...], "size": (w,h)}, ...]
        """
        ...

    def extract_images_from_page(
        self,
        pdf_path: str,
        page_number: int,
        output_dir: str = None,
    ) -> List[Dict[str, Any]]: ...
```

### 3.4 仓储接口 (Repository Interfaces)

#### 3.4.1 ImageChunkRepository

```python
# 文件: src/multimodal/domain/repositories/image_chunk_repository.py

class ImageChunkRepository(ABC):
    """
    图片片段仓储接口
    定义领域实体的持久化操作契约
    """

    def save(self, chunk: ImageChunk) -> ImageChunk: ...
    def save_batch(self, chunks: List[ImageChunk]) -> List[ImageChunk]: ...
    def find_by_id(self, chunk_id: str) -> Optional[ImageChunk]: ...
    def find_by_source(self, source_file: str) -> List[ImageChunk]: ...
    def find_by_document_type(self, document_type: str) -> List[ImageChunk]: ...

    def similarity_search(
        self,
        query: str,
        k: int = 3,
        filter_criteria: Dict[str, Any] = None,
    ) -> List[ImageChunk]: ...

    def update_status(self, chunk_id: str, status: ProcessingStatus) -> bool: ...
    def delete(self, chunk_id: str) -> bool: ...
    def delete_by_source(self, source_file: str) -> int: ...
    def count(self) -> int: ...
    def exists(self, chunk_id: str) -> bool: ...
```

---

## 4. 应用层设计 (Application Layer)

### 4.1 DTOs (Data Transfer Objects)

#### 4.1.1 ImageIngestDTO - 图片导入请求

```python
# 文件: src/multimodal/application/dtos/image_ingest_dto.py

@dataclass
class ImageIngestDTO:
    """
    图片导入请求DTO
    """

    image_paths: List[str]
    source_file: str = ""
    document_type: str = "unknown"
    page_start: int = 0
    options: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_single_image(cls, image_path, **kwargs) -> "ImageIngestDTO": ...
    @classmethod
    def from_pdf(cls, pdf_path, **kwargs) -> "ImageIngestDTO": ...


@dataclass
class ImageIngestResultDTO:
    """
    图片导入结果DTO
    """

    success: bool
    total_count: int = 0
    success_count: int = 0
    failed_count: int = 0
    image_chunks: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    duration_ms: float = 0.0

    @property
    def is_partial_success(self) -> bool: ...
    @property
    def is_full_success(self) -> bool: ...


@dataclass
class PDFIngestDTO:
    pdf_path: str
    document_type: str = "unknown"
    extract_images: bool = True
    min_image_size: int = 100
    output_dir: Optional[str] = None


@dataclass
class PDFIngestResultDTO:
    success: bool
    pdf_path: str
    text_chunks_count: int = 0
    image_chunks_count: int = 0
    extracted_images_count: int = 0
    errors: List[str] = field(default_factory=list)
    duration_ms: float = 0.0
```

#### 4.1.2 MultimodalQueryDTO - 查询请求

```python
# 文件: src/multimodal/application/dtos/multimodal_query_dto.py

@dataclass
class MultimodalQueryDTO:
    """
    多模态查询请求DTO
    """

    query: str
    k: int = 3
    include_images: bool = True
    include_text: bool = True
    document_types: List[str] = field(default_factory=list)
    image_path: Optional[str] = None
    options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ImageSourceDTO:
    chunk_id: str
    image_path: str
    description: str
    ocr_text: str
    source_file: str
    page_number: int
    relevance_score: float = 0.0
    thumbnail_path: Optional[str] = None


@dataclass
class TextSourceDTO:
    chunk_id: str
    content: str
    source_file: str
    page_number: int
    relevance_score: float = 0.0


@dataclass
class MultimodalQueryResultDTO:
    """
    多模态查询结果DTO
    """

    query: str
    answer: str
    text_sources: List[TextSourceDTO] = field(default_factory=list)
    image_sources: List[ImageSourceDTO] = field(default_factory=list)
    total_sources: int = 0
    confidence: float = 0.0
    duration_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]: ...


@dataclass
class ImageQueryDTO:
    image_path: str
    query: str
    options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ImageQueryResultDTO:
    image_path: str
    query: str
    answer: str
    detected_text: str = ""
    confidence: float = 0.0
    duration_ms: float = 0.0
```

### 4.2 应用服务 (Application Services)

#### 4.2.1 MultimodalIngestService - 导入服务

```python
# 文件: src/multimodal/application/services/multimodal_ingest_service.py

class MultimodalIngestService(ABC):
    """
    多模态导入应用服务
    协调OCR、VLM、PDF提取器进行文档导入

    Use Cases:
        UC1: 上传单张图片并导入知识库
        UC2: 批量上传多张图片并导入知识库
        UC3: 从PDF提取内嵌图片并导入知识库
        UC4: 导入整个文件夹的图片和PDF
    """

    def ingest_image(self, dto: ImageIngestDTO) -> ImageIngestResultDTO:
        """
        UC1/UC2: 导入图片
        """
        ...

    def ingest_pdf(self, dto: PDFIngestDTO) -> PDFIngestResultDTO:
        """
        UC3: 导入PDF（文本+内嵌图片）
        """
        ...

    def ingest_folder(
        self,
        folder_path: str,
        document_type: str = "unknown",
    ) -> Dict[str, Any]:
        """
        UC4: 导入整个文件夹
        """
        ...

    def get_processing_status(self, source_file: str) -> Dict[str, Any]: ...
    def delete_by_source(self, source_file: str) -> int: ...
```

#### 4.2.2 MultimodalQueryService - 查询服务

```python
# 文件: src/multimodal/application/services/multimodal_query_service.py

class MultimodalQueryService(ABC):
    """
    多模态查询应用服务
    协调RAG检索和VLM推理进行问答

    Use Cases:
        UC5: 文本+图片混合检索问答
        UC6: 基于上传图片的问答
        UC7: 仅图片检索
    """

    def query(self, dto: MultimodalQueryDTO) -> MultimodalQueryResultDTO:
        """
        UC5: 混合检索问答
        流程:
            1. 文本检索 (RAGAssistant)
            2. 图片检索 (ImageChunkRepository)
            3. 组合上下文
            4. LLM生成答案
        """
        ...

    def query_with_image(self, dto: ImageQueryDTO) -> ImageQueryResultDTO:
        """
        UC6: 基于图片问答
        流程:
            1. OCR提取文字
            2. VLM分析图片+回答
        """
        ...

    def search_images(self, query: str, k: int = 3) -> List[ImageSourceDTO]:
        """
        UC7: 仅图片检索
        """
        ...
```

---

## 5. 基础设施层设计 (Infrastructure Layer)

### 5.1 OCR引擎实现

```python
# 文件: src/multimodal/infrastructure/ocr/paddleocr_engine.py

class PaddleOCREngine(MultimodalProcessingService):
    """
    PaddleOCR引擎实现
    设备: CPU (异构计算设计)
    """

    PREDEFINED_CONFIG = {
        "lang": "ch",
        "use_angle_cls": True,
        "use_gpu": False,  # 固定CPU
        "det_db_thresh": 0.3,
        "rec_batch_num": 16,
    }

    def __init__(self, config: Dict[str, Any] = None): ...

    def extract_text_from_image(self, image_path: str) -> Tuple[str, List[Dict]]:
        """
        返回: (完整文字, [{"text": "...", "bbox": BoundingBox, "confidence": 0.9}, ...])
        """
        ...

    def process_image(self, image_path, source_file, page_number, options) -> ProcessingResult:
        """
        完整流程: OCR + 生成ImageChunk
        """
        ocr_text, text_blocks = self.extract_text_from_image(image_path)
        # 创建ImageChunk（不含VLM描述，由调用方补充）
        ...
```

### 5.2 VLM引擎实现

```python
# 文件: src/multimodal/infrastructure/vlm/qwen_vl_engine.py

class QwenVLEngine(MultimodalProcessingService):
    """
    Qwen-VL-2B 视觉语言模型引擎
    设备: GPU/NPU (INT4量化, ~1.5GB显存)
    """

    PREDEFINED_VLMS = {
        "qwen-vl-2b": {
            "repo_id": "Qwen/Qwen-VL-2B",
            "quantization": "int4",
            "max_new_tokens": 256,
            "temperature": 0.7,
        }
    }

    def __init__(
        self,
        model_key: str = "qwen-vl-2b",
        device: str = None,  # auto检测
        model_dir: str = "./models",
    ):
        """
        初始化:
            1. DeviceManager检测最优设备
            2. 加载模型 (INT4量化)
            3. 分配 ~1.5GB 显存
        """
        ...

    def generate_image_description(
        self,
        image_path: str,
        ocr_text: str = "",
        prompt: str = None,
    ) -> str:
        """
        生成图片描述
        使用OCR结果作为上下文，提升描述质量
        """
        default_prompt = f"""请详细描述这张图片的内容，包括：
1. 图片中的主要元素和场景
2. 文字信息（如有）：{ocr_text if ocr_text else '无'}
3. 图片的类型和用途

请用中文回答。"""
        ...

    def analyze_image_with_query(
        self,
        image_path: str,
        query: str,
    ) -> str:
        """
        基于问题分析图片
        """
        prompt = f"""图片问题: {query}

请根据图片内容回答问题。如果图片中没有相关信息，请说明"图片中未包含此信息"。"""
        ...

    def process_image(self, image_path, source_file, page_number, options) -> ProcessingResult:
        """
        完整流程: OCR -> VLM描述 -> 生成完整ImageChunk
        """
        ...
```

### 5.3 PDF图片提取器

```python
# 文件: src/multimodal/infrastructure/pdf/pdf_image_extractor.py

class PDFImageExtractor(PDFImageExtractionService):
    """
    PDF内嵌图片提取器
    使用 pdfplumber 或 PyMuPDF
    """

    def __init__(self, output_dir: str = "./temp_pdf_images"): ...

    def extract_images_from_pdf(
        self,
        pdf_path: str,
        output_dir: str = None,
        min_size: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Returns: [{"page": 1, "image_path": "/path/to/img.jpg", "bbox": [...], "size": (w,h)}, ...]
        """
        ...

    def extract_images_from_page(
        self,
        pdf_path: str,
        page_number: int,
        output_dir: str = None,
    ) -> List[Dict[str, Any]]: ...
```

### 5.4 设备管理器

```python
# 文件: src/multimodal/infrastructure/device/device_manager.py

class DeviceManager:
    """
    异构计算设备管理器
    实现 NPU > GPU > CPU 优先级自动选择
    """

    DEVICE_PRIORITY = ["npu", "cuda", "cpu"]

    def __init__(self, forced_device: str = None): ...

    def get_device(self) -> str:
        """
        获取最优可用设备
        1. 强制指定时验证可用性
        2. 按优先级检测
        """
        ...

    def get_vlm_device(self) -> str:
        """
        VLM专用设备（GPU/NPU）
        """
        if self._npu_available:
            return "npu:0"
        if self._cuda_available:
            return "cuda:0"
        raise RuntimeError("No accelerator device available")

    def get_ocr_device(self) -> str:
        """OCR固定CPU"""
        return "cpu"

    def get_cpu_device(self) -> str:
        """CPU设备"""
        return "cpu"

    def get_device_info(self) -> Dict[str, Any]:
        """
        返回设备信息
        {
            "vlm_device": "cuda:0",
            "ocr_device": "cpu",
            "total_memory_mb": 8192,
            "available_memory_mb": 6144,
        }
        """
        ...

    def get_allocation_plan(self) -> Dict[str, int]:
        """获取8GB显存分配方案"""
        ...
```

### 5.5 仓储实现

```python
# 文件: src/multimodal/infrastructure/persistence/chroma_image_chunk_repository.py

class ChromaImageChunkRepository(ImageChunkRepository):
    """
    Chroma向量数据库仓储实现
    """

    COLLECTION_NAME = "multimodal_image_chunks"

    def __init__(
        self,
        persist_dir: str = "./chroma_db_multimodal",
        embedding_model: str = "BAAI/bge-large-zh-v1.5",
    ):
        """
        复用现有BGE嵌入模型
        设备: CPU (异构计算设计)
        """
        ...

    def save(self, chunk: ImageChunk) -> ImageChunk:
        """保存单个图片片段"""
        ...

    def save_batch(self, chunks: List[ImageChunk]) -> List[ImageChunk]:
        """批量保存"""
        ...

    def similarity_search(
        self,
        query: str,
        k: int = 3,
        filter_criteria: Dict[str, Any] = None,
    ) -> List[ImageChunk]:
        """
        相似度检索
        使用page_content（VLM描述）作为检索文本
        """
        ...
```

---

## 6. 接口层设计 (Interface Layer)

### 6.1 API路由

```python
# 文件: src/multimodal/interface/api/routes.py

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Optional

router = APIRouter(prefix="/api/multimodal", tags=["multimodal"])


@router.post("/image/ingest")
async def ingest_image(
    files: List[UploadFile] = File(...),
    document_type: str = Form("unknown"),
) -> Dict[str, Any]:
    """
    UC1/UC2: 上传图片并导入知识库

    Request:
        - files: 图片文件列表
        - document_type: 文档类型

    Response:
        {
            "success": true,
            "total_count": 3,
            "success_count": 3,
            "image_chunks": [...]
        }
    """
    ...


@router.post("/pdf/ingest")
async def ingest_pdf(
    file: UploadFile = File(...),
    document_type: str = Form("unknown"),
    extract_images: bool = Form(True),
) -> Dict[str, Any]:
    """
    UC3: 上传PDF并导入（文本+内嵌图片）

    Request:
        - file: PDF文件
        - document_type: 文档类型
        - extract_images: 是否提取内嵌图片

    Response:
        {
            "success": true,
            "text_chunks_count": 10,
            "image_chunks_count": 5,
            "extracted_images_count": 5,
        }
    """
    ...


@router.post("/query")
async def query(
    query: str = Form(...),
    k: int = Form(3),
    include_images: bool = Form(True),
    include_text: bool = Form(True),
) -> MultimodalQueryResultDTO:
    """
    UC5: 文本+图片混合检索问答

    Response:
        {
            "query": "...",
            "answer": "...",
            "text_sources": [...],
            "image_sources": [...],
        }
    """
    ...


@router.post("/query/image")
async def query_with_image(
    file: UploadFile = File(...),
    query: str = Form(...),
) -> ImageQueryResultDTO:
    """
    UC6: 基于上传图片问答

    Response:
        {
            "image_path": "...",
            "query": "...",
            "answer": "...",
            "detected_text": "...",
        }
    """
    ...


@router.get("/search/images")
async def search_images(
    query: str,
    k: int = 3,
    document_type: Optional[str] = None,
) -> List[ImageSourceDTO]:
    """
    UC7: 仅图片检索
    """
    ...


@router.delete("/source/{source_file}")
async def delete_by_source(source_file: str) -> Dict[str, int]:
    """
    删除指定来源的所有片段
    """
    ...


@router.get("/status/{source_file}")
async def get_processing_status(source_file: str) -> Dict[str, Any]:
    """
    获取处理状态
    """
    ...
```

### 6.2 Streamlit UI组件

```python
# 文件: src/multimodal/interface/ui/components.py

def render_multimodal_sidebar(kb: KnowledgeBase) -> None:
    """
    侧边栏多模态组件

    Components:
        1. 多模态模式开关
        2. 图片上传器
        3. PDF上传器
        4. 处理状态显示
        5. 显示模式切换
    """
    st.markdown("---")
    st.markdown("🖼️ 多模态知识库")

    multimodal_enabled = st.checkbox(
        "启用多模态模式",
        value=False,
        help="支持图片和PDF内嵌图片的OCR识别和VLM分析"
    )

    if multimodal_enabled:
        tab1, tab2 = st.tabs(["📷 图片上传", "📄 PDF上传"])

        with tab1:
            uploaded_images = st.file_uploader(
                "上传图片",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True,
                help="支持JPG、PNG格式"
            )

            if uploaded_images:
                if st.button("📷 分析并添加到知识库", type="primary"):
                    with st.spinner("处理图片中..."):
                        for img in uploaded_images:
                            # 调用 MultimodalIngestService
                            ...

        with tab2:
            uploaded_pdf = st.file_uploader(
                "上传PDF",
                type=["pdf"],
                help="支持PDF文件，将自动提取内嵌图片"
            )

            if uploaded_pdf:
                if st.button("📄 分析并添加到知识库", type="primary"):
                    with st.spinner("处理PDF中..."):
                        # 调用 MultimodalIngestService.ingest_pdf
                        ...

        show_images = st.checkbox("检索结果显示图片", value=True)


def render_image_sources(image_sources: List[ImageSourceDTO]) -> None:
    """
    渲染图片来源
    """
    if not image_sources:
        return

    st.markdown("### 🖼️ 相关图片")

    for idx, img in enumerate(image_sources):
        with st.expander(f"图片 {idx + 1}: {img.description[:50]}...", expanded=True):
            try:
                st.image(img.image_path, width=300)
            except Exception:
                st.warning(f"无法显示图片: {img.image_path}")

            st.markdown(f"**描述**: {img.description}")
            if img.ocr_text:
                st.markdown(f"**OCR文字**: {img.ocr_text}")
            st.markdown(f"**来源**: {img.source_file} (第{img.page_number}页)")
            st.markdown(f"**相关度**: {img.relevance_score:.2f}")
```

---

## 7. 配置文件设计

### 7.1 config.yaml 新增多模态配置

```yaml
# 文件: config/config.yaml

# === 现有配置保持不变 ===

# 多模态RAG配置
multimodal:
  enabled: true
  vlm_model: "qwen-vl-2b"
  vlm_quantization: "int4"           # INT4量化，适配8GB显存
  ocr_engine: "paddleocr"            # 或 "easyocr"
  device_priority: "auto"            # auto/npu/cuda/cpu

# 显存配置（8GB基准）
memory:
  total_mb: 8192
  gpu_reserved_mb: 3584              # 预留3.5GB
  vlm_required_mb: 1536              # VLM约1.5GB (INT4)
  cpu_memory_mb: 3072                # OCR+嵌入+向量库约3GB

# PDF处理配置
pdf:
  extract_images: true
  min_image_size: 100               # 最小图片尺寸（像素）
  output_dir: "./temp_pdf_images"
  supported_types: [".pdf"]

# 向量数据库配置（多模态）
multimodal_vectorstore:
  persist_dir: "./chroma_db_multimodal"
  collection_name: "multimodal_image_chunks"
  embedding_model: "BAAI/bge-large-zh-v1.5"

# 设备配置
device:
  vlm_device: "auto"                # NPU > GPU > CPU
  ocr_device: "cpu"                 # 固定CPU
  embedding_device: "cpu"            # 固定CPU
```

---

## 8. 文件结构

```
ascend-rag-assistant/
├── config/
│   └── config.yaml                    # 【修改】新增多模态配置
│
├── src/
│   ├── skill_tree/                    # 【现有】
│   ├── knowledge_base.py             # 【现有】
│   ├── rag_engine.py                  # 【现有】
│   ├── ascend_adapter.py              # 【现有】
│   │
│   └── multimodal/                   # 【新增】多模态RAG模块
│       │
│       ├── __init__.py               # 模块导出
│       │
│       ├── domain/                    # 【DDD】领域层
│       │   ├── __init__.py
│       │   ├── entities/
│       │   │   ├── __init__.py
│       │   │   ├── image_chunk.py     # ImageChunk实体
│       │   │   └── multimodal_document.py  # MultimodalDocument聚合根
│       │   ├── value_objects/
│       │   │   ├── __init__.py
│       │   │   ├── bounding_box.py    # BoundingBox值对象
│       │   │   ├── device_type.py     # DeviceType/DevicePriority
│       │   │   └── processing_status.py  # ProcessingStatus/Result
│       │   ├── services/
│       │   │   ├── __init__.py
│       │   │   └── multimodal_processing_service.py  # 领域服务接口
│       │   └── repositories/
│       │       ├── __init__.py
│       │       └── image_chunk_repository.py  # 仓储接口
│       │
│       ├── application/              # 【DDD】应用层
│       │   ├── __init__.py
│       │   ├── dtos/
│       │   │   ├── __init__.py
│       │   │   ├── image_ingest_dto.py    # 导入DTO
│       │   │   └── multimodal_query_dto.py  # 查询DTO
│       │   └── services/
│       │       ├── __init__.py
│       │       ├── multimodal_ingest_service.py  # 导入服务
│       │       └── multimodal_query_service.py  # 查询服务
│       │
│       ├── infrastructure/            # 【DDD】基础设施层
│       │   ├── __init__.py
│       │   ├── ocr/
│       │   │   ├── __init__.py
│       │   │   └── paddleocr_engine.py  # PaddleOCR实现
│       │   ├── vlm/
│       │   │   ├── __init__.py
│       │   │   └── qwen_vl_engine.py    # Qwen-VL实现
│       │   ├── pdf/
│       │   │   ├── __init__.py
│       │   │   └── pdf_image_extractor.py  # PDF提取器
│       │   ├── device/
│       │   │   ├── __init__.py
│       │   │   └── device_manager.py   # 设备管理器
│       │   └── persistence/
│       │       ├── __init__.py
│       │       └── chroma_image_chunk_repository.py  # Chroma实现
│       │
│       └── interface/                 # 【DDD】接口层
│           ├── __init__.py
│           ├── api/
│           │   ├── __init__.py
│           │   └── routes.py           # FastAPI路由
│           └── ui/
│               ├── __init__.py
│               └── components.py       # Streamlit组件
│
├── app.py                             # 【修改】集成多模态UI
├── server.py                          # 【修改】注册多模态API
└── requirements.txt                   # 【修改】新增依赖
```

---

## 9. 模块依赖关系

```
┌─────────────────────────────────────────────────────────────────┐
│                           app.py                                │
│                    Streamlit 主应用                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    interface/ui/components.py                   │
│                  Streamlit UI组件（侧边栏等）                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                application/services/                             │
│     MultimodalIngestService      MultimodalQueryService          │
│              │                              │                   │
│              ▼                              ▼                   │
│  ┌───────────────────────────────────────────────────────┐     │
│  │              domain/services/                          │     │
│  │  MultimodalProcessingService (Interface)               │     │
│  │  ImageIndexingService (Interface)                      │     │
│  │  PDFImageExtractionService (Interface)                 │     │
│  └───────────────────────────────────────────────────────┘     │
│              │                              │                   │
└──────────────┼──────────────────────────────┼──────────────────┘
               │                              │
               ▼                              ▼
┌──────────────────────────┐  ┌──────────────────────────────────┐
│   infrastructure/ocr/     │  │   infrastructure/vlm/            │
│   PaddleOCREngine         │  │   QwenVLEngine                   │
│   (CPU运行)                │  │   (GPU/NPU运行, INT4)            │
└──────────────────────────┘  └──────────────────────────────────┘
               │                              │
               │                              │
               ▼                              ▼
┌──────────────────────────┐  ┌──────────────────────────────────┐
│   infrastructure/pdf/    │  │   infrastructure/device/          │
│   PDFImageExtractor       │  │   DeviceManager                  │
└──────────────────────────┘  │   (NPU > GPU > CPU)               │
                              └──────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│               infrastructure/persistence/                         │
│         ChromaImageChunkRepository                                │
│         (复用BGE嵌入模型, CPU运行)                               │
└──────────────────────────────────────────────────────────────────┘
```

---

## 10. Use Case 流程图

### UC1: 上传单张图片并导入知识库

```
用户上传图片
      │
      ▼
[MultimodalIngestService.ingest_image]
      │
      ├─▶ [PaddleOCREngine.extract_text]  (CPU)
      │         │
      │         ▼
      │    返回: (ocr_text, text_blocks)
      │
      ├─▶ [QwenVLEngine.generate_description]  (GPU/NPU)
      │         │
      │         ▼
      │    返回: page_content
      │
      ▼
[创建ImageChunk]
      │
      ├─ page_content = VLM描述
      ├─ ocr_text = OCR结果
      ├─ status = COMPLETED
      │
      ▼
[ChromaImageChunkRepository.save]
      │
      ▼
成功返回 ImageIngestResultDTO
```

### UC3: 从PDF提取内嵌图片并导入

```
用户上传PDF
      │
      ▼
[PDFImageExtractor.extract_images_from_pdf]
      │
      ├─ 遍历每一页
      ├─ 提取内嵌图片
      ├─ 保存到 output_dir
      │
      ▼
返回: [{"page": 1, "image_path": "...", ...}, ...]
      │
      ▼
[MultimodalIngestService.ingest_image]
      │
      ├─ 遍历每个image_path
      ├─ 执行 UC1 流程
      │
      ▼
成功返回 PDFIngestResultDTO
```

### UC5: 文本+图片混合检索问答

```
用户提问
      │
      ▼
[MultimodalQueryService.query]
      │
      ├─▶ [RAGAssistant.similarity_search]  (文本检索)
      │         │
      │         ▼
      │    返回: text_sources
      │
      ├─▶ [ChromaImageChunkRepository.similarity_search]  (图片检索)
      │         │
      │         ▼
      │    返回: image_sources
      │
      ▼
[组合上下文]
      │
      ├─ "【文本资料】\n" + text_sources
      ├─ "【图片资料】\n" + image_sources
      │
      ▼
[LLM生成答案] (复用RAGAssistant.llm)
      │
      ▼
返回 MultimodalQueryResultDTO
```

---

## 11. 验收标准对照表

| 验收标准 | 实现位置 | Use Case |
|---------|---------|----------|
| 上传图片OCR+分析存入知识库 | `infrastructure/ocr` + `infrastructure/vlm` | UC1 |
| PDF内嵌图片提取处理 | `infrastructure/pdf` | UC3 |
| 侧边栏显示图片上传选项 | `interface/ui/components.py` | UI |
| 检索时返回图片相关内容 | `application/services/query_service` | UC5 |
| OCR在CPU运行，VLM在GPU/NPU运行 | `infrastructure/device/device_manager.py` | 架构 |

---

## 12. 技术依赖

```txt
# requirements.txt 新增依赖

# OCR
paddleocr>=2.7.0
paddlepaddle>=2.5.0  # CPU版本

# 或可选 EasyOCR
easyocr>=1.7.0

# VLM
transformers>=4.35.0
accelerate>=0.25.0
bitsandbytes>=0.41.0  # INT4量化

# PDF图片提取
pdfplumber>=0.10.0
PyMuPDF>=1.23.0

# 向量数据库（复用现有）
chromadb>=0.4.0

# 设备检测（昇腾）
cann>=7.0.0  # 可选
```

---

## 13. 附录：Use Case 清单

| ID | 名称 | 输入 | 输出 |
|----|------|------|------|
| UC1 | 上传单张图片并导入知识库 | 图片文件 | ImageIngestResultDTO |
| UC2 | 批量上传多张图片并导入知识库 | 图片文件列表 | ImageIngestResultDTO |
| UC3 | 从PDF提取内嵌图片并导入 | PDF文件 | PDFIngestResultDTO |
| UC4 | 导入整个文件夹的图片和PDF | 文件夹路径 | Dict统计信息 |
| UC5 | 文本+图片混合检索问答 | 查询文本 | MultimodalQueryResultDTO |
| UC6 | 基于上传图片的问答 | 图片+问题 | ImageQueryResultDTO |
| UC7 | 仅图片检索 | 查询文本 | List[ImageSourceDTO] |

---

**文档结束**