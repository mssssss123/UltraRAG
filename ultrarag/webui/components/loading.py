import streamlit as st
from ultrarag.webui.utils.language import t

@st.fragment
def loading(text):
    if "loading" not in st.session_state: st.session_state["loading"] = False
    if st.session_state["loading"]:
        show_modal(text)
         
def show_modal(text):
    if text=="Loading":
        z=999
        color="rgba(255, 255, 255, 1)"
    elif text=="Error":
        z=1000
        color="rgba(255, 0, 0, 1)"
    else:
        z=998
        color="rgba(255, 255, 255, 1)"
        
        
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
            z-index: {z};">
            <div style="
                background-color: {color};
                color:black;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.25);
                text-align: center;
                ">
                <h3 style="color:black;">{text}...</h3>
                <p>{t('Please wait while the model is loading.')}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
