import streamlit as st
import sys
from pathlib import Path
import importlib
from ultrarag.webui.utils.language import t
import yaml
home_path = Path().resolve()
sys.path.append(home_path.as_posix())
from utils.config import DATA_PIPELINE
from ultrarag.webui.components.collection_selectbox import collection_selectbox

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
                st.session_state.dc_config[key] = value
        st.success(t("Configuration loaded from path.").format(path=config_path))
    except FileNotFoundError:
        st.error(t("Configuration file not found: path.").format(path=config_path))
    except Exception as e:
        st.error(t("Error loading configuration: error.").format(error=e))

def display(global_configs):
    if "dc_config" not in st.session_state:st.session_state.dc_config = {}
    dc_config = st.session_state.dc_config
    
    st.subheader(t("Data Construction"))
    pipeline_names = [pipeline["name"] for pipeline in DATA_PIPELINE]
    cols = st.columns([2, 4, 4])

    with cols[0]:
        selected_pipeline = st.selectbox(t("Select pipeline:"), pipeline_names)

    module_path = None
    pipeline_type = None
    for pipeline in DATA_PIPELINE:
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
            f"./config/data_construction/{pipeline_type}-{st.session_state.now_time.strftime('%Y-%m-%d-%H-%M-%S')}.yml",
            help=t("Specify the path for saving or loading configurations.")
        )

    with load_save_cols[1]:
        output_path = st.text_input(
            t("Output Dir"),
            f"./output/data_construction/{pipeline_type}-{st.session_state.now_time.strftime('%Y-%m-%d-%H-%M-%S')}",
            help=t("Specify the path for saving output files.")
        )

    cols = st.columns([5, 5, 10])

    is_loaded=False
    with cols[0]:
        if st.button(t("Load Config")):
            load_config_from_file(config_path)
            is_loaded=True

    with cols[1]:
        if st.button(t("Save Config")):
            save_config_to_file(config_path, st.session_state.dc_config)
            
    cols = st.columns([5, 5],vertical_alignment='bottom')
    with cols[0]:
        if not is_loaded:
            dc_config["current_kb_config_id"],dc_config["collections"] = collection_selectbox()
            is_loaded=False
        else:
            dc_config["current_kb_config_id"],dc_config["collections"] = collection_selectbox(dc_config["current_kb_config_id"],dc_config["collections"])
    with cols[1]:
        try:
            st.text(f"{t('kb_csv_path')}:{st.session_state['kb_csv']}")
        except:
            st.warning(t("Please config the knowledge base."))
    
    st.write(f"### {t('Pipeline Config')}")
    if module_path:
        module.display()