import streamlit as st
from ultrarag.webui.utils.language import t

def display():
    # 初始化会话状态中的配置
    if 'data_synthesis_config' not in st.session_state.dc_config["embedding_training_data"]:
        st.session_state.dc_config["embedding_training_data"]['data_synthesis_config'] = {}
    data_synthesis_config = st.session_state.dc_config["embedding_training_data"]["data_synthesis_config"]

    # 设置默认值
    default_values = {
        'api_key': "",
        'base_url': "",
        'model_name': "",
        'language': "zh",
        'input_pair_path': "",
        'output_path': "",
        'query_num_per_corpus': 1,
        'corpus_sample_num': -1,
        'negs_start_index': 0,
        'negs_end_index': 20,
        'shot_num': 0,
        'shot_file': None,
        'input_prompt_path': None,
        'query_path': None,
        'corpus_path': None,
    }

    for key, value in default_values.items():
        data_synthesis_config.setdefault(key, value)

    cols = st.columns(3)

    with cols[0]:
        st.text_input(
            t("API Key"),
            value=data_synthesis_config.get('api_key', ''),
            key="ds_api_key",
            on_change=lambda: data_synthesis_config.update({'api_key': st.session_state.ds_api_key}),
            help=t("API key for authentication."),
        )
        st.text_input(
            t("Language"),
            value=data_synthesis_config.get('language', ''),
            key="ds_language",
            on_change=lambda: data_synthesis_config.update({'language': st.session_state.ds_language}),
            help=t("Select the language"),
        )
        st.number_input(
            t("Query Num per Corpus"),
            value=data_synthesis_config.get('query_num_per_corpus', 0),
            key="ds_query_num_per_corpus",
            on_change=lambda: data_synthesis_config.update({'query_num_per_corpus': st.session_state.ds_query_num_per_corpus}),
            help=t("Number of queries per corpus."),
        )
        st.number_input(
            t("Negs End Index"),
            value=data_synthesis_config.get('negs_end_index', 20),
            key="ds_negs_end_index",
            on_change=lambda: data_synthesis_config.update({'negs_end_index': st.session_state.ds_negs_end_index}),
            help=t("End index for negative samples."),
        )
        st.text_input(
            t("Query Path"),
            value=data_synthesis_config.get('query_path', ''),
            key="ds_query_path",
            on_change=lambda: data_synthesis_config.update({'query_path': st.session_state.ds_query_path}),
            help=t("Path to save the queries."),
        )
    with cols[1]:
        st.text_input(
            t("Base URL"),
            value=data_synthesis_config.get('base_url', ''),
            key="ds_base_url",
            on_change=lambda: data_synthesis_config.update({'base_url': st.session_state.ds_base_url}),
            help=t("Base URL"),
        )
        st.text_input(
            t("Input Pair Path"),
            value=data_synthesis_config.get('input_pair_path', ''),
            key="ds_input_pair_path",
            on_change=lambda: data_synthesis_config.update({'input_pair_path': st.session_state.ds_input_pair_path}),
            help="Path to the input pair data.",
        )
        st.number_input(
            t("Corpus Sample Num"),
            value=data_synthesis_config.get('corpus_sample_num', -1),
            key="ds_corpus_sample_num",
            on_change=lambda: data_synthesis_config.update({'corpus_sample_num': st.session_state.ds_corpus_sample_num}),
            help="Number of corpus samples (default: -1 for all samples).",
        )
        st.text_input(
            t("Shot File"),
            value=data_synthesis_config.get('shot_file', ''),
            key="ds_shot_file",
            on_change=lambda: data_synthesis_config.update({'shot_file': st.session_state.ds_shot_file}),
            help="Path to the shot file.",
        )
        st.text_input(
            t("Corpus Path"),
            value=data_synthesis_config.get('corpus_path', ''),
            key="ds_corpus_path",
            on_change=lambda: data_synthesis_config.update({'corpus_path': st.session_state.ds_corpus_path}),
            help=t("Path to the raw chunk data."),
        )
    with cols[2]:
        st.text_input(
            t("Model Name"),
            value=data_synthesis_config.get('model_name', ''),
            key="ds_model_name",
            on_change=lambda: data_synthesis_config.update({'model_name': st.session_state.ds_model_name}),
            help=t("Model Name"),
        )
        st.text_input(
            t("Output Path"),
            value=data_synthesis_config.get('output_path', ''),
            key="ds_output_path",
            on_change=lambda: data_synthesis_config.update({'output_path': st.session_state.ds_output_path}),
            help=t("Path to save the output."),
        )
        st.number_input(
            t("Negs Start Index"),
            value=data_synthesis_config.get('negs_start_index', 0),
            key="ds_negs_start_index",
            on_change=lambda: data_synthesis_config.update({'negs_start_index': st.session_state.ds_negs_start_index}),
            help=t("Start index for negative samples."),
        )
        st.text_input(
            t("Input Prompt Path"),
            value=data_synthesis_config.get('input_prompt_path', ''),
            key="ds_input_prompt_path",
            on_change=lambda: data_synthesis_config.update({'input_prompt_path': st.session_state.ds_input_prompt_path}),
            help=t("Path to the input prompts."),
        )    




