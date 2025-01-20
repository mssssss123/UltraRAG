import streamlit as st
import sys
from pathlib import Path
import importlib
import yaml
import os
from datetime import datetime
import time
import torch
from utils.config import EVAL_PIPELINE, RETRIEVAL_METRICS, GENERATED_METRICS
from ultrarag.webui.components.preview import parse_json_files, preview_dataset
from ultrarag.webui.components.collection_selectbox import collection_selectbox
from ultrarag.webui.utils.language import t
import re

# Set up base paths for the application
home_path = Path().resolve()
sys.path.append(home_path.as_posix())
dataset_path = home_path / "resource/dataset/test_dataset"

def ensure_directory_exists(file_path):
    """Ensure the directory exists for the given file path."""
    directory = Path(file_path).parent
    directory.mkdir(parents=True, exist_ok=True)

def save_config_to_file(config_path, config):
    """Save configuration to a YAML file."""
    try:
        ensure_directory_exists(config_path)
        with open(config_path, "w") as file:
            yaml.dump(config, file)
        st.success(t("Configuration saved to path.").format(path=config_path))
    except Exception as e:
        st.error(t("Error saving configuration: error.").format(error=e))

def load_config_from_file(config_path):
    """Load configuration from a YAML file."""
    try:
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
            for key, value in config.items():
                st.session_state.eval_config[key] = value
        st.success(t("Configuration loaded from path.").format(path=config_path))
    except FileNotFoundError:
        st.error(t("Configuration file not found: path.").format(path=config_path))
    except Exception as e:
        st.error(t("Error loading configuration: error.").format(error=e))

def select_cuda_devices(device_key):
    """Create a selectbox for CUDA device selection."""
    if torch.cuda.is_available():
        cuda_devices = [f"cuda:{i}" for i in range(torch.cuda.device_count())]
    else:
        cuda_devices = [t("No CUDA devices available")]
    selected_devices = st.selectbox(
        t('Select CUDA Devices for') + f" {device_key}",
        cuda_devices
    )
    return selected_devices

def display(global_configs):
    """Main display function for evaluation configuration."""
    # Initialize session state and default values
    if "eval_config" not in st.session_state:
        st.session_state.eval_config = {}
    eval_config = st.session_state.eval_config
    
    # Set default values for configuration
    eval_config.setdefault('test_dataset', [])
    eval_config.setdefault('selected_retrieval_metrics', [])
    eval_config.setdefault('selected_generated_metrics', [])
    eval_config.setdefault('collections', [])
    eval_config.setdefault('collections_names', [])
    
    # Model and evaluation settings
    eval_config.setdefault("evaluate_only", False) 
    eval_config.setdefault("metric_api_key", "") 
    eval_config.setdefault("metric_base_url", "") 
    eval_config.setdefault("metric_model_name", "") 
    eval_config.setdefault("api_key", "")  
    eval_config.setdefault("base_url", "") 
    eval_config.setdefault("model_name", "") 
    
    # Model paths and types
    eval_config.setdefault("embedding_model_path", "") 
    eval_config.setdefault("reranker_model_path", "")  
    eval_config.setdefault("llm_type", "Local")  
    eval_config.setdefault("metric_llm_type", "API")  
    eval_config.setdefault("model_name_or_path", "")  
    eval_config.setdefault("metric_model_name_or_path", "")  

    # Retrieval settings
    eval_config.setdefault("pooling", "mean")
    eval_config.setdefault("query_instruction", None)
    eval_config.setdefault("queries_path", "")
    eval_config.setdefault("corpus_path", "")
    eval_config.setdefault("qrels_path", "")
    eval_config.setdefault("retrieval_output_path", "")
    eval_config.setdefault("log_path", None)
    eval_config.setdefault("topk", 10)
    eval_config.setdefault("cutoffs", "")
    
    # GPU settings
    eval_config.setdefault("embedding_gpu", "4")
    eval_config.setdefault("reranker_gpu", "4")

    # Setup CUDA device options
    if torch.cuda.is_available():
        cuda_devices = [f"{i}" for i in range(torch.cuda.device_count())]
    else:
        cuda_devices = [t("No CUDA devices available")]

    # Main UI components
    st.subheader(t("Evaluation"))
    
    # Pipeline selection
    pipeline_names = [pipeline["name"] for pipeline in EVAL_PIPELINE]
    cols = st.columns([2, 4, 4])

    with cols[0]:
        selected_pipeline = st.selectbox(t("Select pipeline:"), pipeline_names)

    # Load selected pipeline module
    module_path = None
    for pipeline in EVAL_PIPELINE:
        if pipeline["name"] == selected_pipeline:
            module_name = pipeline["name"]
            module_path = pipeline["module"]
            pipeline_type = pipeline["pipeline"]
            st.session_state.command_parameter["pipeline_type"] = pipeline_type
            break

    # Set default output path
    eval_config.setdefault(
        'output_path', 
        f"output/evaluate/{pipeline_type}-{st.session_state.now_time.strftime('%Y-%m-%d-%H-%M-%S')}"
    )
    
    module=""
    try:
        module = importlib.import_module(module_path)
    except Exception as e:
        # print(e)
        pass        


    st.write(f"### {t('Common Config')}")
    load_save_cols = st.columns([5, 5])

    with load_save_cols[0]:
        config_path = st.text_input(
            t("Configuration Path"),
            f"config/evaluate/{pipeline_type}-{st.session_state.now_time.strftime('%Y-%m-%d-%H-%M-%S')}.yml",
            help=t("Specify the path for saving or loading configurations.")
        )

    cols = st.columns([5, 5, 10])

    is_loaded=False
    with cols[0]:
        if st.button(t("Load Config")):
            load_config_from_file(config_path)
            is_loaded=True

    with cols[1]:
        if st.button(t("Save Config")):
            save_config_to_file(config_path, st.session_state.eval_config)

    if not dataset_path.exists():
        all_files = []
    else:
        all_files = [str(dataset_path / f) for f in os.listdir(dataset_path) if f.endswith(('.json', '.jsonl'))]

    cols = st.columns([5, 5])
    with cols[0]:
        eval_config["embedding_model_path"] = st.text_input(
            t("Embedding Model Path"),
            value=eval_config["embedding_model_path"],
            help=t("Path to the embedding model.")
        )
    with cols[1]:
        eval_config["embedding_gpu"] = select_cuda_devices("Embedding")
    col1, col2 = st.columns([1,1])
    with col1:
        with st.expander(t("Retrieval Evaluation"), expanded=True):
            st.multiselect(
                t("Retrieval Metrics"),
                options=RETRIEVAL_METRICS,
                default=eval_config.get('selected_retrieval_metrics', []),
                help=t("Select the retrieval metrics to evaluate (e.g., precision, recall)."),
                key="eval_selected_retrieval_metrics",
                on_change=lambda: eval_config.update(
                    {'selected_retrieval_metrics': st.session_state.eval_selected_retrieval_metrics}
                )
            )
            eval_config["pooling"] = st.text_input(
                t("Pooling Strategy"),
                value=eval_config["pooling"],
                help=t("Select the pooling strategy to use.")
            )
            eval_config["query_instruction"] = st.text_input(
                t("Query Instruction"),
                value=eval_config["query_instruction"] or "",
                help=t("Instruction to extract query text.")
            )
            eval_config["queries_path"] = st.text_input(
                t("Queries File Path"),
                value=eval_config["queries_path"],
                help=t("Path to the queries file.")
            )
            eval_config["corpus_path"] = st.text_input(
                t("Corpus File Path"),
                value=eval_config["corpus_path"],
                help=t("Path to the corpus file.")
            )
            eval_config["qrels_path"] = st.text_input(
                t("Qrels File Path"),
                value=eval_config["qrels_path"],
                help=t("Path to the qrels file.")
            )
            eval_config["retrieval_output_path"] = st.text_input(
                t("Output Results Path"),
                value=eval_config["retrieval_output_path"],
                help=t("Path to save the output results.")
            )
            eval_config["log_path"] = st.text_input(
                t("Log File Path"),
                value=eval_config["log_path"] or "",
                help=t("Path to save the log file (optional).")
            )
            eval_config["topk"] = st.number_input(
                t("Top K Documents"),
                value=eval_config["topk"],
                min_value=1,
                step=1,
                help=t("Top k documents to retrieve.")
            )
            eval_config["cutoffs"] = st.text_input(
                t("Cutoffs"),
                value=eval_config["cutoffs"] or "",
                help=t("Cutoff for evaluation metrics, separated by commas (e.g., 10,20,50).")
            )
    with col2:
        with st.expander(t("Generated Evaluation"), expanded=True):
            st.multiselect(
                t("Generated Metrics"),
                options=GENERATED_METRICS,
                default=eval_config.get('selected_generated_metrics', []),
                help=t("Select the generated metrics to evaluate (e.g., BLEU, ROUGE)."),
                key = "eval_selected_generated_metrics",
                on_change=lambda: eval_config.update(
                    {'selected_generated_metrics': st.session_state.eval_selected_generated_metrics}
                )
            )
            eval_config["evaluate_only"] = st.checkbox(
                t("Evaluate Only"),
                value=eval_config["evaluate_only"],
                help=t("If set, skip generation and directly evaluate datasets.")
            )
            cols = st.columns([5, 5],vertical_alignment='bottom')
            with cols[0]:
                if not is_loaded:
                    eval_config["current_kb_config_id"],eval_config["collections"] = collection_selectbox()
                    is_loaded=False
                else:
                    eval_config["current_kb_config_id"],eval_config["collections"] = collection_selectbox(eval_config["current_kb_config_id"],eval_config["collections"])
            with cols[1]:
                try:
                    st.text(f"{t('kb_csv_path')}:{st.session_state['kb_csv']}")
                except:
                    st.warning(t("Please config the knowledge base.")  ) 
            col1, col2 = st.columns([1,1],vertical_alignment='bottom')
            with col1:
                st.multiselect(
                    t("Select Test Datasets"),
                    options=all_files,
                    default=eval_config.get('test_dataset', []),
                    key="eval_config_test_dataset",
                    help=t("Select datasets to include in the test configuration."),
                    on_change=lambda: eval_config.update({'test_dataset': st.session_state.eval_config_test_dataset})
                )
            with col2:
                if st.button(t("Preview Selected Datasets")):
                    selected_files = eval_config['test_dataset']
                    if not selected_files:
                        st.warning(t("No datasets selected to preview."))
                    else:
                        preview_data = parse_json_files(selected_files)
                        preview_contents = []
                        for file, content in preview_data.items():
                            if isinstance(content, list):
                                preview_contents += content
                        preview_dataset("all_test_datasets", preview_contents)
            eval_config["llm_type"] = st.selectbox(
                t("Select LLM Model"),
                options=["API", "Local"],
                index=['API', 'Local'].index(
                    eval_config.get('llm_type', 'Local')
                ),
                key = "eval_select_llm_model",
                on_change=lambda: eval_config.update(
                    {'llm_type': st.session_state.eval_select_llm_model}
                ),
            )
            if eval_config["llm_type"] == "API":
                cols = st.columns([5, 5, 5])
                with cols[0]:
                    eval_config["api_key"] = st.text_input(
                        t("API Key"),
                        value=eval_config.get("api_key", ""),
                        help=t("API key for accessing the model.")
                    )
                with cols[1]:
                    eval_config["base_url"] = st.text_input(
                        t("Base URL"),
                        value=eval_config.get("base_url", ""),
                        help=t("Base URL for the API service.")
                    )
                with cols[2]:
                    eval_config["model_name"] = st.text_input(
                        t("Model Name"),
                        value=eval_config.get("model_name", ""),
                        help=t("Name of the model hosted on the API.")
                    )
            elif eval_config["llm_type"] == "Local":
                eval_config["model_name_or_path"] = st.text_input(
                    t("Model Name or Path"),
                    value=eval_config.get("model_name_or_path", ""),
                    help=t("Path or name of the locally hosted model.")
                )

            eval_config["metric_llm_type"] = st.selectbox(
                    t("Select Metric Model"),
                    options=["API", "Local"],
                    index=['API', 'Local'].index(
                        eval_config.get('metric_llm_type', 'Local')
                    ),
                    key = "eval_select_metric_model",
                    on_change=lambda: eval_config.update(
                        {'metric_llm_type': st.session_state.eval_select_metric_model}
                    ),
                )

            if eval_config["metric_llm_type"] == "API":
                cols = st.columns([5, 5, 5])
                with cols[0]:
                    eval_config["metric_api_key"] = st.text_input(
                        t("Metric API Key"),
                        value=eval_config.get("metric_api_key", ""),
                        help=t("API key for metric evaluation.")
                    )
                with cols[1]:
                    eval_config["metric_base_url"] = st.text_input(
                        t("Metric Base URL"),
                        value=eval_config.get("metric_base_url", ""),
                        help=t("Base URL for metric evaluation service.")
                    )
                with cols[2]:
                    eval_config["metric_model_name"] = st.text_input(
                        t("Metric Model Name"),
                        value=eval_config.get("metric_model_name", ""),
                        help=t("Model name for metric evaluation.")
                    )
            elif eval_config["metric_llm_type"] == "Local":
                eval_config["metric_model_name_or_path"] = st.text_input(
                    t("Metric Model Name or Path"),
                    value=eval_config.get("metric_model_name_or_path", ""),
                    help=t("Path or name of the locally hosted model.")
                )
            cols_gpu = st.columns([5, 5])
            with cols_gpu[0]:
                eval_config["reranker_model_path"] = st.text_input(
                    t("Reranker Model Path"),
                    value=eval_config["reranker_model_path"],
                    help=t("Path to the reranker model.")
                )
            with cols_gpu[1]:
                eval_config["reranker_gpu"] = select_cuda_devices("Reranker")
            eval_config["output_path"] = st.text_input(
                t("Output Dir"),
                eval_config.get("output_path", f"output/evaluate/{pipeline_type}-{st.session_state.now_time.strftime('%Y-%m-%d-%H-%M-%S')}"),
                help=t("Specify the path for saving output files.")
            )

    if module:
        st.write(f"### {t('Pipeline Config')}")
        module.display()
        
        
        
