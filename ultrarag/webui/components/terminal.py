import streamlit as st
import subprocess
import re
from loguru import logger
from ultrarag.webui.utils.language import t

def extract_last_parenthesis_content(text):
    match = re.search(r'\(([^)]+)\)$', text)
    if match:
        return match.group(1)
    return text 

def check_llm_type(key, llm_type, metric_llm_type):
    if llm_type == "API" and key == "model_name_or_path":
        return True
    elif llm_type == "Local" and key in {"api_key", "base_url", "model_name"}:
        return True
    elif metric_llm_type == "API" and key == "metric_model_name_or_path":
        return True
    elif metric_llm_type == "Local" and key in {"metric_api_key", "metric_base_url", "metric_model_name"}:
        return True
    elif key == "llm_type" or key == "metric_llm_type":
        return True
    return False
    

def convert_parameters_to_args(params):
    args = []
    llm_type=""
    metric_llm_type=""
    if "llm_type" in params:
        llm_type = params["llm_type"]
    if "metric_llm_type" in params:
        metric_llm_type = params["metric_llm_type"]
    if "pipeline_step" in params:
        args.append(f"--pipeline_step {params['pipeline_step']}")
        params = params[f"{params['pipeline_step']}_config"]
    for key, value in params.items():
        if not value:
            continue
        if key == "command":
            continue
        if check_llm_type(key,llm_type,metric_llm_type):
            continue
        if key == "collections":
            value = [extract_last_parenthesis_content(v) for v in value]
            args.append(f"--knowledge_id {' '.join(map(str, value))}")
            args.append(f"--knowledge_stat_tab_path {st.session_state['kb_csv']}")
            continue
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
    st.title(t("Terminal"))
    if not full_command:
        command_parameter = convert_parameters_to_args(st.session_state.command_parameter)
        phase_parameter = ""
        command = f"python {st.session_state.file_path}"
        if st.session_state.active_tab == "Data Construction":
            params=st.session_state.dc_config[f'{st.session_state.command_parameter["pipeline_type"]}']
            phase_parameter = convert_parameters_to_args(params)
            phase_parameter += f' {convert_parameters_to_args(st.session_state.dc_config)}'
            if "pipeline_step" in params:
                command = params[f"{params['pipeline_step']}_config"].get("command",f"python {st.session_state.file_path}")
            else:
                command = params.get("command",f"python {st.session_state.file_path}")
        elif st.session_state.active_tab == "Evaluation":
            try:
                phase_parameter = convert_parameters_to_args(st.session_state.eval_config)
            except:
                phase_parameter = ""
        elif st.session_state.active_tab == "Train":
            phase_parameter = convert_parameters_to_args(st.session_state.train_config[f'{st.session_state.command_parameter["pipeline_type"]}'])
            command = st.session_state.train_config[f'{st.session_state.command_parameter["pipeline_type"]}'].get("command",f"python {st.session_state.file_path}")
            
        full_command = f"{command} {command_parameter} {phase_parameter}"
    else:
        full_command = f"{full_command} {convert_parameters_to_args(para_dict)}"
    col1, col2 = st.columns(2)
    if col1.button(t("Preview Command"), key=f"Preview Command {key}"):
        st.text_area(t("Command Preview"), full_command, height=100)

    if col2.button(t("Run Command"), key=f"Run Command {key}"):
        log_container = st.container(height=450)
        log_container.empty()
        try:
            with st.spinner(t("Running...")):
                process = subprocess.Popen(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                for line in process.stderr:
                    log_container.text(line.strip())
                for line in process.stdout:
                    log_container.text(line.strip())
                    
            process.wait()
            if process.returncode != 0:
                st.error(t("Command execution failed."))
        except Exception as e:
            st.error(f"Execution Error: {e}")
