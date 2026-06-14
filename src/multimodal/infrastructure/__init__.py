"""
Infrastructure Layer - 基础设施层
保留PDF处理等基础设施组件
"""

from .pdf.pdf_image_extractor import PDFImageExtractor

__all__ = [
    "PDFImageExtractor",
]
