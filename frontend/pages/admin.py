import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.title("🛡️ Platform Admin Dashboard")

tab1, tab2 = st.tabs(["Manage Events", "Analytics"])

with tab1:
    st.subheader("Onboard New Venue & Event")
    # Venue Creation
    with st.expander("Add New Venue"):
        v_name = st.text_input("Venue Name")
        v_city = st.text_input("City")
        v_cap = st.number_input("Total Capacity", min_value=1)
        if st.button("Register Venue"):
            requests.post(f"{API_URL}/admin/venues/", params={"name": v_name, "city": v_city, "capacity": v_cap})
            st.success("Venue Registered!")

    # Event Creation [cite: 123]
    with st.form("event_creation"):
        st.write("Create New Event")
        v_id = st.number_input("Venue ID", min_value=1)
        e_name = st.text_input("Event Name")
        e_cat = st.selectbox("Category", ["Concert", "Workshop", "Sports"])
        e_date = st.date_input("Event Date")
        e_price = st.number_input("Ticket Price", min_value=0.0)
        e_limit = st.number_input("Max Tickets Per User", min_value=1, value=5)
        
        if st.form_submit_button("Launch Event"):
            # This triggers auto-generation of seats in the backend [cite: 126]
            requests.post(f"{API_URL}/admin/events/", params={
                "venue_id": v_id, "name": e_name, "category": e_cat, 
                "date": str(e_date), "price": e_price, "max_per_user": e_limit
            })
            st.success(f"Event {e_name} is now LIVE.")

with tab2:
    st.subheader("System Performance")
    stats = requests.get(f"{API_URL}/admin/analytics").json()
    col1, col2 = st.columns(2)
    col1.metric("Total Tickets Sold", stats.get("total_tickets_sold", 0)) # [cite: 201]
    col2.metric("Gross Revenue", f"${stats.get('total_revenue', 0)}")