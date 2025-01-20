import streamlit as st
import torch
from ultrarag.webui.utils.language import t

def display():
    if 'ddr' not in st.session_state.dc_config:
        st.session_state.dc_config['ddr'] = {}
    ddr = st.session_state.dc_config["ddr"]

    # Set default configuration values
    ddr.setdefault('gpu_vis', '0,1,2,3')
    ddr.setdefault('data_model_name_or_path', "")
    ddr.setdefault('train_model_name_or_path', "")
    ddr.setdefault('config_path', "config/pipeline/ddr/datasets.yaml")
    ddr.setdefault('train_output_path', "resource/dataset/train_dataset/dpos_train.jsonl")
    ddr.setdefault('dev_output_path', "resource/dataset/train_dataset/dpos_dev.jsonl")
    ddr.setdefault("embedding_model_path", "") 
    ddr.setdefault('command', "bash ultrarag/datasets/DDR/workflow.sh")
    
    # Setup CUDA device selection
    if torch.cuda.is_available():
        cuda_devices = [f"{i}" for i in range(torch.cuda.device_count())]
    else:
        cuda_devices = [t("No CUDA devices available")]
    default_selected_devices = [
        device for device in ddr.get('gpu_vis', '').split(',') if device in cuda_devices
    ]

    # Display configuration interface
    with st.expander(f"DDR {t('Configuration')}"):
        cols = st.columns([3, 3, 3])

        # Column 1: GPU and Model Settings
        with cols[0]:
            # GPU device selection
            st.multiselect(
                t("Select CUDA Devices"),
                options=cuda_devices,
                default=default_selected_devices,
                key="ddr_cuda",
                help=t("Select the GPUs you want to use."),
                on_change=lambda: ddr.update({'gpu_vis': ','.join(st.session_state.ddr_cuda) if 'No CUDA devices available' not in cuda_devices else t("No CUDA devices available")})
            )

            # Model path inputs
            st.text_input(
                t("Data Model Name or Path"),
                value=ddr.get('data_model_name_or_path', ''),
                key="ddr_data_model_name_or_path",
                on_change=lambda: ddr.update(
                    {'data_model_name_or_path': st.session_state.ddr_data_model_name_or_path}
                ),
                help=t("Path to the data model or model name."),
            )
            st.text_input(
                t("Embedding Model Path"),
                value=ddr.get('embedding_model_path', ''),
                key="ddr_embedding_model_path",
                on_change=lambda: ddr.update(
                    {'embedding_model_path': st.session_state.ddr_embedding_model_path}
                ),
                help=t("Path to the embedding model.")
            )

        # Column 2: Training Configuration
        with cols[1]:
            st.text_input(
                t("Train Model Name or Path"),
                value=ddr.get('train_model_name_or_path', ''),
                key="ddr_train_model_name_or_path",
                on_change=lambda: ddr.update(
                    {'train_model_name_or_path': st.session_state.ddr_train_model_name_or_path}
                ),
                help=t("Path to the model to be trained."),
            )
            st.text_input(
                t("Config Path"),
                value=ddr.get('config_path', ''),
                key="ddr_config_path",
                on_change=lambda: ddr.update(
                    {'config_path': st.session_state.ddr_config_path}
                ),
                help=t("Path to the YAML configuration file."),
            )

        # Column 3: Output Configuration
        with cols[2]:
            st.text_input(
                t("Train Output Path"),
                value=ddr.get('train_output_path', ''),
                key="ddr_train_output_path",
                on_change=lambda: ddr.update(
                    {'train_output_path': st.session_state.ddr_train_output_path}
                ),
                help=t("Path to save the train data JSONL file."),
            )
            st.text_input(
                t("Dev Output Path"),
                value=ddr.get('dev_output_path', ''),
                key="ddr_dev_output_path",
                on_change=lambda: ddr.update(
                    {'dev_output_path': st.session_state.ddr_dev_output_path}
                ),
                help=t("Path to save the dev data JSONL file."),
            )
