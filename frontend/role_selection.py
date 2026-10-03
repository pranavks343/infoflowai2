"""Choose a workspace after sign-in without changing account permissions."""
import streamlit as st

ROLES = ("Employee", "HR", "IT", "Admin")


def choose_role(account_role):
    allowed = ROLES if account_role == "Admin" else ("Employee", account_role)
    selected = st.session_state.get("signin_role")
    if selected not in allowed:
        st.session_state.pop("signin_role", None)
        selected = None

    if selected is None:
        st.subheader("Choose your role")
        st.caption("Which workspace would you like to use for this sign-in?")
        with st.form("signin_role_form"):
            requested = st.radio(
                "I am signing in as", ROLES, index=None, horizontal=True,
                key="signin_role_choice",
            )
            st.caption("HR, IT, and Admin workspaces require access assigned by your administrator.")
            submitted = st.form_submit_button("Continue to workspace", type="primary")
        if submitted:
            if requested is None:
                st.warning("Select a role to continue.")
            elif requested not in allowed:
                st.warning(
                    f"Your account has {account_role} access. Ask your administrator "
                    f"to assign {requested} access, or select an available role."
                )
            else:
                st.session_state.signin_role = requested
                st.rerun()
        st.stop()

    st.sidebar.caption(f"Workspace: {selected}")
    if st.sidebar.button("Change workspace"):
        for name in ("signin_role", "signin_role_choice", "chat_result", "it_result", "hr_result"):
            st.session_state.pop(name, None)
        st.rerun()
    return selected
