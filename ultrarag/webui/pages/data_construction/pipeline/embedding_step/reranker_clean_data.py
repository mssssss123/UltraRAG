import streamlit as st
from ultrarag.webui.utils.language import t

def display():
    if 'reranker_clean_data_config' not in st.session_state.dc_config["embedding_training_data"]:
        st.session_state.dc_config["embedding_training_data"]['reranker_clean_data_config'] = {}
    reranker_clean_data_config = st.session_state.dc_config["embedding_training_data"]["reranker_clean_data_config"]
    
    # Setting default values based on the required parameters
    reranker_clean_data_config.setdefault('reranker', "")
    reranker_clean_data_config.setdefault('corpus_path', "")
    reranker_clean_data_config.setdefault('qrel_path', "")
    reranker_clean_data_config.setdefault('output_path', "")
    reranker_clean_data_config.setdefault('search_start_index', 1)
    reranker_clean_data_config.setdefault('search_end_index', 30)
    reranker_clean_data_config.setdefault('keep_neg_num', 7)
    reranker_clean_data_config.setdefault('score_ratio', 1.0)
    reranker_clean_data_config.setdefault('score_margin', 0.0)
    reranker_clean_data_config.setdefault('min_pos_score', 0.0)
    reranker_clean_data_config.setdefault('max_neg_score', 1.0)
    
    cols = st.columns([3, 3, 3])
    
    with cols[0]:
        st.text_input(
            t("Reranker Model Path"),
            value=reranker_clean_data_config.get('reranker', ''),
            key="clean_data_reranker",
            on_change=lambda: reranker_clean_data_config.update(
                {'reranker': st.session_state.clean_data_reranker}
            ),
            help=t("Path to the reranker model."),
        )
        st.number_input(
            t("Search Start Index"),
            value=reranker_clean_data_config.get('search_start_index', 1),
            key="clean_data_emb_search_start_index",
            on_change=lambda: reranker_clean_data_config.update(
                {'search_start_index': st.session_state.clean_data_emb_search_start_index}
            ),
            help=t("Start index for search."),
        )
        st.number_input(
            t("Max Negative Score"),
            value=reranker_clean_data_config.get('max_neg_score', 1.0),
            key="clean_data_emb_max_neg_score",
            on_change=lambda: reranker_clean_data_config.update(
                {'max_neg_score': st.session_state.clean_data_emb_max_neg_score}
            ),
            help=t("Maximum negative score."),
        )
        st.number_input(
            t("Keep Negative Number"),
            value=reranker_clean_data_config.get('keep_neg_num', 7),
            key="clean_data_emb_keep_neg_num",
            on_change=lambda: reranker_clean_data_config.update(
                {'keep_neg_num': st.session_state.clean_data_emb_keep_neg_num}
            ),
            help=t("Number of negatives to keep."),
        )
    with cols[1]:
        st.text_input(
            t("QRel Path"),
            value=reranker_clean_data_config.get('qrel_path', ''),
            key="clean_data_emb_qrel_path",
            on_change=lambda: reranker_clean_data_config.update(
                {'qrel_path': st.session_state.clean_data_emb_qrel_path}
            ),
            help=t("Path to the qrel data."),
        )
        st.number_input(
            t("Search End Index"),
            value=reranker_clean_data_config.get('search_end_index', 30),
            key="clean_data_emb_search_end_index",
            on_change=lambda: reranker_clean_data_config.update(
                {'search_end_index': st.session_state.clean_data_emb_search_end_index}
            ),
            help=t("End index for search."),
        )
        st.number_input(
            t("Min Positive Score"),
            value=reranker_clean_data_config.get('min_pos_score', 0.0),
            key="clean_data_emb_min_pos_score",
            on_change=lambda: reranker_clean_data_config.update(
                {'min_pos_score': st.session_state.clean_data_emb_min_pos_score}
            ),
            help=t("Minimum positive score."),
        )
    with cols[2]:
        st.text_input(
            t("Output Path"),
            value=reranker_clean_data_config.get('output_path', ''),
            key="clean_data_emb_output_path",
            on_change=lambda: reranker_clean_data_config.update(
                {'output_path': st.session_state.clean_data_emb_output_path}
            ),
            help=t("Path to save the output."),
        )
        st.number_input(
            t("Score Ratio"),
            value=reranker_clean_data_config.get('score_ratio', 1.0),
            key="clean_data_emb_score_ratio",
            on_change=lambda: reranker_clean_data_config.update(
                {'score_ratio': st.session_state.clean_data_emb_score_ratio}
            ),
            help=t("Ratio for scoring."),
        )
        st.number_input(
            t("Score Margin"),
            value=reranker_clean_data_config.get('score_margin', 0.0),
            key="clean_data_emb_score_margin",
            on_change=lambda: reranker_clean_data_config.update(
                {'score_margin': st.session_state.clean_data_emb_score_margin}
            ),
            help=t("Margin for scoring."),
        )

