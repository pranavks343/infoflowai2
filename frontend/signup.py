import streamlit as st
import json
import os

USER_DB = "users.json"

# Ensure user database exists
def init_user_db():
    if not os.path.exists(USER_DB):
        with open(USER_DB, "w") as f:
            json.dump({}, f)

# Load current users
def load_users():
    with open(USER_DB, "r") as f:
        return json.load(f)

# Save users to db
def save_users(users):
    with open(USER_DB, "w") as f:
        json.dump(users, f, indent=2)

def show_signup():
    st.title("📝 Sign Up for InfoFlow AI")

    init_user_db()

    with st.form("signup_form"):
        username = st.text_input("Choose a username")
        password = st.text_input("Choose a password", type="password")
        role = st.selectbox("Select your role", ["Employee", "HR", "IT"])
        submit = st.form_submit_button("Create Account")

        if submit:
            if not username or not password:
                st.warning("Username and password are required.")
                return

            users = load_users()
            if username in users:
                st.error("Username already exists. Please choose another.")
                return

            users[username] = {"password": password, "role": role}
            save_users(users)

            st.success(f"Account created for '{username}' as '{role}' ✅")
            st.info("You can now go to the login screen.")
