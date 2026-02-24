import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.title("🛂 Entry Validation")
st.info("Check-in attendees by entering their unique ticket code.")

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