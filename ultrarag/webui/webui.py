import streamlit as st
st.set_page_config(page_title="UltraRAG", page_icon="docs/assets/icon.png", layout='wide')
if "command_parameter" not in st.session_state: st.session_state.command_parameter = {}
from components.global_config import global_config
from components.tab_bar import tab_bar
from components.terminal import terminal
from datetime import datetime
if "now_time" not in st.session_state: st.session_state.now_time = datetime.now()

st.markdown(
    """
    <style>
    #root > div:nth-child(1) > div.withScreencast > div > div > div > div {
        left: 5vw; /* 设置左边距为 5vw */
    }
    </style>
    """,
    unsafe_allow_html=True,
)
st.logo(
    "docs/assets/logo.png",
    size='large',
)

def main():
    """
    Main function to setup and run the UltraRAG web interface.
    Configures page layout, initializes components and manages tab-based navigation.
    """
    # Configure main content area styling
    st.markdown(
        """
        <style>
        /* Adjust the padding of the main content area */
        .block-container {
            padding-top: 3rem;
            padding-bottom: 15vh;
            padding-left: 5vw;
            padding-right: 5vw;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Initialize global configurations and UI components
    global_configs = global_config()
    tab_bar(global_configs)
    
    # Display terminal for all tabs except Chat/Inference
    if st.session_state.active_tab != "Chat/Inference":
        terminal()

if __name__ == "__main__":
    main()
