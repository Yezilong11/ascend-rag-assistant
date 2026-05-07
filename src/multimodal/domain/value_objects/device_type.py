"""
DeviceType - 设备类型值对象
定义异构计算中的设备枚举和优先级
"""

from enum import Enum
from typing import List, Dict, Any


class DeviceType(Enum):
    """
    设备类型枚举
    """

    NPU = "npu"
    CUDA = "cuda"
    CPU = "cpu"

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"DeviceType.{self.name}"

    @property
    def is_accelerator(self) -> bool:
        """是否为加速器设备"""
        return self in (DeviceType.NPU, DeviceType.CUDA)

    @property
    def is_npu(self) -> bool:
        """是否为NPU设备"""
        return self == DeviceType.NPU

    @property
    def is_cuda(self) -> bool:
        """是否为CUDA设备"""
        return self == DeviceType.CUDA

    @property
    def is_cpu(self) -> bool:
        """是否为CPU设备"""
        return self == DeviceType.CPU

    def get_memory_estimate_mb(self, model_type: str = "vlm") -> int:
        """获取该设备上运行指定模型的预估显存需求"""
        estimates = {
            "vlm": {
                DeviceType.NPU: 1536,
                DeviceType.CUDA: 1536,
                DeviceType.CPU: 2048,
            },
            "ocr": {
                DeviceType.NPU: 512,
                DeviceType.CUDA: 512,
                DeviceType.CPU: 1024,
            },
            "embedding": {
                DeviceType.NPU: 1024,
                DeviceType.CUDA: 1024,
                DeviceType.CPU: 1536,
            },
        }
        return estimates.get(model_type, {}).get(self, 0)

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {"value": self.value, "name": self.name}


class DevicePriority:
    """
    设备优先级管理器
    根据硬件可用性和配置确定最优设备选择
    """

    DEFAULT_PRIORITY: List[DeviceType] = [
        DeviceType.NPU,
        DeviceType.CUDA,
        DeviceType.CPU,
    ]

    def __init__(self, priority_list: List[DeviceType] = None):
        self._priority = priority_list or self.DEFAULT_PRIORITY

    def get_available_device(
        self,
        npu_available: bool = False,
        cuda_available: bool = False,
        forced_device: DeviceType = None,
    ) -> DeviceType:
        """获取最优可用设备"""
        if forced_device:
            if forced_device == DeviceType.NPU and not npu_available:
                raise ValueError("NPU requested but not available")
            if forced_device == DeviceType.CUDA and not cuda_available:
                raise ValueError("CUDA requested but not available")
            return forced_device

        for device in self._priority:
            if device == DeviceType.NPU and npu_available:
                return device
            if device == DeviceType.CUDA and cuda_available:
                return device
            if device == DeviceType.CPU:
                return device

        return DeviceType.CPU

    def get_vlm_device(
        self,
        npu_available: bool = False,
        cuda_available: bool = False,
    ) -> DeviceType:
        """获取VLM专用设备（仅返回加速器）"""
        if npu_available:
            return DeviceType.NPU
        if cuda_available:
            return DeviceType.CUDA
        raise RuntimeError("No accelerator device available for VLM")

    def get_ocr_device(self) -> DeviceType:
        """获取OCR设备（固定CPU）"""
        return DeviceType.CPU

    def get_embedding_device(self) -> DeviceType:
        """获取嵌入设备（固定CPU，用于异构计算设计）"""
        return DeviceType.CPU

    def get_vectorstore_device(self) -> DeviceType:
        """获取向量库设备（固定CPU）"""
        return DeviceType.CPU

    def get_allocation_plan(self, total_memory_mb: int = 8192) -> Dict[str, int]:
        """生成分显存分配方案（8GB基准）"""
        reserved = 3584
        vlm = 1536
        ocr = 1024
        embedding = 1536
        vectorstore = 512

        return {
            "reserved_mb": reserved,
            "vlm_mb": vlm,
            "ocr_mb": ocr,
            "embedding_mb": embedding,
            "vectorstore_mb": vectorstore,
            "total_allocated_mb": vlm + ocr + embedding + vectorstore,
            "total_memory_mb": total_memory_mb,
        }