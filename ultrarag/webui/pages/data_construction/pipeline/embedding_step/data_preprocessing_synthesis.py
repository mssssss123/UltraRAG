import streamlit as st
from ultrarag.webui.utils.language import t

def display():
    if 'data_preprocessing_synthesis_config' not in st.session_state.dc_config["embedding_training_data"]:
        st.session_state.dc_config["embedding_training_data"]['data_preprocessing_synthesis_config'] = {}
    data_preprocessing_synthesis_config = st.session_state.dc_config["embedding_training_data"]["data_preprocessing_synthesis_config"]
    
    data_preprocessing_synthesis_config.setdefault('embed', "")
    data_preprocessing_synthesis_config.setdefault('pooling', "mean")
    data_preprocessing_synthesis_config.setdefault('corpus_path', "")
    data_preprocessing_synthesis_config.setdefault('output_path', "")
    data_preprocessing_synthesis_config.setdefault('search_start_index', 1)
    data_preprocessing_synthesis_config.setdefault('search_end_index', 30)
    
    cols = st.columns([3, 3, 3])
    
    with cols[0]:
        st.text_input(
            t("Embedding Model Path"),
            value=data_preprocessing_synthesis_config.get('embed', ''),
            key="dps_emb_embed",
            on_change=lambda: data_preprocessing_synthesis_config.update(
                {'embed': st.session_state.dps_emb_embed}
            ),
            help=t("Path to the embedding model."),
        )
        st.number_input(
            t("Search Start Index"),
            value=data_preprocessing_synthesis_config.get('search_start_index', 1),
            key="dps_emb_search_start_index",
            on_change=lambda: data_preprocessing_synthesis_config.update(
                {'search_start_index': st.session_state.dps_emb_search_start_index}
            ),
            help=t("Start index for search."),
        )
    with cols[1]:
        st.text_input(
            t("Pooling"),
            value=data_preprocessing_synthesis_config.get('pooling', 'mean'),
            key="dps_emb_pooling",
            on_change=lambda: data_preprocessing_synthesis_config.update(
                {'pooling': st.session_state.dps_emb_pooling}
            ),
            help=t("Pooling method."),
        )
        st.number_input(
            t("Search End Index"),
            value=data_preprocessing_synthesis_config.get('search_end_index', 30),
            key="dps_emb_search_end_index",
            on_change=lambda: data_preprocessing_synthesis_config.update(
                {'search_end_index': st.session_state.dps_emb_search_end_index}
            ),
            help=t("End index for search."),
        )
    with cols[2]:
        st.text_input(
            t("Corpus Path"),
            value=data_preprocessing_synthesis_config.get('corpus_path', ''),
            key="dps_emb_corpus_path",
            on_change=lambda: data_preprocessing_synthesis_config.update(
                {'corpus_path': st.session_state.dps_emb_corpus_path}
            ),
            help=t("Path to the raw chunk data."),
        )
        st.text_input(
            t("Output Path"),
            value=data_preprocessing_synthesis_config.get('output_path', ''),
            key="dps_emb_output_path",
            on_change=lambda: data_preprocessing_synthesis_config.update(
                {'output_path': st.session_state.dps_emb_output_path}
            ),
            help=t("Path to save the output."),
        )

