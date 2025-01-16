import importlib
import streamlit as st
import extra_streamlit_components as stx
from utils.config import TABS
from ultrarag.webui.utils.language import t

if "active_tab" not in st.session_state:
    st.session_state.active_tab = TABS[0]["name"]  
if "file_path" not in st.session_state:
    st.session_state.file_path = TABS[0]["file_path"] 
    
def tab_bar(global_configs):
    st.header(t("Phase"))
    
    chosen_tab = stx.tab_bar(data=[
        stx.TabBarItemData(id=tab["name"], title=t(tab["name"]), description="")
        for tab in TABS
    ], default=TABS[0]["name"])
    
    st.session_state.active_tab = chosen_tab
    current_tab_index = next((index for index, tab in enumerate(TABS) if tab["name"] == chosen_tab), 0)
    st.session_state.file_path = TABS[current_tab_index]["file_path"]

    module_path = TABS[current_tab_index]["module"]
    module = importlib.import_module(module_path)
    module.display(global_configs) 

