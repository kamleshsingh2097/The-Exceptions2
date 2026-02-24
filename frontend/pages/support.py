import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.title("🎧 Support & Refund Center")

order_id = st.number_input("Order ID", min_value=1)
resolution = st.text_area("Resolution Notes") # [cite: 156]

if st.button("Process Refund Request"):
    # Rule: Refund allowed only before event date [cite: 158]
    # Rule: Refund restores seat availability [cite: 63, 161]
    res = requests.post(f"{API_URL}/orders/{order_id}/refund")
    if res.status_code == 200:
        st.warning("Order Refunded. Seat inventory has been restored.")
    else:
        st.error(f"Refund Failed: {res.json().get('detail')}")

st.divider()
st.subheader("Open Support Cases")
# Extension: View support dashboard [cite: 174]
st.write("1. Refund Request #882 - Pending")
st.write("2. Seat Change #901 - Resolved")