"""
PDF Infrastructure - PDF图片提取器
从PDF中提取内嵌图片
"""

import os
from typing import List, Dict, Any, Optional
import uuid

from ...domain.services.multimodal_processing_service import PDFImageExtractionService


class PDFImageExtractor(PDFImageExtractionService):
    """
    PDF内嵌图片提取器
    使用 pdfplumber 或 PyMuPDF
    """

    def __init__(self, output_dir: str = "./temp_pdf_images"):
        self._output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def extract_images_from_pdf(
        self,
        pdf_path: str,
        output_dir: str = None,
        min_size: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        从PDF提取所有图片
        Returns: [{"page": 1, "image_path": "...", "bbox": [...], "size": (w,h)}, ...]
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")

        output_dir = output_dir or self._output_dir
        os.makedirs(output_dir, exist_ok=True)

        extracted_images = []

        try:
            import pdfplumber

            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    images = self._extract_images_from_page_plumber(
                        page, page_num, output_dir, min_size
                    )
                    extracted_images.extend(images)

        except ImportError:
            try:
                import fitz

                doc = fitz.open(pdf_path)
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    images = self._extract_images_from_page_pymupdf(
                        page, page_num + 1, output_dir, min_size
                    )
                    extracted_images.extend(images)
                doc.close()

            except ImportError:
                raise ImportError(
                    "PDF处理依赖未安装。请运行: pip install pdfplumber\n"
                    "或: pip install PyMuPDF"
                )

        return extracted_images

    def _extract_images_from_page_plumber(
        self,
        page,
        page_num: int,
        output_dir: str,
        min_size: int,
    ) -> List[Dict[str, Any]]:
        """使用pdfplumber从页面提取图片"""
        extracted = []

        try:
            images = page.images
            for img_idx, img in enumerate(images):
                x0 = img.get("x0", 0)
                y0 = img.get("top", 0)
                x1 = img.get("x1", 0)
                y1 = img.get("bottom", 0)

                width = x1 - x0
                height = y1 - y0

                if width < min_size or height < min_size:
                    continue

                img_path = os.path.join(
                    output_dir,
                    f"pdf_{page_num}_img_{img_idx}_{uuid.uuid4().hex[:8]}.png"
                )

                try:
                    page.to_image().save(img_path, resolution=150)
                    extracted.append({
                        "page": page_num,
                        "image_path": img_path,
                        "bbox": [x0, y0, x1, y1],
                        "size": (width, height),
                    })
                except Exception:
                    continue

        except Exception:
            pass

        return extracted

    def _extract_images_from_page_pymupdf(
        self,
        page,
        page_num: int,
        output_dir: str,
        min_size: int,
    ) -> List[Dict[str, Any]]:
        """使用PyMuPDF从页面提取图片"""
        extracted = []

        try:
            image_list = page.get_images(full=True)

            for img_idx, img in enumerate(image_list):
                xref = img[0]
                base_image = page.parent.extract_image(xref)

                if not base_image:
                    continue

                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                width = base_image.get("width", 0)
                height = base_image.get("height", 0)

                if width < min_size or height < min_size:
                    continue

                img_path = os.path.join(
                    output_dir,
                    f"pdf_{page_num}_img_{img_idx}_{uuid.uuid4().hex[:8]}.{image_ext}"
                )

                with open(img_path, "wb") as f:
                    f.write(image_bytes)

                extracted.append({
                    "page": page_num,
                    "image_path": img_path,
                    "bbox": [0, 0, width, height],
                    "size": (width, height),
                })

        except Exception:
            pass

        return extracted

    def extract_images_from_page(
        self,
        pdf_path: str,
        page_number: int,
        output_dir: str = None,
    ) -> List[Dict[str, Any]]:
        """从指定页面提取图片"""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")

        output_dir = output_dir or self._output_dir
        os.makedirs(output_dir, exist_ok=True)

        extracted_images = []

        try:
            import pdfplumber

            with pdfplumber.open(pdf_path) as pdf:
                if page_number < 1 or page_number > len(pdf.pages):
                    raise ValueError(f"页码 {page_number} 超出范围")

                page = pdf.pages[page_number - 1]
                extracted_images = self._extract_images_from_page_plumber(
                    page, page_number, output_dir, 100
                )

        except ImportError:
            try:
                import fitz

                doc = fitz.open(pdf_path)
                if page_number < 1 or page_number > len(doc):
                    raise ValueError(f"页码 {page_number} 超出范围")

                page = doc[page_number - 1]
                extracted_images = self._extract_images_from_page_pymupdf(
                    page, page_number, output_dir, 100
                )
                doc.close()

            except ImportError:
                raise ImportError("请安装 pdfplumber 或 PyMuPDF")

        return extracted_images