import streamlit as st
import requests

def show_it_dashboard():
    st.title("🛠️ IT Employee Knowledge Assistant")

    query = st.text_input("Ask about IT policies, setup guides, troubleshooting...")

    if query:
        with st.spinner("Processing..."):
            try:
                response = requests.post("http://localhost:8000/api/it/query", json={"query": query})
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check for errors in the response
                    if data.get("error"):
                        error_msg = data.get("error", "")
                        if "API key" in error_msg or "invalid_api_key" in error_msg:
                            st.error("🔑 **Invalid OpenAI API Key**: Please update the OPENAI_API_KEY in `/backend/.env` with a valid key from https://platform.openai.com/api-keys")
                        elif "Vector store not found" in error_msg or "No documents" in error_msg:
                            st.warning("📂 **No Documents Found**: Please upload documents first using the HR Dashboard.")
                        else:
                            st.error(f"❌ **Error**: {error_msg}")
                    else:
                        answer = data.get("answer", "No answer returned.")
                        sources = data.get("sources", [])
                        st.markdown(f"**🧠 Answer:** {answer}")
                        if sources:
                            st.markdown("📄 **Sources:** " + ", ".join(sources))
                else:
                    st.error("❌ Error from server.")
                    st.code(response.text)
            except requests.exceptions.RequestException:
                st.error("⚠️ Cannot reach backend. Is FastAPI running?")
