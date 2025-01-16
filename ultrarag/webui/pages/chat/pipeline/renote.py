import asyncio
import sys, time
import streamlit as st
from pathlib import Path
home_path = Path().resolve()
sys.path.append(home_path.as_posix())
output_path = home_path / "output"

import pandas as pd

from ultrarag.common.utils import get_debug_fold
from ultrarag.workflow.ultraragflow import RenoteFlow
from ultrarag.webui.components.collection_selectbox import close_existing_searcher
from ultrarag.webui.utils.language import t




def display_configurations():
    """配置部分显示在一个 expander 内"""
    if "renote_inst" not in st.session_state:
        st.session_state.renote_inst = ""

    if "collection" not in st.session_state:
        st.session_state.collection = []

    if "renote_history" not in st.session_state:
        st.session_state.renote_history = []
        st.session_state.renote_messages = []

    if 'chat_config' not in st.session_state:
        st.session_state.chat_config = {}
    with st.expander("UltraRAG-Adaptive-Note"):
        if 'selected_options' not in st.session_state:
            st.session_state['selected_options'] = []
        if 'current_kb_config_id' not in st.session_state:
            st.session_state['current_kb_config_id'] = None
            
        kb_df = st.session_state.get('kb_df')
        if (isinstance(kb_df, pd.DataFrame)) and not kb_df.empty:
            try:
                st.session_state.renote_inst = RenoteFlow.from_modules(
                    llm=st.session_state.llm,
                    database=st.session_state.searcher
                )
                if st.button(t("clear history"), type="primary"):
                    st.session_state.renote_history = []
                    st.session_state.renote_messages = []
            except Exception as e:
                print(e)
                st.warning(t("Please load the model and select the collections"))
        else:
            try:
                st.session_state['selected_options'] = []
                st.session_state['current_kb_config_id'] = None
                st.session_state.renote_inst = ""
            except:
                pass
            close_existing_searcher()

async def listen(query, container):
    process_info = ""
    buff = ""
    first_response = 0
    time_start, first_response = time.perf_counter(), 0            

    inst = st.session_state.renote_inst
    response = await inst.aquery(
        query=query, 
        messages=st.session_state.renote_messages, 
        collection=st.session_state.selected_collection
    )
    async for chunk in response:
        if first_response == 0 and isinstance(chunk, dict) and chunk['state'] == "data": 
            first_response = time.perf_counter() - time_start
        if isinstance(chunk, dict):
            if chunk["state"].startswith("renote"): process_info = get_debug_fold(title=chunk["state"], context=chunk["value"])
            if chunk["state"].startswith("thinking"): process_info += get_debug_fold(title=chunk["state"], context=chunk["value"])
            if chunk['state'].startswith("allnote"): process_info += get_debug_fold(title=chunk["state"], context=chunk["value"])
            if chunk['state'] == "data": buff += chunk['value']
        else:
            buff += chunk
        
        container.chat_message("assistant").markdown(process_info + buff, unsafe_allow_html=True)
    extra_infos = f"\n\nspend: {time.perf_counter() - time_start :.2f} s, first response {first_response:.2f} s"
    container.chat_message("assistant").markdown(process_info + buff + extra_infos, unsafe_allow_html=True)
    return process_info + buff + extra_infos, buff

@st.fragment
def chat_component():
    """聊天框组件"""
    st.subheader(f"{t('Welcome to ')}UltraRAG-Adaptive-Note")

    his_container = st.container(height=500)
    
    with his_container:
        for (query, response) in st.session_state.renote_history:
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
            st.session_state.renote_messages.append({"role": "user", "content": query})
            st.session_state.renote_messages.append({"role": "assistant", "content": pure_response})
            st.session_state.renote_history.append((query, response_with_extra_info))
            st.rerun()

def display():
    display_configurations()
    if st.session_state.get("renote_inst",""):
        chat_component()
