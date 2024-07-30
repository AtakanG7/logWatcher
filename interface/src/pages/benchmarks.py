# pages/benchmarks.py

import streamlit as st
import plotly.graph_objects as go
from utils.benchmarking import ContainerBenchmark
from utils.dockermanager import DockerManager
import os 
def load_css():
    css_file = os.path.join(os.path.dirname(__file__), "..", "public", "css", "style.css")
    with open(css_file, "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

docker_manager = DockerManager()

def plot_benchmark_results(results):
    fig = go.Figure()

    if 'cpu' in results:
        fig.add_trace(go.Bar(x=['CPU Avg', 'CPU Max', 'CPU Min'], 
                             y=[results['cpu']['average'], results['cpu']['max'], results['cpu']['min']],
                             name='CPU Usage (%)', marker_color='blue'))

    if 'memory' in results:
        fig.add_trace(go.Bar(x=['Memory Avg', 'Memory Max', 'Memory Min'], 
                             y=[results['memory']['average'], results['memory']['max'], results['memory']['min']],
                             name='Memory Usage (MB)', marker_color='green'))

    if 'http' in results:
        fig.add_trace(go.Bar(x=['Requests/s', 'Success Rate'], 
                             y=[results['http']['requests_per_second'], 
                                results['http']['successful_requests'] / results['http']['total_requests'] * 100],
                             name='HTTP Performance', marker_color='red'))

    fig.update_layout(title='Benchmark Results', barmode='group')
    st.plotly_chart(fig)

def show_benchmarks_page():
    # Container selection
    containers = docker_manager.list_containers(all=True, networks=['monitoring'])
    container_names = [x.get('name') for x in containers]
    selected_container = st.selectbox("Select Container to Benchmark", container_names)

    st.title(f"Benchmark: {selected_container}")

    # Benchmark parameters
    st.subheader("Benchmark Parameters")
    duration = st.slider("Benchmark Duration (seconds)", min_value=5, max_value=60, value=10)
    http_url = st.text_input("Application URL", "http://localhost:8080")
    num_requests = st.number_input("Number of HTTP Requests", min_value=10, max_value=1000, value=100)

    if st.button("Run Benchmark"):
        with st.spinner("Running benchmarks..."):
            benchmark = ContainerBenchmark(selected_container)
            benchmark.run_all_benchmarks(http_url, duration, num_requests)
            results = benchmark.get_results()

        st.success("Benchmark completed!")
        
        # Display results
        st.subheader("Benchmark Results")
        plot_benchmark_results(results)

        # Detailed results
        st.subheader("Detailed Results")
        st.json(results)

if __name__ == "__main__":
    load_css()
    show_benchmarks_page()