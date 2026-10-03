from pathlib import Path
import os
import requests
import streamlit as st
from api_client import api_request
from answer_view import show_answer

UPLOADS_FOLDER = Path(os.environ.get("DATA_DIR", "frontend/data")) / "uploaded_docs"


def show_hr_dashboard():
    st.title("📁 HR Dashboard")
    uploaded_file = st.file_uploader("Upload a PDF, DOCX, or TXT file", type=["pdf", "docx", "txt"])
    if st.button("Send to Knowledge Base", disabled=uploaded_file is None) and uploaded_file:
        with st.spinner("Indexing document..."):
            try:
                filename = Path(uploaded_file.name).name
                response = api_request("POST", "/api/ingest/upload", files={"file": (filename, uploaded_file.getvalue())})
                response.raise_for_status()
                data = response.json()
                if data.get("error"):
                    st.error(data["error"])
                else:
                    UPLOADS_FOLDER.mkdir(parents=True, exist_ok=True)
                    (UPLOADS_FOLDER / filename).write_bytes(uploaded_file.getvalue())
                    st.success("Document indexed. You can now ask questions about it.")
            except (requests.RequestException, OSError):
                st.error("Unable to finish uploading the document. Please try again.")
    st.divider()
    with st.form("hr_question"):
        query = st.text_input("Ask a question about the knowledge base")
        submitted = st.form_submit_button("Ask")
    if submitted and query.strip():
        with st.spinner("Searching..."):
            try:
                response = api_request("POST", "/api/chat/query", json={"query": query})
                response.raise_for_status()
                st.session_state.hr_result = response.json()
            except requests.RequestException:
                st.error("Unable to get an answer right now. Please try again.")
    if "hr_result" in st.session_state:
        show_answer(st.session_state.hr_result)
