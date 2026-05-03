"""
Domain Layer Value Objects
"""

from .bounding_box import BoundingBox
from .device_type import DeviceType, DevicePriority
from .processing_status import ProcessingStatus, ProcessingResult

__all__ = [
    "BoundingBox",
    "DeviceType",
    "DevicePriority",
    "ProcessingStatus",
    "ProcessingResult",
]