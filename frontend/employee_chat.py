import requests
import streamlit as st
from api_client import api_request
from answer_view import show_answer


def show_employee_chat():
    st.title("💬 Employee Assistant")
    with st.form("employee_question"):
        query = st.text_input("What would you like to know?")
        submitted = st.form_submit_button("Ask")
    if submitted and query.strip():
        with st.spinner("Searching for information..."):
            try:
                response = api_request("POST", "/api/chat/query", json={"query": query})
                response.raise_for_status()
                st.session_state.chat_result = response.json()
            except requests.RequestException:
                st.error("Unable to get an answer right now. Please try again.")
    if "chat_result" in st.session_state:
        show_answer(st.session_state.chat_result)
