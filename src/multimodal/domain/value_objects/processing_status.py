"""
ProcessingStatus - 处理状态值对象
定义图片处理的生命周期状态
"""

from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


class ProcessingStatus(Enum):
    """
    处理状态枚举
    """

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"

    def __str__(self) -> str:
        return self.value

    def is_terminal(self) -> bool:
        """是否为终态（已完成或失败）"""
        return self in (ProcessingStatus.COMPLETED, ProcessingStatus.FAILED)

    def is_pending(self) -> bool:
        """是否为待处理状态"""
        return self == ProcessingStatus.PENDING

    def is_processing(self) -> bool:
        """是否为处理中状态"""
        return self == ProcessingStatus.PROCESSING

    def is_successful(self) -> bool:
        """是否成功完成"""
        return self == ProcessingStatus.COMPLETED


@dataclass
class ProcessingResult:
    """
    处理结果值对象
    封装处理操作的返回结果
    """

    status: ProcessingStatus
    message: str = ""
    data: Optional[Any] = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    @property
    def is_success(self) -> bool:
        """是否成功"""
        return self.status == ProcessingStatus.COMPLETED

    @property
    def is_failure(self) -> bool:
        """是否失败"""
        return self.status == ProcessingStatus.FAILED

    @property
    def is_partial(self) -> bool:
        """是否部分成功"""
        return self.status == ProcessingStatus.PARTIAL

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "status": self.status.value,
            "message": self.message,
            "data": self.data,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
        }

    @classmethod
    def success(
        cls,
        message: str = "处理成功",
        data: Any = None,
        duration_ms: float = 0.0,
        **metadata,
    ) -> "ProcessingResult":
        """创建成功结果"""
        return cls(
            status=ProcessingStatus.COMPLETED,
            message=message,
            data=data,
            duration_ms=duration_ms,
            metadata=metadata,
        )

    @classmethod
    def failure(
        cls,
        message: str = "处理失败",
        error: str = None,
        duration_ms: float = 0.0,
        **metadata,
    ) -> "ProcessingResult":
        """创建失败结果"""
        return cls(
            status=ProcessingStatus.FAILED,
            message=message,
            error=error or message,
            duration_ms=duration_ms,
            metadata=metadata,
        )

    @classmethod
    def partial(
        cls,
        message: str = "部分成功",
        data: Any = None,
        failed_count: int = 0,
        success_count: int = 0,
        duration_ms: float = 0.0,
    ) -> "ProcessingResult":
        """创建部分成功结果（批量处理时）"""
        return cls(
            status=ProcessingStatus.PARTIAL,
            message=message,
            data=data,
            duration_ms=duration_ms,
            metadata={
                "failed_count": failed_count,
                "success_count": success_count,
            },
        )