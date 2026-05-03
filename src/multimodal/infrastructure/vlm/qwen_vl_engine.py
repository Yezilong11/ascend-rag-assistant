"""
VLM Infrastructure - Qwen-VL视觉语言模型引擎
支持 GPU/NPU 运行，INT4量化
"""

import os
from typing import Tuple, List, Dict, Any
import torch

from ...domain.value_objects.processing_status import ProcessingResult
from ...domain.services.multimodal_processing_service import MultimodalProcessingService

MODELSCOPE_AVAILABLE = True
try:
    from modelscope import snapshot_download
except ImportError:
    MODELSCOPE_AVAILABLE = False


class QwenVLEngine(MultimodalProcessingService):
    """
    Qwen-VL-2B 视觉语言模型引擎
    设备: GPU/NPU (INT4量化, ~1.5GB显存)
    """

    PREDEFINED_VLMS = {
        "qwen-vl-2b": {
            "repo_id": "Qwen/Qwen3-VL-2B-Instruct",
            "ms_repo_id": "Qwen/Qwen3-VL-2B-Instruct",
            "quantization": "int4",
            "max_new_tokens": 256,
            "temperature": 0.7,
        }
    }

    def __init__(
        self,
        model_key: str = "qwen-vl-2b",
        model_dir: str = "./models",
        config: Dict[str, Any] = None,
    ):
        self._model_key = model_key
        self._model_config = self.PREDEFINED_VLMS.get(model_key, self.PREDEFINED_VLMS["qwen-vl-2b"])
        self._model_dir = model_dir
        self._config = {**self._model_config, **(config or {})}

        self._model = None
        self._processor = None
        self._initialized = False
        self._device = None

    def _get_device(self) -> str:
        """获取可用设备"""
        if torch.cuda.is_available():
            return "cuda:0"
        try:
            import acl
            return "npu:0"
        except ImportError:
            return "cpu"

    def _download_model(self) -> str:
        """从ModelScope下载模型到本地"""
        repo_id = self._model_config["repo_id"]
        ms_repo_id = self._model_config.get("ms_repo_id", repo_id)
        local_model_name = repo_id.split("/")[-1]
        target_dir = os.path.join(self._model_dir, local_model_name)

        if os.path.exists(target_dir):
            print(f"✅ 本地VLM模型已存在: {target_dir}")
            return target_dir

        if not MODELSCOPE_AVAILABLE:
            raise ImportError(
                "请安装ModelScope: pip install modelscope\n"
                "然后手动下载模型到 models/Qwen3-VL-2B-Instruct 目录"
            )

        print(f"🔍 本地VLM模型未找到，正在从ModelScope下载...")
        print(f"   目标路径: {target_dir}")

        try:
            snapshot_download(ms_repo_id, local_dir=target_dir)
            print(f"✅ ModelScope下载完成: {target_dir}")
            return target_dir

        except Exception as e:
            raise RuntimeError(f"ModelScope下载失败: {e}")

    def _initialize(self):
        """初始化VLM模型"""
        if self._initialized:
            return

        self._device = self._get_device()
        if self._device == "cpu":
            raise RuntimeError("Qwen-VL需要GPU/NPU，不能在CPU上运行")

        model_path = self._download_model()

        print(f"加载VLM模型: {model_path} -> {self._device}")

        from transformers import AutoModelForVision2Seq, AutoProcessor
        import qwen_vl_utils

        self._qwen_vl_utils = qwen_vl_utils

        load_kwargs = {"trust_remote_code": True, "torch_dtype": torch.float16}

        if self._model_config.get("quantization") == "int4":
            from transformers import BitsAndBytesConfig
            load_kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
            )

        load_kwargs["device_map"] = "auto"

        self._processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)
        self._model = AutoModelForVision2Seq.from_pretrained(model_path, **load_kwargs)

        self._initialized = True
        print("✅ VLM模型加载完成")

    def generate_image_description(
        self,
        image_path: str,
        ocr_text: str = "",
        prompt: str = None,
    ) -> str:
        """生成图片描述"""
        self._initialize()

        if prompt is None:
            ocr_context = f"图片中的文字: {ocr_text}" if ocr_text else "图片中无文字"
            prompt = f"请详细描述这张图片，包括: 1.主要内容和场景 2.{ocr_context} 3.图片类型。用中文回答。"

        messages = [{"role": "user", "content": [{"type": "image", "image": image_path}, {"type": "text", "text": prompt}]}]

        text = self._processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        image_inputs, _ = self._qwen_vl_utils.process_vision_info(messages)
        inputs = self._processor(text=[text], images=image_inputs, padding=True, return_tensors="pt")
        inputs = inputs.to(self._model.device)

        generated_ids = self._model.generate(
            **inputs,
            max_new_tokens=self._config.get("max_new_tokens", 256),
            temperature=self._config.get("temperature", 0.7),
        )

        output_text = self._processor.batch_decode(
            generated_ids[:, len(inputs.input_ids[0]):],
            skip_special_tokens=True,
        )[0]

        return output_text.strip()

    def analyze_image_with_query(self, image_path: str, query: str) -> str:
        """基于问题分析图片"""
        self._initialize()
        prompt = f"图片问题: {query}\n请根据图片内容回答。如果图片中没有相关信息，请说明。用中文回答。"
        return self.generate_image_description(image_path, prompt=prompt)

    def extract_text_from_image(self, image_path: str) -> Tuple[str, List[Dict]]:
        return "", []

    def process_image(self, image_path: str, source_file: str = "", page_number: int = 0, options: Dict = None):
        import time
        start = time.time()
        try:
            self._initialize()
            return ProcessingResult.success(data={"image_path": image_path}, duration_ms=(time.time() - start) * 1000)
        except Exception as e:
            return ProcessingResult.failure(error=str(e), duration_ms=(time.time() - start) * 1000)

    def process_image_batch(self, image_paths: List[str], source_file: str = "", start_page: int = 0, options: Dict = None):
        results = [self.process_image(p, source_file, start_page + i, options) for i, p in enumerate(image_paths)]
        return ProcessingResult.partial(data=results, success_count=sum(1 for r in results if r.is_success), failed_count=sum(1 for r in results if r.is_failure))