import streamlit as st
import os
from pathlib import Path
from ultrarag.webui.components.collection_selectbox import close_existing_searcher

home_path = Path().resolve()
output_path = home_path / "output"

import asyncio
import time
from loguru import logger
from ultrarag.workflow.ultraragflow import NaiveFlow
from ultrarag.common.utils import get_debug_fold
import pandas as pd
from ultrarag.webui.utils.language import t



def display_configurations():
    """
    Display Vanilla RAG configurations in a Streamlit expander.
    Initializes necessary session states and handles model/collection setup.
    """
    # Initialize session states if not exists
    if 'chat_config' not in st.session_state:
        st.session_state.chat_config = {}

    if "naive_flow_inst" not in st.session_state:
        st.session_state.naive_flow_inst = ""

    if "collection" not in st.session_state:
        st.session_state.collection = []

    if "simple_rag_history" not in st.session_state:
        st.session_state.simple_rag_history = []
        st.session_state.simple_rag_messages = []

    # Display configuration expander
    with st.expander("Vanilla RAG"):
        if 'selected_options' not in st.session_state:
            st.session_state['selected_options'] = []
        if 'current_kb_config_id' not in st.session_state:
            st.session_state['current_kb_config_id'] = None
            
        # Initialize NaiveFlow if knowledge base is loaded
        kb_df = st.session_state.get('kb_df')
        if (isinstance(kb_df, pd.DataFrame)) and not kb_df.empty:
            try:
                st.session_state.naive_flow_inst = NaiveFlow.from_modules(
                    llm=st.session_state.llm,
                    index=st.session_state.searcher,
                    reranker=st.session_state.reranker
                )
                if st.button(t("clear history"), type="primary"):
                    st.session_state.simple_rag_history = []
                    st.session_state.simple_rag_messages = []
            except Exception as e:
                print(e)
                st.warning(t("Please load the model and select the collections"))
        else:
            try:
                st.session_state['selected_options'] = []
                st.session_state['current_kb_config_id'] = None
                st.session_state.naive_flow_inst = ""
            except:
                pass
            close_existing_searcher()
            
async def listen(query, container):
    """
    Listen for and process chat responses asynchronously.
    
    Args:
        query: User input query
        container: Streamlit container for displaying responses
    
    Returns:
        tuple: (response with debug info, pure response)
    """
    process_info = ""
    buff = ""
    time_start, first_response = time.perf_counter(), 0            

    # Get response from RAG instance
    rag_link = st.session_state.naive_flow_inst
    response = await rag_link.aquery(
        query=query, 
        messages=st.session_state.simple_rag_messages, 
        collection=st.session_state.selected_collection
    )

    # Process streaming response
    async for chunk in response:
        if first_response == 0 and isinstance(chunk, dict) and chunk['state'] == "data": 
            first_response = time.perf_counter() - time_start
        
        # Handle different response states
        if isinstance(chunk, dict):
            if chunk["state"] == "recall": 
                process_info = get_debug_fold(title="recall", context=chunk['value'])
            if chunk['state'] == "data": 
                buff += chunk['value']
        else:
            buff += chunk
            
        # Update display
        container.chat_message("assistant").markdown(process_info + buff, unsafe_allow_html=True)

    # Add timing information
    extra_infos = f"\n\nspend: {time.perf_counter() - time_start :.2f} s, first response {first_response:.2f} s"
    container.chat_message("assistant").markdown(process_info + buff + extra_infos, unsafe_allow_html=True)
    return process_info + buff + extra_infos, buff

@st.fragment
def chat_component():
    """
    Display the chat interface component.
    Handles message history, user input, and response display.
    """
    st.subheader(f"{t('Welcome to ')}Vanilla RAG")

    # Setup chat container
    his_container = st.container(height=500)
    
    with his_container:
        # Display chat history
        for (query, response) in st.session_state.simple_rag_history:
            with st.chat_message(name="user", avatar="user"):
                st.markdown(query, unsafe_allow_html=True)
            with st.chat_message(name="assistant", avatar="assistant"):
                st.markdown(response, unsafe_allow_html=True)
        container = st.empty()
        container_a = st.empty()
        
    # Handle user input
    chat_input_container = st.container()
    with chat_input_container:
        if query := st.chat_input(t("Please input your question")):
            container.chat_message("user").markdown(query, unsafe_allow_html=True)
            response_with_extra_info, pure_response = asyncio.run(listen(query,container_a))
            
            # Update chat history
            st.session_state.simple_rag_messages.append({"role": "user", "content": query})
            st.session_state.simple_rag_messages.append({"role": "assistant", "content": pure_response})
            st.session_state.simple_rag_history.append((query, response_with_extra_info))
            st.rerun()

def display():
    display_configurations()
    if st.session_state.get("naive_flow_inst",""):
        chat_component()




