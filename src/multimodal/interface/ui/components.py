"""
UI Components - Streamlit组件
"""

from typing import List, Optional, Any
import streamlit as st


def render_multimodal_sidebar(kb: Any = None) -> None:
    """
    侧边栏多模态组件
    """
    st.markdown("---")
    st.markdown("🖼️ 多模态知识库")

    if "multimodal_enabled" not in st.session_state:
        st.session_state.multimodal_enabled = False

    multimodal_enabled = st.checkbox(
        "启用多模态模式",
        value=st.session_state.multimodal_enabled,
        help="支持图片和PDF内嵌图片的OCR识别和VLM分析"
    )

    st.session_state.multimodal_enabled = multimodal_enabled

    if multimodal_enabled:
        tab1, tab2 = st.tabs(["📷 图片上传", "📄 PDF上传"])

        with tab1:
            uploaded_images = st.file_uploader(
                "上传图片",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True,
                help="支持JPG、PNG格式"
            )

            if uploaded_images:
                doc_type_img = st.selectbox(
                    "文档类型",
                    options=["unknown", "tech_doc", "rules", "faq", "history"],
                    format_func=lambda x: {
                        "unknown": "自动识别",
                        "tech_doc": "技术文档",
                        "rules": "竞赛规则",
                        "faq": "常见问题",
                        "history": "历史赛题",
                    }.get(x, x),
                    key="img_doc_type",
                )

                if st.button("📷 分析并添加到知识库", type="primary", key="process_images"):
                    _process_images(uploaded_images, doc_type_img)

        with tab2:
            uploaded_pdf = st.file_uploader(
                "上传PDF",
                type=["pdf"],
                help="支持PDF文件，将自动提取内嵌图片"
            )

            if uploaded_pdf:
                doc_type_pdf = st.selectbox(
                    "文档类型",
                    options=["unknown", "tech_doc", "rules", "faq", "history"],
                    format_func=lambda x: {
                        "unknown": "自动识别",
                        "tech_doc": "技术文档",
                        "rules": "竞赛规则",
                        "faq": "常见问题",
                        "history": "历史赛题",
                    }.get(x, x),
                    key="pdf_doc_type",
                )

                extract_imgs = st.checkbox("提取PDF内嵌图片", value=True)

                if st.button("📄 分析并添加到知识库", type="primary", key="process_pdf"):
                    _process_pdf(uploaded_pdf, doc_type_pdf, extract_imgs)

        st.session_state.show_images = st.checkbox(
            "检索结果显示图片",
            value=st.session_state.get("show_images", True),
            key="show_images_toggle",
        )


def _process_images(files, document_type: str):
    """处理上传的图片"""
    import requests
    import io

    file_handles = []
    try:
        files_data = []
        for f in files:
            file_bytes = f.getvalue()
            file_io = io.BytesIO(file_bytes)
            file_handles.append(file_io)
            files_data.append(("files", (f.name, file_io, f.type)))

        files_data.append(("document_type", (None, document_type)))

        response = requests.post(
            "http://localhost:8000/api/multimodal/image/ingest",
            files=files_data,
        )

        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                st.success(f"✅ 成功处理 {result.get('success_count', 0)} 张图片")
            else:
                st.error(f"❌ 处理失败: {result.get('errors', ['未知错误'])}")
        else:
            st.error(f"❌ 请求失败: {response.status_code}")

    except requests.exceptions.ConnectionError:
        st.error("❌ 无法连接到API服务，请确保server.py已启动")
    except Exception as e:
        st.error(f"❌ 处理失败: {str(e)}")
    finally:
        for fh in file_handles:
            try:
                fh.close()
            except Exception:
                pass


def _process_pdf(file, document_type: str, extract_images: bool):
    """处理上传的PDF"""
    import requests
    import io

    file_handle = None
    try:
        file_bytes = file.getvalue()
        file_handle = io.BytesIO(file_bytes)

        files_data = [
            ("file", (file.name, file_handle, file.type))
        ]
        files_data.append(("document_type", (None, document_type)))
        files_data.append(("extract_images", (None, str(extract_images))))

        response = requests.post(
            "http://localhost:8000/api/multimodal/pdf/ingest",
            files=files_data,
        )

        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                st.success(
                    f"✅ PDF处理完成\n"
                    f"- 文本块: {result.get('text_chunks_count', 0)}\n"
                    f"- 图片块: {result.get('image_chunks_count', 0)}\n"
                    f"- 提取图片: {result.get('extracted_images_count', 0)}"
                )
            else:
                st.error(f"❌ 处理失败: {result.get('errors', ['未知错误'])}")
        else:
            st.error(f"❌ 请求失败: {response.status_code}")

    except requests.exceptions.ConnectionError:
        st.error("❌ 无法连接到API服务，请确保server.py已启动")
    except Exception as e:
        st.error(f"❌ 处理失败: {str(e)}")
    finally:
        if file_handle:
            try:
                file_handle.close()
            except Exception:
                pass


def render_image_sources(image_sources: List[Any]) -> None:
    """渲染图片来源"""
    import os

    if not image_sources:
        return

    st.markdown("### 🖼️ 相关图片")

    for idx, img in enumerate(image_sources):
        try:
            description = getattr(img, "description", "") or ""
            ocr_text = getattr(img, "ocr_text", "") or ""
            source_file = getattr(img, "source_file", "") or ""
            page_number = getattr(img, "page_number", 0) or 0
            relevance = getattr(img, "relevance_score", 0.0) or 0.0
            image_path = getattr(img, "image_path", "") or ""

            with st.expander(f"图片 {idx + 1}: {description[:50]}...", expanded=True):
                if image_path and os.path.exists(image_path):
                    try:
                        st.image(image_path, width=300)
                    except Exception:
                        st.warning(f"无法显示图片: {image_path}")
                else:
                    st.info("图片文件不存在")

                st.markdown(f"**描述**: {description}")
                if ocr_text:
                    st.markdown(f"**OCR文字**: {ocr_text}")
                st.markdown(f"**来源**: {os.path.basename(source_file)} (第{page_number}页)")
                st.markdown(f"**相关度**: {relevance:.2f}")

        except Exception as e:
            st.warning(f"渲染图片 {idx + 1} 失败: {str(e)}")