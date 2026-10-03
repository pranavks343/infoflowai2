import streamlit as st


def show_answer(data):
    if data.get("error"):
        st.error(data["error"])
        return
    st.markdown("**Answer**")
    st.write(data.get("answer", "No answer returned."))
    if data.get("sources"):
        st.markdown("**Sources**")
        for source in data["sources"]:
            st.write(source)
