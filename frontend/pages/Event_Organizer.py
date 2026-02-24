import streamlit as st
import requests
from datetime import datetime
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

API_URL = "http://localhost:8000"

st.title("🛡️ Event Organizer Dashboard")
st.caption("Manage venues, events, and performance")

if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None

if not st.session_state.auth_token:
    st.warning("Please login from the Home page first.")
    st.stop()
if st.session_state.get("user_role") != "organizer":
    st.error("Access denied. This page is only for Event Organizer role.")
    st.stop()

tab1, tab2 = st.tabs(["Manage Events", "Analytics"])

with tab1:
    st.subheader("Onboard New Venue & Event")
    # Venue Creation
    with st.expander("Add New Venue"):
        v_name = st.text_input("Venue Name")
        v_city = st.text_input("City")
        v_cap = st.number_input("Total Capacity", min_value=1)
        if st.button("Register Venue"):
            resp = requests.post(f"{API_URL}/admin/venues/", params={"name": v_name, "city": v_city, "capacity": v_cap})
            if resp.status_code == 200 or resp.status_code == 201:
                st.success("Venue Registered!")
            else:
                st.error(f"Venue creation failed ({resp.status_code}): {resp.text}")

    # Event Creation [cite: 123]
    with st.form("event_creation"):
        st.write("Create New Event")
        v_id = st.number_input("Venue ID", min_value=1)
        e_name = st.text_input("Event Name")
        e_cat = st.selectbox("Category", ["Concert", "Workshop", "Sports"])
        e_date = st.date_input("Event Date")
        e_time = st.time_input("Event Time")
        e_price = st.number_input("Ticket Price", min_value=0.0)
        e_limit = st.number_input("Max Tickets Per User", min_value=1, value=5)
        
        if st.form_submit_button("Launch Event"):
            # This triggers auto-generation of seats in the backend [cite: 126]
            resp = requests.post(f"{API_URL}/admin/events/", params={
                "venue_id": int(v_id),
                "name": e_name,
                "category": e_cat,
                "date": datetime.combine(e_date, e_time).isoformat(),
                "price": float(e_price),
                "max_per_user": int(e_limit)
            })
            if resp.status_code == 200 or resp.status_code == 201:
                st.success(f"Event {e_name} is now LIVE.")
            else:
                st.error(f"Event creation failed ({resp.status_code}): {resp.text}")

with tab2:
    st.subheader("System Performance")
    try:
        resp = requests.get(f"{API_URL}/admin/analytics")
        if resp.status_code == 200:
            stats = resp.json()
        else:
            st.warning(f"Analytics endpoint returned status {resp.status_code}")
            stats = {}
    except requests.exceptions.RequestException as exc:
        st.error(f"Failed to fetch analytics: {exc}")
        stats = {}
    except ValueError:
        st.error("Analytics endpoint did not return valid JSON.")
        stats = {}

    col1, col2 = st.columns(2)
    col1.metric("Total Tickets Sold", stats.get("total_tickets_sold", 0))  # [cite: 201]
    col2.metric("Gross Revenue", f"${stats.get('total_revenue', 0):.2f}")

    # debug: show upcoming events available right now
    st.markdown("---")
    st.write("### Upcoming Events (debug)")
    try:
        evt_resp = requests.get(f"{API_URL}/events/upcoming")
        if evt_resp.status_code == 200:
            st.json(evt_resp.json())
        else:
            st.write(f"could not fetch events: {evt_resp.status_code}")
    except Exception as e:
        st.write(f"error fetching events: {e}")
