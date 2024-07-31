import streamlit as st
import yaml
import os
import configparser
import json
from streamlit_monaco import st_monaco
from utils.configuration import save_yaml, get_config_path, update_config
from utils.dockermanager import DockerManager

def load_css():
    css_file = os.path.join(os.path.dirname(__file__), "..", "public", "css", "style.css")
    with open(css_file, "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

docker_manager = DockerManager()

config_extensions = {
    'grafana': {'ext':'ini','name':'grafana', 'isEnv':False},
    'loki': {'ext':'yaml','name':'loki', 'isEnv':False},
    'promtail': {'ext':'yaml','name':'promtail', 'isEnv':False},
    'alertmanager': {'ext':'yaml','name':'alertmanager', 'isEnv':False},
    'prometheus': {'ext':'yaml','name':'prometheus', 'isEnv':False},
    'application': {'ext':'.env','name':'application', 'isEnv':True},
    'node-exporter': {'ext':'yaml','name':'node-exporter', 'isEnv':False},
    'cadvisor': {'ext':'json','name':'cadvisor', 'isEnv':False}
}

def load_config(config_path, config_type):
    if config_type not in config_extensions:
        raise ValueError(f"Unsupported config type: {config_type}")

    file_type = config_extensions[config_type]['ext']
    is_env = config_extensions[config_type]['isEnv']

    try:
        with open(config_path, 'r') as file:
            if is_env:
                config = dict(line.strip().split('=') for line in file if line.strip() and not line.startswith('#'))
            elif file_type == 'ini':
                parser = configparser.ConfigParser()
                parser.read_string(file.read())
                config = {section: dict(parser[section]) for section in parser.sections()}
            elif file_type == 'yaml':
                config = yaml.safe_load(file)
            elif file_type == 'json':
                config = json.load(file)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")

        return config

    except Exception as e:
        st.error(f"Error loading configuration: {str(e)}")
        return None

def show_configuration_page():
    st.title("Configuration Management")
    st.warning("Note: Updating configurations may require service restarts.")

    container_list = [x.get('name') for x in docker_manager.list_containers(all=True, networks=['monitoring'])]
    config_type = st.selectbox("Select Configuration", container_list)
    
    if config_type not in config_extensions:
        st.error(f"Unsupported configuration type: {config_type}")
        return

    config_path = get_config_path(config_type)

    try:
        config = load_config(config_path, config_type)
        if config is None:
            return

        yaml_rep = yaml.dump(config, default_flow_style=False)
        content = st_monaco(value=yaml_rep, height=400, language=config_extensions[config_type]['ext'])

        if st.button(f"Update {config_type} Config"):
            update_config(config_type, content, config_path)

    except Exception as e:
        st.error(f"Error processing configuration: {str(e)}")

if __name__ == "__main__":
    load_css()
    show_configuration_page()