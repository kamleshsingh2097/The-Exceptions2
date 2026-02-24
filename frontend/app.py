import streamlit as st
import requests

st.set_page_config(page_title="Event Pro", layout="wide")

if "auth_token" not in st.session_state:
    st.title("🔐 Secure Login")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            # Simulate API call to /token
            st.session_state.auth_token = "valid_jwt_token"
            st.session_state.user_role = "customer" # Should come from backend
            st.success("Logged in! Use the sidebar to navigate.")
else:
    st.title(f"Welcome back!")
    st.info(f"You are logged in as a **{st.session_state.user_role.upper()}**")
    if st.button("Logout"):
        del st.session_state.auth_token
        st.rerun()