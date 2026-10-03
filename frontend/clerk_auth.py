import os
from pathlib import Path

from dotenv import load_dotenv
import requests
import streamlit as st
import streamlit.components.v2 as components

from api_client import api_request

load_dotenv(Path(__file__).resolve().parents[1] / "backend" / ".env")

_clerk = components.component(
    "clerk_auth",
    html='<div class="clerk-status">Loading secure sign-in…</div><div class="clerk-controls"></div><div class="clerk-signin"></div><div class="clerk-signup" hidden></div><div class="clerk-user" hidden></div>',
    js=(Path(__file__).parent / "clerk_component.js").read_text(),
    isolate_styles=False,
)


def login():
    key = os.getenv("CLERK_PUBLISHABLE_KEY", "")
    if not key:
        st.info("Secure sign-in is being configured. Please check back shortly.")
        st.stop()
    result = _clerk(
        key="clerk_session", data={
            "publishableKey": key,
            "authenticated": bool(st.session_state.get("clerk_token")),
        },
        default={"auth": None}, on_auth_change=lambda: None,
    )
    auth = result.auth
    if not isinstance(auth, dict) or not auth.get("token"):
        for name in ("clerk_token", "clerk_user", "chat_result", "it_result", "hr_result"):
            st.session_state.pop(name, None)
        if isinstance(auth, dict) and auth.get("error"):
            st.error("Secure sign-in could not load. Please refresh or contact your administrator.")
        st.stop()
    st.session_state.clerk_token = auth["token"]
    try:
        response = api_request("GET", "/api/auth/me")
        if response.status_code != 200:
            st.error("Sign-in verification is temporarily unavailable. Please try again shortly.")
            st.stop()
        user = response.json()
    except requests.RequestException:
        st.error("Unable to verify your sign-in. Please try again shortly.")
        st.stop()
    old_user = st.session_state.get("clerk_user", {})
    if old_user.get("user_id") != user["user_id"]:
        for name in ("chat_result", "it_result", "hr_result"):
            st.session_state.pop(name, None)
    st.session_state.clerk_user = user
    st.sidebar.write("Signed in", auth.get("name") or user["user_id"])
    st.sidebar.caption(user["role"])
    return user["role"]
