import streamlit as st
import pandas as pd
import os
import json
import uuid
from ultrarag.modules.embedding import BaseEmbedding
from ultrarag.modules.knowledge_managment import Knowledge_Managment
import asyncio
from st_aggrid import AgGrid, GridOptionsBuilder
from pathlib import Path
import hashlib
from ultrarag.webui.components.loading import loading
import time
import shutil
import traceback
from loguru import logger
from ultrarag.webui.utils.language import t

def change_config(kb_config_id=None):
    selected_config = st.session_state.get('kb_df', pd.DataFrame())
    
    if not kb_config_id:
        kb_config_id = generate_kb_config_id(
            st.session_state['embedding_model_name']
        )
    
    if not selected_config.empty:
        for _, config in selected_config.iterrows():
            if kb_config_id == config['kb_config_id']:
                st.session_state['temp_selected_kb_config_id'] = kb_config_id
                st.session_state['temp_embedding_model_name'] = config['embedding_model_name']
                st.session_state['temp_chunk_size'] = config['chunk_size']
                st.session_state['temp_overlap'] = config['overlap']
                st.session_state['temp_others'] = config['others']
                return

    st.session_state['temp_selected_kb_config_id'] = "custom"

    
    
def generate_file_id(file_name):
    """Generate a unique file_id based on the file name."""
    return hashlib.md5(file_name.encode()).hexdigest()

def generate_kb_config_id(embedding_model_name):
    """Generate a unique kb_config_id based on the configuration."""
    config_str = f"{embedding_model_name}"
    return hashlib.md5(config_str.encode()).hexdigest()

def generate_knowledge_base_id(kb_name, kb_config_id, file_list, chunk_size, overlap, others):
    """Generate a unique knowledge_base_id based on kb_name and kb_config_id."""
    combined_str = f"{kb_name}-{kb_config_id}-{file_list}-{chunk_size}-{overlap}-{others}"
    return hashlib.md5(combined_str.encode()).hexdigest()

columns_to_extract = ["embedding_model_name", "chunk_size", "overlap", "others"]

default_files_csv = "resource/kb_manager/manage_table/file_manager.csv"
default_kb_csv = "resource/kb_manager/manage_table/knowledge_base_manager.csv"
default_files_dir = "resource/kb_manager/files"
default_kb_dir = "resource/kb_manager/kb"

def load_csv(path):
    try:
        if os.path.exists(path):
            return pd.read_csv(path)
    except:
        return pd.DataFrame()
    return pd.DataFrame()

def save_csv(df, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)

@st.fragment
def kb_manage():
    cols=st.columns([1,1])
    try:
        if 'files_df' not in st.session_state:
            st.session_state['files_df'] = load_csv(st.session_state['files_csv'])
        if 'kb_df' not in st.session_state:
            st.session_state['kb_df'] = load_csv(st.session_state['kb_csv'])
    except:
        if 'files_df' not in st.session_state:
            st.session_state['files_df'] = load_csv(default_files_csv)
        if 'kb_df' not in st.session_state:
            st.session_state['kb_df'] = load_csv(default_kb_csv)
    
    if "uploader_file_key" not in st.session_state:
        st.session_state["uploader_file_key"] = 1
        
    files_df = st.session_state['files_df']
    kb_df = st.session_state['kb_df']

    # 左侧：File Management
    with cols[0]:
        st.subheader(t("File Management"))
        
        file_cols=st.columns([1, 1],vertical_alignment='bottom')
        with file_cols[0]:
            st.session_state['files_csv'] = st.text_input(t("File Management CSV Path"), value=default_files_csv)
        with file_cols[1]:
            st.session_state['file_save_dir'] = st.text_input(t("File Save Path"), value=default_files_dir)
        file_cols2=st.columns([1],vertical_alignment='bottom')
        with file_cols2[0]:
            st.markdown(
                """
                <style>
                .hidden-input {
                    visibility: hidden;
                    height: 5.25rem;
                }
                </style>
                <input type="text" class="hidden-input"/>
                """,
                unsafe_allow_html=True,
            )
            uploaded_files = st.file_uploader(t("Upload Files"), accept_multiple_files=True, key=st.session_state["uploader_file_key"])
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(st.session_state['file_save_dir'], uploaded_file.name)
                    file_id = generate_file_id(file_path)
                    os.makedirs(st.session_state['file_save_dir'], exist_ok=True)
                    if not files_df.empty and not files_df[files_df["id"] == file_id].empty:
                        logger.warning(t("File Existed, Ignored").format(file_name=uploaded_file.name))
                        continue
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    files_df = pd.concat([files_df, pd.DataFrame([{ "id": file_id, "file_path": file_path }])])
                st.session_state['files_df'] = files_df
                save_csv(files_df, st.session_state['files_csv'])
                st.session_state["uploader_file_key"]+=1
                st.success(t("Uploaded Successfully"))
                st.rerun()

        
   
    cols2=st.columns([1,1],vertical_alignment='bottom')
    with cols2[0]:
        st.subheader(t("File Lists"))
        selected_files=""
        if not files_df.empty:
            gb = GridOptionsBuilder.from_dataframe(files_df)
            gb.configure_selection(selection_mode="multiple", use_checkbox=True, header_checkbox=True)
            grid_options = gb.build()
            grid_response = AgGrid(files_df, gridOptions=grid_options, fit_columns_on_grid_load=True, height=200)
            selected_files = grid_response['selected_rows']
            if st.button(t("Remove Selected Files")):
                for row in grid_response['selected_rows']['file_path']:                    
                    file_path = row
                    if os.path.exists(file_path):
                        os.remove(file_path)
                files_df = files_df[~files_df['file_path'].isin([row for row in selected_files['file_path']])]
                st.session_state['files_df'] = files_df
                save_csv(files_df, st.session_state['files_csv'])
                st.success(t("File Deleted Successfully"))
                st.rerun()
        else:
            st.info(t("No File Found"))

    # 右侧：Collection Management
    with cols[1]:
        st.subheader(t("Collection Management"))
        
        kb_cols=st.columns([1, 1],vertical_alignment='bottom')
        with kb_cols[0]:
            st.session_state['kb_csv'] = st.text_input(t("Collection Management CSV Path"), value=default_kb_csv)
        with kb_cols[1]:
            st.session_state['kb_save_dir'] = st.text_input(t("Collection Save Path"), value=default_kb_dir)
        with st.container():
            cols1_1=st.columns([1, 1, 1])
            with cols1_1[0]:
                kb_name = st.text_input(t("Collection Name"))
                others = st.text_area(
                    t("Others (JSON Format)"),
                    value=st.session_state.get('temp_others', '{}'),
                    key="others",
                    on_change=change_config
                )
            with cols1_1[1]:
                chunk_size = st.number_input(
                    t("Chunk Size"),
                    min_value=1,
                    value=st.session_state.get('temp_chunk_size', 512),
                    key="chunk_size",
                    on_change=change_config
                )
                overlap = st.number_input(
                    t("Overlap"),
                    min_value=0,
                    max_value=100,
                    value=st.session_state.get('temp_overlap', 10),
                    key="overlap",
                    on_change=change_config
                )
            with cols1_1[2]:
                embedding_model_name = st.text_input(
                    t("Embedding Name"),
                    value=st.session_state.get('temp_embedding_model_name', ''),
                    key="embedding_model_name",
                    on_change=change_config
                )
                if not st.session_state.get("embedding"):
                    st.warning(t("Please load the embedding model."))
                else:
                    embedding_model_path = st.session_state.config['embedding_model_path']
                    st.text(embedding_model_path)
            kb_btn_disabled = False if (
                isinstance(selected_files, pd.DataFrame) 
                and not selected_files.empty 
                and selected_files['file_path'].any()
                and kb_name 
                and chunk_size is not None  
                and st.session_state.get("embedding") 
                and overlap is not None 
                and embedding_model_name
            ) else True
            cols1_2=st.columns([1, 1, 1],vertical_alignment='bottom')
            # with cols1_2[0]:
            #     kb_config_ids = ["custom"]
            #     if not kb_df.empty:
            #         kb_config_ids.extend(kb_df['kb_config_id'].unique())
            #     temp_id = st.session_state.get('temp_selected_kb_config_id', "custom")
            #     index = kb_config_ids.index(temp_id) if temp_id in kb_config_ids else 0
            #     selected_kb_config_id = st.selectbox(
            #         "选择配置 ID",
            #         kb_config_ids,
            #         index=index,
            #         key="selected_kb_config_id",
            #         on_change=lambda: change_config(st.session_state["selected_kb_config_id"])
            #     )
            # with cols1_2[1]:
            #     st.text("当前配置详情：")
            #     st.json({
            #         "embedding_model_name": st.session_state['embedding_model_name'],
            #         "chunk_size": st.session_state['chunk_size'],
            #         "overlap": st.session_state['overlap'],
            #         "others": st.session_state['others']
            #     },expanded=False)
            with cols1_2[2]:
                submit_kb = st.button(t("Save & Build"), disabled=kb_btn_disabled)
                if submit_kb:
                    st.session_state["loading"] = True
                    loading(t("Loading"))
                    try:
                        kb_config_id = generate_kb_config_id(embedding_model_name)
                        file_list = [fp for fp in selected_files['file_path']]
                        kb_id = generate_knowledge_base_id(kb_name, kb_config_id, file_list, chunk_size, overlap, others)
                        kb_path = f"{st.session_state['kb_save_dir']}/{kb_id}.jsonl"
                        qdrant_dir = f"{st.session_state['kb_save_dir']}_qdrant"
                        # todo
                        if not kb_df.empty and not kb_df[kb_df["knowledge_base_id"] == kb_id].empty:
                            logger.warning(t("Collection Params Existed, Ignored").format(kb_id=kb_id))
                            st.session_state["loading"] = False
                            st.rerun()
                        os.makedirs(st.session_state['kb_save_dir'], exist_ok=True)
                        os.makedirs(qdrant_dir, exist_ok=True)
                        others_json = json.loads(others)
                        kb_df = asyncio.run(Knowledge_Managment.index(kb_config_id,kb_name,embedding_model_name,embedding_model_path,qdrant_dir,kb_path,kb_id,file_list,st.session_state.get("embedding"),chunk_size,overlap,json.dumps(others_json),kb_df))
                        st.session_state['kb_df'] = kb_df
                        save_csv(kb_df, st.session_state['kb_csv'])
                        st.session_state['temp_selected_kb_config_id'] = kb_config_id
                        st.success(t("Collection Params Saved Successfully！"))
                        st.rerun()
                    except json.JSONDecodeError:
                        logger.error(traceback.format_exc())
                        st.error(t("Others Params Must Be Json Format"))
                        loading(t("Error"))
                        time.sleep(2)
                        st.session_state["loading"] = False
                        st.rerun()
                    except Exception as e:
                        logger.error(traceback.format_exc())
                        loading(t("Error"))
                        logger.error(traceback.format_exc())
                        time.sleep(2)
                        st.session_state["loading"] = False
                        st.rerun()

    with cols2[1]:
        st.subheader(t("Collection Lists"))
        if not kb_df.empty:
            kb_gb = GridOptionsBuilder.from_dataframe(kb_df)
            kb_gb.configure_default_column(resizable=True)
            kb_gb.configure_selection(selection_mode="multiple", use_checkbox=True, header_checkbox=True)
            kb_grid_options = kb_gb.build()
            kb_grid_response = AgGrid(kb_df, gridOptions=kb_grid_options, fit_columns_on_grid_load=False, height=200)
            selected_kb = kb_grid_response['selected_rows']
            if st.button(t("Delete Selected Collections")):
                for i,row in enumerate(selected_kb['qdrant_path']):
                    kb_path = row
                    kb_base = kb_path.replace("_qdrant", "")
                    collection_path = os.path.join(kb_path, "collection", selected_kb["knowledge_base_id"].values[i])
                    if os.path.exists(collection_path):
                        shutil.rmtree(collection_path)
                    meta_path = os.path.join(kb_path, 'meta.json')
                    with open(meta_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    if selected_kb["knowledge_base_id"].values[i] in data.get("collections", {}):
                        del data["collections"][selected_kb["knowledge_base_id"].values[i]]
                    with open(meta_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
                    json_file_path = os.path.join(kb_base, f"{selected_kb['knowledge_base_id'].values[i]}.json")
                    if os.path.exists(json_file_path):
                        os.remove(json_file_path)
                kb_df = kb_df[~kb_df['qdrant_path'].isin([row for row in selected_kb['qdrant_path']])]
                st.session_state['kb_df'] = kb_df
                save_csv(kb_df, st.session_state['kb_csv'])
                st.success(t("Collection Deleted Successfully"))
                st.rerun()
        else:
            st.info(t("No Collection Available"))


