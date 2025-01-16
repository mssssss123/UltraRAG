import streamlit as st
import os
import asyncio
import jsonlines
import argparse
from pathlib import Path
from ultrarag.webui.utils.config import EMBEDDING_STEPS
import importlib
from ultrarag.webui.utils.language import t

# 设置路径
home_path = Path().resolve()
output_path = home_path / "output"


# 初始化 Streamlit 会话状态
def display():
    if 'embedding_training_data' not in st.session_state.dc_config:
        st.session_state.dc_config['embedding_training_data'] = {}
    with st.expander(f"Embedding {t('Configuration')}"):
        embedding_training_data_config = st.session_state.dc_config['embedding_training_data']
        embedding_training_data_config.setdefault('pipeline_step', "")
        
        pipeline_names = [pipeline["name"] for pipeline in EMBEDDING_STEPS]
        cols = st.columns([2, 4, 4])

        with cols[0]:
            selected_pipeline = st.selectbox(t("Select pipeline:"), pipeline_names)

        module_path = None
        for pipeline in EMBEDDING_STEPS:
            if pipeline["name"] == selected_pipeline:
                module_name = pipeline["name"]
                module_path = pipeline["module"]
                pipeline_step = pipeline["pipeline"]
                embedding_training_data_config["pipeline_step"] = pipeline_step
                break
        try:
            module = importlib.import_module(module_path)
        except ModuleNotFoundError:
            st.error(f"Module '{module_path}' not found.")
        if module_path:
            module.display()
        
