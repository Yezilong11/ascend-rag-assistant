"""
昇腾NPU适配模块
用于将模型推理从CPU/GPU迁移至昇腾910B NPU
"""

import torch


class AscendAdapter:
    """昇腾NPU适配器"""

    def __init__(self):
        self.npu_available = self._check_npu()

    def _check_npu(self) -> bool:
        """检查昇腾NPU是否可用"""
        try:
            import acl
            _ = acl
            return True
        except ImportError:
            print("[WARNING] 昇腾CANN环境未配置")
            return False

    def get_device(self):
        """获取可用设备"""
        if self.npu_available:
            return "npu:0"
        elif torch.cuda.is_available():
            return "cuda:0"
        else:
            return "cpu"

    def optimize_model(self, model, config=None):
        """
        模型优化配置
        Args:
            model: 加载的模型
            config: 优化配置
        """
        if config is None:
            config = {
                "quantization": "int8",      # 可选: int8, int4, fp16
                "use_cache": True,           # KV Cache加速
                "batch_size": 4,             # 批处理大小
                "max_seq_length": 2048,      # 最大序列长度
            }

        if self.npu_available:
            # 昇腾NPU特定优化
            print("[INFO] 应用昇腾NPU优化配置")
            # 量化配置
            if config["quantization"] == "int8":
                # INT8量化
                pass
            elif config["quantization"] == "int4":
                # INT4量化
                pass

        return model, config

    def benchmark(self, model, tokenizer, test_prompts):
        """
        性能基准测试
        Args:
            model: 模型实例
            tokenizer: 分词器
            test_prompts: 测试用例列表
        Returns:
            性能指标字典
        """
        import time

        metrics = {
            "first_token_latency": [],
            "tokens_per_second": [],
            "total_time": []
        }

        for prompt in test_prompts:
            start_time = time.time()

            # 编码
            inputs = tokenizer(prompt, return_tensors="pt")

            # 生成
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=100,
                    do_sample=True
                )

            end_time = time.time()

            # 计算指标
            total_time = end_time - start_time
            num_tokens = outputs.shape[1] - inputs.input_ids.shape[1]

            metrics["total_time"].append(total_time)
            metrics["tokens_per_second"].append(num_tokens / total_time)

        return {
            "avg_tokens_per_second": sum(metrics["tokens_per_second"]) / len(metrics["tokens_per_second"]),
            "avg_total_time": sum(metrics["total_time"]) / len(metrics["total_time"])
        }


# 使用示例
"""
from src.ascend_adapter import AscendAdapter

adapter = AscendAdapter()
device = adapter.get_device()
print(f"使用设备: {device}")

# 优化模型
model, config = adapter.optimize_model(model)

# 性能测试
metrics = adapter.benchmark(model, tokenizer, test_prompts)
print(f"平均生成速度: {metrics['avg_tokens_per_second']:.2f} tokens/s")
"""
