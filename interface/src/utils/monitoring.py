import requests
from typing import Dict, Any, Optional

class PrometheusMonitor:
    def __init__(self, prometheus_url: str = "http://localhost:9090"):
        self.prometheus_url = prometheus_url

    def query(self, query: str) -> Dict[str, Any]:
        """Execute a PromQL query and return the result."""
        response = requests.get(f"{self.prometheus_url}/api/v1/query", params={"query": query})
        response.raise_for_status()
        return response.json()

    def get_metric_value(self, query: str) -> Optional[float]:
        """Get a single metric value from a query."""
        result = self.query(query)
        if result["status"] == "success" and result["data"]["result"]:
            return float(result["data"]["result"][0]["value"][1])
        return None

    def get_container_cpu_usage(self, container_name: str) -> Optional[float]:
        """Get the current CPU usage of a specific container as a percentage."""
        query = f'sum(rate(container_cpu_usage_seconds_total{{name=~".*{container_name}.*"}}[5m])) * 100'
        cpu_usage = self.get_metric_value(query)
        return round(cpu_usage, 2) if cpu_usage is not None else None

    def get_container_memory_usage(self, container_name: str) -> Dict[str, Optional[float]]:
        """Get the current memory usage of a specific container."""
        usage_query = f'container_memory_usage_bytes{{name=~".*{container_name}.*"}}'
        limit_query = f'container_spec_memory_limit_bytes{{name=~".*{container_name}.*"}}'
        
        usage = self.get_metric_value(usage_query)
        limit = self.get_metric_value(limit_query)
        
        usage_mb = round(usage / (1024 * 1024), 2) if usage is not None else None
        limit_mb = round(limit / (1024 * 1024), 2) if limit is not None else None
        percentage = round((usage / limit) * 100, 2) if usage is not None and limit is not None and limit > 0 else None
        
        return {
            "usage_mb": usage_mb,
            "limit_mb": float(0) if limit_mb == float(0) else limit_mb,
            "percentage": percentage
        }

    def get_container_disk_usage(self, container_name: str) -> Optional[float]:
        """Get the current disk usage of a specific container in MB."""
        query = f'container_fs_usage_bytes{{name=~".*{container_name}.*"}}'
        disk_usage = self.get_metric_value(query)
        return round(disk_usage / (1024 * 1024), 2) if disk_usage is not None else None

    def get_container_network_traffic(self, container_name: str) -> Dict[str, Optional[float]]:
        """Get the current network traffic of a specific container in KB/s."""
        receive_query = f'rate(container_network_receive_bytes_total{{name=~".*{container_name}.*"}}[5m])'
        transmit_query = f'rate(container_network_transmit_bytes_total{{name=~".*{container_name}.*"}}[5m])'
        
        receive = self.get_metric_value(receive_query)
        transmit = self.get_metric_value(transmit_query)
        
        return {
            "receive": round(receive / 1024, 2) if receive is not None else None,
            "transmit": round(transmit / 1024, 2) if transmit is not None else None
        }

    def get_container_io_usage(self, container_name: str) -> Dict[str, Optional[float]]:
        """Get the current I/O usage of a specific container in MB/s."""
        read_query = f'rate(container_fs_reads_bytes_total{{name=~".*{container_name}.*"}}[5m])'
        write_query = f'rate(container_fs_writes_bytes_total{{name=~".*{container_name}.*"}}[5m])'
        
        read = self.get_metric_value(read_query)
        write = self.get_metric_value(write_query)
        
        return {
            "read": round(read / (1024 * 1024), 2) if read is not None else None,
            "write": round(write / (1024 * 1024), 2) if write is not None else None
        }

    def get_container_processes(self, container_name: str) -> Optional[int]:
        """Get the number of processes running inside the container."""
        query = f'container_processes{{name=~".*{container_name}.*"}}'
        return int(self.get_metric_value(query)) if self.get_metric_value(query) is not None else None

    def get_container_cpu_throttling(self, container_name: str) -> Dict[str, Optional[float]]:
        """Get CPU throttling information for the container."""
        periods_query = f'container_cpu_cfs_periods_total{{name=~".*{container_name}.*"}}'
        throttled_periods_query = f'container_cpu_cfs_throttled_periods_total{{name=~".*{container_name}.*"}}'
        
        periods = self.get_metric_value(periods_query)
        throttled_periods = self.get_metric_value(throttled_periods_query)
        
        throttling_ratio = (throttled_periods / periods) * 100 if periods is not None and throttled_periods is not None and periods > 0 else None
        
        return {
            "periods": periods,
            "throttled_periods": throttled_periods,
            "throttling_ratio": round(throttling_ratio, 2) if throttling_ratio is not None else None
        }

def get_container_metrics(container_name: str) -> Dict[str, Any]:
    """Get all container metrics in one call."""
    monitor = PrometheusMonitor()
    return {
        "cpu_usage": monitor.get_container_cpu_usage(container_name),
        "memory_usage": monitor.get_container_memory_usage(container_name),
        "disk_usage": monitor.get_container_disk_usage(container_name),
        "network_traffic": monitor.get_container_network_traffic(container_name),
        "io_usage": monitor.get_container_io_usage(container_name),
        "processes": monitor.get_container_processes(container_name),
        "cpu_throttling": monitor.get_container_cpu_throttling(container_name)
    }