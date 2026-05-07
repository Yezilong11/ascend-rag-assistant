"""
DeviceManager - 异构计算设备管理器
实现 NPU > GPU > CPU 优先级自动选择
"""

import os
import torch
from typing import Dict, Any, Optional

from ...domain.value_objects.device_type import DeviceType, DevicePriority


class DeviceManager:
    """
    异构计算设备管理器
    实现 NPU > GPU > CPU 优先级自动选择

    显存分配方案（8GB基准）:
        - VLM (GPU/NPU): ~1.5GB (INT4)
        - OCR (CPU): ~1GB
        - Embedding (CPU): ~1.5GB
        - VectorStore (CPU): ~0.5GB
        - Reserved: ~3.5GB
    """

    def __init__(self, forced_device: str = None, config: Dict[str, Any] = None):
        self._config = config or {}
        self._forced_device = forced_device
        self._npu_available = self._check_npu()
        self._cuda_available = self._check_cuda()
        self._device_priority = DevicePriority()

    def _check_npu(self) -> bool:
        """检查昇腾NPU是否可用"""
        try:
            import acl
            _ = acl
            return True
        except ImportError:
            return False

    def _check_cuda(self) -> bool:
        """检查CUDA是否可用"""
        return torch.cuda.is_available()

    def get_device(self) -> str:
        """获取最优可用设备"""
        forced = None
        if self._forced_device:
            try:
                forced = DeviceType(self._forced_device.lower())
            except ValueError:
                pass

        device = self._device_priority.get_available_device(
            npu_available=self._npu_available,
            cuda_available=self._cuda_available,
            forced_device=forced,
        )
        return self._device_to_string(device)

    def get_vlm_device(self) -> str:
        """
        VLM专用设备（GPU/NPU）
        VLM必须在加速器上运行
        """
        if self._npu_available:
            return "npu:0"
        if self._cuda_available:
            return "cuda:0"
        raise RuntimeError("No accelerator device available for VLM. VLM requires GPU or NPU.")

    def get_ocr_device(self) -> str:
        """OCR设备（固定CPU）"""
        return "cpu"

    def get_embedding_device(self) -> str:
        """嵌入设备（固定CPU）"""
        return "cpu"

    def get_vectorstore_device(self) -> str:
        """向量库设备（固定CPU）"""
        return "cpu"

    def _device_to_string(self, device: DeviceType) -> str:
        """将设备类型转换为字符串"""
        if device == DeviceType.NPU:
            return "npu:0"
        elif device == DeviceType.CUDA:
            return "cuda:0"
        return "cpu"

    def get_device_info(self) -> Dict[str, Any]:
        """
        返回设备信息
        """
        info = {
            "npu_available": self._npu_available,
            "cuda_available": self._cuda_available,
            "vlm_device": self.get_vlm_device(),
            "ocr_device": self.get_ocr_device(),
            "embedding_device": self.get_embedding_device(),
            "vectorstore_device": self.get_vectorstore_device(),
        }

        if self._cuda_available:
            info["gpu_name"] = torch.cuda.get_device_name(0)
            info["gpu_memory_total_mb"] = torch.cuda.get_device_properties(0).total_memory / 1024 / 1024
            info["gpu_memory_available_mb"] = (torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated(0)) / 1024 / 1024

        return info

    def get_allocation_plan(self) -> Dict[str, int]:
        """获取8GB显存分配方案"""
        total = 8192
        if self._cuda_available:
            total = int(torch.cuda.get_device_properties(0).total_memory / 1024 / 1024)

        return self._device_priority.get_allocation_plan(total_memory_mb=total)

    def is_npu(self) -> bool:
        """当前VLM设备是否为NPU"""
        return self._npu_available

    def is_cuda(self) -> bool:
        """当前VLM设备是否为CUDA"""
        return self._cuda_available and not self._npu_available

    def get_accelerator_type(self) -> str:
        """获取加速器类型"""
        if self._npu_available:
            return "npu"
        if self._cuda_available:
            return "cuda"
        return "cpu"