"""
OCR Infrastructure - OCR引擎实现
使用 EasyOCR 进行文字识别
设备: CPU (异构计算设计)
"""

import os
from typing import Tuple, List, Dict, Any, Optional
import time

from ...domain.value_objects.bounding_box import BoundingBox
from ...domain.value_objects.processing_status import ProcessingStatus, ProcessingResult
from ...domain.services.multimodal_processing_service import MultimodalProcessingService


class PaddleOCREngine(MultimodalProcessingService):
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

        import easyocr
        self._easyocr_engine = easyocr.Reader(['ch_sim', 'en'], gpu=False, verbose=False)

        self._initialized = True

    def extract_text_from_image(self, image_path: str) -> Tuple[str, List[Dict]]:
        """从图片提取文字（OCR）"""
        self._initialize()

        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")

        return self._extract_easyocr(image_path)

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

    def process_image(
        self,
        image_path: str,
        source_file: str = "",
        page_number: int = 0,
        options: Dict[str, Any] = None,
    ) -> ProcessingResult:
        """处理单张图片（OCR）"""
        start_time = time.time()

        try:
            ocr_text, text_blocks = self.extract_text_from_image(image_path)

            return ProcessingResult.success(
                message=f"OCR处理完成 ({self._engine_type})",
                data={
                    "ocr_text": ocr_text,
                    "text_blocks": text_blocks,
                    "image_path": image_path,
                    "engine_type": self._engine_type,
                },
                duration_ms=(time.time() - start_time) * 1000,
            )

        except Exception as e:
            return ProcessingResult.failure(
                message=f"OCR处理失败: {str(e)}",
                error=str(e),
                duration_ms=(time.time() - start_time) * 1000,
            )

    def process_image_batch(
        self,
        image_paths: List[str],
        source_file: str = "",
        start_page: int = 0,
        options: Dict[str, Any] = None,
    ) -> ProcessingResult:
        """批量处理图片"""
        results = []
        failed_count = 0

        for idx, image_path in enumerate(image_paths):
            result = self.process_image(
                image_path=image_path,
                source_file=source_file,
                page_number=start_page + idx,
                options=options,
            )
            if result.is_success:
                results.append(result.data)
            else:
                failed_count += 1

        return ProcessingResult.partial(
            message=f"批量处理完成，成功{len(results)}个，失败{failed_count}个",
            data=results,
            success_count=len(results),
            failed_count=failed_count,
        )