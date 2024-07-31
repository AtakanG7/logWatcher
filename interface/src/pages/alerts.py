# pages/alerts.py

import streamlit as st
from utils.alerting import get_current_alerts, create_new_alert
import utils.configuration as config
import os
def load_css():
    css_file = os.path.join(os.path.dirname(__file__), "..", "public", "css", "style.css")
    with open(css_file, "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def show_alerts_section():
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

def show_alert_settings_section():
    st.title("Alert Settings")

    # Get the current email settings
    email_settings = config.get_email_settings()

    # Edit alert
    st.header("Email Configurations")
    with st.form("email_settings"):
        st.subheader("Authentication")
        auth_username = st.text_input(label="Auth Username", placeholder="your_username", value=email_settings.get("auth_username", ""))
        auth_password = st.text_input(label="Auth Password", placeholder="your_password", value=email_settings.get("auth_password", ""), type="password")

        st.subheader("Email Settings")
        from_address = st.text_input(label="From Address", placeholder="your_email@example.com", value=email_settings.get("from", ""))
        smarthost = st.text_input(label="Smarthost", placeholder="smtp.example.com", value=email_settings.get("smarthost", ""))
        to_address = st.text_input(label="To Address", placeholder="recipient_email@example.com", value=email_settings.get("to", ""))
        if st.form_submit_button(label="Update Email Settings"):
            config.update_email_settings({
                "auth_username": auth_username,
                "auth_password": auth_password,
                "from": from_address,
                "smarthost": smarthost,
                "to": to_address
            })
            st.success("Email settings updated successfully")

if __name__ == "__main__":
    try:
        st.set_page_config(page_title="Alerts Management", layout="wide")
        load_css()
        show_alerts_section()
        show_alert_settings_section()
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")