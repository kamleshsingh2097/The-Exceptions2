import sys
import os

# ensure parent folder (frontend) is on the import path so `utils` can be resolved
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import requests
from utils.pdf_gen import generate_ticket_pdf
from utils.email_sim import simulate_email_sending

# Configuration
API_URL = "http://localhost:8000"

st.set_page_config(page_title="Customer Portal", layout="wide")
st.title("🎟️ Event Discovery & Booking")

if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "customer_email" not in st.session_state:
    st.session_state.customer_email = None
if "customer_name" not in st.session_state:
    st.session_state.customer_name = None

with st.sidebar:
    st.header("Account")
    if st.session_state.auth_token:
        st.success(f"Logged in as {st.session_state.customer_email}")
        if st.button("Logout"):
            st.session_state.auth_token = None
            st.session_state.customer_email = None
            st.session_state.customer_name = None
            st.rerun()
    else:
        auth_tab_login, auth_tab_register = st.tabs(["Login", "Register"])
        with auth_tab_login:
            login_email = st.text_input("Email", key="login_email")
            login_password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login"):
                login_res = requests.post(
                    f"{API_URL}/auth/login",
                    json={"email": login_email, "password": login_password}
                )
                if login_res.status_code == 200:
                    login_data = login_res.json()
                    st.session_state.auth_token = login_data["access_token"]
                    st.session_state.customer_email = login_data["email"]
                    st.session_state.customer_name = login_data["name"]
                    st.rerun()
                else:
                    st.error(login_res.json().get("detail", "Login failed"))
        with auth_tab_register:
            reg_name = st.text_input("Name", key="reg_name")
            reg_email = st.text_input("Email ", key="reg_email")
            reg_password = st.text_input("Password ", type="password", key="reg_password")
            if st.button("Create Account"):
                reg_res = requests.post(
                    f"{API_URL}/auth/register",
                    json={"name": reg_name, "email": reg_email, "password": reg_password}
                )
                if reg_res.status_code == 200:
                    reg_data = reg_res.json()
                    st.session_state.auth_token = reg_data["access_token"]
                    st.session_state.customer_email = reg_data["email"]
                    st.session_state.customer_name = reg_data["name"]
                    st.rerun()
                else:
                    st.error(reg_res.json().get("detail", "Registration failed"))

# --- 1. Browse Upcoming Events ---
# Displays only events with 'upcoming' status [cite: 138, 158]
try:
    response = requests.get(f"{API_URL}/events/upcoming")
    if response.status_code == 200:
        events = response.json()
        
        if not events:
            st.info("No upcoming events at the moment. Check back later!")
        
        for event in events:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.subheader(event['name'])
                    st.write(f"**Category:** {event['category']} | **Date:** {event['event_date']}")
                    st.write(f"**Venue ID:** {event['venue_id']}")
                
                with col2:
                    st.write(f"### ${event['ticket_price']}")
                    if st.button(f"View Seats", key=f"view_{event['id']}"):
                        st.session_state.selected_event_id = event['id']
                        st.session_state.event_name = event['name']
                        st.session_state.event_date = event['event_date']
                        st.session_state.price = event['ticket_price']

        # --- 2. Seat Selection & Checkout ---
        if "selected_event_id" in st.session_state:
            st.divider()
            st.header(f"Booking for: {st.session_state.event_name}")
            
            # Fetch available seats for the event [cite: 139]
            ev_id = st.session_state.selected_event_id
            seats_res = requests.get(f"{API_URL}/events/{ev_id}/seats")
            
            if seats_res.status_code == 200:
                available_seats = seats_res.json()
                seat_map = {s['seat_number']: s['id'] for s in available_seats}
                
                selected_labels = st.multiselect(
                    "Select your seats:", 
                    options=list(seat_map.keys()),
                    help=f"You can select up to {event.get('max_tickets_per_user', 5)} seats."  # cite: 62
                )

                if selected_labels:
                    total_cost = len(selected_labels) * st.session_state.price
                    st.write(f"**Total Amount:** ${total_cost}")

                    if st.button("Place Order & Pay"):  # cite: 141-142
                        seat_ids = [seat_map[label] for label in selected_labels]
                        
                        # API call to process booking [cite: 28]
                        booking_payload = {
                            "event_id": ev_id,
                            "seat_ids": seat_ids
                        }

                        if not st.session_state.auth_token:
                            st.error("Please login first to place an order.")
                            st.stop()

                        book_res = requests.post(
                            f"{API_URL}/orders/book",
                            json=booking_payload,
                            headers={"Authorization": f"Bearer {st.session_state.auth_token}"}
                        )
                        
                        if book_res.status_code == 200:
                            order_data = book_res.json()
                            ticket_codes = order_data.get("ticket_codes", [])
                            primary_ticket_code = ticket_codes[0] if ticket_codes else "TICK-XXXX"
                            st.success("🎉 Booking Successful!")
                            if ticket_codes:
                                st.write("**Ticket Code(s):** " + ", ".join(ticket_codes))
                            
                            # Trigger Optional Extensions [cite: 198]
                            ticket_info = {
                                "customer_name": st.session_state.customer_name or "Valued Customer",
                                "event_name": st.session_state.event_name,
                                "venue_name": "Main Arena",
                                "event_date": st.session_state.event_date,
                                "seat_number": ", ".join(selected_labels),
                                "ticket_code": primary_ticket_code,
                                "ticket_codes": ticket_codes
                            }
                            
                            # Extension: Email Simulation [cite: 203]
                            simulate_email_sending(
                                st.session_state.customer_email or "customer@example.com",
                                ticket_info
                            )
                            
                            # Extension: PDF Generation [cite: 202]
                            pdf_bytes = generate_ticket_pdf(ticket_info)
                            st.download_button(
                                label="📥 Download PDF Ticket",
                                data=pdf_bytes,
                                file_name=f"Ticket_{st.session_state.event_name}.pdf",
                                mime="application/pdf"
                            )
                        else:
                            detail = "Unknown booking error"
                            try:
                                detail = book_res.json().get("detail", detail)
                            except Exception:
                                pass
                            st.error(f"Booking failed: {detail}")
            else:
                st.error("Could not load seat map.")

except Exception as e:
    st.error("Backend server is unreachable. Please ensure the FastAPI server is running.")

# --- 3. Request Refund ---
st.divider()
with st.expander("Request a Refund"):
    st.write("Note: Refunds are only allowed before the event date.")  # cite: 158
    refund_order_id = st.number_input("Enter Order ID:", min_value=1, step=1)
    if st.button("Submit Refund Request"):  # cite: 144
        ref_res = requests.post(f"{API_URL}/orders/{refund_order_id}/refund")
        if ref_res.status_code == 200:
            st.warning("Refund processed. Seat availability has been restored.")  # cite: 63, 161
        else:
            st.error(ref_res.json().get('detail'))
