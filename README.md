# Ascend RAG Assistant

<div align="center">

🚀 **基于昇腾AI平台的RAG智能竞赛助手**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-1.2.0-green.svg)](https://www.langchain.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.50.0-red.svg)](https://streamlit.io/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-1.5.0-purple.svg)](https://trychroma.com/)

</div>

## 📖 项目简介

**Ascend RAG Assistant** 是一个基于检索增强生成（RAG）技术的AI竞赛智能助教系统，专为昇腾AI生态打造。系统能够基于竞赛官方文档、报名须知、规则说明等资料，为参赛选手提供24/7全天候的智能问答服务。

### ✨ 核心特性

- 🧠 **基于RAG的知识问答** - 结合私域知识库与大语言模型，提供准确可靠的回答
- ⚡ **昇腾NPU原生优化** - 原生支持华为昇腾910B NPU
- 🎯 **可切换模型** - 侧边栏自由切换不同大小、不同量化级别的模型
- 🚀 **ModelScope一键下载** - 自动从魔搭下载模型到项目文件夹，国内访问更快
- 🖥️ **精致对话界面** - 基于Streamlit构建的现代化聊天界面
- 📚 **多格式文档支持** - 支持PDF、TXT、Markdown等多种文档格式的导入
- 🏠 **完全本地部署** - 支持全流程本地运行，保护数据隐私
- 🔄 **易于扩展** - 模块化设计，方便添加新的数据源和模型

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    用户交互层 (Streamlit)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │ 文档上传管理 │  │  智能问答界面  │  │   系统状态监控   │   │
│  └──────────────┘  └──────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     RAG 核心引擎                              │
│  ┌───────────────────┐      ┌──────────────────────────┐    │
│  │   知识库检索       │ ───→ │   Prompt 工程 + 生成     │    │
│  └───────────────────┘      └──────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     向量知识库 (ChromaDB)                     │
│  - BGE-Large-ZH 嵌入模型                                      │
│  - 递归字符切分策略                                           │
│  - 持久化存储支持                                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     昇腾NPU 适配层                            │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────┐  │
│  │  设备自动检测    │  │   量化优化       │  │ 性能测试   │  │
│  └──────────────────┘  └──────────────────┘  └────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 快速开始

### 环境要求

- Python 3.10+
- PyTorch 2.0+
- (可选) 华为昇腾NPU + CANN工具链

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/your-username/ascend-rag-assistant.git
cd ascend-rag-assistant
```

2. **创建虚拟环境**
```bash
conda create -n ascend-rag python=3.10
conda activate ascend-rag
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

 4. **下载模型**

推荐使用 **ModelScope（魔搭社区）** 下载，国内访问更快：

```bash
# 安装modelscope
pip install modelscope

# 下载 BGE 嵌入模型
modelscope download --model BAAI/bge-large-zh-v1.5 --local_dir ./models/bge-large-zh-v1.5

# 下载 Qwen2 大语言模型（推荐）
modelscope download --model qwen/Qwen2-1.5B-Instruct-GPTQ-Int4 --local_dir ./models/Qwen2-1.5B-Instruct-GPTQ-Int4
```

**支持的模型列表：**

| 模型 | 推荐 | 说明 |
|------|------|------|
| Qwen2-1.5B-Instruct | 🚀 **推荐** | 标准版，质量最好 |
| Qwen2-1.5B-Instruct-GPTQ-Int4 |  | 4bit量化，速度提升3-5倍 |
| Qwen2-0.5B-Instruct | ⚡ CPU推荐 | 更快，适合CPU环境 |
| chatglm3-6b |  | 大模型，质量更好 |

**自动下载：** 如果本地模型不存在，系统会**自动从ModelScope下载到 `./models/` 文件夹**，无需手动操作。

**GPTQ量化优势：**
- 显存占用减少 75%
- 推理速度提升 **3-5倍**
- 回答质量损失可忽略

 目录结构：
```
models/
├── bge-large-zh-v1.5/
└── Qwen2-1.5B-Instruct-GPTQ-Int4/  # 推荐量化版
```

5. **启动应用**
```bash
streamlit run app.py
```

应用启动后，访问 `http://localhost:8501` 即可使用。

## 📖 使用指南

### 基本使用流程

1. **初始化知识库** - 应用启动后会自动初始化向量数据库
2. **导入竞赛资料** - 在侧边栏上传PDF/TXT/MD文件，点击「添加到知识库」
3. **启动AI引擎** - 点击「启动AI引擎」加载大模型
4. **开始问答** - 在主输入框输入问题，获取智能回答

### 预置知识库

本项目已预置了近百场国内大学生竞赛的相关资料，包括：
- 报名须知
- 竞赛规则
- 评分标准
- 常见问题FAQ
- 技术文档

### 配置说明

在 `config/` 目录下可以修改系统配置：
- `config.yaml`: 模型路径、超参数等配置

## 🧩 模块说明

### `src/knowledge_base.py` - 知识库管理

负责文档加载、文本切分、向量化存储和检索：
- 支持多种文档格式（PDF、TXT、MD）
- 递归字符切分策略，chunk_size=500，chunk_overlap=50
- 使用 BGE-Large-ZH 中文嵌入模型
- ChromaDB 持久化存储

### `src/rag_engine.py` - RAG引擎核心

结合检索到的知识和大模型生成能力：
- 支持预定义多模型切换，默认优先加载量化版
- 自动从ModelScope下载模型到`./models/`文件夹
- 支持GPTQ量化模型自动检测和加载
- 自定义Prompt模板
- 返回回答及参考来源
- 异常处理机制

### `src/ascend_adapter.py` - 昇腾NPU适配

提供昇腾NPU设备管理和性能优化：
- 自动检测NPU可用性
- 支持INT8/INT4量化
- KV Cache加速
- 性能基准测试工具

**性能参考（昇腾910B）**:
| 模型 | 量化 | 平均生成速度 |
|------|------|-------------|
| Qwen2-1.5B | INT8 | ~25 tokens/s |
| ChatGLM3-6B | INT4 | ~18 tokens/s |

**性能参考（CPU/CUDA）**:
| 硬件 | 模型 | 量化 | 平均生成速度 | 300字回答时间 |
|------|------|------|-------------|--------------|
| CPU | Qwen2-0.5B | 无 | ~8-12 tokens/s | 25-40秒 |
| CPU | Qwen2-1.5B | 无 | ~3-5 tokens/s | 60-100秒 |
| CUDA GPU | Qwen2-1.5B | FP16 | ~15-20 tokens/s | 15-20秒 |
| CUDA GPU | Qwen2-1.5B | GPTQ-Int4 | ~30-40 tokens/s | 8-10秒 |

## ⚡ 性能优化指南

### 使用GPTQ量化模型（推荐）

1. **安装依赖**
```bash
pip install auto-gptq optimum modelscope
```

2. **下载量化模型（推荐使用ModelScope）**
```bash
modelscope download --model qwen/Qwen2-1.5B-Instruct-GPTQ-Int4 --local-dir ./models/Qwen2-1.5B-Instruct-GPTQ-Int4
```

3. **自动检测**
系统会自动检测GPTQ模型（路径含`gptq`/`int4`/`int8`）并使用量化加载，无需修改代码。

### CPU进一步优化

1. **使用更小模型** - 使用 `Qwen/Qwen2-0.5B-Instruct`，速度提升2-3倍
2. **限制生成长度** - 默认`max_new_tokens=256`，可根据需要调整
3. **关闭采样** - 设置`do_sample=False`使用贪婪搜索，速度略快但多样性减少

## 📊 效果展示

| 功能 | 演示 |
|------|------|
| 智能问答 | 支持竞赛报名、规则、日程等各类问题查询 |
| 来源引用 | 每个回答都标注参考来源，可追溯 |
| 文档上传 | 支持随时添加新的竞赛资料 |

## 🛠️ 开发计划

- [ ] 支持更多LLM模型（百川、灵犀等）
- [ ] 添加Parent-document检索优化
- [ ] 支持多模态文档（图片中的文字提取）
- [ ] API服务化部署
- [ ] Docker容器化支持
- [ ] 优化昇腾NPU上的量化推理性能

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启一个 Pull Request

## 📄 许可证

本项目仅供学习和研究使用。

## 🙏 致谢

- [LangChain](https://www.langchain.com/) - 优秀的LLM应用框架
- [ChromaDB](https://trychroma.com/) - 开源向量数据库
- [BGE](https://github.com/FlagOpen/FlagEmbedding) - 优秀的中文嵌入模型
- [Qwen](https://github.com/QwenLM/Qwen2) - 通义千问大模型
- [ModelScope](https://modelscope.cn/) - 魔搭社区，方便的模型下载服务
- [昇腾AI](https://www.hiascend.com/) - 华为昇腾AI计算平台

---

<div align="center">
Made with ❤️ for the Ascend AI ecosystem
</div>
