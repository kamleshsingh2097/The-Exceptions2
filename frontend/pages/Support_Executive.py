import streamlit as st
import requests
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

API_URL = "http://localhost:8000"

st.title("🎧 Support Executive")
st.caption("Review refund requests and resolve customer issues")

if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None

if not st.session_state.auth_token:
    st.warning("Please login from the Home page first.")
    st.stop()
if st.session_state.get("user_role") != "support":
    st.error("Access denied. This page is only for Support Executive role.")
    st.stop()

def get_error_detail(response, default_message: str) -> str:
    try:
        data = response.json()
        if isinstance(data, dict):
            return data.get("detail", default_message)
    except ValueError:
        pass
    text = (response.text or "").strip()
    return text or default_message


order_id = st.number_input("Order ID", min_value=1)
resolution = st.text_area("Resolution Notes") # [cite: 156]

if st.button("Process Refund Request"):
    # Rule: Refund allowed only before event date [cite: 158]
    # Rule: Refund restores seat availability [cite: 63, 161]
    headers = {}
    if st.session_state.get("auth_token"):
        headers["Authorization"] = f"Bearer {st.session_state.auth_token}"
    res = requests.post(
        f"{API_URL}/orders/{order_id}/refund",
        params={"review_note": resolution},
        headers=headers
    )
    if res.status_code == 200:
        st.warning("Order Refunded. Seat inventory has been restored.")
    else:
        st.error(f"Refund Failed: {get_error_detail(res, 'Refund failed')}")

st.divider()
st.subheader("Customer Refund Requests")
try:
    req_res = requests.get(f"{API_URL}/support/refund-requests")
    if req_res.status_code == 200:
        requests_data = req_res.json()
        if not requests_data:
            st.info("No refund requests yet.")
        else:
            st.dataframe(requests_data, use_container_width=True)
    else:
        st.error(f"Could not fetch requests: {get_error_detail(req_res, 'Request failed')}")
except requests.exceptions.RequestException as exc:
    st.error(f"Support request feed unavailable: {exc}")
