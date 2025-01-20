import streamlit as st
import sys
from pathlib import Path
import importlib
import yaml
home_path = Path().resolve()
sys.path.append(home_path.as_posix())
from ultrarag.webui.utils.config import TRAIN_PIPELINE
from ultrarag.webui.components.terminal import terminal
from ultrarag.webui.utils.language import t

def ensure_directory_exists(file_path):
    directory = Path(file_path).parent
    directory.mkdir(parents=True, exist_ok=True)

def save_config_to_file(config_path, config):
    try:
        ensure_directory_exists(config_path)
        with open(config_path, "w") as file:
            yaml.dump(config, file)
        st.success(t("Configuration saved to path.").format(path=config_path))
    except Exception as e:
        st.error(t("Error saving configuration: error.").format(error=e))

def load_config_from_file(config_path):
    try:
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
            for key, value in config.items():
                st.session_state.train_config[key] = value
        st.success(t("Configuration loaded from path.").format(path=config_path))
    except FileNotFoundError:
        st.error(t("Configuration file not found: path.").format(path=config_path))
    except Exception as e:
        st.error(t("Error loading configuration: error.").format(error=e))

def display(global_configs):
    if "train_config" not in st.session_state:st.session_state.train_config = {}
    train_config = st.session_state.train_config
    if "lora_config" not in train_config:train_config["lora_config"] = {}
    lora_config = train_config["lora_config"]

    lora_config.setdefault('model_name_or_path', "")
    lora_config.setdefault('lora_name_or_path', "")
    lora_config.setdefault('save_path', "")
    
    st.subheader(t("Train"))
    pipeline_names = [pipeline["name"] for pipeline in TRAIN_PIPELINE]
    cols = st.columns([2, 4, 4])

    with cols[0]:
        selected_pipeline = st.selectbox(t("Select pipeline:"), pipeline_names)

    module_path = None
    for pipeline in TRAIN_PIPELINE:
        if pipeline["name"] == selected_pipeline:
            module_name = pipeline["name"]
            module_path = pipeline["module"]
            pipeline_type = pipeline["pipeline"]
            st.session_state.command_parameter["pipeline_type"] = pipeline_type
            break

    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError:
        st.error(f"Module '{module_path}' not found.")
        return
    except AttributeError:
        st.error(f"Module '{module_path}' does not have a 'display' function.")
        return


    st.write(f"### {t('Common Config')}")
    load_save_cols = st.columns([5, 5])

    with load_save_cols[0]:
        config_path = st.text_input(
            t("Configuration Path"),
            f"./config/train/{pipeline_type}-{st.session_state.now_time.strftime('%Y-%m-%d-%H-%M-%S')}.yml",
            help=t("Specify the path for saving or loading configurations.")
        )

    with load_save_cols[1]:
        output_path = st.text_input(
            t("Output Dir"),
            f"./output/train/{pipeline_type}-{st.session_state.now_time.strftime('%Y-%m-%d-%H-%M-%S')}",
            help=t("Specify the path for saving output files.")
        )

    cols = st.columns([5, 5, 10])

    with cols[0]:
        if st.button(t("Load Config")):
            load_config_from_file(config_path)

    with cols[1]:
        if st.button(t("Save Config")):
            save_config_to_file(config_path, st.session_state.train_config)

    st.write(f"### {t('LoRA Merge')}")
    with st.expander(f"{t('LoRA Merge')}"):
        st.text_input(
            t("Model Name or Path"),
            value=lora_config.get('model_name_or_path', ""),
            key="lora_config_model_name_or_path",
            on_change=lambda: lora_config.update({'model_name_or_path': st.session_state.lora_config_model_name_or_path}),
            help=t("Path to the base model or model name."),
        )
        st.text_input(
            t("LoRA Name or Path"),
            value=lora_config.get('lora_name_or_path', ""),
            key="lora_config_lora_name_or_path",
            on_change=lambda: lora_config.update({'lora_name_or_path': st.session_state.lora_config_lora_name_or_path}),
            help=t("Path to the LoRA checkpoint."),
        )
        st.text_input(
            t("Save Path"),
            value=lora_config.get('save_path', ""),
            key="lora_config_save_path",
            on_change=lambda: lora_config.update({'save_path': st.session_state.lora_config_save_path}),
            help=t("Path to save the merged model."),
        )
        terminal("python ultrarag/finetune/dpo_and_sft/Merge_model.py",lora_config,"lora")
        
    st.write(f"### {t('Pipeline Config')}")
    if module_path:
        module.display()
        
    