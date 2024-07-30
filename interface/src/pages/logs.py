import streamlit as st
from utils.dockermanager import DockerManager
import asyncio
from streamlit.runtime.scriptrunner import add_script_run_ctx
from datetime import datetime, timedelta
import os 
docker_manager = DockerManager()

def load_css():
    css_file = os.path.join(os.path.dirname(__file__), "..", "public", "css", "style.css")
    with open(css_file, "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

async def update_logs(logs_container, stop_event, log_time_option, config_type='application'):
    all_logs = []
    last_log_time = None
    logs_found = False

    while not stop_event.is_set():
        minutes_back = int(log_time_option.split('/')[0]) if log_time_option.split('/')[0] != 'all' else None
        end_time = datetime.now()
        
        if last_log_time:
            start_time = last_log_time
        elif minutes_back:
            start_time = end_time - timedelta(seconds=minutes_back)
        else:
            start_time = None
        
        app_logs = docker_manager.get_container_logs(config_type, since=start_time, until=end_time)
        
        new_logs = [log.strip() for log in app_logs.decode('utf-8').split('\n') if log.strip()]

        if new_logs:
            logs_found = True
            all_logs.extend(new_logs)
            last_log_time = end_time
            
            formatted_logs = "\n".join(reversed(all_logs))
            logs_container.empty()  
            logs_container.code(formatted_logs)
        
        if not logs_found:
            logs_container.empty()  
            logs_container.info('No logs found in the last ' + log_time_option.split('/')[1])

        await asyncio.sleep(0.1 if new_logs else 1)

def show_logs_page():
    with st.sidebar:
        config_type = st.selectbox("Select Container", [x.get('name') for x in docker_manager.list_containers(all=True, networks=['monitoring'])])
        log_time_option = st.selectbox("Select Timing", ['60/1min', '300/5min', '1800/30min', '3600/1hour', 'all'])
    
    st.title("Application Logs - " + config_type)
    
    logs_container = st.empty()

    stop_event = asyncio.Event()

    async def start_log_update():
        add_script_run_ctx(asyncio.current_task())
        await update_logs(logs_container, stop_event, log_time_option, config_type)

    try:
        asyncio.run(start_log_update())
    except st.runtime.scriptrunner.StopException:
        stop_event.set()
        st.write("Stopped fetching logs.")

if __name__ == "__main__":
    st.set_page_config(page_title="LogWatcher Application Logs", layout="wide")
    load_css()
    show_logs_page()