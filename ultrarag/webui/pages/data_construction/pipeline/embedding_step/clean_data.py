import streamlit as st
from ultrarag.webui.utils.language import t

def display():
    if 'clean_data_config' not in st.session_state.dc_config["embedding_training_data"]:
        st.session_state.dc_config["embedding_training_data"]['clean_data_config'] = {}
    clean_data_config = st.session_state.dc_config["embedding_training_data"]["clean_data_config"]
    
    # Setting default values based on the required parameters
    clean_data_config.setdefault('embed', "")
    clean_data_config.setdefault('pooling', "mean")
    clean_data_config.setdefault('query_instruction', None)
    clean_data_config.setdefault('corpus_path', "")
    clean_data_config.setdefault('qrel_path', "")
    clean_data_config.setdefault('output_path', "")
    clean_data_config.setdefault('search_start_index', 1)
    clean_data_config.setdefault('search_end_index', 30)
    clean_data_config.setdefault('keep_neg_num', 7)
    clean_data_config.setdefault('score_ratio', 1.0)
    clean_data_config.setdefault('score_margin', 0.0)
    clean_data_config.setdefault('min_pos_score', 0.0)
    clean_data_config.setdefault('max_neg_score', 1.0)
    
    cols = st.columns([3, 3, 3])
    
    with cols[0]:
        st.text_input(
            t("Embedding Model Path"),
            value=clean_data_config.get('embed', ''),
            key="clean_data_emb_embed",
            on_change=lambda: clean_data_config.update(
                {'embed': st.session_state.clean_data_emb_embed}
            ),
            help=t("Path to the embedding model."),
        )
        st.text_input(
            t("QRel Path"),
            value=clean_data_config.get('qrel_path', ''),
            key="clean_data_emb_qrel_path",
            on_change=lambda: clean_data_config.update(
                {'qrel_path': st.session_state.clean_data_emb_qrel_path}
            ),
            help=t("Path to the qrel data."),
        )
        st.number_input(
            t("Search Start Index"),
            value=clean_data_config.get('search_start_index', 1),
            key="clean_data_emb_search_start_index",
            on_change=lambda: clean_data_config.update(
                {'search_start_index': st.session_state.clean_data_emb_search_start_index}
            ),
            help=t("Start index for search."),
        )
        st.number_input(
            t("Max Negative Score"),
            value=clean_data_config.get('max_neg_score', 1.0),
            key="clean_data_emb_max_neg_score",
            on_change=lambda: clean_data_config.update(
                {'max_neg_score': st.session_state.clean_data_emb_max_neg_score}
            ),
            help=t("Maximum negative score."),
        )
        
        
    with cols[1]:
        st.text_input(
            t("Pooling"),
            value=clean_data_config.get('pooling', 'mean'),
            key="dhn_emb_pooling",
            on_change=lambda: clean_data_config.update(
                {'pooling': st.session_state.dhn_emb_pooling}
            ),
            help=t("Pooling method."),
        )
        st.text_input(
            t("Output Path"),
            value=clean_data_config.get('output_path', ''),
            key="clean_data_emb_output_path",
            on_change=lambda: clean_data_config.update(
                {'output_path': st.session_state.clean_data_emb_output_path}
            ),
            help=t("Path to save the output."),
        )
        st.number_input(
            t("Search End Index"),
            value=clean_data_config.get('search_end_index', 30),
            key="clean_data_emb_search_end_index",
            on_change=lambda: clean_data_config.update(
                {'search_end_index': st.session_state.clean_data_emb_search_end_index}
            ),
            help=t("End index for search."),
        )
        st.number_input(
            t("Min Positive Score"),
            value=clean_data_config.get('min_pos_score', 0.0),
            key="clean_data_emb_min_pos_score",
            on_change=lambda: clean_data_config.update(
                {'min_pos_score': st.session_state.clean_data_emb_min_pos_score}
            ),
            help=t("Minimum positive score."),
        )
        
    with cols[2]:
        st.text_input(
            t("Query Instruction"),
            value=clean_data_config.get('query_instruction', None),
            key="dhn_emb_query_instruction",
            on_change=lambda: clean_data_config.update(
                {'query_instruction': st.session_state.dhn_emb_query_instruction}
            ),
            help=t("Query instruction."),
        )
        st.number_input(
            t("Keep Negative Number"),
            value=clean_data_config.get('keep_neg_num', 7),
            key="clean_data_emb_keep_neg_num",
            on_change=lambda: clean_data_config.update(
                {'keep_neg_num': st.session_state.clean_data_emb_keep_neg_num}
            ),
            help=t("Number of negatives to keep."),
        )
        
        st.number_input(
            t("Score Ratio"),
            value=clean_data_config.get('score_ratio', 1.0),
            key="clean_data_emb_score_ratio",
            on_change=lambda: clean_data_config.update(
                {'score_ratio': st.session_state.clean_data_emb_score_ratio}
            ),
            help=t("Ratio for scoring."),
        )
        st.number_input(
            t("Score Margin"),
            value=clean_data_config.get('score_margin', 0.0),
            key="clean_data_emb_score_margin",
            on_change=lambda: clean_data_config.update(
                {'score_margin': st.session_state.clean_data_emb_score_margin}
            ),
            help=t("Margin for scoring."),
        )

