# frontend/employee_chat.py
import streamlit as st
import requests

def show_employee_chat():
    st.title("💬 Employee Assistant")
    st.write("Ask questions about company policies, procedures, and general information.")
    
    query = st.text_input("What would you like to know?", placeholder="e.g., What is the vacation policy?")
    
    if query:
        with st.spinner("Searching for information..."):
            try:
                # 🔧 Corrected endpoint here
                response = requests.post("http://localhost:8000/api/chat/query", json={"query": query})
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check for errors in the response
                    if data.get("error"):
                        error_msg = data.get("error", "")
                        if "API key" in error_msg or "invalid_api_key" in error_msg:
                            st.error("🔑 **Invalid OpenAI API Key**: Please update the OPENAI_API_KEY in `/backend/.env` with a valid key from https://platform.openai.com/api-keys")
                        elif "Vector store not found" in error_msg or "No documents" in error_msg:
                            st.warning("📂 **No Documents Found**: Please upload documents first using the HR Dashboard or IT Dashboard.")
                        else:
                            st.error(f"❌ **Error**: {error_msg}")
                    else:
                        answer = data.get("answer", "No information found.")
                        sources = data.get("sources", [])
                        
                        st.markdown(f"**🤖 Answer:** {answer}")
                        
                        if sources:
                            st.markdown("**📚 Sources:**")
                            for source in sources:
                                st.markdown(f"- {source}")
                else:
                    st.error("Failed to get response from the server.")
            except requests.exceptions.RequestException:
                st.error("🔌 **Backend Not Available**: Unable to connect to the backend server. Please make sure the backend is running on port 8000.")
