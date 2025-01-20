import streamlit as st
import json
from ultrarag.webui.utils.language import t

def parse_json_files(file_paths):
    """
    Parse multiple JSON and JSONL files into a dictionary.
    
    Args:
        file_paths: List of paths to JSON/JSONL files
        
    Returns:
        dict: Dictionary with file paths as keys and parsed content as values
    """
    parsed_data = {}
    for file in file_paths:
        try:
            with open(file, 'r') as f:
                # Handle JSONL files line by line
                if file.endswith('.jsonl'):
                    parsed_data[file] = [json.loads(line) for line in f]
                # Handle regular JSON files
                else:
                    parsed_data[file] = json.load(f)
        except Exception as e:
            # Store error message if parsing fails
            parsed_data[file] = str(e)
    return parsed_data

@st.dialog("preview_dataset")
def preview_dataset(file, content):
    """
    Open a dialog to display paginated content from JSON/JSONL files.
    
    Args:
        file: Path to the file being previewed
        content: Parsed content from the file
    """
    # Initialize pagination state if not exists
    if f"page_{file}" not in st.session_state:
        st.session_state[f"page_{file}"] = 1
    if f"items_per_page" not in st.session_state:
        st.session_state[f"items_per_page"] = 2

    # Calculate pagination parameters
    items_per_page = st.session_state[f"items_per_page"]
    total_pages = (len(content) + items_per_page - 1) // items_per_page
    page = st.session_state[f"page_{file}"]

    # Calculate current page indices
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, len(content))

    # Display header with file and page information
    st.subheader(t("Preview of File").format(file=file, page=page, total_pages=total_pages))
    
    # Items per page control
    new_items_per_page = st.number_input(
        t("Items per page"),
        min_value=1,
        max_value=10,
        value=items_per_page,
        key=f"new_items_per_page",
        help=t("Set the number of items displayed per page.")
    )
    
    # Update items per page if changed
    if new_items_per_page != items_per_page:
        st.session_state[f"items_per_page"] = new_items_per_page
        st.rerun(scope="fragment")
        
    # Display content items
    for i in range(start_idx, end_idx):
        st.json(content[i], expanded=False)

    col1, col2, col3 = st.columns([1, 2, 1],vertical_alignment='bottom')
    with col1:
        if st.button(t("Previous"), key=f"prev_{file}"):
            if page > 1:
                st.session_state[f"page_{file}"] -= 1
                st.rerun(scope="fragment")
    with col3:
        if st.button(t("Next"), key=f"next_{file}"):
            if page < total_pages:
                st.session_state[f"page_{file}"] += 1
                st.rerun(scope="fragment")
    with col2:
        jump_to_page = st.number_input(
            t("Jump to page"),
            min_value=1,
            max_value=total_pages,
            value=page,
            key=f"jump_{file}",
            help=t("Enter the page number to jump to.")
        )
        if jump_to_page != page:
            st.session_state[f"page_{file}"] = jump_to_page
            st.rerun(scope="fragment")