"""Send the current Clerk session token with every backend request."""
import requests
import streamlit as st


def api_request(method, path, **kwargs):
    token = st.session_state.get("clerk_token")
    if not token:
        st.info("Sign in to continue.")
        st.stop()
    response = requests.request(
        method, "http://127.0.0.1:8000" + path,
        headers={"Authorization": "Bearer " + token}, timeout=120, **kwargs,
    )
    if response.status_code == 401:
        st.warning("Your session expired. Wait for it to refresh or sign in again.")
        st.stop()
    if response.status_code == 403:
        st.error("Your account does not have permission to perform this action.")
        st.stop()
    return response
