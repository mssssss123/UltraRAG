import streamlit as st
import os
from pathlib import Path
from ultrarag.webui.components.preview import parse_json_files, preview_dataset
import torch
from ultrarag.webui.utils.language import t
# Set paths
home_path = Path().resolve()
output_path = home_path / "output"
dataset_path = home_path / "resource/dataset/train_dataset"

def display():
    if 'train_config' not in st.session_state:
        st.session_state.train_config = {}
    if 'kbalign' not in st.session_state.train_config:
        st.session_state.train_config['kbalign'] = {}

    with st.expander(f"KBAlign {t('Configuration')}"):
        kbalign_config = st.session_state.train_config['kbalign']
        kbalign_config.setdefault('gpu_vis', '0,1,2,3')
        kbalign_config.setdefault('master_port', 2223)
        kbalign_config.setdefault('use_lora', True)
        kbalign_config.setdefault('model_name_or_path', "")
        kbalign_config.setdefault('train_data_path', [])
        kbalign_config.setdefault('eval_data_path', [])
        kbalign_config.setdefault('output_dir', "output/kbalign")
        kbalign_config.setdefault('logging_dir', "output/logs/kbalign")
        kbalign_config.setdefault('deepspeed_config_file', "config/pipeline/kbalign")
        kbalign_config.setdefault('config_file', "config/pipeline/finetune.yaml")
        kbalign_config.setdefault('log_file', "output/logs/kbalign/finetune_run.log")
        kbalign_config.setdefault('task_type', "SFT")
        kbalign_config.setdefault('command', "bash ultrarag/finetune/kbalign/train.sh")
        
        if torch.cuda.is_available():
            cuda_devices = [f"{i}" for i in range(torch.cuda.device_count())]
        else:
            cuda_devices = [t("No CUDA devices available")]
        default_selected_devices = [
            device for device in kbalign_config.get('gpu_vis', '').split(',') if device in cuda_devices
        ]

        cols1 = st.columns(3,vertical_alignment='center')
        with cols1[0]:
            st.checkbox(
                t("Use LoRA"),
                value=kbalign_config.get('use_lora', True),
                key="use_lora",
                on_change=lambda: kbalign_config.update({'use_lora': st.session_state.use_lora}),
                help=t("Enable or disable LoRA."),
            )
        if not dataset_path.exists():
            all_files = []
        else:
            all_files = [str(dataset_path / f) for f in os.listdir(dataset_path) if f.endswith(('.json', '.jsonl'))]
        col1, col2 = st.columns([1,1],vertical_alignment='bottom')
        with col1:
            kbalign_config['train_data_path'] = st.multiselect(
                t("Select Train Datasets"),
                options=all_files,
                default=kbalign_config.get('train_data_path', []),
                key="train_data_path",
                help=t("Select datasets to include in the test configuration.")
            )
        with col2:
            if st.button("Preview Selected train Datasets"):
                selected_files = kbalign_config['train_data_path']
                if not selected_files:
                    st.warning(t("No datasets selected to preview."))
                else:
                    preview_data = parse_json_files(selected_files)
                    preview_contents = []
                    for file, content in preview_data.items():
                        if isinstance(content, list):
                            preview_contents += content
                    preview_dataset("all_train_data_paths", preview_contents)
        col1, col2 = st.columns([1,1],vertical_alignment='bottom')
        with col1:
            kbalign_config['eval_data_path'] = st.multiselect(
                t("Select Eval Datasets"),
                options=all_files,
                default=kbalign_config.get('eval_data_path', []),
                key="eval_data_path",
                help=t("Select datasets to include in the test configuration.")
            )
        with col2:
            if st.button(t("Preview Selected eval Datasets")):
                selected_files = kbalign_config['eval_data_path']
                if not selected_files:
                    st.warning(t("No datasets selected to preview."))
                else:
                    preview_data = parse_json_files(selected_files)
                    preview_contents = []
                    for file, content in preview_data.items():
                        if isinstance(content, list):
                            preview_contents += content
                    preview_dataset("all_eval_data_paths", preview_contents)
        cols = st.columns(3)
        with cols[0]:
            selected_devices = st.multiselect(
                t("Select CUDA Devices"),
                options=cuda_devices,
                default=default_selected_devices,
                help=t("Select the GPUs you want to use."),
            )
            if 'No CUDA devices available' not in cuda_devices:
                gpu_vis = ','.join(selected_devices)
                kbalign_config['gpu_vis'] = gpu_vis
                st.session_state.gpu_vis = gpu_vis
            else:
                gpu_vis = t("No CUDA devices available")
                kbalign_config['gpu_vis'] = gpu_vis

            st.text_input(
                t("Output Dir"),
                value=kbalign_config.get('output_dir', "output/kbalign"),
                key="output_dir",
                on_change=lambda: kbalign_config.update({'output_dir': st.session_state.output_dir}),
                help=t("Specify the output directory."),
            )
            st.text_input(
                t("DeepSpeed Config File"),
                value=kbalign_config.get('deepspeed_config_file', "config/pipeline/kbalign"),
                key="deepspeed_config_file",
                on_change=lambda: kbalign_config.update({'deepspeed_config_file': st.session_state.deepspeed_config_file}),
                help=t("Specify the DeepSpeed configuration file path."),
            )
        with cols[1]:
            st.number_input(
                t("Master Port"),
                value=kbalign_config.get('master_port', 2223),
                min_value=1,
                max_value=65535,
                step=1,
                key="master_port",
                on_change=lambda: kbalign_config.update({'master_port': st.session_state.master_port}),
                help="Specify the master port.",
            )
            st.text_input(
                t("Logging Directory"),
                value=kbalign_config.get('logging_dir', "output/logs/kbalign"),
                key="logging_dir",
                on_change=lambda: kbalign_config.update({'logging_dir': st.session_state.logging_dir}),
                help=t("Specify the logging directory."),
            )
            st.text_input(
                t("YAML Config File"),
                value=kbalign_config.get('config_file', "config/pipeline/finetune.yaml"),
                key="config_file",
                on_change=lambda: kbalign_config.update({'config_file': st.session_state.config_file}),
                help=t("Specify the YAML configuration file path."),
            )
        with cols[2]:
            st.text_input(
                t("Model Path"),
                value=kbalign_config.get('model_name_or_path', ""),
                key="model_name_or_path",
                on_change=lambda: kbalign_config.update({'model_name_or_path': st.session_state.model_name_or_path}),
                help=t("Specify the model path."),
            )
            st.text_input(
                t("Log File"),
                value=kbalign_config.get('log_file', "output/logs/kbalign/finetune_run.log"),
                key="log_file",
                on_change=lambda: kbalign_config.update({'log_file': st.session_state.log_file}),
                help=t("Specify the log file path."),
            )
