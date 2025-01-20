import streamlit as st
import os
from pathlib import Path
from ultrarag.webui.components.preview import parse_json_files, preview_dataset
import torch
from ultrarag.webui.utils.language import t

# Set up base paths for the application
home_path = Path().resolve()
output_path = home_path / "output"
dataset_path = home_path / "resource/dataset/train_dataset"

def display():
    # Initialize session state for configurations
    if 'train_config' not in st.session_state:
        st.session_state.train_config = {}
    if 'sft' not in st.session_state.train_config:
        st.session_state.train_config['sft'] = {}

    # SFT Configuration UI
    with st.expander(f"SFT {t('Configuration')}"):
        sft_config = st.session_state.train_config['sft']
        
        # Set default configuration values
        sft_config.setdefault('gpu_vis', '0,1,2,3')
        sft_config.setdefault('master_port', 2223)
        sft_config.setdefault('use_lora', True)
        sft_config.setdefault('model_name_or_path', "")
        sft_config.setdefault('train_data_path', [])
        sft_config.setdefault('eval_data_path', [])
        sft_config.setdefault('output_dir', "output/sft")
        sft_config.setdefault('logging_dir', "output/logs/sft")
        sft_config.setdefault('deepspeed_config_file', "config/pipeline/train/ds_config_zero2.json")
        sft_config.setdefault('config_file', "config/pipeline/finetune.yaml")
        sft_config.setdefault('log_file', "output/logs/sft/finetune_run.log")
        sft_config.setdefault('task_type', "SFT")
        sft_config.setdefault('command', "bash ultrarag/finetune/dpo_and_sft/train.sh")
        
        # Setup CUDA device selection
        if torch.cuda.is_available():
            cuda_devices = [f"{i}" for i in range(torch.cuda.device_count())]
        else:
            cuda_devices = [t("No CUDA devices available")]
        default_selected_devices = [
            device for device in sft_config.get('gpu_vis', '').split(',') 
            if device in cuda_devices
        ]

        # LoRA checkbox
        cols1 = st.columns(3, vertical_alignment='center')
        with cols1[0]:
            st.checkbox(
                t("Use LoRA"),
                value=sft_config.get('use_lora', True),
                key="use_lora",
                on_change=lambda: sft_config.update({'use_lora': st.session_state.use_lora}),
                help=t("Enable or disable LoRA."),
            )

        # Dataset file collection
        if not dataset_path.exists():
            all_files = []
        else:
            all_files = [
                str(dataset_path / f) 
                for f in os.listdir(dataset_path) 
                if f.endswith(('.json', '.jsonl'))
            ]

        # Training dataset selection and preview
        col1, col2 = st.columns([1,1], vertical_alignment='bottom')
        with col1:
            st.multiselect(
                t("Select Train Datasets"),
                options=all_files,
                default=sft_config.get('train_data_path', []),
                key="train_data_path",
                help=t("Select datasets to include in the test configuration."),
                on_change=lambda: sft_config.update({'train_data_path': st.session_state.train_data_path})
            )
        with col2:
            if st.button(t("Preview Selected train Datasets")):
                selected_files = sft_config['train_data_path']
                if not selected_files:
                    st.warning(t("No datasets selected to preview."))
                else:
                    preview_data = parse_json_files(selected_files)
                    preview_contents = [
                        item for file, content in preview_data.items() 
                        if isinstance(content, list) 
                        for item in content
                    ]
                    preview_dataset("all_train_data_paths", preview_contents)

        # Evaluation dataset selection and preview
        col1, col2 = st.columns([1,1], vertical_alignment='bottom')
        with col1:
            st.multiselect(
                t("Select Eval Datasets"),
                options=all_files,
                default=sft_config.get('eval_data_path', []),
                key="eval_data_path",
                help=t("Select datasets to include in the test configuration."),
                on_change=lambda: sft_config.update({'eval_data_path': st.session_state.eval_data_path})
            )
        with col2:
            if st.button(t("Preview Selected eval Datasets")):
                selected_files = sft_config['eval_data_path']
                if not selected_files:
                    st.warning(t("No datasets selected to preview."))
                else:
                    preview_data = parse_json_files(selected_files)
                    preview_contents = [
                        item for file, content in preview_data.items() 
                        if isinstance(content, list) 
                        for item in content
                    ]
                    preview_dataset("all_eval_data_paths", preview_contents)

        # Configuration columns
        cols = st.columns(3)
        
        # Column 1: Device and output settings
        with cols[0]:
            st.multiselect(
                t("Select CUDA Devices"),
                options=cuda_devices,
                default=default_selected_devices,
                key="kbalign_config_cuda",
                help=t("Select the GPUs you want to use."),
                on_change=lambda: sft_config.update({'gpu_vis': ','.join(st.session_state.kbalign_config_cuda) if 'No CUDA devices available' not in cuda_devices else t("No CUDA devices available")})
            )

            # Output directory and deepspeed config settings
            st.text_input(
                t("Output Directory"),
                value=sft_config.get('output_dir', "output/sft"),
                key="output_dir",
                on_change=lambda: sft_config.update({'output_dir': st.session_state.output_dir}),
                help=t("Specify the output directory."),
            )
            
            st.text_input(
                t("DeepSpeed Config File"),
                value=sft_config.get('deepspeed_config_file', "config/pipeline/train/ds_config_zero2.json"),
                key="deepspeed_config_file",
                on_change=lambda: sft_config.update(
                    {'deepspeed_config_file': st.session_state.deepspeed_config_file}
                ),
                help=t("Specify the DeepSpeed configuration file path."),
            )

        with cols[1]:
            st.number_input(
                t("Master Port"),
                value=sft_config.get('master_port', 2223),
                min_value=1,
                max_value=65535,
                step=1,
                key="master_port",
                on_change=lambda: sft_config.update({'master_port': st.session_state.master_port}),
                help=t("Specify the master port."),
            )
            st.text_input(
                t("Logging Directory"),
                value=sft_config.get('logging_dir', "output/logs/sft"),
                key="logging_dir",
                on_change=lambda: sft_config.update({'logging_dir': st.session_state.logging_dir}),
                help=t("Specify the logging directory."),
            )
            st.text_input(
                t("YAML Config File"),
                value=sft_config.get('config_file', "config/pipeline/finetune.yaml"),
                key="config_file",
                on_change=lambda: sft_config.update({'config_file': st.session_state.config_file}),
                help=t("Specify the YAML configuration file path."),
            )
        with cols[2]:
            st.text_input(
                t("Model Path"),
                value=sft_config.get('model_name_or_path', ""),
                key="model_name_or_path",
                on_change=lambda: sft_config.update({'model_name_or_path': st.session_state.model_name_or_path}),
                help=t("Specify the model path."),
            )
            st.text_input(
                t("Log File"),
                value=sft_config.get('log_file', "output/logs/sft/finetune_run.log"),
                key="log_file",
                on_change=lambda: sft_config.update({'log_file': st.session_state.log_file}),
                help=t("Specify the log file path."),
            )
