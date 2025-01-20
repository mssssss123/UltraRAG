import streamlit as st
import os
from pathlib import Path
from ultrarag.webui.utils.language import t

home_path = Path().resolve()
output_path = home_path / "output"



# Update ratios when file list changes
def update_ratios():
    file_list = st.session_state.dc_config['merge'].get('file_list', [])
    st.session_state.dc_config['merge']['ratios'] = [1] * len(file_list)

# Update file list from text input
def update_file_list():
    file_list_input = st.session_state['dc_file_list_input']
    file_list = file_list_input.split("\n") if file_list_input else []
    merge_config = st.session_state.dc_config['merge']
    merge_config['file_list'] = list(set(merge_config.get('file_list', []) + file_list))
    update_ratios()

# Update file list from multiselect
def update_selected_files():
    selected_files = st.session_state['dc_selected_files']
    st.session_state.dc_config['merge']['file_list'] = selected_files
    update_ratios()

def display():
    # Initialize session state if not exists
    if 'dc_config' not in st.session_state:
        st.session_state.dc_config = {}
    if 'merge' not in st.session_state.dc_config:
        st.session_state.dc_config['merge'] = {}

    with st.expander(f"Merge {t('Configuration')}"):
        cols = st.columns([4, 4])

        # Validate output directory
        if not output_path.exists():
            st.error(f"Output folder '{output_path}' not found.")
            return
        
        # Get all available files from output directory
        all_files = [str(output_path / f) for f in os.listdir(output_path) 
                    if os.path.isfile(output_path / f)]

        # Initialize default values for merge configuration
        merge_config = st.session_state.dc_config['merge']
        merge_config.setdefault('file_list', [])
        merge_config.setdefault('ratios', [])
        merge_config.setdefault('fixed_steps', 4)
        merge_config.setdefault('output_file', 'output/output.jsonl')
        merge_config.setdefault('output_format', "jsonl")
        merge_config.setdefault('random_merge', True)

        # File selection section
        with cols[0]:
            current_file_list = merge_config.get('file_list', [])
            extended_options = list(set(all_files + current_file_list))
            st.multiselect(
                t("Select Files from Output Folder (Full Paths)"),
                options=extended_options,  
                default=current_file_list, 
                key="dc_selected_files",
                on_change=update_selected_files,
                help=t("Select files from the output folder or add your own full paths."),
            )

        # Manual file path input section
        st.text_area(
            t("Or Enter Full Paths (one per line)"),
            value="\n".join(current_file_list),
            key="dc_file_list_input",
            on_change=update_file_list,
            help=t("Enter additional full paths, one per line."),
        )

        # Output configuration section
        with cols[1]:
            st.text_input(
                t("Output File"),
                value=merge_config.get('output_file', 'output/output.jsonl'),
                key="dc_output_file",
                on_change=lambda: merge_config.update(
                    {'output_file': st.session_state.dc_output_file}
                ),
                help=t("Specify the name of the output file."),
            )

        # Merge parameters section
        cols = st.columns([4, 4])
        with cols[0]:
            st.text_input(
                t("Ratios (e.g., [1, 2, 3])"),
                value=str(merge_config.get('ratios', [])),
                key="dc_ratios_display",
                help=t("Specify the ratios for data splits, e.g., [1, 2, 3]."),
            )
        with cols[1]:
            st.number_input(
                t("Fixed Steps"),
                min_value=1,
                value=merge_config.get('fixed_steps', 4),
                step=1,
                key="dc_fixed_steps",
                on_change=lambda: merge_config.update(
                    {'fixed_steps': st.session_state.dc_fixed_steps}
                ),
                help=t("Specify the fixed step size for merging."),
            )

        # Additional options section
        cols = st.columns([4, 4])
        with cols[0]:
            st.checkbox(
                t("Random Merge"),
                value=merge_config.get('random_merge', True),
                key="dc_random_merge",
                on_change=lambda: merge_config.update(
                    {'random_merge': st.session_state.dc_random_merge}
                ),
                help=t("Enable or disable random merging."),
            )
        with cols[1]:
            st.selectbox(
                t("Output Format"),
                options=['json', 'jsonl'],
                index=['json', 'jsonl'].index(
                    merge_config.get('output_format', 'jsonl')
                ),
                key="dc_output_format",
                on_change=lambda: merge_config.update(
                    {'output_format': st.session_state.dc_output_format}
                ),
                help=t("Choose the output format."),
            )
