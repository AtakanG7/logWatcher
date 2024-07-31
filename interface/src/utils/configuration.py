"""
Configuration utilities for loading and saving configuration files.
"""

# Standard library imports
import os
from typing import Dict, Any

# Third party imports
import streamlit as st
import yaml

# Local imports
from utils.dockermanager import DockerManager

# Global constants
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Configuration file extensions and names
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

docker_manager = DockerManager()

def get_email_settings() -> Dict[str, Any]:
    """Get email settings from alertmanager configuration."""
    config_path = get_config_path('alertmanager')
    config = load_config(config_path)
    return config['receivers'][0]['email_configs'][0]

def update_email_settings(email_settings: Dict[str, Any]):
    """Update email settings in alertmanager configuration."""
    config_path = get_config_path('alertmanager')
    config = load_config(config_path)
    config['receivers'][0]['email_configs'][0].update(email_settings)
    save_yaml(config_path, yaml.dump(config), config_type='alertmanager')

def load_config(file_path: str) -> Dict[str, Any]:
    """Load YAML configuration from file."""
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def save_yaml(file_path: str, content: str, config_type: str) -> bool:
    """Save YAML configuration to file and restart container if successful."""
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

def get_config_path(config_type: str) -> str:
    """Get path to configuration file."""
    container_name = config_extensions[config_type]['name']
    isEnv = config_extensions[config_type]['isEnv']
    ext = config_extensions[config_type]['ext']
    return os.path.join(ROOT_DIR, "../../..", 'config', config_type.lower(), ((container_name + ".") if not isEnv else "") + ext)

def update_config(config_type: str, content: str, config_path: str):
    """Save YAML configuration to file and restart container if successful,
    and display success or failure message.
    """
    if (save_yaml(file_path=config_path, content=content, config_type=config_type.lower())):
        st.success("🎉 {} config updated successfully".format(config_type))
        st.info("Restarting {} service to apply changes!".format(config_type))
    else:
        st.error("Failed to update {} config".format(config_type))

