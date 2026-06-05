"""
RAG API 依赖注入模块
管理 RAGAssistant 和 KnowledgeBase 的单例生命周期

设计要点：
- 使用模块级全局变量实现单例模式，确保整个应用共享同一实例
- KnowledgeBase 采用惰性初始化，首次调用时创建，后续复用
- RAGAssistant 由外部显式设置/清除，支持模型的热加载与卸载
- clear_rag_assistant() 主动释放 GPU 显存，避免模型卸载后显存残留
- _is_loading 标记防止并发加载请求

使用方式：
    from src.rag_api.dependencies import (
        get_knowledge_base,
        get_rag_assistant,
        set_rag_assistant,
        clear_rag_assistant,
        get_is_loading,
        set_is_loading,
    )
"""

import os
import logging
import threading
from typing import Optional

import torch
import yaml

from src.rag_engine import RAGAssistant, PREDEFINED_MODELS, PREDEFINED_RERANKERS
from src.knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)

# 模块级锁，保护全局变量的线程安全访问
_lock = threading.Lock()

_rag_assistant: Optional[RAGAssistant] = None
_knowledge_base: Optional[KnowledgeBase] = None
_is_loading: bool = False

_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "config.yaml")


def _load_config() -> dict:
    """
    读取 config/config.yaml 配置文件

    Returns:
        dict: 解析后的配置字典

    Raises:
        FileNotFoundError: 配置文件不存在时抛出
    """
    if not os.path.exists(_CONFIG_PATH):
        logger.warning(f"配置文件不存在: {_CONFIG_PATH}，使用默认配置")
        return {}
    with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_knowledge_base() -> KnowledgeBase:
    """
    获取 KnowledgeBase 单例实例（惰性初始化）

    首次调用时从 config/config.yaml 读取 knowledge_base 配置节，
    创建 KnowledgeBase 实例并缓存到模块级变量。后续调用直接返回同一实例。

    配置项映射：
        - persist_dir: 向量数据库持久化目录，默认 "./chroma_db"
        - model_dir:   本地模型存放目录，默认 "./models"

    Returns:
        KnowledgeBase: 知识库实例
    """
    global _knowledge_base

    with _lock:
        if _knowledge_base is not None:
            return _knowledge_base

    config = _load_config()
    kb_config = config.get("knowledge_base", {})

    persist_dir = kb_config.get("persist_dir", "./chroma_db")
    model_dir = "./models"

    logger.info(f"正在初始化 KnowledgeBase: persist_dir={persist_dir}, model_dir={model_dir}")

    kb = KnowledgeBase(
        persist_dir=persist_dir,
        model_dir=model_dir,
    )

    with _lock:
        # 双重检查：防止并发初始化
        if _knowledge_base is None:
            _knowledge_base = kb

    logger.info("KnowledgeBase 初始化完成")
    return _knowledge_base


def get_rag_assistant() -> Optional[RAGAssistant]:
    """
    获取当前 RAGAssistant 实例

    RAGAssistant 需要占用大量 GPU 显存，因此不自动初始化，
    由外部通过 set_rag_assistant() 显式设置。

    Returns:
        Optional[RAGAssistant]: 当前实例，未加载时返回 None
    """
    with _lock:
        return _rag_assistant


def set_rag_assistant(assistant: RAGAssistant) -> None:
    """
    设置 RAGAssistant 实例

    在模型加载完成后调用，将实例保存到模块级变量供后续请求使用。
    如果已有实例存在，会先调用 clear_rag_assistant() 释放旧实例的 GPU 显存。

    Args:
        assistant: 已初始化完成的 RAGAssistant 实例
    """
    global _rag_assistant

    with _lock:
        if _rag_assistant is not None:
            logger.warning("检测到已有 RAGAssistant 实例，先释放旧实例资源")
            _clear_rag_assistant_unlocked()

        _rag_assistant = assistant
        logger.info(f"RAGAssistant 实例已设置: model_key={assistant.model_key}")


def _clear_rag_assistant_unlocked() -> None:
    """
    清除 RAGAssistant 实例并释放 GPU 显存（内部方法，调用方需已持有 _lock）

    执行以下清理步骤：
    1. 删除模型对象 (assistant.model) 释放模型权重占用的显存
    2. 删除 pipeline 对象 (assistant.pipeline_obj) 释放推理管线占用的显存
    3. 调用 torch.cuda.empty_cache() 清空 CUDA 缓存池
    4. 将模块级变量设为 None

    所有步骤均有异常保护，确保即使某步失败也能继续执行后续清理。
    """
    global _rag_assistant

    if _rag_assistant is None:
        logger.info("无需清除，当前无 RAGAssistant 实例")
        return

    assistant = _rag_assistant

    try:
        if hasattr(assistant, "model") and assistant.model is not None:
            del assistant.model
            logger.info("已释放 RAGAssistant.model")
    except Exception as e:
        logger.error(f"释放 model 时出错: {e}")

    try:
        if hasattr(assistant, "pipeline_obj") and assistant.pipeline_obj is not None:
            del assistant.pipeline_obj
            logger.info("已释放 RAGAssistant.pipeline_obj")
    except Exception as e:
        logger.error(f"释放 pipeline_obj 时出错: {e}")

    try:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            logger.info("已清空 CUDA 缓存")
    except Exception as e:
        logger.error(f"清空 CUDA 缓存时出错: {e}")

    _rag_assistant = None
    logger.info("RAGAssistant 实例已清除")


def clear_rag_assistant() -> None:
    """
    清除 RAGAssistant 实例并释放 GPU 显存（线程安全）

    对外接口，内部获取锁后调用 _clear_rag_assistant_unlocked()。
    """
    with _lock:
        _clear_rag_assistant_unlocked()


def get_is_loading() -> bool:
    """
    获取模型加载状态标记

    Returns:
        bool: True 表示模型正在加载中，False 表示未在加载
    """
    with _lock:
        return _is_loading


def set_is_loading(val: bool) -> None:
    """
    设置模型加载状态标记

    在模型加载开始时设为 True，加载完成或失败时设为 False。
    防止并发加载请求导致资源冲突。

    Args:
        val: 加载状态，True 为正在加载，False 为未在加载
    """
    global _is_loading
    with _lock:
        _is_loading = val
        logger.info(f"模型加载状态已更新: _is_loading={_is_loading}")
