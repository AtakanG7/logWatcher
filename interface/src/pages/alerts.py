# pages/alerts.py

import streamlit as st
from utils.alerting import get_current_alerts, create_new_alert

def show_alerts_page():
    st.title("Alerts Management")

    # Display current alerts
    st.header("Current Alerts")
    alerts = get_current_alerts()
    if alerts:
        for alert in alerts:
            st.warning(f"Alert: {alert['labels']['alertname']} - {alert['annotations']['description']}")
    else:
        st.info("No active alerts")

    # Create new alert
    st.header("Create New Alert")
    with st.form("new_alert"):
        name = st.text_input("Alert Name")
        expression = st.text_input("Alert Expression (PromQL)")
        duration = st.text_input("Duration (e.g., 5m)", "5m")
        severity = st.selectbox("Severity", ["critical", "warning", "info"])

        submitted = st.form_submit_button("Create Alert")
        if submitted:
            if create_new_alert(name, expression, duration, severity):
                st.success(f"Alert '{name}' created successfully")
            else:
                st.error("Failed to create alert")

    # Refresh button
    if st.button("Refresh Alerts"):
        st.experimental_rerun()

if __name__ == "__main__":
    show_alerts_page()