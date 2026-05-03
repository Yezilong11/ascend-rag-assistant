"""
BoundingBox - 边界框值对象
表示图片或文本在文档中的位置信息
"""

from dataclasses import dataclass
from typing import List, Tuple, Dict, Any, Optional


@dataclass(frozen=True)
class BoundingBox:
    """
    边界框 - 值对象(Value Object)
    不可变，表示二维空间中的矩形区域

    Attributes:
        x1: 左上角X坐标
        y1: 左上角Y坐标
        x2: 右下角X坐标
        y2: 右下角Y坐标
    """

    x1: float
    y1: float
    x2: float
    y2: float

    def __post_init__(self):
        """验证边界框有效性"""
        if self.x1 > self.x2 or self.y1 > self.y2:
            raise ValueError(f"Invalid bounding box: ({self.x1}, {self.y1}, {self.x2}, {self.y2})")

    @property
    def width(self) -> float:
        """获取宽度"""
        return self.x2 - self.x1

    @property
    def height(self) -> float:
        """获取高度"""
        return self.y2 - self.y1

    @property
    def area(self) -> float:
        """获取面积"""
        return self.width * self.height

    @property
    def center(self) -> Tuple[float, float]:
        """获取中心点坐标"""
        return ((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)

    def contains(self, point: Tuple[float, float]) -> bool:
        """检查点是否在边界框内"""
        px, py = point
        return self.x1 <= px <= self.x2 and self.y1 <= py <= self.y2

    def overlaps(self, other: "BoundingBox") -> bool:
        """检查是否与另一个边界框重叠"""
        return not (
            self.x2 < other.x1 or
            self.x1 > other.x2 or
            self.y2 < other.y1 or
            self.y1 > other.y2
        )

    def to_list(self) -> List[float]:
        """转换为列表 [x1, y1, x2, y2]"""
        return [self.x1, self.y1, self.x2, self.y2]

    def to_dict(self) -> Dict[str, float]:
        """转换为字典"""
        return {"x1": self.x1, "y1": self.y1, "x2": self.x2, "y2": self.y2}

    @classmethod
    def from_list(cls, values: List[float]) -> "BoundingBox":
        """从列表创建"""
        if len(values) != 4:
            raise ValueError(f"BoundingBox requires 4 values, got {len(values)}")
        return cls(x1=values[0], y1=values[1], x2=values[2], y2=values[3])

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["BoundingBox"]:
        """从字典创建"""
        if data is None:
            return None
        return cls(
            x1=float(data["x1"]),
            y1=float(data["y1"]),
            x2=float(data["x2"]),
            y2=float(data["y2"]),
        )

    @classmethod
    def from_paddleocr(cls, bbox_data) -> "BoundingBox":
        """
        从PaddleOCR格式创建边界框
        PaddleOCR返回格式: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
        取左上(x1,y1)和右下(x3,y3)
        """
        if not bbox_data or len(bbox_data) < 4:
            raise ValueError(f"Invalid PaddleOCR bbox data: {bbox_data}")
        x_coords = [p[0] for p in bbox_data]
        y_coords = [p[1] for p in bbox_data]
        return cls(
            x1=min(x_coords),
            y1=min(y_coords),
            x2=max(x_coords),
            y2=max(y_coords),
        )

    @classmethod
    def from_easyocr(cls, bbox_data) -> "BoundingBox":
        """从EasyOCR格式创建边界框"""
        return cls.from_paddleocr(bbox_data)

    def __repr__(self) -> str:
        return f"BoundingBox(x1={self.x1}, y1={self.y1}, x2={self.x2}, y2={self.y2})"