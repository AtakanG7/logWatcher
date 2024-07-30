# utils/alerting.py

import requests
from typing import List, Dict, Any

class PrometheusAlerts:
    def __init__(self, prometheus_url: str = "http://localhost:9090"):
        self.prometheus_url = prometheus_url

    def get_alerts(self) -> List[Dict[str, Any]]:
        """Fetch current alerts from Prometheus"""
        response = requests.get(f"{self.prometheus_url}/api/v1/alerts")
        if response.status_code == 200:
            return response.json().get('data', {}).get('alerts', [])
        return []

    def create_alert(self, name: str, expression: str, duration: str, severity: str) -> bool:
        """Create a new alert rule in Prometheus"""
        # In a real scenario, this would involve updating Prometheus' configuration file
        # and reloading Prometheus. For this example, we'll just simulate it.
        print(f"Creating alert: {name} with expression: {expression}")
        return True

def get_current_alerts() -> List[Dict[str, Any]]:
    alerts = PrometheusAlerts()
    return alerts.get_alerts()

def create_new_alert(name: str, expression: str, duration: str, severity: str) -> bool:
    alerts = PrometheusAlerts()
    return alerts.create_alert(name, expression, duration, severity)