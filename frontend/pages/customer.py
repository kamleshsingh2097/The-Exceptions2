import sys
import os

# ensure parent folder (frontend) is on the import path so `utils` can be resolved
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import requests
from datetime import datetime
from utils.pdf_gen import generate_ticket_pdf
from utils.email_sim import simulate_email_sending

# Configuration
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


def format_event_datetime(value: str) -> str:
    if not value:
        return "N/A"
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %I:%M %p")
    except ValueError:
        return value

st.set_page_config(page_title="Customer Portal", layout="wide")
st.title("🎟️ Event Discovery & Booking")

if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "customer_email" not in st.session_state:
    st.session_state.customer_email = None
if "customer_name" not in st.session_state:
    st.session_state.customer_name = None

if not st.session_state.auth_token:
    st.warning("Please login from the Home page first.")
    st.stop()
if st.session_state.get("user_role") != "customer":
    st.error("Access denied. This page is only for Customer role.")
    st.stop()

# --- 1. Browse Upcoming Events ---
# Displays only events with 'upcoming' status [cite: 138, 158]
try:
    response = requests.get(f"{API_URL}/events/upcoming")
    if response.status_code == 200:
        events = response.json()
        
        if not events:
            st.info("No upcoming events at the moment. Check back later!")
        
        for event in events:
            event_when = format_event_datetime(event.get("event_date"))
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.subheader(event['name'])
                    st.write(f"**Category:** {event['category']} | **Date & Time:** {event_when}")
                    st.write(f"**Venue ID:** {event['venue_id']}")
                
                with col2:
                    st.write(f"### ${event['ticket_price']}")
                    if st.button(f"View Seats", key=f"view_{event['id']}"):
                        st.session_state.selected_event_id = event['id']
                        st.session_state.event_name = event['name']
                        st.session_state.event_date = event_when
                        st.session_state.price = event['ticket_price']

        # --- 2. Seat Selection & Checkout ---
        if "selected_event_id" in st.session_state:
            st.divider()
            st.header(f"Booking for: {st.session_state.event_name}")
            st.write(f"**When:** {st.session_state.event_date}")
            
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
                            order_id = None
                            if isinstance(order_data, dict):
                                order_id = order_data.get("order_id")
                                if order_id is None:
                                    order_obj = order_data.get("order", {})
                                    if isinstance(order_obj, dict):
                                        order_id = order_obj.get("id")
                            ticket_codes = order_data.get("ticket_codes", [])
                            primary_ticket_code = ticket_codes[0] if ticket_codes else "TICK-XXXX"
                            st.success("🎉 Booking Successful!")
                            if order_id is not None:
                                st.write(f"**Order ID:** {order_id}")
                            if ticket_codes:
                                st.write("**Ticket Code(s):** " + ", ".join(ticket_codes))
                            
                            # Trigger Optional Extensions [cite: 198]
                            ticket_info = {
                                "customer_name": st.session_state.customer_name or "Valued Customer",
                                "event_name": st.session_state.event_name,
                                "venue_name": "Main Arena",
                                "event_date": st.session_state.event_date,
                                "seat_number": ", ".join(selected_labels),
                                "order_id": order_id if order_id is not None else "N/A",
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
                            if book_res.status_code == 409:
                                st.error("⚠️ Too slow! Someone else just booked one of those seats. Please choose again.")
                                st.rerun()
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
    refund_review = st.text_area("Refund Review / Reason (optional)")
    if st.button("Submit Refund Request"):  # cite: 144
        ref_res = requests.post(
            f"{API_URL}/orders/{refund_order_id}/refund",
            params={"review_note": refund_review},
            headers={"Authorization": f"Bearer {st.session_state.auth_token}"}
        )
        if ref_res.status_code == 200:
            msg = "Refund processed for this Order ID. Seat availability has been restored."
            try:
                msg = ref_res.json().get("message", msg)
            except Exception:
                pass
            st.warning(msg)  # cite: 63, 161
        else:
            st.error(get_error_detail(ref_res, "Refund request failed"))
