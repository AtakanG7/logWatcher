# utils/configuration.py

from utils.dockermanager import DockerManager
from typing import Dict, Any
import streamlit as st
import yaml
import os

docker_manager = DockerManager()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

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

def load_config(file_path: str) -> Dict[str, Any]:
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def save_yaml(file_path, content, config_type=None):
    try:
        with open(file_path, 'w') as file:
            yaml.dump(yaml.safe_load(content), file, default_flow_style=False)

        docker_manager.restart_container_by_name(config_type)
        return True
    except (yaml.YAMLError, FileNotFoundError) as e:
        st.error(f"Error saving YAML file: {e}")
        return False
    except PermissionError as e:
        st.error(f"Permission denied when saving YAML file: {e}")
        return False

def get_config_path(config_type):
    return os.path.join(ROOT_DIR, "../../..", 'config', config_type.lower(), f"{config_type.lower()}.{config_extensions[config_type]}")

def update_config(config_type, content, config_path):
    if (save_yaml(file_path=config_path, content=content, config_type=config_type.lower())):
        st.success("🎉 {} config updated successfully".format(config_type))
        st.info("🔧 Restarting {} service to apply changes!".format(config_type))
    else:
        st.error("🚨 Failed to update {} config".format(config_type))
