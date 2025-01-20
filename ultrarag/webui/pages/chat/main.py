import streamlit as st
import sys
from pathlib import Path
import importlib
import yaml

# Setup path configuration
home_path = Path().resolve()
sys.path.append(home_path.as_posix())

from utils.config import CHAT_PIPELINE
from ultrarag.webui.components.collection_selectbox import collection_selectbox
from ultrarag.webui.utils.language import t

def ensure_directory_exists(file_path):
    """
    Create directory if it doesn't exist.
    Args:
        file_path: Path to the file or directory to create
    """
    directory = Path(file_path).parent
    directory.mkdir(parents=True, exist_ok=True)

def save_config_to_file(config_path, config):
    """
    Save configuration to a YAML file.
    Args:
        config_path: Path where to save the configuration
        config: Configuration dictionary to save
    """
    try:
        ensure_directory_exists(config_path)
        with open(config_path, "w") as file:
            yaml.dump(config, file)
        st.success(t("Configuration saved to path.").format(path=config_path))
    except Exception as e:
        st.error(t("Error saving configuration: error.").format(error=e))

def load_config_from_file(config_path):
    """
    Load configuration from a YAML file.
    Args:
        config_path: Path to the configuration file
    """
    try:
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
            for key, value in config.items():
                st.session_state.chat_config[key] = value
        st.success(t("Configuration loaded from path.").format(path=config_path))
    except FileNotFoundError:
        st.error(t("Configuration file not found: path.").format(path=config_path))
    except Exception as e:
        st.error(t("Error loading configuration: error.").format(error=e))

def display(global_configs):
    if "chat_config" not in st.session_state:st.session_state.chat_config = {}
    chat_config = st.session_state.chat_config

    # Display main header and pipeline selection
    st.subheader(t("Chat/Inference"))
    pipeline_names = [pipeline["name"] for pipeline in CHAT_PIPELINE]
    cols = st.columns([2, 4, 4])

    # Pipeline selection dropdown
    with cols[0]:
        selected_pipeline = st.selectbox(t("Select pipeline:"), pipeline_names)

    # Load selected pipeline module
    module_path = None
    for pipeline in CHAT_PIPELINE:
        if pipeline["name"] == selected_pipeline:
            module_name = pipeline["name"]
            module_path = pipeline["module"]
            pipeline_type = pipeline["pipeline"]
            st.session_state.command_parameter["pipeline_type"] = pipeline_type
            break

    module = importlib.import_module(module_path)

    # Common configuration section
    st.write(f"### {t('Common Config')}")
    load_save_cols = st.columns([5, 5])

    # Configuration path input
    with load_save_cols[0]:
        config_path = st.text_input(
            t("Configuration Path"),
            f"./config/chat/{pipeline_type}-{st.session_state.now_time.strftime('%Y-%m-%d-%H-%M-%S')}.yml",
            help=t("Specify the path for saving or loading configurations.")
        )

    # Output directory input
    with load_save_cols[1]:
        output_path = st.text_input(
            t("Output Dir"),
            f"./output/chat/{pipeline_type}-{st.session_state.now_time.strftime('%Y-%m-%d-%H-%M-%S')}",
            help=t("Specify the path for saving output files.")
        )

    # Load/Save configuration buttons
    cols = st.columns([5, 5, 10])
    is_loaded = False
    
    with cols[0]:
        if st.button(t("Load Config")):
            load_config_from_file(config_path)
            is_loaded = True

    with cols[1]:
        if st.button(t("Save Config")):
            save_config_to_file(config_path, st.session_state.dc_config)
    
    # Knowledge base configuration
    cols = st.columns([5, 5], vertical_alignment='bottom')
    with cols[0]:
        if not is_loaded:
            chat_config["current_kb_config_id"],chat_config["collections"] = collection_selectbox()
            is_loaded=False
        else:
            chat_config["current_kb_config_id"],chat_config["collections"] = collection_selectbox(chat_config["current_kb_config_id"],chat_config["collections"])
    with cols[1]:
        try:
            st.text(f"{t('kb_csv_path')}:{st.session_state['kb_csv']}")
        except:
            st.warning(t("Please config the knowledge base."))

    # Pipeline specific configuration
    st.write(f"### {t('Pipeline Config')}")
    if module_path:
        module.display()