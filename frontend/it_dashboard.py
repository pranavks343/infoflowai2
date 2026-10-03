import requests
import streamlit as st
from api_client import api_request
from answer_view import show_answer


def show_it_dashboard():
    st.title("🛠️ IT Knowledge Assistant")
    with st.form("it_question"):
        query = st.text_input("Ask about IT policies, setup guides, troubleshooting...")
        submitted = st.form_submit_button("Ask")
    if submitted and query.strip():
        with st.spinner("Searching for information..."):
            try:
                response = api_request("POST", "/api/it/query", json={"query": query})
                response.raise_for_status()
                st.session_state.it_result = response.json()
            except requests.RequestException:
                st.error("Unable to get an answer right now. Please try again.")
    if "it_result" in st.session_state:
        show_answer(st.session_state.it_result)
