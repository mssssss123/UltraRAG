import os
import time
import asyncio
import pandas as pd
import streamlit as st
from pathlib import Path
import traceback
from loguru import logger
from flask import Flask, send_file, abort
import threading    

from ultrarag.common.utils import get_debug_fold, get_image_fold
from ultrarag.modules.database import QdrantIndex
from ultrarag.workflow.ultraragflow import VisRagFLow
from ultrarag.modules.embedding import VisNetClient, VisRAGNetServer
from ultrarag.modules.llm import HuggingfaceClient, HuggingFaceServer
from ultrarag.modules.knowledge_managment import Knowledge_Managment
from ultrarag.webui.components.collection_selectbox import close_existing_searcher
from ultrarag.webui.utils.language import t




def create_image_server(port=5000):
    """
    Create and start a Flask server for serving images.
    
    Args:
        port: Port number for the server (default: 5000)
    
    Returns:
        str: Success message with server port information
    """
    app = Flask(__name__)
    
    @app.route('/images/<path:filepath>')
    def serve_image(filepath):
        """
        Serve images from any path.
        Example: http://localhost:5000/images/path/to/your/image.jpg
        
        Args:
            filepath: Path to the requested image
        """
        filepath = f"/{filepath}"
        logger.debug(f"filepath: {filepath}")

        image_path = Path(filepath)
        if not image_path.is_file():
            return abort(404, "File not found")
            
        # Check if file is an allowed image type
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        if image_path.suffix.lower() not in allowed_extensions:
            return abort(400, "Unsupported file type")
            
        return send_file(filepath)

    def run_server():
        """Start the Flask server in production mode"""
        app.run(host='0.0.0.0', port=port, debug=False)
    
    # Start server in a background thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    return f"Image server started in background on port: {port}"

if "imageStorage" not in st.session_state:
    st.session_state.imageStorage = True
    create_image_server()

def display_configurations():
    """
    Display VisRAG configurations in a Streamlit expander.
    Initializes necessary session states and handles model/collection setup.
    """
    # Initialize session states if not exists
    if "visrag_inst" not in st.session_state:
        st.session_state.visrag_inst = ""
    if "collection" not in st.session_state:
        st.session_state.collection = []
    if "visrag_history" not in st.session_state:
        st.session_state.visrag_history = []
        st.session_state.visrag_messages = []

    # Display configuration expander
    with st.expander("VisRAG"):
        if 'selected_options' not in st.session_state:
            st.session_state['selected_options'] = []
        if 'current_kb_config_id' not in st.session_state:
            st.session_state['current_kb_config_id'] = None
            
        # Initialize VisRAG if knowledge base is loaded
        kb_df = st.session_state.get('kb_df')
        if (isinstance(kb_df, pd.DataFrame)) and not kb_df.empty:
            try:
                st.session_state.visrag_inst = VisRagFLow.from_modules(
                    llm_model=st.session_state.llm,
                    database=st.session_state.searcher,
                )
                if st.button(t("clear history"), type="primary"):
                    st.session_state.visrag_history = []
                    st.session_state.visrag_messages = []
            except Exception as e:
                logger.error(traceback.format_exc())
                st.warning(t("Please load the model and select the collections"))
        else:
            try:
                st.session_state['selected_options'] = []
                st.session_state['current_kb_config_id'] = None
                st.session_state.visrag_inst = ""
            except:
                pass
            close_existing_searcher()

home_path = Path().resolve()
output_path = home_path / "output"

if 'chat_config' not in st.session_state:
    st.session_state.dc_config = {}


async def listen(query,container):
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

    # Get response from VisRAG instance
    rag_link = st.session_state.visrag_inst
    response = rag_link.aquery(
        query=query, 
        messages=st.session_state.visrag_messages, 
        collection=st.session_state.selected_collection
    )

    # Process streaming response
    async for chunk in response:
        if isinstance(chunk, dict) and chunk["state"] == "recall": 
            context = [f"http://localhost:5000/images/{home_path.as_posix()}/{url}" for url in chunk['value']]
            process_info = get_image_fold(title="recall", context=context)
        if isinstance(chunk, dict) and chunk['state'] == "answer":
            if first_response == 0: first_response = time.perf_counter() - time_start
            buff += chunk['value']
        container.chat_message("assistant").markdown(process_info + buff, unsafe_allow_html=True)
    extra_infos = f"\n\n\ntotal spend: {time.perf_counter() - time_start :.2f} s, first reponse {first_response:.2f} s"
    container.chat_message("assistant").markdown(process_info + buff + extra_infos, unsafe_allow_html=True)
    return process_info + buff + extra_infos, buff

@st.fragment
def chat_component():
    """
    Display the chat interface component.
    Handles message history, user input, and response display.
    """
    st.subheader(f"{t('Welcome to ')}VisRAG")

    # Setup chat container
    his_container = st.container(height=500)
    
    with his_container:
        # Display chat history
        for (query, response) in st.session_state.visrag_history:
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
            st.session_state.visrag_messages.append({"role": "user", "content": query})
            st.session_state.visrag_messages.append({"role": "assistant", "content": pure_response})
            st.session_state.visrag_history.append((query, response_with_extra_info))
            st.rerun()

def display():
    display_configurations()
    if st.session_state.get("visrag_inst",""):
        chat_component()
