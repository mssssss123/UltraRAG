import streamlit as st
from ultrarag.modules.knowledge_managment import Knowledge_Managment
from ultrarag.webui.utils.language import t
from loguru import logger

def close_existing_searcher():
    if st.session_state.get("searcher"):
        st.session_state.searcher.close()
    try:
        st.session_state.selected_collection = [
            st.session_state['kb_df'].iloc[idx]["knowledge_base_id"]
            for idx, option in enumerate(st.session_state.get('filtered_options', []))
            if option in st.session_state.get('selected_options', [])
        ]
        if st.session_state.get("embedding") and st.session_state.selected_collection:
            st.session_state.searcher=Knowledge_Managment.get_searcher(
                embedding_model=st.session_state.get("embedding"),
                knowledge_id=st.session_state.selected_collection,
                knowledge_stat_tab_path = st.session_state['kb_csv']
            )
    except Exception as e:
        logger.warning(e)
        pass
    
def update_selection():
    selected = st.session_state['multiselect']
    kb_df = st.session_state.get('kb_df')
    if selected:
        selected_row = kb_df.apply(
            lambda row: f"{row['knowledge_base_name']}({row['knowledge_base_id']})", axis=1
        ) == selected[0]
        st.session_state['current_kb_config_id'] = kb_df[selected_row].iloc[0]['kb_config_id']
    else:
        st.session_state['current_kb_config_id'] = None
    st.session_state['selected_options'] = selected
    
    if kb_df is not None:
        st.session_state['filtered_options'] = kb_df.apply(
            lambda row: f"{row['knowledge_base_name']}({row['knowledge_base_id']})", axis=1
        ).values
        st.session_state['selected_options'] = selected
    close_existing_searcher()


def collection_selectbox(collections=None, selected_options=None):
    if 'current_kb_config_id' not in st.session_state:
        st.session_state['current_kb_config_id'] = None
    if 'selected_options' not in st.session_state:
        st.session_state['selected_options'] = []
        
    if collections:
        st.session_state['current_kb_config_id'] = collections
        st.session_state['selected_options'] = selected_options
        
    kb_df = st.session_state.get('kb_df')
        
    if st.session_state['current_kb_config_id'] is not None:
        filtered_df = kb_df[kb_df["kb_config_id"] == st.session_state['current_kb_config_id']]
    else:
        filtered_df = kb_df
    
    try:
        filtered_options = filtered_df.apply(lambda row: f"{row['knowledge_base_name']}({row['knowledge_base_id']})", axis=1).values
        selected_options = st.multiselect(
                                t("Select Collection"),
                                filtered_options,
                                default=st.session_state['selected_options'],
                                key="multiselect",
                                on_change=update_selection
                            )
        return st.session_state['current_kb_config_id'], selected_options
    except:
        st.text(t("Select Collection"))
        st.warning(t("Please Configure/Load Collection First"))
        return None, []
        