import streamlit as st
import requests
import os

UPLOADS_FOLDER = os.path.join(os.environ.get("DATA_DIR", "frontend/data"), "uploaded_docs")

def show_hr_dashboard():
    st.title("📁 HR Dashboard – Upload Documents to Knowledge Base")

    # ✅ Ensure uploads folder exists
    if not os.path.exists(UPLOADS_FOLDER):
        os.makedirs(UPLOADS_FOLDER)

    # ✅ File uploader interface
    uploaded_file = st.file_uploader("📤 Upload a PDF/DOCX/TXT file", type=["pdf", "docx", "txt"])

    if uploaded_file is not None:
        # Save uploaded file to disk
        file_path = os.path.join(UPLOADS_FOLDER, os.path.basename(uploaded_file.name))
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"✅ File saved to: {file_path}")

        # Button to send to FastAPI for ingestion
        if st.button("🚀 Send to Knowledge Base"):
            with open(file_path, "rb") as f:
                files = {"file": (uploaded_file.name, f)}
                try:
                    response = requests.post("http://localhost:8000/api/ingest/upload", files=files)
                    if response.status_code == 200 and not response.json().get("error"):
                        st.success("✅ File uploaded and indexed into the vector store!")
                    else:
                        st.error(f"❌ Upload failed. Status code: {response.status_code}")
                        st.code(response.text)
                except requests.exceptions.RequestException:
                    st.error("🔌 Backend not available. Please ensure FastAPI is running on port 8000.")

    # ✅ Check if there are any files uploaded
    available_files = [
        f for f in os.listdir(UPLOADS_FOLDER)
        if f.endswith((".pdf", ".docx", ".txt"))
    ]

    st.markdown("---")
    st.subheader("💬 Ask a Query from Knowledge Base")

    if not available_files:
        st.warning("⚠️ No documents found in the knowledge base. Please ask the HR to upload the relevant file.")
    else:
        user_query = st.text_input("🔍 Enter your query")
        if user_query:
            with st.spinner("Thinking..."):
                try:
                    response = requests.post(
                        "http://localhost:8000/api/chat/query",
                        json={"query": user_query}
                    )
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Check for errors in the response
                        if data.get("error"):
                            error_msg = data.get("error", "")
                            if "API key" in error_msg or "invalid_api_key" in error_msg:
                                st.error("🔑 **Invalid OpenAI API Key**: Please update the OPENAI_API_KEY in `/backend/.env` with a valid key from https://platform.openai.com/api-keys")
                            elif "Vector store not found" in error_msg or "No documents" in error_msg:
                                st.warning("📂 **No Documents Found**: Please upload documents first and click '🚀 Send to Knowledge Base'.")
                            else:
                                st.error(f"❌ **Error**: {error_msg}")
                        else:
                            st.success("🧠 Answer:")
                            st.write(data.get("answer", "No answer provided."))

                            if sources := data.get("sources"):
                                st.markdown("#### 📚 Sources:")
                                for src in sources:
                                    st.write(f"• {src}")
                    else:
                        st.error("❌ Failed to fetch answer from backend.")
                        st.code(response.text)
                except requests.exceptions.RequestException:
                    st.error("🔌 Backend not available. Please ensure FastAPI is running on port 8000.")
