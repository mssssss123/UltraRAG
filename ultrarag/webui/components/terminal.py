import streamlit as st
import subprocess
import re
from loguru import logger
from ultrarag.webui.utils.language import t

def extract_last_parenthesis_content(text):
    """
    Extract content from the last set of parentheses in a text string.
    
    Args:
        text: String to extract content from
        
    Returns:
        str: Content within last parentheses, or original text if no parentheses found
    """
    match = re.search(r'\(([^)]+)\)$', text)
    if match:
        return match.group(1)
    return text 

def check_llm_type(key, llm_type, metric_llm_type):
    """
    Check if a parameter key should be included based on LLM types.
    
    Args:
        key: Parameter key to check
        llm_type: Type of main LLM ('API' or 'Local')
        metric_llm_type: Type of metric LLM ('API' or 'Local')
        
    Returns:
        bool: True if key should be excluded based on LLM types
    """
    # Skip model path for API type
    if llm_type == "API" and key == "model_name_or_path":
        return True
    # Skip API parameters for Local type
    elif llm_type == "Local" and key in {"api_key", "base_url", "model_name"}:
        return True
    # Skip metric model path for API type
    elif metric_llm_type == "API" and key == "metric_model_name_or_path":
        return True
    # Skip metric API parameters for Local type
    elif metric_llm_type == "Local" and key in {"metric_api_key", "metric_base_url", "metric_model_name"}:
        return True
    # Skip LLM type parameters
    elif key == "llm_type" or key == "metric_llm_type":
        return True
    return False
    

def convert_parameters_to_args(params):
    """
    Convert a parameter dictionary to command line arguments string.
    
    Args:
        params: Dictionary of parameters to convert
        
    Returns:
        str: Formatted command line arguments string
    """
    args = []
    llm_type = ""
    metric_llm_type = ""
    
    # Get LLM types if specified
    if "llm_type" in params:
        llm_type = params["llm_type"]
    if "metric_llm_type" in params:
        metric_llm_type = params["metric_llm_type"]
        
    # Handle pipeline step configuration
    if "pipeline_step" in params:
        args.append(f"--pipeline_step {params['pipeline_step']}")
        params = params[f"{params['pipeline_step']}_config"]
        
    # Convert parameters to command line arguments
    for key, value in params.items():
        # Skip empty values and special keys
        if not value:
            continue
        if key == "command":
            continue
        if check_llm_type(key, llm_type, metric_llm_type):
            continue
            
        # Handle collections parameter specially
        if key == "collections":
            value = [extract_last_parenthesis_content(v) for v in value]
            args.append(f"--knowledge_id {' '.join(map(str, value))}")
            args.append(f"--knowledge_stat_tab_path {st.session_state['kb_csv']}")
            continue
            
        # Format different parameter types
        if isinstance(value, bool):
            if value:
                args.append(f"--{key}")
        elif isinstance(value, (list, tuple)):
            args.append(f"--{key} {' '.join(map(str, value))}")
        elif isinstance(value, dict):
            continue
        else:
            args.append(f"--{key} {value}")
            
    return " ".join(args)

def terminal(full_command="", para_dict="", key=None):
    """
    Display terminal interface for command execution.
    
    Args:
        full_command: Optional pre-defined command string
        para_dict: Optional parameter dictionary
        key: Optional unique key for components
    """
    st.title(t("Terminal"))
    
    # Build command if not provided
    if not full_command:
        # Get base command parameters
        command_parameter = convert_parameters_to_args(st.session_state.command_parameter)
        phase_parameter = ""
        command = f"python {st.session_state.file_path}"
        
        # Add phase-specific parameters based on active tab
        if st.session_state.active_tab == "Data Construction":
            params = st.session_state.dc_config[f'{st.session_state.command_parameter["pipeline_type"]}']
            phase_parameter = convert_parameters_to_args(params)
            phase_parameter += f' {convert_parameters_to_args(st.session_state.dc_config)}'
            if "pipeline_step" in params:
                command = params[f"{params['pipeline_step']}_config"].get("command",f"python {st.session_state.file_path}")
            else:
                command = params.get("command", f"python {st.session_state.file_path}")
        elif st.session_state.active_tab == "Evaluation":
            try:
                phase_parameter = convert_parameters_to_args(st.session_state.eval_config)
            except:
                phase_parameter = ""
        elif st.session_state.active_tab == "Train":
            phase_parameter = convert_parameters_to_args(st.session_state.train_config[f'{st.session_state.command_parameter["pipeline_type"]}'])
            command = st.session_state.train_config[f'{st.session_state.command_parameter["pipeline_type"]}'].get("command", f"python {st.session_state.file_path}")
            
        full_command = f"{command} {command_parameter} {phase_parameter}"
    else:
        full_command = f"{full_command} {convert_parameters_to_args(para_dict)}"
        
    # Display command preview and execution buttons
    col1, col2 = st.columns(2)
    if col1.button(t("Preview Command"), key=f"Preview Command {key}"):
        st.text_area(t("Command Preview"), full_command, height=100)

    if col2.button(t("Run Command"), key=f"Run Command {key}"):
        log_container = st.container(height=450)
        log_container.empty()
        try:
            with st.spinner(t("Running...")):
                process = subprocess.Popen(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                # Display stderr and stdout in real-time
                for line in process.stderr:
                    log_container.text(line.strip())
                for line in process.stdout:
                    log_container.text(line.strip())
                    
            process.wait()
            if process.returncode != 0:
                st.error(t("Command execution failed."))
        except Exception as e:
            st.error(f"Execution Error: {e}")
