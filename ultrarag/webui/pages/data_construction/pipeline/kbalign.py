import streamlit as st
import torch
from ultrarag.webui.utils.language import t

def display():
    if 'kbalign' not in st.session_state.dc_config:
        st.session_state.dc_config['kbalign'] = {}
    kbalign = st.session_state.dc_config["kbalign"]

    # Default values for the parameters
    kbalign.setdefault('gpu_vis', '0,1,2,3')
    kbalign.setdefault('model_name_or_path', "")
    kbalign.setdefault('config_path', "config/pipeline/kbalign/datasets.yaml")
    kbalign.setdefault('embedding_model_path', "")
    kbalign.setdefault('knowledge_id', "")
    kbalign.setdefault('knowledge_stat_tab_path', "")
    kbalign.setdefault('language', "English") 
    kbalign.setdefault('functions_to_run', ["function_q", "function_qr"])
    kbalign.setdefault('output_dir', "resource/dataset/train_dataset/kbalign") 
    kbalign.setdefault('file_list', [f'{kbalign["output_dir"]}/kbalign_short_final_data/kbalign_short_final_data.jsonl',f'{kbalign["output_dir"]}/kbalign_long_final_data/kbalign_long_final_data.jsonl'])
    kbalign.setdefault('ratios', [1,1])
    kbalign.setdefault('fixed_steps', 4)
    kbalign.setdefault('short_target_num', 2000)
    kbalign.setdefault('long_target_num', 2000)
    kbalign.setdefault('random_merge', False)
    kbalign.setdefault('clustering', False)
    kbalign.setdefault('output_file', "resource/dataset/train_dataset/kbalign.jsonl")
    kbalign.setdefault('output_format', "jsonl")

    # Check available CUDA devices
    if torch.cuda.is_available():
        cuda_devices = [f"{i}" for i in range(torch.cuda.device_count())]
    else:
        cuda_devices = [t("No CUDA devices available")]
    
    default_selected_devices = [
        device for device in kbalign.get('gpu_vis', '').split(',') if device in cuda_devices
    ]
    
    # Streamlit UI
    with st.expander(f"KBAlign {t('Configuration')}"):
        cols = st.columns([3, 3, 3])

        # First column (CUDA devices, Model Paths)
        with cols[0]:
            st.multiselect(
                t("Select CUDA Devices"),
                options=cuda_devices,
                default=default_selected_devices,
                key="kbalign_cuda",
                help=t("Select the GPUs you want to use."),
                on_change=lambda: kbalign.update({'gpu_vis': ','.join(st.session_state.kbalign_cuda) if 'No CUDA devices available' not in cuda_devices else t("No CUDA devices available")})
            )
            # Text input for model name or path
            st.text_input(
                t("Model Name or Path"),
                value=kbalign.get('model_name_or_path', ''),
                key="kbalign_model_name_or_path",
                on_change=lambda: kbalign.update(
                    {'model_name_or_path': st.session_state.kbalign_model_name_or_path}
                ),
                help=t("Path to the LLM model or model name."),
            )

            # Text input for embedding model path
            st.text_input(
                t("Embedding Model Path"),
                value=kbalign.get('embedding_model_path', ''),
                key="kbalign_embedding_model_path",
                on_change=lambda: kbalign.update(
                    {'embedding_model_path': st.session_state.kbalign_embedding_model_path}
                ),
                help=t("Path to the embedding model.")
            )
            st.text_input(
                t("Output File"),
                value=kbalign.get('output_file', ''),
                key="kbalign_output_file",
                on_change=lambda: kbalign.update(
                    {'output_file': st.session_state.kbalign_output_file}
                ),
                help=t("Specify the name of the output file."),
            )
            st.number_input(
                t("Short Target Num"),
                value=kbalign.get('short_target_num', 2000),
                key="kbalign_short_target_num",
                on_change=lambda: kbalign.update(
                    {'short_target_num': st.session_state.kbalign_short_target_num}
                ),
                step=1,
                help=t("If set to -1, the full dataset will be generated based on the knowledge base size."),
            )


        with cols[1]:
            st.text_input(
                t("Config Path"),
                value=kbalign.get('config_path', ''),
                key="kbalign_config_path",
                on_change=lambda: kbalign.update(
                    {'config_path': st.session_state.kbalign_config_path}
                ),
                help=t("Path to the YAML configuration file."),
            )

            st.selectbox(
                t("Output Format"),
                options=["json", "jsonl"],
                index=['json', 'jsonl'].index(
                    kbalign.get('output_format', 'jsonl')
                ),
                key="kbalign_output_format",
                on_change=lambda: kbalign.update(
                    {'output_format': st.session_state.kbalign_output_format}
                ),
                help=t("Choose the output format."),
            )
            st.number_input(
                t("Fixed Steps"),
                value=kbalign.get('fixed_steps', 0),
                key="kbalign_fixed_steps",
                on_change=lambda: kbalign.update(
                    {'fixed_steps': st.session_state.kbalign_fixed_steps}
                ),
                step=1,
                help=t("Specify the fixed step size for merging."),
            )
            st.text_input(
                t("Ratios (Space-separated)"),
                value=" ".join(map(str, kbalign.get('ratios', []))),
                key="kbalign_ratios",
                on_change=lambda: kbalign.update(
                    {'ratios': list(map(int, st.session_state.kbalign_ratios.split()))}
                ),
                help=t("Proportions for each file in format 1:2:3."),
            )
            st.number_input(
                t("Long Target Num"),
                value=kbalign.get('long_target_num', 2000),
                key="kbalign_long_target_num",
                on_change=lambda: kbalign.update(
                    {'long_target_num': st.session_state.kbalign_long_target_num}
                ),
                step=1,
                help=t("If set to -1, the full dataset will be generated based on the knowledge base size."),
            )         
        with cols[2]:
            st.text_input(
                t("Output Dir"),
                value=kbalign.get('output_dir', ''),
                key="kbalign_output_dir",
                on_change=lambda: kbalign.update(
                    {
                        'output_dir': st.session_state.kbalign_output_dir,
                        'file_list': [f'{st.session_state.kbalign_output_dir}/kbalign_short_final_data/kbalign_short_final_data.jsonl',f'{st.session_state.kbalign_output_dir}/kbalign_long_final_data/kbalign_long_final_data.jsonl']
                    }
                ),
                help=t("Specify the path for saving output files."),
            )

            st.selectbox(
                "Language",
                options=["Chinese", "English"],
                index=["Chinese", "English"].index(
                    kbalign.get('language', 'English')
                ),
                key="kbalign_language",
                on_change=lambda: kbalign.update(
                    {'language': st.session_state.kbalign_language}
                ),
                help=t("Select the language"),
            )

            st.multiselect(
                t("Functions to Run"),
                options=["function_q", "function_qr"],  # 可以根据实际需求增加更多选项
                default=kbalign.get('functions_to_run', []),  # 默认为空列表或从配置中获取
                key="kbalign_functions_to_run",
                on_change=lambda: kbalign.update(
                    {'functions_to_run': st.session_state.kbalign_functions_to_run}
                ),
                help=t("Select which functions to run (e.g., function_q, function_qr)."),
            )
            st.checkbox(
                t("Random Merge"),
                value=kbalign.get('random_merge', False),
                key="kbalign_random_merge",
                on_change=lambda: kbalign.update(
                    {'random_merge': st.session_state.kbalign_random_merge}
                ),
                help=t("Enable or disable random merging."),
            )
            st.checkbox(
                t("Clustering"),
                value=kbalign.get('clustering', False),
                key="kbalign_clustering",
                on_change=lambda: kbalign.update(
                    {'clustering': st.session_state.kbalign_clustering}
                ),
                help=t("Heterogeneous data requires clustering."),
            )