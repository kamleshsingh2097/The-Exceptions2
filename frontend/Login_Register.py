import streamlit as st
import requests

API_URL = "http://localhost:8000"


def get_error_detail(response, default_message: str) -> str:
    try:
        data = response.json()
        if isinstance(data, dict):
            return data.get("detail", default_message)
    except ValueError:
        pass
    text = (response.text or "").strip()
    return text or default_message


st.set_page_config(page_title="Login/Register", layout="wide")
st.title("Login/Register")
st.caption("Access your role-based workspace")

if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "customer_email" not in st.session_state:
    st.session_state.customer_email = None
if "customer_name" not in st.session_state:
    st.session_state.customer_name = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None

if st.session_state.auth_token:
    if not st.session_state.user_role:
        st.warning("Session role not found. Please logout and login again.")
    st.success(f"Logged in as {st.session_state.customer_email}")
    st.info("Use the sidebar to open pages.")
    if st.button("Logout"):
        st.session_state.auth_token = None
        st.session_state.customer_email = None
        st.session_state.customer_name = None
        st.session_state.user_role = None
        st.rerun()
else:
    login_tab, register_tab = st.tabs(["Login", "Register"])

    with register_tab:
        st.subheader("Create Account")
        role_options = {
            "Event Organizer": "organizer",
            "Customer": "customer",
            "Entry Manager": "entry_manager",
            "Support Executive": "support",
        }
        with st.form("register_form"):
            reg_name = st.text_input("Name")
            reg_email = st.text_input("Email")
            reg_password = st.text_input("Password", type="password")
            reg_role_label = st.selectbox("Register As", options=list(role_options.keys()))
            if st.form_submit_button("Register"):
                reg_res = requests.post(
                    f"{API_URL}/auth/register",
                    json={
                        "name": reg_name,
                        "email": reg_email,
                        "password": reg_password,
                        "role": role_options[reg_role_label],
                    },
                )
                if reg_res.status_code == 200:
                    st.success("Registration successful. Please login.")
                else:
                    st.error(get_error_detail(reg_res, "Registration failed"))

    with login_tab:
        st.subheader("Login")
        with st.form("login_form"):
            login_email = st.text_input("Email", key="app_login_email")
            login_password = st.text_input("Password", type="password", key="app_login_password")
            if st.form_submit_button("Login"):
                login_res = requests.post(
                    f"{API_URL}/auth/login",
                    json={"email": login_email, "password": login_password},
                )
                if login_res.status_code == 200:
                    login_data = login_res.json()
                    login_role = login_data.get("role")
                    if isinstance(login_role, str) and login_role.startswith("UserRole."):
                        login_role = login_role.split(".", 1)[1]
                    st.session_state.auth_token = login_data["access_token"]
                    st.session_state.customer_email = login_data["email"]
                    st.session_state.customer_name = login_data["name"]
                    st.session_state.user_role = login_role
                    st.success("Login successful.")
                    st.rerun()
                else:
                    st.error(get_error_detail(login_res, "Login failed"))
