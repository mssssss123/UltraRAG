import streamlit as st
from ultrarag.webui.utils.language import t

@st.fragment
def loading(text):
    """
    Display a loading modal with customizable text.
    
    Args:
        text: Text to display in the loading modal
    """
    # Initialize loading state if not exists
    if "loading" not in st.session_state: 
        st.session_state["loading"] = False
        
    # Show modal if loading state is True
    if st.session_state["loading"]:
        show_modal(text)
         
def show_modal(text):
    """
    Show a modal overlay with specified text and styling.
    
    Args:
        text: Text to display in the modal
    """
    # Set z-index and color based on text type
    if text == "Loading":
        z_index = 999
        color = "rgba(255, 255, 255, 1)"
    elif text == "Error":
        z_index = 1000
        color = "rgba(255, 0, 0, 1)"
    else:
        z_index = 998
        color = "rgba(255, 255, 255, 1)"
        
    # Display modal using HTML/CSS
    st.markdown(
        f"""
        <div style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: {z_index};">
            <div style="
                background-color: {color};
                color: black;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.25);
                text-align: center;
                ">
                <h3 style="color: black;">{text}...</h3>
                <p>{t('Please wait while the model is loading.')}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
