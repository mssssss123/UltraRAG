import streamlit as st
import os
from pathlib import Path
from ultrarag.webui.utils.language import t

# Set up paths
home_path = Path().resolve()
output_path = home_path / "output"


def display():
    # Initialize session state for configurations
    if 'train_config' not in st.session_state:
        st.session_state.train_config = {}
    if 'bgem3' not in st.session_state.train_config:
        st.session_state.train_config['bgem3'] = {}

    # BGEM3 Configuration UI
    with st.expander(f"BGEM3 {t('Configuration')}"):
        bgem3_config = st.session_state.train_config['bgem3']
        
        # Set default configuration values
        bgem3_config.setdefault('model_name_or_path', '/public/kqa/440M_v0')
        bgem3_config.setdefault('train_data', 'workspace/train_history_2/train_v3_incr.jsonl')
        bgem3_config.setdefault('train_group_size', 1)
        bgem3_config.setdefault('learning_rate', 7e-6)
        bgem3_config.setdefault('num_train_epochs', 2)
        bgem3_config.setdefault('per_device_train_batch_size', 128)
        bgem3_config.setdefault('query_max_len', 512)
        bgem3_config.setdefault('sentence_pooling_method', "mean")
        bgem3_config.setdefault('logging_steps', 1)
        bgem3_config.setdefault('save_steps', 1000)
        bgem3_config.setdefault('output_dir', str(output_path / "tuned_models"))
        bgem3_config.setdefault('query_instruction_for_retrieval', None)
        bgem3_config.setdefault('command', "bash scripts/finetune-bgem3.sh")
        
        # Create three-column layout
        cols = st.columns(3)

        # Column 1: Model and Training Settings
        with cols[0]:
            st.text_input(
                t("Model Path"),
                value=bgem3_config.get('model_name_or_path', 'resource/model'),
                key="model_name_or_path",
                on_change=lambda: bgem3_config.update(
                    {'model_name_or_path': st.session_state.model_name_or_path}
                ),
                help=t("Specify the model path."),
            )
            st.text_input(
                t("Training Data"),
                value=bgem3_config.get('train_data', 'resource/dataset/train.jsonl'),
                key="train_data",
                on_change=lambda: bgem3_config.update(
                    {'train_data': st.session_state.train_data}
                ),
                help=t("Specify the path to training data."),
            )
            st.number_input(
                t("Train Group Size"),
                value=bgem3_config.get('train_group_size', 1),
                min_value=1,
                max_value=10,
                step=1,
                key="train_group_size",
                on_change=lambda: bgem3_config.update(
                    {'train_group_size': st.session_state.train_group_size}
                ),
                help=t("Set the train group size."),
            )
            st.text_input(
                t("Sentence Pooling Method"),
                value=bgem3_config.get('sentence_pooling_method', ''),
                key="sentence_pooling_method",
                on_change=lambda: bgem3_config.update(
                    {'sentence_pooling_method': st.session_state.sentence_pooling_method}
                ),
                help=t("Specify the sentence pooling method."),
            )
        with cols[1]:
            st.number_input(
                t("Learning Rate"),
                value=bgem3_config.get('learning_rate', 7e-6),
                min_value=1e-8,
                max_value=1e-3,
                step=1e-6,
                key="learning_rate",
                on_change=lambda: bgem3_config.update(
                    {'learning_rate': st.session_state.learning_rate}
                ),
                help=t("Set the learning rate."),
            )
            st.number_input(
                t("Epochs"),
                value=bgem3_config.get('num_train_epochs', 2),
                min_value=1,
                max_value=100,
                step=1,
                key="num_train_epochs",
                on_change=lambda: bgem3_config.update(
                    {'num_train_epochs': st.session_state.num_train_epochs}
                ),
                help=t("Set the number of training epochs."),
            )
            st.number_input(
                t("Batch Size"),
                value=bgem3_config.get('per_device_train_batch_size', 128),
                min_value=1,
                max_value=1024,
                step=1,
                key="per_device_train_batch_size",
                on_change=lambda: bgem3_config.update(
                    {'per_device_train_batch_size': st.session_state.per_device_train_batch_size}
                ),
                help=t("Set the batch size."),
            )
            st.text_input(
                t("Output Dir"),
                value=bgem3_config.get('output_dir', str(output_path / "tuned_models")),
                key="output_dir",
                on_change=lambda: bgem3_config.update(
                    {'output_dir': st.session_state.output_dir}
                ),
                help=t("Specify the output directory."),
            )
        with cols[2]:
            st.text_input(
                t("Query Instruction"),
                value=bgem3_config.get('query_instruction_for_retrieval', None),
                key="query_instruction_for_retrieval",
                on_change=lambda: bgem3_config.update(
                    {'query_instruction_for_retrieval': st.session_state.query_instruction_for_retrieval}
                ),
                help=t("Query Instrustion."),
            )
            st.number_input(
                t("Query Max Length"),
                value=bgem3_config.get('query_max_len', 512),
                min_value=1,
                max_value=1024,
                step=1,
                key="query_max_len",
                on_change=lambda: bgem3_config.update(
                    {'query_max_len': st.session_state.query_max_len}
                ),
                help=t("Specify the maximum query length."),
            )
            st.number_input(
                t("Logging Steps"),
                value=bgem3_config.get('logging_steps', 1),
                min_value=1,
                max_value=1000,
                step=1,
                key="logging_steps",
                on_change=lambda: bgem3_config.update(
                    {'logging_steps': st.session_state.logging_steps}
                ),
                help=t("Specify logging steps interval."),
            )
            st.number_input(
                t("Save Steps"),
                value=bgem3_config.get('save_steps', 1000),
                min_value=1,
                max_value=10000,
                step=100,
                key="save_steps",
                on_change=lambda: bgem3_config.update(
                    {'save_steps': st.session_state.save_steps}
                ),
                help=t("Specify save steps interval."),
            )
