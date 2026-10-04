import streamlit as st
from login import login
from signup import show_signup
from hr_dashboard import show_hr_dashboard
from it_dashboard import show_it_dashboard
from employee_chat import show_employee_chat

# Set white background (default) and wide layout
st.set_page_config(page_title="🤖 InfoFlow AI", layout="wide")

# ✅ Clean White Header
st.markdown("""
    <div style='background-color:#ffffff;padding:20px 10px;border-radius:10px;border:1px solid #e6e6e6;box-shadow:0 2px 5px rgba(0,0,0,0.05);margin-bottom:20px'>
        <h1 style='color:#1f4e79;text-align:center;'>🤖 InfoFlow AI – Internal Knowledge Assistant</h1>
    </div>
""", unsafe_allow_html=True)

# 👤 Auth Toggle in Sidebar
auth_mode = st.sidebar.radio("🔐 Choose Authentication", ["Login", "Sign Up"])

# ✍️ Signup
if auth_mode == "Sign Up":
    st.sidebar.markdown("🚀 **Create your account to get started!**")
    show_signup()
    st.stop()

# 🔑 Login
logged_in, role = login()
if not logged_in:
    st.sidebar.info("ℹ️ Please log in to access the system.")
    st.stop()

# 📂 Role-Based Sidebar Navigation
st.sidebar.header("📂 Navigation")

if role == "Employee":
    menu = st.sidebar.selectbox("🧑‍💼 Employee Panel", ["Employee Assistant"])
elif role == "HR":
    menu = st.sidebar.selectbox("🧑‍💼 HR Panel", ["HR Dashboard", "Employee Assistant"])
elif role == "IT":
    menu = st.sidebar.selectbox("🧑‍💻 IT Panel", ["IT Support", "Employee Assistant"])
else:
    menu = None

# 📄 Page Routing
st.markdown("---")
if menu == "Employee Assistant":
    show_employee_chat()
elif menu == "HR Dashboard" and role == "HR":
    show_hr_dashboard()
elif menu == "IT Support" and role == "IT":
    show_it_dashboard()
else:
    st.warning("⚠️ Invalid role or unauthorized access.")
