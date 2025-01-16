import streamlit as st
from ultrarag.webui.utils.language import t

def display():
    if 'dig_hard_neg_config' not in st.session_state.dc_config["embedding_training_data"]:
        st.session_state.dc_config["embedding_training_data"]['dig_hard_neg_config'] = {}
    dig_hard_neg_config = st.session_state.dc_config["embedding_training_data"]["dig_hard_neg_config"]
    
    # Setting default values based on the required parameters
    dig_hard_neg_config.setdefault('embed', "")
    dig_hard_neg_config.setdefault('pooling', "mean")
    dig_hard_neg_config.setdefault('query_instruction', None)
    dig_hard_neg_config.setdefault('corpus_path', "")
    dig_hard_neg_config.setdefault('qrel_path', "")
    dig_hard_neg_config.setdefault('output_path', "")
    dig_hard_neg_config.setdefault('search_start_index', 1)
    dig_hard_neg_config.setdefault('search_end_index', 30)
    
    cols = st.columns([3, 3, 3])
    
    with cols[0]:
        st.text_input(
            t("Embedding Model Path"),
            value=dig_hard_neg_config.get('embed', ''),
            key="dhn_emb_embed",
            on_change=lambda: dig_hard_neg_config.update(
                {'embed': st.session_state.dhn_emb_embed}
            ),
            help=t("Path to the embedding model."),
        )
        st.text_input(
            t("QRel Path"),
            value=dig_hard_neg_config.get('qrel_path', ''),
            key="dhn_emb_qrel_path",
            on_change=lambda: dig_hard_neg_config.update(
                {'qrel_path': st.session_state.dhn_emb_qrel_path}
            ),
            help=t("Path to the qrel data."),
        )
        st.number_input(
            t("Search Start Index"),
            value=dig_hard_neg_config.get('search_start_index', 1),
            key="dhn_emb_search_start_index",
            on_change=lambda: dig_hard_neg_config.update(
                {'search_start_index': st.session_state.dhn_emb_search_start_index}
            ),
            help=t("Start index for search."),
        )
    with cols[1]:
        st.text_input(
            t("Pooling"),
            value=dig_hard_neg_config.get('pooling', 'mean'),
            key="dhn_emb_pooling",
            on_change=lambda: dig_hard_neg_config.update(
                {'pooling': st.session_state.dhn_emb_pooling}
            ),
            help=t("Pooling method."),
        )
        st.text_input(
            t("Corpus Path"),
            value=dig_hard_neg_config.get('corpus_path', ''),
            key="dhn_emb_corpus_path",
            on_change=lambda: dig_hard_neg_config.update(
                {'corpus_path': st.session_state.dhn_emb_corpus_path}
            ),
            help=t("Path to the raw chunk data."),
        )
        st.number_input(
            t("Search End Index"),
            value=dig_hard_neg_config.get('search_end_index', 30),
            key="dhn_emb_search_end_index",
            on_change=lambda: dig_hard_neg_config.update(
                {'search_end_index': st.session_state.dhn_emb_search_end_index}
            ),
            help=t("End index for search."),
        )
        

    with cols[2]:
        st.text_input(
            t("Query Instruction"),
            value=dig_hard_neg_config.get('query_instruction', None),
            key="dhn_emb_query_instruction",
            on_change=lambda: dig_hard_neg_config.update(
                {'query_instruction': st.session_state.dhn_emb_query_instruction}
            ),
            help=t("Query instruction."),
        )
        st.text_input(
            t("Output Path"),
            value=dig_hard_neg_config.get('output_path', ''),
            key="dhn_emb_output_path",
            on_change=lambda: dig_hard_neg_config.update(
                {'output_path': st.session_state.dhn_emb_output_path}
            ),
            help=t("Path to save the output."),
        )
        