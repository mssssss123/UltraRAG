import sys, time, asyncio
from pathlib import Path
home_path = Path().resolve()
sys.path.append(home_path.as_posix())
from ultrarag.webui.utils.config import LANGUAGES, MODEL_TYPES, EMBEDDING_MODEL_TYPES, RERANKER_MODEL_TYPES
from ultrarag.webui.components.kb_manage import kb_manage
from ultrarag.webui.components.load_btn import load_btn
import streamlit as st
import torch
import subprocess
import extra_streamlit_components as stx
import json
from ultrarag.webui.utils.language import t
from loguru import logger

def load_config(file_path):
    try:
        with open(file_path, "r") as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def initialize_session_state_from_config(config):
    for key, value in config.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
# 初始化全局索引变量
def init_index(key, default_index=0):
    if key not in st.session_state:
        st.session_state[key] = default_index


# 更新索引
@st.fragment()
def update_index(key, items):
    selected_item = st.session_state[key]
    st.session_state[key + '_index'] = items.index(selected_item)
    if key == "language_selectbox":
        st.session_state.rerun_trigger = True

def first_col():
    cols = st.columns([2, 16])
    with cols[0]:
        init_index('language_selectbox_index', 0)
        st.session_state.config['language'] = st.selectbox(
            t("Select Language"),  
            LANGUAGES,
            index=st.session_state['language_selectbox_index'],  
            key="language_selectbox", 
            on_change=update_index,   
            args=('language_selectbox', LANGUAGES) 
        )
        if 'rerun_trigger' in st.session_state and st.session_state.rerun_trigger:
            st.session_state.rerun_trigger = False
            st.rerun()
        

def select_llm_model():
    cols = st.columns([4,7],vertical_alignment='bottom')
    with cols[0]:
        init_index('llm_model_selectbox_index', 0)
        st.session_state.config['model_type'] = st.selectbox(
            t('Select LLM Model'), MODEL_TYPES, index=st.session_state['llm_model_selectbox_index'],
            key="llm_model_selectbox", on_change=update_index, args=('llm_model_selectbox', MODEL_TYPES)
        )
    with cols[1]:
        st.session_state.config['selected_devices_llm'] = select_cuda_devices(t("LLM Model"))

def select_cuda_devices(device_key):
    if torch.cuda.is_available():
        cuda_devices = [f"cuda:{i}" for i in range(torch.cuda.device_count())]
    else:
        cuda_devices = [t("No CUDA devices available")]
    selected_devices = st.multiselect(
        t('Select CUDA Devices for') + f" {device_key}",
        cuda_devices,
        default=st.session_state.config.get(f'selected_devices_{device_key.lower().replace(" ", "_")}', [])
    )
    return selected_devices

def display_model_fields():
    model_type = st.session_state.config.get('model_type', '')
    with st.container():
        model_name = st.session_state.config.get('model_name', '')
        api_key = st.session_state.config.get('api_key', '')
        base_url = st.session_state.config.get('base_url', '')
        model_path = st.session_state.config.get('model_path', '')

        if model_type == 'API':
            cols = st.columns([2, 4, 4])
            with cols[0]:
                st.session_state.config['model_name'] = st.text_input(t('Model Name'), value=model_name)
            with cols[1]:
                st.session_state.config['api_key'] = st.text_input(t('API Key'), value=api_key)
            with cols[2]:
                st.session_state.config['base_url'] = st.text_input(t('Base URL'), value=base_url)
        elif model_type == 'Custom':
            cols = st.columns([10]) 
            with cols[0]:
                st.session_state.config['model_path']  = st.text_input(t('Model Path'), value=model_path)

def select_embedding_model():
    cols = st.columns([4,7],vertical_alignment='bottom')
    with cols[0]:
        init_index('embedding_model_selectbox_index', 0)  # 默认选择第一个嵌入模型类型
        st.session_state.config['embedding_model_type'] = st.selectbox(
            t('Select Embedding Model'), EMBEDDING_MODEL_TYPES, index=st.session_state['embedding_model_selectbox_index'],
            key="embedding_model_selectbox", on_change=update_index, args=('embedding_model_selectbox', EMBEDDING_MODEL_TYPES)
        )
    with cols[1]:
        st.session_state.config['selected_devices_embedding'] = select_cuda_devices("Embedding Model")

def display_embedding_model_fields():
    embedding_model_type = st.session_state.config.get('embedding_model_type', '')
    with st.container():
        st.session_state.config['embedding_model_path'] = st.text_input(t('Embedding Model Path'), value=st.session_state.config.get('embedding_model_path', '')) if embedding_model_type == 'Custom' else ""

def select_reranker_model():
    cols = st.columns([4,7],vertical_alignment='bottom')
    with cols[0]:
        init_index('reranker_model_selectbox_index', 0)  # 默认选择第一个重排序模型类型
        st.session_state.config['reranker_model_type']  = st.selectbox(
            t('Select Reranker Model'), RERANKER_MODEL_TYPES, index=st.session_state['reranker_model_selectbox_index'],
            key="reranker_model_selectbox", on_change=update_index, args=('reranker_model_selectbox', RERANKER_MODEL_TYPES)
        )
    with cols[1]:
        st.session_state.config['selected_devices_reranker'] = select_cuda_devices("Reranker Model")

def display_reranker_model_fields():
    reranker_model_type = st.session_state.config.get('reranker_model_type', '')
    with st.container():
        st.session_state.config['reranker_model_path'] = st.text_input(t('Reranker Model Path'), value=st.session_state.config.get('reranker_model_path', '')) if reranker_model_type == 'Custom' else ""

def advanced_settings():
    kb_manage()

def nvidia_smi_watch():
    with st.expander(t("NVIDIA SMI Monitor"), expanded=False):
        cols = st.columns([6, 4])
        smi_status = st.empty()
        smi_output = st.empty()
        smi_status.text(t("Status: Idle")) 
        process = None
        output_buffer = []

        def start_watch():
            nonlocal process, output_buffer
            smi_status.text(t("Status: Watching..."))
            process = subprocess.Popen(
                ["nvidia-smi"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True
            )
            output_buffer.clear()
            for line in process.stdout:
                output_buffer.append(line)  # 不再 strip，保留原始换行符
                smi_output.markdown(
                    "<div style='font-family: monospace; white-space: pre-wrap; word-wrap: break-word; margin: 0; max-height: 40vh; overflow: scroll;'>"
                    + "".join(output_buffer) + "</div>",
                    unsafe_allow_html=True,
                )

        def stop_watch():
            nonlocal process
            smi_status.text(t("Status: Idle"))
            if process:
                process.terminate()
                process = None

        with cols[0]:
            if st.button(t("Start Watch")):
                if not process:
                    start_watch()

        with cols[1]:
            if st.button(t("Stop Watch")):
                stop_watch()

def global_config():
    config_path = "ultrarag/webui/utils/model_config.json"
    model_config = load_config(config_path)
    if model_config:
        initialize_session_state_from_config(model_config)
    if "config" not in st.session_state: st.session_state.config = {}
    st.header(t("Global Settings"))
    with st.expander(t("Global Settings"), expanded=True):
        global_tab = [t("Model Manage"),t("Knowledge Base Manage")]
        chosen_tab = stx.tab_bar(data=[
            stx.TabBarItemData(id=tab, title=tab, description="")
            for tab in global_tab
        ], default=global_tab[0])

        current_tab_index = next((index for index, tab in enumerate(global_tab) if tab == chosen_tab), 0)
        model_manage_container = st.container()
        kb_manage_container = st.container()

        if current_tab_index == 0:
            with model_manage_container:
                first_col()
                cols = st.columns([15,1,15,1,15],vertical_alignment='bottom')
                with cols[0]:
                    select_llm_model()
                    display_model_fields()
                with cols[2]:
                    select_embedding_model()
                    display_embedding_model_fields()
                with cols[4]:
                    select_reranker_model()
                    display_reranker_model_fields()
                load_btn()
            kb_manage_container.empty() 
        elif chosen_tab == t("Knowledge Base Manage"):
            with kb_manage_container:
                st.session_state.config['advanced_settings'] = advanced_settings()
            model_manage_container.empty() 
        # if current_tab_index == 0:
        #     first_col()
        #     select_llm_model()
        #     display_model_fields()
        #     select_embedding_model()
        #     display_embedding_model_fields()
        #     select_reranker_model()
        #     display_reranker_model_fields()
        #     load_btn()
        # else:
        #     st.session_state.config['advanced_settings'] = advanced_settings()
        
    nvidia_smi_watch()
    return st.session_state.config
