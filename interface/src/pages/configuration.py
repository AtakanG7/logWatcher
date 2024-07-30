# pages/configuration.py

from streamlit_monaco import st_monaco
from utils.configuration import load_config, save_yaml, get_config_path, update_config
from utils.dockermanager import DockerManager
import streamlit as st
import yaml
import os 
def load_css():
    css_file = os.path.join(os.path.dirname(__file__), "..", "public", "css", "style.css")
    with open(css_file, "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

docker_manager = DockerManager()

config_extensions = {
    'grafana': 'ini',
    'loki': 'yaml',
    'promtail': 'yaml',
    'alertmanager': 'yaml',
    'prometheus': 'yaml',
    'application': 'env',
    'node-exporter': 'yaml',
    'cadvisor': 'json'
}

def show_configuration_page():
    st.title("Configuration Management")
    st.warning("Note: Updating configurations may require service restarts.")
    config_type = st.selectbox("Select Configuration", [x.get('name') for x in docker_manager.list_containers(all=True, networks=['monitoring'])])
    config_path = get_config_path(config_type)

    try:
        config = load_config(config_path)
        yaml_rep = yaml.dump(config, default_flow_style=False)
    except Exception as e:
        st.error(f"Error loading configuration: {str(e)}")
        return

    content = st_monaco(value=yaml_rep, height=400, language=config_extensions[config_type])

    if st.button(f"Update {config_type} Config"):
        update_config(config_type, content, config_path)


if __name__ == "__main__":
    load_css()
    show_configuration_page()