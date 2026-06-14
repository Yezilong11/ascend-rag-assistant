"""
OCR引擎 - EasyOCR实现
使用 EasyOCR 进行文字识别
设备: CPU (异构计算设计)
"""

import os
from typing import Tuple, List, Dict, Any, Optional
import time

from ..domain.value_objects.bounding_box import BoundingBox
from ..domain.value_objects.processing_status import ProcessingStatus, ProcessingResult
from ..domain.value_objects.processing_status import ProcessingStatus as PS


class EasyOCREngine:
    """
    OCR引擎实现
    使用 EasyOCR 进行文字识别
    设备: CPU (异构计算设计)
    """

    def __init__(self, config: Dict[str, Any] = None):
        self._config = config or {}
        self._easyocr_engine = None
        self._initialized = False
        self._engine_type = "unknown"

    def _initialize(self):
        """延迟初始化OCR引擎"""
        if self._initialized:
            return

        import logging
        logging.getLogger("easyocr").setLevel(logging.ERROR)

        try:
            import easyocr
            self._easyocr_engine = easyocr.Reader(['ch_sim', 'en'], gpu=False, verbose=False)
            self._engine_type = "easyocr"
        except ImportError:
            print("⚠️ easyocr未安装，使用基础OCR回退模式")
            self._easyocr_engine = None
            self._engine_type = "fallback"
        except Exception as e:
            print(f"⚠️ EasyOCR初始化失败: {e}，使用基础OCR回退模式")
            self._easyocr_engine = None
            self._engine_type = "fallback"

        self._initialized = True

    def extract_text_from_image(self, image_path: str) -> Tuple[str, List[Dict]]:
        """从图片提取文字（OCR）"""
        self._initialize()

        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")

        if self._easyocr_engine is not None:
            return self._extract_easyocr(image_path)
        else:
            return self._extract_fallback(image_path)

    def _extract_easyocr(self, image_path: str) -> Tuple[str, List[Dict]]:
        """使用EasyOCR提取"""
        self._engine_type = "easyocr"
        result = self._easyocr_engine.readtext(image_path)

        if not result:
            return "", []

        text_blocks = []
        full_text_parts = []

        for item in result:
            if len(item) >= 2:
                bbox_data = item[0]
                text = item[1]
                confidence = item[2] if len(item) > 2 else 0.9

                try:
                    if len(bbox_data) >= 4:
                        x_coords = [p[0] for p in bbox_data]
                        y_coords = [p[1] for p in bbox_data]
                        bbox = BoundingBox(
                            x1=min(x_coords),
                            y1=min(y_coords),
                            x2=max(x_coords),
                            y2=max(y_coords),
                        )
                    else:
                        continue
                except Exception:
                    continue

                text_blocks.append({
                    "text": text,
                    "bbox": bbox,
                    "confidence": confidence,
                })
                full_text_parts.append(text)

        full_text = " ".join(full_text_parts)
        return full_text, text_blocks

    def _extract_fallback(self, image_path: str) -> Tuple[str, List[Dict]]:
        """基础OCR回退：使用Pillow提取图片基本信息"""
        self._engine_type = "fallback"
        try:
            from PIL import Image
            img = Image.open(image_path)
            info = f"[图片] {os.path.basename(image_path)} ({img.size[0]}x{img.size[1]}) {img.mode})"
            return info, []
        except Exception:
            return f"[图片] {os.path.basename(image_path)}", []

    def generate_image_description(
        self,
        image_path: str,
        ocr_text: str = "",
        prompt: str = None,
    ) -> str:
        """OCR引擎不生成图片描述，返回OCR文字作为描述"""
        return ocr_text

    def analyze_image_with_query(
        self,
        image_path: str,
        query: str,
    ) -> str:
        """OCR引擎不支持图片问答"""
        return "请使用VLM引擎进行图片问答分析"
