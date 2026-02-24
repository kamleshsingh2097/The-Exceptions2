import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.title("🛂 Entry Manager")
st.info("Check-in attendees by entering their unique ticket code.")

if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None

if not st.session_state.auth_token:
    st.warning("Please login from the Home page first.")
    st.stop()
if st.session_state.get("user_role") != "entry_manager":
    st.error("Access denied. This page is only for Entry Manager role.")
    st.stop()

ticket_code = st.text_input("Enter/Scan Ticket Code")

if st.button("Validate & Admit"):
    if ticket_code:
        # Business Rule: Ticket invalid after use [cite: 64, 163]
        res = requests.post(f"{API_URL}/tickets/validate", params={"ticket_code": ticket_code})
        if res.status_code == 200:
            st.balloons()
            st.success("✅ VALID: Access Granted.")
        else:
            st.error(f"❌ INVALID: {res.json().get('detail')}")
