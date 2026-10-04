"""Send requests to the internal API for a locally signed-in user."""
import requests
import streamlit as st


def api_request(method, path, **kwargs):
    if not st.session_state.get("logged_in"):
        st.info("Log in to continue.")
        st.stop()
    return requests.request(
        method, "http://127.0.0.1:8000" + path, timeout=120, **kwargs,
    )
