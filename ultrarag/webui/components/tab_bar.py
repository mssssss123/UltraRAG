import importlib
import streamlit as st
import extra_streamlit_components as stx
from utils.config import TABS
from ultrarag.webui.utils.language import t

def tab_bar(global_configs):
    """
    Display and manage a tab bar interface for navigation.
    
    Args:
        global_configs: Dictionary containing global configuration settings
    """
    # Initialize session state variables if not exists
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = TABS[0]["name"]
        
    if "file_path" not in st.session_state:
        st.session_state.file_path = TABS[0]["file_path"]
        
    # Display phase header
    st.header(t("Phase"))
    
    # Create tab bar with translated tab titles
    chosen_tab = stx.tab_bar(data=[
        stx.TabBarItemData(
            id=tab["name"], 
            title=t(tab["name"]), 
            description=""
        )
        for tab in TABS
    ], default=TABS[0]["name"])
    
    # Update session state with chosen tab
    st.session_state.active_tab = chosen_tab
    
    # Find current tab index and update file path
    current_tab_index = next(
        (index for index, tab in enumerate(TABS) if tab["name"] == chosen_tab), 
        0
    )
    st.session_state.file_path = TABS[current_tab_index]["file_path"]

    # Import and display module for current tab
    module_path = TABS[current_tab_index]["module"]
    module = importlib.import_module(module_path)
    module.display(global_configs) 

