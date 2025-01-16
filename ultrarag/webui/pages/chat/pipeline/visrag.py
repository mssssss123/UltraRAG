import os
import time
import asyncio
import pandas as pd
import streamlit as st
from pathlib import Path
import traceback
from loguru import logger
from flask import Flask, send_file, abort
import threading    

from ultrarag.common.utils import get_debug_fold, get_image_fold
from ultrarag.modules.database import QdrantIndex
from ultrarag.workflow.ultraragflow import VisRagFLow
from ultrarag.modules.embedding import VisNetClient, VisRAGNetServer
from ultrarag.modules.llm import HuggingfaceClient, HuggingFaceServer
from ultrarag.modules.knowledge_managment import Knowledge_Managment
from ultrarag.webui.components.collection_selectbox import close_existing_searcher
from ultrarag.webui.utils.language import t




def create_image_server(port=5000):
    app = Flask(__name__)
    
    @app.route('/images/<path:filepath>')
    def serve_image(filepath):
        """
        访问任意路径下的图片
        示例：http://localhost:5000/images/path/to/your/image.jpg
        """
        filepath = f"/{filepath}"
        logger.debug(f"filepath: {filepath}")

        image_path = Path(filepath)
        if not image_path.is_file():
            return abort(404, "文件不存在")
            
        # 检查是否是图片文件（可选）
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        if image_path.suffix.lower() not in allowed_extensions:
            return abort(400, "不支持的文件类型")
            
        return send_file(filepath)

    def run_server():
        app.run(host='0.0.0.0', port=port, debug=False)
    
    # 在新线程中启动服务器
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    return f"图片服务器已在后台启动，端口：{port}"

if "imageStorage" not in st.session_state:
    st.session_state.imageStorage = True
    create_image_server()

def display_configurations():
    """配置部分显示在一个 expander 内"""
    # 初始化 session_state
    if "visrag_inst" not in st.session_state:
        st.session_state.visrag_inst = ""
    if "collection" not in st.session_state:
        st.session_state.collection = []
    if "visrag_history" not in st.session_state:
        st.session_state.visrag_history = []
        st.session_state.visrag_messages = []
    with st.expander("VisRAG"):
        if 'selected_options' not in st.session_state:
            st.session_state['selected_options'] = []
        if 'current_kb_config_id' not in st.session_state:
            st.session_state['current_kb_config_id'] = None
            
        kb_df = st.session_state.get('kb_df')
        if (isinstance(kb_df, pd.DataFrame)) and not kb_df.empty:
            try:
                st.session_state.visrag_inst = VisRagFLow.from_modules(
                    llm_model=st.session_state.llm,
                    database=st.session_state.searcher,
                )
                if st.button(t("clear history"), type="primary"):
                    st.session_state.visrag_history = []
                    st.session_state.visrag_messages = []
            except Exception as e:
                logger.error(traceback.format_exc())
                st.warning(t("Please load the model and select the collections"))
        else:
            try:
                st.session_state['selected_options'] = []
                st.session_state['current_kb_config_id'] = None
                st.session_state.visrag_inst = ""
            except:
                pass
            close_existing_searcher()

# 设置路径
home_path = Path().resolve()
output_path = home_path / "output"

if 'chat_config' not in st.session_state:
    st.session_state.dc_config = {}


async def listen(query,container):
    process_info = ""
    buff = ""
    time_start, first_response = time.perf_counter(), 0            

    rag_link = st.session_state.visrag_inst
    response = rag_link.aquery(
        query=query, 
        messages=st.session_state.visrag_messages, 
        collection=st.session_state.selected_collection
    )
    async for chunk in response:
        if isinstance(chunk, dict) and chunk["state"] == "recall": 
            context = [f"http://localhost:5000/images/{home_path.as_posix()}/{url}" for url in chunk['value']]
            process_info = get_image_fold(title="recall", context=context)
        if isinstance(chunk, dict) and chunk['state'] == "answer":
            if first_response == 0: first_response = time.perf_counter() - time_start
            buff += chunk['value']
        container.chat_message("assistant").markdown(process_info + buff, unsafe_allow_html=True)
    extra_infos = f"\n\n\ntotal spend: {time.perf_counter() - time_start :.2f} s, first reponse {first_response:.2f} s"
    container.chat_message("assistant").markdown(process_info + buff + extra_infos, unsafe_allow_html=True)
    return process_info + buff + extra_infos, buff

@st.fragment
def chat_component():
    """聊天框组件"""
    st.subheader(f"{t('Welcome to ')}VisRAG")

    his_container = st.container(height=500)
    
    with his_container:
        for (query, response) in st.session_state.visrag_history:
            with st.chat_message(name="user", avatar="user"):
                st.markdown(query, unsafe_allow_html=True)
            with st.chat_message(name="assistant", avatar="assistant"):
                st.markdown(response, unsafe_allow_html=True)
        container = st.empty()
        container_a = st.empty()
        
    chat_input_container = st.container()
    with chat_input_container:
        if query := st.chat_input(t("Please input your question")):
            container.chat_message("user").markdown(query, unsafe_allow_html=True)
            response_with_extra_info, pure_response = asyncio.run(listen(query,container_a))
            st.session_state.visrag_messages.append({"role": "user", "content": query})
            st.session_state.visrag_messages.append({"role": "assistant", "content": pure_response})
            st.session_state.visrag_history.append((query, response_with_extra_info))
            st.rerun()

def display():
    display_configurations()
    if st.session_state.get("visrag_inst",""):
        chat_component()
