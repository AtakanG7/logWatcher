import streamlit as st
import time
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from utils.monitoring import PrometheusMonitor, get_container_metrics
from utils.dockermanager import DockerManager
import os

def load_css():
    css_file = os.path.join(os.path.dirname(__file__), "..", "public", "css", "style.css")
    with open(css_file, "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def initialize_app():
    st.title("📊 Container Monitoring Dashboard")
    
    if 'history' not in st.session_state:
        st.session_state.history = {
            'cpu_usage': [], 'memory_usage': [], 'disk_usage': [], 'network_receive': [],
            'network_transmit': [], 'io_read': [], 'io_write': [], 'processes': []
        }

def create_gauge(value, title, max_value=100):
    return go.Indicator(
        value=value,
        title={'text': title, 'font': {'size': 24}},
        delta={'reference': max_value/2},
        gauge={
            'axis': {'range': [None, max_value], 'tickwidth': 1},
            'bar': {'color': "darkgreen"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, max_value/3], 'color': 'lightgreen'},
                {'range': [max_value/3, 2*max_value/3], 'color': 'gold'},
                {'range': [2*max_value/3, max_value], 'color': 'darkgreen'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    )

def create_time_series(data, title):
    return go.Scatter(y=data, mode='lines+markers', name=title, line={'width': 2}, marker={'size': 4})

def update_history(metrics):
    for key in ['cpu_usage', 'memory_usage', 'disk_usage', 'processes']:
        value = metrics[key]['percentage'] if isinstance(metrics[key], dict) else metrics[key]
        st.session_state.history[key].append(value)
    
    st.session_state.history['network_receive'].append(metrics['network_traffic']['receive'])
    st.session_state.history['network_transmit'].append(metrics['network_traffic']['transmit'])
    st.session_state.history['io_read'].append(metrics['io_usage']['read'])
    st.session_state.history['io_write'].append(metrics['io_usage']['write'])

    for key in st.session_state.history:
        st.session_state.history[key] = st.session_state.history[key][-60:]

def create_dashboard(metrics):
    fig = make_subplots(
        rows=3, cols=3,
        specs=[
            [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
            [{"type": "scatter", "colspan": 3}, None, None],
            [{"type": "scatter", "colspan": 3}, None, None],
        ],
        subplot_titles=("CPU Usage", "Memory Usage", "Disk Usage", 
                        "Resource Usage Over Time", "Network and I/O Usage"),
    )

    fig.add_trace(create_gauge(metrics['cpu_usage'], "CPU Usage (%)"), row=1, col=1)
    fig.add_trace(create_gauge(metrics['memory_usage']['percentage'], "Memory Usage (%)"), row=1, col=2)
    fig.add_trace(create_gauge(metrics['disk_usage'], "Disk Usage (MB)"), row=1, col=3)

    for i, key in enumerate(['cpu_usage', 'memory_usage', 'disk_usage']):
        fig.add_trace(create_time_series(st.session_state.history[key], f"{key.split('_')[0].capitalize()} Usage"), row=2, col=1)

    for key in ['network_receive', 'network_transmit', 'io_read', 'io_write']:
        fig.add_trace(create_time_series(st.session_state.history[key], f"{key.replace('_', ' ').title()} ({'KB/s' if 'network' in key else 'MB/s'})"), row=3, col=1)

    fig.update_layout(height=1000, grid={'rows': 3, 'columns': 3, 'pattern': "independent"}, template="plotly_dark")
    
    return fig

def display_additional_metrics(metrics):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Processes", metrics['processes'])
    with col2:
        st.metric("Memory Usage", f"{metrics['memory_usage']['percentage']} MB")
    with col3:
        st.metric("CPU Throttling", f"{metrics['cpu_throttling']['throttling_ratio']}%")

def main():
    initialize_app()
    docker_manager = DockerManager()
    monitor = PrometheusMonitor()

    containers = docker_manager.list_containers()
    container_names = [c['name'] for c in containers]
    selected_container = st.selectbox("Select a container to monitor:", container_names, index=0)

    metrics_placeholder = st.empty()

    while True:
        metrics = get_container_metrics(selected_container)
        update_history(metrics)

        with metrics_placeholder.container():
            fig = create_dashboard(metrics)
            st.plotly_chart(fig, use_container_width=True)
            display_additional_metrics(metrics)

        time.sleep(1)

if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="Container Monitoring Dashboard", page_icon="📊")
    load_css()
    main()