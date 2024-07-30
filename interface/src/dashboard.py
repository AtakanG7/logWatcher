import streamlit as st
from utils.dockermanager import DockerManager
from utils.monitoring import get_container_metrics
import time
import os

docker_manager = DockerManager()

def load_css():
    css_file = os.path.join(os.path.dirname(__file__), "public", "css", "style.css")
    with open(css_file, "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def main():
    st.title("LogWatcher Dashboard")

    configuration = st.selectbox("Select Configuration", [x['name'] for x in docker_manager.list_containers(all=True, networks=['monitoring'])])
    
    dashboard_page = st.empty()

    while True:
        metrics = get_container_metrics(configuration)
        containers = docker_manager.list_containers(all=True, networks=['monitoring'])
        with dashboard_page.container():
            col1, col2 = st.columns([2, 1])

            with col1:
                st.subheader("Metrics")
                metrics_grid = [
                    ("CPU Usage", f"{metrics['cpu_usage']}%", "💻"),
                    ("Memory Usage", f"{metrics['memory_usage']['percentage']}%", "🧠"),
                    ("Memory Used", f"{metrics['memory_usage']['usage_mb']} MB", "📊"),
                    ("Memory Limit", f"{metrics['memory_usage']['limit_mb']} MB", "🚫"),
                    ("Disk Usage", f"{metrics['disk_usage']} MB", "💾"),
                    ("Network Receive", f"{metrics['network_traffic']['receive']} KB/s", "📥"),
                    ("Network Transmit", f"{metrics['network_traffic']['transmit']} KB/s", "📤"),
                    ("I/O Read", f"{metrics['io_usage']['read']} MB/s", "📖"),
                    ("I/O Write", f"{metrics['io_usage']['write']} MB/s", "✍️"),
                    ("Processes", f"{metrics['processes']}", "🔢"),
                    ("CPU Throttling", f"{metrics['cpu_throttling']['throttling_ratio']}%", "🐢"),
                ]

                for i in range(0, len(metrics_grid), 3):
                    cols = st.columns(3)
                    for j in range(3):
                        if i + j < len(metrics_grid):
                            label, value, icon = metrics_grid[i + j]
                            with cols[j]:
                                st.markdown(f"""
                                <div class="metric-card">
                                    <div class="metric-value">{value}</div>
                                    <div class="metric-label"><span class="metric-icon">{icon}</span> {label}</div>
                                </div>
                                """, unsafe_allow_html=True)

            with col2:
                st.subheader("Quick Links")
                
                st.markdown('<div class="quick-links">', unsafe_allow_html=True)
                for container in containers:
                    if not container['ports']:
                        continue
                    
                    name = container['name']
                    status = container['status']
                    ports = container['ports']
                    
                    status_class = {
                        'running': 'status-running',
                        'exited': 'status-stopped'
                    }.get(status, 'status-other')
                    
                    link = f"http://localhost:{ports[0].split(':')[0]}"
                    icon = "🐳"
                    
                    st.markdown(f"""
                    <div href={link} class="quick-link">
                        <span class="quick-link-icon">{icon}</span>
                        <strong>{name.upper()}</strong>
                        <a href={link}>{link}</a>
                        <div class="container-status {status_class}">{status.upper()}</div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        time.sleep(0.1)

if __name__ == "__main__":
    st.set_page_config(page_title="LogWatcher Dashboard", layout="wide")
    load_css()
    main()