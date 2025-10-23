import streamlit as st
import json
import os

USER_DB = "users.json"

def load_users():
    if not os.path.exists(USER_DB):
        return {}
    with open(USER_DB, "r") as f:
        return json.load(f)

def login():
    st.sidebar.title("🔐 Login")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.username = None

    if not st.session_state.logged_in:
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        login_button = st.sidebar.button("Login")

        if login_button:
            users = load_users()
            user = users.get(username)
            if user and user["password"] == password:
                st.session_state.logged_in = True
                st.session_state.role = user["role"]
                st.session_state.username = username
                st.success(f"Welcome, {username}! You are logged in as {user['role']}.")
                st.rerun()
            else:
                st.error("Invalid username or password.")
        return False, None
    else:
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.role = None
            st.rerun()
        return True, st.session_state.role
